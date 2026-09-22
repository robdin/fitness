# Turuan framework review and migration map

The supplied REPO_GUIDE.md was reviewed across its fifteen sections. The actual turuan repository still requires authentication. This is a guide-level assessment, not a code audit. The new fitness code is independently implemented.

The guide reports 183 authored episodes, 20 published videos and four performance records. Those numbers do not establish a bottleneck or profitability.

## Preserve and incorporate

| Reference design | Why retain it | New implementation / next step |
| --- | --- | --- |
| Recording before expensive visual work | Avoids generating against speculative timing | Accepted per-beat audio sets final durations |
| One timing resolver | Prevents captions/scenes/chapters drifting | Inspect and wrap pace.py when accessible; do not duplicate its legacy math |
| Free checks before paid work | Avoids preventable spend | Structural check plus cumulative reservations |
| Small representative image sample | Detects bad prompts/models early | Provider benchmark designed; no paid batch executed |
| Derived spoken script | Avoids contradictory editable text | One pilot.json yields scripts and both sequences |
| Deterministic text/diagrams | Improves exactness and cost | Pillow/FFmpeg cards and thumbnails |
| Nonzero failure and aggregate gates | Allows dependable automation | CLI failure codes and integrity tests |
| Incident knowledge in tools | Reduces repeated errors | Decision log, bounded prompts and regression controls |

## Improve or review

| Finding in the guide | Change here | Verification / remaining gap |
| --- | --- | --- |
| “Nobody should watch the MP4” | Require complete recorded-media review | Human review remains pending |
| Native A/B winner described as CTR | Use native watch time; separate other diagnostics | Official platform source below |
| Fixed 8:05 / word-count production target | Duration serves the explanation | Current prototypes are shorter; no long-form winner claimed |
| File existence as cache validity | Inputs and artifact hashes | Tampering and stale-input tests |
| Auto-chaining can mutate during checks | Separate check, render, review and export | Read-only validation test |
| Raw audio moved or overwritten by edits | Retain copied source with checksum | Import never moves original |
| Shared provider limits per worker | One transactional account ledger | Concurrent reservation/unknown-slot tests |
| Missing metrics confused with performance | Explicit nulls, periods and sources | Mapped CSV importer |
| Safety-language lint treated as scientific QA | Claim scope plus actual source review | Claims remain pending |
| Brand doctrine tied to one format | Brand configuration and domain-specific claims | Separate-root extension; compatibility untested |
| Recording bottleneck inferred from inventory | Measure touch/wait/rework before optimizing | No three-run operating measurements yet |
| Consumer funnel and support absent | Resources, paid scope, events and economics | Actual account/customer operation pending |

[YouTube test guidance](https://support.google.com/youtube/answer/16391400?hl=en), [mid-roll guidance](https://support.google.com/youtube/answer/6175006?hl=en).

The old fixed quota arithmetic should become a dated capability check against the actual project and current official endpoint. Avoid replacing one hard-coded universal daily quota with another.

## Code review after access

Inspect actual command side effects, file locking, dependency invalidation, cache signatures, raw audio handling, provider retry semantics, upload receipts, credential scopes, timing-sidecar compatibility and frame verification. Confirm that the guide reflects the source.

Keep legacy episode IDs, intentionally non-contiguous image indices and published paths. Build fixtures from retained inputs and compare timing/output behavior before porting a module. Do not bulk regenerate the legacy catalog.

Candidate reuse order: timing normalization; layout components; deterministic renderer utilities; export verification; provider adapter boundaries; metrics imports. Brand doctrine, fixed duration, cadence and empirical “best practice” claims stay configurable.

A later migration is complete only when a retained Turuan sample behaves as expected and a fitness sample uses new policy without scattered hard-coded changes. No such compatibility result is claimed today.
