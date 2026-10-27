# Production specialist review · 27 October 2026

**Verdict: ready for a bounded viewer review; conditionally ready for the first publishing week after human audio/video and native-app checks. The recurring production process is not yet validated.** Preserve Blueprint and the current month. A further whole-month rebuild would spend effort before the main uncertainties have been observed.

This is an audit of the V6 artifacts and implementation at `main` commit `1f189077`, not a production change, listening approval, platform-preview approval or audience test. Effort estimates below are planning assumptions for one operator familiar with the project; they are not measured task durations or provider quotes.

## What is already strong

- The sixteen core videos and separate BC00 introduction have retained narration, word alignment, canonical scripts, source identifiers and technical receipts. The two additional controls share encoded audio and duration with their respective masters. D remains a separate preview, so an experiment does not silently change the production cohort.
- This review independently recalculated all nineteen review-export SHA-256 values and checked all seventeen current narration hashes and their stored delivery tag/speed against the production configuration. **No current mismatch was found.**
- The existing receipt reports nineteen complete decodes, 13,057 checked frames, caption rates at or below 20 characters/second, and durations of 20.2–26.1 seconds. Its explicit pending fields are accurate boundaries, not failures hidden by a passing test suite.
- Both delivered ZIPs passed an independent ZIP CRC read: 408 review-archive members and 235 source-archive members. This establishes archive integrity, not a complete restore or off-device backup.
- Synthesis is an explicit operation; matching retained audio is reused; uncertain requests block automatic resubmission. The graphics can be rebuilt from retained narration without another provider request.
- The nineteen exports' recorded rendering time totals approximately **100 seconds**. This is machine work from the retained receipts, not hands-on labor and not the total production time. Rendering speed is not the principal sustainability uncertainty.

## Ranked findings and smallest repairs

### 1. P1 · The release still has no recorded human listening or native-platform sign-off

**Evidence.** `examples/month-one-v6/production-verification.json` has `human_listening_review: false`, `target_uploader_preview: false` and no audience observations. `content/month-one-v6/LISTENING_REVIEW.md` lists current recognition differences for BC03, BC04, BC08, BC09 and BC16. All seventeen master exports total approximately **6 minutes 31 seconds** of playback. Five earlier takes were revised; the batch therefore contains 22 completed voice requests for seventeen current tracks.

**Why it matters.** Full decoding, ASR and text bounds cannot establish natural emphasis, awkward pauses, intelligibility on a phone speaker, whether a qualification is heard, or whether the platform covers a key element. The D receipt explicitly says its illustration below y=1510 may be partly covered by native overlays. No new external claim about today's platform UI is needed to recognize that this remains untested locally.

**Smallest repair before publication.** Review BC00 and Week 1 in full at normal playback speed, once with sound and once muted; inspect the five flagged phrases when their clips are reviewed. Log reviewer, UTC timestamp, exact MP4 hash, device, result and any correction. Preview the first upload on each intended platform, checking the actual feed crop, on-screen controls and caption behavior. Because captions are already burned into the MP4, explicitly check that a second automatic caption layer does not obscure or duplicate them. Review each later week's files before their release. Record sign-off outside the generated verification summary so a package rebuild does not erase it.

**Estimate:** 45–75 minutes for the full month's human pass plus notes; 30–45 minutes for first-platform previews, assuming access is working. Audio corrections are additional. These are preparation estimates, not implied permission to publish.

### 2. P2 · Caption speed passes, but the combined reading and listening load is untested

**Observed, not inferred from a generic rule.** I inspected BC00, BC05 and BC08 scene-2 PNGs and decoded BC05's final MP4 at 5 and 7 seconds. The example scenes simultaneously show a heading, three example rows, a footer, a scope label, a source/editorial cue, captions, phase labels and identity text. Their layout records contain 69, 77 and 66 visible words respectively; some are persistent identity text, so these counts are **not** a per-second reading demand. In BC05, the three-row example is visible during a roughly 6.08-second beat while the narration continues.

