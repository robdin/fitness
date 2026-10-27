# Experimentation review — Blueprint V6

27 October 2026 · Baseline inspected: `1f189077` · Review only; no production, protocol or measurement inputs changed.

**Verdict: proceed toward a bounded audience pilot after a short measurement rehearsal. Do not call the project validated, or the automated go/no-go workflow ready, yet.** The protocol already makes several good decisions: YouTube is primary; Reels is separate; BC00 is excluded; low exposure is inconclusive; operating hurdles are explicitly provisional; and publishing prebuilt content cannot establish sustainable creation. The highest-value improvement is a reliable, simple decision process, not more creative variants.

The actual observations file is empty, the three V6 JSONL logs are empty, and operations are null/empty. Calling the shared evaluator directly on those V6 inputs returns `INSUFFICIENT_EVIDENCE`. All results called synthetic below were created in memory and were never written into measurement files.

## Priorities before the first public post

| Priority | Finding and evidence | Concrete improvement |
|---|---|---|
| P1 | **V6 has a CLI gap, not an absent evaluator.** `tools/video/evaluate_month_one_v3.py:22` accepts only `v3` and `v5`. `--series v6` exits 2. Its `evaluate()` function correctly accepts the V6 plan/content/records. | Add V6 to the supported CLI and a V6 smoke test when implementation is authorized. Until then, use the read-only Python command below. Do not substitute `--series v5` with BC observations: that loads the wrong plan and episode IDs. |
| P1 | **The exact reporting window is specified more precisely than the verified collection process.** `month_one_metrics.py:32–40` requires first 168 hours, maturity, a particular label and collection by hour 192. No current V6 collection rehearsal is recorded. | Demonstrate an export/screenshot for each required native metric that actually covers the prescribed window. Save publication time, report start/end, report timezone, data-through time and collection time separately. If the native UI cannot supply the exact window, amend and freeze a feasible, consistently defined window before launch; never relabel calendar-day data as exact elapsed hours. |
| P1 | **Labor validation trusts aggregate assertions.** `evaluate_month_one_v3.py:10–13` checks four videos, a nonempty log reference and hours, but no dates, distinct batches, episode IDs, log existence or weekly reconciliation. Two copies of one invented 12-hour batch pass the production gate in a synthetic check. | Require unique batch IDs, distinct representative weeks, actual draft IDs, labor-log references and completed scope. Reconcile all recurring hands-on work per calendar week, including publishing, community, measurement and supporting assets. Record unattended time and setup separately. A nonempty filename is not evidence. |
| P1 | **The extension rule and first-week metric need reconciliation.** The plan offers another 14-day observation/distribution window, but late exposure cannot change a frozen first-168-hour total. An otherwise valid first-week record collected on day 21 is rejected; a 504-hour record is ignored. | Define the extension as time to recover missing data, complete comprehension/labor checks or let genuinely delayed releases mature. Later reach is a separately labeled diagnostic. If the first-week exposure hurdle remains unmet, preserve `INSUFFICIENT_EVIDENCE`; any new distribution trial needs a new bounded cohort and explicit investment decision. |
| P2 | **The operational instructions are scattered across historical versions.** V6 has empty logs, but the detailed row guidance is in `research/audience-v3/06_INTEGRATION_AND_TESTING.md:64–70`; that same document mentions old B-series stimuli and topic-balanced hooks. | Create one short current V6 field sheet with current IDs, live URLs, exact metric mapping, response scoring, labor fields and the evaluator command. Keep prior research as context rather than operator instructions. |

YouTube's Analytics API uses date parameters and Pacific calendar-day boundaries, and responses can stop at the latest date for which all requested metrics are available. Thus an API query over seven named dates is not automatically seven elapsed days after an 18:00 New York publication. This establishes an integration risk, not proof that Studio lacks every suitable report. The current account/UI was not accessed in this review. [YouTube report query reference](https://developers.google.com/youtube/analytics/reference/reports/query), [YouTube time dimensions](https://developers.google.com/youtube/analytics/dimensions).

