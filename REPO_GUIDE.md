# Repository guide

Project Fitness is the first brand on a reusable content-business core. DEX is its fictional host, not a human professional. Start with README.md, docs/IMPLEMENTATION_STATUS.md and research/RESEARCH_ROUNDS.md.

## Sources of truth

- Authored text and sequence: content/pilots/<id>/pilot.json.
- Brand policy: config/brand.json.
- Evidence: research/sources.json, research/evidence/, research/claims.json.
- Experiment design: experiments/<id>.json and its instrument.
- Approved business decisions: docs/DECISIONS.md. Proposals and examples are not policy.
- Operational facts: .local/state.sqlite3, immutable import receipts and current build manifests.
- External payments and publications: their providers. Local draft status is not a remote receipt.

Use stable IDs. Keep research findings, working hypotheses, reviews and observed results distinguishable. Never create a research result, sale, approval or upload receipt by changing prose status.

## Commands and side effects

check, status, check-bundle, power, economics and metrics-report do not intentionally modify authored files. init creates the local database. render creates versioned build artifacts. audio copies and hashes a source recording; it does not move the original. Budget/job commands only record local ledger state. experiment commands manage local assignments and scores. metrics-import preserves an explicitly mapped aggregate export. commerce-import verifies a recent signed event then records minimal facts. release prepares a reviewed package and never uploads it.

Check command help and docs/OPERATIONS.md for syntax. No command automatically submits a paid generation request, emails a person or publishes publicly.

## Working on the code

Run the structural check, relevant control tests and git diff --check after changes. A code, evidence, brand, narration or audio change can invalidate a build. Rebuild before review. Keep paid provider uncertainty reserved until reconciled. A duplicate request with the same identity must not buy work twice.

Do not infer research quality from a schema pass. Do not infer viewer understanding from a silent prototype. Exact rendered media, captions and implied visual claims need review.

## Reuse

Use a separate project root and runtime store for another brand. Core commands may be shared; claims, audience, assets, reviewers and external accounts must be supplied for the new domain. See docs/TURUAN_REUSE.md before touching legacy IDs or timing behavior. The current code has no tested Turuan compatibility adapter.

Prompt files are reviewed instructions, not an active deployed agent team. Any future agent gets bounded inputs, output schema, tool permissions and a deterministic handoff.
