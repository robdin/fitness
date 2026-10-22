# Beginner month V3 · research and production handoff

The B-series replaces the proposed November editorial sequence with a beginner-first journey. The project owner selected **Training Club** on 22 October 2026. Training Lab and Coach’s Notebook remain comparison references. This selection is not audience validation.

## What is complete

Five research briefs cover psychology, short-form video, beginner discovery, brand strategy and writing. A 34-record research/guidance register, 34 community-question records and eight creator references record their access and scope limits. The 64-question bank contains original editorial prompts, not invented interviews. See [the research index](../research/audience-v3/README.md).

All 16 B-series scripts have narrated review exports. The package also contains two B01 brand alternatives, a B07 static-interpolation control, 20 carousel panels and 16 story frames. Exact posting copy, source links, caption files, a proposed November calendar and retained production inputs accompany them. Prior M/N-series and earlier MVP assets remain intact.

The current master exports are 1080 × 1920, 30 fps, H.264/AAC with 48 kHz stereo narration. Final durations are 16.7–23.9 seconds; B13 is intentionally shorter after readability repair. Answer beats begin by 3.43 seconds. The voice’s pitch and speed were not altered. These timings are measured production facts, not claims about algorithm preferences.

## Verification and remaining review

The exact [production receipt](../examples/month-one-v3/production-verification.json) records 19 successful full decodes and 12,138 frame checks for text bounds. Caption text matches the scripts, stays within the synchronization limits and reaches no more than 20 characters per second. Brand text pairs pass the 4.5:1 house contrast benchmark. Comparison exports have identical encoded audio. The checks also bind script, timeline, renderer, tokens, font, narration and alignment identities so stale revisions cannot be silently packaged.

Local ASR checked all 16 final tracks; a second model checked nine flagged tracks. B01, B08 and B12 were reworded after ambiguous phrases appeared in both passes. B13 was shortened after caption timing failed. Twenty completed Fish requests are retained: sixteen current tracks plus four earlier revisions. No unresolved request was retried, and no new image-generation request was made. Actual provider charges remain unknown; the model name is not a billing receipt.

Remaining ASR differences in the latest applicable pass are B04/B05 number spelling, B10 “the/a,” B11 a possessive, B13 “setup/set up,” and B16 “missed a/miss the.” These are listening flags, not proof of spoken errors. The package is complete for review; full human listening, final editorial approval and target uploader inspection are still pending. No audience tests, public releases or measured owner production hours have been recorded.

The current operating decision is **INSUFFICIENT EVIDENCE**, as it should be before launch. The evaluator cannot count low publishing time for a prebuilt archive as proof that four new videos per week are sustainable.

## Where the media is retained

Local review hub: `.local/month-one-v3/review/index.html`.

Sibling deliverables directory: `../fitness-deliverables/month-one-v3/`:

- `Rep_and_Reason_Beginner_Month_Review.zip`: portable hub, media, research, source-linked copy and schedule.
- `Rep_and_Reason_Beginner_Month_Sources.zip`: authored source, retained current/revision narration, alignments, sanitized receipts, QA and rendering inputs. Restore into a matching repository checkout; this is not a complete Git snapshot.
- `delivery-receipt.json`: archive identities and integrity checks.

Large media stays outside Git. Do not upload private environment/profile files or regenerate already completed narration. Package manifests are checked against every archived file; actual local key/profile values are scanned without displaying them.

## Reproduce and inspect

Use the repository’s pinned npm dependencies, Python environment and installed FFmpeg/ffprobe. Retained narration allows rendering without a provider request.

```sh
python tools/calendar/build_month_one_v3.py --check
python tools/video/produce_month_one_v3.py render
python tools/video/produce_month_one_v3.py render --ids B01 --brand lab
python tools/video/produce_month_one_v3.py render --ids B01 --brand notebook
python tools/video/produce_month_one_v3.py render --ids B07 --treatment static
node tools/video/render_supporting_v3.cjs
node tools/video/render_brand_v3.cjs
python tools/video/check_month_one_audio.py --series v3
python tools/video/package_month_one_v3.py
```

ASR needs the already cached local models and faster-whisper; it does not download or upload audio. A second pass on a revised track must match its current audio hash. Rendering alternative brands reuses the same approved voice; it does not call Fish. Synthesis requires the explicit `synthesize --generate` action and local credentials, and refuses existing receipts that need reconciliation.

## Launch and go/no-go

The follow-up [character and citation research](../research/audience-v3/07_TRUST_AND_CHARACTER.md) adds a [controlled test protocol](../research/audience-v3/08_CHARACTER_TEST_PROTOCOL.md). The owner subsequently requested production: [V4](MONTH_ONE_V4.md) now contains the graphics-led month and a citation test after the owner removed the character. These retained V3 exports remain graphics-only; audience validation remains pending. The review hub includes the new research and field guide. Its seven studies and correction are recorded separately from the original source register.

The proposed schedule is November 1–30, with the last core post on November 28 and a final seven-day readout December 5. Nothing is scheduled or published. Shift all dates if review delays launch. Keep actual platform exports and publication timestamps separate from the proposal.

The [experiment protocol](../experiments/month-one-v3.json) balances eight question and eight answer openings across week, topic and weekday. This is descriptive organic comparison, not randomized causal A/B evidence. Optional brand and motion usability screens use identical content/audio and first-exposure assignment. The [integration report](../research/audience-v3/06_INTEGRATION_AND_TESTING.md) explains rubrics, thresholds, failure conditions and the two representative production batches needed to evaluate the user’s 12-hour weekly limit.

```sh
python tools/video/evaluate_month_one_v3.py
```

The default JSON observations and operations files are intentionally empty/unknown. Supply real, sourced first-168-hour snapshots and real labor records. Synthetic examples exist only inside unit tests. An operator’s creative approval, technical QA and real audience validation are three different observations.
