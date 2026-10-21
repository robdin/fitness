# Rep & Reason — researched social cut V3

A **36.2-second**, 1080×1920, 30 fps revision using the approved deeper Fish voice,
word-timed JavaScript motion graphics, selected OpenArt footage, original quiet
instrumental backing and 17 synchronized English captions.

The original Blender MVP remains complete and unchanged. The full research
review, evidence limitations and production decisions are in
[`docs/VIDEO_PACING_AND_VISUAL_RESEARCH_2026-10-21.md`](../../docs/VIDEO_PACING_AND_VISUAL_RESEARCH_2026-10-21.md).

## What changed

- The user's existing private studio voice profile supplies the narration through
  Fish `s2.1-pro-free`, with the approved deeper, neutral delivery. No emotion
  tags, pitch adjustment or speech speed change are applied.
- Narration is 175.18 WPM; the full edit including opening and ending space is
  170.72 WPM. This is an editorial baseline to test, not a proven platform optimum.
- Sixty clock markers morph into exactly sixty tiles. The 15/25/8/12 allocations
  reveal as their numbers are spoken and remain labeled as an invented example.
- Equipment trips and the log/change/compare sequence are animated with code.
- Captions follow returned word timestamps, use at most two lines, and stay
  approximately within the conservative Meta ad safe region. Maximum reading
  speed is 20.00 characters/second before SRT millisecond rounding.
- The selected MiniMax and Seedance footage from V2 is reused with its audio
  muted. This assembly spends no additional OpenArt generation credits.

## Delivered files

The project conversation contains the MP4, SRT, poster and source ZIP. The source
ZIP preserves the exact narration WAV, alignment response, selected OpenArt
clips, font/license, scripts and research. Large media and the private voice audio
are delivered in that package rather than committed to this repository.

`timeline.json`, `build-receipt.json`, `verification.json` and the SRT are retained
here for review. The provider's alignment text was checked against every word of
the intended script; this is not an independent transcription or a claim that a
human has audited the audio. No social account publication has occurred.

## Reproduce offline

Extract the source ZIP. Its `fitness/` root mirrors this repository. Requirements:
Python 3 with NumPy and Pillow, FFmpeg/ffprobe, Node.js and `@napi-rs/canvas`.
The package version used for delivery is recorded in the build receipt.

```bash
cd fitness
python tools/video/assemble_social_v3.py
```

Install `@napi-rs/canvas` in the checkout or expose its installed location through
`NODE_PATH`. `CODEX_PRIMARY_RUNTIME_NODE` and `CODEX_PRIMARY_RUNTIME_NODE_MODULES`
are optional runtime integration variables. The compositor renders five-second
pieces in separate processes to bound native image-cache memory, then joins them
without an additional video encode. Expected final output:
`../deliverables/v3/Rep_and_Reason_Time_Audit_V3.mp4`.

For layout checks only:

```bash
python tools/video/prepare_social_v3.py
node tools/video/render_social_v3.cjs .local/social-v3 ../preview --stills
```

Regenerating narration is optional and is a separate network action. The existing
WAV is sufficient for offline reproduction. To generate a revised script, run
`tools/video/generate_fish_narration.py --voice-id YOUR_PRIVATE_PROFILE_ID`; provide
the credential through `FISH_API_KEY` or its hidden prompt. Never commit a key.
The model name and availability must be rechecked before a future generation;
the successful free-model request during this build is not a promise of perpetual
free service. A regenerated voice is not guaranteed to be byte-identical.

## Editorial boundaries

The time breakdown is fictional, totals exactly 60 minutes and is labeled in
speech, captions and graphics. There are no measured performance gains, fabricated
before/after numbers, or prescriptions to shorten every rest interval. The video
asks the viewer to log one session, change one practical source of delay and compare.
