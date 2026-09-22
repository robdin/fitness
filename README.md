# Project Fitness — DEX content business OS

**Know why. Train better.**

A working, local-first foundation for an evidence-led fitness content business. Research, scripts, production controls and experiments live together. The current release prepares **three topics × two sequence variants**, with six silent video prototypes. It has not published videos, recruited participants, generated sales or run a live A/B test.

## Start here

- [Business plan](docs/BUSINESS_PLAN.md): customer, positioning, GTM, offer ladder, economics and decision gates.
- [Product requirements](docs/PRD.md): requirements, acceptance criteria and build boundaries.
- [All research rounds](research/RESEARCH_ROUNDS.md): 20 decision records and outstanding validation.
- [Pilot review guide](docs/PILOTS.md): the three comparisons, recording instructions and questionnaires.
- [Six-variant preview gallery](examples/pilot-review/index.html): open locally after cloning or extracting the package.
- [Experiment playbook](docs/EXPERIMENTS.md): randomized screening versus YouTube packaging tests.
- [Implementation status](docs/IMPLEMENTATION_STATUS.md): working features, manual steps and integrations still needed.
- [Operations](docs/OPERATIONS.md), [architecture](docs/ARCHITECTURE.md), [Turuan reuse audit](docs/TURUAN_REUSE.md).
- [Execution backlog](docs/BACKLOG.md): sequenced work with acceptance criteria.

## Quick start

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
| examples/pilot-review/ | Small retained snapshot of all six silent prototypes |
| .local/ | Ignored runtime state, audio, builds, reports and release packages |

The small prototype snapshot is included for review. Large production media, customer data, secrets and runtime state do not belong in Git. Back up the ignored operating data separately. The system is a trusted single-operator tool, not an authenticated multi-tenant service.

## Current boundary

The target repository was empty. This implementation is new code informed by the supplied Turuan guide. A code-level Turuan review has not been completed, so no code port or compatibility claim has been made. Production account connections, real narration, editorial approval and audience/customer observations remain necessary. See the status file for the exact boundary and docs/DELIVERY.md for GitHub delivery status.
