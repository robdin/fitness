# Training Club month · V4 production handoff

The full November 2026 month now has a muscular, approachable fictional guide, clearer visual hierarchy and claim-specific evidence cues. The owner requested that the character/trust research be applied to production. M is a provisional creative choice; it is not a measured winner. V3's graphics-only exports remain preserved.

## Delivered

- 16 narrated 1080 × 1920, 30 fps masters, B01–B16, using the approved voice and unchanged scripts.
- 20 carousel panels and 16 story frames, with posting copy and native-poll instructions.
- Six CT1 clips: B04/B08 × muscular M, smaller-build R and graphics-only G. Two are also core masters; four are additional exports.
- Two B03 citation clips: label on/off. One is a core master; one is additional. Both retain full source links.
- 21 distinct video files in total; SRTs, covers, six scene stills per video, schedule, source records, exact stimulus hashes and production source archive.

Open `.local/month-one-v4/review/index.html`, or serve it on localhost. The user-facing archives are in `../fitness-deliverables/month-one-v4/`:

- `Rep_and_Reason_Training_Club_Month_Review.zip`
- `Rep_and_Reason_Training_Club_Month_Sources.zip`

The [verification receipt](../examples/month-one-v4/production-verification.json) binds the final media, renderer, fonts, tokens, character assets, configuration, scripts, narration and alignment. Full decodes, all-frame text bounds, caption identity/rate, dimensions, audio loudness and matched encoded audio are checked. Pixel tests establish that M/R/G differ only in the portrait slot and B03 differs only in the source-cue region. These tests do not establish perceived identity or audience preference.

## What changed and what was retained

The [brand application](../brand/v4/STYLE_GUIDE.md) specifies the guide and layout. [Production configuration](../content/month-one-v4/production.json) maps each short source cue to the existing evidence register. Editorial advice is marked editorial; a named study is not attached indiscriminately to every tip. Supporting-post packages include their linked episode references.

The November 1–30 schedule, four core videos per week, eight question/eight answer openings, script scope, community demand records and source links remain canonical in `content/month-one-v3`. This avoids paying for unchanged narration and preserves the existing factual review. All 16 voice files and provider alignments are reused; no new Fish request was made. Two image-generation calls produced the reusable M/R assets.

## Review limits and next decision

The six CT1 stimuli and two citation stimuli are produced; no pretest, recruitment, participant observations or public release has happened. The smaller guide still appears athletic, and the generative edit changes small clothing/contour details. Run the 6–9-person manipulation pretest before treating M/R as a clean physique comparison. If the intended difference is not perceived, revise the character or report a broader visual-package comparison.

Use the [CT1 field guide](../research/audience-v3/CHARACTER_TEST_FIELD_GUIDE.md) for the 36-person adult screen after the pretest. The comparison hub is for production review, not a participant first-exposure page. A validated instrumented player is needed to measure the unique visible-time primary metric; moderator estimates must be labeled as such. No data collector or participant database has been silently deployed.

The inherited ASR checks remain valid against the unchanged voice hashes. Listen to all final videos before release, especially B04/B05 number wording, B10 articles, B11 possessive, B13 word spacing and B16 missed-a wording. These are ASR flags, not established audio errors. Browser playback and sampled phone-size stills are technical visual checks, not full human listening or target-platform approval. Instagram/YouTube uploader previews remain pending.

For the business go/no-go, retain the [month protocol](../experiments/month-one-v3.json): platform-specific audience interest, comprehension and recurring hands-on labor capped at 12 hours weekly. Keep the launch visual version fixed within the comparison block, record any revision dates, and do not pool V3/V4 observations. Existing prebuilt exports do not demonstrate the cost of making the next month. The current business decision remains **INSUFFICIENT EVIDENCE** until real observations and two representative production batches are measured.

## Rebuild retained media

From the repository with Node dependencies, Python Pillow and FFmpeg installed:

```sh
.venv/bin/python tools/video/produce_month_one_v4.py render
.venv/bin/python tools/video/produce_month_one_v4.py render --ids B04 B08 --character R
.venv/bin/python tools/video/produce_month_one_v4.py render --ids B04 B08 --character G
.venv/bin/python tools/video/produce_month_one_v4.py render --ids B03 --no-citation
node tools/video/render_supporting_v4.cjs
.venv/bin/python tools/video/package_month_one_v4.py
```

The source archive retains narration WAVs, word alignments and sanitized generation receipts under `.local/month-one-v3/voice`. Restore those first. Rendering requires no provider call. Packaging reuses the local credential-value scan; the API key and private voice profile are excluded from archives and Git. Do not commit the review MP4s or private workspace.
