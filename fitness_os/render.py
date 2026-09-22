from __future__ import annotations
import math
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .common import OSFailure, atomic_write, file_hash


def font_path(root, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    options = [Path(root)/"assets/fonts"/name, Path("/usr/share/fonts/truetype/dejavu")/name]
    for path in options:
        if path.exists():
            return path
    raise OSFailure("Install DejaVu Sans or put its TTF files in assets/fonts (retain license).")


def environment(root):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise OSFailure("FFmpeg and ffprobe are required for media rendering")
    return {"ffmpeg": subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True).stdout.splitlines()[0],
            "font": file_hash(font_path(root)), "bold_font": file_hash(font_path(root, True))}


def wrapped(draw, text, font, width):
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) > width and current:
            lines.append(current); current = word
        else:
            current = trial
    return lines + ([current] if current else [])


def card(root, brand, pilot, beat, path, index, total, preview=True):
    palette = brand["palette"]
    navy, lime, cream, coral = [palette[x] for x in ("navy", "lime", "cream", "coral")]
    im = Image.new("RGB", (1280, 720), navy)
    d = ImageDraw.Draw(im)
    font = lambda size, bold=False: ImageFont.truetype(str(font_path(root, bold)), size)
    d.rounded_rectangle((55, 47, 133, 91), radius=13, fill=lime)
    d.text((69, 54), "DEX", font=font(23, True), fill=navy)
    d.text((151, 57), "PROJECT FITNESS  /  KNOW WHY. TRAIN BETTER.", font=font(19), fill=cream)
    title_lines = wrapped(d, beat["heading"], font(49, True), 1130)
    if len(title_lines) > 2:
        raise OSFailure("Heading is too long for the card")
    y = 144
    for line in title_lines:
        d.text((65, y), line, font=font(49, True), fill=cream); y += 61
    y += 31
    for number, text in enumerate(beat["lines"], 1):
        text_lines = wrapped(d, text, font(30), 995)
        if y + len(text_lines)*41 > 574:
            raise OSFailure(f"Screen text overflows: {pilot['id']}/{beat['id']}")
        d.rounded_rectangle((66, y+3, 106, y+36), radius=8, fill=lime)
        d.text((77, y+5), str(number), font=font(21, True), fill=navy)
        for line in text_lines:
            d.text((126, y), line, font=font(30), fill=cream); y += 41
        y += 20
    d.line((65, 608, 1215, 608), fill="#42526A", width=2)
    note = beat.get("source_label", "Original decision worksheet • educational example")
    for j, line in enumerate(wrapped(d, note, font(17), 1100)):
        d.text((65, 625+j*22), line, font=font(17), fill="#BEC8D6")
    d.text((65, 683), "SILENT PROTOTYPE • REVIEW PENDING" if preview else "REVIEW COPY • RECORDED AUDIO", font=font(15, True), fill=coral)
    d.text((1142, 681), f"{index}/{total}", font=font(16), fill=cream)
    im.save(path)


def thumbnail(root, brand, text, path, alternative=False):
    im = Image.new("RGB", (1280,720), brand["palette"]["navy"])
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(font_path(root, True)), 91)
    lines = wrapped(d, text.upper(), font, 1010)
    if len(lines)>4:
        raise OSFailure("Thumbnail headline too long")
    d.rounded_rectangle((65,55,235,111), radius=15, fill=brand["palette"]["lime"])
    d.text((91,60), "DEX", font=ImageFont.truetype(str(font_path(root,True)),40), fill=brand["palette"]["navy"])
    for index, line in enumerate(lines):
        d.text((72,185+index*105), line, font=font, fill=brand["palette"]["cream"])
    d.rectangle((73,645,1198,655), fill=brand["palette"]["coral" if alternative else "lime"])
    im.save(path)


def probe_duration(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True, check=True)
    value = float(result.stdout.strip())
    if not math.isfinite(value) or value <= 0:
        raise OSFailure("Invalid media duration")
    return value


def timestamp(seconds):
    ms = round(seconds*1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms,60000); s, ms=divmod(ms,1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def media(root, bundle, data):
    pilot, variant = data["pilot"], data["variant"]
    beats = {b["id"]: b for b in pilot["beats"]}
    order = pilot["variants"][variant]
    durations, audio = [], []
    ffconcat = ["ffconcat version 1.0"]
    captions, elapsed, cue = [], 0.0, 1
    for i, bid in enumerate(order, 1):
        beat = beats[bid]
        frame = bundle / f"scene-{i:02}.png"
        card(root, data["brand"], pilot, beat, frame, i, len(order), data["mode"]=="preview")
        if data["mode"] == "recorded":
            apath = Path(root) / data["audio"][bid]["path"]
            audio.append(apath)
            duration = probe_duration(apath)
        else:
            duration = max(8, len(beat["narration"].split())/150*60)
        durations.append(duration)
        ffconcat += [f"file '{frame.name}'", f"duration {duration:.6f}"]
        words = beat["narration"].split()
        chunks = [" ".join(words[j:j+12]) for j in range(0,len(words),12)]
        for j, text in enumerate(chunks):
            start = elapsed+duration*j/len(chunks)
            end = elapsed+duration*(j+1)/len(chunks)
            captions.append(f"{cue}\n{timestamp(start)} --> {timestamp(end)}\n{text}\n")
            cue += 1
        elapsed += duration
    ffconcat.append(f"file 'scene-{len(order):02}.png'")
    atomic_write(bundle/"frames.ffconcat", "\n".join(ffconcat)+"\n")
    atomic_write(bundle/"captions.srt", "\n".join(captions))
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-safe", "1", "-f", "concat", "-i", "frames.ffconcat", "-t", str(sum(durations)), "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-threads", "2", "-an", "silent.mp4"], cwd=bundle, check=True, capture_output=True)
    if audio:
        arguments = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
        for path in audio:
            arguments += ["-i", str(path)]
        transforms = [f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=mono[a{i}]" for i in range(len(audio))]
        transforms.append("".join(f"[a{i}]" for i in range(len(audio)))+f"concat=n={len(audio)}:v=0:a=1[out]")
        subprocess.run(arguments+["-filter_complex", ";".join(transforms), "-map", "[out]", str(bundle/"narration.wav")], check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", str(bundle/"silent.mp4"), "-i", str(bundle/"narration.wav"), "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(bundle/"video.mp4")], check=True, capture_output=True)
    else:
        (bundle/"silent.mp4").rename(bundle/"video.mp4")
    return durations
