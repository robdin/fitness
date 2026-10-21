# Rep & Reason — month-one validation pilot

Prepared 21 October 2026. The user's goal is **audience interest and a sustainable production process**, with **up to 12 hands-on hours per week**. This is a bounded pilot, not a commitment to continuous production or a claim of market validation.

## What to review

- [30-day calendar](../content/month-one/CALENDAR.md): proposed November 1–30 dates, 16 videos, four carousels, eight story prompts, two review days.
- [Exact scripts and posting copy](../content/month-one/SCRIPTS.md).
- [Canonical episode data](../content/month-one/episodes.json): one source for narration, graphics, captions and packaging.
- [Supporting posts](../content/month-one/supporting-posts.json): 20 carousel panels and eight two-frame story sequences. Add native poll/quiz stickers when uploading; backgrounds alone are not interactive polls.
- [Source and claim limits](../research/month-one-sources.json).
- [Pilot protocol and decision hurdles](../experiments/month-one-v1.json).
- Local review hub: `.local/month-one/review/index.html`. Large media and private voice inputs stay outside Git. Open the HTML directly or serve that folder locally.

PR #3 was already merged when this work began. Main's verified merge commit is `dcba7ba079fb6b05ec1ebbb2e4cb9094b7a3f701`. This work branches from that baseline. The historical Blender MVP and V3 source files are preserved. The V3 MP4 and voice source ZIP were not found in the local folders searched, so this work does **not** claim a new full playback review of V3. Its existing renderer, retained timing, documentation and receipts informed the new implementation.

## Current delivery

All 16 core videos now have the existing approved studio voice. The review package also includes two additional M01 treatments, 20 carousel panels and 16 story frames. The three M01 treatments have identical encoded audio, script and timing. The review hub selects only exports whose retained checksum and script match. Human watch/listen review and a preview in each target uploader remain pending; nothing has been published.

The retained [verification receipt](../examples/month-one/verification.json) records actual durations, file hashes, caption rates and audio levels. Fish accepted 17 synthesis requests: one for each episode and one deliberate M07 clarity revision. The first streaming WAV header was finalized from its retained PCM without another request. A regression test covers the header boundary; no audio samples, pitch or speed are changed by header finalization. Model billing has not been reconciled to an invoice.

Independent local speech recognition checked all 16 tracks with `base.en`; `small.en` rechecked 12 tracks with ambiguous differences. Both initially struggled with M07's closing phrase “check who,” so the closing sentence was revised and its original recording retained. These are text comparisons, not a human listening audit. Minor article, inflection and number-format differences remain documented in `.local/month-one/audio-qa/` for listening review. No substantive quantitative claim is inferred from recognition alone.

Final caption timing uses pauses around adjacent speech where needed, with interior boundaries displaced by at most 450 ms from the adjacent spoken edges. Captions retain the entire script, do not overlap and stay at or below 20 characters per second. A failure to fit remains an error rather than triggering speech acceleration.

## Creative hypotheses and actual experiments

The first frame should pose a recognizable decision with an immediately readable visual. Larger graphics, short phrases, semantic reveals and contrasting quantities are proposed improvements; none is established as an audience winner.

M01 has three treatments of the **same script and timing**: A compact static diagram, B a larger static diagram, and C the larger diagram with explanatory motion. All three reuse the exact same WAV and caption timings. A/B changes the scale/layout package; B/C changes motion. A is a new control reconstruction, **not the historical V3**. Do not call A versus C an isolated size test.

The renderer uses twelve diagram families: countable time tiles, decisions, relative/absolute change, rest clocks, equipment routes, paired participants, time constraints, rescaled axes, log context, variable switches, study weeks and question checklists. Numerical labels are deterministic. The 15/25/8/12 allocation stays invented and sums to 60. Graph examples remain explicitly invented. The sample-size story depicts eight people, not sixteen independent participants.

Review the full videos at phone size, muted and with audio. Ask for an unaided takeaway before revealing a checklist. Use the protocol's 12–18-person usability screen to find problems; do not claim a statistically proven format winner from that small sample. No participants have been recruited or tested by this build.

The live calendar alternates question and answer hooks within its three pillars. Different topics, dates and viewers remain confounders. Publish one version per topic, record associations, and avoid near-duplicate organic uploads masquerading as randomized tests. Week-four content is a prebuilt follow-up reserve, not a response to results that do not yet exist.

## Source review and editorial status

M04/M12 use a narrowly stated 2016 rest-interval trial; M07 uses a 2025 eight-person within-subject study. The retrieved primary abstracts support the stated design and findings, with population and scope limits retained. A full-text risk-of-bias appraisal and qualified final editorial review are not claimed. Other episodes are original decision prompts or labeled arithmetic examples, not research-proven prescriptions.

Research badges, hypothetical sales and audience figures are never used as credibility shortcuts. No physiological outcome graphs or measured time savings are invented. The distinction between rest and avoidable delay remains explicit.

## Production and recovery

