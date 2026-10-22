# CT1 field guide and response sheet

Status: prepared instructions; no collected participant responses. Use with the [protocol](08_CHARACTER_TEST_PROTOCOL.md). Custom questions below are product research items, not a validated psychological or clinical scale.

## Before a session

Verify eligibility (self-identified male, 18–35, at most six months consistent lifting), voluntary participation and the assigned arm/topic. Store only an anonymous participant ID and age band in the response sheet. Contact/payment mappings, if needed, stay private. Record consent separately and explain that this tests educational content, not the participant's body or fitness. They can skip questions or stop. Do not ask for photos, body measurements or medical history.

Use the frozen file and hash. Confirm a working phone player without showing other variants. Ask the viewer to watch as they normally would and stop when they choose. Avoid telling them “this one is more inspiring” or explaining the hypothesis. Do not force completion or praise their choice.

## First exposure and observation

Record assigned variant and topic, start, unique visible seconds played, duration, muted state, skip, technical failure and missingness reason. Calculate completion only from actual playback records. If no instrumented player exists, label observations moderator estimates and do not claim the protocol's primary metric was measured. Do not fabricate event logs.

## Ask before showing alternatives

1. “What was the main point?”
2. “What, if anything, would you do on your next visit?”
3. “What does this video not tell you?”

Use the canonical B04/B08 rubric from the calendar. Pass only when the main point and a compatible action are present and the viewer does not endorse the critical overgeneralization. Score verbatim responses blind to arm where possible. A second reviewer resolves uncertain cases. B04 must not become “24 uninterrupted reps” or a universal dose. B08 must not become “two visits meet every activity need” or an optimal-gains guarantee.

Then rate each item from 1 (strongly disagree) to 7 (strongly agree), with a separate “cannot tell” option:

- Trust: “I would trust this channel to explain another beginner question.”
- Task confidence: “I feel able to take the next step described here.”
- Inspiration: “This makes me want to work toward my fitness goals.”
- Discouragement: “This made starting feel more intimidating.”
- Clarity: “The explanation was easy to follow.”

M/R only, asked after those outcomes:

- Similarity: “The character felt like someone I could identify with.”
- Attainability: “The fitness level shown feels like a realistic aspiration for me.”
- Muscularity check: “The character looked muscular.”
- Friendliness check: “The character seemed approachable.”

Also ask: “Did anything about the character make the explanation less useful?” and “What channel name do you remember?” Do not infer that a drawing is medically or naturally attainable from a high rating. G's character-specific questions are not applicable, not zero.

Offer the same optional next explanation after these questions. Record actual start versus decline and identify this as post-survey behavior. Only then show the alternatives in rotated order and ask preference plus reason. Keep that answer separate from first-exposure outcomes.

## Minimal response record

Use one private row per person with: anonymous_id; age_band; beginner_eligible; allocation_block; arm; episode_id; stimulus_sha256; started; unique_visible_seconds; duration_seconds; completion_90pct; skipped; technical_failure; missing_reason; muted; takeaway_text; action_text; limitation_text; comprehension_pass; critical_error_code; trust_1_7; confidence_1_7; inspiration_1_7; intimidation_1_7; clarity_1_7; similarity_1_7_or_null; attainability_1_7_or_null; muscularity_1_7_or_null; friendliness_1_7_or_null; character_comment; brand_recall; optional_next_started; later_preference; rater_id.

Keep a separate allocation log, file manifest and labor log. Report aggregate results in Git; inspect free text for identifying details before sharing. No response file is prefilled with simulated participants.

## Result card

For each arm and topic report assigned / started / completed / skipped / failed playback / missing; completion and next-start counts; comprehension passes; each rating's distribution and missing count; recurring explanations for confusion or discouragement; actual hands-on minutes. Report M–R differences with uncertainty. Do not pool first exposure and later preference or treat multiple views from one person as independent participants.

End with one of: repair stimulus, retain graphics-only, advance M/R to confirmation, or insufficient evidence. A design preference can select a prototype; it cannot be reported as proven audience lift.