At a hypothetical 360-pixel-wide display, the renderer's 43-pixel caption type scales to roughly 14.3 pixels, the 35-pixel example copy to 11.7, and the 27-pixel source cue to 9. These are geometric projections, not measurements on a user's device or universal accessibility thresholds. `verify_v6_frames.cjs` checks bounds and caption size; it does not assess simultaneous attention, all pairwise text collisions, screen-reader access or whether a phone viewer reads the source cue.

**Measured delivery.** Counting regex word tokens in each canonical spoken script and dividing by the retained WAV's decoded duration gives approximately **164–203 words/minute**, including natural pauses within that WAV and excluding the extra video lead/tail. BC00 is about 203, BC05 about 199 and BC08 about 197. The provider's 0.85 setting therefore does not itself prove that the result sounds relaxed. No ideal words-per-minute standard or causal retention prediction is asserted here, and I did not listen to the audio.

**Smallest repair.** First test these exact dense examples with target adults, on a phone, at normal speed. If they miss the point or next step, try one minimal alternate of one clip: reveal only the row being discussed; retain the material scope qualification; keep essential captions; put the full three-line template in the associated carousel or starter resource. For the introduction, try fewer spoken words before changing the voice or the whole visual identity. Compare comprehension and perceived ease on first exposure. Do not regenerate all seventeen narrations based only on this audit.

**When/estimate:** prelaunch viewer check, then a single repair only if needed; 30–60 minutes to prepare a one-clip visual alternate, 30–60 minutes for a short listening/comprehension session, excluding recruitment. Not an extra simultaneous public-feed experiment.

### 3. P2 · Future voice revisions can pass incomplete input-provenance checks

There are two distinct issues, neither of which proves today's files are stale.

**A. Synthesis cache identity.** `tools/video/synthesize_month_one_v6.py:49–56` accepts a completed receipt when script hash, delivery tag, speed and file hashes match. It does not compare `model` and does not record a safe voice-profile fingerprint. A synthetic receipt for `old-model` was retained when `generate()` was called with a different model/profile and the same text/tag/speed. Network access was patched to raise if attempted; no request occurred. The public wrapper in `produce_month_one_v6.py` currently asserts the configured model is `s2.1-pro-free`, so arbitrary model drift is guarded there. Voice-profile changes are not guarded by that assertion.

**B. Render-stage voice contract.** `tools/video/build_month_one.py:24–29` verifies completion, script hash and retained audio/alignment hashes. It does not compare expected delivery settings to the generation receipt. `package_month_one_v6.py:37–39` also checks the script and artifact hashes, rather than the full voice contract. `produce_month_one_v6.py` incorporates a production-file digest into graphics metadata, but expected voice settings are not separately enforced at this boundary. In a scratch workspace, changing only the expected production identity in the episode still allowed retained BC00 speech through timeline creation. The renderer call was mocked to stop; no render or provider request occurred.

**Smallest repair before the next voice/configuration change.** Define one nonsecret synthesis-input identity covering spoken text, direction, speed, model and a stable private-profile fingerprint. Enforce it at synthesis reuse and before rendering; put the accepted voice/audio/alignment input hashes in the render receipt. Keep the current fail-closed behavior for unresolved requests. Add negative tests for changed speed/tag/model/profile and for replacing retained audio without rebuilding its video. Human release sign-off should bind to the final exported MP4 hash.

**Estimate:** 1.5–3 engineering hours including focused regression tests. This is a future-revision guard, not a reason to discard today's verified masters.

### 4. P2 · The delivered source subset has a reproducible clean-restore ASR failure

**Independent reproduction.** Extracting the actual `Conversational_Blueprint_Month_Sources.zip` to a temporary directory and running:

```sh
python tools/video/check_month_one_audio.py --series v6 --ids BC00
```

fails with `FileNotFoundError` for `fitness/content/month-one/episodes.json` before optional ASR dependencies are even imported. That legacy file is absent from the archive. `check_month_one_audio.py` eagerly executes `episodes=load_episodes()` before selecting V6; `month_one_core.py` hardcodes the legacy path for that loader. The documented V6 rebuild includes this check. Retained ASR reports in the source archive can support current verification, but do not make this command work in a clean subset restore.

