# Rep & Reason — complete Codex handoff

> **Latest owner brand clarification, 23 October 2026:** the brand must be science backed, apply 80/20 prioritization and fit a real lifestyle. [Current positioning and names](../research/brand-culture-2026-10/POSITIONING_AND_NAMES.md) proposes Essential Effort, Reason & Routine and The Useful Few as the new shortlist, with eight ideas total. No final name is selected or cleared. Treat Pareto as prioritization, not a universal promise of 80% of fitness results from 20% effort. Training Club, the approved voice and no-character decision remain the production foundation.

> **Brand exploration, 23 October 2026:** [Pop culture research](../research/brand-culture-2026-10/README.md) combines dated platform reports, community discussions, meme examples, a preliminary name screen and a testing plan. Proposed directions are Offscreen Athletic, Minor Upgrades and Active Lore; none is selected or cleared. The owner wants broader fitness than lifting. Five topic replacements are proposed for the month, with new research/production still required. Existing production, names, calendars and posting state are unchanged by this research.

> **Current production, 22 October 2026:** [MONTH_ONE_V4.md](MONTH_ONE_V4.md) is the graphics-led V4.1 update. The owner removed the AI character. All 16 narrated masters and 36 supporting images are rebuilt without it; a separate B03 citation control gives 17 distinct videos. Open `.local/month-one-v4-graphics/review/index.html`; current archives are in `../fitness-deliverables/month-one-v4-graphics`. Character testing is retired without observations. Approved narration, source boundaries and the November calendar are retained. Full listening, target-app preview and audience/labor measurements remain pending.

> **Research foundation:** [MONTH_ONE_V3.md](MONTH_ONE_V3.md) documents the five research perspectives, canonical B-series scripts and schedule. Training Club remains selected. The active follow-up is [citation visibility](../experiments/citation-visibility-v1.json); the prior character research is historical, not a launch gate.

> **Latest content revision, 21 October 2026:** use [MONTH_ONE_V2.md](MONTH_ONE_V2.md)
> for the creator/community-sourced calendar, 16 new N-series scripts and the
> balanced experiment framework. The [N-series production package](MONTH_ONE_V2_PRODUCTION.md)
> now contains 16 narrated review videos, one matched control and 36 supporting
> images. Full listening/editorial review and audience testing remain pending.
> [MONTH_ONE.md](MONTH_ONE.md) documents the separate completed M-series exports.

> **Continuation verified 21 October 2026:** PR #3 is now merged at
> `dcba7ba079fb6b05ec1ebbb2e4cb9094b7a3f701`. Continue with
> [MONTH_ONE.md](MONTH_ONE.md) for the new calendar, content, tests and media
> status. The original handoff below preserves the earlier delivery snapshot;
> references to PR #3 being open/draft are historical.

**Prepared:** 21 October 2026  
**Owner:** Ron  
**Repository:** https://github.com/robdin/fitness  
**Purpose:** Continue the existing project in a fresh Codex session without rebuilding completed work or losing decisions, media, research or access context.

## 1. Read this first

The latest finished deliverable is **Rep_and_Reason_Time_Audit_V3.mp4**: a
36.2-second vertical fitness explainer with Ron's approved deeper voice, precise
JavaScript animations, existing OpenArt footage and synchronized subtitles.

The original **51-second Blender MVP is finished and merged into `main` through
PR #2**. Do not rebuild it. V2 and V3 are separate subsequent edits on **draft
PR #3**, which has **not been merged** as of this handoff.

The video is delivered for creative review. It has not been posted to YouTube or
Instagram. There are no audience results, sales or validated format winners.

**Immediate next action:** obtain the V3 MP4 and source ZIP, open the existing
video, and continue from Ron's feedback. A new chat is not a reason to regenerate
the voice, rerun the research, spend generation credits or start the build over.

### Copy this into the next Codex session

> Continue Rep & Reason in `https://github.com/robdin/fitness`. Read
> `docs/CODEX_HANDOFF.md` on `codex/openart-social-v2` and verify the current status
> of PR #3. PR #2's original 51-second Blender MVP is complete and merged; do not
> rebuild it. The latest review cut is the 36.2-second
> `Rep_and_Reason_Time_Audit_V3.mp4`, with my approved deeper Fish voice, timed
> JavaScript diagrams, existing OpenArt footage and 17 captions. Restore the
> media from `Rep_and_Reason_Time_Audit_V3_Sources.zip` if needed. Review the actual
> V3 and continue from my feedback. Preserve the approved voice, the explicitly
> invented 15/25/8/12-minute example, and the completed MVP. Keep code and decisions
> in GitHub and retain media separately. Do not publish to social accounts or
> purchase/renew anything unless I request it. Explain any concrete access blocker
> and keep progressing on work that is already authorized.

