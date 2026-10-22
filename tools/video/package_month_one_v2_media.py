"""Verify the exact N-series media, then package a portable, private review hub.

No provider requests, publishing or approval. Only explicitly listed files enter
archives; private profiles and arbitrary .local files are never collected.
"""
import hashlib
import html
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from PIL import Image
from month_one_core import ROOT, digest, script, normalized
from produce_month_one_v2 import episodes, WORKSPACE, RENDERER
from build_month_one import probe
sys.path.insert(0,str(ROOT/'tools/calendar'))
from build_month_one_v2 import load, source_map, posting_copy

REVIEW=WORKSPACE/'review'
DELIVERY=ROOT.parent/'fitness-deliverables/month-one-v2-media'

def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n')

def verify_export(ep,treatment):
    folder=REVIEW/ep['id'];file=folder/f"{ep['id']}-{treatment}.mp4"
    receipt=json.loads((folder/f'verification-{treatment}.json').read_text())
    tl=json.loads((folder/'timeline.json').read_text())
    expected=hashlib.sha256(script(ep).encode()).hexdigest()
    if tl['episode']!=ep or tl['script_sha256']!=expected or receipt['script_sha256']!=expected:
        raise ValueError(f"{ep['id']}: stale script or graphic configuration")
    if receipt['sha256']!=digest(file) or receipt['timeline_sha256']!=digest(folder/'timeline.json') or receipt['renderer_sha256']!=digest(RENDERER):
        raise ValueError(f"{ep['id']}: stale media/timeline/renderer hash")
    assert receipt['full_decode']=='passed' and receipt['voice_present'] and tl['timing']=='provider_word_alignment'
    assert normalized(script(ep))==normalized(' '.join(c['text'] for c in tl['captions']))
    assert all(0<=c['start']<c['end']<=tl['duration'] and c['cps']<=20.01 for c in tl['captions'])
    assert all(a['end']<=b['start']+.001 for a,b in zip(tl['captions'],tl['captions'][1:]))
    voice=WORKSPACE/'voice'/ep['id'];generation=json.loads((voice/'generation.json').read_text())
    assert generation['status']=='complete' and generation['script_sha256']==expected
    assert generation['audio_sha256']==digest(voice/'narration.wav') and generation['alignment_sha256']==digest(voice/'alignment.json')
    meta=probe(file);v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['codec_name'],v['r_frame_rate'])==(1080,1920,'h264','30/1')
    assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
    assert int(v['nb_frames'])==round(tl['duration']*30) and abs(float(meta['format']['duration'])-tl['duration'])<.04
    assert -18<=float(receipt['loudness']['input_i'])<=-14 and float(receipt['loudness']['input_tp'])<=-1
    return {'file':str(file.relative_to(REVIEW)),'sha256':digest(file),'bytes':file.stat().st_size,'duration':receipt['duration'],'frames':receipt['frames'],'max_cps':receipt['max_cps'],'loudness':receipt['loudness']}

def verify_all():
    exports=[verify_export(e,t) for e in episodes() for t in (['motion','static'] if e['id']=='N01' else ['motion'])]
    audio=[]
    for t in ['motion','static']:
        audio.append(subprocess.run(['ffmpeg','-v','error','-i',str(REVIEW/'N01'/f'N01-{t}.mp4'),'-map','0:a:0','-c','copy','-f','md5','-'],capture_output=True,text=True,check=True).stdout)
    assert len(set(audio))==1,'Comparison audio differs'
    subprocess.run(['node',str(ROOT/'tools/video/verify_v2_frames.cjs')],check=True,capture_output=True)
    frame_check=json.loads((REVIEW/'frame-check.json').read_text())
    support=json.loads((REVIEW/'supporting/manifest.json').read_text())
    assert support['content_sha256']==digest(ROOT/'content/month-one-v2/calendar.json')
    assert support['renderer_sha256']==digest(ROOT/'tools/video/render_supporting_v2.cjs')
    assert len(support['outputs'])==36
    for item in support['outputs']:
        p=REVIEW/'supporting'/item['file'];assert digest(p)==item['sha256']
        with Image.open(p) as im:assert im.size==((1080,1350) if item['file'].startswith('K') else (1080,1920))
    asr=[]
    for e in episodes():
        reports=[]
        for model in ['base.en','small.en']:
            p=WORKSPACE/'audio-qa'/model/(e['id']+'.json')
            if p.exists():
                r=json.loads(p.read_text());assert r['audio_sha256']==digest(WORKSPACE/'voice'/e['id']/'narration.wav')
                reports.append({'model':model,'differences':r['differences']})
        assert reports and reports[0]['model']=='base.en'
        asr.append({'id':e['id'],'reports':reports,'human_listening_review':False})
    result={'status':'narrated_review_assets_complete_human_review_pending','core_episodes':16,'video_exports':len(exports),
        'carousel_panels':20,'story_frames':16,'duration_seconds_range':[min(e['duration'] for e in exports),max(e['duration'] for e in exports)],
        'decode_passes':len(exports),'max_caption_cps':max(e['max_cps'] for e in exports),'frames_checked':frame_check['frames'],
        'comparison_audio_identical':True,'fish_requests_submitted':len(list((WORKSPACE/'voice').glob('N*/generation.json'))),
        'provider_actual_charge':None,'new_image_generation_requests':0,'human_listening_review':False,'target_uploader_preview':False,
        'live_audience_observations':0,'hands_on_labor_measured':False,'public_upload':False,'asr_review':asr,'outputs':exports}
    write_json(REVIEW/'verification-summary.json',result)
    write_json(ROOT/'examples/month-one-v2/production-verification.json',result)
    return result