Requirements: Python 3.11+, Pillow, Node 24+, FFmpeg and the locked `@napi-rs/canvas` dependency. `numpy` is needed only by legacy V3 preparation; `faster-whisper` is optional for independent audio checks.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
npm ci
.venv/bin/python tools/video/build_month_one.py --stills
node tools/video/render_supporting_posts.cjs
.venv/bin/python tools/video/package_month_one.py
```

New narration requires the current `FISH_API_KEY` environment variable or ignored `.local/fish.env`, plus ignored `.local/fish-profile.json` with the existing studio voice ID and explicitly selected model. Do not put credentials or the private voice ID in Git. The browser showed `Ron Narration v2 studio` and `S2.1 Pro Free` available on October 21; availability can change. The endpoint does not return a complete billing receipt, so do not invent an actual cost record from a model name.

```bash
# Explicit network generation, only after current voice/model access is configured:
.venv/bin/python tools/video/synthesize_month_one.py --generate --ids M01

# Reuses retained voice; renders five-second pieces with bounded memory:
.venv/bin/python tools/video/build_month_one.py --ids M01
.venv/bin/python tools/video/build_month_one.py --ids M01 --treatment compact
.venv/bin/python tools/video/build_month_one.py --ids M01 --treatment large

# All remaining approved scripts, using the same configured voice:
.venv/bin/python tools/video/synthesize_month_one.py --generate
.venv/bin/python tools/video/build_month_one.py
.venv/bin/python tools/video/package_month_one.py
.venv/bin/python tools/video/verify_month_one.py
.venv/bin/python tools/video/archive_month_one.py
```

Synthesis is resumable and binds each receipt to the exact script. A started/unresolved request blocks automatic retries; reconcile its provider state first. Completed matching outputs are reused. No pitch shifting or speech time compression is applied. Changed scripts need new recordings and matching alignments. Explicit `--allow-silent` creates visibly labeled draft videos only; they are not narrated release masters.

Media validation checks full decode, expected frame count, actual output duration, script/alignment equality, two-line captions, reading speed, core-text bounds and audio level where present. Source/provider alignment is not independent recognition or a human listening audit. The tools do not attest creative or publication approval. Each final asset still needs the operator's complete watch/listen review and target-uploader preview.

Optional independent ASR uses locally cached models and FFmpeg-decoded PCM to avoid a PyAV API mismatch. Install `faster-whisper` separately and deliberately cache the selected model before running `tools/video/check_month_one_audio.py`. The check does not upload narration or automatically download models. Retained transcripts and the superseded M07 version are included in the source archive. API credentials and private profile configuration are excluded.

```bash
.venv/bin/python -m fitness_os check
.venv/bin/python -m unittest discover -s tests -v
npm test
git diff --check
```

The new JS checks work from canonical data and do not require ignored build outputs. Existing 22 control tests remain distinct from the new production/decision tests.

## Measurement and decision

YouTube is the primary attention readout. Keep Reels separate. YouTube defines engaged views, stayed-to-watch and average percentage viewed differently; do not calculate all three from public starts. [Official metric definitions](https://support.google.com/youtube/answer/12220281?hl=en).

Save snapshots at 24 hours for diagnosis and at seven days for the decision. Only the fixed 168-hour window is consumed by the decision script. Keep raw exports, traffic-source notes and metric definitions with the row's `source_export`. Never sum overlapping lifetime snapshots. Blank/unavailable metrics remain blank. APV can exceed 100% through repeat viewing, so the validator does not incorrectly cap it at 100.

The provisional hurdles are explicit operating choices, **not** industry norms or evidence of statistical power: 12 mature YouTube releases; eight with at least 100 engaged views; median stayed-to-watch of 60% and median APV of 70%; five distinct substantive useful responses; 80% comprehension pass among at least ten target viewers; two measured weeks within 12 operator hours each. Freeze any changes before the first public post.

A useful response describes a relevant problem, a concrete intended application, or an actual use of a resource. Exclude bot responses, generic praise, your own accounts and duplicates from the same person. Retain an anonymized coding rationale. Ten comprehension checks are a usability signal, not a representative effect estimate. A pass requires a correct main takeaway **and** no critical overgeneralization. Record recurring errors separately.

Track setup, research, scripting, review, rework, publishing, comment review and analytics separately. Treat this initial engineering build as setup cost and amortize it transparently; never call the unattended render duration the full cost of an episode. Record provider charges if any, including failed jobs, rather than assuming zero from a lack of invoices.

Copy the blank observation and operations templates into `.local/month-one/measurement/`, fill them from actual records, then run:

```bash
.venv/bin/python tools/video/month_one_metrics.py \
  .local/month-one/measurement/observations.csv \
  --operations .local/month-one/measurement/operations.json
```

- **Go for a bounded second month:** all gates pass and no recurring critical error remains.
- **Iterate once:** mixed evidence or a specific repairable problem. State the one change and the next fixed horizon.
- **No-go for the current format:** sufficient observations show both weak attention and weak usefulness, or labor remains over capacity after one documented simplification.
- **Insufficient evidence:** reach, mature observations, comprehension or labor records are missing. One bounded 14-day follow-up can resolve distribution or measurement; indefinite extensions are not validation.

November 30 is provisional because the last three posts are not seven days old. December 5 is the complete 16-video seven-day readout. No social publishing, recruiting, paid acquisition, purchasing or renewals have been performed.
