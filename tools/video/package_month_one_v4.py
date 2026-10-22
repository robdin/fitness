"""Verify, assemble and archive the Training Club production and test stimuli."""
import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image
from month_one_core import ROOT, digest, script, normalized
from build_month_one import probe
from produce_month_one_v4 import episodes, workspace_for, WORKSPACE, RENDERER
from produce_month_one_v3 import WORKSPACE as VOICE_WORKSPACE
from package_month_one_v3 import CSS, markdown_page, zip_files, write_json
from build_month_one_v3 import load, validate, source_map, posting_copy

REVIEW=WORKSPACE/'review'
DELIVERY=ROOT.parent/'fitness-deliverables/month-one-v4'

def candidates():
    result=[(e,'M',True) for e in episodes()]
    for arm in ['R','G']:result.extend((e,arm,True) for e in episodes(arm) if e['id'] in ['B04','B08'])
    result.append((episodes(citation=False)[2],'M',False))
    return result

def relative_folder(id,arm='M',citation=True):
    return id if arm=='M' and citation else f'variants/{arm if citation else "citation-off"}/{id}'

def audio_hash(file):
    return subprocess.run(['ffmpeg','-v','error','-i',str(file),'-map','0:a:0','-c','copy','-f','md5','-'],capture_output=True,text=True,check=True).stdout.strip()

def verify():
    d,s,p=load();validate(d,s,p);outputs=[]
    for ep,arm,citation in candidates():
        id=ep['id'];folder=workspace_for(arm,citation)/'review'/id;file=folder/f'{id}-motion.mp4'
        tl=json.loads((folder/'timeline.json').read_text());r=json.loads((folder/'verification-motion.json').read_text())
        assert tl['episode']==ep and tl['timing']=='provider_word_alignment'
        assert tl['script_sha256']==r['script_sha256']==hashlib.sha256(script(ep).encode()).hexdigest()
        assert normalized(script(ep))==normalized(' '.join(c['text'] for c in tl['captions']))
        assert all(0<=c['start']<c['end']<=tl['duration'] and c['cps']<=20.01 for c in tl['captions'])
        assert all(a['end']<=b['start']+.001 for a,b in zip(tl['captions'],tl['captions'][1:]))
        assert r['sha256']==digest(file) and r['renderer_sha256']==digest(RENDERER) and r['timeline_sha256']==digest(folder/'timeline.json')
        voice=VOICE_WORKSPACE/'voice'/id;generation=json.loads((voice/'generation.json').read_text())
        assert generation['status']=='complete' and generation['script_sha256']==tl['script_sha256']
        assert generation['audio_sha256']==digest(voice/'narration.wav') and generation['alignment_sha256']==digest(voice/'alignment.json')
        assert r['full_decode']=='passed' and r['voice_present']
        meta=probe(file);v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
        assert (v['width'],v['height'],v['codec_name'],v['r_frame_rate'])==(1080,1920,'h264','30/1')
        assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
        assert int(v['nb_frames'])==round(tl['duration']*30) and abs(float(meta['format']['duration'])-tl['duration'])<.04
        assert -18<=float(r['loudness']['input_i'])<=-14 and float(r['loudness']['input_tp'])<=-1
        subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],capture_output=True,check=True)
        outputs.append(dict(id=id,arm=arm,citation= citation,path=relative_folder(id,arm,citation)+f'/{id}-motion.mp4',sha256=digest(file),audio_md5=audio_hash(file),duration=r['duration'],frames=r['frames'],max_cps=r['max_cps'],loudness=r['loudness'],answer_starts_seconds=round(tl['beats'][1]['start'],3),render_elapsed_seconds=r['render_elapsed_seconds']))
    for id in ['B03','B04','B08']:
        items=[x for x in outputs if x['id']==id];assert len({x['audio_md5'] for x in items})==1;assert len({x['duration'] for x in items})==1
    subprocess.run(['node',str(ROOT/'tools/video/verify_v4_frames.cjs')],capture_output=True,check=True)
    frames=json.loads((REVIEW/'frame-check.json').read_text())
    support=json.loads((REVIEW/'supporting/manifest.json').read_text())
    assert support['content_sha256']==digest(ROOT/'content/month-one-v3/calendar.json') and support['renderer_sha256']==digest(ROOT/'tools/video/render_supporting_v4.cjs')
    assert support['character_sha256']==digest(ROOT/'brand/v4/characters/guide-muscular.png') and len(support['outputs'])==36
    for x in support['outputs']:
        file=REVIEW/'supporting'/x['file'];assert digest(file)==x['sha256']
        with Image.open(file) as im:assert im.size==((1080,1350) if x['file'].startswith('BK') else (1080,1920))
    asr=[]
    for e in episodes():
        reports=[]
        for model in ['base.en','small.en']:
            path=VOICE_WORKSPACE/'audio-qa'/model/(e['id']+'.json')
            if path.exists():
                r=json.loads(path.read_text());assert r['audio_sha256']==digest(VOICE_WORKSPACE/'voice'/e['id']/'narration.wav');reports.append(dict(model=model,differences=r['differences']))
        assert reports;asr.append(dict(id=e['id'],reports=reports,human_listening_review=False))
    result=dict(status='production_candidate_complete_audience_validation_pending',version=4,core_episodes=16,video_exports=21,carousel_panels=20,story_frames=16,character_stimuli=6,citation_stimuli=2,stimuli_include_core_exports=True,decode_passes=21,frames_checked=frames['frames'],max_caption_cps=max(x['max_cps'] for x in outputs),duration_seconds_range=[min(x['duration'] for x in outputs),max(x['duration'] for x in outputs)],maximum_answer_start_seconds=max(x['answer_starts_seconds'] for x in outputs),comparison_audio_identical=True,new_voice_requests=0,new_image_requests=2,retained_voice_tracks=16,human_listening_review=False,target_uploader_preview=False,target_audience_tests=0,live_audience_observations=0,hands_on_labor_measured=False,public_upload=False,asr_review=asr,outputs=outputs)
    write_json(REVIEW/'verification-summary.json',result);write_json(ROOT/'examples/month-one-v4/production-verification.json',result)
    return result

