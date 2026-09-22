# Operating the local system

## Establish state

Run the structural check before building. init creates .local/state.sqlite3 and a random experiment assignment salt. Keep this store stable during a study; replacing it can change new assignments.

~~~bash
python -m fitness_os check
python -m fitness_os init
python -m fitness_os render --all --workers 2
python -m fitness_os gallery
~~~

Read-only checks are not evidence approvals. The gallery copies current verified builds into a portable review folder. It does not register an experiment or release a video.

## Narration and release

Import reviewed audio as described in PILOTS.md. Review claims in research/claims.json with an identified person and exact supporting evidence. The claim status is a local attestation, not automated scientific validation. A change in claims, brand, code or scripts invalidates old builds.

Set the intended channel ID before public-release approval. Complete all seven checks: evidence, script, visual, audio, captions, rights, packaging. Watch the complete recorded export, including transitions and the caveat.

~~~bash
python -m fitness_os approve .local/builds/CURRENT-BUNDLE --reviewer operator-name --checks evidence,script,visual,audio,captions,rights,packaging --note "Describe the actual review and any resolved issues here."
python -m fitness_os release .local/builds/CURRENT-BUNDLE
~~~

These are syntax examples, not approvals. Silent previews cannot pass this gate. release makes a local package and never uploads it. Preserve the review record and manually verify the account and selected title/thumbnail before any later upload.

## Provider ledger

No generation provider is connected. Budget commands record your explicit authorized cumulative limit in minor currency units; the convention in this project is USD cents. Do not mix currencies in one provider budget. There is no automatic monthly reset.

~~~bash
python -m fitness_os budget openart --ceiling-cents 500 --concurrency 1
python -m fitness_os reserve openart P01-scene1 path/to/request-input.json --estimated-cents 100
python -m fitness_os start-job RETURNED-JOB-ID
~~~

The example $5 ceiling is not a current spending authorization. start-job only marks the local ledger as attempted; it does not submit a request. A future adapter must preserve that lifecycle.

Use reconcile with unknown when a request may have been submitted but its state is unclear. Keep its funds and slot reserved. After checking the provider, terminal reconciliation requires actual-cents, including zero. Success also needs a request-id and result location. Do not infer free failure from a timeout.

A repeated reserve with the same input returns the old job. It never automatically retries a failed paid request. A deliberate additional attempt requires reconciliation, a revised request file with attempt context and another allowed reservation.

## Metrics and commerce

Map a real aggregate Studio export to measurement/youtube_observations.csv. Preserve blanks for unavailable metrics and the source observation window. Percentage inputs are 0–100, not fractions. Do not include participant or subscriber information.

~~~bash
python -m fitness_os metrics-import path/to/mapped-observations.csv
python -m fitness_os metrics-report
python -m fitness_os economics config/economics.example.json
~~~

Metrics reports expose raw observation rows. Snapshots overlap; the tool does not add them into an invented lifetime total.

commerce-import accepts the exact raw body and signature header from a recent webhook and reads the signing secret from an environment variable. It rejects stale signatures and deduplicates provider event IDs. It is a local verification/import command, not an HTTP server or durable event queue. For older events, use a future authenticated provider reconciliation path rather than disabling timestamp checks.

There is no entitlement, email or revenue-recognition engine. A checkout observation is not automatically a paid invoice, and checkout plus invoice must not be counted twice.

## Retention and recovery

Git retains source, policies and research. Independently back up .local/raw_audio, audio records, reviewed builds/releases, approved experiment records, metric imports and the SQLite database. Stop writers or use SQLite's backup facility when copying the database. Keep participant contact mappings separate, with a documented retention/deletion decision before recruitment.

Restore into a separate project root. Run check, verify retained artifact hashes and confirm database assignments/jobs. An unresolved provider job stays unresolved until compared with the provider. Do not upload or regenerate merely because a local database was restored.

Credentials belong in protected account configuration, never in content manifests, command-line arguments or Git. Approval records are trusted local operator attestations; this system is not a security boundary against a user who can edit its files.

## Failure ownership

Rendering or missing font: producer. Claim/source conflict: editor/reviewer. Unknown paid job: operator with provider access. Ambiguous audience response: research owner. Payment/access mismatch: commercial operator. Record the incident, affected IDs, fix and verification; update prompts only after the change is reviewed.
