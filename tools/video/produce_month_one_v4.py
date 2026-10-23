"""Graphics-led Training Club production; reuse approved B-series narration."""
import argparse
import hashlib
import json
from types import SimpleNamespace
from produce_month_one_v3 import episodes as originals, WORKSPACE as VOICE_WORKSPACE
from month_one_core import ROOT
from build_month_one import build

WORKSPACE=ROOT/'.local/month-one-v4-graphics'
RENDERER=ROOT/'tools/video/render_month_one_v4.cjs'
CONFIG=ROOT/'content/month-one-v4/production.json'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def episodes(citation=True):
    config=json.loads(CONFIG.read_text())
    result=originals('club')
    for e in result:
        e['visual']='v4.1-graphics'
        e['graphics'].update(layout='full-width-graphics',
            source_cue=config['episodes'][e['id']],source_cue_visible=citation,
            production_sha256=digest(CONFIG))
    return result

def workspace_for(citation=True):
    return WORKSPACE if citation else ROOT/'.local/month-one-v4-graphics-no-citation'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['stills','render']);p.add_argument('--ids',nargs='+')
    p.add_argument('--no-citation',action='store_true')
    p.add_argument('--treatment',choices=['motion','static'],default='motion')
    p.add_argument('--width',type=int,choices=[720,1080],default=1080)
    args=p.parse_args();eps=episodes(not args.no_citation)
    if args.ids:
        unknown=set(args.ids)-{e['id'] for e in eps}
        if unknown:p.error('Unknown IDs: '+', '.join(sorted(unknown)))
        eps=[e for e in eps if e['id'] in args.ids]
    workspace=workspace_for(not args.no_citation);workspace.mkdir(parents=True,exist_ok=True)
    if not (workspace/'voice').exists():(workspace/'voice').symlink_to(VOICE_WORKSPACE/'voice',target_is_directory=True)
    settings=SimpleNamespace(stills=args.action=='stills',allow_silent=False,treatment=args.treatment,width=args.width)
    for e in eps:print(json.dumps(build(e,settings,workspace=workspace,renderer=RENDERER)),flush=True)

if __name__=='__main__':main()
