"""Verify and package the research-led B-series. No network or publication."""
import hashlib,html,json,re,shutil,subprocess,sys,zipfile
from pathlib import Path
from PIL import Image
from month_one_core import ROOT,digest,script,normalized
from produce_month_one_v3 import episodes,WORKSPACE,RENDERER
from build_month_one import probe
sys.path.insert(0,str(ROOT/'tools/calendar'))
from build_month_one_v3 import load,source_map,posting_copy,validate
REVIEW=WORKSPACE/'review';DELIVERY=ROOT.parent/'fitness-deliverables/month-one-v3'

def write_json(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def validate_identity(ep,receipt,tl):
 expected=hashlib.sha256(script(ep).encode()).hexdigest()
 if tl['episode']!=ep or tl['script_sha256']!=expected or receipt['script_sha256']!=expected:raise ValueError('Stale script, brand, asset or graphic configuration')
 if tl['timing']!='provider_word_alignment':raise ValueError('Final export needs provider timing')
 if normalized(script(ep))!=normalized(' '.join(c['text'] for c in tl['captions'])):raise ValueError('Caption text differs')

def verify_export(ep,treatment='motion',workspace=WORKSPACE):
 folder=workspace/'review'/ep['id'];file=folder/f"{ep['id']}-{treatment}.mp4";receipt=json.loads((folder/f'verification-{treatment}.json').read_text());tl=json.loads((folder/'timeline.json').read_text())
 validate_identity(ep,receipt,tl)
 assert receipt['sha256']==digest(file) and receipt['timeline_sha256']==digest(folder/'timeline.json') and receipt['renderer_sha256']==digest(RENDERER)
 assert receipt['full_decode']=='passed' and receipt['voice_present']
 assert all(0<=c['start']<c['end']<=tl['duration'] and c['cps']<=20.01 for c in tl['captions'])
 assert all(a['end']<=b['start']+.001 for a,b in zip(tl['captions'],tl['captions'][1:]))
 voice=WORKSPACE/'voice'/ep['id'];generation=json.loads((voice/'generation.json').read_text())
 assert generation['status']=='complete' and generation['script_sha256']==tl['script_sha256']
 assert generation['audio_sha256']==digest(voice/'narration.wav') and generation['alignment_sha256']==digest(voice/'alignment.json')
 meta=probe(file);v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['codec_name'],v['r_frame_rate'])==(1080,1920,'h264','30/1')
 assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
 assert int(v['nb_frames'])==round(tl['duration']*30) and abs(float(meta['format']['duration'])-tl['duration'])<.04
 assert -18<=float(receipt['loudness']['input_i'])<=-14 and float(receipt['loudness']['input_tp'])<=-1
 # Re-decode the final artifact, rather than trusting a receipt for another byte stream.
 subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],check=True,capture_output=True)
 return dict(id=ep['id'],brand=ep['graphics']['brand'],treatment=treatment,sha256=digest(file),duration=receipt['duration'],frames=receipt['frames'],bytes=file.stat().st_size,max_cps=receipt['max_cps'],loudness=receipt['loudness'],answer_starts_seconds=round(tl['beats'][1]['start'],3))

