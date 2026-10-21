"""Generate the approved, neutral delivery and retain Fish word timestamps.

Credentials are read from FISH_API_KEY or a hidden terminal prompt. They are
never written to output files. Uses the explicitly selected free API model.
"""
import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
MODEL = 's2.1-pro-free'
ENDPOINT = 'https://api.fish.audio/v1/tts/stream/with-timestamp'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--voice-id', required=True)
    p.add_argument('--out', type=Path, default=ROOT / '.local/fish-voice')
    args = p.parse_args()
    source = json.loads((ROOT / 'examples/blender-mvp/timeline.json').read_text())
    text = ' '.join(c['text'] for c in source['cues'])
    body = {'text': text, 'reference_id': args.voice_id,
            'format': 'wav', 'sample_rate': 44100, 'latency': 'normal'}
    key = os.environ.get('FISH_API_KEY') or getpass.getpass('Fish API key (hidden): ')
    request = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + key,
                 'Content-Type': 'application/json', 'model': MODEL})
    args.out.mkdir(parents=True, exist_ok=True)
    partial = args.out / 'narration.partial'
    alignments, events = {}, 0
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            if 'text/event-stream' not in response.headers.get('Content-Type', ''):
                raise RuntimeError('Unexpected response type; expected timestamped audio')
            with partial.open('wb') as audio:
                for line in response:
                    if not line.startswith(b'data:'):
                        continue
                    payload = line[5:].strip()
                    if payload == b'[DONE]':
                        continue
                    event = json.loads(payload)
                    if 'error' in event:
                        raise RuntimeError(str(event['error']))
                    audio.write(base64.b64decode(event.get('audio_base64', '')))
                    if event.get('alignment') is not None:
                        alignments[int(event['chunk_seq'])] = {
                            'content': event['content'],
                            'offset': event['chunk_audio_offset_sec'],
                            'alignment': event['alignment']}
                    events += 1
        if not partial.stat().st_size or not alignments:
            raise RuntimeError('Incomplete audio or missing word timestamps')
        partial.replace(args.out / 'narration.wav')
        (args.out / 'alignment.json').write_text(json.dumps(alignments, indent=2) + '\n')
        (args.out / 'generation.json').write_text(json.dumps({
            'model': MODEL, 'text': text, 'format': 'wav', 'sample_rate': 44100,
            'latency': 'normal', 'delivery': 'approved first take; no emotion cues',
            'voice': 'existing private Ron Narration v2 studio profile',
            'events': events, 'alignment_chunks': len(alignments)}, indent=2) + '\n')
        print(json.dumps({'status': 'complete', 'events': events,
                          'alignment_chunks': len(alignments),
                          'audio_bytes': (args.out / 'narration.wav').stat().st_size}), flush=True)
    except urllib.error.HTTPError as error:
        message = error.read(2000).decode(errors='replace').replace(key, '[REDACTED]')
        raise SystemExit(f'Fish API HTTP {error.code}: {message}') from None
    except Exception as error:
        raise SystemExit(str(error).replace(key, '[REDACTED]')) from None


if __name__ == '__main__':
    main()
