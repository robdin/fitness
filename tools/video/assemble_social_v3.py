"""Render in bounded processes so native image memory is released between chunks."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--work',type=Path,default=ROOT/'.local/social-v3')
    p.add_argument('--out',type=Path,default=ROOT.parent/'deliverables/v3')
    p.add_argument('--skip-prepare',action='store_true')
    args=p.parse_args()
    args.work=args.work.resolve();args.out=args.out.resolve()
    args.out.mkdir(parents=True,exist_ok=True)
    if not args.skip_prepare:
        subprocess.run([sys.executable,str(ROOT/'tools/video/prepare_social_v3.py'),'--out',str(args.work)],check=True)
    tl=json.loads((args.work/'timeline.json').read_text())
    node=os.environ.get('CODEX_PRIMARY_RUNTIME_NODE','node')
    env=os.environ.copy()
    if 'NODE_PATH' not in env and 'CODEX_PRIMARY_RUNTIME_NODE_MODULES' in env:
        env['NODE_PATH']=env['CODEX_PRIMARY_RUNTIME_NODE_MODULES']
    cmd=[node,'--expose-gc',str(ROOT/'tools/video/render_social_v3.cjs'),str(args.work),str(args.out)]
    subprocess.run(cmd+['--stills'],env=env,check=True)
    pieces=[]
    # Each child exits after five seconds of video, bounding Skia's native cache.
    for start in range(0,round(tl['duration']*tl['fps']),150):
        subprocess.run(cmd+['--range',str(start),'150'],env=env,check=True)
        pieces.append(args.out/f'segment-{start:05}.mp4')
    concat=args.work/'segments.txt'
    concat.write_text(''.join("file '"+str(p).replace("'", "'\\''")+"'\n" for p in pieces))
    final=args.out/'Rep_and_Reason_Time_Audit_V3.mp4'
    pending=args.out/'Rep_and_Reason_Time_Audit_V3.partial.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),
                    '-i',str(args.work/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy',
                    '-c:a','aac','-b:a','192k','-t',str(tl['duration']),'-movflags','+faststart',
                    str(pending)],check=True)
    subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(pending)],check=True)
    pending.replace(final)
    print('COMPLETE',final,flush=True)


if __name__=='__main__':
    main()