If PR #3 has since merged, read the same paths on `main`. If a newer head exists,
inspect its changes before using the production baseline recorded below.

## 2. Verified GitHub state

| Item | State at handoff |
| --- | --- |
| PR #2 | Merged 12 October 2026: https://github.com/robdin/fitness/pull/2 |
| Main/MVP merge commit | `18a39886418da80cfc7c6930c7960b74c716491b` |
| PR #3 | Open, draft: https://github.com/robdin/fitness/pull/3 |
| PR #3 branch | `codex/openart-social-v2` — the historical name also contains V3 |
| V2 commit | `76f560a2583fc5894c762de7c5fad424a6915f70` |
| V3 production baseline | `3b72d993ecfa3ac1415b3afc3992aa317739490a` |
| CI for that V3 baseline | Completed successfully: “Validate content and controls,” run 15 |
| CI link | https://github.com/robdin/fitness/actions/runs/39679607436 |
| This handoff | Documentation added after the V3 production baseline; retrieve the branch's current head |

CI passing is not creative approval, a publication authorization, or evidence of
audience performance. This handoff does not merge PR #3.

### Fresh checkout

```bash
git clone https://github.com/robdin/fitness.git
cd fitness
git fetch origin
git switch --track origin/codex/openart-social-v2
git status --short
```

For an existing checkout, inspect `git status` first and preserve local work.
If the branch already exists locally, use `git switch codex/openart-social-v2`
and update it normally. Do not reset or overwrite unrelated changes. A fresh
clone is safer than assuming the previous chat's scratch checkout is current:
some changes were delivered directly through GitHub tools while that checkout
remained on an older `main`.

## 3. Product and brand context

Rep & Reason is an evidence-led fitness education project. The broader repository
contains a local content-business operating system: research, scripts, production
controls, pilot experiments, measurement and offer drafts.

| Decision | Current direction |
| --- | --- |
| Working channel name | **Rep & Reason** |
| Descriptor | Strength & fitness explained. |
| Tagline | **Know why. Train better.** |
| Audience | Recreational lifters dealing with limited time, equipment constraints and conflicting advice |
| Promise | Explain a training decision and give one useful next step |
| Current format | Faceless voiceover, exact diagrams and restrained cinematic object footage |
| Character | DEX remains an optional fictional guide; character versus faceless has not been validated |
| Main colors | Navy `#10233E`, lime `#B9F227`, cream `#F7F4EA`; supporting blue and coral |
| Typeface | Bundled Space Grotesk, with SIL Open Font License |
| Voice | Practical and clear; Ron selected the first, deeper voice delivery |
| Distribution target | YouTube Shorts and Instagram Reels, with later derivatives where useful |
| Proposed content reuse | Standalone vertical stories, carousel, owned answer page and email |
| Monetization | Existing offer drafts and economics are hypotheses, not launched products or forecasts |

The name, handles and domain are not documented as cleared. There is no evidence
that the character, visual style, posting cadence or offer ladder has won a live
test. SEO/AEO strategy is to answer a real question clearly, maintain accurate
authorship and cite primary sources; there is no guaranteed ranking mechanism.

Read `brand/README.md` and `brand/RECOVERY_STATUS.md`. An earlier unpublished
49-file brand package was lost and was **not recovered byte-for-byte**. Its
34-source register, 30 question briefs, six derivative scripts and concept board
must not be claimed as recovered or fully revalidated. The current brand brief
is the retained working direction.

## 4. Deliverables and how to obtain them

### Current review package

These were saved under **Project Fitness** in the originating ChatGPT account and
linked in the project conversation. A standalone Codex CLI session may not have
access to ChatGPT Library or chat attachments. Download these files from the chat
and place them on the machine where Codex will work when those tools are absent.

