# Blueprint month · conversational production

27 October 2026. Owner-requested revision: casual, relatable narration; mental models only when natural; **Blueprint remains the visual identity**. New BC identities and a separate workspace preserve every earlier BP master.

## Package

- Sixteen revised core episodes, BC01–BC16, on the same tentative November dates and four-video weekly cadence.
- BC00: one separate account introduction. Intended for profile orientation, excluded from the sixteen-topic cohort and operating thresholds.
- Seventeen new narrations using the existing speaker with conversational direction. Synthesis pacing is set to 0.85 through Fish's documented prosody control; no local pitch or tempo processing is used. Captions follow the returned word timing.
- Two private matched controls: BC03 source label off (CV3), and BC04 static route. Each uses its master audio and timing.
- Twenty carousel panels and sixteen story frames, with updated copy and native-poll instructions.
- A local starter kit and three refreshed D still-companion comparisons, kept separate from the graphics-led masters.

Review: `/Users/ronobdin/Github/fitness/.local/month-one-v6-conversational/review/index.html`.

Delivery: `/Users/ronobdin/Github/fitness-deliverables/month-one-v6-conversational/`.

D comparisons: `/Users/ronobdin/Github/fitness/.local/blueprint-character-d-v6-preview/index.html`.

Use [the canonical calendar](../content/month-one-v6/calendar.json), [scripts](../content/month-one-v6/SCRIPTS.md), [source map](../content/month-one-v6/SOURCE_MAP.md) and [current protocol](../experiments/month-one-v6.json). The schedule remains a proposal; this build does not schedule, upload, pin or publish.

The [pilot execution sheet](MONTH_ONE_V6_PILOT.md), [account entry copy](../content/month-one-v6/ACCOUNT_ENTRY.md) and [measurement field guide](../measurement/MONTH_ONE_V6_FIELD_GUIDE.md) implement the subsequent six-specialist review. All sixteen captions now include practical prompts; two polls are clearer; BC05's new hook matches its instructor-help lesson. One additional BC05 narration replaced a preserved successful take. Blueprint and the primary decision hurdles remain unchanged.

## What changed

Every core narration now uses ordinary speech, contractions and a specific next step. Optional discussion questions live in posting captions. Examples show a gym-help message, equipment note, meal list, full-trip appointment and return plan. The scene examples are invented and labeled; they are not testimonials or prescriptions.

BC01, BC05 and BC08 are explicitly editorial navigation/planning lessons. Their source cues no longer imply that youth guidance or adult activity targets validate a message template or calendar arithmetic. Existing bounded scientific claims elsewhere retain their source references and meaningful limitations. BC08 now teaches whole-trip time rather than a two-day training-dose claim.

There is no mandatory mental-model field or on-screen framework. Turuan remains optional background reading. Intro and supporting copy preserve the mission: personal aesthetic, health and capability goals alongside a full life. No public brand name has been selected by this revision.

## Verification and limits

The completed production receipt is `examples/month-one-v6/production-verification.json`, copied into the review hub. It records actual export hashes, full decoding, dimensions/codecs, caption reading rates, all-frame text bounds, loudness, speech-check differences and matched-pair checks. Missing receipts mean a build is incomplete; this document is not itself proof that a render finished.

Local speech recognition is a screen for missing or altered words, not a substitute for listening. Current differences are listed in [listening notes](../content/month-one-v6/LISTENING_REVIEW.md); five earlier takes were rewritten and regenerated after both recognizers flagged the same wording. Full human listening, native YouTube/Instagram overlay checks and target-audience tests remain pending until actually recorded. No engagement lift, character preference, recurring production hours or go/no-go outcome has been measured. The weekly hands-on ceiling remains twelve hours.

## Rebuild

From the repository, with retained narration and installed dependencies:

```sh
.venv/bin/python tools/calendar/build_month_one_v6.py --check
.venv/bin/python tools/video/produce_month_one_v6.py render
.venv/bin/python tools/video/produce_month_one_v6.py render --ids BC03 --no-citation
.venv/bin/python tools/video/produce_month_one_v6.py render --ids BC04 --treatment static
node tools/video/render_supporting_v6.cjs
.venv/bin/python tools/video/check_month_one_audio.py --series v6
.venv/bin/python tools/video/package_month_one_v6.py
.venv/bin/python tools/video/build_off_duty_preview_v6.py
.venv/bin/python tools/video/prepare_month_one_v6_pilot.py
.venv/bin/python tools/video/evaluate_month_one_v3.py --series v6
```

The D build additionally needs the retained atlas and generation record in `.local/blueprint-character-d-v6-preview/`; these are copies of the existing D assets, not newly generated images. It produces comparisons without replacing the month masters. The graphics-led package remains independently usable.

Speech generation is a separate explicit operation, using the local Fish configuration:

```sh
.venv/bin/python tools/video/produce_month_one_v6.py synthesize --generate --ids BC05
```

Completed receipts with the new complete input contract can be reused for synthesis. Historical receipts remain usable for rendering, with profile identity explicitly unknown; they cannot silently satisfy a changed or unproven synthesis profile. Render/build checks verify the expected model, direction and speed as well as script/audio/alignment hashes. Run `check_month_one_audio.py --series v6 --check-inputs` for a provider-free, ASR-free restore check.

An unresolved provider request must be reconciled before another attempt; do not delete a receipt and retry blindly. Keys and private profile IDs are excluded from delivery archives. Changed script or delivery settings require a new matching narration receipt and build. Preserve the historical V5/CV2 pair; CV3 is a fresh stimulus version with no participants. Local pilot review records persist separately from regenerated technical verification reports and are bound to the exact media hashes.
