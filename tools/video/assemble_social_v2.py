"""Assemble the OpenArt social cut without rebuilding the completed Blender MVP.

Requires Python 3, Pillow, NumPy, FFmpeg. Run from any directory.
Input clips: .local/openart-v2/{minimax,seedance}.mp4.
The original mixed soundtrack is reused; no new speech/model calls are made.
"""
import argparse
import hashlib
import json
import math
import subprocess
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H, FPS, SR = 1080, 1920, 30, 48000
NAVY, CREAM, LIME = '#10233E', '#F7F4EA', '#B9F227'
MUTED, BLUE, CORAL = '#9EADBF', '#74B9FF', '#FF6B4A'
COLORS = [LIME, CREAM, BLUE, CORAL]
LABELS = ['LIFTING', 'REST', 'SETUP', 'WAITING']
VALUES = [15, 25, 8, 12]
TITLE = {
    'hook': ('AN HOUR.', 'OF WHAT?'),
    'audit': ('FOUR BUCKETS.', 'ONE SESSION.'),
    'friction': ('FIND THE', 'FRICTION.'),
    'rest': ('REST IS PART', 'OF THE PLAN.'),
    'action': ('LOG. CHANGE.', 'COMPARE.'),
    'close': ('KNOW WHY.', 'TRAIN BETTER.'),
}