| Filename | Purpose | Size |
| --- | --- | --- |
| `Rep_and_Reason_Time_Audit_V3.mp4` | Finished captioned video | 5,507,996 bytes |
| `Rep_and_Reason_Time_Audit_V3.srt` | Editable synchronized subtitles | 1,171 bytes |
| `Rep_and_Reason_Time_Audit_V3_Poster.jpg` | Cover/review frame | 127,571 bytes |
| `Rep_and_Reason_Time_Audit_V3_Sources.zip` | Exact media inputs, scripts, font and research | 27,135,580 bytes |

The source ZIP contains **21 files**, including:

- Two selected OpenArt MP4s, under `fitness/.local/openart-v2/`.
- The exact approved-delivery narration WAV, provider alignment JSON and sanitized
  generation metadata, under `fitness/.local/fish-voice/`.
- Four V3 production scripts, the original timeline used as script input,
  Space Grotesk and its license, V3 manifests, captions and research.
- Poster and contact sheet under `review/`.

**The source ZIP does not contain the final V3 MP4, the whole repository, private
voice model weights, a raw voice enrollment recording or API credentials.**
Download the MP4 separately to watch it without rendering. Clone GitHub to obtain
the full operating system and current code. The ZIP preserves the build's media
inputs and source snapshot; use the current GitHub code for subsequent work.

### Older versions

| Version | Length | Narration and role |
| --- | --- | --- |
| Blender MVP | 51.0 sec | Original synthetic narration, editable Blender scenes; completed baseline |
| Social V2 | 41.067 sec | Reused original synthetic narration; selected OpenArt shots and captions |
| Social V3 | 36.2 sec | Approved deeper Fish voice; word-timed JS graphics; current review version |

`Rep_and_Reason_Time_Audit_V2_Sources.zip` retains all four earlier video candidates
(MiniMax, Seedance, Gemini and Wan) and three image candidates. V3's smaller source
ZIP contains only its two selected clips. Use V2's package if comparing unused
creative candidates; do not assume those candidates are in V3's ZIP.

The original Blender MP4 can be restored losslessly from GitHub without rendering:

```bash
python tools/blender/unpack_mvp.py
```

Its offline player is `examples/blender-mvp/index.html`; its editable source is
`examples/blender-mvp/time-audit.blend`. The original video is stored in 33 small
parts because a large upload repeatedly stalled.

### Integrity fingerprints

```text
V3 MP4 SHA-256
e256bf2b9d56b2d815235ce09245a540ecb89eaa47b6e77c8177183f858a28cd

V3 source ZIP SHA-256
8f85074e7ee1d1467b6c445d22098bf70d1ce509668c8b6293f23aa8c9a3b795

V3 narration WAV SHA-256
8290844881739f5cf3a49bb4d249de546e885768122d726dedb08b658df79ee2

Original Blender MVP MP4 SHA-256
350a6b3439cf1034a5e8bb6a8fe947b9df23d344ec8b8ae94a1d4c9a142ab947
```

These identify delivered files. They are not a promise that a future FFmpeg
version, different platform or new neural synthesis will produce identical bytes.

## 5. V3: exact creative and technical state

| Property | Delivered value |
| --- | --- |
| Canvas | 1080×1920, 9:16 |
| Duration and frames | 36.2 seconds; 1,086 frames at 30 fps |
| Encoding | H.264, yuv420p, AAC stereo at 48 kHz |
| Spoken script | 103 words, counting hyphenated words as one |
| Narration duration | Approximately 35.279 seconds |
| Narration pace | 175.18 WPM |
| Whole-edit pace | 170.72 WPM, including head/tail space |
| Voice timing | 0.12-second lead; natural voice timing and roughly 0.8-second ending space |
| Voice processing | No pitch shift or time compression |
| Captions | 17 cues, maximum 2 lines, maximum 34 characters per line |
| Caption reading rate | Maximum 20.00 characters/second before SRT millisecond rounding |
| Audio | −16.55 LUFS integrated, −2.57 dBTP, 2.4 LU loudness range |
| Music | Quiet original procedural instrumental bed |
| OpenArt clip audio | Muted |
| New OpenArt spend for V3 assembly | 0 generation credits |

### Scene map

| Time | Scene | Visual purpose |
| --- | --- | --- |
| 0.00–3.38 | Hook | MiniMax stopwatch shot; “AN HOUR. OF WHAT?” |
| 3.38–12.58 | Audit | Sixty clock markers morph into a 10×6 grid; buckets reveal with the spoken numbers |
| 12.58–18.927 | Friction | Labeled station/equipment diagram and repeated-trip marker |
| 18.927–25.327 | Rest | Seedance stopwatch footage; largest block is not automatically the problem |
| 25.327–33.567 | Action | Log one session, change one practical thing, compare the next session |
| 33.567–36.20 | Close | One-session audit call to action and brand line |

