# Content business OS — product requirements

Version 0.1 · 20 September 2026. This document specifies the target and labels the implemented subset.

## Problem and users

A founder needs to turn an audience question into accurate, reviewable content and learn whether it supports a useful business. Repeated manual work is expensive, but automating an unsupported claim or untested offer increases the wrong output.

Primary user: founder/editor/operator. Supporting roles: evidence reviewer, narrator/producer and analyst. The viewer receives a clear explanation and practical resource; the internal tool architecture stays out of that experience.

## Goals and non-goals

Goals: traceable claims, repeatable production, controlled cost, defensible experiments, useful commercial records, and reuse across brands.

The current release targets one trusted operator and one brand per project root. It does not supply autonomous health advice, public publishing, automatic product access, a multi-user approval system, a CRM or a hosted production worker.

## Implemented journeys

1. Inspect source-backed research decisions and the remaining validation gaps.
2. Edit one canonical pilot script and two sequence orderings.
3. Build six silent prototypes concurrently, then compare cards, scripts, thumbnails and captions.
4. Import accepted per-beat recordings, retain originals and render narrated review copies.
5. Record evidence and complete-media review for an exact public release package.
6. Prepare randomized screening and score pseudonymous participants once stimuli and protocol are ready.
7. Record provider budgets/jobs without calling a paid provider.
8. Import mapped aggregate metrics or verify a recent signed billing event.
9. Calculate an explicit economics scenario without presenting it as observed revenue.

No live external service is deployed by these commands.

## Data ownership

| Entity | Canonical location | Identity / invariant |
| --- | --- | --- |
| Brand | config/brand.json | Stable brand ID and intended channel |
| Source | research/sources.json | Unique source ID, URL, access date, finding and limitation |
| Study | research/evidence/ | Verified record; access level and review limitations preserved |
| Claim | research/claims.json | Source links, scope, prohibited inference and review |
| Pilot | content/pilots/<id>/pilot.json | Stable ID; exact beat text; each variant uses every beat once |
| Audio | .local/raw_audio/ and audio/ | Retained source checksum and matching script fingerprint |
| Build | .local/builds/ | Inputs, environment, artifacts and checksums |
| Public approval | Build approval.json | Manifest hash, channel, seven checks, reviewer and note |
| Release | .local/releases/ | Retained exact reviewed package; no remote ID fabricated |
| Job / budget | SQLite | Unique provider/content/input identity; atomic reservation |
| Experiment | Protocol JSON plus SQLite | Frozen design; one participant, one assigned cell |
| Metrics | .local/metrics/ | Preserved mapped CSV and immutable observation receipt |
| Commerce | SQLite | Deduplicated provider event facts; not access or accounting balance |

Authored files, runtime facts and external-provider facts are different authorities. A script's status string is not proof of review, publication or audience exposure.

## Requirements and acceptance

| ID | Requirement | Current state | Acceptance / remaining work |
| --- | --- | --- | --- |
| F01 | Stable brand/content identity | Implemented | Unknown/mismatched identity fails structural check |
| F02 | Traceable material claims | Implemented structure; review pending | Every used claim resolves to sources; human approval still needed |
| F03 | Outcome-specific evidence review | Packet and workflow supplied | Complete appraisal and exact source locations before approval |
| F04 | Canonical script and sequence variants | Implemented | Same beats occur once per variant |
| F05 | Recording-first final production | Implemented import/render | Changed narration rejects old audio; original bytes preserved |
| F06 | Deterministic graphics and media assembly | Implemented | Current six builds succeed; inspect actual media |
| F07 | Final visual, audio and caption review | Manual review gate | Seven explicit checks for recorded public package |
| F08 | Versioned build/cache | Implemented | Changed input or output checksum invalidates current bundle |
| F09 | Paid-provider execution | Not implemented | Add authenticated adapter, receipts and reconciliation within budget |
| F10 | Budget and shared concurrency accounting | Implemented local ledger | Concurrent reservations cannot exceed ceiling; unknown jobs hold slots |
| F11 | Public release package | Implemented local export | Matching review, current channel, retained output integrity |
| F12 | Authenticated upload/schedule | Not implemented | Retain remote receipt; reconcile ambiguous uploads before retries |
| F13 | Randomized sequence screening | Implemented local assignments/scores | Reviewed narrated stimuli and frozen protocol before assignment |
| F14 | Native title/thumbnail experiment | Protocol supplied, manual Studio | Eligible channel/video; use native result and observation window |
| F15 | Aggregate metrics intake | Implemented mapped CSV | Missing metrics stay null; snapshots never blindly summed |
| F16 | Email signup and resource delivery | Copy and resource drafts only | Consent, domain and delivery/unsubscribe test in chosen provider |
| F17 | Payments / access | Signed-event import only | Hosted checkout, current-state reconciliation and entitlement lifecycle |
| F18 | Cohorts and renewal reporting | Definitions supplied | Real customer events and provider reconciliation required |
| F19 | Controlled learning and correction | Decision log and claim links | Extend dependency map to all published derivatives |
| F20 | Multi-brand operation | Separate-root design only | Test domain/credential/data isolation before shared hosting |

