# Rep & Reason: narration pace and visual design

Research and application date: **21 October 2026**. Episode: the one-session time audit.

## Decision

Use the approved deeper voice at its natural speed, supported by precisely timed
JavaScript motion graphics and selected OpenArt footage. The resulting V3 is
**36.2 seconds**, with **103 script words**, **175.18 words per minute across the
35.279-second narration**, and **170.72 WPM across the complete edit**. Hyphenated
words count as one word. No pitch shift or voice time compression is applied.

The strongest defensible conclusion is not that Shorts has a secret optimal WPM.
It is that pace, comprehension, caption reading load and visual timing must work
together. **170–185 WPM is our editorial starting range for this familiar,
single-idea English explainer; it is not a scientifically established optimum.**

## What the speech-rate evidence actually says

| Evidence | Finding relevant to this project | Limits on applying it to Shorts/Reels |
|---|---|---|
| Guo, Kim & Rubin, 2014 [1] | Observational analysis of 6.9 million edX watching sessions associated faster delivery with greater engagement. | Four MOOCs, not randomized speech rates, not a short-video feed. Engagement is not proof of understanding. Instructor energy and content can confound the association. |
| Murphy et al., 2022, online 2021 [2] | Lecture experiments found relatively little comprehension cost at 1.5× and 2× playback in their tested conditions, with deterioration at higher speeds. | Playback compression differs from speaking naturally. This individual study does not establish that 2× is safe for every topic or viewer. |
| Tharumalingam et al., 2025 [3] | Meta-analysis of 24 studies and 110 effect sizes found that increasing lecture speed can impair test performance; costs were small and often nonsignificant at speeds no greater than 1.5×. | Lecture learning rather than feed retention. It does not translate a multiplier into a universal WPM target. |
| YouTube's content analytics guidance [4] | Shorts exposes engaged views, stayed-to-watch and watch-duration measures that can test our audience's response. | Official analytics documentation is not evidence for an ideal narration speed. No universal WPM recommendation was located in the official material reviewed. |

This was a targeted research review of primary studies, a recent meta-analysis,
platform documentation and official tool documentation, not an exhaustive
systematic review. No controlled study directly establishing an optimal WPM for
English fitness Shorts or Reels was found in the sources examined. Popular
creator claims such as “200 WPM is what the algorithm wants” should therefore
remain hypotheses, not production requirements.

### Practical pacing rules

1. Count the words and measure the actual delivered audio. A requested TTS speed
   or script estimate is not a measurement.
2. Preserve a conversational voice. Faster speech is useful only while the
   listener can follow the reasoning and the visual evidence.
3. Make a distinction between ordinary language and a new number, mechanism or
   qualification. The latter needs a matching visual and time to inspect it.
4. Trim unnecessary preambles and empty holds before accelerating speech.
5. For a future mechanism-heavy episode, begin slower than this episode and test
   understanding. Do not turn the present 175 WPM result into a channel-wide rule.

For this episode the selected voice naturally fits the working range. The
invented time buckets arrive at 7.64, 9.08, 10.44 and 11.56 seconds. Each receives a
corresponding visual reveal; previously revealed values stay visible for comparison.

## Captions: a different speed problem

Spoken WPM, subtitle characters per second and playback multipliers are different
measures. Captions compete with diagrams for visual attention, so a fast voice
cannot justify an unreadable caption.

Netflix's English guide allows up to 20 characters per second for adult content
and 42 characters per line; its general guide calls for no more than two lines
[5,6]. This is a professional timed-text reference, **not a YouTube/Instagram
algorithm rule**. Spaces and punctuation count in the reading-speed calculation.

V3 applies the following:

- All 17 original narration phrases are retained without paraphrasing.
- Maximum two lines, maximum 34 characters per line; selected breaks follow
  phrase boundaries instead of leaving an orphan word.
- Display intervals use Fish's returned word timestamps, with short leads and
  tails in available pauses. Maximum reading speed is 20.00 characters/second
  before millisecond rounding in SRT export.
- Cream text on a dark opaque panel; no one-word-at-a-time flashing.
- Caption panel is between y=1112 and y=1248 in the 1080×1920 frame. Important
  text stays approximately within x=70–920 and y=286–1248.

Meta's published ad guidance recommends leaving roughly the top 14%, bottom 35%
and sides 6% clear of key creative elements [7]. We use that as a conservative
layout proxy. Organic interface placement varies by device, caption length and
placement; this is not a guarantee that every possible UI overlay is identical.
The exported file should still be previewed in the intended upload interface.