def verify_all():
 d,s,p=load();validate(d,s,p)
 exports=[verify_export(e) for e in episodes()];exports.append(verify_export(episodes()[6],'static'))
 for brand in ['lab','notebook']:exports.append(verify_export(episodes(brand)[0],workspace=ROOT/('.local/month-one-v3-'+brand)))
 def audio_hash(p):return subprocess.run(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c','copy','-f','md5','-'],capture_output=True,text=True,check=True).stdout.strip()
 a=[audio_hash(REVIEW/'B01/B01-motion.mp4')]+[audio_hash(ROOT/f'.local/month-one-v3-{b}/review/B01/B01-motion.mp4') for b in ['lab','notebook']];assert len(set(a))==1
 assert audio_hash(REVIEW/'B07/B07-motion.mp4')==audio_hash(REVIEW/'B07/B07-static.mp4')
 subprocess.run(['node',str(ROOT/'tools/video/verify_v3_frames.cjs')],check=True,capture_output=True);frames=json.loads((REVIEW/'frame-check.json').read_text())
 support=json.loads((REVIEW/'supporting/manifest.json').read_text());assert support['content_sha256']==digest(ROOT/'content/month-one-v3/calendar.json');assert support['renderer_sha256']==digest(ROOT/'tools/video/render_supporting_v3.cjs');assert len(support['outputs'])==36
 for x in support['outputs']:
  path=REVIEW/'supporting'/x['file'];assert digest(path)==x['sha256']
  with Image.open(path) as im:assert im.size==((1080,1350) if x['file'].startswith('BK') else (1080,1920))
 asr=[]
 for e in episodes():
  reports=[]
  for model in ['base.en','small.en']:
   path=WORKSPACE/'audio-qa'/model/(e['id']+'.json')
   if path.exists():
    r=json.loads(path.read_text());assert r['audio_sha256']==digest(WORKSPACE/'voice'/e['id']/'narration.wav'),'Stale ASR '+e['id'];reports.append(dict(model=model,differences=r['differences']))
  assert reports and reports[0]['model']=='base.en';asr.append(dict(id=e['id'],reports=reports,human_listening_review=False))
 receipts=list((WORKSPACE/'voice').glob('B*/generation.json'))+list((WORKSPACE/'voice-revisions').glob('B*/generation.json'))
 assert all(json.loads(x.read_text())['status']=='complete' for x in receipts)
 result=dict(status='narrated_review_package_complete_audience_validation_pending',core_episodes=16,video_exports=19,carousel_panels=20,story_frames=16,brand_packages=3,decode_passes=19,frames_checked=frames['frames'],max_caption_cps=max(x['max_cps'] for x in exports),duration_seconds_range=[min(x['duration'] for x in exports),max(x['duration'] for x in exports)],maximum_answer_start_seconds=max(x['answer_starts_seconds'] for x in exports),brand_comparison_audio_identical=True,motion_comparison_audio_identical=True,provider_requests_completed=len(receipts),retained_prior_voice_revisions=len(receipts)-16,provider_actual_charge=None,new_image_requests=0,human_listening_review=False,target_uploader_preview=False,target_audience_tests=0,live_audience_observations=0,hands_on_labor_measured=False,public_upload=False,asr_review=asr,outputs=exports)
 write_json(REVIEW/'verification-summary.json',result);write_json(ROOT/'examples/month-one-v3/production-verification.json',result);return result

CSS='''*{box-sizing:border-box}body{margin:0;background:#F5F3EA;color:#14221C;font:17px/1.6 system-ui}main{max-width:1180px;margin:auto;padding:40px 24px}h1{font-size:clamp(42px,7vw,80px);line-height:1.02;letter-spacing:-.04em}h2{line-height:1.2}a{color:#2149CA}header{border-top:12px solid #2149CA;padding:25px 0}nav{display:flex;gap:15px;flex-wrap:wrap}.eyebrow{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase}.note{color:#415248}.block{background:#E5EBCF;padding:24px;margin:28px 0;border-radius:12px}article{display:grid;grid-template-columns:260px 1fr;gap:32px;padding:32px 0;border-top:1px solid #BAC5AF}video{width:100%;border-radius:10px;background:#14221C}.brands{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.brands video{max-height:540px}details{padding:10px 0}summary{cursor:pointer;font-weight:600}.strip{display:flex;gap:12px;overflow:auto;padding:15px 0}.strip img{height:290px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #C7CEBF;padding:10px;text-align:left;vertical-align:top}pre{white-space:pre-wrap}section{scroll-margin-top:20px}.doc{max-width:900px}.doc h1{font-size:48px}.doc p{margin:18px 0}.doc li{margin:7px 0}@media(max-width:680px){article,.grid{grid-template-columns:1fr}.brands{gap:10px}.brands h3{font-size:15px}.brands p{font-size:13px}article video{max-width:320px;margin:auto}main{padding:20px 15px}.strip img{height:230px}.doc h1{font-size:36px}table{display:block;overflow:auto}}'''
def inline(t):
 t=html.escape(t);t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:'<a href="'+m[2].replace('.md','.html')+'">'+m[1]+'</a>',t);return re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',t)