The four bucket reveals begin at approximately **7.64, 9.08, 10.44 and 11.56
seconds**. All 60 tiles remain accounted for: 15 lifting, 25 rest, 8 setup and 12
waiting. These are **invented example minutes**, not research findings or a
description of a typical workout.

The caveat appears in narration, subtitles and a persistent audit label. Blank
session-comparison fields intentionally do not invent an improvement. Do not
turn the story into a prescription to shorten all rest periods.

### Approved script

> Your workout took an hour. But where did that hour go? An hour in the gym is not
> an hour of lifting. In this made-up example: fifteen minutes lifting.
> Twenty-five resting. Eight setting up. And twelve waiting. Those are four
> different problems. Start with a delay you can actually change. Like repeated
> trips for equipment. A time audit is not a reason to rush every rest period.
> The biggest block is not automatically the problem. For one session, log the
> four buckets. Make one practical change. Then compare the next session. Measure
> the friction before you rewrite the plan. Know why. Train better.

Ron has approved the **voice direction**, not a final publication of every V3
frame. The most recent request after delivery was to prepare this handoff; no
subsequent creative feedback on V3 is recorded here.

## 6. Voice: approved choice, access and regeneration

The user first requested his own voice, then a more enthusiastic version, and
finally selected **“the first one with the deeper voice.”** That means the first
sample's neutral/deeper delivery, not the first account profile in a list.

- Selected existing private Fish profile title: **Ron Narration v2 studio**.
- Another existing profile, **Ron Narration**, was also found. Do not silently
  switch profiles based on their ordering.
- Model used successfully: **`s2.1-pro-free`**.
- Input uses no square-bracket emotion cues, normal latency and 44.1 kHz WAV.
- The full narration is already retained. An API connection is unnecessary for
  playback, caption adjustments, visual edits or offline reproduction.
- The saved test filename is `Rep_and_Reason_Fish_Voice_Test.mp3`; it was restored
  to the original deeper sample after the enthusiastic comparison.

The user supplied a Fish API key earlier. **Its value is intentionally excluded
from this document, GitHub and the source ZIP.** Do not recover it from chat or
copy it into source files. If a new request truly requires synthesis, obtain the
current credential securely through the environment or the script's hidden prompt.
Resolve the private profile ID in the user's Fish account; the profile ID is not
needed for the supplied WAV.

### Observed service behavior, not a future availability promise

On 21 October, the API wallet showed zero credit, yet the explicitly requested
free model synthesized successfully. Creating a new saved voice returned a 403
model-limit error; existing private profiles were usable. This is why the work
used the existing studio profile instead of attempting another clone.

Timestamped synthesis uses `POST /v1/tts/stream/with-timestamp`, with the selected
model in the `model` header. Response events contain audio and alignment data.
Alignments can be cumulative within a chunk: retain the latest snapshot per
`chunk_seq`, then add `chunk_audio_offset_sec` to local segment times. Appending
every snapshot would duplicate words. The generator already handles this.

The API rejected 48 kHz WAV in this request; 44.1 kHz succeeded. Do not confuse
that synthesis format with the final video's resampled 48 kHz soundtrack.

Optional regeneration command, only after a revised script or voice change:

```bash
python tools/video/generate_fish_narration.py --voice-id YOUR_PRIVATE_PROFILE_ID
```

The generator reads `FISH_API_KEY` or asks through a hidden terminal prompt.
It writes `narration.wav`, `alignment.json` and sanitized `generation.json` in
`.local/fish-voice/`. Recheck current model availability before a future call.
Do not promise indefinite free usage or exact reproducibility of neural speech.

The user prefers the **external browser** over the in-app browser when UI access
is needed. Use an available service API/connector first; browser login state and
connected tools may not carry over to a separate Codex environment.

## 7. OpenArt and model decisions

OpenArt was connected in the originating ChatGPT environment, and the existing
account credits were used for earlier visual candidates. The user reports the
subscription ends **24 October 2026**. Confirm the account's current terms and
balance before a future generation; do not assume they transfer to another tool
or that subscription renewal has been requested.

V3 reuses these exact selected assets:

| Asset | OpenArt history ID | OpenArt resource ID | Role |
| --- | --- | --- | --- |
| `minimax.mp4` | `FmNfzPL7eLzcWKXbFvsf` | `qlo6NrRVcJDjGtaHkLHr` | Opening stopwatch shot |
| `seedance.mp4` | `rtZkAyHLaPmoRZl1rWKT` | `S8bghXDskNjOBEJ0qhdj` | Rest section |

Project ID: `M1ohGPOCnik4u3Bn0q8m`. File checksums and exact bytes are in
`examples/openart-social-v3/source-manifest.json`. These identifiers are useful
for account-side retrieval; they are not public download URLs or credentials.

The connected catalog was checked during the research, including MiniMax H3,
Seedance 2.5, Wan 3.0 and other choices. The user explicitly wanted the Arena
leaderboard considered. The retrieved page displayed a **21 September 2026**
snapshot, even though it was accessed on 21 October. Do not describe it as a
newly updated October ranking.

Arena is a model shortlist input. It does not establish diagram accuracy,
exercise-form correctness or the best shot for this episode. The selected
MiniMax footage was not claimed to be the number-one overall model. Different
model configurations, resolutions and overlapping uncertainty matter.

For future generations: specify the shot, check the available model and exact
configured credit cost, submit once, retain the job ID and receipt, reconcile
uncertain jobs before retrying, download the output and hash it. Keep numerical
labels, captions and scientific annotations in code. The current source media
needs no additional generation call.

## 8. Research conclusions to preserve

The full review is committed at:

https://github.com/robdin/fitness/blob/codex/openart-social-v2/docs/VIDEO_PACING_AND_VISUAL_RESEARCH_2026-10-21.md

It contains 13 source entries, distinctions between evidence and editorial
inference, tool comparisons and an audience-testing proposal. It is a targeted
review, not an exhaustive systematic review.

### Narration pace

No controlled source reviewed established a universal optimum WPM for English
fitness Shorts or Reels. **170–185 WPM is an editorial starting range for this
single-idea episode**, not an algorithm requirement or a scientific threshold.

Guo et al. (2014) associated faster delivery with engagement in a large edX
dataset, but that was observational MOOC viewing. Murphy et al. found modest
costs for accelerated lectures in their tested conditions. The broader 2025
meta-analysis by Tharumalingam et al. found possible comprehension costs from
faster playback, with small/often nonsignificant costs at up to 1.5×. Playback
multipliers do not directly imply a natural speaking-rate target for a feed video.

V3's approved voice naturally falls near 175 WPM. The edit therefore preserves
the voice and synchronizes visuals instead of forcing acceleration.

### Caption and visual design

- Netflix's 20 adult characters/second and two-line guidance is a professional
  timed-text reference; it is not a Shorts/Reels ranking rule.
- V3 uses short phrase captions rather than flashing every word individually.
- Meta's approximately 14% top / 35% bottom / 6% side ad safe-area guidance was
  used conservatively. Organic UI overlays vary; preview in the target uploader.
- Caption panels occupy y=1112–1248; key text is approximately within x=70–920
  and y=286–1248 on the 1080×1920 canvas.
- Noetel et al.'s multimedia review supports signaling, contiguity, coherence
  and segmentation. Applying those findings here is a design inference, not a
  claim of experimentally proven Shorts retention gains.
- Numbers appear when named; labels stay near their graphics; motion explains a
  process; invented data stays explicitly labeled.

### Tool roles

| Tool | Intended role |
| --- | --- |
| JS Canvas / Skia | Exact diagrams, deterministic labels, timing and captions; used in V3 |
| Remotion | Future React-based reusable episode/editor system if that workflow becomes useful |
| Motion Canvas | Future voice-synchronized vector explanations of mechanisms |
| Blender | Controlled 3D geometry, props and spatial explanations; original MVP is retained |
| OpenArt | Cinematic contextual footage and object shots |
| FFmpeg | Encoding, mixing, concatenation and playback/loudness verification |

These tools are options with different roles. They do not all need to appear in
every episode. Do not install a larger framework simply to reproduce this cut.

## 9. Source-of-truth map

