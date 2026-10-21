"""Prepare the approved voice, word-aligned captions and media for social V3.

No network calls. Requires NumPy, Pillow and FFmpeg. Input narration and its
Fish timestamp response must already exist; no credential belongs in this file.
"""
import argparse
import json
import math
import re
import subprocess
import textwrap
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FPS, SR, LEAD, TAIL = 30, 44100, .12, .8


def run(*args):
    subprocess.run(list(map(str, args)), check=True)


def normalized(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def stamp(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT / '.local/fish-voice'
    original = json.loads((ROOT / 'examples/blender-mvp/timeline.json').read_text())
    alignment = json.loads((source / 'alignment.json').read_text())
    words, pos = [], 0
    for chunk in alignment.values():
        for seg in chunk['alignment']['segments']:
            count = len(normalized(seg['text']))
            words.append({**seg, 'start': seg['start'] + chunk['offset'] + LEAD,
                          'end': seg['end'] + chunk['offset'] + LEAD,
                          'a': pos, 'b': pos + count})
            pos += count
    script = ' '.join(c['text'] for s in original['scenes'] for c in s['cues'])
    assert normalized(script) == ''.join(normalized(w['text']) for w in words)
    cues, scenes, cursor = [], [], 0
    for scene in original['scenes']:
        indices = []
        for cue in scene['cues']:
            end = cursor + len(normalized(cue['text']))
            ws = [w for w in words if w['b'] > cursor and w['a'] < end]
            cues.append({'text': cue['text'], 'spoken_start': ws[0]['start'],
                         'spoken_end': ws[-1]['end'], 'scene': scene['id']})
            indices.append(len(cues)-1)
            cursor = end
        scenes.append({'id': scene['id'], 'cue_indices': indices})
    with wave.open(str(source / 'narration.wav')) as f:
        voice = np.frombuffer(f.readframes(f.getnframes()), '<i2').astype(float)/32768
        assert f.getframerate() == SR and f.getnchannels() == 1
    duration = math.ceil((LEAD + len(voice)/SR + TAIL)*FPS)/FPS
    for i, cue in enumerate(cues):
        cue['start'] = max(0, cue['spoken_start']-.1)
        next_start = cues[i+1]['spoken_start']-.1 if i+1 < len(cues) else duration
        cue['end'] = min(cue['spoken_end']+.25, next_start)
        cue['lines'] = textwrap.wrap(cue['text'], width=34, break_long_words=False,
                                     break_on_hyphens=False)
        assert len(cue['lines']) <= 2
        cue['cps'] = len(cue['text']) / (cue['end']-cue['start'])
        if cue['cps'] > 20:
            floor = cues[i-1]['end'] if i else 0
            cue['start'] = max(floor, cue['end']-len(cue['text'])/20)
            cue['cps'] = len(cue['text']) / (cue['end']-cue['start'])
    # Break at phrase boundaries rather than leaving short orphan words.
    breaks = {
        2: ['An hour in the gym', 'is not an hour of lifting.'],
        3: ['In this made-up example:', 'fifteen minutes lifting.'],
        4: ['Twenty-five resting.', 'Eight setting up.'],
        12: ['For one session,', 'log the four buckets.'],
        15: ['Measure the friction', 'before you rewrite the plan.'],
    }
    for i, lines in breaks.items():
        assert ' '.join(lines) == cues[i]['text']
        cues[i]['lines'] = lines
    for i, scene in enumerate(scenes):
        scene['start'] = 0 if i == 0 else cues[scene['cue_indices'][0]]['start']
        scene['end'] = cues[scenes[i+1]['cue_indices'][0]]['start'] if i+1 < len(scenes) else duration
    markers = {}
    for key, token in [('lifting', 'fifteen'), ('rest', 'Twenty'), ('setup', 'Eight'), ('waiting', 'twelve')]:
        markers[key] = next(w['start'] for w in words if w['text'].lower() == token.lower())
    timeline = {'episode':'Rep & Reason / time audit / social V3', 'fps':FPS,
                'duration':duration, 'scenes':scenes, 'cues':cues, 'words':words,
                'markers':markers, 'voice_lead':LEAD, 'word_count':len(script.split()),
                'voice_wpm':len(script.split())/(len(voice)/SR)*60,
                'overall_wpm':len(script.split())/duration*60,
                'example':'15 + 25 + 8 + 12 = 60 invented minutes; not measured data',
                'voice_model':'Fish s2.1-pro-free', 'delivery':'approved deeper take; unchanged pitch and speed',
                'public_upload':False}
    (out/'timeline.json').write_text(json.dumps(timeline, indent=2)+'\n')
    (out/'Rep_and_Reason_Time_Audit_V3.srt').write_text('\n\n'.join(
        f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"+'\n'.join(c['lines'])
        for i,c in enumerate(cues))+'\n')
    # A restrained original instrumental bed. No old synthetic voice is reused.
    n = round(duration*SR)
    bed = np.zeros(n)
    notes = [130.8128, 164.8138, 195.9977, 246.9417]
    for i, start in enumerate(np.arange(0, duration, .6)):
        p = round(start*SR)
        t = np.arange(min(round(.6*SR), n-p))/SR
        tone = .011*np.sin(2*np.pi*notes[(i//4)%4]*t)*np.exp(-7*t)
        if i % 4 == 0:
            tone += .019*np.sin(2*np.pi*(47*t+7*(1-np.exp(-15*t))))*np.exp(-22*t)
        bed[p:p+len(t)] += tone
    t = np.arange(n)/SR
    bed *= np.minimum(t/1.2, 1)*np.clip((duration-t)/1.2, 0, 1)
    voice_pad = np.zeros(n)
    voice_pad[round(LEAD*SR):round(LEAD*SR)+len(voice)] = voice
    # Normalize voice RMS before mixing; final loudness is measured by FFmpeg.
    rms = np.sqrt(np.mean(voice**2))
    voice_pad *= min(.15/max(rms, 1e-8), .85/max(np.max(np.abs(voice)), 1e-8))
    mixed = np.column_stack([voice_pad+bed, voice_pad+bed*.96])
    with wave.open(str(out/'mix-unmastered.wav'), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((np.clip(mixed, -.99, .99)*32767).astype('<i2').tobytes())
    run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',out/'mix-unmastered.wav',
        '-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar',48000,'-c:a','pcm_s16le',out/'mix.wav')
    for scene, clip, seconds in [('hook','minimax',3.5),('rest','seedance',4.8)]:
        sc = next(s for s in scenes if s['id']==scene)
        dest = out/clip
        dest.mkdir(exist_ok=True)
        run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',ROOT/f'.local/openart-v2/{clip}.mp4',
            '-vf',f"setpts={(sc['end']-sc['start'])/seconds}*PTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
            '-frames:v',math.ceil((sc['end']-sc['start'])*FPS)+2,'-q:v',3,dest/'%04d.jpg')
    print(json.dumps({'duration':duration,'voice_wpm':timeline['voice_wpm'],
                     'overall_wpm':timeline['overall_wpm'],'max_caption_cps':max(c['cps'] for c in cues),
                     'markers':markers}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=ROOT/'.local/social-v3')
    prepare(p.parse_args().out.resolve())
