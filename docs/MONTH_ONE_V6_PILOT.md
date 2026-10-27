# V6 pilot · execution sheet

Updated 27 October 2026. The four audit actions are caption/entry improvements, measurement repair and rehearsal, first-week playback plus BC05 correction, and a bounded organic pilot. Blueprint, the conversational speaker direction and the primary audience/effort hurdles remain unchanged. A fresh visual experiment is conditional on actual feedback.

## What is ready and what remains real-world work

All sixteen captions now carry a usable example or specific action and one relevant discussion prompt. Two polls use everyday language and allow uncertainty. BC05 now promises a question to ask about starting weight, matching its instructor-help lesson; the successful previous take is preserved. The profile copy is in [ACCOUNT_ENTRY.md](../content/month-one-v6/ACCOUNT_ENTRY.md).

The repaired evaluator supports V6, reports joint attention separately, and requires distinct dated production weeks with reconciled immutable labor logs. Recovery checks now run without the old calendar or ASR downloads; new voice receipts bind model, delivery, speed and an opaque profile fingerprint. Historical audio remains explicitly profile-unknown where that fact was never recorded.

Actual audience evidence and owner labor are still unmeasured. Automated decoding, alignment, speech recognition and frame checks do not establish human listening or native uploader legibility. Metricool now confirms Instagram @bodyofourdreams and YouTube channel UCBJu873k_PPBioEwrtsDU5Q for brand 7611975, in America/New_York. TikTok @bodyofourdreams is also connected but remains outside this two-platform pilot. Planner and YouTube analytics reads succeeded; the pilot-period queue and queried analytics were empty. See [the connection receipt](../examples/month-one-v6/metricool-connection-verification.json). Connection is verified; native upload previews and exact-window metric rehearsal are still separate checks. Do not label this pilot launched until native post receipts exist.

## First-week order

Dates remain the existing proposal, at 18:00 America/New_York. BC00 is an additional orientation asset, outside the sixteen core videos. Verify it before BC01; it can release immediately before BC01 on launch day.

| Date | Asset | Action |
|---|---|---|
| Nov 1 | BC00 + BC01 | Introduce the account; help with the first gym visit. Pin only once live. |
| Nov 2 | BCS01 | Ask whether the plan or equipment feels unclear. Add a native poll. |
| Nov 3 | BC02 | Machines are a valid starting option; copy the equipment note. |
| Nov 4 | BCK01 | Founding story carousel; third profile pin once live. |
| Nov 5 | BC03 | Rest guidance with the small-study limitation. |
| Nov 6 | BCS02 | Rest-timer poll; the follow-up is general advice, not a fabricated vote result. |
| Nov 7 | BC04 | Fit a short walk around lunch; preserve the whole-target caveat. |
| Nov 8, 20:00 | Internal review | Collect mature BC01 data if available, check questions and log effort. Do not judge the full month from one post. |

If launch is delayed, shift the full calendar and readout before publishing; do not quietly compress the cadence. The existing full-cohort proposal is December 5. Later cumulative reach does not improve a frozen first-week exposure count.

## Playback and native upload review

Use the generated `pilot/index.html` for BC00–BC04 and the revised BC05. Listen at normal speed on the phone you will use. Check the actual rendered export from beginning to end: intelligible natural speech, no missing/changed words, captions in time, readable example, source/limitation clear, and one understandable next action. BC03 especially must not sound like a universal three-minute prescription; BC04 must not imply a short walk meets all activity needs.

Then preview each exact upload in both intended platforms. Check captions, UI overlays, first-frame crop/cover, description/source copy, account identity and audience setting. Record the platform, checked media SHA-256, reviewer, time, result and any correction in the local operations ledger. Repeat the relevant review after an export changes. A local frame check does not supply this native preview.

