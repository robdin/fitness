"""Prepare, render and verify retained month-one outputs; never generates speech."""
import argparse
import json
import math
import subprocess
import time
import wave
import hashlib
from pathlib import Path
from month_one_core import ROOT, load_episodes, make_timeline, write_srt, digest, script
from voice_contract import validate_voice_receipt

def run(*args, capture=False):
    return subprocess.run(list(map(str,args)),check=True,capture_output=capture,text=capture)

def probe(path):
    return json.loads(run('ffprobe','-v','error','-show_streams','-show_format','-of','json',path,capture=True).stdout)

def build(ep,args,workspace=None,renderer=None):
    workspace=Path(workspace) if workspace is not None else ROOT/'.local/month-one'
    renderer=Path(renderer) if renderer is not None else ROOT/'tools/video/render_month_one.cjs'
    start=time.monotonic(); work=workspace/'build'/ep['id']; work.mkdir(parents=True,exist_ok=True)
    out=workspace/'review'/ep['id'];out.mkdir(parents=True,exist_ok=True)
    voice=workspace/'voice'/ep['id']; voiced=(voice/'narration.wav').exists()
    voice_check=None
    if voiced:
        if ep.get('voice_contract'):
            voice_check=validate_voice_receipt(ep,voice,**ep['voice_contract'])
        generation=json.loads((voice/'generation.json').read_text())
        if generation.get('status')!='complete' or generation.get('script_sha256')!=hashlib.sha256(script(ep).encode()).hexdigest():
            raise RuntimeError(f"{ep['id']}: current script does not have a complete narration receipt")
        if generation.get('audio_sha256')!=digest(voice/'narration.wav') or generation.get('alignment_sha256')!=digest(voice/'alignment.json'):
            raise RuntimeError(f"{ep['id']}: narration/alignment hash mismatch")
    alignment=json.loads((voice/'alignment.json').read_text()) if voiced else None
    dur=None
    if voiced:
        with wave.open(str(voice/'narration.wav')) as w: dur=w.getnframes()/w.getframerate()
    tl=make_timeline(ep,alignment,dur)
    if voiced and max(c['cps'] for c in tl['captions'])>20.01:
        raise RuntimeError(f"{ep['id']}: caption reading rate exceeds 20 cps; adjust before final rendering")
    (work/'timeline.json').write_text(json.dumps(tl,indent=2)+'\n')
    (out/'timeline.json').write_text(json.dumps(tl,indent=2)+'\n')
    write_srt(tl,out/f"{ep['id']}.srt")
    run('node',renderer,work/'timeline.json',out,'--stills','--treatment',args.treatment,capture=True)
    if args.stills: return {'id':ep['id'],'status':'stills','timing':tl['timing']}
    if not voiced and not args.allow_silent: raise RuntimeError(f"{ep['id']}: voice absent; use --allow-silent only for drafts")
    segments=work/args.treatment;segments.mkdir(exist_ok=True)
    frames=round(tl['duration']*30)
    for first in range(0,frames,150):
        run('node',renderer,work/'timeline.json',segments,'--range',first,min(150,frames-first),'--treatment',args.treatment,'--width',args.width,capture=True)
    paths=[segments/f'segment-{f:05}.mp4' for f in range(0,frames,150)]
    (segments/'concat.txt').write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in paths))
    target=out/f"{ep['id']}-{args.treatment}{'-silent-draft' if not voiced else ''}.mp4"
    temp=target.with_suffix('.partial.mp4')
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',segments/'concat.txt']
    if voiced:
        # Preserve the approved voice pitch and speed; narration-only mix.
        command+=['-i',voice/'narration.wav','-filter_complex',f'[1:a]adelay=120:all=1,apad,loudnorm=I=-16:TP=-1.5:LRA=9[a]','-map','0:v:0','-map','[a]','-c:a','aac','-b:a','192k','-ar','48000','-ac','2']
    command+=['-c:v','copy','-t',tl['duration'],'-movflags','+faststart',temp]
    run(*command); meta=probe(temp)
    run('ffmpeg','-v','error','-i',temp,'-f','null','-')
    temp.replace(target)
    report={'id':ep['id'],'file':target.name,'sha256':digest(target),'duration':float(meta['format']['duration']),
      'frames':int(next(s for s in meta['streams'] if s['codec_type']=='video')['nb_frames']),
      'full_decode':'passed','voice_present':voiced,'timing':tl['timing'],'render_elapsed_seconds':round(time.monotonic()-start,2),
      'caption_count':len(tl['captions']),'max_cps':round(max(c['cps'] for c in tl['captions']),3),
      'script_sha256':tl['script_sha256'],'public_upload':False,'human_listening_review':False}
    report['renderer_sha256']=digest(renderer)
    report['timeline_sha256']=digest(out/'timeline.json')
    report['width']=args.width;report['height']=args.width*16//9
    if voice_check is not None:report['voice_provenance']=voice_check
    if report['frames']!=frames:raise RuntimeError('Frame count mismatch')
    if voiced:
        result=run('ffmpeg','-hide_banner','-nostats','-i',target,'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-',capture=True)
        import re
        loud=json.loads(re.findall(r'\{\s*"input_i".*?\}',result.stderr,re.S)[-1]);report['loudness']={k:loud[k] for k in ['input_i','input_tp','input_lra']}
    (out/f'verification-{args.treatment}.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ids',nargs='+');p.add_argument('--stills',action='store_true');p.add_argument('--allow-silent',action='store_true');p.add_argument('--treatment',choices=['compact','large','motion'],default='motion');p.add_argument('--width',type=int,default=1080);args=p.parse_args()
    if args.width not in [720,1080]:p.error('Supported widths are 720 and 1080')
    for ep in load_episodes():
        if not args.ids or ep['id'] in args.ids: print(json.dumps(build(ep,args)),flush=True)