## What makes a useful visualization

Noetel et al.'s overview of 29 reviews, encompassing 1,189 studies and 78,177
participants, supports multimedia design principles including signaling,
temporal/spatial contiguity, coherence and segmentation [8]. These findings concern
learning, not a promise of viral reach. Our application is a design inference:
show the relevant object when it is named, keep its label close, guide attention,
and avoid decorative motion that interferes with the explanation.

| Information in the episode | Chosen visual | Why it fits |
|---|---|---|
| An hour is a finite whole | Sixty markers form a clock ring, then rearrange into a 10×6 tile grid. | The same 60 units remain present as the representation changes. |
| The four invented time buckets | Exactly 15 lime, 25 cream, 8 blue and 12 coral tiles, with adjacent labels and values. | Part-to-whole allocation is countable and does not depend on generated text. Labels supplement color. |
| Repeated equipment trips | Two labeled stations and a moving marker along the connecting route. | Motion represents the described process instead of being unrelated decoration. |
| Rest is not automatically waste | Calm stopwatch footage and a short interpretive statement. | Keeps the caveat salient without prescribing a particular rest duration. |
| Log, change, compare | Three successive states: blank log, equipment regrouping, blank session comparison. | One action at a time; no invented improvement or time-saving result. |
| Next step | One-session audit call to action. | Gives the viewer a concrete experiment to try. |

The example is explicitly fictional in voice, captions and a persistent label
during the breakdown. The clip does not claim that the split is typical, measured
in a study, or representative of the viewer. We preserve the approved script;
this production review does not add physiological or training-effect claims.

## Tool selection for this subject matter

| Tool | Best role in Rep & Reason | Tradeoff | Decision for V3 |
|---|---|---|---|
| JavaScript Canvas / Skia [9] | Exact diagrams, labels, timed highlighting, counters and reusable visual states. | Requires code and explicit layout checks. | Used for all new diagrams and captions, rendered deterministically frame by frame. |
| Remotion [10] | A React-based episode system with reusable layouts, media and frame-driven animation. | Adds a larger composition/render stack; its current licensing should be checked before a commercial pipeline rollout. | Good future template/editor option; not required for this completed cut. |
| Motion Canvas [11] | Narrated vector explanations, authored transitions and synchronization through time events. | Specialized animation system rather than a general video editor. | Strong future option for mechanism-heavy educational sequences. |
| Blender EEVEE / Cycles [12] | Consistent 3D props, geometry, materials and camera motion; controlled spatial demonstrations. | More scene setup and render cost; anatomical accuracy still needs expert/source review. | Existing 51-second Blender MVP preserved. No Blender rerender required for this revision. |
| OpenArt video models | Cinematic object shots, atmosphere and visual transitions. | Generated geometry, clocks and writing can drift; beauty is not factual accuracy. | Reused the selected MiniMax and Seedance source shots. Generated audio is muted. |
| FFmpeg | Reproducible encoding, soundtrack mixing, normalization and verification. | Technical assembly rather than creative authoring. | Final H.264/AAC delivery and audio/video checks. |

For future fitness episodes, use code for a dose-response curve or a comparison
of study estimates, Blender for controlled spatial relations, and OpenArt for
contextual footage. A generated movement should not silently become an exercise
form demonstration or evidence of a biomechanical claim. For those tasks,
reviewed real demonstrations or controlled, verified animation are preferable.

### Using Arena and the OpenArt connection sensibly

The Arena page retrieved on 21 October displayed a **21 September 2026** snapshot,
718,577 votes and 48 models [13]. Its leading entries included:

| Rank displayed | Model/configuration | Displayed score |
|---|---|---|
| 1 | Gemini Omni 1.1 Flash | 1516 ±15 |
| 2 | Gemini Omni Flash | 1513 ±9 |
| 5 | Dreamina Seedance 2.0, 720p | 1479 ±8 |
| 6 | Wan 3.0 | 1476 ±13 |
| 7 | Dreamina Seedance 2.5, 720p | 1474 ±9 |
| 8 | MiniMax H3 | 1460 ±9 |

Ranks are a shortlist signal, not a proof of the best result for this storyboard.
Uncertainty overlaps, configurations differ, and aesthetic preference is not a
test of exact numeracy, anatomy or instruction accuracy. We do **not** claim the
selected MiniMax shot is from the overall number-one model.

