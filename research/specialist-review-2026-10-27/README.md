# Six-specialist review · fitness MVP

27 October 2026 · Blueprint V6 · baseline `1f189077` in `robdin/mvp-project-bomd`.

**Historical audit snapshot.** The owner subsequently authorized the four-step implementation. See [the pilot execution sheet](../../docs/MONTH_ONE_V6_PILOT.md) for current changes and remaining external checks. The reports and verification below describe the pre-fix baseline; their defect assertions are not current acceptance tests. New regression tests live under `tests/test_month_one_v6_*`.

**Connection follow-up:** The later [Metricool receipt](../../examples/month-one-v6/metricool-connection-verification.json) confirms Instagram, YouTube and TikTok connections. The historical connection blocker below is resolved; no posts were created. Native upload previews and exact-window analytics rehearsal remain separate.

**Implementation verification:** [implementation-verification.json](implementation-verification.json) records 101 passing Python tests, 23 passing Node tests, CRC-checked final archives, an isolated all-seventeen-input source restore without site packages or the legacy calendar, and a byte-identical BC05 rebuild from that archive. Final package checks cover nineteen videos and 13,136 frames; the refreshed review/pilot entry pages have 192 valid local references combined. The red team independently checked current media/input provenance and found three readiness edge cases, now fixed and regression-tested. Exactly one new narration request was made in this pass; sixteen current tracks were retained. No audience/labor observations were invented. Human listening, native upload previews, actual account verification and native metric-export rehearsal remain pending; no posts were created. The native Metricool page required sign-in, so it did not resolve the connector's no-network response.

**Recommendation: keep the current brand and month, make a focused preparation pass, and collect real viewer evidence.** The project has enough material for an initial viewer test. Public release and a dependable automated business decision still need a working account route, human playback checks and a few measurement fixes. A new month of creative production is not the next prerequisite.

Six separate agents reviewed content creation, monetization, engagement, digital marketing, experimentation and production. The root agent checked overlapping recommendations, challenged their scope, corrected one description of an already-existing scene, and reproduced key findings independently. These are evidence-informed audits, not six audience studies. No script, render, protocol, measurement input or public account was changed by this review.

## Read the specialist reports

| Review | Most useful finding | Practical next action |
| --- | --- | --- |
| [Content Creation](CONTENT_CREATION.md) | BC05's broad starting-weight question promises more than its instruction-request payoff. All seventeen example scenes use text cards. | Narrow that promise before its release; test one demonstration scene in BC08 or BC11 if viewers need it. |
| [Monetization](MONETIZATION.md) | The most plausible value is help applying fitness to an ordinary week, but no paid demand or recurring use has been observed. | Keep revenue out of the month-one gate. Optionally observe use of the existing Real Week Card before building a paid offer. |
| [Engagement](ENGAGEMENT.md) | Thirteen of sixteen captions repeat the same discussion question; useful message/log examples are often omitted. | Put the copyable tool in each relevant caption, remove the literal “Optional discussion:” label, and ask at most one specific question. |
| [Digital Marketing](DIGITAL_MARKETING.md) | A viewer's path from clip to profile to next useful help is still proposed. | Use a clear beginner/full-calendar descriptor and verified, progressively available destinations. Confirm the intended accounts. |
| [Experimentation](EXPERIMENTATION.md) | The V6 command is missing, duplicate production batches can satisfy the labor gate, and exact metric-window collection has not been rehearsed. | Repair and rehearse the decision workflow; prioritize one organic pilot, comprehension checks and measured production. |
| [Production](PRODUCTION.md) | Technical media checks are strong, but human delivery checks and restore/configuration safeguards have gaps. | Finish first-week phone review, repair the source-archive audio-check path, and bind future narration reuse to the intended voice/model/settings. |

## The outcome and the larger goal

The immediate job is to decide which changes would give this content idea a fair test. The larger goal is a repeatable workflow that answers: **does this particular account earn useful attention while four new videos and the supporting work fit within twelve hands-on hours per week?**

The ambition pass used the owner's supplied instructions and the available [ambition skill](../../../claude/skills/ambition/SKILL.md). The originally supplied home-directory path was absent; the matching skill was found in the shared `claude` repository. Its method was applied through raw-script/frame inspection, current platform sources, executable adversarial checks and a synthesis red team. The existing sixteen-post plan, twelve-hour cap and provisional decision hurdles were treated as constraints, not replaced by new performance promises.

