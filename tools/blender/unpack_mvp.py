"""Restore the exact retained MP4 from its lossless GitHub transfer parts."""
import base64
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[2] / 'examples/blender-mvp'
    media = root / 'media'
    manifest = json.loads((media / 'manifest.json').read_text())
    data = bytearray()
    prefix, suffix = 'window.REP_MVP_PARTS.push(', ');\n'
    for part in manifest['parts']:
        name = part['file']
        if Path(name).name != name:
            raise ValueError('Invalid part filename')
        text = (media / name).read_text()
        if not text.startswith(prefix) or not text.endswith(suffix):
            raise ValueError(f'Invalid part: {name}')
        chunk = base64.b64decode(json.loads(text[len(prefix):-len(suffix)]), validate=True)
        if len(chunk) != part['bytes'] or hashlib.sha256(chunk).hexdigest() != part['sha256']:
            raise ValueError(f'Corrupt part: {name}')
        data.extend(chunk)
    if len(data) != manifest['bytes'] or hashlib.sha256(data).hexdigest() != manifest['sha256']:
        raise ValueError('Video checksum mismatch')
    name = manifest['filename']
    if Path(name).name != name:
        raise ValueError('Invalid output filename')
    output = root / name
    temporary = output.with_suffix('.mp4.tmp')
    temporary.write_bytes(data)
    temporary.replace(output)
    print(output)


if __name__ == '__main__':
    main()
