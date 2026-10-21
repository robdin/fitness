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

def finalize_stream_wav(source, target):
    """Finalize a streaming WAV header without changing any PCM samples."""
    pcm_bytes=0
    with wave.open(str(source),'rb') as reader:
        if reader.getframerate()!=44100 or reader.getnchannels()!=1 or reader.getsampwidth()!=2:
            raise RuntimeError('Unexpected audio format')
        reported_frames=reader.getnframes()
        with wave.open(str(target),'wb') as writer:
            # Streaming sentinels can overflow RIFF's 32-bit size field.
            # Let the seekable writer calculate the real count from PCM bytes.
            writer.setparams(reader.getparams()._replace(nframes=0))
            while block:=reader.readframes(65536):
                if len(block)%2: raise RuntimeError('Incomplete PCM sample')
                writer.writeframesraw(block); pcm_bytes+=len(block)
    if not pcm_bytes: raise RuntimeError('Empty audio stream')
    return {'duration':pcm_bytes/2/44100,'provider_header_frames':reported_frames,
            'finalized_frames':pcm_bytes//2,'provider_stream_sha256':digest(source)}

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
        finalized=out/'narration.finalized.wav'
        audio_meta=finalize_stream_wav(partial,finalized)
        if alignment_words(chunks,lead=0)[-1]['end']>audio_meta['duration']+.05:
            raise RuntimeError('Alignment exceeds decoded audio')
        finalized.replace(out/'narration.wav'); partial.unlink()
        (out/'alignment.json').write_text(json.dumps(chunks,indent=2)+'\n')
        meta.update(status='complete',**audio_meta,events=events,elapsed_seconds=time.time()-meta['started_unix'],
                    audio_sha256=digest(out/'narration.wav'),alignment_sha256=digest(out/'alignment.json'))
        receipt.write_text(json.dumps(meta,indent=2)+'\n')
        print(json.dumps({'id':episode['id'],'status':'complete','duration':round(audio_meta['duration'],2)}),flush=True)
    except Exception as error:
        meta.update(status='unresolved',error_type=type(error).__name__)
        if isinstance(error,urllib.error.HTTPError): meta['http_status']=error.code
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
