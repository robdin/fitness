"""Optional FFmpeg smoke test. All media, reviews and releases are synthetic temporary fixtures."""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from fitness_os.common import read_json, write_json, OSFailure
from fitness_os.pipeline import import_audio, build, approve, release, REVIEW_CHECKS
from fitness_os.captions import import_captions
from fitness_os.render import probe_duration


def main():
    source = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="fitness-synthetic-media-") as directory:
        root = Path(directory)
        for folder in ("config", "content", "research", "fitness_os"):
            shutil.copytree(source/folder, root/folder, ignore=shutil.ignore_patterns("__pycache__"))
        brand = read_json(root/"config/brand.json")
        brand["channel_id"] = "TEST-ONLY-NO-UPLOAD"
        write_json(root/"config/brand.json", brand)
        claims = read_json(root/"research/claims.json")
        for claim in claims:
            claim.update(review_status="approved", reviewer="SYNTHETIC-TEST-FIXTURE-NOT-EDITORIAL-REVIEW")
        write_json(root/"research/claims.json", claims)
        tone = root/"test-tone.wav"
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.8", "-ar", "48000", str(tone)], check=True)
        pilot = read_json(root/"content/pilots/P01-time/pilot.json")
        for beat in pilot["beats"]:
            import_audio(root, pilot["id"], beat["id"], tone, "TEST-ONLY")
        assert tone.exists(), "Import must retain the original"
        built = [build(root, pilot["id"], variant, "recorded") for variant in ("A", "B")]
        durations = [probe_duration(Path(item["path"])/"video.mp4") for item in built]
        assert abs(durations[0]-durations[1]) < .1
        for item in built:
            streams = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(Path(item["path"])/"video.mp4")], capture_output=True, text=True, check=True).stdout)["streams"]
            assert {s["codec_type"] for s in streams} == {"audio", "video"}
        correction = root/"fixture-correction.srt"
        correction.write_text("1\n00:00:00,000 --> 00:00:01,000\nSynthetic timing fixture\n")
        import_captions(root, pilot["id"], "A", correction, "TEST-ONLY")
        corrected = build(root, pilot["id"], "A", "recorded")
        assert corrected["path"] != built[0]["path"]
        assert (Path(corrected["path"])/"captions.srt").read_text() == correction.read_text()
        approve(root, corrected["path"], "TEST-ONLY", REVIEW_CHECKS, "Synthetic fixture exercises release integrity; this is not a real editorial approval.")
        exported = release(root, corrected["path"])
        assert release(root, corrected["path"])["release_id"] == exported["release_id"]
        with open(Path(exported["path"])/"video.mp4", "ab") as stream:
            stream.write(b"intentional-test-corruption")
        try:
            release(root, corrected["path"])
        except OSFailure:
            pass
        else:
            raise AssertionError("A corrupted retained release must be rejected")
        print(json.dumps({"status":"passed","synthetic_recorded_variant_durations":durations,"audio_video_streams":True,"caption_correction_invalidates_build":True,"source_audio_retained":True,"release_copy_corruption_rejected":True,"all_fixture_files":"temporary; removed after completion","real_approvals_or_uploads":0},indent=2))


if __name__ == "__main__":
    main()
