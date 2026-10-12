# Rep & Reason — Blender MVP

One complete vertical fitness explainer: **Your workout took an hour. Where did it go?**

Open [index.html](index.html) after cloning or downloading the repository: its player and download button work offline. To restore a standalone MP4, run `python tools/blender/unpack_mvp.py` from the repository root. The video has Blender animation, synthetic narration, burned-in captions, an original procedural music bed and transition effects. It is an internal creative MVP, not a published episode or a live audience experiment.

## Deliverables

- `media/`: the complete 51-second MP4 stored in small lossless parts, with a checksum manifest. The unpack command restores `Rep_and_Reason_Blender_MVP.mp4`: 1080 × 1920, 30 fps, H.264/AAC.
- `player.js`: loads those same bytes for offline playback and download.
- `time-audit.blend`: four editable scenes, lights, materials and animation.
- `captions.srt`: caption timings from the synthesized audio clips.
- `timeline.json`: actual scene and caption boundaries.
- `poster.jpg` and `contact-sheet.jpg`: review images.
- `build-receipt.json`: source/output fingerprints and release status.
- `../../content/mvp/time-audit/episode.json`: editable copy and sequence.
- `../../tools/blender/`: geometry, narration and composition scripts.

The 15/25/8/12-minute split is **invented for demonstration**, totals 60 minutes, and is labeled in narration and on screen. It does not describe a study, a typical person, or the viewer. No muscle-growth, strength, safety, or time-saving result is promised.

## Rebuild

The tested toolchain is Blender 4.5.3 LTS, Python 3.12, FFmpeg, Pillow, NumPy, SciPy, Piper's eSpeak bridge (1.8.0), and OpenVINO 2026.4.1. The packaged scripts perform no downloads or public publishing.

1. Install Blender and FFmpeg. Install the optional Python dependencies in a virtual environment:

   `python -m pip install numpy pillow scipy piper-tts==1.8.0 openvino==2026.4.1`

2. Download the model and its adjacent `.onnx.json` configuration from the [LJ Speech high voice directory](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ljspeech/high). Keep model weights outside Git. The linked model card identifies the speech dataset as public domain; a copy is retained with the episode.

3. From the repository root, prepare audio:

   `python tools/blender/compose_mvp.py --audio-only --voice-model /absolute/path/en_US-ljspeech-high.onnx`

4. Render the Blender scenes:

   `blender --background --python tools/blender/build_scene.py -- --out .local/blender-mvp`

5. Assemble:

   `python tools/blender/compose_mvp.py`

6. Copy `.local/blender-mvp/time-audit.blend` to this folder after a successful render.

7. If updating the retained video, run `python tools/blender/pack_mvp.py` and commit the refreshed `media/` files and index.

Use `--stills` to inspect a cheaper Blender look check. The default full render requires all 48 frames for each of four props; the compositor rejects incomplete loops and an episode that differs from the narration's source hash. Voice clips are cached by text, model hash and synthesis settings. Re-render geometry when changing `build_scene.py`. Neural synthesis is not claimed to be bit-identical across machines or runtime versions.

The local inference adapter uses OpenVINO and explicitly declines optional diagnostic collection. It does not import ONNX Runtime. The previous ONNX Runtime path was rejected by automatic approval review for telemetry, and is not used in this deliverable.

## Creative direction

Faceless narration with product-like 3D props, midnight/navy backgrounds, lime emphasis and large Space Grotesk type. This is an intentional Blender experiment within the proposed Rep & Reason identity. The current operational `config/brand.json` and the six earlier A/B stimuli remain separately versioned.

The next useful review is the actual narrated MP4: pacing, voice preference, mobile readability, and whether the example makes the logging task clear. Synthetic narration is a prototype choice. Name clearance, editorial review, voice/art direction approval, platform upload and audience measurement remain separate decisions.

## Provenance

All 3D geometry, lighting, materials, motion, layout and procedural music/effects were created for this MVP. No stock 3D models, purchased music, generated human demonstrations, or voice clones are used. Space Grotesk is bundled with its SIL Open Font License in the episode's `fonts` folder. Blender and speech model weights are not bundled in this repository.

Workspace maintenance removed interrupted local exports before they reached GitHub. This version was rebuilt from the source checkpoint and editable Blender project recovered from GitHub, then rendered and checked again. See `../../brand/RECOVERY_STATUS.md` for the separate older brand-package recovery limits.

The large single-file GitHub upload repeatedly stalled. Small transfer parts preserve the exact verified MP4 without recompression. The local unpacked MP4 is ignored by Git; the complete video bytes are tracked under `media/`. Both the Python unpacker and browser player reconstruct the same video.