**Smallest repair.** Select the series before loading its episodes, so V6 does not depend on an unrelated historical calendar. Document the distinction between rendering retained narration and rerunning optional ASR, including the deliberate local model-cache requirement. Add a source-subset smoke check that imports the V6 pipeline, selects BC00, checks required assets and runs its non-generative validation without relying on the original repository's omitted files. A separate one-clip restore render can establish media recovery when authorized; none was performed in this audit.

The source subset is clearly labeled as a subset, not a full repository backup. Git ignores `.local/`, and both inspected ZIPs are in a sibling local directory. An off-device copy and restore receipt were not supplied or independently verified; do not assume they exist or that they do not.

**When/estimate:** fix before handing the source subset to another operator; approximately 30–60 minutes for loader/docs and a narrow test, plus 30–60 minutes for a clean retained-media restore exercise and separately managed backup. Not a blocker to playing existing exports.

### 5. P2 · Four-video weekly sustainability remains an unmeasured hypothesis

**Evidence.** The V6 operations template has no weekly labor records. The calendar already allocates exactly twelve hours, including 1.5 hours of corrections and 1.25 hours of contingency. The experiment correctly requires two representative four-video production/revision batches and explicitly rejects prebuilt uploading as proof of recurring production capacity. The evidence gap is execution, not absence of a plan.

**Smallest repair.** Start the timer for actual research, source decisions, script review, TTS review, editorial corrections, supporting images, publication handling, community response and measurement. Keep initial engineering, unattended generation/render time and recurring operator time separate. Record rejected takes and rework against the episode that caused them. Measure two representative batches of four genuinely new or materially revised episodes; simply changing IDs or uploading the current ZIP is not a production batch.

Use the current format for those batches. Keep D variants and the two research controls out of routine four-post production unless a scheduled test specifically needs them. The highest-value simplification is reducing optional variants and supporting-post complexity, not removing source review or human listening. At the end of each week report accepted outputs, hands-on hours, unresolved work and actual known charges. If the cap is exceeded, apply one documented simplification and test it rather than quietly omitting work from the timer.

**Estimate:** 10–15 minutes/week for disciplined time logging and reconciliation, included in the measurement allocation. The actual production total is unknown until measured. Research at 1.5 hours for four topics is a planning allowance of 22.5 minutes/topic, not proof that a new clinical or controversial topic can be reviewed safely within that allowance.

### 6. P3 · Provider cost and recovery controls are useful but still manual and separate

**Evidence.** V6 writes a receipt before submitting and marks uncertain failures `unresolved`; it does not blindly retry. Current receipts record `credits_charged: null`, and the package reports `provider_actual_charge: null`. A model identifier containing `free` is not a billing receipt. The current month tooling is separate from the legacy `fitness_os` budget/provider ledger, as the framework handoff already acknowledges. The receipt-file existence check is not an exclusive process lock.

**Smallest repair during the pilot.** Keep a compact batch cost/recovery record with requested/accepted/rejected counts, provider evidence where actually available, actual charge or explicit unknown, and operator reconciliation. Specify a batch request/spend ceiling before new generation. Run one synthesis operator/process at a time. For an unresolved result, first reconcile or recover that result; record the decision and preserve the superseded attempt before authorizing a fresh identified attempt. Do not treat deletion of a receipt as reconciliation. Only add file locking or full ledger integration if parallel submission becomes a real workflow need.

**Estimate:** 15–30 minutes/week for cost/attempt review while volumes stay small. A full billing integration is later work and unnecessary for the first controlled content test.

### 7. P3 · Historical voice documentation can mislead an operator scanning below the current banner

**Evidence.** `brand/blueprint/VOICE_DIRECTION.md` correctly opens with “Applied to production” and points to V6. Later passages still say existing masters contain earlier audio, the revised scripts have not been rendered, and no complete month video was regenerated. The top paragraph explicitly calls the auditions historical, so this is not evidence that V6 is missing. It is a documentation-navigation risk. The review package also carries many prior-version references, increasing the reading burden.

