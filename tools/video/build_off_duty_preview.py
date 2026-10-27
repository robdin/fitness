"""Build review comparisons from existing masters. Never alters the month or publishes."""
import hashlib,html,json,shutil,subprocess,sys,zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.local/blueprint-character-d-preview'
ORIGINAL=ROOT/'.local/month-one-v5-blueprint/review'
DELIVERY=ROOT.parent/'fitness-deliverables/blueprint-character-d-preview'
IDS=['BP04','BP11','BP16']
def run(*args):return subprocess.run(list(map(str,args)),capture_output=True,text=True,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):return json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',p).stdout)
def audio_md5(p):return run('ffmpeg','-v','error','-i',p,'-map','0:a:0','-c','copy','-f','md5','-').stdout.strip()
def main():
 run('node',ROOT/'tools/video/render_off_duty_preview.cjs')
 reports=[]
 for id in IDS:
  folder=OUT/id;src=ORIGINAL/id/f'{id}-motion.mp4';source_receipt=json.loads((src.parent/'verification-motion.json').read_text())
  assert sha(src)==source_receipt['sha256'],'Source master changed'
  baseline=folder/f'{id}-without-character.mp4';shutil.copy2(src,baseline)
  shutil.copy2(src.parent/f'{id}.srt',folder/f'{id}.srt')
  shutil.copy2(src.parent/'posting-copy.json',folder/'posting-copy.json')
  with Image.open(folder/'overlay.png') as im:
   assert im.mode=='RGBA' and im.size==(1080,1920)
   bbox=im.getchannel('A').getbbox();assert bbox and bbox[1]>=1510
   assert im.getchannel('A').crop((0,0,1080,1510)).getextrema()==(0,0)
  meta=probe(src);vs=next(s for s in meta['streams'] if s['codec_type']=='video');frames=int(vs['nb_frames']);duration=float(vs['duration'])
  char=folder/f'{id}-with-character.mp4'
  run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',src,'-loop','1','-i',folder/'overlay.png','-filter_complex','[0:v][1:v]overlay=0:0:format=yuv420:shortest=1[v]','-map','[v]','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-r','30','-frames:v',frames,'-c:a','copy','-movflags','+faststart',char)
  pair=folder/f'{id}-side-by-side.mp4'
  run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',src,'-i',char,'-loop','1','-i',folder/'comparison-header.png','-filter_complex','[0:v][1:v]hstack=inputs=2:shortest=1[row];[2:v][row]vstack=inputs=2:shortest=1,format=yuv420p[v]','-map','[v]','-map','0:a:0','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-r','30','-frames:v',frames,'-c:a','copy','-movflags','+faststart',pair)
  entries=[]
  for p in [baseline,char,pair]:
   m=probe(p);v=next(s for s in m['streams'] if s['codec_type']=='video');a=next(s for s in m['streams'] if s['codec_type']=='audio')
   assert v['r_frame_rate']=='30/1' and int(v['nb_frames'])==frames
   assert (v['width'],v['height'])==((2160,2060) if p==pair else (1080,1920))
   assert abs(float(v['duration'])-duration)<.034
   assert a['codec_name']=='aac' and a['sample_rate']=='48000'
   run('ffmpeg','-v','error','-i',p,'-f','null','-')
   entries.append({'file':str(p.relative_to(OUT)),'sha256':sha(p),'audio_md5':audio_md5(p),'duration_seconds':float(v['duration']),'frames':frames,'full_decode':'passed'})
  assert len({x['audio_md5'] for x in entries})==1,'Audio changed'
  for t,name in [(.5,'cover'),(7,'midpoint')]:run('ffmpeg','-hide_banner','-loglevel','error','-y','-ss',t,'-i',pair,'-frames:v','1',folder/f'{name}.png')
  reports.append({'id':id,'baseline_byte_identical':sha(baseline)==sha(src),'overlay_alpha_bbox':bbox,'audio_identical':True,'source_script_sha256':source_receipt['script_sha256'],'outputs':entries})
  print(id+' complete: matched audio, duration and frame count',flush=True)
 receipt={'status':'creative_preview_not_audience_test','character':'D / Off-Duty Hero','episodes':reports,'canonical_production_changed':False,'public_upload':False,'sprite_sha256':sha(OUT/'assets/off-duty-poses.png'),'renderer_sha256':sha(ROOT/'tools/video/render_off_duty_preview.cjs'),'notes':['The original masters are copied byte-for-byte. Character editions overlay only the decorative area below y=1510; video re-encoding can introduce small compression differences elsewhere.','Source cues, caption timings and wording come directly from the original decoded video.','The character is a still illustration, with no lip synchronization or generated motion.','This placement preserves the teaching area but may be partly covered by native platform overlays.']}
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
 build_hub(receipt)
 DELIVERY.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(DELIVERY/'Off_Duty_Hero_Comparisons.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(OUT.rglob('*')):
   if p.is_file():z.write(p,str(Path('Off_Duty_Hero_Comparisons')/p.relative_to(OUT)))
  for name in ['render_off_duty_preview.cjs','build_off_duty_preview.py']:z.write(ROOT/'tools/video'/name,'Off_Duty_Hero_Comparisons/source/'+name)
 with zipfile.ZipFile(DELIVERY/'Off_Duty_Hero_Comparisons.zip') as z:assert z.testzip() is None
 print(str(OUT/'index.html'));print(str(DELIVERY/'Off_Duty_Hero_Comparisons.zip'))

def build_hub(receipt):
 titles={'BP04':'A walk in your real week','BP11':'Tomorrow’s lunch','BP16':'Returning after a missed workout'}
 css='''*{box-sizing:border-box}body{margin:0;background:#F3F5F4;color:#173249;font:17px/1.55 system-ui,sans-serif}main{max-width:1150px;margin:auto;padding:30px 24px}h1{font-size:clamp(30px,5vw,52px);line-height:1.1}h2{font-size:25px}a{color:#2348C6}nav{display:flex;gap:20px;flex-wrap:wrap}section{padding:25px 0;border-top:1px solid #b5c4d1;scroll-margin-top:12px}video{display:block;width:100%;max-height:82vh;background:#2348C6}p{max-width:850px}.meta{font-size:14px}.links{display:flex;gap:18px;flex-wrap:wrap}.zoom{display:block;width:100%;height:auto;margin-top:15px}summary{cursor:pointer} @media(max-width:500px){main{padding:20px 12px}h2{font-size:21px}}'''
 page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Off-Duty Hero · matched content previews</title><style>'+css+'</style><main><h1>D — Off-Duty Hero<br>in the actual content</h1><p>Left: the existing Blueprint master. Right: the same clip with D in the lower decorative area. Each comparison is one synchronized video with one audio track.</p><nav>'+''.join(f'<a href="#{i}">{html.escape(titles[i])}</a>' for i in IDS)+'</nav><p class="meta">Creative review only. These three previews do not change the full month or establish an audience winner. The character is a still illustration; native social overlays may partly cover this placement.</p>']
 for ep in receipt['episodes']:
  id=ep['id'];page.append(f'<section id="{id}"><h2>{html.escape(titles[id])}</h2><video controls playsinline preload="metadata" poster="{id}/cover.png" src="{id}/{id}-side-by-side.mp4" aria-label="{id} synchronized side-by-side comparison"></video><p class="links"><a href="{id}/{id}-side-by-side.mp4" download>Download comparison</a><a href="{id}/{id}-without-character.mp4">Original at full size</a><a href="{id}/{id}-with-character.mp4">Character version at full size</a></p><details><summary>Inspect a still frame</summary><img class="zoom" src="{id}/midpoint.png" alt="{html.escape(titles[id])}: original on the left and character version on the right"></details></section>')
 page.append('<p class="meta">Checked: original master hashes, identical encoded audio, matched runtime/frame count, full decoding and transparent overlay bounds. No new narration requests. <a href="verification.json">Verification receipt</a> · <a href="generation.json">Asset source and prompt</a></p></main></html>')
 (OUT/'index.html').write_text(''.join(page))
if __name__=='__main__':main()