| Path | Meaning |
| --- | --- |
| `docs/CODEX_HANDOFF.md` | This comprehensive continuation document |
| `docs/PROJECT_HANDOFF.md` | Short history and original MVP recovery instructions |
| `docs/VIDEO_PACING_AND_VISUAL_RESEARCH_2026-10-21.md` | Current pacing and visualization research |
| `examples/openart-social-v3/README.md` | V3 build, delivery and editorial explanation |
| `examples/openart-social-v3/timeline.json` | Produced scene/caption/word timing snapshot |
| `examples/openart-social-v3/verification.json` | Checks performed on the delivered media |
| `examples/openart-social-v3/build-receipt.json` | Output and source fingerprints, model and renderer details |
| `examples/openart-social-v3/source-manifest.json` | Selected OpenArt IDs and fingerprints |
| `tools/video/generate_fish_narration.py` | Optional Fish synthesis with timestamps; network action |
| `tools/video/prepare_social_v3.py` | Align script, build SRT, mix music and voice, decode selected clips |
| `tools/video/render_social_v3.cjs` | JS/Skia frame renderer and animation states |
| `tools/video/assemble_social_v3.py` | Bounded rendering orchestration and final mux |
| `tools/video/assemble_social_v2.py` | Historical V2 compositor using original narration |
| `examples/blender-mvp/` | Completed original video, offline player, `.blend` and timeline |
| `tools/blender/` | Historical Blender build, composition and lossless pack/unpack tools |
| `content/mvp/time-audit/episode.json` | Authored episode content from the MVP |
| `content/mvp/time-audit/fonts/` | Space Grotesk and license |
| `fitness_os/` | Original Python business/content-control system |
| `research/`, `content/pilots/`, `experiments/`, `offers/`, `measurement/` | Earlier research, pilot variants, protocols, draft offers and metric definitions |

### Script synchronization caveat

V3 is still an episode-specific renderer. `generate_fish_narration.py` reads the
original timeline's top-level `cues`; `prepare_social_v3.py` reads its scene-level
cues. Several visual markers, cue indices, phrase breaks, values and titles are
hard-coded for this script. Editing only `episode.json` will not automatically
update V3. Do not edit the historical MVP just to force a new script through it.

For another episode or a script revision, introduce a dedicated V3/V4 episode
input, update both synthesis and preparation to consume it, retain the original
MVP inputs, then regenerate speech and timing only as needed. Verify text matches
the actual returned alignment. This is a known next engineering task, not work
already completed in the current deliverable.

### Older documentation can be stale

Some foundation documents still say no paid generation occurred, providers are
unconnected, voice approval is pending, or repository authentication needs
restoring. Those statements describe earlier phases. OpenArt assets and the
approved voice now exist, and GitHub delivery works. However, the repository
still does **not** contain a general, fully integrated paid-provider adapter or
automated social publisher. V3's media scripts sit alongside the original
`fitness_os` controls; they do not automatically implement every reservation,
invoice, rights and release-record contract in that system.

Use current receipts and this handoff for the V3 state. Reconcile old status and
architecture documents as a focused follow-up; do not interpret their historical
wording as a reason to discard delivered work or as evidence of integrations that
have not been built.

## 10. Restore media in a new Codex checkout

After cloning the correct branch, download the source ZIP alongside the checkout.
The following runs from the `fitness/` repository root and restores only the
ignored media inputs, preserving the newer code from GitHub:

```bash
python - <<'PY'
from pathlib import Path
from zipfile import ZipFile

archive = Path('../Rep_and_Reason_Time_Audit_V3_Sources.zip')
prefix = 'fitness/.local/'
root = Path('.local').resolve()
with ZipFile(archive) as z:
    for info in z.infolist():
        if not info.filename.startswith(prefix) or info.is_dir():
            continue
        target = (root / info.filename[len(prefix):]).resolve()
        if root not in target.parents:
            raise ValueError('Unexpected archive path')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(z.read(info))
print('Restored existing narration, alignment and selected clips.')
PY
```

Expected required inputs:

```text
.local/fish-voice/narration.wav
.local/fish-voice/alignment.json
.local/fish-voice/generation.json
.local/openart-v2/minimax.mp4
.local/openart-v2/seedance.mp4
```

The source ZIP contains Ron's synthesized narration. Retain it privately; keep
credentials, raw voice enrollment recordings and model weights out of Git.

The previous scratch root was `/workspace/scratch/99bd8b35d955`, with the repository
in `fitness/` and outputs in `deliverables/v3/`. Those are historical convenience
paths, not durable locations or required paths in the new environment. GitHub and
the downloaded deliverables are the transferable sources.