Ledger location: `.local/month-one-v6-conversational/pilot/operations.json`. The preparer creates it from the empty tracked template only if absent and never overwrites it. A review entry is `{episode_id, media_sha256, kind, platform, reviewer, reviewed_at, result, notes}`. `kind` is `listening` (platform omitted) or `native_preview` (platform `youtube_shorts` or `instagram_reels`, plus `account_native_id` matching the verified target account); `result` is `pass` or `needs_fix`. Timestamp must include timezone. Record actual reviews only. The newest review for that exact hash/platform/account controls readiness; conflicting newest-time results fail closed; a later correction invalidates an earlier pass.

An account record is `{native_id, public_url, verified_at, verified_by, timezone}`. Verify against the actual signed-in account. Release entries should include episode/platform, native post ID, public URL, actual public timestamp, master hash and scheduling receipt if used. A scheduler's accepted job is not proof of public release.

## Measurement rehearsal and collection

Follow [the field guide](../measurement/MONTH_ONE_V6_FIELD_GUIDE.md). Synthetic unit tests rehearse parsing, decision logic and rejection of bad evidence; they are never mixed into actual logs.

The current Metricool YouTube **all videos** metric catalog exposes views, watch minutes and average duration, but does not expose engaged views, stayed-to-watch or average percentage viewed under those names. Do not substitute those fields. Use native Studio for the required primary fields and preserve the original labels, filters, data-through time and source export. The native first-168-hour workflow still needs rehearsal on this account. If exact-window collection is unavailable, document it and make any prospective protocol revision before launch. Never invent a match.

For each actual public episode, record the release timestamp and calculate +168 hours and the current +24-hour collection grace deadline. Collect once in that fixed window, preserve the original source, map native fields, then run:

```sh
.venv/bin/python tools/video/evaluate_month_one_v3.py --series v6
```

The 14-day bounded extension can complete late-release maturity, comprehension/labor checks, or missing documentation for a snapshot collected within the permitted grace. It cannot turn a later cumulative report into first-week data or bypass the current collection deadline.

## Viewer check and the conditional visual experiment

Use willing adult beginners: do not send unsolicited recruitment. Seek ten distinct first-exposure viewers for the core checks, with a mix of busy schedules and prior gym experience documented. The existing audience protocol is a small comprehension screen, not a representative market survey.

Give each person one current clip first, without explaining its lesson. Ask: “What was this telling you?”, then “What would you do next?” Record the answers before asking “Was there anything this didn't tell you?” Score against that episode's existing takeaway, next action and critical error in the canonical calendar. Ask what was hard to read or follow. Keep responses pseudonymous; retain prior relationship and recruitment source as possible bias. Test BC00 separately for who the account helps and why to return.

Only if at least two independent first-exposure viewers identify the same actionable readability or comprehension problem, log it and select **one** relevant change. This is an operating trigger, not statistical significance. For example, if the example card gets lost, simplify or lengthen that card; don't simultaneously change character, music, voice and hook. Use matched narration/timing where the tested change allows it, record all unavoidable differences, and use fresh viewers with first exposure balanced between versions. Keep preference questions after comprehension. A repeated critical misunderstanding needs correction even before that trigger; withhold the affected release until corrected and rechecked.

CV3, static-motion and D character comparisons remain available as private assets. They are not extra scheduled posts and no visual test is declared run. No new character or style change is necessary to launch.

## Sustainability and decision

Measure two real complete weeks that each create or substantially revise four distinct core drafts, including research, scripts, claims, visuals, review, supporting posts, posting, community and measurement. Next-month drafts can supply this work while the prebuilt month runs. Count hands-on time separately from unattended rendering and setup. No invented representative batch for this implementation session.

The retained hurdles are 12 mature releases, eight eligible videos with at least 100 engaged views each, median stayed-to-watch ≥60%, median percentage viewed ≥70%, five distinct useful responses, at least ten comprehension checks with ≥80% passing, and two evidenced production weeks ≤12 hands-on hours. These are provisional operating choices, not industry benchmarks. Report distribution failures and uncertainty. Read the exact go/iterate/no-go/insufficient rules in [protocol 6.1](../experiments/month-one-v6.json).

Monetization is a later diagnostic: collect recurring problems and voluntary requests; don't add an untested paid offer, an email funnel or an affiliate push to this audience/sustainability pilot.
