"""Produce the Blueprint month, retaining matching narration and isolating new scripts."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from types import SimpleNamespace
from month_one_core import ROOT, script, digest
from build_month_one import build
from synthesize_month_one import generate, read_key

WORKSPACE = ROOT / '.local/month-one-v5-blueprint'
RENDERER = ROOT / 'tools/video/render_month_one_v5.cjs'
CONFIG = ROOT / 'content/month-one-v5/production.json'
TOKENS = ROOT / 'brand/blueprint/tokens.json'

def episodes(citation=True):
    content = json.loads((ROOT / 'content/month-one-v5/calendar.json').read_text())
    config = json.loads(CONFIG.read_text())
    fonts = [ROOT / 'content/mvp/time-audit/fonts/SpaceGrotesk.ttf', ROOT / 'brand/blueprint/fonts/Fraunces-Italic.ttf']
    result = []
    for original in content['episodes']:
        design = {**config['episodes'][original['id']], 'brand': 'blueprint', 'layout': 'blueprint-graphics',
                  'source_cue_visible': citation, 'production_sha256': digest(CONFIG), 'tokens_sha256': digest(TOKENS),
                  'font_sha256': {p.name: digest(p) for p in fonts}}
        if len(design['headlines']) != len(original['beats']):
            raise ValueError('Every beat needs a headline')
        result.append({**original, 'pillar': original['cluster'],
                       'beats': [[b['role'], b['narration']] for b in original['beats']],
                       'graphics': design, 'cover': design['headlines'][0], 'visual': 'v5-blueprint',
                       'balanced_captions': True, 'original_brief': original['beats'],
                       'canonical_sha256': hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest()})
    return result

def workspace_for(citation=True):
    return WORKSPACE if citation else ROOT / '.local/month-one-v5-blueprint-no-citation'

def retain_voice(ep):
    """Copy only a verified, script-identical voice; never overwrite an existing track."""
    prior = ep.get('voice_reuse_from')
    if not prior:
        return False
    source = ROOT / '.local/month-one-v3/voice' / prior
    target = WORKSPACE / 'voice' / ep['id']
    if (target / 'generation.json').exists():
        retained = json.loads((target / 'generation.json').read_text())
        assert retained['status'] == 'complete'
        assert retained['script_sha256'] == hashlib.sha256(script(ep).encode()).hexdigest()
        assert retained['audio_sha256'] == digest(target / 'narration.wav')
        assert retained['alignment_sha256'] == digest(target / 'alignment.json')
        return True
    receipt = json.loads((source / 'generation.json').read_text())
    expected = hashlib.sha256(script(ep).encode()).hexdigest()
    assert receipt['status'] == 'complete' and receipt['script_sha256'] == expected
    assert receipt['audio_sha256'] == digest(source / 'narration.wav')
    assert receipt['alignment_sha256'] == digest(source / 'alignment.json')
    target.mkdir(parents=True, exist_ok=True)
    for name in ['narration.wav', 'alignment.json', 'generation.json']:
        if (target / name).exists():
            assert digest(target / name) == digest(source / name), 'Retained artifact mismatch'
        else:
            shutil.copy2(source / name, target / name)
    for model in ['base.en', 'small.en']:
        old = ROOT / '.local/month-one-v3/audio-qa' / model / (prior + '.json')
        if old.exists():
            report = json.loads(old.read_text())
            assert report['audio_sha256'] == receipt['audio_sha256']
            report.update(id=ep['id'], retained_from=prior)
            dest = WORKSPACE / 'audio-qa' / model / (ep['id'] + '.json')
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(report, indent=2) + '\n')
    return True

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['retain', 'stills', 'synthesize', 'render'])
    p.add_argument('--ids', nargs='+')
    p.add_argument('--generate', action='store_true')
    p.add_argument('--no-citation', action='store_true')
    p.add_argument('--treatment', choices=['motion', 'static'], default='motion')
    p.add_argument('--width', type=int, choices=[720, 1080], default=1080)
    args = p.parse_args()
    eps = episodes(not args.no_citation)
    if args.ids:
        unknown = set(args.ids) - {e['id'] for e in eps}
        if unknown: p.error('Unknown IDs: ' + ', '.join(sorted(unknown)))
        eps = [e for e in eps if e['id'] in args.ids]
    workspace = workspace_for(not args.no_citation)
    workspace.mkdir(parents=True, exist_ok=True)
    if args.no_citation and not (workspace / 'voice').exists():
        (workspace / 'voice').symlink_to(WORKSPACE / 'voice', target_is_directory=True)
    if args.action == 'synthesize':
        if not args.generate: p.error('Synthesis requires --generate; no request sent')
        profile = json.loads((ROOT / '.local/fish-profile.json').read_text())
        key = read_key()
        for ep in eps:
            if retain_voice(ep):
                print(ep['id'] + ' retained', flush=True)
            else:
                generate(ep, key, profile['voice_id'], profile['model'], output_root=WORKSPACE / 'voice')
    elif args.action == 'retain':
        for ep in eps:
            if retain_voice(ep): print(ep['id'] + ' retained', flush=True)
    else:
        settings = SimpleNamespace(stills=args.action == 'stills', allow_silent=False, treatment=args.treatment, width=args.width)
        for ep in eps:
            if ep.get('voice_reuse_from'): retain_voice(ep)
            print(json.dumps(build(ep, settings, workspace=workspace, renderer=RENDERER)), flush=True)

if __name__ == '__main__': main()
