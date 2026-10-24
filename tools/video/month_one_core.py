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

def caption_chunks(text,balanced=False):
    # Keep sentence boundaries when possible, then pack to <=62 characters.
    result=[]
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        chunks=textwrap.wrap(sentence, width=62, break_long_words=False, break_on_hyphens=False)
        if balanced and len(chunks)>1:
            # Avoid a lone trailing word flashing as a separate caption. Keep
            # sentence order, the same maximum length and the original text.
            for j in range(len(chunks)-1,0,-1):
                while len(chunks[j])<20:
                    previous=chunks[j-1].split()
                    if len(previous)<3:break
                    moved=previous[-1]+' '+chunks[j]
                    if len(moved)>62:break
                    chunks[j-1]=' '.join(previous[:-1]);chunks[j]=moved
        for chunk in chunks:
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

def fit_caption_timing(captions,duration,max_cps=20,slack=.45):
    """Borrow nearby reading time with bounded displacement from spoken words.

    Interior boundaries stay within 450 ms of the adjoining spoken edges.
    No overlapping cues, changed speech, deleted text or hidden rate exceptions.
    """
    required=[len(c['text'])/max_cps for c in captions]; n=len(captions)
    lower=[0]+[max(0,c['spoken_start']-slack) for c in captions[1:]]+[duration]
    upper=[0]+[min(duration,captions[i-1]['spoken_end']+slack) for i in range(1,n)]+[duration]
    for i in range(1,n+1):lower[i]=max(lower[i],lower[i-1]+required[i-1])
    for i in range(n-1,-1,-1):upper[i]=min(upper[i],upper[i+1]-required[i])
    if any(a>b+.000001 for a,b in zip(lower,upper)):
        raise ValueError('Caption reading speed cannot fit within speech synchronization limits')
    boundaries=[0]
    for i in range(1,n):
        preferred=(captions[i-1]['spoken_end']+captions[i]['spoken_start'])/2
        boundaries.append(max(lower[i],boundaries[-1]+required[i-1],min(preferred,upper[i])))
    boundaries.append(duration)
    for i,c in enumerate(captions):
        c.update(start=boundaries[i],end=boundaries[i+1],cps=len(c['text'])/(boundaries[i+1]-boundaries[i]))

def make_timeline(episode, alignment=None, voice_duration=None):
    words=alignment_words(alignment) if alignment else []
    if words and normalized(script(episode))!=''.join(normalized(w['text']) for w in words):
        raise ValueError(f"{episode['id']}: provider text does not match script")
    beats=[]; captions=[]; cursor=0; clock=.12
    for beat_index, (kind, text) in enumerate(episode['beats']):
        end=cursor+len(normalized(text))
        matched=[w for w in words if w['b']>cursor and w['a']<end]
        start=matched[0]['start'] if matched else clock
        stop=matched[-1]['end'] if matched else start+max(len(text)/18.5,len(text.split())/2.9)
        beats.append({'kind':kind,'text':text,'start':start,'end':stop})
        chunks=caption_chunks(text,balanced=episode.get('balanced_captions',False))
        override=episode.get('caption_overrides',{}).get(str(beat_index))
        if override is not None:
            if not isinstance(override,list) or not all(isinstance(x,str) and x for x in override) or ' '.join(override)!=text:
                raise ValueError('Caption override must preserve the exact spoken text')
            chunks=[c for part in override for c in caption_chunks(part,balanced=episode.get('balanced_captions',False))]
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
        # Use an unused trailing pause too, while preserving the next speech cue.
        c['end']=min(next_start,max(c['end'],c['start']+len(c['text'])/20))
        c['cps']=len(c['text'])/max(.001,c['end']-c['start'])
    if words and any(c['cps']>20.01 for c in captions):
        fit_caption_timing(captions,duration)
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
