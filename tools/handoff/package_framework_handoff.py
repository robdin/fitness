"""Package the dated framework, current source snapshot and retained public media.

No provider calls, publication, Git mutation or credential/profile export.
Uses an explicit allowlist for files that are not already tracked in Git.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT.parent / 'fitness-deliverables/reusable-framework-2026-10-24'
NAME = 'Content_Framework_Handoff'
MAIN = 'docs/CONTENT_IDEA_FRAMEWORK_AND_HANDOFF.md'
TEMPLATE = 'docs/templates/NEW_CONTENT_IDEA_TEMPLATE.md'
EXTRAS = [MAIN, TEMPLATE, 'brand/blueprint/CHARACTER_PREVIEW.md',
          'brand/blueprint/tokens.json', 'brand/dreamy-tactical/tokens.json',
          'tools/video/build_off_duty_preview.py', 'tools/video/render_off_duty_preview.cjs',
          'tools/handoff/package_framework_handoff.py']
MEDIA = [
    ROOT.parent / 'fitness-deliverables/month-one-v5-blueprint/Blueprint_Month_Review.zip',
    ROOT.parent / 'fitness-deliverables/month-one-v5-blueprint/Blueprint_Month_Sources.zip',
    ROOT.parent / 'fitness-deliverables/blueprint-character-d-preview/Off_Duty_Hero_Comparisons.zip',
]
CONCEPTS = ['A-everyday-you.png', 'B-cloud-runner.png', 'C-steady.png',
            'D-off-duty-hero.png', 'E-quiet-power.png', 'F-dreamwalker.png',
            'manifest.json', 'prompts.json']
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.jsonl', '.py', '.cjs', '.js', '.html',
                 '.csv', '.toml', '.yml', '.yaml', '.srt', '.vtt', '.ics', '.example'}
SECRET_PATTERNS = [rb'sk-fish-[A-Za-z0-9_-]{12,}', rb'gh[pousr]_[A-Za-z0-9]{25,}',
                   rb'github_pat_[A-Za-z0-9_]{25,}',
                   rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']

VERIFY_SCRIPT = '''"""Verify all files in an extracted Content_Framework_Handoff directory."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
for item in manifest['files']:
    p=(root/item['path']).resolve()
    assert p.is_relative_to(root), 'Unsafe manifest path'
    assert p.is_file(), 'Missing file: '+item['path']
    data=p.read_bytes()
    assert len(data)==item['bytes'], 'Size mismatch: '+item['path']
    assert hashlib.sha256(data).hexdigest()==item['sha256'], 'Hash mismatch: '+item['path']
print('Verified',len(manifest['files']),'manifest files.')
'''

RESTORE = '''# Restore this handoff

Read `CONTENT_IDEA_FRAMEWORK_AND_HANDOFF.md` first. The fitness case study and
the blank `NEW_CONTENT_IDEA_TEMPLATE.md` can be read without installing tools.

1. Extract this outer ZIP into a new directory; do not overwrite a checkout.
2. From the extracted `Content_Framework_Handoff` directory run:

   ```sh
   python3 verify_bundle.py
   ```

3. `source/fitness/` is a working-tree source snapshot. It includes the uncommitted
   D and framework changes and public visual tokens. It has no `.git` history.
   Compare it with a fresh clone if Git history is needed. Do not initialize or
   overwrite an existing repository as part of a blind restore.
4. Extract `media/Blueprint_Month_Sources.zip` into a separate staging directory.
   Copy its `fitness/.local/month-one-v5-blueprint/` directory into
   `source/fitness/.local/month-one-v5-blueprint/`. This supplies retained voice
   and audio-QA records. Keep the newer outer source snapshot for code/docs.
5. Extract `media/Blueprint_Month_Review.zip` into staging. Copy the **contents** of
   `Blueprint_Month/` into `source/fitness/.local/month-one-v5-blueprint/review/`.
   Open that `index.html` to watch the 18 exports without rendering.
6. Extract `media/Off_Duty_Hero_Comparisons.zip` into staging. Copy the **contents**
   of `Off_Duty_Hero_Comparisons/` into
   `source/fitness/.local/blueprint-character-d-preview/`. Open its `index.html`.
7. Copy `character-exploration/` into
   `source/fitness/.local/character-exploration-2026-10-24/`.
   Generation metadata preserves original-machine absolute reference paths;
   use the restored local D reference rather than those historical paths.
