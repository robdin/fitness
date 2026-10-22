# November content — narrated review package

The creator/community-sourced N-series now has **16 narrated vertical videos, 20 carousel panels and 16 story frames**. One additional N01 static export provides a matched motion comparison. These are review assets, not accepted or published releases. The earlier M-series files are preserved separately.

Open `.local/month-one-v2/review/index.html` in this checkout, or extract `Rep_and_Reason_November_Content_Review.zip` and open its `index.html`. Delivery archives are in the sibling `fitness-deliverables/month-one-v2-media/` directory. The review ZIP includes posting copy, source links, subtitles, the planning calendar and verification receipts. The production-source ZIP includes retained narration and editable graphics code; it excludes the API key and private voice profile.

## What is ready

| Week | Videos | Supporting posts |
| --- | --- | --- |
| Nov 1–7 | N01: two gym days; N02: failure; N03: machines; N04: rep progression | K01: plan around your week; S01/S02 polls |
| Nov 8–14 | N05: RIR estimates; N06: busy-gym backup; N07: one bad session; N08: rest | K02: backup card; S03/S04 polls |
| Nov 15–21 | N09: lighter weights; N10: partial range; N11: supersets; N12: soreness | K03: study-reading checklist; S05/S06 polls |
| Nov 22–28 | N13: rankings versus programs; N14: full body/split; N15: more sets; N16: machine logs | K04: program checklist; S07/S08 polls |

The proposed schedule remains November 1–30 at 18:00 America/New_York. Videos fall on Sunday, Tuesday, Thursday and Saturday. The final full-cohort seven-day readout is December 5. The JSON calendar's `scripted_not_rendered_or_published` and supporting-copy status fields preserve the original authoring snapshot; use the [production receipt](../examples/month-one-v2/production-verification.json) for current artifact status. No status field grants editorial approval.

## Creative implementation

The cream/navy/lime design uses a relevant object immediately, large two-line headings, a single central diagram and complete spoken captions. Six semantic beats change the explanation; restrained entrance animation, a speech-timed rep reveal and word emphasis support the narration. Study conditions stay visible. No external creator imagery, footage or voice is used. Original diagrams require no new image-generation credits.

The approved deeper voice is preserved at its generated speed and pitch. Actual final durations are **26.27–32.67 seconds**. The earlier 30–40-second estimate assumed 150 words/minute; the retained voice speaks faster. Before any release or audience observation, the experiment's working target was revised to **25–35 seconds**. Scripts and hook assignments did not change. Record each actual duration in analysis; this is not evidence that shorter videos perform better.

N04's eight-to-nine example is an invented training log, not a muscle-growth measurement. N15's arrows are conceptual, not a fitted dose-response graph. N10's range marks are not an exercise tutorial. N06/N07/N13/N16 remain editorial planning checklists. Persistent scope labels and posting sources qualify the diagrams.

The story prompt has an empty region at x112/y1010, 762×205 pixels, reserved for a **real native poll**. Use the two options in its posting-copy file. Do not publish the empty prompt without adding the sticker; the follow-up text is educational copy, not a report of poll results. Carousels are 1080×1350; stories and videos are 1080×1920.

## Verification and remaining review

- All 17 MP4s have H.264 video at 30 fps and stereo AAC at 48 kHz; all decode completely. Each carries exact script, timeline, renderer and file hashes.
- All **13,747 motion-video frames** pass conservative text-bound checks. The captions preserve every scripted word, remain nonoverlapping and never exceed 20 characters/second. This is a mechanical check, not proof of comfortable reading.
- Supporting-image tests preserve the exact authored copy, check bounds, and keep text out of the native-poll region. Image dimensions and hashes are verified before packaging.
- Independent local `base.en` speech recognition checked all 16 voices. `small.en` checked the eight tracks with differences. No narration was uploaded for these checks. Exact differences remain in the verification receipt and source archive. These are fallible recognition comparisons, not a human listening sign-off.
- Listen especially to **N03 at 20.2s** (“settings and your technique”), **N04 at 24.6s** (“What does your log track”), **N07 at 10.8s** (“several changed”) and **N08 at 5.5–11s** (“produced” / “rests”). The two recognizers can agree on a reduced consonant or an error; do not assume either explanation. N09/N11 include word-spacing differences, and the N10/N12 second checks matched. N12's original “worked” flag is at 25.9s. Full watch/listen review of all videos remains required.
- N01's static and motion exports have identical encoded audio, script, composition, caption behavior and timing. Only interpolated animation differs. No winner has been established.

No target-uploader preview, participant recruitment, comprehension observation, live audience result or measured hands-on production week has occurred. No provider invoice was inspected; the configured model name is not proof of zero charges. Sixteen synthesis requests completed, with no automatic retries or revisions in this batch. Render elapsed seconds are recorded separately from hands-on labor; initial setup time remains unmeasured.

## Use the experiment without expanding the workload

Keep the [month-one protocol](MONTH_ONE_V2.md) and its 12-hour weekly ceiling. Review week one first, then use the five specified V2 clips for comprehension checks. Ask for the takeaway, next action and what the clip does not establish before showing the answer key. Repeated critical errors trigger repair even if viewers like the graphics.

The extra N01 static file is an optional motion screen: show one version first, balance first assignment, collect the unaided response, then allow preference comparison. Report raw counts and prior exposure. It does not replace the five-topic V2 comprehension gate, and side-by-side preference does not establish a retention effect. If review time is tight, omit this optional screen and use the clearer acceptable treatment. Do not schedule both exports as an alleged randomized organic test.

The organic month still compares eight question-led and eight answer-led openings, balanced by week, cluster and weekday. Use the same approved treatment throughout the first batch. Record actual exposure, duration and traffic sources; topic and platform distribution remain confounders. A go/no-go conclusion still requires real attention/usefulness observations and two measured production weeks, not the fact that these assets rendered successfully.

## Reproduce without buying another generation

```bash
# Uses retained voice/alignment inputs; no provider request.
.venv/bin/python tools/video/produce_month_one_v2.py render
.venv/bin/python tools/video/produce_month_one_v2.py render --ids N01 --treatment static
node tools/video/render_supporting_v2.cjs
.venv/bin/python tools/video/check_month_one_audio.py --series v2
.venv/bin/python tools/video/check_month_one_audio.py --series v2 --model small.en --ids N03 N04 N07 N08 N09 N10 N11 N12
.venv/bin/python tools/video/package_month_one_v2_media.py
```

ASR requires the locally cached models and optional faster-whisper dependencies. The command never silently downloads them. Synthesis is separate and requires an explicit `synthesize --generate`; matching completed inputs are reused, and unresolved provider submissions block retries. Keep `.local/fish.env` and `.local/fish-profile.json` private. Rebuild changed script/graphics/audio before packaging; stale hashes are rejected.

```bash
.venv/bin/python tools/calendar/build_month_one_v2.py --check
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m fitness_os check
npm test
git diff --check
```