Studio supports report exports and date-range selection, but the official guide alone does not establish that all required fields are available together over an exact first-168-hour interval. An actual dry run is the outside check needed here. [YouTube Advanced mode](https://support.google.com/youtube/answer/9717005?hl=en).

## Keep one primary pilot; postpone the variant screens

The primary question should remain: **does this account's current package earn enough useful attention to justify one more month, while four new core videos and the promised operating work fit within 12 hands-on hours per week?** That is an operating feasibility pilot, not a causal A/B experiment.

Keep all sixteen scheduled core topics, the selected Blueprint identity, existing conversational voice, one master per topic and the fixed launch slot. Keep the intro separate. Preserve the frozen attention, usefulness, comprehension and capacity hurdles unless a documented prelaunch feasibility problem requires an explicit version change. Do not lower a hurdle after seeing outcomes.

Use three components:

1. **Main organic cohort:** first-week YouTube attention and exposure, substantive response coding, and a separate Reels report. Report all sixteen scheduled posts, their actual publication/maturity status and missingness. Twelve mature/eight sufficiently exposed posts is a minimum evidence gate, not permission to ignore the other four. Treat any pre-December 5 output as interim while the planned full cohort is still maturing.
2. **A small comprehension safeguard:** at least ten distinct eligible adult viewers, one designated first-exposure clip per person, unaided takeaway and action first. Sample across the most consequential topics and the brand's pillars; record coverage. Ten viewers cannot validate sixteen clips or all audience subgroups. BC00 can be shown afterward for orientation feedback, outside the primary clip score.
3. **Two real production weeks:** create or substantially rework two representative four-video batches, such as next-month drafts, without changing the frozen current-month masters. Log the whole recurring weekly workload. Historical setup time remains visible separately. If only uploading is timed, recurring production stays unknown.

**Defer citation CV3, motion/static and D-character comparisons.** Brand fit can be a brief orientation question, not a fourth comparative trial. Four concurrent screens introduce recruiting, allocation, scoring and multiple-result interpretation work before the core proposition has any live evidence. Their existing stimuli are useful retained assets; readiness of a variant is not a reason to run it immediately.

If audience checks uncover one clear issue, choose the relevant next experiment: motion only for diagram comprehension; citation visibility only for trust/source understanding; character only for identification/attention without comprehension harm. Run one with fresh viewers after the current cohort, preserve first exposure, and write the decision rule first. None of these small screens should promise feed-retention uplift.

## What the current metrics can and cannot decide

**Keep the denominator distinctions.** YouTube defines engaged views as staying past the initial seconds, excluding loops; stayed-to-watch measures initial continuation; average percentage viewed is calculated among people who stayed, using engaged views and their watch time. These are related but different stages. Public starts, unique people and engaged views are not interchangeable. Do not derive stayed-to-watch by dividing engaged views by public views without a verified platform mapping. [YouTube content performance definitions](https://support.google.com/youtube/answer/12220281?hl=en).

Reels remains secondary: retain native reach, views, watch-time fields available in the actual account, saves, shares and follows with their window and denominator. Do not pool them with YouTube or invent a Reels equivalent of stayed-to-watch. Save the native field label and import mapping; missing is not zero.

**Report low-exposure posts prominently.** Restricting attention summaries to posts with 100 engaged views selects a subset related to the outcome being studied. The minimum is a reasonable operating hurdle, not statistical power. The current plan correctly requests all-post exposure and missingness; ensure the final report actually includes them. Add a sixteen-row episode table, median/range of exposure, eligible count and traffic mix. Do not let strong attention among eight selected posts conceal that the remainder never found an audience.

**Add joint attention as a diagnostic.** The evaluator takes separate medians for stayed-to-watch and average percentage viewed. In a synthetic twelve-post example, six posts score 80/60 and six score 40/90; the medians are 60/75, so the attention gate passes even though no post clears both thresholds. This implements the written rule correctly; it is not a calculation bug. Report how many posts individually clear both thresholds and inspect the paired values. If the owner wants a joint-performance hurdle, define it before launch rather than inventing one at readout.

**Question versus answer is descriptive only.** Actual V6 allocation is balanced by week and weekday, but food is two answer-led posts and recovery is one question-led post; strength is four question/two answer. Topic, duration, cold-start effects, returning viewers and distribution remain competing explanations. Do not use a p-value or call an organic median difference causal. Use the result to select a later matched question, not crown a hook winner.

**Five useful responders measures problem resonance, not necessarily endorsement.** Existing categories sensibly include corrections and disagreement. Preserve those distinctions in the readout. Report intended action, reported action, specific question, correction/disagreement and praise separately; don't present five critical replies as five satisfied followers. Also distinguish volunteered organic responses from invited usability participants and acquaintances. Do not infer cross-platform identities. The primary deduplication scope must be explicit before results: one platform's unique account tokens is auditable; a pooled count of supposedly unique people generally is not.

**No power claim is justified.** Eight sufficiently exposed posts are eight content units, not 800 randomized independent participants. The citation screen's total 24–36 people is exploratory and has no specified detectable effect or power calculation. Its seven-point trust question is custom, not a validated scale. With ten independent comprehension observations, even an illustrative 8/10 pass result has a Wilson 95% interval of approximately 49.0%–94.3%. That calculation illustrates uncertainty; convenience recruitment and mixed clips add limits it does not solve. Retain the 80% threshold as a product hurdle, not evidence that the population comprehension rate exceeds 80%. [NIST proportion interval method](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm).

## A usable current field sheet

These are proposed fields and administration rules, not observations or new requirements already implemented.

| Record | Minimum practical fields |
|---|---|
| Publication and metric snapshot | `cohort`, `episode_id`, `platform`, native post ID/URL, master SHA-256, actual publication timestamp, report start/end/timezone, data-through time, collected-at time, window definition, native metric labels/values, export reference, missing reasons, traffic mix if available, any distribution intervention or edit |
| Viewer check | Anonymous participant token, adult beginner/returner eligibility and relevant time constraint, recruitment channel/prior relationship, first-exposure episode and hash, playback/skip/missing status, verbatim takeaway/action/limit responses, three component scores, critical-error category, overall pass, reviewer and adjudication note |
| Useful response | Platform-scoped anonymous responder token, episode, date, recruitment/organic origin, category, paraphrase, useful yes/no plus reason, positive/neutral/critical meaning, deduplication scope; keep private identity mappings outside Git |
| Labor event | Date, unique batch and draft IDs, task, active start/end or minutes, unattended minutes, setup/recurring classification, revision reason, receipt/log reference |
| Weekly labor summary | Week start/end, unique completed core drafts, promised supporting/publishing/community/measurement scope, hands-on total reconciled to event rows, omitted scope, waiting time separately, actual provider charges separately, simplification performed and before/after scope |

For comprehension, show the assigned clip once without the comparison hub or an explanation of the desired answer. Ask “What was the main point?” and “What would you do next?” before the limit question. Score meaning, not memorized phrasing: the main point is compatible with the episode; the action is feasible and compatible; no critical overgeneralization is endorsed. Record missing separately and report the number assigned, started, completed and scored. Require ten unique people for the primary ten checks; a person's second clip is useful diagnostic data, not another independent participant.

Use the BC-specific `comprehension` fields in `content/month-one-v6/calendar.json`. The old `experiments/comprehension-v1.json` uses P01–P03 multiple-choice questions and a different scoring rule; it is not a drop-in V6 instrument. Write acceptable paraphrases and examples of wrong actions for the selected BC clips before scoring. Have a second person inspect ambiguous passes and every critical flag, ideally without knowing variant assignment. Two people independently expressing the same material misunderstanding should trigger an editorial review and a documented repair decision; this is a proposed operating trigger, not a validated prevalence threshold.

During the month, capture optional 24-hour diagnostics without selecting winners, complete the primary fixed-window records, and hold a weekly short review for integrity, misunderstandings and labor. Do not optimize the frozen cohort continuously. A necessary factual correction is logged and changes the affected episode's comparability; evidence integrity takes priority over preserving a creative test.

The final decision table should show each gate, observed numerator/denominator or hours, missingness, failed conditions, and one bounded next action. Include all sixteen posts, the useful-response category mix, joint attention diagnostic and total recurring workload. Preserve a separate qualitative explanation when the machine output is incomplete; its aggregate checks do not audit the underlying records.

## Reproducible checks and manual workaround

The existing test file passes: `.venv/bin/python -m unittest discover -s tests -p 'test_month_one_v3.py'` ran **6 tests, OK**. Those tests cover existing decision branches and prevent upload-only hours from passing; they do not cover V6 CLI routing, duplicate batches or the export integration. All synthetic fixtures below are intentionally unrealistic, non-observed inputs for adversarial software checks.

Read-only current V6 evaluation from the repository root:

```sh
.venv/bin/python - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, 'tools/video')
from evaluate_month_one_v3 import evaluate
read = lambda path: json.loads(Path(path).read_text())
plan = read('experiments/month-one-v6.json')
print(json.dumps(evaluate(
    read('measurement/month-one-v6-observations.json'),
    read('measurement/month-one-v6-operations.json'),
    plan, read(plan['content'])), indent=2))
PY
```

Observed current output: `INSUFFICIENT_EVIDENCE`. This is the correct result for empty actual records. The workaround retains the production-batch guard; calling the lower-level `analyze()` alone bypasses that wrapper.

Minimal in-memory reproduction of the important edge cases:

```sh
.venv/bin/python - <<'PY'
import copy, json, sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, 'tools/video')
from evaluate_month_one_v3 import evaluate
p = json.loads(Path('experiments/month-one-v6.json').read_text())
c = json.loads(Path(p['content']).read_text())
rows = []
for e in c['episodes'][:12]:
    pub = datetime.fromisoformat(e['publish_at'])
    rows.append(dict(episode_id=e['id'], platform='youtube_shorts',
        published_at=pub.isoformat(),
        observed_at=(pub + timedelta(hours=168)).isoformat(),
        window_hours=168, reporting_window='first_168_hours',
        engaged_views=100, stayed_to_watch_pct=65,
        average_percentage_viewed=75, source_export='SYNTHETIC_ONLY'))
b = dict(batch_id='SAME_BATCH', week_start='2026-11-01',
    core_videos_created_or_substantially_reworked=4,
    source_labor_log='NONEXISTENT_SYNTHETIC_REF', hands_on_hours=12)
ops = dict(comprehension_checks=10, comprehension_passes=8,
    distinct_useful_responses=5, unresolved_recurring_critical_error=False,
    simplification_attempted=False,
    representative_production_batches=[b, copy.deepcopy(b)])
print('duplicate batch:', evaluate(rows, ops, p, c)['decision'])
split = copy.deepcopy(rows)
for i, r in enumerate(split):
    r['stayed_to_watch_pct'], r['average_percentage_viewed'] = (
        (80, 60) if i < 6 else (40, 90))
r = evaluate(split, ops, p, c)
print('disjoint attention:', r['decision'],
      r['median_stayed_to_watch_pct'], r['median_average_percentage_viewed'])
late = copy.deepcopy(rows)
for r in late:
    r['observed_at'] = (datetime.fromisoformat(r['published_at'])
        + timedelta(days=21)).isoformat()
try:
    evaluate(late, ops, p, c)
except ValueError as error:
    print('late first-week export:', error)
for r in late:
    r['window_hours'] = 504
    r['reporting_window'] = 'first_504_hours'
print('21-day replacement:', evaluate(late, ops, p, c)['decision'])
PY
```

Observed outputs: duplicate batch → `GO_BOUNDED_MONTH_TWO`; disjoint attention → `GO_BOUNDED_MONTH_TWO 60.0 75.0`; late first-week export → `Snapshot collected outside the allowed export grace period`; 21-day replacement → `INSUFFICIENT_EVIDENCE`.

## Red-team conclusion and limits

The plausible false positive is a good-looking subset of posts, five ambiguous responses and two asserted low-effort batches producing a GO while real recurring workload or viewer value remains weak. The plausible false negative is good content receiving little initial distribution, or a valid report being unavailable within the export grace period, leaving the pilot permanently inconclusive. The remedies are auditable records, a tested export process, paired diagnostics and an explicit bounded investment decision—not a larger pile of variants.

Applying the ambition skill means testing the decision machinery against raw configuration and adversarial cases, then using external platform definitions and the existing test suite as checks. Those checks confirm the CLI and logic behaviors above. They cannot judge audience value. The outside judge for that remains real target viewers, native platform observations and measured owner work.

This review did not inspect social accounts, recruit participants, run public tests, measure actual owner time, listen to every video or change the launch schedule. It recommends targeted measurement preparation and a lean launch, not an unsupported business GO or a rebuild of the entire content month.
