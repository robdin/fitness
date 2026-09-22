# Architecture

One project root contains authored policy and content; ignored local state contains operational records. Python is the controller. Pillow and FFmpeg assemble reviewed assets. No additional orchestration service is needed for the current workload.

~~~mermaid
flowchart TD
  S["Sources and evidence"] --> C["Claims and script"]
  B["Brand policy"] --> C
  C --> P["Preview build"]
  C --> A["Accepted narration"]
  A --> R["Recorded build"]
  B --> R
  R --> V["Exact package review"]
  V --> X["Local release export"]
  R --> E["Frozen screening stimuli"]
  E --> M["Assignments and observations"]
  M --> D["Reviewed decision"]
  D --> C
~~~

The diagram ends at a local export: there is no upload adapter. A separate commerce path currently ends at signed-event facts, not customer fulfillment.

## Modules

- catalog: load identities and validate references; collect render inputs.
- common: canonical fingerprints, atomic writes and path boundaries.
- render: card/thumbnail layout, audio durations, caption draft and FFmpeg assembly.
- pipeline: manifests, caching, retained audio, review and release export.
- store: transactional budgets, job state, assignments, responses and audit entries.
- experiments: frozen current protocol, readiness checks and descriptive reports.
- metrics: explicit Studio column mapping and preserved observations.
- commerce: raw-body signature check and deduplicated minimal provider facts.
- economics: transparent monthly planning arithmetic.
- cli: commands, explicit side effects and machine-readable errors.

## Extending providers

Add one adapter at a time. Its contract must return provider, exact model/settings, request ID, input fingerprint, status, output URI, downloaded file checksum, rights reference, estimated/actual currency cost and timings. No adapter may silently regenerate an uncertain request.

Reserve → mark attempted → submit once → store receipt → reconcile → retain output → validate → make available to a build. A timeout after submission is unknown until reconciled. Cancelled does not imply unbilled.

Benchmark a small fixed asset set across OpenArt and Higgsfield, including character consistency and a difficult scene. Keep precise scientific diagrams and typography deterministic. Neither provider has been connected here.

## Portability

Another brand can use the same package with --root pointing to its project files. It requires its own catalog, claims, source ledger, policies and runtime store. Current validation expects the W01–W20 research framework. This is a reusable project convention, not arbitrary schema-free multitenancy.

Keep compatibility adapters at the boundary when Turuan code becomes accessible. Do not rewrite its timing resolver or rename published IDs just to match the new folder tree.