def reference_paths():
    patterns=['research/audience-v3/*','content/month-one-v3/*','content/month-one-v4/*','brand/v3/*','brand/v4/**/*','experiments/month-one-v3.json','experiments/character-trust-v1.json','docs/MONTH_ONE_V4.md','examples/month-one-v4/*.json','measurement/month-one-v3*']
    return sorted({p for pat in patterns for p in ROOT.glob(pat) if p.is_file()})

def build_hub(result):
    d,s,p=load();sm=source_map(s);esc=html.escape
    for ep,arm,citation in candidates():
        if arm=='M' and citation:continue
        src=workspace_for(arm,citation)/'review'/ep['id'];dest=REVIEW/relative_folder(ep['id'],arm,citation);dest.mkdir(parents=True,exist_ok=True)
        for f in src.iterdir():
            if f.suffix in ['.png','.mp4','.json','.srt']:shutil.copy2(f,dest/f.name)
    # Freeze exact stimulus bytes without inventing participant observations.
    stimuli=[x for x in result['outputs'] if x['id'] in ['B04','B08','B03']]
    write_json(REVIEW/'test-stimuli.json',dict(status='produced_pretest_pending',character=[x for x in stimuli if x['id'] in ['B04','B08']],citation=[x for x in stimuli if x['id']=='B03'],participants=0))
    write_json(ROOT/'examples/month-one-v4/test-stimuli.json',json.loads((REVIEW/'test-stimuli.json').read_text()))
    protocol_path=ROOT/'experiments/character-trust-v1.json';protocol=json.loads(protocol_path.read_text())
    protocol['stimulus_hashes']=[dict(id=x['id'],arm=x['arm'],sha256=x['sha256']) for x in stimuli if x['id'] in ['B04','B08']]
    protocol['citation_followup']['stimulus_hashes']=[dict(citation=x['citation'],sha256=x['sha256']) for x in stimuli if x['id']=='B03']
    write_json(protocol_path,protocol)
    for src in reference_paths():
        dest=REVIEW/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        if src.suffix=='.md':dest.with_suffix('.html').write_text(markdown_page(src.read_text()))
    def player(folder,id):return f'<video controls playsinline preload="metadata" poster="{folder}/cover.png" src="{folder}/{id}-motion.mp4" aria-label="{id} preview"></video>'
    page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rep & Reason · Training Club production</title><style>'+CSS+'.variants{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.variants video{max-height:560px} @media(max-width:680px){.variants{grid-template-columns:1fr}.variants video{max-width:300px}} </style><main><header><p class="eyebrow">TRAINING CLUB / PRODUCTION V4 / NOVEMBER 2026</p><h1>Your first month.<br>One useful answer at a time.</h1><p>16 narrated vertical videos, 4 carousels and 8 stories, with an original illustrated guide and clear evidence cues.</p><nav><a href="#week-1">Week 1</a><a href="#week-2">Week 2</a><a href="#week-3">Week 3</a><a href="#week-4">Week 4</a><a href="#character">Character test</a><a href="#citations">Citation test</a><a href="#review">Review status</a></nav><p class="note">Muscular guide is the provisional production candidate. No audience winner has been established. These files have not been published.</p><p><a href="content/month-one-v3/CALENDAR.html">Full schedule</a> · <a href="content/month-one-v3/calendar.ics">Planning calendar</a> · <a href="content/month-one-v3/SCRIPTS.html">Scripts</a> · <a href="brand/v4/STYLE_GUIDE.html">Brand application</a> · <a href="docs/MONTH_ONE_V4.html">Production handoff</a></p></header>']
    for week in range(1,5):
        page.append(f'<section id="week-{week}"><h2>Week {week}</h2>')
        for e in d['episodes']:
            if e['week']!=week:continue
            id=e['id'];pkg=dict(id=id,visual_version='v4-M',proposed_publish_at=e['publish_at'],youtube_title=e['title'],youtube_description=posting_copy(e,sm,'youtube')+'\n\nOriginal fictional illustrated guide.',instagram_caption=posting_copy(e,sm,'instagram')+'\n\nOriginal fictional illustrated guide.',hook_type=e['hook_type'],evidence_ids=e['evidence_ids'],human_review_pending=True,public_upload=False)
            write_json(REVIEW/id/'posting-copy.json',pkg)
            page.append(f'<article id="{id}">{player(id,id)}<div><p class="eyebrow">NOV {e["day"]} / {id} / {e["cluster"]} / {e["hook_type"]} OPENING</p><h2>{esc(e["title"])}</h2><p>{esc(e["caption"])}</p><p><a href="{id}/{id}-motion.mp4" download>Download video</a> · <a href="{id}/{id}.srt">Captions</a> · <a href="{id}/posting-copy.json">Posting copy and sources</a></p><details><summary>Script and comprehension check</summary><p>{esc(" ".join(b["narration"] for b in e["beats"]))}</p><p><strong>Takeaway:</strong> {esc(e["comprehension"]["answer"])}</p><p><strong>Critical error:</strong> {esc(e["comprehension"]["critical_error"])}</p></details><details><summary>Instagram caption and source links</summary><pre>{esc(pkg["instagram_caption"])}</pre></details></div></article>')
        for post in d['supporting_posts']:
            if (post['day']-1)//7+1!=week:continue
            id=post['id'];story=post['kind']=='story';names=['prompt.png','followup.png'] if story else [f'{i}.png' for i in range(1,6)]
            evidence=list(dict.fromkeys(i for e in d['episodes'] if e['id'] in post['episode_ids'] for i in e['evidence_ids']))
            refs=[dict(id=i,title=sm[i]['title'],url=sm[i]['url']) for i in evidence]
            pkg={**post,'visual_version':'v4','public_upload':False,'status':'rendered_review_pending','sources':refs}
            if story:pkg['native_poll_placement']=dict(x=112,y=1010,width=762,height=205,instruction='Add a real native Instagram poll with these options. The PNG itself is not interactive.')
            else:pkg['instagram_caption']=post['caption']+'\n\nSources and scope:\n'+'\n'.join(f'{x["title"]}: {x["url"]}' for x in refs)+'\nSee the linked episode descriptions for claim boundaries.'
            write_json(REVIEW/'supporting'/id/'posting-copy.json',pkg)
            page.append(f'<section><p class="eyebrow">NOV {post["day"]} / {id} / {post["kind"]}</p><h3>{esc(post["title"])}</h3><div class="strip">'+''.join(f'<a href="supporting/{id}/{name}"><img loading="lazy" src="supporting/{id}/{name}" alt="{id} panel {i+1}"></a>' for i,name in enumerate(names))+f'</div><a href="supporting/{id}/posting-copy.json">Copy, source links and upload instructions</a></section>')
        page.append('</section>')
    page.append('<section id="character" class="block"><h2>Character comparison: six matched clips</h2><p>Same words, encoded audio, timing, text and diagram positions. Only the character asset changes. M/R differences include minor generative clothing/contour changes; R still looks athletic. Pretest perceived muscularity and equal friendliness before interpreting this as a physique test. G is the same V4 layout without the guide, not the old V3 composition.</p>')
    for id in ['B04','B08']:
        page.append(f'<h3>{id}</h3><div class="variants">')
        for arm,label in [('M','Muscular guide'),('R','Smaller-build guide'),('G','Graphics only')]:page.append(f'<div><h3>{label}</h3>'+player(relative_folder(id,arm),id)+'</div>')
        page.append('</div>')
    page.append('<p><a href="research/audience-v3/08_CHARACTER_TEST_PROTOCOL.html">Protocol</a> · <a href="research/audience-v3/CHARACTER_TEST_FIELD_GUIDE.html">Survey and field guide</a> · <a href="test-stimuli.json">Frozen file hashes</a></p><p>Comparison page is for production review. Do not show all arms before first-exposure testing. No instrumented participant player is bundled: use a validated player for unique visible-time telemetry, or label moderator observations as estimates.</p></section>')
    page.append('<section id="citations" class="block"><h2>Citation comparison: one specific claim</h2><p>B03 has identical audio, scope and caption text. The control removes only the short source label. Both versions retain complete source links in their posting description. Source cues provide traceability; a trust lift remains a hypothesis.</p><div class="grid"><div><h3>Source label on</h3>'+player('B03','B03')+'</div><div><h3>Source label off</h3>'+player('variants/citation-off/B03','B03')+'</div></div><p><a href="B03/posting-copy.json">Shared posting copy and sources for both versions</a></p></section>')
    flagged=[a['id'] for a in result['asr_review'] if a['reports'][-1]['differences']]
    page.append(f'<section id="review" class="block"><h2>What has been checked</h2><p>All 21 videos decode at 1080 × 1920, 30 fps, with matched comparison audio. {result["frames_checked"]:,} frames checked for text bounds. Captions stay at or below 20 characters per second. All 16 approved voice tracks are reused; no new narration requests.</p><p>Independent speech checks are bound to the unchanged audio. Listening flags: {", ".join(flagged)}. Full human listening, target-app preview and audience tests remain pending. No participant results or hands-on labor are invented.</p><p><a href="verification-summary.json">Verification receipt</a> · <a href="experiments/month-one-v3.json">Month go/no-go framework</a> · <a href="research/audience-v3/07_TRUST_AND_CHARACTER.html">Trust and character research</a></p><p>Keep the visual version fixed for the launch block. Track platform results separately, log recurring production work, and keep the 12-hour weekly cap. Reusable artwork reduces repeat generation work; it does not yet prove the process fits the cap.</p></section></main></html>')
    (REVIEW/'index.html').write_text(''.join(page))

def archive():
    DELIVERY.mkdir(parents=True,exist_ok=True)
    files=[p for p in REVIEW.rglob('*') if p.is_file() and p.suffix in ['.html','.json','.jsonl','.md','.ics','.png','.srt','.mp4']]
    paths=reference_paths()+[p for pat in ['tools/video/*v3*','tools/video/*v4*','tools/video/month_one_core.py','tools/video/build_month_one.py','tools/video/synthesize_month_one.py','tools/video/check_month_one_audio.py','tools/video/month_one_metrics.py','tools/calendar/build_month_one_v3.py','content/mvp/time-audit/fonts/*','tests/*v4*','package.json','package-lock.json'] for p in ROOT.glob(pat) if p.is_file()]
    extras={'RESTORE.txt':'Compare before restoring source files into a matching fitness checkout. Install dependencies with npm ci and Python Pillow; provide local FFmpeg. Retained narration belongs in fitness/.local/month-one-v3/voice. Run produce_month_one_v4.py render, then variants R/G for B04 B08, B03 --no-citation, render_supporting_v4.cjs and package_month_one_v4.py. No provider key is needed to render retained audio. Archive packaging uses the original private-value scanner when a local Fish profile is configured. Public source is a production subset, not a complete repository backup.\n'}
    for folder in (VOICE_WORKSPACE/'voice').glob('B*'):
        paths.extend([folder/'narration.wav',folder/'alignment.json']);r=json.loads((folder/'generation.json').read_text());r.pop('voice',None)
        extras[str(Path('fitness')/(folder/'generation.json').relative_to(ROOT))]=json.dumps(r,indent=2)+'\n'
    paths+=list((VOICE_WORKSPACE/'audio-qa').glob('*/*.json'))
    receipt=dict(review=zip_files(DELIVERY/'Rep_and_Reason_Training_Club_Month_Review.zip',[(p,str(Path('Rep_and_Reason_Training_Club')/p.relative_to(REVIEW))) for p in files]),sources=zip_files(DELIVERY/'Rep_and_Reason_Training_Club_Month_Sources.zip',[(p,str(Path('fitness')/p.relative_to(ROOT))) for p in set(paths)],extras),public_upload=False)
    write_json(DELIVERY/'delivery-receipt.json',receipt);return receipt

def main():
    result=verify();build_hub(result);print(json.dumps(archive(),indent=2))

if __name__=='__main__':main()
