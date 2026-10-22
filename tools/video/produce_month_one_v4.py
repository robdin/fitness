"""Training Club production candidates; reuse approved B-series narration."""
import argparse
import hashlib
import json
from types import SimpleNamespace
from produce_month_one_v3 import episodes as originals, WORKSPACE as VOICE_WORKSPACE
from month_one_core import ROOT
from build_month_one import build

WORKSPACE=ROOT/'.local/month-one-v4'
RENDERER=ROOT/'tools/video/render_month_one_v4.cjs'
CONFIG=ROOT/'content/month-one-v4/production.json'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def episodes(character='M',citation=True):
    if character not in ['M','R','G']:raise ValueError('Unknown character')
    config=json.loads(CONFIG.read_text())
    asset={'M':'guide-muscular.png','R':'guide-smaller.png','G':None}[character]
    result=originals('club')
    for e in result:
        e['visual']='v4'
        e['graphics'].update(character=character,character_asset='brand/v4/characters/'+asset if asset else None,
            character_sha256=digest(ROOT/'brand/v4/characters'/asset) if asset else None,
            source_cue=config['episodes'][e['id']],source_cue_visible=citation,
            production_sha256=digest(CONFIG))
    return result

def workspace_for(character='M',citation=True):
    return WORKSPACE if character=='M' and citation else ROOT/f'.local/month-one-v4-{character.lower()}{"" if citation else "-no-citation"}'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['stills','render']);p.add_argument('--ids',nargs='+')
    p.add_argument('--character',choices=['M','R','G'],default='M')
    p.add_argument('--no-citation',action='store_true')
    p.add_argument('--treatment',choices=['motion','static'],default='motion')
    p.add_argument('--width',type=int,choices=[720,1080],default=1080)
    args=p.parse_args();eps=episodes(args.character,not args.no_citation)
    if args.ids:
        unknown=set(args.ids)-{e['id'] for e in eps}
        if unknown:p.error('Unknown IDs: '+', '.join(sorted(unknown)))
        eps=[e for e in eps if e['id'] in args.ids]
    workspace=workspace_for(args.character,not args.no_citation);workspace.mkdir(parents=True,exist_ok=True)
    if not (workspace/'voice').exists():(workspace/'voice').symlink_to(VOICE_WORKSPACE/'voice',target_is_directory=True)
    settings=SimpleNamespace(stills=args.action=='stills',allow_silent=False,treatment=args.treatment,width=args.width)
    for e in eps:print(json.dumps(build(e,settings,workspace=workspace,renderer=RENDERER)),flush=True)

if __name__=='__main__':main()
