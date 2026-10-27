# Project BOMD — fitness content MVP

> **Pilot preparation, 27 October 2026:** [Execution sheet](docs/MONTH_ONE_V6_PILOT.md) · [Profile copy](content/month-one-v6/ACCOUNT_ENTRY.md) · [Measurement field guide](measurement/MONTH_ONE_V6_FIELD_GUIDE.md). The specialist follow-up adds useful captions, a corrected BC05 hook/narration, stronger measurement and recovery checks, and a hash-bound first-week review page. Instagram @bodyofourdreams and the YouTube channel are now confirmed connected through Metricool (TikTok is also connected). Actual playback, native uploader/export checks and audience/labor evidence remain pending. No public posts have been created.

> **Current production, 27 October 2026:** [Conversational Blueprint V6](docs/MONTH_ONE_V6.md) is the current revision: sixteen rewritten core videos, a separate account introduction, updated supporting content and refreshed matched controls. Blueprint's identity is unchanged; mental models are optional. [Calendar](content/month-one-v6/CALENDAR.md) · [Scripts](content/month-one-v6/SCRIPTS.md). Review and measurement remain pending; nothing is published. Earlier production descriptions below are historical.

> **Historical synthesis, 24 October 2026:** [Complete project handoff and reusable content framework](docs/CONTENT_IDEA_FRAMEWORK_AND_HANDOFF.md), with a [blank template for another idea](docs/templates/NEW_CONTENT_IDEA_TEMPLATE.md). Blueprint V5 is the current month; D — Off-Duty Hero is selected for character exploration. Older brand/prototype descriptions below are historical. Audience validation remains pending.

**Know why. Train better.**

Historical V3 snapshot: a working, local-first foundation for an evidence-led fitness content business. Research, scripts, production controls and experiments live together. The latest B-series review package contains **16 rewritten narrated videos, two brand alternatives, one motion control, four carousels and eight story sequences**, supported by five research briefs and a 64-question bank. Training Club is the owner-selected brand direction. The N-series remains available as a prior version. Earlier M-series, Blender/V3 work and six silent prototypes are retained. It has not published videos, recruited participants, generated sales or run a live A/B test.

## Start here

- [Conversational Blueprint V6](docs/MONTH_ONE_V6.md): current production and rebuild instructions. Local review: `.local/month-one-v6-conversational/review/index.html`. D comparisons: `.local/blueprint-character-d-v6-preview/index.html`.
- [Training Club production V4](docs/MONTH_ONE_V4.md): the full month with larger diagrams, source cues and a matched citation test. The AI character has been removed. [Brand application](brand/v4/STYLE_GUIDE.md). Audience validation remains pending.
- [Research-led beginner month V3](docs/MONTH_ONE_V3.md): all five research perspectives applied to a complete new month of production. [Read the research](research/audience-v3/README.md), [calendar](content/month-one-v3/CALENDAR.md), [scripts](content/month-one-v3/SCRIPTS.md), and [three brand systems](brand/v3/STYLE_GUIDE.md). The media hub and ZIPs are retained locally; audience validation remains pending.

- [Demand-led calendar V2](docs/MONTH_ONE_V2.md): creator/community source map,
  16 new original scripts and visual briefs, complete supporting copy, November
  planning calendar and balanced testing protocol. [Open the visual calendar](examples/month-one-v2/index.html).
  [Finished N-series review media](docs/MONTH_ONE_V2_PRODUCTION.md): 16 narrated
  videos, one matched motion control and 36 supporting images, with source-linked
  posting copy and retained production inputs. Listening/editorial review remains
  pending. The M-series media below is a separate earlier package.

- [Month-one validation pilot](docs/MONTH_ONE.md): 30-day calendar, 16 narrated videos,
  three visual treatments, supporting posts, reusable production tools and an
  audience-interest / 12-hour-per-week go/no-go protocol.

- [Current Codex handoff](docs/CODEX_HANDOFF.md): the finished 36.2-second V3 social cut, approved deeper voice, research, source-media recovery and continuation instructions.

