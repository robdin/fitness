"""Build conversational Blueprint content in its own workspace; never publishes."""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from month_one_core import ROOT, digest
from build_month_one import build
from synthesize_month_one_v6 import generate, read_key

WORKSPACE=ROOT/'.local/month-one-v6-conversational'
RENDERER=ROOT/'tools/video/render_month_one_v6.cjs'
CONFIG=ROOT/'content/month-one-v6/production.json'
TOKENS=ROOT/'brand/blueprint/tokens.json'

def episodes(citation=True,include_intro=True):
    data=json.loads((ROOT/'content/month-one-v6/calendar.json').read_text())
    config=json.loads(CONFIG.read_text())
    source=([data['orientation_asset']] if include_intro else [])+data['episodes']
    fonts=[ROOT/'content/mvp/time-audit/fonts/SpaceGrotesk.ttf',ROOT/'brand/blueprint/fonts/Fraunces-Italic.ttf']
    result=[]
    for e in source:
        design={**config['episodes'][e['id']],'brand':'blueprint','layout':'blueprint-graphics',
                'source_cue_visible':citation,'production_sha256':digest(CONFIG),'tokens_sha256':digest(TOKENS),
                'font_sha256':{p.name:digest(p) for p in fonts}}
        assert len(design['headlines'])==len(e['beats'])==6
        result.append({**e,'pillar':e['cluster'],'beats':[[b['role'],b['narration']] for b in e['beats']],
                       'graphics':design,'cover':design['headlines'][0],'visual':'v6-blueprint-conversational',
                       'balanced_captions':True,'original_brief':e['beats'],
                       'canonical_sha256':hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()})
    return result

def workspace_for(citation=True):
    return WORKSPACE if citation else ROOT/'.local/month-one-v6-conversational-no-citation'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['synthesize','stills','render'])
    p.add_argument('--ids',nargs='+');p.add_argument('--generate',action='store_true')
    p.add_argument('--no-citation',action='store_true');p.add_argument('--treatment',choices=['motion','static'],default='motion')
    p.add_argument('--width',type=int,choices=[720,1080],default=1080)
    args=p.parse_args();eps=episodes(not args.no_citation)
    if args.ids:
        unknown=set(args.ids)-{e['id'] for e in eps}
        if unknown:p.error('Unknown IDs: '+', '.join(sorted(unknown)))
        eps=[e for e in eps if e['id'] in args.ids]
    workspace=workspace_for(not args.no_citation);workspace.mkdir(parents=True,exist_ok=True)
    if args.no_citation and not (workspace/'voice').exists():(workspace/'voice').symlink_to(WORKSPACE/'voice',target_is_directory=True)
    if args.action=='synthesize':
        if not args.generate:p.error('Pass --generate for an explicitly requested production run')
        if args.no_citation:p.error('Synthesize the master once; variants share its audio')
        profile=json.loads((ROOT/'.local/fish-profile.json').read_text());key=read_key()
        assert profile['model']=='s2.1-pro-free','Review changed provider model before generating'
        voice=json.loads(CONFIG.read_text())['voice']
        for ep in eps:generate(ep,key,profile['voice_id'],profile['model'],WORKSPACE/'voice',voice['delivery_tag'],voice['prosody_speed'])
    else:
        settings=SimpleNamespace(stills=args.action=='stills',allow_silent=False,treatment=args.treatment,width=args.width)
        for ep in eps:print(json.dumps(build(ep,settings,workspace=workspace,renderer=RENDERER)),flush=True)

if __name__=='__main__':main()
