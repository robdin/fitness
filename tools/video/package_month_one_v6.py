"""Verify and package Blueprint media, source material and matched test stimuli."""
import hashlib,html,json,shutil,subprocess,sys
from pathlib import Path
from PIL import Image
from month_one_core import ROOT,digest,script,normalized
from build_month_one import probe
from voice_contract import validate_voice_receipt
from produce_month_one_v6 import episodes,workspace_for,WORKSPACE,RENDERER,TOKENS
from package_month_one_v3 import CSS as BASE_CSS,markdown_page,zip_files,write_json
sys.path.insert(0,str(ROOT/'tools/calendar'))
from build_month_one_v6 import load,validate,source_map,posting_copy
from check_copy import public_source_title, require_clean, strings

REVIEW=WORKSPACE/'review'
DELIVERY=ROOT.parent/'fitness-deliverables/month-one-v6-conversational'
CSS=BASE_CSS+'''body{background:#F3F5F4;color:#173249}a{color:#2348C6}header{border-color:#2348C6}.block{background:#DDD6F5;border-radius:5px}video{border-radius:5px;background:#2348C6}.note{color:#173249}.eyebrow{color:#2348C6}h1 em{font-family:Georgia,serif;font-weight:500}.strip{scroll-snap-type:x proximity}.strip a{scroll-snap-align:start}'''

def candidates():
    e=episodes()
    return [(x,True,'motion') for x in e]+[(next(x for x in episodes(False) if x['id']=='BC03'),False,'motion'),(next(x for x in e if x['id']=='BC04'),True,'static')]

def relative_folder(id,citation=True):
    return id if citation else f'variants/citation-off/{id}'

