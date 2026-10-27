# Conversational revision · source and decision notes

27 October 2026. This is an application of the existing research to new wording and concrete examples, not a new demand survey or an audience-validated format.

## Owner direction

Casual, relatable narration; mental models only where seamless; retain Blueprint. The sixteen topics, proposed November release dates and twelve-hour weekly cap are retained. BC00 is a separate introduction. Earlier visual-gallery selections do not override the explicit Blueprint choice.

All sixteen scripts were rewritten. Completed example cards replace abstract categories in selected beats. Their fictional times, settings, messages and meals illustrate a format without prescribing an exercise dose, load, personal diet or guaranteed outcome. Every topic still has a bounded action; questions move to optional caption discussion. Mental-model names are absent from narration.

## Evidence handling

The inherited registry is [blueprint-v5/sources.json](../blueprint-v5/sources.json). The new [source map](../../content/month-one-v6/SOURCE_MAP.md) binds references to BC episodes. Creator and community entries are retained as historical topic leads, not newly measured popularity or scientific support.

- BC02 keeps the equipment-review distinction between muscle growth and modality-specific strength. [2023 review](https://pubmed.ncbi.nlm.nih.gov/37582807/) re-opened; it reports no detected hypertrophy difference in direct comparison and modality-specific strength changes.
- BC03 retains a bounded summary of the small trained-men rest trial, without making three minutes a universal prescription. [Schoenfeld et al., 2016](https://pubmed.ncbi.nlm.nih.gov/26605807/) is retained from the prior verified registry; direct re-access returned a browser challenge during this revision. Secondary summaries were not substituted as evidence.
- BC06 retains the distinction between soreness and training effectiveness, and between soreness and concerning pain. [Military Health expert guidance](https://www.army.mil/article-amp/279545/military_health_expert_clarifies_no_pain_no_gain_workout_myths) re-opened. No diagnosis or new recovery dose is supplied.
- BC09 preserves food sources and the optional role of powder, without a personal intake target. [NIH ODS](https://ods.od.nih.gov/factsheets/ExerciseAndAthleticPerformance-HealthProfessional/) re-opened.
- BC12 keeps the qualified proximity-to-failure claim and uncertainty about a best stopping point. The [publisher's 2024 paper](https://link.springer.com/article/10.1007/s40279-024-02069-2) was accessible when PubMed returned a challenge. Its exploratory meta-regression does not supply a universal beginner target. [ACSM's 2026 summary](https://acsm.org/resistance-training-guidelines-update-2026/) was also re-opened.
- BC14 preserves regular timing guidance, real-life constraints and appropriate help for ongoing problems. [CDC sleep guidance](https://www.cdc.gov/sleep/about/index.html) re-opened.
- The walking and meal-planning sources were checked in the immediately preceding audit: [CDC activity](https://www.cdc.gov/physical-activity-basics/guidelines/adults.html) and [Food Standards Scotland](https://www.foodstandards.gov.scot/consumer-advice/healthy-eating/planning-and-shopping/meal-planning). Neither a short walk nor one meal is presented as a complete plan.

BC01, BC05 and BC08 are now labeled editorial workflows. A request for beginner help, an instructor question and whole-trip arithmetic should not borrow a scientific badge from a source about a different claim. The fictional log and basic rep/set definitions are explanatory examples, not evidence that a log proves growth.

## Voice implementation

Use the existing private speaker profile with the chosen conversational direction, on the configured Fish S2.1 model. The [official timestamped TTS API](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech-stream-with-timestamps) supports the prosody setting used here. Speech is generated with a 0.85 speed setting to allow caption reading time; the renderer does not locally alter pitch or tempo. Captions are checked against actual returned word timings, not inferred from a nominal speed multiplier.

## What the revision can establish

Technical checks can establish file integrity, readable text bounds, exact intended scripts, automated transcript differences and matched stimuli. They cannot establish relatability, retention or follow conversion. Keep the operating thresholds unchanged and collect the existing audience and hands-on labor measures. CV3 and the BC04 motion pair are prepared stimuli, not completed experiments.
