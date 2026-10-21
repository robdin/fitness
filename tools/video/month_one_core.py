"""Offline month-one content/timing utilities. Never contacts a provider."""
import hashlib
import json
import math
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / 'content/month-one/episodes.json'

def load_episodes():
    return json.loads(CONTENT.read_text())['episodes']

def script(episode):
    return ' '.join(b[1] for b in episode['beats'])

def normalized(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def caption_chunks(text):
    # Keep sentence boundaries when possible, then pack to <=62 characters.
    result=[]
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        for chunk in textwrap.wrap(sentence, width=62, break_long_words=False, break_on_hyphens=False):
            lines=textwrap.wrap(chunk, width=32, break_long_words=False, break_on_hyphens=False)
            if len(lines)>2:
                # A balanced split avoids a third line caused by word lengths.
                words=chunk.split()
                valid=[(' '.join(words[:i]),' '.join(words[i:])) for i in range(1,len(words))]
                valid=[p for p in valid if max(map(len,p))<=34]
                if not valid:
                    for i in range(0,len(lines),2):
                        pair=lines[i:i+2]; result.append({'text':' '.join(pair),'lines':pair})
                    continue
                lines=list(min(valid,key=lambda p:abs(len(p[0])-len(p[1]))))
            result.append({'text':chunk,'lines':lines})
    return result

def alignment_words(alignment, lead=.12):
    words=[]; position=0
    for _, chunk in sorted(alignment.items(),key=lambda kv:int(kv[0])):
        for seg in chunk['alignment']['segments']:
            size=len(normalized(seg['text']))
            if not size: continue
            start=float(seg['start'])+float(chunk['offset'])+lead
            end=float(seg['end'])+float(chunk['offset'])+lead
            if end<start or (words and start<words[-1]['start']-.01):
                raise ValueError('Non-monotonic provider alignment')
            words.append({'text':seg['text'],'start':start,'end':end,'a':position,'b':position+size})
            position+=size
    return words

def make_timeline(episode, alignment=None, voice_duration=None):
    words=alignment_words(alignment) if alignment else []
    if words and normalized(script(episode))!=''.join(normalized(w['text']) for w in words):
        raise ValueError(f"{episode['id']}: provider text does not match script")
    beats=[]; captions=[]; cursor=0; clock=.12
    for kind, text in episode['beats']:
        end=cursor+len(normalized(text))
        matched=[w for w in words if w['b']>cursor and w['a']<end]
        start=matched[0]['start'] if matched else clock
        stop=matched[-1]['end'] if matched else start+max(len(text)/18.5,len(text.split())/2.9)
        beats.append({'kind':kind,'text':text,'start':start,'end':stop})
        chunks=caption_chunks(text)
        total=sum(len(c['text']) for c in chunks)
        estimate=start
        for chunk in chunks:
            ce=cursor+len(normalized(chunk['text']))
            cw=[w for w in words if w['b']>cursor and w['a']<ce]
            cs=cw[0]['start'] if cw else estimate
            cend=cw[-1]['end'] if cw else cs+(stop-start)*len(chunk['text'])/total
            captions.append({**chunk,'spoken_start':cs,'spoken_end':cend})
            estimate=cend; cursor=ce
        clock=stop+.14
    duration=((voice_duration+.12) if voice_duration else clock)+.8
    duration=math.ceil(duration*30)/30
    if words and words[-1]['end']>duration: raise ValueError('Alignment exceeds audio duration')
    for i,b in enumerate(beats):
        b['start']=0 if i==0 else max(0,b['start']-.05)
        b['end']=beats[i+1]['start']-.05 if i+1<len(beats) else duration
    for i,c in enumerate(captions):
        floor=captions[i-1]['end'] if i else 0
        next_start=captions[i+1]['spoken_start']-.04 if i+1<len(captions) else duration
        c['end']=min(c['spoken_end']+.2,next_start)
        c['start']=max(floor,c['spoken_start']-.1)
        # Use available pre-roll only; never silently overlap adjacent captions.
        c['start']=max(floor,min(c['start'],c['end']-len(c['text'])/20))
        c['cps']=len(c['text'])/max(.001,c['end']-c['start'])
    markers={}
    whole=normalized(script(episode))
    for token in ['fifteen','twentyfive','eight','twelve']:
        at=whole.find(token)
        if at<0:continue
        matched=[w for w in words if w['b']>at and w['a']<at+len(token)]
        if matched: markers[token]=matched[0]['start']
        else:
            pos=0
            for b in beats:
                length=len(normalized(b['text']))
                if pos<=at<pos+length:
                    markers[token]=b['start']+(at-pos)/length*(b['end']-b['start']);break
                pos+=length
    return {'markers':markers,'episode':episode,'duration':duration,'fps':30,'beats':beats,'captions':captions,
            'timing':'provider_word_alignment' if words else 'estimated_visual_draft',
            'words':words,'script_sha256':hashlib.sha256(script(episode).encode()).hexdigest()}

def stamp(seconds):
    ms=round(seconds*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def write_srt(timeline,path):
    Path(path).write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(c['lines']) for i,c in enumerate(timeline['captions']))+'\n')