def audio_hash(file):
    return subprocess.run(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c','copy','-f','md5','-'],capture_output=True,text=True,check=True).stdout.strip()

def verify():
    d,s,p=load();validate(d,s,p);outputs=[]
    for ep,citation,treatment in candidates():
        id=ep['id'];folder=workspace_for(citation)/'review'/id;file=folder/f'{id}-{treatment}.mp4'
        tl=json.loads((folder/'timeline.json').read_text());r=json.loads((folder/f'verification-{treatment}.json').read_text())
        assert tl['episode']==ep and tl['timing']=='provider_word_alignment','Stale timeline '+id
        assert tl['script_sha256']==r['script_sha256']==hashlib.sha256(script(ep).encode()).hexdigest()
        assert normalized(script(ep))==normalized(' '.join(c['text'] for c in tl['captions']))
        assert all(0<=c['start']<c['end']<=tl['duration'] and c['cps']<=20.01 and len(c['lines'])<=2 for c in tl['captions'])
        assert all(a['end']<=b['start']+.001 for a,b in zip(tl['captions'],tl['captions'][1:]))
        assert r['sha256']==digest(file) and r['renderer_sha256']==digest(RENDERER) and r['timeline_sha256']==digest(folder/'timeline.json')
        voice=WORKSPACE/'voice'/id;generation=json.loads((voice/'generation.json').read_text())
        voice_check=validate_voice_receipt(ep,voice,**ep['voice_contract'])
        assert r['voice_provenance']==voice_check,'Stale narration settings '+id
        assert generation['status']=='complete' and generation['script_sha256']==tl['script_sha256']
        assert generation['audio_sha256']==digest(voice/'narration.wav') and generation['alignment_sha256']==digest(voice/'alignment.json')
        assert r['full_decode']=='passed' and r['voice_present']
        meta=probe(file);v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
        assert (v['width'],v['height'],v['codec_name'],v['r_frame_rate'])==(1080,1920,'h264','30/1')
        assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
        assert int(v['nb_frames'])==round(tl['duration']*30) and abs(float(meta['format']['duration'])-tl['duration'])<.04
        assert -18<=float(r['loudness']['input_i'])<=-14 and float(r['loudness']['input_tp'])<=-1
        subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],capture_output=True,check=True)
        outputs.append(dict(id=id,visual_version='v6-blueprint-conversational',citation=citation,treatment=treatment,path=relative_folder(id,citation)+f'/{id}-{treatment}.mp4',sha256=digest(file),audio_md5=audio_hash(file),duration=r['duration'],frames=r['frames'],max_cps=r['max_cps'],loudness=r['loudness'],answer_starts_seconds=round(tl['beats'][1]['start'],3),render_elapsed_seconds=r['render_elapsed_seconds']))
    for id in ['BC03','BC04']:
        pair=[x for x in outputs if x['id']==id]
        assert len(pair)==2 and len({x['audio_md5'] for x in pair})==1 and len({x['duration'] for x in pair})==1
    subprocess.run(['node',str(ROOT/'tools/video/verify_v6_frames.cjs')],capture_output=True,check=True)
    frames=json.loads((REVIEW/'frame-check.json').read_text())
    support=json.loads((REVIEW/'supporting/manifest.json').read_text())
    assert support['content_sha256']==digest(ROOT/'content/month-one-v6/calendar.json')
    assert support['renderer_sha256']==digest(ROOT/'tools/video/render_supporting_v6.cjs') and support['tokens_sha256']==digest(TOKENS)
    assert support['font_sha256']==episodes()[0]['graphics']['font_sha256']
    assert support['character_assets']==0 and len(support['outputs'])==36
    for x in support['outputs']:
        f=REVIEW/'supporting'/x['file'];assert digest(f)==x['sha256']
        with Image.open(f) as im:assert im.size==((1080,1350) if x['file'].startswith('BCK') else (1080,1920))
    asr=[]
    for e in episodes():
        reports=[]
        for model in ['base.en','small.en']:
            f=WORKSPACE/'audio-qa'/model/(e['id']+'.json')
            if f.exists():
                r=json.loads(f.read_text());assert r['audio_sha256']==digest(WORKSPACE/'voice'/e['id']/'narration.wav')
                reports.append(dict(model=model,differences=r['differences']))
        assert reports and reports[0]['model']=='base.en'
        asr.append(dict(id=e['id'],reports=reports,human_listening_review=False))
    result=dict(status='production_candidate_complete_audience_validation_pending',version='v6-blueprint-conversational',core_episodes=16,video_exports=19,orientation_videos=1,carousel_panels=20,story_frames=16,character_stimuli=0,citation_stimuli=2,motion_stimuli=2,stimuli_include_core_exports=True,decode_passes=19,frames_checked=frames['frames'],max_caption_cps=max(x['max_cps'] for x in outputs),duration_seconds_range=[min(x['duration'] for x in outputs),max(x['duration'] for x in outputs)],maximum_answer_start_seconds=max(x['answer_starts_seconds'] for x in outputs),comparison_audio_identical=True,new_voice_requests=len(list((WORKSPACE/"voice").glob("*/generation.json")))+len(list((WORKSPACE/"voice-revisions").glob("*/*/generation.json"))),new_image_requests=0,retained_voice_tracks=0,provider_actual_charge=None,human_listening_review=False,target_uploader_preview=False,target_audience_tests=0,live_audience_observations=0,hands_on_labor_measured=False,public_upload=False,asr_review=asr,outputs=outputs)
    write_json(REVIEW/'verification-summary.json',result);write_json(ROOT/'examples/month-one-v6/production-verification.json',result)
    return result

def reference_paths():
    patterns=['content/month-one-v6/*','content/month-one-v3/*','research/blueprint-v5/*','research/audience-v3/*','research/brand-culture-2026-10/*','brand/blueprint/**/*','brand/dreamy-tactical/*','brand/v3/*.md','brand/v4/*.md','experiments/month-one-v6.json','experiments/citation-visibility-v3.json','experiments/month-one-v3.json','experiments/citation-visibility-v1.json','experiments/character-trust-v1.json','docs/MONTH_ONE_V6.md','docs/MONTH_ONE_V4.md','examples/month-one-v6/*.json','measurement/month-one-v6*']
    patterns+=['content/lifestyle-pilot/*.md','research/lifestyle-audit-2026-10-26/*.md','research/blueprint-v6/*.md','brand/v3/tokens.json','examples/month-one-v4/production-verification.json','examples/month-one-v4/test-stimuli.json','measurement/MONTH_ONE_V6_FIELD_GUIDE.md','docs/MONTH_ONE_V6_PILOT.md']
    return sorted({p for pat in patterns for p in ROOT.glob(pat) if p.is_file()})

