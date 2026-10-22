# Training Club month · graphics-led production handoff

V4.1 removes the AI character from the full November 2026 production package. Headlines now use the full width, diagrams are about 18% larger than the former character layout, and carousels contain no portrait. Approved narration, evidence cues, factual boundaries and the calendar are retained. The character test is retired without participant results.

## Deliverables

- 16 narrated 1080 × 1920, 30 fps masters, B01–B16.
- Four five-panel carousels and eight two-frame stories: 36 images total.
- One additional B03 export without the short source label, for the separate citation test. Both versions retain source links and spoken qualifications.
- 17 distinct video files, captions, covers, scene stills, posting copy, source records, calendar and a reproducible source archive.

Open `.local/month-one-v4-graphics/review/index.html`. Current archives live in `../fitness-deliverables/month-one-v4-graphics/`:

- `Rep_and_Reason_Graphics_Month_Review.zip`
- `Rep_and_Reason_Graphics_Month_Sources.zip`

Earlier local exports are historical. The old character artwork, renderer options, posting-copy disclosure and character comparison players are absent from the active source and delivery package. Previous versions remain recoverable through Git/history.

## Verification

The [production receipt](../examples/month-one-v4/production-verification.json) binds media, renderer, fonts, tokens, configuration, scripts, narration and alignment. Checks cover full decoding, all-frame text bounds, caption identity/rate, format and loudness. Citation-control audio and timing match, with a pixel test limiting its visual difference to the source-cue band. The package checks the expected video inventory so stale character exports cannot slip into the current ZIP.

All 16 voice files and word alignments are reused. This revision makes no image-generation or Fish requests. Retained ASR reports remain valid against the unchanged audio hashes. Full listening, editorial release review and Instagram/YouTube uploader previews are still pending; ASR flags remain B04/B05 numbers, B10 articles, B11 possessive, B13 word spacing and B16 missed-a wording. These flags do not establish spoken errors.

## Schedule and testing

The canonical November 1–30 calendar remains `content/month-one-v3`: four core videos weekly, balanced question/answer openings, four carousels and eight stories. The final seven-day readout remains December 5. Shift the entire schedule if review delays launch; nothing has been scheduled on a social platform.

The [citation protocol](../experiments/citation-visibility-v1.json) is independent of the retired character experiment. It is an exploratory credibility/comprehension screen, not a powered claim of small trust effects. No participants have been recruited or tested. Exact B03 stimulus hashes are in [the manifest](../examples/month-one-v4/test-stimuli.json).

Keep the [month go/no-go protocol](../experiments/month-one-v3.json): platform-specific audience interest, comprehension and recurring hands-on work capped at 12 hours weekly. Record `v4.1-graphics` in observations and keep that layout stable within the launch block. Publishing these prebuilt files does not measure the cost of creating the next month. Audience results and two representative four-video production batches remain unmeasured, so the business decision is still **INSUFFICIENT EVIDENCE**.

## Rebuild

From the repository with Node dependencies, Python Pillow and FFmpeg installed:

```sh
.venv/bin/python tools/video/produce_month_one_v4.py render
.venv/bin/python tools/video/produce_month_one_v4.py render --ids B03 --no-citation
node tools/video/render_supporting_v4.cjs
.venv/bin/python tools/video/package_month_one_v4.py
```

Restore retained WAVs, alignments and sanitized receipts under `.local/month-one-v3/voice` first. Rendering needs no provider key or call. Packaging uses the local private-value scanner; credentials and the private voice profile are excluded from archives and Git. Large review media stays outside Git.
