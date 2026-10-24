# Blueprint month · production handoff

The owner selected Blueprint on 23 October 2026 and requested content production. The new BP01–BP16 cohort applies the “body of our dreams” direction to strength, movement, food, recovery and practical planning. Blueprint is a visual style; the public brand name remains open. The campaign wording is “Body of our dreams.”

## Content and schedule

The [canonical calendar](../content/month-one-v5/calendar.json) retains November 1–30, 2026, four core videos/week, four five-panel carousels and eight two-frame stories. Every core video has a source map, caption, response prompt, comprehension rubric and unscheduled alternative hook. The [readable schedule](../content/month-one-v5/CALENDAR.md), [scripts](../content/month-one-v5/SCRIPTS.md) and [supporting copy](../content/month-one-v5/SUPPORTING_POSTS.md) are generated from that source. Dates are planning slots; nothing is scheduled or published. Shift the entire plan if review delays launch.

Eleven reviewed B-series narrations are retained exactly. BP04, BP07, BP11, BP14 and BP15 introduce walking, a first run club, lunch planning, sleep timing and an activity tryout. Five new Fish requests use the approved voice. The new scripts retain their own source/age limits. BP11 uses an explicit caption break in its opening sentence to meet reading-rate limits while retaining the exact words, audio and bounded synchronization rules.

## Review package

Expected inventory: 16 narrated masters plus BP03 source-label-off and BP04 static-route controls = **18 distinct videos**, 20 carousel panels and 16 story frames. Controls are additional research stimuli, not additional scheduled posts.

Review location: `.local/month-one-v5-blueprint/review/index.html`.

Delivery location: `../fitness-deliverables/month-one-v5-blueprint/`, containing `Blueprint_Month_Review.zip`, `Blueprint_Month_Sources.zip` and a delivery receipt. Completion and hashes are recorded in `examples/month-one-v5/production-verification.json` after the package verifier succeeds; the expected inventory above is not itself a completion receipt.

## Verification and release limits

The verifier checks exact scripts and voice hashes, caption identity/rate, timeline/config/font identity, full video decoding, 1080 × 1920 at 30 fps, AAC stereo, loudness, every frame's text bounds and supporting-image inventory. Unit pixel tests isolate the citation difference to its label band and the motion difference to its route. Encoded audio and duration must match within each pair. Source archives exclude private credentials/profile values and retain font licenses.

Independent local speech recognition covers all tracks; new flagged tracks receive a second recognition pass. Reports distinguish recognition differences from confirmed synthesis mistakes. Full human listening, actual Instagram/YouTube overlay previews, audience checks and measured recurring hands-on labor remain pending. No platform result or human review is fabricated.

## Experiments and business decision

Use [month-one-v5.json](../experiments/month-one-v5.json) and [citation-visibility-v2.json](../experiments/citation-visibility-v2.json). CV1 remains historical and its original hashes are preserved. Blueprint's CV2 uses BP03 with the same rest-trial narration but a newly verified matched layout. BP04 supplies the independent motion comprehension comparison. A source can improve traceability without proving that viewers will trust the account more.

Keep 168-hour platform observations separate, record missingness and retain the original operating hurdles. Eight Q/A hooks remain balanced by week and weekday; the new content pillars are uneven, so the earlier pillar-balance claim no longer applies. Audience scope is inclusive, while scientific claims retain their studied populations.

The user prioritizes audience interest and a sustainable process at **12 hands-on hours/week**. This prebuilt package does not measure the recurring cost of the next month. Two representative four-video production batches and audience observations remain necessary. The current business decision remains **INSUFFICIENT EVIDENCE**.

## Measurement

Empty V5 observation, operations, response-coding, viewer-test and labor files live under `measurement/month-one-v5-*`. They contain no invented results. Run `.venv/bin/python tools/video/evaluate_month_one_v3.py --series v5` against these separate records; the shared evaluator retains the existing decision rules. The current output is `INSUFFICIENT_EVIDENCE`.

Rendered durations are 16.7–23.9 seconds. BP13's concise month-one progress checklist is below the 18-second planning target; it retains the original exact speech rather than adding empty time. The 18–30-second target is editorial guidance, not a claim that a duration causes success.

## Rebuild commands

With Node dependencies, Python Pillow, FFmpeg and retained narration available:

```sh
python3 tools/calendar/build_month_one_v5.py --check
.venv/bin/python tools/video/produce_month_one_v5.py render
.venv/bin/python tools/video/produce_month_one_v5.py render --ids BP03 --no-citation
.venv/bin/python tools/video/produce_month_one_v5.py render --ids BP04 --treatment static
node tools/video/render_supporting_v5.cjs
.venv/bin/python tools/video/package_month_one_v5.py
```

Retained V5 narration lives under `.local/month-one-v5-blueprint/voice`. The source archive includes those WAVs, alignments and sanitized receipts. The original V3 tracks are used only when initially retaining eleven exact scripts; restored V5 tracks must be usable without the historical audio directory. Rebuilding retained audio requires no new Fish request. New generation is a separate explicit `synthesize --generate` action.