def build_hub(result):
    d,s,p=load();sm=source_map(s);esc=html.escape
    src=workspace_for(False)/'review/BC03';dest=REVIEW/'variants/citation-off/BC03';dest.mkdir(parents=True,exist_ok=True)
    for f in src.iterdir():
        if f.suffix in ['.png','.mp4','.json','.srt']:shutil.copy2(f,dest/f.name)
    stimuli=dict(status='produced_test_not_run',participants=0,citation=[x for x in result['outputs'] if x['id']=='BC03'],motion=[x for x in result['outputs'] if x['id']=='BC04'])
    write_json(REVIEW/'test-stimuli.json',stimuli);write_json(ROOT/'examples/month-one-v6/test-stimuli.json',stimuli)
    protocol_path=ROOT/'experiments/citation-visibility-v3.json';protocol=json.loads(protocol_path.read_text());protocol['status']='stimuli_produced_test_not_run';protocol['stimulus_hashes']=[dict(citation=x['citation'],sha256=x['sha256']) for x in stimuli['citation']];write_json(protocol_path,protocol)
    for src in reference_paths():
        dest=REVIEW/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        if src.suffix=='.md':dest.with_suffix('.html').write_text(markdown_page(src.read_text()).replace(BASE_CSS,CSS))
    def player(folder,id,treatment='motion'):
        return f'<video controls playsinline preload="metadata" poster="{folder}/cover.png" src="{folder}/{id}-{treatment}.mp4" aria-label="{id} {treatment} preview"></video>'
    page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Body of our dreams · Blueprint month</title><style>'+CSS+'</style><main><header><p class="eyebrow">BLUEPRINT / SELECTED STYLE / NOVEMBER 2026</p><h1><em>Your dream body.</em><br>Your real life.</h1><p>Updated 27 October: copyable caption tools, a clearer BC05 promise, conversational voice and the same Blueprint identity.</p><p>A separate Start here intro plus 16 narrated videos across strength, movement, food, recovery and practical planning. Four carousels, eight stories and two additional experiment controls.</p><nav><a href="#week-1">Week 1</a><a href="#week-2">Week 2</a><a href="#week-3">Week 3</a><a href="#week-4">Week 4</a><a href="#experiments">Experiments</a><a href="#review">Review status</a></nav><p class="note">Body of Our Dreams uses the owner-selected Blueprint style. Review exports, not scheduled or published posts.</p><p><a href="content/month-one-v6/CALENDAR.html">Full schedule</a> · <a href="docs/MONTH_ONE_V6_PILOT.html">Run the pilot</a> · <a href="content/month-one-v6/ACCOUNT_ENTRY.html">Profile copy</a> · <a href="content/month-one-v6/calendar.ics">Planning calendar</a> · <a href="content/month-one-v6/SCRIPTS.html">Scripts</a> · <a href="content/month-one-v6/SOURCE_MAP.html">Claim/source map</a> · <a href="brand/blueprint/STYLE_GUIDE.html">Style guide</a></p></header>']
    intro=d['orientation_asset']
    pkg=dict(id='BC00',youtube_title=intro['title'],youtube_description=posting_copy(intro,sm,'youtube'),instagram_caption=posting_copy(intro,sm,'instagram'),public_upload=False,human_review_pending=True,counted_in_core_cohort=False)
    write_json(REVIEW/'BC00/posting-copy.json',pkg)
    page.append('<section id="start-here"><h2>Start here · account introduction</h2>'+player('BC00','BC00')+'<p>Separate orientation video; not an extra core calendar slot.</p><p><a href="BC00/BC00-motion.mp4" download>Download intro</a> · <a href="BC00/posting-copy.json">Posting copy</a> · <a href="content/lifestyle-pilot/START_HERE_KIT.html">Starter kit</a></p></section>')
    for week in range(1,5):
        page.append(f'<section id="week-{week}"><h2>Week {week}</h2>')
        for e in d['episodes']:
            if e['week']!=week:continue
            id=e['id'];pkg=dict(id=id,visual_version='v6-blueprint-conversational',proposed_publish_at=e['publish_at'],youtube_title=e['title'],youtube_description=posting_copy(e,sm,'youtube'),instagram_caption=posting_copy(e,sm,'instagram'),hook_type=e['hook_type'],evidence_ids=e['evidence_ids'],human_review_pending=True,public_upload=False)
            write_json(REVIEW/id/'posting-copy.json',pkg)
            page.append(f'<article id="{id}">{player(id,id)}<div><p class="eyebrow">NOV {e["day"]} / {id} / {esc(e["series"])} / {e["hook_type"]} OPENING</p><h2>{esc(e["title"])}</h2><p>{esc(e["caption"])}</p><p><a href="{id}/{id}-motion.mp4" download>Download video</a> · <a href="{id}/{id}.srt">Captions</a> · <a href="{id}/posting-copy.json">Platform copy and sources</a></p><details><summary>Script and comprehension check</summary><p>{esc(" ".join(b["narration"] for b in e["beats"]))}</p><p><strong>Takeaway:</strong> {esc(e["comprehension"]["answer"])}</p><p><strong>Critical error:</strong> {esc(e["comprehension"]["critical_error"])}</p></details><details><summary>Instagram caption and source links</summary><pre>{esc(pkg["instagram_caption"])}</pre></details></div></article>')
        for post in d['supporting_posts']:
            if (post['day']-1)//7+1!=week:continue
            id=post['id'];story=post['kind']=='story';names=['prompt.png','followup.png'] if story else [f'{i}.png' for i in range(1,6)]
            evidence=list(dict.fromkeys(i for e in d['episodes'] if e['id'] in post['episode_ids'] for i in e['evidence_ids']))
            refs=[dict(id=i,title=public_source_title(sm[i]['title']),url=sm[i]['url']) for i in evidence]
            pkg={**post,'visual_version':'v6-blueprint-conversational','public_upload':False,'status':'rendered_review_pending','sources':refs}
            if story:pkg['native_poll_placement']=dict(x=112,y=1010,width=762,height=205,instruction='Add a native Instagram poll using the supplied options; the PNG is not interactive.')
            else:pkg['instagram_caption']=post['caption']+'\n\n'+post['source_note']+('\n\nSources:\n'+'\n'.join(f'{x["title"]}: {x["url"]}' for x in refs) if refs else '')
            require_clean(strings(pkg, id+'.posting-copy'))
            write_json(REVIEW/'supporting'/id/'posting-copy.json',pkg)
            page.append(f'<section><p class="eyebrow">NOV {post["day"]} / {id} / {post["kind"]}</p><h3>{esc(post["title"])}</h3><div class="strip">'+''.join(f'<a href="supporting/{id}/{name}"><img loading="lazy" src="supporting/{id}/{name}" alt="{id} panel {i+1}"></a>' for i,name in enumerate(names))+f'</div><a href="supporting/{id}/posting-copy.json">Copy, sources and upload instructions</a></section>')
        page.append('</section>')
    page.append('<section id="experiments" class="block"><h2>Matched experiments</h2><p>Research controls are not extra scheduled posts. No participant tests have run.</p><h3>BC03: claim-specific source label</h3><p>Same audio, timing, captions, scope and description links. Only the label changes.</p><div class="grid"><div><h3>Label on</h3>'+player('BC03','BC03')+'</div><div><h3>Label off</h3>'+player('variants/citation-off/BC03','BC03')+'</div></div><h3>BC04: motion that explains a route</h3><p>Same wording, timing, source cues and encoded audio. Only route interpolation changes.</p><div class="grid"><div><h3>Motion</h3>'+player('BC04','BC04')+'</div><div><h3>Static</h3>'+player('BC04','BC04','static')+'</div></div><p><a href="test-stimuli.json">Exact stimulus hashes</a> · <a href="experiments/citation-visibility-v3.json">Citation protocol</a></p></section>')
    flagged=[a['id'] for a in result['asr_review'] if a['reports'][-1]['differences']]
    page.append(f'<section id="review" class="block"><h2>Review status</h2><p>All 19 videos decode at 1080 × 1920, 30 fps. {result["frames_checked"]:,} frames checked for text bounds. Captions stay within 20 characters/second. Seventeen freshly generated conversational narrations, including the separate intro. Both comparison pairs have identical encoded audio and runtime.</p><p>Speech-recognition differences to inspect: {", ".join(flagged) or "none in latest checks"}. Recognition differences do not establish spoken errors. Full human listening and target-app overlay previews remain pending.</p><p>Audience interest, comprehension and recurring hands-on effort still require measurement. Keep platform observations separate and the 12-hour weekly cap. Business decision: insufficient evidence.</p><p><a href="verification-summary.json">Production receipt</a> · <a href="content/month-one-v6/LISTENING_REVIEW.html">Listening notes</a> · <a href="docs/MONTH_ONE_V6.html">Handoff and rebuild</a> · <a href="experiments/month-one-v6.json">Month decision protocol</a> · <a href="research/blueprint-v6/README.html">Research update</a></p></section></main></html>')
    (REVIEW/'index.html').write_text(''.join(page))