The connected OpenArt catalog was checked during this work. It exposed MiniMax
H3, Seedance 2.5, Wan 3.0 and other options. Earlier project tests already produced
four source clips. The selected MiniMax opening and Seedance rest footage fit
the brand and are preserved with their OpenArt IDs and checksums. Reusing them
spends **zero additional OpenArt generation credits** for V3.

For the next episode, specify the shot first, shortlist two suitable models from
the available catalog, generate the same short shot, and compare prompt adherence,
object consistency, unwanted text, motion and editability. Check actual configured
credit cost before generation. Keep numbers, captions and scientific annotations
in the compositor rather than asking the generative model to draw them.

## How to validate the editorial choice after publication

This version has not been posted and has no audience-performance results. The
next test should change one major variable at a time; comparing V2 with V3 would
confound voice, pace, captions and graphics.

For a pace test, compare the same script, voice and visuals at a slightly slower
natural delivery against this baseline. Inspect Shorts stayed-to-watch, engaged
view duration, percentage viewed and the retention curve around the four values
[4]. For Reels, use the available watch-time, retention, save and share measures
in the account's current interface. Compare rates with their denominators, not
raw view counts alone. Small organic-post comparisons are noisy and not randomized
causal experiments. Also ask a few viewers to explain the takeaway; retention
alone cannot tell us whether they understood the distinction between rest and delay.

## Sources

1. Guo, P. J., Kim, J., & Rubin, R. (2014). *How Video Production Affects Student Engagement: An Empirical Study of MOOC Videos.* [Author-hosted paper](https://up.csail.mit.edu/other-pubs/las2014-pguo-engagement.pdf).
2. Murphy, D. H., et al. (2022; online 2021). *Learning in double time: The effect of lecture video speed on immediate and delayed comprehension.* DOI: 10.1002/acp.3899. [Author-hosted paper](https://castel.psych.ucla.edu/wp-content/uploads/sites/111/2021/11/ACP-Lecture-Speed-Murphy-2021-in-press.pdf).
3. Tharumalingam, T., Roberts, B. R., Fawcett, J. M., & Risko, E. F. (2025). *Increasing Video Lecture Playback Speed Can Impair Test Performance — a Meta-Analysis.* DOI: 10.1007/s10648-025-10003-9. [Author-hosted paper](https://bradyrtroberts.ca/uploads/Tharumalingam%20et%20al.,%202025.pdf).
4. YouTube Help. [Understand your YouTube content performance](https://support.google.com/youtube/answer/12220281?co=GENIE.Platform%3DAndroid&hl=en). Accessed 2026-10-21.
5. Netflix. [English (USA) Timed Text Style Guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide). Accessed 2026-10-21.
6. Netflix. [Timed Text Style Guide: General Requirements](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements). Accessed 2026-10-21.
7. Meta. [About text overlays and the safe zone](https://www.facebook.com/business/help/980593475366490) and [Instagram Reels ad specifications](https://www.facebook.com/business/ads-guide/update/image/instagram-reels). Official indexed guidance reviewed 2026-10-21; some full pages were login/throttle restricted.
8. Noetel, M., et al. (2022; online 2021). *Multimedia Design for Learning: An Overview of Reviews With Meta-Meta-Analysis.* DOI: 10.3102/00346543211052329. [Journal abstract](https://journals.sagepub.com/doi/10.3102/00346543211052329). Abstract reviewed; full article restricted.
9. @napi-rs/canvas. [Official project and README](https://github.com/Brooooooklyn/canvas). Installed package README reviewed 2026-10-21.
10. Remotion. [The core idea](https://www.remotion.dev/docs/idea). Accessed 2026-10-21.
11. Motion Canvas. [Introduction](https://motioncanvas.io/docs/). Accessed 2026-10-21.
12. Blender. [Rendering](https://www.blender.org/features/rendering/) and [EEVEE manual](https://docs.blender.org/manual/en/latest/render/eevee/index.html). Official indexed descriptions reviewed 2026-10-21; full fetch was unavailable.
13. Arena. [Text-to-video leaderboard](https://arena.ai/leaderboard/video/text-to-video). Retrieved 2026-10-21; page snapshot dated 2026-09-21.

Production measurements and source fingerprints are in
`examples/openart-social-v3/verification.json` and `build-receipt.json`.