def markdown_page(body):
 parts=[];lines=body.splitlines();i=0
 while i<len(lines):
  line=lines[i]
  if not line.strip():i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    row=[x.strip() for x in lines[i].strip('|').split('|')];i+=1
    if all(re.fullmatch(r'[:\- ]+',x) for x in row):continue
    rows.append(row)
   parts.append('<table>'+''.join('<tr>'+''.join(f'<{"th" if k==0 else "td"}>{inline(x)}</{"th" if k==0 else "td"}>' for x in row)+'</tr>' for k,row in enumerate(rows))+'</table>');continue
  if line.startswith('#'):
   n=min(6,len(line)-len(line.lstrip('#')));parts.append(f'<h{n}>{inline(line[n:].strip())}</h{n}>')
  elif line.startswith('- ') or re.match(r'^\d+\. ',line):parts.append('<p>• '+inline(re.sub(r'^(?:- |\d+\. )','',line))+'</p>')
  else:parts.append('<p>'+inline(line)+'</p>')
  i+=1
 return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS+'</style><main class="doc">'+''.join(parts)+'</main></html>'

def reference_paths():
 return [p for pat in ['research/audience-v3/*','content/month-one-v3/*','brand/v3/*','experiments/month-one-v3.json','docs/MONTH_ONE_V3.md','examples/month-one-v3/production-verification.json','measurement/month-one-v3*'] for p in ROOT.glob(pat) if p.is_file()]

