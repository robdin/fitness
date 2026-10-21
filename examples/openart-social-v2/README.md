# Rep & Reason — social cut V2

A 41.067-second vertical edit of “Your workout took an hour. Where did it go?”
The completed 51-second Blender MVP remains unchanged. V2 reuses its existing
synthetic narration and original mixed soundtrack, removes long scene holds,
and adds selected OpenArt footage with precise animated graphics.

## Delivered media

- `Rep_and_Reason_Time_Audit_V2.mp4`: 1080 × 1920, 30 fps, H.264/AAC, 17 burned-in English captions.
- `Rep_and_Reason_Time_Audit_V2.srt`: matching editable subtitle track.
- `Rep_and_Reason_Time_Audit_V2_Sources.zip`: all four downloaded OpenArt video tests, three image candidates, original MVP audio source, font/license, composition script, timelines, captions, poster and build receipt.

The media files are delivered in the project conversation. Large generated source
files are retained in the source package rather than committed to Git. The ZIP
contains the complete local inputs needed to reproduce this cut without contacting
OpenArt or rebuilding Blender. Its root `fitness/` matches the repository layout.

## Editorial decisions

MiniMax footage opens the video; Seedance footage supports the rest section.
Generated clip audio is muted. The remaining scenes use editable graphics so
numbers, labels and captions are exact. All four source clips are preserved for
future comparison, including the unused Gemini and Wan versions.

The 15/25/8/12-minute breakdown is an invented example. That caveat remains spoken,
captioned and visibly labeled. The video encourages logging one session and making
one practical change; it does not promise a training or time-saving outcome.

Captions use at most two lines and keep 266 or more pixels below the caption box.
The final file has not been published to a social account. This assembly used no
additional OpenArt generation credits.

## Reproduce or revise

Requirements: Python 3, Pillow, NumPy and FFmpeg. No Blender, model weights,
credentials, or network requests are needed for assembly.

1. Extract the source ZIP. Run commands from its `fitness/` directory, or copy the
   included `.local/openart-v2/` inputs into an existing repository checkout.
2. Run `python tools/video/assemble_social_v2.py --stills-only` to inspect layouts.
3. Run `python tools/video/assemble_social_v2.py` to create the captioned video.
4. Optional: `python tools/video/assemble_social_v2.py --clean --out ../clean-export`
   creates a version without burned-in subtitles for editors adding native captions.

Default output is `../deliverables/`. Keep text revisions in sync with narration;
this compositor reuses existing speech and does not synthesize changed copy.

## Verification

The final export contains 1,232 frames at 30 fps and 48 kHz stereo AAC. All 17
subtitle cues are ordered, nonoverlapping and inside the finished duration.
Final MP4 checksum and source checksums are in `build-receipt.json`. Visual QA
includes all six scene layouts and the longer two-line captions. Full decode and
audio loudness checks are recorded in `verification.json`.
