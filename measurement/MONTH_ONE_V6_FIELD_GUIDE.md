# V6 measurement field guide

27 October 2026. Current cohort: BC01–BC16. BC00 is an orientation asset, outside the core decision. This guide defines how to collect evidence; it contains no observations. The current empty files must continue to return `INSUFFICIENT_EVIDENCE`.

## Run the current decision report

From the repository root:

```sh
.venv/bin/python tools/video/evaluate_month_one_v3.py --series v6
```

Optional `--observations` and `--operations` paths select different actual input files. The V6 plan and calendar are still loaded from the V6 canonical paths. Never use `--series v5` with BC records.

V6 uses evidence schema `v6-evidence-v1`: the plan may explicitly set `evidence_schema` to that value; protocol version `6.x` also activates it. Historical V3/V5 behavior remains unchanged. Missing evidence yields `INSUFFICIENT_EVIDENCE`; malformed, contradictory or unverifiable supplied records fail with an error and must be corrected against the original source.

The frozen operating hurdles remain in `experiments/month-one-v6.json`. The report now adds `joint_attention_diagnostic` with eligible, complete and individually passing-both episode counts. That diagnostic does **not** change the separate-median attention rule or introduce a new success threshold.

## Snapshot collection and mapping

Before launch, rehearse the native report workflow. Record what the account actually offers; do not promise that a connector or date-range selector provides exact first-168-hour data. Preserve the native report or screenshot, including labels and filters.

| Input field | Record from the actual source |
|---|---|
| `episode_id`, `platform` | Current BC ID; `youtube_shorts` or `instagram_reels`. Keep a separate mapping to native post ID/URL and master hash. |
| `published_at` | Actual public release time with timezone, not the calendar's planned slot. |
| `observed_at` | When the report was collected, with timezone. This is not the report's end or data-through time. |
| `window_hours`, `reporting_window` | Current protocol expects `168` and `first_168_hours` only when that exact elapsed window is supported by the source. |
| `engaged_views` | YouTube's native engaged-view count. Do not substitute public views. |
| `stayed_to_watch_pct` | Native percentage in 0–100 units; do not derive from an unverified views ratio. |
| `average_percentage_viewed` | Native percentage, not a 0–1 fraction. It can exceed 100; do not clip it. |
| `views`, `reach`, watch time, saves, shares, subscribers | Preserve available native definitions and matching reporting windows. Missing fields stay null/blank, not zero. Reels is reported separately. |
| `source_export` | Stable local reference to the preserved report/screenshot. The evaluator requires a reference but does not independently authenticate platform exports. |

Retain accompanying metadata: `report_start_at`, `report_end_at`, `report_timezone`, `data_through_at`, original metric labels, mapping notes, missing reasons, collection method, and any distribution intervention or correction. The current evaluator does not validate these extra fields; human source review is still required. Do not mix multiple overlapping snapshots into the primary file.

YouTube API dates use Pacific calendar-day boundaries. Seven named calendar dates do not automatically equal 168 elapsed hours after an evening New York release; metric availability can also lag. If exact-window collection proves unavailable, document the evidence and revise/freeze a feasible window **before** the first post. Do not silently relabel it or patch data to satisfy validation. The evaluator currently preserves the protocol's 24-hour collection grace period; later collection requires an explicit protocol decision, even if the underlying report is historical. [YouTube date dimensions](https://developers.google.com/youtube/analytics/dimensions), [report availability](https://developers.google.com/youtube/analytics/reference/reports/query).

