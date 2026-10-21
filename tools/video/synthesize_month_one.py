"""Explicit, resumable Fish synthesis. Inputs and credentials never enter Git.

Requires --generate; requests are not retried automatically. A started receipt
blocks retries until the operator reconciles its provider outcome.
"""
import argparse
import base64
import hashlib
import json
import os
import time
import urllib.request
import wave
from pathlib import Path
from month_one_core import ROOT, load_episodes, script, normalized, alignment_words, digest

def read_key():
    key=os.environ.get('FISH_API_KEY','').strip()
    local=ROOT/'.local/fish.env'
    if not key and local.exists():
        for line in local.read_text().splitlines():
            if line.strip().startswith('FISH_API_KEY='):
                key=line.strip().split('=',1)[1].strip().strip('\"').strip("'")
    if not key: raise RuntimeError('FISH_API_KEY is not configured; no request sent')
    return key

def generate(episode,key,profile,model):
    out=ROOT/'.local/month-one/voice'/episode['id']; out.mkdir(parents=True,exist_ok=True)
    text=script(episode); sha=hashlib.sha256(text.encode()).hexdigest()
    receipt=out/'generation.json'
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old.get('status')=='complete' and old.get('script_sha256')==sha:
            if not (out/'narration.wav').exists() or not (out/'alignment.json').exists():
                raise RuntimeError(f"{episode['id']}: complete receipt has missing artifacts; restore them")
            if old.get('audio_sha256')!=digest(out/'narration.wav') or old.get('alignment_sha256')!=digest(out/'alignment.json'):
                raise RuntimeError(f"{episode['id']}: retained media hash mismatch; no request sent")
            print(episode['id']+' retained',flush=True); return
        raise RuntimeError(f"{episode['id']}: existing receipt needs reconciliation; no retry sent")
    meta={'status':'started','script_sha256':sha,'model':model,'voice':'Ron Narration v2 studio',
          'started_unix':time.time(),'text':text,'credits_charged':None,'charge_note':'Configured free model; provider billing receipt not returned by endpoint.'}
    receipt.write_text(json.dumps(meta,indent=2)+'\n')
    body={'text':text,'reference_id':profile,'format':'wav','sample_rate':44100,'latency':'normal'}
    request=urllib.request.Request('https://api.fish.audio/v1/tts/stream/with-timestamp',
        data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','model':model})
    chunks={}; events=0; partial=out/'narration.partial'
    try:
        with urllib.request.urlopen(request,timeout=120) as response, partial.open('wb') as audio:
            if 'text/event-stream' not in response.headers.get('Content-Type',''):
                raise RuntimeError('Unexpected response type')
            for line in response:
                if not line.startswith(b'data:'): continue
                data=line[5:].strip()
                if data==b'[DONE]': continue
                event=json.loads(data)
                if 'error' in event: raise RuntimeError('Provider returned an error event')
                audio.write(base64.b64decode(event.get('audio_base64','')))
                if event.get('alignment') is not None:
                    chunks[int(event['chunk_seq'])]={'offset':event['chunk_audio_offset_sec'],'alignment':event['alignment']}
                events+=1
        if not chunks or not partial.stat().st_size: raise RuntimeError('Incomplete response')
        if ''.join(normalized(w['text']) for w in alignment_words(chunks))!=normalized(text):
            raise RuntimeError('Alignment does not match the script')
        with wave.open(str(partial)) as audio:
            if audio.getframerate()!=44100: raise RuntimeError('Unexpected audio sample rate')
            duration=audio.getnframes()/audio.getframerate()
        partial.replace(out/'narration.wav')
        (out/'alignment.json').write_text(json.dumps(chunks,indent=2)+'\n')
        meta.update(status='complete',duration=duration,events=events,elapsed_seconds=time.time()-meta['started_unix'],
                    audio_sha256=digest(out/'narration.wav'),alignment_sha256=digest(out/'alignment.json'))
        receipt.write_text(json.dumps(meta,indent=2)+'\n')
        print(json.dumps({'id':episode['id'],'status':'complete','duration':round(duration,2)}),flush=True)
    except Exception as error:
        meta.update(status='unresolved',error_type=type(error).__name__)
        receipt.write_text(json.dumps(meta,indent=2)+'\n')
        # Do not print provider bodies/headers, request objects or credential values.
        raise RuntimeError(f"{episode['id']}: {type(error).__name__}; reconcile before retry") from None

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--generate',action='store_true'); p.add_argument('--ids',nargs='+')
    p.add_argument('--profile-file',type=Path,default=ROOT/'.local/fish-profile.json'); args=p.parse_args()
    if not args.generate: raise SystemExit('No request sent. Explicit --generate is required.')
    config=json.loads(args.profile_file.read_text()); key=read_key()
    for episode in load_episodes():
        if not args.ids or episode['id'] in args.ids: generate(episode,key,config['voice_id'],config.get('model','s2.1-pro-free'))