## 11. Reproduce or revise the video

**Watching the existing MP4 needs none of these build steps.** Use them when an
edit requires a new export or when the final MP4 is unavailable but inputs remain.

### Dependencies

- Python 3.11+; delivery used Python 3.12.
- NumPy and Pillow for V3 preparation/review.
- FFmpeg and ffprobe on `PATH`.
- Node.js; delivery used v24.19.0.
- `@napi-rs/canvas`; delivery used **0.1.100**.
- Bundled Space Grotesk font.

The project's `pyproject.toml` declares Pillow but not NumPy or Node dependencies.
An editable Python install alone is not a full V3 rendering setup. A normal local
setup from the repository root is:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . numpy
npm install --no-save --package-lock=false @napi-rs/canvas@0.1.100
ffmpeg -version
ffprobe -version
node --version
```

Install FFmpeg and Node through the machine's chosen package manager if absent.
Do not install Blender merely to render V3. Keep `node_modules/`, `.venv/`, caches
and media out of commits. If the environment supplies another Node binary or
module location, use `CODEX_PRIMARY_RUNTIME_NODE` / `NODE_PATH`; these are optional
runtime conveniences, not secrets.

### First inspect stills

```bash
python tools/video/prepare_social_v3.py
node tools/video/render_social_v3.cjs .local/social-v3 ../deliverables/v3 --stills
```

Inspect the hook, all four buckets, the longest caption, the action states and
the close before a full export. Changing captions alone does not require Fish.
Changing voice text does require new speech and alignment.

### Full export

```bash
python tools/video/assemble_social_v3.py
```

Default output:

```text
../deliverables/v3/Rep_and_Reason_Time_Audit_V3.mp4
```

For already prepared inputs:

```bash
python tools/video/assemble_social_v3.py --skip-prepare
```

**Use the Python orchestrator for full renders.** It renders 150-frame/five-second
pieces in separate Node processes, limits FFmpeg threads, then concatenates the
video without another video encode and adds the soundtrack. This bounds native
Skia image-cache memory. Two earlier monolithic render attempts exited with code
137 near the rest scene; garbage collection alone did not solve that growth.

The orchestrator writes a temporary MP4, probes it and replaces the final path.
An earlier export reported completion but had a missing `moov` atom; the delivered
file was remuxed to a fresh path and fully decoded successfully. Never deliver a
file solely because a subprocess printed “COMPLETE.”

The V3 scripts do not currently provide a `--clean` export flag. V2 has one, but
do not assume it applies to V3. If a clean master is needed for native captions,
wire the existing frame-rendering caption toggle through V3's CLI and validate a
separate export. This is optional future work, not an already supplied file.

The orchestrator regenerates working files; it does not automatically refresh
every committed receipt, exported SRT copy or source ZIP. After a changed final
build, copy the matching SRT/timeline, refresh verification and hashes, and retain
the exact media package before updating documentation.

## 12. Verification and completion criteria

### Already performed on the delivered V3

- Full MP4 video/audio decode passed, 1,086 frames, 36.2 seconds.
- 17 subtitle cues are ordered, nonoverlapping and inside the video duration.
- Maximum two lines, 34 characters per line and 20.00 characters/second before
  serialization rounding.
- Provider alignment text matches the entire script after punctuation/hyphen
  normalization. This is **not independent ASR or a claim of a human listening audit**.
- Twelve storyboard frames and a decoded final audit frame were visually inspected.
- The invented bucket counts sum to exactly 60 and are labeled as fictional.
- Final audio measured −16.55 LUFS integrated and −2.57 dBTP.
- Original MVP SHA-256 remained unchanged.
- Repository content check and all **22 existing tests** passed locally.
- GitHub CI passed for the V3 production baseline identified in section 2.

The 22 existing tests cover the original operating-system controls. They are not
22 new animation tests or proof that the video will retain viewers.

### Commands for a changed export

From the repository root:

```bash
python -m fitness_os check
python -m unittest discover -s tests -v

ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate,channels,nb_frames -of json ../deliverables/v3/Rep_and_Reason_Time_Audit_V3.mp4

ffmpeg -v error -i ../deliverables/v3/Rep_and_Reason_Time_Audit_V3.mp4 -f null -