def archive():
    DELIVERY.mkdir(parents=True,exist_ok=True)
    files=[p for p in REVIEW.rglob('*') if p.is_file() and p.suffix in ['.html','.json','.jsonl','.md','.ics','.png','.srt','.mp4','.ttf','.txt']]
    expected={relative_folder(e['id'],c)+f'/{e["id"]}-{t}.mp4' for e,c,t in candidates()}
    assert {str(p.relative_to(REVIEW)) for p in files if p.suffix=='.mp4'}==expected
    assert not any('characters' in p.parts for p in files)
    paths=reference_paths()+[p for pat in ['tools/video/*.py','tools/video/*.cjs','tools/calendar/*.py','tools/brand/*.py','tools/brand/*.cjs','tests/test_copy_rules.py','AGENTS.md','brand/v3/*','content/mvp/time-audit/fonts/*','tests/*v6*','package.json','package-lock.json'] for p in ROOT.glob(pat) if p.is_file()]
    extras={'RESTORE.txt':'Compare before restoring fitness source files. Install pinned Node dependencies, Python Pillow and FFmpeg. Run python3 tools/video/check_month_one_audio.py --series v6 --check-inputs for a standard-library retained-input check without ASR/model downloads. Retained voice belongs in fitness/.local/month-one-v6-conversational/voice. Run produce_month_one_v6.py render, BC03 --no-citation, BC04 --treatment static, render_supporting_v6.cjs, then package_month_one_v6.py. Rendering retained speech needs no provider call. Credential/profile files are excluded. This is a production source subset, not a full repository backup.\n'}
    for ep in episodes():
        folder=WORKSPACE/'voice'/ep['id'];paths.extend([folder/'narration.wav',folder/'alignment.json']);r=json.loads((folder/'generation.json').read_text());r.pop('voice',None)
        extras[str(Path('fitness')/(folder/'generation.json').relative_to(ROOT))]=json.dumps(r,indent=2)+'\n'
    paths+=list((WORKSPACE/'audio-qa').glob('*/*.json'))
    paths+=list((WORKSPACE/'voice-revisions').rglob('*.wav'))+list((WORKSPACE/'voice-revisions').rglob('*.json'))
    receipt=dict(review=zip_files(DELIVERY/'Conversational_Blueprint_Month_Review.zip',[(p,str(Path('Conversational_Blueprint_Month')/p.relative_to(REVIEW))) for p in files]),sources=zip_files(DELIVERY/'Conversational_Blueprint_Month_Sources.zip',[(p,str(Path('fitness')/p.relative_to(ROOT))) for p in set(paths)],extras),public_upload=False)
    write_json(DELIVERY/'delivery-receipt.json',receipt);return receipt

def main():
    result=verify();build_hub(result);print(json.dumps(archive(),indent=2))
if __name__=='__main__':main()