The durable addition is this review index, six detailed reports and [a repeatable findings check](verify_findings.py). More automation, a public resource site, products or regenerated videos would be separate implementation work. None was created or authorized by these reports.

## What the outside checks actually established

The machine-readable result is [verification.json](verification.json). Reproduce from the repository root:

```sh
.venv/bin/python research/specialist-review-2026-10-27/verify_findings.py
```

The script reads current production and operations, runs synthetic evaluator cases only in memory, and writes only this review's verification file. It does not request narration, call publishing tools or add synthetic data to actual measurement files. A successful run means the recorded findings were reproduced, including defects; it is not a release-acceptance gate. Update or retire these snapshot assertions after the defects are repaired.

| Check | Result | Interpretation |
| --- | --- | --- |
| Canonical caption fields | 13/16 use the identical broad question; 16/16 include the editorial prefix | A concrete copy cleanup opportunity; no claimed comment/save uplift |
| Production configuration | 17/17 episodes contain an example card | A shared presentation choice, not proof that audiences dislike it |
| `evaluate_month_one_v3.py --series v6` | Exit 2: unsupported choice | Missing command routing; the callable evaluator does support V6 |
| Actual empty V6 observations | `INSUFFICIENT_EVIDENCE` | Correct; there is no business GO yet |
| Synthetic repeated, undated production batch | `GO_BOUNDED_MONTH_TWO` | The labor gate fails to enforce distinct real weeks/log evidence |
| Synthetic split attention performance | Separate medians pass while 0/12 posts pass both targets individually | Consistent with the written rule; add a paired diagnostic, rather than calling this a calculation bug |
| Retained Sources ZIP | Contains the audio checker but omits its eagerly loaded legacy episode file | Production reviewer reproduced the resulting restore-command failure; the retained media itself is not thereby corrupt |
| Metricool live read | Again reports no connected network for brand `7611975` | Unresolved integration state, despite the earlier user-reported connections; native account state was not inspected |

The earlier 68 Python and 23 Node tests passed before merge. The experimentation reviewer reran the six relevant evaluator tests successfully. Passing those tests did not catch the new adversarial cases. The production reviewer separately used temporary files and a blocked network stub to demonstrate stale model/voice reuse, and extracted the actual source archive to exercise its audio-check command. Details and limits are in the specialist reports.