def build_hub(result):
 d,s,p=load();sm=source_map(s);esc=html.escape
 for src in reference_paths():
  dest=REVIEW/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
  if src.suffix=='.md':dest.with_suffix('.html').write_text(markdown_page(src.read_text()))
 for brand in ['lab','notebook']:
  src=ROOT/f'.local/month-one-v3-{brand}/review/B01';dest=REVIEW/'brand'/brand;dest.mkdir(parents=True,exist_ok=True)
  for n in ['B01-motion.mp4','cover.png','timeline.json','verification-motion.json','B01.srt']:shutil.copy2(src/n,dest/n)
 page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rep & Reason · beginner month</title><style>'+CSS+'</style><main><header><p class="eyebrow">REP & REASON / RESEARCH EDITION / NOVEMBER 2026</p><h1>Make the next gym visit<br>less confusing.</h1><p>Five research perspectives applied to a new month of beginner fitness content.</p><nav><a href="#research">Research</a><a href="#brand">Three brand options</a><a href="#week-1">Week 1</a><a href="#week-2">Week 2</a><a href="#week-3">Week 3</a><a href="#week-4">Week 4</a><a href="#tests">Tests and decision</a></nav><p class="note">16 narrated masters · 4 carousels · 8 stories · 2 brand alternatives · 1 motion control. Review exports, not published posts. Audience validation and final listening/uploader review remain pending.</p></header>']
 page.append('<section id="research" class="block"><h2>The research, compiled</h2><div class="grid">')
 for name,title in [('01_PSYCHOLOGY','Psychology: questions and useful engagement'),('02_VIDEO_AND_DISTRIBUTION','Short-form video and platform evidence'),('03_BEGINNER_JOURNEY','Beginner needs and discovery routes'),('04_BRAND_STRATEGY','Brand strategy and three directions'),('05_WRITING_PLAYBOOK','Writing: tension with an honest payoff'),('06_INTEGRATION_AND_TESTING','Integration, rework audit and testing')]:page.append(f'<a href="research/audience-v3/{name}.html">{title}</a>')
 page.append('</div><p><a href="research/audience-v3/QUESTION_BANK.html">64-question bank</a> · <a href="research/audience-v3/SOURCE_REGISTER.html">34 research/guidance sources</a> · <a href="research/audience-v3/sources.json">Community and creator records</a></p><p><a href="content/month-one-v3/CALENDAR.html">Full schedule</a> · <a href="content/month-one-v3/calendar.ics">Importable planning calendar</a> · <a href="content/month-one-v3/SCRIPTS.html">All scripts</a></p></section>')
 page.append('<section id="brand"><h2>Three directions. One factual promise.</h2><p>Training Club was selected by the project owner. These B01 exports share exactly the same encoded narration and timing. The comparison changes the visual package, not just its color. No target-viewer preference test has run.</p><div class="brands">')
 for brand,title,desc in [('lab','A · Training Lab','Precise, analytical, modular.'),('club','B · Training Club','Direct, energetic, welcoming. Selected direction.'),('notebook','C · Coach’s Notebook','Calm, practical, personal.')]:
  prefix='B01' if brand=='club' else 'brand/'+brand
  page.append(f'<div><h3>{title}</h3><video controls playsinline preload="metadata" poster="{prefix}/cover.png" src="{prefix}/B01-motion.mp4"></video><p>{desc}</p></div>')
 page.append('</div><p><a href="brand/v3/STYLE_GUIDE.html">Complete style guide</a> · <a href="brand/comparison.png">Visual comparison board</a></p></section>')
 for week in range(1,5):
  page.append(f'<section id="week-{week}"><h2>Week {week}</h2>')
  for e in d['episodes']:
   if e['week']!=week:continue
   id=e['id'];pkg=dict(id=id,proposed_publish_at=e['publish_at'],youtube_title=e['title'],youtube_description=posting_copy(e,sm,'youtube'),instagram_caption=posting_copy(e,sm,'instagram'),hook_type=e['hook_type'],community_ids=e['community_ids'],evidence_ids=e['evidence_ids'],human_review_pending=True,public_upload=False);write_json(REVIEW/id/'posting-copy.json',pkg)
   links=''.join(f'<li><a href="{esc(sm[i]["url"])}">{esc(sm[i]["title"])}</a></li>' for i in e['evidence_ids']) or '<li>Original editorial planning or measurement checklist; community leads are in the source map.</li>'
   page.append(f'<article id="{id}"><video controls playsinline preload="metadata" poster="{id}/cover.png" src="{id}/{id}-motion.mp4" aria-label="{id} {esc(e["title"])}"></video><div><p class="eyebrow">NOV {e["day"]} / {id} / {e["cluster"]} / {e["hook_type"]} OPENING</p><h2>{esc(e["title"])}</h2><p>{esc(e["caption"])}</p><p><a href="{id}/{id}-motion.mp4" download>Download video</a> · <a href="{id}/{id}.srt">Captions</a> · <a href="{id}/posting-copy.json">Posting copy</a></p><details><summary>Script, support and comprehension check</summary><p>{esc(" ".join(b["narration"] for b in e["beats"]))}</p><ul>{links}</ul><p><strong>Expected takeaway:</strong> {esc(e["comprehension"]["answer"])}</p><p><strong>Critical misunderstanding:</strong> {esc(e["comprehension"]["critical_error"])}</p></details><details><summary>Instagram caption</summary><pre>{esc(pkg["instagram_caption"])}</pre></details></div></article>')
  for post in d['supporting_posts']:
   if (post['day']-1)//7+1!=week:continue
   id=post['id'];story=post['kind']=='story';names=['prompt.png','followup.png'] if story else [f'{i}.png' for i in range(1,6)];pkg={**post,'public_upload':False,'status':'rendered_review_pending'}
   if story:pkg['native_poll_placement']=dict(x=112,y=1010,width=762,height=205,instruction='Add one real native poll with the supplied options. Image alone is not interactive.')
   write_json(REVIEW/'supporting'/id/'posting-copy.json',pkg)
   page.append(f'<section><p class="eyebrow">NOV {post["day"]} / {id} / {post["kind"]}</p><h3>{esc(post["title"])}</h3><div class="strip">'+''.join(f'<a href="supporting/{id}/{name}"><img loading="lazy" src="supporting/{id}/{name}" alt="{id} panel {i+1}"></a>' for i,name in enumerate(names))+f'</div><a href="supporting/{id}/posting-copy.json">Copy and upload instructions</a></section>')
  page.append('</section>')
 page.append('<section id="tests" class="block"><h2>Test the explanation, then the business.</h2><p>B07 compares interpolated motion with a static control. Scene cuts, captions, content and encoded audio match. This is a usability stimulus, not a second scheduled post.</p><div class="grid"><div><h3>Motion</h3><video controls playsinline preload="metadata" src="B07/B07-motion.mp4"></video></div><div><h3>Static interpolation control</h3><video controls playsinline preload="metadata" src="B07/B07-static.mp4"></video></div></div>')
 flagged=[a['id'] for a in result['asr_review'] if a['reports'][-1]['differences']]
 page.append(f'<p>All 19 exports decode. {result["frames_checked"]:,} frames checked for text bounds; captions at ≤20 characters per second; text contrast benchmark passed. Final durations: {result["duration_seconds_range"][0]:.1f}–{result["duration_seconds_range"][1]:.1f} seconds. Answer beats begin by {result["maximum_answer_start_seconds"]:.1f} seconds.</p><p>Independent speech checks cover all tracks. Remaining differences for listening: {", ".join(flagged)}. Some are number spelling or word spacing; ASR does not establish a spoken error or replace listening.</p><p>Audience interest and recurring hands-on production must still be measured. The weekly cap is 12 hours. Publishing these prebuilt files alone does not measure the cost of making the next month.</p><p><a href="verification-summary.json">Verification receipt</a> · <a href="docs/MONTH_ONE_V3.html">Production/review guide</a> · <a href="experiments/month-one-v3.json">Frozen-before-launch decision protocol</a></p></section></main></html>')
 (REVIEW/'index.html').write_text(''.join(page))