For reference, YouTube distinguishes initial continuation from average percentage viewed among viewers who stayed. Keep native denominators; a public play count is not a unique-person count. [YouTube metric definitions](https://support.google.com/youtube/answer/12220281?hl=en).

Preserve low-exposure posts in the file and the report. Extra observation time cannot retroactively improve a frozen first-week exposure count. Later exposure belongs in separately labeled diagnostics; a changed distribution test requires its own bounded cohort and decision.

## Representative recurring labor

Measure at least two distinct complete local weeks. A week starts Monday at 00:00 in `America/New_York` and ends the next Monday at 00:00. Each week needs at least four unique completed new or substantially revised core draft IDs. Do not count uploading prebuilt masters as creating them, or reuse the same four draft IDs to prove a second production week.

Include **all recurring scope** in each week: research, script work, claim review, visuals, audio review, corrections when needed, supporting posts, publishing, community work and measurement. A batch that omits the operating work is not evidence that the full weekly cadence fits 12 hours. Preparation weeks may remain incomplete evidence until the representative full scope has actually been measured; do not perform unnecessary tasks or invent minutes to pass a gate.

Keep setup/rebuild work and unattended machine time separately visible. Active timer intervals are hands-on work only: pause the timer during waiting or breaks. Start/end times may not overlap with another active event. `active_minutes` must match elapsed active time to within one second. Optional `unattended_minutes` are never added to hands-on hours; they describe separate machine waiting outside the active interval and may overlap other machine work.

Use the existing monthly JSONL file as a working log if useful. At week close, create an **immutable per-week JSONL snapshot** containing that week's recurring active rows only, with one JSON object per line. Verify it, then hash it. Do not point a batch receipt at a continuously growing month log: appending even a blank line changes its hash. Keep private person-level notes and identity mappings out of Git.

Required labor-row fields:

| Field | Meaning |
|---|---|
| `event_id` | Unique identifier across every supplied snapshot. |
| `batch_id` | The one batch represented by this immutable snapshot. |
| `classification` | `recurring`; setup rows belong elsewhere. |
| `task` | One of `research`, `script`, `claim_review`, `visuals`, `audio_review`, `corrections`, `supporting_posts`, `publishing`, `community`, `measurement`. |
| `started_at`, `ended_at` | ISO timestamps with timezone, within the batch's local week. Split a hands-on interval at a week boundary. |
| `active_minutes` | Finite nonnegative number, reconciled to the active interval. |
| `unattended_minutes` | Optional finite nonnegative separate waiting time; excluded from the capacity gate. |
| `draft_ids` | List of IDs worked on in that event; can be empty for account-level operations. Every counted completed draft must link to a production-task row. |

Each entry in operations' `representative_production_batches` needs:

| Field | Meaning |
|---|---|
| `batch_id` | Unique, stable week/batch identifier. |
| `week_start`, `timezone` | Monday `YYYY-MM-DD`, and exactly `America/New_York`. |
| `completed_drafts` | At least four objects, each with unique `draft_id`, `change_type` (`new` or `substantial_revision`), timezone-aware `completed_at` inside that week, and a short factual `completion_note`. The same ID cannot appear in another representative batch. |
| `core_videos_created_or_substantially_reworked` | Optional legacy count; if supplied, must exactly equal the completed-drafts list length. |
| `source_labor_log` | Repository-relative path to that immutable `.jsonl` snapshot. Absolute/outside-repository paths and escaping symlinks are rejected. |
| `source_labor_sha256` | Actual lowercase SHA-256 of the exact snapshot bytes. |
| `hands_on_hours` | Sum of snapshot active minutes divided by 60; rounding to two decimal places is accepted. Machine time is excluded. |
| `scope_review` | Object with each task above as a key and `{ "status": "logged" }` when actual positive active rows exist. Only `corrections` may use `{ "status": "not_needed", "reason": "factual explanation" }` if none was needed. Unmeasured required work remains missing evidence. |

Compute an existing snapshot's hash, replacing the placeholder path with its actual local path:

```sh
shasum -a 256 measurement/REPLACE_WITH_ACTUAL_WEEK_SNAPSHOT.jsonl
```

The CLI verifies file existence, SHA-256 and JSONL structure before evaluating. It rejects duplicate batch/event/draft IDs, repeated weeks, overlapping active intervals, out-of-week completion, unsupported completion types and mismatched hours. Only fully evidenced weeks enter the capacity gate; they are ordered by local week, and the existing rule considers the latest required weeks. A missing earlier record remains explicitly missing rather than disappearing from the report.

For programmatic analysis, `evaluate(..., labor_records=..., verified_labor_sources=...)` accepts explicit mappings by `source_labor_log`: parsed rows and verified hashes. Obtain them with `load_labor_evidence(batches, repository_root)` for actual files. Injected records are a caller trust boundary used by tests; supplying a hash string alone does not independently prove human work. The validator checks record integrity and reconciliation, not truthfulness or completion quality. Keep actual artifact/revision references in completion notes for human review.

## Viewer and useful-response records

Use the current BC-specific takeaway, action and critical-error definitions in `content/month-one-v6/calendar.json`. Old P-series multiple-choice tests are not the current instrument. Record distinct anonymous participant ID, eligibility, recruitment source/prior relationship, first-exposure episode/hash, playback/missingness, verbatim takeaway/action/limit answers, component scoring, overall pass and reviewer note. Takeaway/action questions precede prompting about limitations. Count ten distinct people for the primary ten checks; repeat views are diagnostics, not extra independent viewers.

For useful responses, retain platform-scoped anonymous responder token, episode/date, organic or invited origin, category, paraphrase, useful yes/no and reason. Separate questions, intended/applied actions, corrections/disagreement, generic praise and spam. Do not infer cross-platform identities or call all useful criticism endorsement. Preserve deduplication scope in the summary.

The evaluator still consumes manually reviewed aggregate comprehension/usefulness counts; it does not automatically audit the participant or response logs. Keep the source rows and review trail, and report missingness. Never fill nulls with zero merely to get a decision.

## Review cadence and final report

Optional 24-hour diagnostics are not the primary window. Review integrity, misunderstandings and hands-on time weekly. Keep the planned core cohort stable; log necessary factual corrections and their effect on comparability. Follow actual publication receipts for maturity, and move the full-cohort readout if launch dates move. The current calendar's proposed final readout is December 5, 2026, 18:00 New York.

At readout show each gate and its denominator, all sixteen scheduled posts, eligible counts/exposure range, paired attention values and joint diagnostic, useful-response category mix, comprehension coverage/missingness, and reconciled weekly workload. The machine output supports a bounded operating decision; it is not an audience-effect significance test or an independent audit of source truth.
