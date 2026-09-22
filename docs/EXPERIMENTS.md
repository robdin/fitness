# Experiment playbook

## Three different questions

| Question | Design | What can be inferred |
| --- | --- | --- |
| Does explanation sequence affect immediate understanding? | Randomized, one viewer to one of six topic/sequence cells | Exploratory within-topic comparison; instrument and recruitment limits remain |
| Which package works for a released video? | Native eligible YouTube title/thumbnail test | Native watch-time-based package result |
| Which topic attracts a useful audience? | Separate topic releases, common observation windows | Observational evidence; different audiences, dates and exposure confound it |

Do not upload near-identical body variants and call the resulting view counts a controlled experiment. Do not change topic, mascot, length, opening and offer together and attribute an outcome to one factor.

## Screening protocol

Files: experiments/format-screening-v1.json and comprehension-v1.json.

Three topics each have:
- A: hook → decision → example → evidence → limits → close.
- B: hook → evidence → decision → example → limits → close.

The practical decision plus example move as a block. This tests **sequence**, not a single changed sentence. The hook, caveat, closing, narration segments, cards and CTA remain the same within a topic. Final recorded duration should also match within each pair.

One independent eligible participant sees one cell. Stable salted assignment persists in SQLite; repeat IDs return the same assignment while enrollment is open. Do not use sequentially predictable labels to hand-pick preferred variants. Recruitment IDs must map to unique people outside the experiment database; the system cannot detect a person using two IDs.

Aim for 60 total assigned viewers, with an expected ten per cell. Unequal cell counts can occur under equal-probability assignment. This is instrument and concept screening, not a powered test of modest effects. Record who was invited, eligible, assigned, exposed and responded; assignment alone is not exposure.

## Before registration

1. Complete evidence review and accept per-beat narration.
2. Render and inspect all six narrated stimuli, with captions available.
3. Calibrate the instrument with 3–5 separate people; repair ambiguous items or ceiling effects before freezing it.
4. Finalize eligibility, recruitment, consent, retention/deletion period and follow-up arrangements.
5. Set the protocol status to ready_for_recruitment; record reviewer, substantive review note, actual start time and six relative build paths in activation.stimuli.
6. Register only the finalized protocol. Registration freezes its content, evidence, brand, instrument and stimulus manifest fingerprints.

The activation review is an operator attestation. It does not authenticate a separate reviewer or run recruitment for you. A draft registration can be examined locally, but if its inputs later change, use a new experiment ID.

~~~bash
python -m fitness_os init
python -m fitness_os experiment register format-screening-v1
python -m fitness_os experiment assign format-screening-v1 participant-001
~~~

The supplied draft intentionally refuses participant assignment until readiness is completed. No real participant has been registered.

## Administration and scoring

Ask for the unaided takeaway before multiple-choice questions. Do not reveal which sequence is expected to work better. Show the same questionnaire for both versions of a topic and score using the retained answer key.

Primary pass: at least 2/3 core questions correct **and** no critical overgeneralization. Secondary ratings are trust and usefulness on the same 1–5 scale. The critical item checks exaggerated generalization; it is not a clinical-safety assessment. Qualitative notes and exposure logs stay in controlled research records outside Git.

~~~bash
python -m fitness_os experiment respond format-screening-v1 participant-001 --correct 2 --critical-error 0 --trust 4 --useful 4
python -m fitness_os experiment analyze format-screening-v1
~~~

These commands are examples, not actual collected scores. The CLI records one response per assigned ID and refuses silent overwrites.

## Stopping and interpretation

Stop enrollment at 60 assigned eligible viewers or 14 days from recruitment, whichever occurs first. The operator monitors that limit. Allow 48 hours for outstanding responses, then close.

~~~bash
python -m fitness_os experiment stop-enrollment format-screening-v1
python -m fitness_os experiment close format-screening-v1
~~~

The first command blocks new assignments while allowing existing participants to respond. The second ends the response window. Neither command schedules itself. Do not stop early because a result looks favorable.

Inspect assignment ratios, missingness, exposure failures, question-level misunderstandings and recruitment composition before effects. The report gives per-cell counts, means and descriptive Wilson intervals, never an automatic winner. Missing responses are not converted to failures or successes. Consider how selective response could change the interpretation.

If one sequence generates a serious recurring misunderstanding, repair it as an editorial defect. Do not ignore the defect because an average trust score is high.

## Confirmatory follow-up

A new experiment needs a fixed primary outcome, minimum useful effect, horizon, exclusions, allocation and analysis plan. Under an illustrative 50% baseline, 15-percentage-point absolute improvement, 80% power and family alpha .05 across three topic comparisons, the local normal-approximation calculation yields **227 viewers per arm per topic**, or 1,362 total before attrition. The baseline and improvement are assumptions.

Do not treat the 60-person screen as satisfying that requirement. Use a statistician or an appropriate design review for consequential inference, particularly if recruiting clustered audiences or changing the instrument.

## YouTube packaging

Use the two title/thumbnail candidates for one chosen body version. Native tests may take up to two weeks and may be inconclusive. A combined title/thumbnail comparison identifies a package, not the independent contribution of its two elements. Short prototypes can later inform a longer release; they do not establish the best long-form duration.

Check feature eligibility in the actual account. Follow the native watch-time-based result and retain its dates, screenshot/export and package identities. Do not rebrand CTR as the test's decision metric. [YouTube guidance](https://support.google.com/youtube/answer/16391400?hl=en).