def build_hub(result):
    data,sources,plan=load();sm=source_map(sources);esc=html.escape
    # These copies keep all review links usable after extracting the ZIP.
    resources={'calendar.ics':'content/month-one-v2/calendar.ics','CALENDAR.md':'content/month-one-v2/CALENDAR.md',
      'SCRIPTS.md':'content/month-one-v2/SCRIPTS.md','SOURCE_MAP.md':'content/month-one-v2/SOURCE_MAP.md',
      'experiment.json':'experiments/month-one-v2.json','PRODUCTION.md':'docs/MONTH_ONE_V2_PRODUCTION.md',
      'calendar.json':'content/month-one-v2/calendar.json','sources.json':'research/month-one-demand-v2.json'}
    for name,source in resources.items():
        content=(ROOT/source).read_bytes()
        if name.endswith('.md'):
            s=content.decode().replace('../../docs/MONTH_ONE_V2_PRODUCTION.md','PRODUCTION.md').replace('../examples/month-one-v2/production-verification.json','verification-summary.json').replace('](MONTH_ONE_V2.md)','](experiment.json)').replace('../../research/month-one-demand-v2.json','sources.json')
            content=s.encode()
        (REVIEW/name).write_bytes(content)
    nav=' · '.join(f'<a href="#week-{i}">Week {i}</a>' for i in range(1,5))
    page=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rep & Reason · November content</title><style>
    *{box-sizing:border-box}body{margin:0;background:#F7F4EA;color:#10233E;font:17px/1.6 system-ui,sans-serif}main{max-width:1160px;margin:auto;padding:42px 24px}h1{font-size:clamp(42px,7vw,78px);line-height:1.02;letter-spacing:-.045em;max-width:900px}h2{line-height:1.2}a{color:#104C76}header{padding-bottom:30px;border-bottom:2px solid #10233E}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:700}.note{color:#53616B}.stat{display:flex;gap:35px;flex-wrap:wrap}.stat b{display:block;font-size:34px}article{display:grid;grid-template-columns:270px 1fr;gap:36px;padding:32px 0;border-top:1px solid #CBD0C4}video{width:100%;border-radius:12px;background:#10233E}.copy{padding:10px 0}details{padding:12px 0}summary{cursor:pointer;font-weight:600}.strip{display:flex;gap:12px;overflow-x:auto;padding:12px 0}.strip img{height:300px;border-radius:8px}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:600px}.block{background:#E7EBDA;padding:25px;border-radius:20px;margin:28px 0}pre{white-space:pre-wrap;font:14px/1.6 system-ui}section{scroll-margin-top:20px}.tag{background:#DDECB8;border-radius:14px;padding:5px 12px;display:inline-block;font-size:13px}@media(max-width:680px){article{grid-template-columns:1fr;gap:8px}article video{max-width:330px;display:block;margin:auto}main{padding:25px 18px}.strip img{height:240px}.comparison{gap:12px}}
    </style><main><header><p class="eyebrow">REP & REASON · NOVEMBER 2026 · REVIEW EDITION</p><h1>A month of useful<br>fitness explanations.</h1><p>Original scripts shaped by creator topics, community questions and separately checked research.</p><div class="stat"><span><b>16</b>narrated videos</span><span><b>4</b>five-panel carousels</span><span><b>8</b>two-frame stories</span><span><b>26–33s</b>video length</span></div><p class="note">Rendered for review. Full listening/editorial review and real audience testing remain pending. Nothing is scheduled or published.</p>''',f'<nav>{nav} · <a href="#comparison">Motion comparison</a> · <a href="#checks">Checks & next steps</a></nav><p><a href="calendar.ics">Planning calendar</a> · <a href="CALENDAR.md">Full schedule</a> · <a href="SOURCE_MAP.md">Source map</a></p></header>']
    for week in range(1,5):
        page.append(f'<section id="week-{week}"><h2>Week {week}</h2>')
        for e in data['episodes']:
            if e['week']!=week:continue
            id=e['id'];folder=REVIEW/id;package={'id':id,'proposed_publish_at':e['publish_at'],'youtube_title':e['title'],
                'youtube_description':posting_copy(e,sm,'YouTube'),'instagram_caption':posting_copy(e,sm,'Instagram'),
                'hook_type':e['hook_type'],'creator_ids':e['creator_ids'],'community_ids':e['community_ids'],'evidence_ids':e['evidence_ids'],
                'human_review_pending':True,'public_upload':False}
            write_json(folder/'posting-copy.json',package)
            speech=' '.join(b['narration'] for b in e['beats'])
            links=''.join(f'<li><a href="{esc(sm[s]["url"])}">{esc(sm[s].get("label",sm[s].get("title",s)))}</a></li>' for s in e['evidence_ids'])
            if not links:links='<li>Original editorial planning checklist; demand links in the source map.</li>'
            page.append(f'<article id="{id}"><video controls playsinline preload="metadata" poster="{id}/cover.png" src="{id}/{id}-motion.mp4" aria-label="{id} {esc(e["title"])}"></video><div class="copy"><p class="eyebrow">November {e["day"]} · {id} · {e["cluster"]}</p><h2>{esc(e["title"])}</h2><span class="tag">Narrated review export</span><p>{esc(e["caption"])}</p><p><a href="{id}/{id}-motion.mp4" download>Download video</a> · <a href="{id}/{id}.srt">Captions</a> · <a href="{id}/posting-copy.json">Posting copy</a></p><details><summary>Script and research</summary><p>{esc(speech)}</p><ul>{links}</ul><p><b>Viewer check:</b> {esc(e["comprehension"]["question"])}</p><p><b>Avoid this misunderstanding:</b> {esc(e["comprehension"]["critical_error"])}</p></details><details><summary>Copy for the post</summary><pre>{esc(package["instagram_caption"])}</pre></details></div></article>')
        for p in data['supporting_posts']:
            if (p['day']-1)//7+1!=week:continue
            id=p['id'];story=p['kind']=='story';names=['prompt.png','followup.png'] if story else [f'{i}.png' for i in range(1,6)]
            evidence=sorted({s for e in data['episodes'] if e['id'] in p['episode_ids'] for s in e['evidence_ids']})
            package={**p,'status':'rendered_review_pending','evidence':[sm[s] for s in evidence], 'public_upload':False}
            if story:package['native_poll_placement']={'x':112,'y':1010,'width':762,'height':205,'instruction':'Add one real native poll with the two specified options; the image itself is not interactive.'}
            write_json(REVIEW/'supporting'/id/'posting-copy.json',package)
            page.append(f'<section id="{id}"><p class="eyebrow">November {p["day"]} · {id} · {p["kind"]}</p><h2>{esc(p["title"])}</h2><div class="strip">'+''.join(f'<a href="supporting/{id}/{n}"><img loading="lazy" src="supporting/{id}/{n}" alt="{id} frame {i+1}"></a>' for i,n in enumerate(names))+f'</div><p>{esc(p.get("caption","Add a native poll: "+" / ".join(p["frames"][0]["options"]) if story else ""))}</p><a href="supporting/{id}/posting-copy.json">Posting instructions and source notes</a></section>')
        page.append('</section>')
    page.append('''<section id="comparison" class="block"><h2>Does motion help this explanation?</h2><p>Same N01 script, captions, composition, timing and encoded audio. Only interpolated movement changes. The static version is a review control, not a second scheduled post.</p><div class="comparison"><div><h3>A · Static</h3><video controls playsinline preload="metadata" src="N01/N01-static.mp4"></video></div><div><h3>B · Motion</h3><video controls playsinline preload="metadata" src="N01/N01-motion.mp4"></video></div></div><p>Show one version first, alternate which version is assigned first, collect an unaided takeaway and limits, then ask about preference. This optional usability comparison does not prove retention lift.</p></section>''')
    flagged=[r['id'] for r in result['asr_review'] if any(x['differences'] for x in r['reports'])]
    page.append(f'<section id="checks" class="block"><h2>What is checked—and what needs you</h2><p>All 17 exports decode; all {result["frames_checked"]:,} core-video frames pass text-bound checks. Captions preserve the full scripts at no more than 20 characters per second. Voice speed and pitch are preserved.</p><p>Independent speech recognition has reviewed all 16 tracks. Differences are flagged for listening in {", ".join(flagged)}; recognition errors are not proof of spoken errors. See the <a href="verification-summary.json">exact verification record</a>.</p><p>Review the full audio and claims, then check each export in the target uploader. Add native story polls there. Audience observations, comprehension scores, measured hands-on hours and provider charges remain uncollected.</p><p><a href="PRODUCTION.md">Production and review guide</a> · <a href="experiment.json">Go / iterate / no-go protocol</a></p></section></main></html>')
    (REVIEW/'index.html').write_text(''.join(page))

def archive():
    data,_,_=load();files=[REVIEW/n for n in ['index.html','verification-summary.json','frame-check.json','calendar.ics','CALENDAR.md','SCRIPTS.md','SOURCE_MAP.md','experiment.json','PRODUCTION.md','calendar.json','sources.json']]
    for e in episodes():
        folder=REVIEW/e['id'];names=['cover.png','timeline.json','layout.json',e['id']+'.srt','posting-copy.json']+[f'scene-{i}.png' for i in range(6)]
        for treatment in (['motion','static'] if e['id']=='N01' else ['motion']):names.extend([f'{e["id"]}-{treatment}.mp4',f'verification-{treatment}.json'])
        files.extend(folder/n for n in names)
    files.extend(REVIEW/'supporting'/n for n in ['manifest.json','layout.json'])
    for p in data['supporting_posts']:
        names=['prompt.png','followup.png'] if p['kind']=='story' else [f'{i}.png' for i in range(1,6)]
        files.extend(REVIEW/'supporting'/p['id']/n for n in names+['posting-copy.json'])
    DELIVERY.mkdir(parents=True,exist_ok=True)
    review_zip=DELIVERY/'Rep_and_Reason_November_Content_Review.zip'
    sources_zip=DELIVERY/'Rep_and_Reason_November_Production_Sources.zip'
    def zip_files(target,pairs,extras=None):
        manifest=[]
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for file,name in sorted(pairs,key=lambda x:x[1]):
                z.write(file,name);manifest.append({'path':name,'sha256':digest(file),'bytes':file.stat().st_size})
            for name,body in (extras or {}).items():z.writestr(name,body);manifest.append({'path':name,'sha256':hashlib.sha256(body.encode()).hexdigest(),'bytes':len(body.encode())})
            z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
        with zipfile.ZipFile(target) as z:
            assert z.testzip() is None
            assert not any('fish.env' in n or 'fish-profile' in n for n in z.namelist())
        return {'file':str(target),'sha256':digest(target),'bytes':target.stat().st_size,'files':len(manifest)}
    review=zip_files(review_zip,[(p,str(Path('Rep_and_Reason_November')/p.relative_to(REVIEW))) for p in files])
    source_paths=[]
    for pattern in ['content/month-one-v2/*','research/month-one-demand-v2.json','experiments/month-one-v2.json','tools/video/*month_one*.py','tools/video/render_month_one_v2.cjs','tools/video/render_supporting_v2.cjs','tools/video/verify_v2_frames.cjs','tools/calendar/*month_one_v2.py','tools/calendar/review_template.html','content/mvp/time-audit/fonts/*','tests/*month*','docs/MONTH_ONE_V2*.md','measurement/month-one-v2*','examples/month-one-v2/*.json','package.json','package-lock.json']:
        source_paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
    extras={'RESTORE.txt':'Restore fitness/.local/month-one-v2/voice to this repository checkout. Rendering needs no API key when retained narration exists. Install pinned dependencies, then run produce_month_one_v2.py render. Do not overwrite newer authored files without comparing them. Private credentials/profile are excluded. Nothing has been publicly uploaded.\n'}
    for e in episodes():
        folder=WORKSPACE/'voice'/e['id'];source_paths.extend(folder/n for n in ['narration.wav','alignment.json'])
        r=json.loads((folder/'generation.json').read_text());r.pop('voice',None)
        extras[str(Path('fitness')/(folder/'generation.json').relative_to(ROOT))]=json.dumps(r,indent=2)+'\n'
        for model in ['base.en','small.en']:
            p=WORKSPACE/'audio-qa'/model/(e['id']+'.json')
            if p.exists():source_paths.append(p)
    sources=zip_files(sources_zip,[(p,str(Path('fitness')/p.relative_to(ROOT))) for p in set(source_paths)],extras)
    receipt={'review':review,'sources':sources,'public_upload':False}
    write_json(DELIVERY/'delivery-receipt.json',receipt)
    return receipt

def main():
    result=verify_all();build_hub(result);print(json.dumps(archive(),indent=2))

if __name__=='__main__':main()