**Smallest repair.** Put the old audition narrative beneath a clearly dated “Historical audition — before V6 approval” heading; use past tense there and link the current listening notes once. Make the one-page release route point to the canonical V6 calendar, current review hub, current listening notes, review sign-off and actual publication/measurement records. Preserve historical experiments and artifacts; do not ask a new operator to infer which “current” paragraph wins.

**When/estimate:** before handoff, 15–30 minutes. No media rebuild needed unless the delivery archive is refreshed to include updated documentation.

## Practical weekly workflow within the existing twelve-hour plan

These are the existing planned allowances grouped into an executable order; they remain assumptions until logged.

| Work block | Hands-on allowance | Exit condition |
| --- | ---: | --- |
| Research and source/claim decisions | 1.5 h | Four bounded, useful topics with source/scope decisions |
| Scripts, captions and spoken read-through | 1.0 h | Freeze one spoken script and next step per episode before synthesis |
| Visual preparation, voice and full-video review | 3.5 h | Accepted retained takes; readable videos; exact-hash human notes |
| One carousel and two two-frame stories | 1.0 h | Copy verified; native poll instructions ready where relevant |
| Cross-posting and actual uploader checks | 0.75 h | Actual publication records or explicit failures; no inferred success |
| Community response review | 0.75 h | Useful responses and recurring confusion recorded |
| Metrics, labor and cost record | 0.75 h | Correct-window exports and total hands-on time with missingness |
| Corrections and rework | 1.5 h | Fix documented problems; preserve old artifact identity |
| Contingency | 1.25 h | Buffer; do not schedule optional creative variants into it by default |
| **Total ceiling** | **12.0 h** | Two representative batches required to support sustainability |

Batch sources and scripts first, then generate only the approved text. Run unattended rendering and ASR while doing independent tasks, but do not count parallel owner work twice. Review the first accepted clip before committing the remaining three to a newly changed visual or voice treatment. Freeze each accepted export; link publication and observations to that hash/version. If a correction changes a tested stimulus, issue a new identified stimulus rather than pooling the old and new versions.

## Red-team check: how this assessment could be wrong

- Dense text may be welcomed as a saveable reference. The audit therefore recommends a first-exposure phone comprehension check, not a blanket simplification or unsupported retention claim.
- A roughly 200-WPM intro may still sound natural with this speaker. Word rate is a triage measurement; only actual listening and viewer response settle the delivery question.
- The cache/provenance holes are reachable code paths, but the current seventeen narration receipts match their configured delivery settings, and all nineteen export hashes matched. These are revision/recovery defects, not evidence of a mismatched launch batch.
- The source-ZIP ASR failure does not make existing videos unusable and does not imply the full repository has the same missing-file error. It exposes an incomplete subset restore path.
- A reusable template could make four videos/week comfortably sustainable, or source review and revisions could consume the entire budget. Neither machine render time nor the amount of work already completed answers that question.
- A previously arranged off-device backup or human review could exist outside the inspected artifacts. No corresponding evidence was provided; absence in these files is not proof of nonexistence everywhere.

## Scope and evidence limits

Reviewed the current calendar/production configuration, V6 production and voice-direction documentation, synthesis/build/render/package/frame-check tools, optional ASR entrypoint, operation/labor templates, actual archive inventories, V6 production receipt and D comparison receipt. Inspected actual current scene images and two decoded frames from BC05's final MP4. Independently checked current media hashes, archive CRCs, delivery metadata, script/audio timing measurements and the safe synthetic/clean-restore reproductions described above.

I did not listen to narration, open target-platform uploaders, verify social account connections, generate media, incur provider requests, inspect credentials, render the whole package, run a new audience test, verify provider prices, measure owner production labor, or validate an off-device restore. All nontrivial findings here arise from local artifacts/code or explicitly labeled production judgment; no current platform or provider-specification claim is inferred from memory.

**Recommended order:** finish the human and phone checks; make only observed clarity repairs; launch the stable first block when authorized; measure two real production batches; repair provenance and clean-subset recovery before the next configuration change or operator handoff. Keep the character expansion and additional production automation behind evidence of usefulness and available time.