ffmpeg -hide_banner -nostats -i ../deliverables/v3/Rep_and_Reason_Time_Audit_V3.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json -f null -
```

The last command measures the input and a hypothetical normalization pass; use
the `input_i`, `input_tp` and `input_lra` fields to report the file's actual level.
Inspect representative decoded frames and listen to the final mix before final
creative approval. Preview text placement in the intended Shorts/Reels uploader.
Stop optional testing once concrete risks and required gates are resolved.

## 13. Broader operating system and remaining work

The repo is more than a video renderer. Existing materials include a business
plan, PRD, 20 research workstream records, source/competitor registers, three
canonical pilot topics with two sequence variants each, six earlier silent
prototypes, worksheet drafts, experiment protocols, aggregate metric imports,
cost-control logic and offline commerce-event handling.

Read these before expanding the product:

- `docs/BUSINESS_PLAN.md`, `docs/PRD.md`, `docs/OPERATIONS.md`.
- `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/BACKLOG.md`.
- `docs/PILOTS.md`, `docs/EXPERIMENTS.md`, `research/RESEARCH_ROUNDS.md`.
- `docs/TURUAN_REUSE.md` for the earlier project; source-level compatibility was
  not established, so do not claim a completed code port.

The earlier research and pilot counts describe retained records, not proof that
every scientific claim or market assumption is resolved. The time-audit video
is a creative sample, not a randomized pilot result. The local tools are a
single-operator foundation, not an authenticated multi-tenant service.

### Prioritized continuation

| Priority | Work | Done when |
| --- | --- | --- |
| P0 | Restore and review the existing V3 | Ron can watch the actual current MP4; feedback is captured precisely |
| P0 | Apply requested creative feedback | Revised voice/layout/pacing is reviewed without unintended script or example changes |
| P1 | Make PR #3 ready for integration | Current head passes checks and the intended changes are reviewed; handle merge under the user's current direction |
| P1 | Reconcile old status documents | Provider, voice and production statements match actual receipts and remaining adapter gaps |
| P1 | Separate episode data from V3 hard-coded timing | A new script can use one dedicated input without modifying the finished MVP |
| P2 | Prepare a reviewed upload package | Correct channel, cover, title, description, captions, claim/rights review and uploader preview |
| P2 | Publish only when requested | Remote platform receipt exists; local export is not called a published video |
| P2 | Measure the first real audience response | Actual platform exports and meaningful denominators are retained |
| P3 | Produce another evidence-led topic | Reviewed question, primary-source claim packet, script, assets and final review |
| P3 | Build provider/publishing automation where needed | Budget records, job reconciliation, retained media, account scopes and retry rules are implemented |

For pacing experiments, change one major variable at a time. V2 versus V3 is a
poor isolated WPM test because voice, captions and graphics also changed. Use
Shorts stayed-to-watch, engaged-view duration, percentage viewed and retention
around the numerical section. Review Reels separately using the metrics actually
available in that account. Saves/shares and simple comprehension feedback can
complement retention. Do not invent universal performance thresholds or infer
causation from two small organic posts.

## 14. Working preferences and boundaries

- Ron wants concrete completed work, not repeated capability acknowledgments or
  confirmation prompts for routine reversible steps.
- Use the existing project and accepted decisions. Do useful work before asking
  a question; ask only when a missing input materially changes the outcome.
- He was frustrated by a previous 13+ hour run. Prefer short visual checkpoints,
  bounded exports and reuse of approved media.
- Share concise progress updates during sustained work and describe failures
  accurately. Do not call an output complete before checking the actual file.
- Prefer an external browser when browser interaction is necessary.
- Keep code and durable decisions in GitHub. Keep large media, voice assets and
  credentials outside the repository, with recoverable source packages.
- Preserve the approved deeper voice. The enthusiastic comparison was not the
  selected direction.
- Do not spend credits merely because they are available, renew a subscription,
  send outreach or publish content without a relevant user instruction.
- If an access rule or automatic approval review blocks a concrete action,
  explain which action is blocked and why. Use a permitted alternative when one
  can complete the task; do not silently bypass the restriction.

## 15. What the next session should report back

After its initial inspection, the next Codex session should briefly confirm:

1. The branch/PR state it actually found.
2. Whether the finished V3 MP4 and source media are available.
3. The specific feedback or next change it is applying.
4. Any concrete missing account access or file needed for that change.

Then proceed with the requested work. This handoff is sufficient to resume the
project without reconstructing the conversation or repeating the completed MVP.