## Build contract and reproducibility

The build hash includes canonical pilot content, brand, referenced claims, source register, all core Python files, audio records, variant/mode and detected rendering environment. Source/file checksums guard cache reuse. This is deliberately conservative: even an unrelated core code change can invalidate all builds.

A cached artifact is reusable only when current inputs and retained file hashes match. A change after review needs another build/review. The manifest includes duration, artifact hashes and caption timing limitations.

Recorded mode takes durations from the accepted audio, then reorders the same segments between A and B. Caption timing within beats is estimated and requires review. No ASR alignment, advanced character animation or speech synthesis is implemented.

Byte-for-byte reproduction across arbitrary FFmpeg/font environments is not promised. Preserve the original build and its environment if exact bytes matter.

## Job lifecycle and money

Local states: reserved → running → succeeded / failed / cancelled; running can become unknown. Unknown retains the reservation and account slot. Terminal outcomes require a verified actual cost, including zero. Actual overruns remain recorded; the code does not hide them to maintain the nominal ceiling.

A repeated reserve call with the same provider/content/input identity returns the original job, including a terminal failure. There is no automatic resubmission. A deliberate revised attempt needs a new input with attempt context after reconciliation.

The ledger does not enforce activity performed outside it. Future adapters must use it before submitting requests and preserve provider idempotency keys where supported. Budgets are cumulative in the local store, not automatically renewed monthly.

## Experiments and analytics

The first screen is a six-cell, between-viewer design: three topics, two orderings each. One viewer sees one cell. Primary pass means at least two of three comprehension questions correct and no critical overgeneralization. The target of 60 is exploratory, not powered evidence for a winner.

Freeze claims, brand, content, instrument and exact stimulus manifests before recruitment. Editing frozen inputs blocks continued assignment/scoring through the CLI. Stop enrollment separately from closing the response window. Clock/count stopping rules are operator-enforced.

Reports preserve missing responses and supply descriptive Wilson intervals. They do not pick a winner or run repeated significance tests. Topic differences are not silently pooled into a sequence effect. The instrument itself still needs calibration.

YouTube body comparisons across separate uploads are observational. Native packaging tests, when available, randomize packages on one video and use watch time. These answer a different question.

## AI responsibilities

Research assistants return verified sources and uncertainty, not automatic approvals. Writers draft from an approved brief and claim scope. Reviewers point to concrete evidence or defects. Producers return exact artifact references. Analysts separate observed facts, assumptions and causal limitations.

Each prompt contract defines allowed inputs, output and handoff. No live multi-agent fleet, API loop or background scheduler is installed. Claude can use this repository context, but deterministic code and human review remain the authority for consequential transitions.

## Reliability, privacy and recovery

The SQLite store uses transactional writes and has no network-facing endpoint. Participant IDs are pseudonyms; recruitment contact information stays outside the repository. Billing imports retain minimal provider references and no email/body payload. These records may still be personal data and need appropriate access and retention.

The tool trusts the local operator. An operator with filesystem access can edit approvals or state; this is not authenticated RBAC or a tamper-proof audit log. Add identity, permissions and protected storage before multi-user or unattended use.

Back up runtime state and original media independently; Git alone omits them. Test a restore, verify media checksums and reconcile external-provider state before resuming. Dependency/source outages remain visible failures.

## Release completion criteria

The code release can be reviewed now if structural checks, integrity tests and the six prototypes pass. A public content release additionally needs reviewed evidence, accepted narration, caption correction, visual/rights review, chosen packaging and an intended channel. A commercial release additionally needs a delivered product and tested signup/payment/refund/cancellation paths.

The current deliverable is the working foundation and pilot review package. Live audience outcomes, billing fulfillment and repository-source compatibility are not complete.
