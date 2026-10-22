"""Produce the beginner-led B-series without mutating the existing M-series media."""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from month_one_core import ROOT, script
from synthesize_month_one import generate, read_key
from build_month_one import build

WORKSPACE=ROOT/'.local/month-one-v3'
RENDERER=ROOT/'tools/video/render_month_one_v3.cjs'

def episodes(brand=None):
    content=json.loads((ROOT/'content/month-one-v3/calendar.json').read_text())
    graphics=json.loads((ROOT/'content/month-one-v3/production.json').read_text())
    result=[]
    for original in content['episodes']:
        design={**graphics['episodes'][original['id']], 'brand':brand or graphics['brand'], 'tokens_sha256':hashlib.sha256((ROOT/'brand/v3/tokens.json').read_bytes()).hexdigest(), 'font_sha256':hashlib.sha256((ROOT/'content/mvp/time-audit/fonts/SpaceGrotesk.ttf').read_bytes()).hexdigest()}
        if len(design['headlines'])!=len(original['beats']):raise ValueError('Every beat needs a headline')
        adapted={**original,'pillar':original['cluster'],'beats':[[b['role'],b['narration']] for b in original['beats']],
                 'graphics':design,'cover':design['headlines'][0],'visual':'v3','original_brief':original['beats'],'balanced_captions':True}
        if script(adapted)!=' '.join(b['narration'] for b in original['beats']):raise ValueError('Narration changed in production adapter')
        adapted['canonical_sha256']=hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest()
        result.append(adapted)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['stills','synthesize','render'])
    p.add_argument('--brand',choices=['club','lab','notebook'],default='club')
    p.add_argument('--ids',nargs='+');p.add_argument('--generate',action='store_true')
    p.add_argument('--treatment',choices=['motion','static'],default='motion')
    p.add_argument('--width',type=int,choices=[720,1080],default=1080)
    args=p.parse_args();eps=episodes(args.brand)
    workspace=WORKSPACE
    if args.brand!='club':
        workspace=ROOT/('.local/month-one-v3-'+args.brand);workspace.mkdir(parents=True,exist_ok=True)
        if not (workspace/'voice').exists():(workspace/'voice').symlink_to(WORKSPACE/'voice',target_is_directory=True)
    if args.ids:
        unknown=set(args.ids)-{e['id'] for e in eps}
        if unknown:p.error('Unknown episode IDs: '+', '.join(sorted(unknown)))
        eps=[e for e in eps if e['id'] in args.ids]
    if args.action=='synthesize':
        if not args.generate:p.error('Synthesis requires --generate; no request sent')
        config=json.loads((ROOT/'.local/fish-profile.json').read_text());key=read_key()
        for e in eps:generate(e,key,config['voice_id'],config['model'],output_root=WORKSPACE/'voice')
    else:
        settings=SimpleNamespace(stills=args.action=='stills',allow_silent=False,treatment=args.treatment,width=args.width)
        for e in eps:print(json.dumps(build(e,settings,workspace=workspace,renderer=RENDERER)),flush=True)

if __name__=='__main__':main()