8. Install dependencies from the restored fitness root only if you need checks
   or rendering: Python >=3.11, Pillow, Node with `npm ci`, FFmpeg/FFprobe and the
   bundled fonts. The main document gives exact commands and side effects.

No credentials, private Fish profile, voice enrollment data, participant contact
records, optional ASR models or SQLite operating state are included. Retained
speech and pose assets allow local rebuilding without new generation requests.
The current BP03 no-citation producer recreates its alternate workspace from
the retained voice when that control is rebuilt.

For a new content idea use a separate root and the blank template. This source
snapshot still has fitness-specific paths, schemas, identities and decision rules.
Do not copy private accounts, source claims or publishing authority to a new idea.

The outer manifest verifies the snapshot and nested ZIP bytes. The two Blueprint
ZIPs also contain their own per-file manifests. The D ZIP contains media hashes
in `verification.json`. Old nested review documents predate this handoff; the
outer Markdown and outer source snapshot describe the latest project state.
'''


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def safe_path(name: str) -> None:
    p = PurePosixPath(name)
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in name, name


def scan(name: str, data: bytes) -> None:
    safe_path(name)
    parts = PurePosixPath(name).parts
    base = parts[-1]
    assert base not in {'fish.env', 'fish-profile.json', 'state.sqlite3', '.env'}, name
    assert not (base.startswith('.env.') and base != '.env.example'), name
    assert '.git' not in parts and 'node_modules' not in parts and '.venv' not in parts, name
    if PurePosixPath(name).suffix in TEXT_SUFFIXES or base == '.gitignore':
        for pattern in SECRET_PATTERNS:
            assert not re.search(pattern, data), 'Credential-pattern match in '+name


def inspect_archive(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None, 'Nested ZIP CRC failure'
        assert len(z.namelist()) == len(set(z.namelist())), 'Duplicate ZIP paths'
        for item in z.infolist():
            if not item.is_dir():
                scan(item.filename, z.read(item.filename))
        manifest_checks = 0
        if 'manifest.json' in z.namelist():
            manifest = json.loads(z.read('manifest.json'))
            for item in manifest:
                data = z.read(item['path'])
                assert digest(data) == item['sha256'] and len(data) == item['bytes']
                manifest_checks += 1
        else:
            receipt = json.loads(z.read('Off_Duty_Hero_Comparisons/verification.json'))
            for episode in receipt['episodes']:
                for item in episode['outputs']:
                    assert digest(z.read('Off_Duty_Hero_Comparisons/'+item['file'])) == item['sha256']
                    manifest_checks += 1
        return {'name': path.name, 'crc': 'passed', 'hashes_checked': manifest_checks,
                'sha256': digest(path.read_bytes()), 'bytes': path.stat().st_size}


def check_restored(archive: Path) -> dict:
    """Exercise the documented restore in an isolated temporary directory."""
    with tempfile.TemporaryDirectory(prefix='fitness-framework-restore-') as temp:
        staging = Path(temp).resolve()
        with zipfile.ZipFile(archive) as z:
            z.extractall(staging)
        base = staging / NAME
        result = subprocess.run([sys.executable, str(base/'verify_bundle.py')],
                                capture_output=True, text=True, check=True)
        fitness = base/'source/fitness'
        for filename in ['Blueprint_Month_Sources.zip', 'Blueprint_Month_Review.zip',
                         'Off_Duty_Hero_Comparisons.zip']:
            with zipfile.ZipFile(base/'media'/filename) as z:
                z.extractall(staging/'nested')
        nested = staging/'nested'
        shutil.copytree(nested/'fitness/.local/month-one-v5-blueprint',
                        fitness/'.local/month-one-v5-blueprint', dirs_exist_ok=True)
        shutil.copytree(nested/'Blueprint_Month',
                        fitness/'.local/month-one-v5-blueprint/review', dirs_exist_ok=True)
        shutil.copytree(nested/'Off_Duty_Hero_Comparisons',
                        fitness/'.local/blueprint-character-d-preview', dirs_exist_ok=True)
        shutil.copytree(base/'character-exploration',
                        fitness/'.local/character-exploration-2026-10-24', dirs_exist_ok=True)
        subprocess.run([sys.executable, str(fitness/'tools/calendar/build_month_one_v5.py'), '--check'],
                       cwd=fitness, capture_output=True, text=True, check=True)
        for id in [f'BP{i:02}' for i in range(1,17)]:
            voice = fitness/'.local/month-one-v5-blueprint/voice'/id
            receipt = json.loads((voice/'generation.json').read_text())
            assert receipt['status'] == 'complete'
            for name, field in [('narration.wav','audio_sha256'),('alignment.json','alignment_sha256')]:
                assert digest((voice/name).read_bytes()) == receipt[field]
        # The snapshot uses retained V5 speech without an old V3 voice directory.
        sys.path.insert(0, str(fitness/'tools/video'))
        try:
            import produce_month_one_v5 as producer
            assert producer.ROOT == fitness
            assert not (fitness/'.local/month-one-v3/voice').exists()
            retained = sum(producer.retain_voice(e) for e in producer.episodes() if e.get('voice_reuse_from'))
            assert retained == 11
        finally:
            sys.path.pop(0)
        review = fitness/'.local/month-one-v5-blueprint/review'
        assert len(list(review.rglob('*.mp4'))) == 18
        assert len(list((fitness/'.local/blueprint-character-d-preview').rglob('*.mp4'))) == 9
        for file in [review/'index.html', fitness/'.local/blueprint-character-d-preview/index.html']:
            for href in re.findall(r'(?:href|src)="([^"#]+)"', file.read_text()):
                if '://' not in href and not href.startswith('data:'):
                    assert (file.parent/href.split('#')[0]).exists(), 'Broken hub link: '+href
        return {'outer_manifest': result.stdout.strip(), 'calendar': 'passed',
                'voice_pairs_verified': 16, 'historical_voice_independent_reuse': retained,
                'restored_master_and_control_videos': 18, 'restored_character_files': 9,
                'review_hub_links': 'passed',
                'scope': 'Isolated extraction, hashes, retained voice and data checks; no clean dependency installation or full re-render.'}


def main() -> None:
    files: dict[str, bytes] = {}
    tracked = git('ls-files', '-z').split('\0')
    for rel in sorted(set(tracked + EXTRAS)):
        if not rel:
            continue
        path = ROOT/rel
        assert path.is_file() and not path.is_symlink(), 'Missing or symlink source: '+rel
        data = path.read_bytes()
        scan(rel, data)
        files['source/fitness/'+rel] = data
    files['CONTENT_IDEA_FRAMEWORK_AND_HANDOFF.md'] = (ROOT/MAIN).read_bytes()
    files['NEW_CONTENT_IDEA_TEMPLATE.md'] = (ROOT/TEMPLATE).read_bytes()
    archives = [inspect_archive(p) for p in MEDIA]
    for p in MEDIA:
        files['media/'+p.name] = p.read_bytes()
    for name in CONCEPTS:
        p = ROOT/'.local/character-exploration-2026-10-24'/name
        data = p.read_bytes()
        scan(name, data)
        files['character-exploration/'+name] = data
    files['RESTORE.md'] = RESTORE.encode()
    files['verify_bundle.py'] = VERIFY_SCRIPT.encode()
    entries = [{'path': path, 'bytes': len(data), 'sha256': digest(data)}
               for path, data in sorted(files.items())]
    manifest = {'prepared_at': '2026-10-24', 'timezone': 'America/New_York',
                'git_base': git('rev-parse', 'HEAD'), 'branch': git('branch', '--show-current'),
                'source_scope': 'Current tracked working-tree files plus named public additions; no Git history.',
                'audience_results': 'none recorded', 'files': entries}
    files['manifest.json'] = (json.dumps(manifest, indent=2)+'\n').encode()
    DELIVERY.mkdir(parents=True, exist_ok=True)
    for name in ['CONTENT_IDEA_FRAMEWORK_AND_HANDOFF.md','NEW_CONTENT_IDEA_TEMPLATE.md','RESTORE.md','manifest.json','verify_bundle.py']:
        (DELIVERY/name).write_bytes(files[name])
    archive = DELIVERY/(NAME+'.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in sorted(files.items()):
            scan(name, data)
            z.writestr(NAME+'/'+name, data,
                       compress_type=zipfile.ZIP_STORED if name.endswith('.zip') else zipfile.ZIP_DEFLATED)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    restored = check_restored(archive)
    receipt = {'status':'transfer_verified', 'date':'2026-10-24',
               'archive': {'file':archive.name,'bytes':archive.stat().st_size,'sha256':digest(archive.read_bytes())},
               'manifest_files':len(entries),'nested_archives':archives,'restore_check':restored,
               'secret_scan':'Explicit private-path exclusion and listed credential-pattern scan passed; not a general guarantee.',
               'new_generation_requests':0,'public_upload':False}
    (DELIVERY/'delivery-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