- [Narrated Blender MVP](examples/blender-mvp/README.md): a complete vertical video with animated 3D visuals, captions, original sound and editable sources.
- [Rep & Reason brand brief](brand/README.md): recovered creative decisions and [recovery limits](brand/RECOVERY_STATUS.md).

- [Business plan](docs/BUSINESS_PLAN.md): customer, positioning, GTM, offer ladder, economics and decision gates.
- [Product requirements](docs/PRD.md): requirements, acceptance criteria and build boundaries.
- [All research rounds](research/RESEARCH_ROUNDS.md): 20 decision records and outstanding validation.
- [Pilot review guide](docs/PILOTS.md): the three comparisons, recording instructions and questionnaires.
- [Six-variant preview gallery](examples/pilot-review/index.html): open locally after cloning or extracting the package.
- [Experiment playbook](docs/EXPERIMENTS.md): randomized screening versus YouTube packaging tests.
- [Implementation status](docs/IMPLEMENTATION_STATUS.md): working features, manual steps and integrations still needed.
- [Operations](docs/OPERATIONS.md), [architecture](docs/ARCHITECTURE.md), [Turuan reuse audit](docs/TURUAN_REUSE.md).
- [Execution backlog](docs/BACKLOG.md): sequenced work with acceptance criteria.

## Historical prototype quick start

Requires Python 3.11+, Pillow, FFmpeg/ffprobe and DejaVu Sans fonts. The current environment was verified with Python 3.12 and Pillow 12.3. Media builds record exact tool/font identities. Fonts are detected at the Linux DejaVu system path; adjust the renderer deliberately for another environment.

~~~bash
python -m pip install -e .
python -m fitness_os check
python -m unittest discover -s tests -v
python -m fitness_os init
python -m fitness_os render --all --workers 2
python -m fitness_os gallery
~~~

The build command runs two independent render workers over all six variants. It uses local code and no paid API. Open the generated gallery path. Preview captions contain the proposed narration; the preview MP4s are silent.

~~~bash
python -m fitness_os power --baseline 0.5 --lift 0.15 --comparisons 3
python -m fitness_os economics config/economics.example.json
python -m fitness_os metrics-report
python -m fitness_os task-packet P01-time --role evidence_review
~~~

The economics inputs are examples, not prices chosen for launch or a revenue forecast. An empty metrics report is expected before account data is imported.

## Repository map

| Path | Purpose |
| --- | --- |
| config/ | Brand, founder decisions and example economics |
| research/ | Source register, competitor observations, 20 rounds and evidence packet |
| content/pilots/ | Canonical scripts, claims, sequences and packaging candidates |
| content/ideas.json | Thirty draft ideas and a gated 12-item editorial queue |
| experiments/ | Protocols and comprehension instrument |
| offers/ | Three actual worksheet drafts, offer scope and lifecycle copy |
| prompts/ | Bounded task instructions for AI assistance |
| measurement/ | Event definitions and import template |
| fitness_os/ | Python CLI, rendering, accounting, experiments and imports |
| tests/ | Failure-path and integrity tests |
| examples/blender-mvp/ | Narrated Blender MVP, editable project and review files |
| tools/blender/ | Procedural scenes, local synthesis and composition |
| content/mvp/ | Editable episode copy and licensed font |
| brand/ | Recovered brand direction and explicit recovery gaps |
| examples/pilot-review/ | Small retained snapshot of all six silent prototypes |
| .local/ | Ignored runtime state, audio, builds, reports and release packages |

The small prototype snapshot is included for review. Large production media, customer data, secrets and runtime state do not belong in Git. Back up the ignored operating data separately. The system is a trusted single-operator tool, not an authenticated multi-tenant service.

## Current boundary

The target repository was empty. This implementation is new code informed by the supplied Turuan guide. A code-level Turuan review has not been completed, so no code port or compatibility claim has been made. Production account connections, final editorial approval and audience/customer observations remain necessary. The deeper narration voice is approved; individual new exports still need final review. See the status file for the exact boundary and docs/DELIVERY.md for GitHub delivery status.
