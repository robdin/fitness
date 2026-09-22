# Pilot review and recording guide

All three pilots are short sequence prototypes. They do not establish a preferred long-form length, character style or public cadence.

| Pilot | Viewer decision | Resource | Comparison |
| --- | --- | --- | --- |
| P01-time | Identify what makes a session run long | Session time audit | Practical decision/example before versus after evidence |
| P02-equipment | Clarify what an exercise substitute must preserve | Substitution questions | Same sequence comparison |
| P03-headlines | Connect a study to a relevant training decision | Study-to-decision card | Same sequence comparison |

Each topic has six canonical narration segments, two sequence variants, two title/thumbnail candidates and one questionnaire. Actual A and B text is derived from the same pilot.json; avoid editing separate exported scripts.

## Review the silent prototypes

Read the script alongside the visual cards. Check the useful action, exact claim scope, missing caveats, implied promises and legibility. The gallery presents A and B side by side. Review both completely; file validity alone does not establish communication quality.

The first topic is a time audit, not a promise to halve training time. The second does not validate every replacement exercise. The third demonstrates reading a comparison, not a universal research-scoring shortcut.

## Record once per beat

After the scientific/script review, record hook, decision, example, evidence, limits and close for each topic. Use the same voice, setup and delivery style. Leave a natural opening/closing pause without long silence. The exact same accepted segment is reused in both orders; avoid recording a more energetic A and calling the difference sequencing.

~~~bash
python -m fitness_os audio P01-time hook /absolute/path/hook.wav --reviewer operator-name
python -m fitness_os render P01-time --variant A --mode recorded
python -m fitness_os render P01-time --variant B --mode recorded
~~~

Import all six beats before recorded rendering. The importer retains a checksum-addressed copy and matching script fingerprint. Editing narration afterwards requires a reviewed current take.

Caption timestamps start as estimates within each beat. Copy the SRT outside the build, correct it while watching the recorded video, then run python -m fitness_os captions P01-time A /absolute/path/corrected.srt --reviewer operator-name and rebuild. Corrections bind to the exact narration, audio and sequence. Repeat for B; its order changes timestamps. Directly editing a retained build invalidates its artifact hash.

The renderer currently creates readable static cards, a DEX badge and caption drafts. It does not include the final animated mascot, detailed anatomy, music or a professional character rig. Those are separate creative tests after explanation quality is established.

## What a pilot result can change

It can reveal a confusing example, an omitted limitation, a weak resource connection or a promising sequence. It cannot by itself validate muscle growth, demand at a particular price, subscription retention or the economics of a channel. Record each proposed change in docs/DECISIONS.md with the observation that supports it.
