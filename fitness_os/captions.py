"""Retain human-corrected SRT tied to exact narration and accepted audio."""
import re
from pathlib import Path
from .common import OSFailure, read_json, file_hash, fingerprint, write_json, atomic_write, rooted


def binding(pilot, variant, audio):
    beats = {b["id"]: b for b in pilot["beats"]}
    return fingerprint([{"beat": bid, "narration": beats[bid]["narration"], "audio_sha256": audio[bid]["sha256"]} for bid in pilot["variants"][variant]])


def validate_srt(text, duration):
    def seconds(value):
        hours, minutes, seconds, millis = map(int, re.split("[:,]", value))
        if minutes >= 60 or seconds >= 60:
            raise OSFailure("Invalid SRT timestamp")
        return hours*3600+minutes*60+seconds+millis/1000
    previous, cues = 0.0, 0
    for index, block in enumerate(re.split(r"\n\s*\n", text.strip().replace("\r\n", "\n")), 1):
        lines = block.splitlines()
        match = re.fullmatch(r"(\d{2,}:\d{2}:\d{2},\d{3}) --> (\d{2,}:\d{2}:\d{2},\d{3})", lines[1]) if len(lines) >= 3 else None
        if not match or lines[0] != str(index) or not " ".join(lines[2:]).strip():
            raise OSFailure("Use sequential nonempty SRT cues with standard timestamps")
        start, end = map(seconds, match.groups())
        if start < previous or end <= start or end > duration+.05:
            raise OSFailure("Caption cues overlap or exceed the recorded duration")
        previous, cues = end, index
    return cues


def import_captions(root, pilot_id, variant, source, reviewer):
    from .catalog import inputs, load_pilot
    pilot = load_pilot(root, pilot_id)
    if variant not in pilot["variants"] or not reviewer.strip():
        raise OSFailure("A valid variant and accountable caption reviewer are required")
    # Load audio directly so a stale previous correction can be replaced deliberately.
    audio = {}
    for beat in pilot["beats"]:
        record = read_json(Path(root)/f".local/audio/{pilot_id}/{beat['id']}.json")
        if record["script_hash"] != fingerprint(beat["narration"]) or file_hash(rooted(root, record["path"])) != record["sha256"]:
            raise OSFailure("Accept current narration before importing captions")
        audio[beat["id"]] = record
    text = Path(source).read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    count = validate_srt(text, sum(a["duration"] for a in audio.values()))
    digest = fingerprint(text)
    path = Path(root)/f".local/caption_sources/{digest}.srt"
    atomic_write(path, text)
    record = {"path":str(path.relative_to(root)),"sha256":file_hash(path),"binding_hash":binding(pilot, variant, audio),"reviewer":reviewer,"cues":count}
    write_json(Path(root)/f".local/captions/{pilot_id}/{variant}.json", record)
    return record


def to_vtt(srt):
    return "WEBVTT\n\n"+re.sub(r"(\d{2,}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt)