The current [Metricool connection page](https://app.metricool.com/brands/connections?blogId=7611975) is the service's returned diagnostic destination. No account was disconnected or changed during these checks. A verified manual publishing route can substitute for scheduler automation.

Technical checks establish the facts above. **Only actual viewers and measured operator work can judge the content proposition.** No retention gain, character preference, sales demand or sustainable weekly hours were established.

## One prioritized work queue

These are recommended changes, not an implementation record. Do not add all six reports' time estimates or turn every suggestion into a launch prerequisite.

### Before the first public release

1. **Finish the real release check.** Listen to the intro and Week 1 on a phone, inspect native Shorts/Reels overlays and verify the intended account identity and upload route. Review later clips before their own releases. Automated speech differences are prompts to listen, not confirmed errors.
2. **Make public copy useful.** Put the existing gym/run-club message and log fields into captions; remove “Optional discussion:”; retain actual scope and sources. Clean up the two story prompts that assume progress or use internal category language. This can improve usability without redoing every narration.
3. **Give the account a truthful entry point.** Proposed descriptor: “Science-backed fitness for beginners with a full calendar.” Keep “Your dream body. Your real life.” as the emotional line and Blueprint as the design. Select a working public name/profile deliberately; a GitHub rename does not configure either platform. Link only to already available episodes.
4. **Prove the measurement route.** Rehearse collecting the required native metrics and preserve their actual reporting boundaries and timezone. Add V6 command routing, unique dated production batches and auditable labor reconciliation. Clarify what a fourteen-day extension can recover without pretending late views change a frozen first-week result.

A public starter kit is optional. Put the small tool directly in a caption when that is sufficient. Before promoting any external download, provide and check an actual mobile-accessible destination; do not send beginners to the local review hub or a source ZIP. YouTube states that external URLs in Shorts descriptions/comments are non-clickable, while channel profile links work. [Official YouTube link guidance](https://support.google.com/youtube/answer/13748639?hl=en).

The exact first-168-hour protocol deserves special care: YouTube's Analytics API uses Pacific calendar-day dates and can have data availability lag. Seven named dates are not automatically 168 hours after an 18:00 New York release. This is an integration risk, not a claim that every Studio report is unsuitable. If the exact window is unavailable, explicitly choose and freeze a feasible definition before collecting outcomes. [YouTube report reference](https://developers.google.com/youtube/analytics/reference/reports/query), [time dimensions](https://developers.google.com/youtube/analytics/dimensions).

### Before the affected operation

- **Before BC05's release:** narrow “What weight should you start with?” to “Not sure what weight to start with? Here's what to ask.” Keep the instructor/setup boundary; do not fill the promise gap with an invented universal load. A changed spoken line requires matching audio, captions and verification.
- **Before handing off a source-only restore:** fix the audio checker so selecting V6 does not first require the omitted V1 episode file, then rerun the isolated restore.
- **Before changing narrator/model/delivery:** ensure cached narration and build validation bind the complete intended synthesis configuration, using a non-secret identity fingerprint where needed. No new provider request is necessary to test the guard.
- **Before another operator uses historical plans:** label the DEX/one-video-per-week commercial documents and pre-V6 voice-status passages as historical. Keep the current Blueprint/four-video/twelve-hour contract easy to find.

### During the bounded pilot

- Run one organic cohort, a small unaided comprehension check and two measured representative production weeks. Keep BC00 separate, platform denominators separate, all posts in the exposure report and missing observations distinct from zero.
- Include people who do not yet have a routine. Ask what they expected, what they understood and what they could actually do next. Do not teach the desired answer before scoring it.
- Preserve the complete recurring workload in the twelve-hour total: research, writing, review, rework, supporting posts, uploads, community and measurement. Uploading this prebuilt month alone does not test ongoing creation.
- If viewers struggle with the cards, prototype **one** BC08 calendar expansion or BC11 ingredient-to-bowl scene. Keep audio, duration, captions and source scope fixed for a visual-only comparison. Use original and revised versions with fresh first exposure; a side-by-side preference alone cannot establish retention improvement.
- Treat follows, source/resource access and subsequent use as diagnostics with real field definitions. Observe the existing Real Week Card only if it fits the available research time. A click, a copy and actual later use are different outcomes.

### Defer

Do not run citation, motion and character screens concurrently just because the stimuli exist. Keep them ready for one specific later question. Defer a whole-month rebrand, new voice casting, a character-animation pipeline, a paid membership, a custom app, extra channels and paid reach. The reports' proposed prices and economics are hypothetical arithmetic, not evidence of willingness to pay or instructions to launch an offer.

## Red-team decisions and disagreements

**Agreement among agents is not an independent audience vote.** They reviewed the same materials and have related analytical biases. Treat “too many text cards” as a testable design concern. The technical examples and code defects are independently checkable; a predicted creative benefit is not.

**Protect existing good work.** BC05 already contains a specific instructor-request card. The content report's wording was corrected during synthesis so it does not recommend inventing an asset that already exists. The meaningful adjustment is the hook/presentation. Similarly, the starter kit already exists; public access and navigation are the gaps.

**Do not turn six recommendations into six projects.** Engagement, marketing and monetization all suggest some form of resource/navigation work. These can share one caption/profile route and one observation log. A public download and an email funnel are not prerequisites for a simple video test.

**Keep safety useful and precise.** A specific boundary may be essential; repeating disclaimers in every layer is not automatically better teaching. Reduce redundant labels and align the example to the spoken point while preserving limits that change the advice. Do not solve a weak payoff by overpromising a workout, diagnosis or transformation.

**Preserve experimental meaning.** Caption-only edits can avoid narration work, but they still change the treatment seen by a viewer. Freeze and version them before public observations. A necessary factual correction during the pilot is logged. Do not silently mix updated and old matched controls or attribute a multi-part creative change to one element.

**Reconcile timing and effort claims.** Content review computes speaking density over the full export; production review uses decoded narration duration. Those rates have different denominators, and neither supplies a universal ideal. Likewise, a two-hour edit estimate is not measured sustainable production. Use real playback and labor records.

**Keep the business decision proportionate.** A modest pilot can justify one more bounded month, identify a repair or reveal insufficient distribution. It cannot settle the entire fitness market. Revenue is not required for the present audience-interest/capacity objective, and adding revenue pressure would change the experiment.

## Decision after this review

Proceed with a focused implementation pass and initial viewer checks. Keep the selected Blueprint style and existing month. The November 1 start and December 5 final readout remain proposed, not scheduled; move them together if preparation delays launch.

This review does not grant publication, outreach, spending or account-setting authority. It does not commit its own reports, change the frozen protocol, or apply the suggested rewrites. It gives the next implementation pass concrete work and external checks, while leaving audience validation to the actual pilot.