def zip_files(target,pairs,extras=None):
 manifest=[]
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  for p,name in sorted(pairs,key=lambda x:x[1]):z.write(p,name);manifest.append(dict(path=name,sha256=digest(p),bytes=p.stat().st_size))
  for name,body in (extras or {}).items():z.writestr(name,body);manifest.append(dict(path=name,sha256=hashlib.sha256(body.encode()).hexdigest(),bytes=len(body.encode())))
  z.writestr('manifest.json',json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(target) as z:
  assert z.testzip() is None
  for item in manifest:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
  # Check actual private values without logging them; names alone are insufficient.
  from synthesize_month_one import read_key
  secrets=[read_key(),json.loads((ROOT/'.local/fish-profile.json').read_text())['voice_id']]
  for n in z.namelist():
   assert 'fish.env' not in n and 'fish-profile' not in n
   data=z.read(n);assert all(secret.encode() not in data for secret in secrets if secret),'Private value detected'
 return dict(file=str(target),bytes=target.stat().st_size,sha256=digest(target),files=len(manifest),manifest_verified=True,private_value_scan='passed')

def archive():
 DELIVERY.mkdir(parents=True,exist_ok=True)
 # Review directory is purpose-built; explicitly allow artifact types and paths, never arbitrary .local content.
 files=[p for p in REVIEW.rglob('*') if p.is_file() and p.suffix in ['.html','.json','.jsonl','.md','.ics','.png','.srt','.mp4']]
 assert not any(p.name.startswith('.') for p in files)
 source_paths=reference_paths()+[p for pat in ['tools/video/*v3*','tools/video/month_one_core.py','tools/video/build_month_one.py','tools/video/synthesize_month_one.py','tools/video/check_month_one_audio.py','tools/video/month_one_metrics.py','tools/calendar/build_month_one_v3.py','content/mvp/time-audit/fonts/*','tests/*v3*','examples/month-one-v3/*.json','package.json','package-lock.json'] for p in ROOT.glob(pat) if p.is_file()]
 extras={'RESTORE.txt':'Restore fitness files into a matching repository checkout after comparing changes. Put retained .local/month-one-v3/voice assets in place. Install the pinned dependencies and run produce_month_one_v3.py render. Retained narration needs no provider call. API keys and private profile are excluded. This archive is production source material, not a complete repository snapshot.\n'}
 for folder in list((WORKSPACE/'voice').glob('B*'))+list((WORKSPACE/'voice-revisions').glob('B*')):
  source_paths += [folder/n for n in ['narration.wav','alignment.json']]
  r=json.loads((folder/'generation.json').read_text());r.pop('voice',None);extras[str(Path('fitness')/(folder/'generation.json').relative_to(ROOT))]=json.dumps(r,indent=2)+'\n'
 source_paths += list((WORKSPACE/'audio-qa').glob('*/*.json'))+[WORKSPACE/'revision-log.json']
 receipt=dict(review=zip_files(DELIVERY/'Rep_and_Reason_Beginner_Month_Review.zip',[(p,str(Path('Rep_and_Reason_Beginner_Month')/p.relative_to(REVIEW))) for p in files]),sources=zip_files(DELIVERY/'Rep_and_Reason_Beginner_Month_Sources.zip',[(p,str(Path('fitness')/p.relative_to(ROOT))) for p in set(source_paths)],extras),public_upload=False)
 write_json(DELIVERY/'delivery-receipt.json',receipt);return receipt

def main():
 r=verify_all();build_hub(r);print(json.dumps(archive(),indent=2))
if __name__=='__main__':main()