def run(args):
    subprocess.run(args, check=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(None)
def font(size, weight=500):
    f = ImageFont.truetype(str(ROOT / 'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'), size)
    f.set_variation_by_axes([weight])
    return f


def ease(x):
    return 1 - (1 - min(1, max(0, x))) ** 3


def wrap(text, size, width):
    f = font(size, 600)
    lines, line = [], ''
    for word in text.split():
        candidate = (line + ' ' + word).strip()
        if f.getlength(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    return lines + ([line] if line else [])


def center(d, y, text, size, color=CREAM, weight=600, cx=500):
    f = font(size, weight)
    d.text((cx - d.textlength(text, font=f) / 2, y), text, font=f, fill=color)


def stamp(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def make_timeline():
    original = json.loads((ROOT / 'examples/blender-mvp/timeline.json').read_text())
    scenes, cues, cursor = [], [], 0
    for source in original['scenes']:
        source_start = source['cues'][0]['start'] - .10
        natural = source['cues'][-1]['end'] + .25 - source_start
        duration = math.ceil(max(natural, 2.3 if source['id'] == 'close' else 0) * FPS) / FPS
        mapped = [{**c, 'start': round(cursor + c['start'] - source_start, 4),
                   'end': round(cursor + c['end'] - source_start, 4)} for c in source['cues']]
        scene = {'id': source['id'], 'start': cursor, 'end': cursor + duration,
                 'duration': duration, 'source_start': source_start, 'cues': mapped}
        if source['id'] in ('hook', 'rest'):
            scene['clip'] = 'minimax' if source['id'] == 'hook' else 'seedance'
            # Hold the intended camera movement within the unclipped source section.
            scene['source_video_seconds'] = 3.5 if source['id'] == 'hook' else 4.8
        scenes.append(scene)
        cues.extend(mapped)
        cursor += duration
    return {'episode': 'Rep & Reason / time audit / social v2', 'fps': FPS,
            'duration': round(cursor, 4), 'scenes': scenes, 'cues': cues,
            'narration': 'Existing synthetic MVP narration, no voice cloning',
            'example': '15 + 25 + 8 + 12 = 60 invented minutes; not measured data',
            'public_upload': False}


def prepare_audio(timeline, work):
    original = work / 'original-audio.wav'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i',
         str(ROOT / 'examples/blender-mvp/Rep_and_Reason_Blender_MVP.mp4'),
         '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', str(original)])
    with wave.open(str(original), 'rb') as f:
        a = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').reshape(-1, 2).astype(np.float64) / 32768
    parts = []
    for s in timeline['scenes']:
        n = round(s['duration'] * SR)
        start = round(s['source_start'] * SR)
        part = a[start:start + n].copy()
        fade = round(.025 * SR)
        part[:fade] *= np.linspace(0, 1, fade)[:, None]
        part[-fade:] *= np.linspace(1, 0, fade)[:, None]
        parts.append(part)
    audio = np.concatenate(parts)
    # The original source is already loudness mastered. Avoid re-normalizing it.
    with wave.open(str(work / 'social-audio.wav'), 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((np.clip(audio, -.999, .999) * 32767).astype('<i2').tobytes())


def background():
    y, x = np.mgrid[0:H, 0:W]
    glow = np.exp(-(((x - 780) / 950) ** 2 + ((y - 900) / 1250) ** 2) * 2)
    a = np.empty((H, W, 3), dtype=np.uint8)
    for i, (low, high) in enumerate([(6, 18), (16, 39), (30, 63)]):
        a[:, :, i] = low + (high - low) * glow
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    for x in range(80, 1000, 48):
        for y in range(500, 1420, 48):
            d.ellipse((x, y, x + 1, y + 1), fill='#25394C')
    return im


BG = background()


def clip_frame(s, local, work):
    source_t = local / s['duration'] * s['source_video_seconds']
    b = subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(source_t),
        '-i', str(work / (s['clip'] + '.mp4')), '-frames:v', '1', '-vf', 'scale=1080:1920',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-threads', '1', '-'])
    return Image.frombytes('RGB', (W, H), b)


def draw_header(im, s, local, index):
    d = ImageDraw.Draw(im)
    d.text((80, 118), 'REP & REASON', font=font(30, 700), fill=CREAM)
    d.text((700, 122), 'FIELD NOTE 001', font=font(23, 500), fill=MUTED)
    d.line((80, 185, 920, 185), fill='#395063', width=2)
    yoff = round(18 * (1 - ease(local / .35)))
    size = 89 if s['id'] not in ('audit', 'close') else 85
    for i, text in enumerate(TITLE[s['id']]):
        d.text((74, 235 + i * 99 + yoff), text, font=font(size, 700), fill=CREAM if i == 0 else LIME)
    # Upper progress rail avoids platform controls and descriptions near the bottom.
    for k in range(6):
        x = 80 + k * 143
        d.rounded_rectangle((x, 464, x + 122, 468), radius=2, fill=LIME if k <= index else '#34465B')


def draw_audit(im, s, local):
    d = ImageDraw.Draw(im)
    d.text((80, 535), 'WHERE THE 60 MINUTES GO', font=font(27, 600), fill=MUTED)
    for k, (label, value, color) in enumerate(zip(LABELS, VALUES, COLORS)):
        y = 625 + k * 158
        d.text((80, y), label, font=font(35, 600), fill=CREAM)
        d.text((775, y - 14), f'{value}m', font=font(52, 700), fill=color)
        d.rounded_rectangle((80, y + 62, 920, y + 99), radius=10, fill='#24364B')
        progress = ease((local - .25 - k * .15) / 1.3)
        bar_width = 840 * value / 60 * progress
        if bar_width > 1:
            d.rounded_rectangle((80, y + 62, 80 + bar_width, y + 99), radius=10, fill=color)
    d.rounded_rectangle((80, 1300, 920, 1400), radius=18, outline='#496175', width=2, fill='#15283D')
    center(d, 1314, 'ILLUSTRATIVE EXAMPLE', 29, LIME)
    center(d, 1354, 'Invented numbers, not measured data', 24, MUTED, 500)


def dumbbell(d, x, y, color):
    d.rounded_rectangle((x - 76, y - 10, x + 76, y + 10), radius=7, fill=color)
    for side in (-1, 1):
        q = x + side * 65
        d.rounded_rectangle((q - 15, y - 47, q + 15, y + 47), radius=7, fill=color)


def draw_friction(im, s, local):
    d = ImageDraw.Draw(im)
    d.text((80, 540), 'ONE DELAY YOU CAN CHANGE', font=font(27, 600), fill=MUTED)
    # One subject, one simple story: repeated walks between a station and a rack.
    for x, label in [(240, 'YOUR STATION'), (760, 'EQUIPMENT')]:
        d.rounded_rectangle((x - 160, 660, x + 160, 930), radius=26, fill='#152C43', outline='#38536A', width=2)
        dumbbell(d, x, 770, LIME if x == 240 else BLUE)
        center(d, 865, label, 23, MUTED, 500, x)
    d.line((240, 1005, 760, 1005), fill='#52677A', width=4)
    x = 240 + 520 * (.5 - .5 * math.cos(local * 1.8))
    d.ellipse((x - 16, 989, x + 16, 1021), fill=CORAL)
    center(d, 1050, 'BACK. AND FORTH. AND BACK.', 29, CORAL)
    d.rounded_rectangle((80, 1190, 920, 1375), radius=24, fill='#1F3543', outline='#6D8C3F', width=2)
    d.text((110, 1210), 'TRY ONE PRACTICAL CHANGE', font=font(25, 700), fill=LIME)
    d.text((110, 1260), 'Group your equipment.', font=font(45, 600), fill=CREAM)
    d.text((110, 1323), 'Then compare your next session.', font=font(26), fill=MUTED)


def draw_rest(im, local):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((80, 1265, 920, 1380), radius=23, fill='#10273B', outline='#84A936', width=2)
    center(d, 1286, 'BIGGEST BLOCK ≠ BIGGEST PROBLEM', 30, LIME)
    center(d, 1334, 'A time audit is not a rest prescription.', 24, CREAM, 500)


def draw_action(im, s, local):
    d = ImageDraw.Draw(im)
    d.text((80, 536), 'YOUR NEXT WORKOUT', font=font(27, 600), fill=MUTED)
    d.rounded_rectangle((80, 610, 920, 1060), radius=24, fill='#14283E', outline='#38526A', width=2)
    d.text((110, 636), 'ONE SESSION LOG', font=font(25, 700), fill=LIME)
    d.text((765, 638), 'MINS', font=font(24), fill=MUTED)
    for i, (label, color) in enumerate(zip(LABELS, COLORS)):
        y = 712 + i * 81
        d.ellipse((112, y + 13, 125, y + 26), fill=color)
        d.text((145, y), label, font=font(30, 600), fill=CREAM)
        d.line((765, y + 35, 860, y + 35), fill='#7E8D9E', width=2)
        if i < 3:
            d.line((110, y + 63, 890, y + 63), fill='#2A4157', width=1)
    thresholds = [0, s['cues'][1]['start'] - s['start'], s['cues'][2]['start'] - s['start']]
    active = max(i for i, v in enumerate(thresholds) if local >= v)
    labels = ['LOG ONE SESSION', 'CHANGE ONE THING', 'COMPARE NEXT TIME']
    for i, text in enumerate(labels):
        y = 1120 + i * 86
        color = LIME if i == active else MUTED
        d.ellipse((80, y, 133, y + 53), fill=LIME if i == active else '#243A50')
        center(d, y + 8, str(i + 1), 27, NAVY if i == active else CREAM, 700, 106)
        d.text((155, y + 3), text, font=font(35, 700 if i == active else 500), fill=color)


def draw_close(im, local):
    d = ImageDraw.Draw(im)
    d.text((80, 625), 'MAKE THE NEXT SESSION', font=font(34), fill=MUTED)
    d.text((75, 690), 'AN EXPERIMENT.', font=font(73, 700), fill=CREAM)
    d.rounded_rectangle((80, 870, 920, 1115), radius=28, fill=LIME)
    center(d, 907, 'TRY ONE', 66, NAVY, 700)
    center(d, 995, 'SESSION AUDIT', 58, NAVY, 700)
    center(d, 1210, 'LIFTING / REST / SETUP / WAITING', 26, MUTED)


def frame(t, timeline, work, base=None, captions=True):
    idx = next((i for i, s in enumerate(timeline['scenes']) if t < s['end'] - .00001), 5)
    s = timeline['scenes'][idx]
    local = t - s['start']
    im = base.copy() if base is not None else clip_frame(s, local, work) if 'clip' in s else BG.copy()
    # The footage has clean negative space above the props; only a subtle title shade is needed.
    if 'clip' in s:
        shade = Image.new('RGBA', (W, 500), (4, 14, 28, 28))
        im.paste(shade, (0, 0), shade)
    draw_header(im, s, local, idx)
    if s['id'] == 'audit': draw_audit(im, s, local)
    elif s['id'] == 'friction': draw_friction(im, s, local)
    elif s['id'] == 'rest': draw_rest(im, local)
    elif s['id'] == 'action': draw_action(im, s, local)
    elif s['id'] == 'close': draw_close(im, local)
    elif s['id'] == 'hook':
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((80, 515, 345, 585), radius=35, fill=LIME)
        d.text((108, 527), '60 MINUTES', font=font(33, 700), fill=NAVY)
    cue = next((c for c in s['cues'] if c['start'] - .025 <= t < c['end'] + .07), None)
    if cue and captions:
        d = ImageDraw.Draw(im)
        lines = wrap(cue['text'], 49, 800)
        assert len(lines) <= 2, cue['text']
        top = 1490
        bottom = top + len(lines) * 64 + 36
        d.rounded_rectangle((60, top - 13, 940, bottom), radius=22, fill='#081421', outline='#3F5266', width=2)
        d.rounded_rectangle((80, top + 6, 86, bottom - 18), radius=3, fill=LIME)
        for k, line in enumerate(lines):
            center(d, top + k * 64, line, 49, CREAM, 600)
    return im


def render(timeline, work, out, clean=False):
    dest = out / ('Rep_and_Reason_Time_Audit_V2_Clean.mp4' if clean else 'Rep_and_Reason_Time_Audit_V2.mp4')
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
           '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(work / 'social-audio.wav'),
           '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-threads', '4',
           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest',
           '-metadata', 'title=Rep & Reason — Where did that hour go?', str(dest)]
    encoder = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for s in timeline['scenes']:
            count = round(s['duration'] * FPS)
            decoder = None
            if 'clip' in s:
                speed = s['duration'] / s['source_video_seconds']
                decoder = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'error',
                    '-i', str(work / (s['clip'] + '.mp4')), '-an', '-vf', f'setpts={speed}*PTS,scale=1080:1920,fps=30',
                    '-frames:v', str(count), '-threads', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
            try:
                for i in range(count):
                    base = None
                    if decoder:
                        b = decoder.stdout.read(W * H * 3)
                        if len(b) != W * H * 3: raise RuntimeError('Truncated source video')
                        base = Image.frombytes('RGB', (W, H), b)
                    encoder.stdin.write(frame(s['start'] + i / FPS, timeline, work, base, not clean).tobytes())
            finally:
                if decoder:
                    decoder.stdout.close()
                    if decoder.wait() != 0: raise RuntimeError('Source decoder failed')
            print('RENDERED', s['id'], round(s['end'], 3), flush=True)
        encoder.stdin.close()
        if encoder.wait() != 0: raise RuntimeError('Video encoder failed')
    finally:
        if encoder.poll() is None: encoder.terminate()
    return dest


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--work', type=Path, default=ROOT / '.local/openart-v2')
    p.add_argument('--out', type=Path, default=ROOT.parent / 'deliverables')
    p.add_argument('--stills-only', action='store_true')
    p.add_argument('--clean', action='store_true')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    timeline = make_timeline()
    print('DURATION', timeline['duration'], flush=True)
    (args.out / 'timeline.json').write_text(json.dumps(timeline, indent=2) + '\n')
    (args.out / 'Rep_and_Reason_Time_Audit_V2.srt').write_text('\n\n'.join(
        f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n" + '\n'.join(wrap(c['text'], 49, 800))
        for i, c in enumerate(timeline['cues'])) + '\n')
    contact = Image.new('RGB', (1080, 1280))
    for i, s in enumerate(timeline['scenes']):
        t = s['start'] + min(1.6, s['duration'] / 2)
        im = frame(t, timeline, args.work)
        im.save(args.work / f'v2-scene-{i+1:02}.jpg', quality=93)
        contact.paste(im.resize((360, 640), Image.Resampling.LANCZOS), ((i % 3) * 360, (i // 3) * 640))
        if i == 0: im.save(args.out / 'Rep_and_Reason_Time_Audit_V2_Poster.jpg', quality=95)
    contact.save(args.out / 'contact-sheet.jpg', quality=94)
    if args.stills_only: return
    prepare_audio(timeline, args.work)
    dest = render(timeline, args.work, args.out, args.clean)
    receipt = {**{k: v for k, v in timeline.items() if k not in ('scenes', 'cues')},
               'width': W, 'height': H, 'video_sha256': sha(dest),
               'original_mvp_sha256': sha(ROOT / 'examples/blender-mvp/Rep_and_Reason_Blender_MVP.mp4'),
               'script_sha256': sha(__file__), 'caption_count': len(timeline['cues']),
               'selected_clips': {n: sha(args.work / (n + '.mp4')) for n in ('minimax', 'seedance')},
               'additional_generation_credits': 0}
    (args.out / 'build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('COMPLETE', dest, flush=True)


if __name__ == '__main__':
    main()
