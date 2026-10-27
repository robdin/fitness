# D — Off-Duty Hero · content comparison

**Updated content, 27 October 2026:** the same three retained poses are now also applied to BC04, BC11 and BC16 from [conversational V6](../../docs/MONTH_ONE_V6.md). Review `.local/blueprint-character-d-v6-preview/index.html`. These refreshed comparisons use the new voice and examples; the original BP comparisons described below remain intact. No new character generation or full-month character rollout was performed.

Selected by the owner on 24 October 2026 from six character concepts. The request was to see existing content side by side with and without D. This is the current character direction; the graphics-led Blueprint month remains the baseline until a broader production change is requested.

## Identity and role

An approachable adult man with a lean athletic build, wavy dark hair, cream tee, cobalt overshirt and headphones. A soft slice-of-life anime treatment connects the dreamy brand to ordinary routines. Aspiration includes making lunch, moving through the day and returning after a setback. He is a fictional companion, not an expert credential, customer testimonial or promised body outcome.

The reference and generated poses are retained locally. The three poses cover a commute with a bag, preparing a bowl and a reassuring open-hand gesture. They are still illustrations; there is no lip synchronization or character animation in this preview.

## Actual content used

| Episode | Topic | Pose |
| --- | --- | --- |
| BP04 | A walk in your real week | Bag / commute |
| BP11 | Tomorrow’s lunch | Bowl / food preparation |
| BP16 | Returning after a missed workout | Welcoming gesture |

Review hub: `.local/blueprint-character-d-preview/index.html`.

Each episode folder includes the original MP4, the character edition, a synchronized side-by-side MP4, two still comparisons, the original subtitles and posting copy. The side-by-side file has one original audio track. Labels identify the original on the left and D on the right.

Delivery archive: `../fitness-deliverables/blueprint-character-d-preview/Off_Duty_Hero_Comparisons.zip`.

## Comparison boundaries and checks

- Original editions are byte-identical copies of verified Blueprint masters.
- The character is placed only below y=1510 in the decorative area of each 1080 × 1920 video. Captions, diagrams, source cues, timing and wording are retained. Re-encoding can introduce small compression differences elsewhere.
- All nine MP4s pass full decoding, frame-count, duration, dimensions and codec checks. Encoded audio hashes match within each three-file set.
- Still frames from each pair were visually inspected. Browser playback was checked for the walking comparison. This does not replace full listening or target-app review.
- Native Reels/Shorts overlays can cover part of this lower placement. This is a conservative companion preview, not a finalized platform-safe character layout.

`verification.json` retains output hashes and checks. `generation.json` retains the image-generation prompt and source reference. No full-month media or experiment files were replaced. The BP03 citation comparison remains separate.

## Rebuilding locally

Keep the original Blueprint masters and their receipts under `.local/month-one-v5-blueprint/review`, and the generated RGBA pose atlas at `.local/blueprint-character-d-preview/assets/off-duty-poses.png`.

```sh
.venv/bin/python tools/video/build_off_duty_preview.py
```

The script invokes `render_off_duty_preview.cjs`, then FFmpeg, verifies the media and rebuilds the review hub and archive. Node canvas, the existing fonts, Pillow, FFmpeg and FFprobe are required. Rebuilding with retained assets makes no generation or narration requests. The archive includes preview assets and scripts; a clean checkout also needs the original month masters to rerun the builder.

No audience preference, engagement lift or production-time savings have been measured. These previews support creative review, not a go/no-go conclusion.
