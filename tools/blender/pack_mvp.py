"""Pack the finished MP4 losslessly into small, browser-playable Git files."""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'examples/blender-mvp'
START, END = '<!-- VIDEO PARTS START -->', '<!-- VIDEO PARTS END -->'


def main():
    video = ROOT / 'Rep_and_Reason_Blender_MVP.mp4'
    data = video.read_bytes()
    media = ROOT / 'media'
    media.mkdir(exist_ok=True)
    parts = []
    for i, start in enumerate(range(0, len(data), 150_000)):
        chunk = data[start:start + 150_000]
        name = f'part-{i:03d}.js'
        encoded = base64.b64encode(chunk).decode()
        (media / name).write_text('window.REP_MVP_PARTS.push(' + json.dumps(encoded) + ');\n')
        parts.append({'file': name, 'bytes': len(chunk), 'sha256': hashlib.sha256(chunk).hexdigest()})
    names = {part['file'] for part in parts}
    for old in media.glob('part-*.js'):
        if old.name not in names:
            old.unlink()
    manifest = {'filename': video.name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(),
                'encoding': 'base64-javascript-parts', 'parts': parts}
    (media / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    index = ROOT / 'index.html'
    before, remainder = index.read_text().split(START, 1)
    _, after = remainder.split(END, 1)
    scripts = ''.join(f'<script src="media/{part["file"]}"></script>\n' for part in parts)
    index.write_text(before + START + '\n' + scripts + END + after)
    print(f'Packed {len(data):,} bytes into {len(parts)} lossless parts')


if __name__ == '__main__':
    main()
