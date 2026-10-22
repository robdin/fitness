"""Build the reviewable demand-led calendar; never generates or publishes media."""
import argparse
import html
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / 'content/month-one-v2/calendar.json'
SOURCES = ROOT / 'research/month-one-demand-v2.json'
PLAN = ROOT / 'experiments/month-one-v2.json'


def load():
    return tuple(json.loads(p.read_text()) for p in (CONTENT, SOURCES, PLAN))


def narration(ep):
    return ' '.join(b['narration'] for b in ep['beats'])


def source_map(sources):
    return {s['id']: s for group in ('creators', 'community', 'evidence', 'metrics_sources') for s in sources[group]}


def validate(data, sources, plan):
    episodes = data['episodes']
    ids = [e['id'] for e in episodes]
    if len(ids) != 16 or len(set(ids)) != 16 or ids != plan['episode_ids']:
        raise ValueError('Sixteen unique episode IDs must match the protocol')
    maps = {k: {s['id'] for s in sources[k]} for k in ('creators', 'community', 'evidence')}
    all_sources = [s['id'] for g in sources if g in (*maps, 'metrics_sources') for s in sources[g]]
    if len(all_sources) != len(set(all_sources)):
        raise ValueError('Duplicate source IDs')
    for s in source_map(sources).values():
        if not s['url'].startswith('https://'):
            raise ValueError('Source URLs must be HTTPS')
    for e in episodes:
        for group, field in [('creators', 'creator_ids'), ('community', 'community_ids'), ('evidence', 'evidence_ids')]:
            if not set(e[field]) <= maps[group]:
                raise ValueError(f'{e["id"]}: unresolved {group} source')
        if not e['creator_ids'] or not e['community_ids']:
            raise ValueError('Every episode needs creator and community traceability')
        if not e['evidence_ids'] and not e['claim_type'].startswith('editorial_'):
            raise ValueError('A research claim needs evidence')
        if len(e['beats']) != 6 or not all(b['narration'] and b['visual'] for b in e['beats']):
            raise ValueError('Six complete spoken and visual beats required')
        if not 75 <= len(narration(e).split()) <= 100:
            raise ValueError(f'{e["id"]}: script outside planned speaking budget')
        if e['beats'][0]['narration'] != e['title']:
            raise ValueError('Scheduled title and spoken hook differ')
        stamp = datetime.fromisoformat(e['publish_at'])
        if stamp.utcoffset() != stamp.astimezone(ZoneInfo(data['timezone'])).utcoffset() or stamp.hour != 18:
            raise ValueError('Publishing time must match local timezone and slot')
        if stamp.strftime('%Y-%m') != data['month'] or stamp.day != e['day']:
            raise ValueError('Date and calendar day disagree')
        if stamp.weekday() not in (6, 1, 3, 5):
            raise ValueError('Core cadence must be Sunday, Tuesday, Thursday, Saturday')
        if e['status'] != 'scripted_not_rendered_or_published':
            raise ValueError('This planner does not certify rendered or published media')
        if not e['comprehension']['answer'] or not e['comprehension']['critical_error']:
            raise ValueError('Every episode needs a comprehension answer key')
    for key in ('week', 'cluster', 'weekday'):
        groups = {}
        for e in episodes:
            value = datetime.fromisoformat(e['publish_at']).weekday() if key == 'weekday' else e[key]
            groups.setdefault(value, []).append(e)
        if len(groups) != 4 or any(Counter(e['hook_type'] for e in group) != {'Q': 2, 'A': 2} for group in groups.values()):
            raise ValueError(f'Hook balance failed by {key}')
    for cluster in {e['cluster'] for e in episodes}:
        if len({datetime.fromisoformat(e['publish_at']).weekday() for e in episodes if e['cluster'] == cluster}) != 4:
            raise ValueError('Each topic cluster must rotate through all four weekdays')
    support = data['supporting_posts']
    if Counter(s['kind'] for s in support) != {'carousel': 4, 'story': 8}:
        raise ValueError('Four carousels and eight stories required')
    if len({s['id'] for s in support}) != 12:
        raise ValueError('Duplicate supporting-post IDs')
    for s in support:
        if not set(s['episode_ids']) <= set(ids):
            raise ValueError('Supporting post references unknown episode')
        if s['kind'] == 'carousel' and len(s['slides']) != 5:
            raise ValueError('Carousel needs five slides')
        if s['kind'] == 'story' and (len(s['frames']) != 2 or len(s['frames'][0]['options']) != 2):
            raise ValueError('Story needs prompt, two poll options and follow-up frame')
    days = [e['day'] for e in episodes] + [s['day'] for s in support] + [r['day'] for r in data['review_days']]
    if sorted(days) != list(range(1, 31)):
        raise ValueError('Every November day must have exactly one primary calendar item')
    if sum(t['hours'] for t in data['weekly_capacity']) > data['weekly_capacity_hours']:
        raise ValueError('Planned weekly labor exceeds the user’s capacity')
    mature = max(datetime.fromisoformat(e['publish_at']) + timedelta(hours=168) for e in episodes)
    if datetime.fromisoformat(data['final_readout_at']) < mature:
        raise ValueError('Final readout precedes the last seven-day observation')
    return {'status': 'PASS', 'episodes': len(ids), 'creators': len(sources['creators']),
            'community_threads': len(sources['community']), 'research_records': len(sources['evidence']),
            'script_word_range': [min(len(narration(e).split()) for e in episodes), max(len(narration(e).split()) for e in episodes)],
            'balanced_by': ['week', 'topic cluster', 'weekday'], 'planned_weekly_hours': sum(t['hours'] for t in data['weekly_capacity']),
            'audience_tests_conducted': False, 'media_verification': 'Separate production receipt; this planner does not inspect media',
            'scope': 'Structural, source-reference, schedule and content-budget checks only; not scientific approval or audience validation.'}


def md_source(s):
    title = s.get('label') or s.get('title') or s.get('demand_paraphrase') or s['id']
    return f'[{s["id"]}: {title}]({s["url"]})'


def source_links(e, sm):
    return '\n'.join('- ' + md_source(sm[id]) for key in ('creator_ids', 'community_ids', 'evidence_ids') for id in e[key])


def posting_copy(e, sm, platform):
    # Never imply creator endorsement. Scientific/editorial sources stay separate from topic leads.
    source_ids = e['evidence_ids'] or e['community_ids']
    label = 'Research and scope' if e['evidence_ids'] else 'Question that prompted this planning checklist'
    links = '\n'.join(f'{sm[id].get("label", sm[id].get("community", id))}: {sm[id]["url"]}' for id in source_ids)
    tags = '#StrengthTraining #FitnessEducation' if platform == 'YouTube' else '#StrengthTraining #FitnessEducation #RepAndReason'
    return f'{e["caption"]}\n\n{label}:\n{links}\n\n{tags}'


def calendar_md(data):
    lines = ['# November 2026 content calendar', '',
             'Proposed schedule • America/New_York • 18:00 local • no posts have been scheduled or published.', '',
             'Four original videos per week, each cross-posted to Shorts and Reels. Q = question-led opening; A = answer-led opening. The comparison is observational, not a randomized platform A/B test.', '',
             '| Date | Core video | Opening | Audience problem |', '| --- | --- | --- | --- |']
    for e in data['episodes']:
        date = datetime.fromisoformat(e['publish_at']).strftime('%a %b %d')
        lines.append(f'| {date} | [{e["id"]} · {e["title"]}](SCRIPTS.md#{e["id"].lower()}) | {e["hook_type"]} | {e["cluster"]} |')
    lines += ['', '## Supporting content', '', '| Date | Format | Ready copy |', '| --- | --- | --- |']
    for s in data['supporting_posts']:
        lines.append(f'| Nov {s["day"]} | {s["kind"]} | [{s["id"]} · {s["title"]}](SUPPORTING_POSTS.md#{s["id"].lower()}) |')
    lines += ['', '## Production and review rhythm', '',
              '- Batch the next four scripts and sources on Friday; render unattended, then review complete exports Saturday. Final narration is required before locking timings.',
              '- At each publication: preview the exact export in each uploader, verify captions and sources, then record the actual URL and timestamp.',
              '- At +24 hours: capture a diagnostic snapshot. At +168 hours: capture the fixed seven-day observation, keeping platforms separate.',
              '- November 8, 15, 22 and 29 at 20:00: review available mature episodes, missing data, questions and actual labor. Do not move the success hurdles.',
              '- November 29: finish the labor and correction review. November 30: provisional decision; only N01–N13 are seven days old at 18:00.',
              '- December 5 at 18:00: N16 reaches seven days. Make the full-cohort decision after exports are available; retrieval may be delayed but the reporting interval must remain the first seven days.',
              '- If evidence is insufficient, one documented 14-day extension ends December 19. Do not repeatedly reset the pilot.', '',
              'The posting slot is a convenience, not a researched best time. Importing the ICS creates local planning events; it does not schedule social uploads.', '',
              '## Weekly hands-on budget', '', '| Work | Planned hours |', '| --- | ---: |']
    lines += [f'| {t["task"]} | {t["hours"]:g} |' for t in data['weekly_capacity']]
    lines += [f'| **Total ceiling** | **{data["weekly_capacity_hours"]}** |', '',
              'These are allocations, not measured productivity. Record setup separately, count all rework, and separate unattended rendering from hands-on work. If the cap is exceeded, simplify optional support/decorative work once and measure again.']
    return '\n'.join(lines).rstrip() + '\n'


def scripts_md(data, sm):
    lines = ['# Sixteen original video scripts', '',
             'Authored scripts and visual briefs. Current N-series exports, exact durations and pending review are documented in [the production guide](../../docs/MONTH_ONE_V2_PRODUCTION.md). The old M-series exports contain different scripts.', '',
             'Original planning estimate: 30–40 seconds at 150 words/minute. The approved voice produced 26.27–32.67-second exports; the documented prelaunch working target is 25–35 seconds. Per-script estimates below remain the original planning estimates, not measured audio. Keep the first visual legible immediately, before any logo. Six beats are semantic transitions, not rigid second marks. Use full spoken captions, not only headlines.', '']
    for e in data['episodes']:
        words = len(narration(e).split())
        lines += [f'<a id="{e["id"].lower()}"></a>', f'## {e["id"]} · {e["title"]}', '',
                  f'**November {e["day"]}, 18:00 ET · {e["cluster"]} · {e["hook_type"]} opening · {words} words / about {words/2.5:.0f} seconds**', '',
                  '**Why this topic:** ' + e['why_this_topic'], '', '**Exact narration**', '', narration(e), '',
                  '**Visual sequence**', '']
        lines += [f'{i}. **{b["role"].capitalize()}:** {b["visual"]}' for i, b in enumerate(e['beats'], 1)]
        lines += ['', '**YouTube title:** ' + e['title'], '', '**YouTube description**', '', posting_copy(e, sm, 'YouTube'), '',
                  '**Instagram caption**', '', posting_copy(e, sm, 'Instagram'), '',
                  '**Unscheduled alternative opening:** ' + e['alternate_hook_not_scheduled'], '',
                  '**Comprehension key:** ' + e['comprehension']['answer'], '',
                  '**Critical misunderstanding:** ' + e['comprehension']['critical_error'], '',
                  '**Production reuse:** ' + e['reuse_note'], '', '**Topic leads and research**', '', source_links(e, sm), '']
    return '\n'.join(lines).rstrip() + '\n'


def supporting_md(data, sm):
    eps = {e['id']: e for e in data['episodes']}
    lines = ['# Supporting-post copy', '', 'Four five-panel carousels and eight two-frame stories. Copy is complete; image exports are in [the production package](../../docs/MONTH_ONE_V2_PRODUCTION.md). Native stickers must be added manually before posting. These posts support the pilot and are not independent randomized experiments.', '']
    for s in data['supporting_posts']:
        lines += [f'<a id="{s["id"].lower()}"></a>', f'## {s["id"]} · November {s["day"]} · {s["title"]}', '']
        if s['kind'] == 'carousel':
            lines += [f'{i}. {text}' for i, text in enumerate(s['slides'], 1)]
            lines += ['', '**Caption:** ' + s['caption']]
        else:
            lines += ['**Frame 1:** ' + s['frames'][0]['text'], '**Native poll options:** ' + ' / '.join(s['frames'][0]['options']), '', '**Frame 2:** ' + s['frames'][1]['text'], '', 'Add the native poll manually in the uploader; a rendered image is not an interactive poll. Do not label the follow-up as audience results.']
        evidence = sorted({id for ep_id in s['episode_ids'] for id in eps[ep_id]['evidence_ids']})
        lines += ['', 'Companion videos: ' + ', '.join(s['episode_ids']) + '.', '', 'Source notes for caption/review:']
        lines += ['- ' + md_source(sm[id]) for id in evidence] if evidence else ['- Original planning checklist; see companion episode demand links.']
        lines += ['']
    return '\n'.join(lines).rstrip() + '\n'


def research_md(sources, data):
    lines = ['# Creator and community source map', '', f'Checked {sources["checked_at"]}. A purposive research sample, not a representative survey or evidence of demand for this channel.', '',
             'Creator sources identify topics and visible packaging; independent research supports factual answers. We did not copy scripts, footage, thumbnails, paid programs or a creator’s voice.', '',
             '## Creator examples', '', '| Source | Published | Views at check | Observed angle → original adaptation |', '| --- | --- | ---: | --- |']
    for s in sources['creators']:
        count = f'{s["views_snapshot"]:,}' if s['views_snapshot'] is not None else 'Not verified'
        reference = md_source(s).replace('|', '\\|')
        lines.append(f'| {reference} · {s["channel"]} | {s["published"] or "Not verified"} | {count} | {s["observed_packaging"]} {s["original_adaptation"]} |')
    lines += ['', 'Counts are lifetime snapshots, not recent velocity or a forecast. C01–C05 were checked on their primary YouTube pages; metadata/descriptions are not a full-video visual audit. C06 is a title-only indexed reference. The sample includes long-form source material; no claim is made about its Shorts retention.', '',
              '## Community question register', '', '| ID / community | Post date | Net score snapshot | Question paraphrase |', '| --- | --- | ---: | --- |']
    for s in sources['community']:
        score = str(s['post_net_score_snapshot']) if s['post_net_score_snapshot'] is not None else 'Not used / unknown'
        lines.append(f'| [{s["id"]} · {s["community"]}]({s["url"]}) | {s["published"] or "Unverified"} | {score} | {s["demand_paraphrase"]} |')
    lines += ['', 'Scores are net votes captured by the search index, not verified current reach. The R03 question is inside a daily thread; parent-thread votes are deliberately not assigned to it. R02 and R24 dates are unverified. Older threads establish recurrence leads only; they are not presented as new trends.', '',
              '## Scientific basis and limits', '']
    for s in sources['evidence']:
        lines += ['- ' + md_source(s) + f' — {s["design"]}. {s["supported_summary"]} **Boundary:** {s["claim_boundary"]}']
    lines += ['', '## Episode traceability', '', '| Episode | Creator lead | Community question | Research / editorial scope |', '| --- | --- | --- | --- |']
    sm = source_map(sources)
    for e in data['episodes']:
        cells = [' '.join(f'[{id}]({sm[id]["url"]})' for id in e[key]) for key in ('creator_ids', 'community_ids', 'evidence_ids')]
        lines.append(f'| {e["id"]} | {cells[0]} | {cells[1]} | {cells[2] or "Original editorial checklist; no physiological prescription"} |')
    lines += ['', 'N12 uses damage research as background for a clearly labeled editorial inference. It does not claim that the cited trial validated a soreness test. N06, N07, N13 and N16 are planning/logging workflows; their creator links are adjacent topic leads, not claims that those creators taught the exact checklist.', '',
              '## Selection and gaps', '', 'The chosen topics meet a practical constraint, offer a concrete visual, and have either bounded research support or an explicitly editorial answer. This is an editorial rubric, not a predictive virality score. We deferred injury diagnosis, steroid controversy, universal exercise rankings and supplement promises; they are outside this pilot’s focus.', '']
    lines += ['- ' + x for x in sources['method']['limits']]
    lines += ['', 'Full source metadata, access limits, exclusions and query families are preserved in [the JSON register](../../research/month-one-demand-v2.json).']
    return '\n'.join(lines).rstrip() + '\n'


def ics_escape(text):
    return text.replace('\\', '\\\\').replace('\n', '\\n').replace(';', '\\;').replace(',', '\\,')


def fold_ics(line):
    # RFC 5545 limit is octets, not Unicode characters; never split a codepoint.
    out = []; current = ''; count = 0
    for char in line:
        n = len(char.encode('utf-8'))
        if count + n > 75:
            out.append(current); current = ' '; count = 1
        current += char; count += n
    return '\r\n'.join(out + [current])


def make_ics(data):
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Rep and Reason//Demand Calendar V2//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:Rep and Reason — proposed November pilot']
    items = []
    for e in data['episodes']:
        stamp = datetime.fromisoformat(e['publish_at'])
        detail = f'Proposed Shorts + Reels post. {e["id"]}; {e["hook_type"]} opening. Exact script: content/month-one-v2/SCRIPTS.md. Diagnostic +24h: {(stamp+timedelta(hours=24)).isoformat()}. Seven-day snapshot: {(stamp+timedelta(hours=168)).isoformat()}. Not scheduled on either platform.'
        items.append((e['id'], stamp, 30, e['title'], detail))
    for s in data['supporting_posts']:
        items.append((s['id'], datetime.fromisoformat(s['publish_at']), 15, s['kind'].capitalize() + ': ' + s['title'], 'Proposed Instagram support post. Copy: content/month-one-v2/SUPPORTING_POSTS.md. Native stickers are manual.'))
    for day in (8, 15, 22, 29):
        items.append((f'REVIEW-{day}', datetime(2026, 11, day, 20, tzinfo=ZoneInfo(data['timezone'])), 45, 'Weekly pilot review and labor log', 'Review available mature snapshots, useful responses and actual hands-on time. Keep thresholds unchanged.'))
    items.append(('INTERIM', datetime(2026, 11, 30, 18, tzinfo=ZoneInfo(data['timezone'])), 60, 'Provisional month-end review', 'Only N01–N13 are seven days old. Full-cohort review is December 5.'))
    items.append(('FINAL', datetime.fromisoformat(data['final_readout_at']), 60, 'Full-cohort go / iterate / no-go review', 'Use first-seven-day exports, useful-response coding, V2 comprehension checks and measured labor. Missing evidence stays missing.'))
    for id, start, minutes, title, description in sorted(items, key=lambda x: x[1]):
        utc = start.astimezone(ZoneInfo('UTC'))
        lines += ['BEGIN:VEVENT', f'UID:{id.lower()}-202611-v2@rep-and-reason.local', 'DTSTAMP:20261021T160000Z',
                  'DTSTART:' + utc.strftime('%Y%m%dT%H%M%SZ'), 'DTEND:' + (utc + timedelta(minutes=minutes)).strftime('%Y%m%dT%H%M%SZ'),
                  'SUMMARY:' + ics_escape(title), 'DESCRIPTION:' + ics_escape(description), 'STATUS:TENTATIVE', 'TRANSP:TRANSPARENT', 'END:VEVENT']
    lines += ['END:VCALENDAR']
    return '\r\n'.join(fold_ics(line) for line in lines) + '\r\n'


def make_html(data, sources, plan):
    esc = html.escape
    sm = source_map(sources)
    posts = {p['day']: p for p in data['episodes'] + data['supporting_posts']}
    days = []
    for day in range(1, 31):
        p = posts.get(day)
        if p:
            kind = 'video' if 'beats' in p else p['kind']
            days.append(f'<a class="day {kind}" href="#{p["id"]}"><span class="date">{day:02}</span><small>{kind} · {p["id"]}</small><strong>{esc(p["title"])}</strong></a>')
        else:
            r = next(r for r in data['review_days'] if r['day'] == day)
            days.append(f'<a class="day review" href="#experiments"><span class="date">{day:02}</span><small>review</small><strong>{esc(r["title"])}</strong></a>')
    cards = []
    for e in data['episodes']:
        links = ' '.join(f'<a href="{esc(sm[id]["url"])}" target="_blank" rel="noopener">{id}</a>' for field in ('creator_ids', 'community_ids', 'evidence_ids') for id in e[field])
        visuals = ''.join(f'<li><b>{esc(b["role"].capitalize())}.</b> {esc(b["visual"])}</li>' for b in e['beats'])
        cards.append(f'''<details id="{e['id']}" class="brief" data-week="{e['week']}" data-cluster="{e['cluster']}"><summary><span class="meta">{e['id']} · NOV {e['day']} · {e['hook_type']} OPENING · {e['cluster'].upper()}</span><h3>{esc(e['title'])}</h3><span class="hint">Read script, visual brief and sources ↗</span></summary><div class="body"><p class="why">{esc(e['why_this_topic'])}</p><h4>Exact narration</h4><p class="script">{esc(narration(e))}</p><h4>Visual sequence</h4><ol>{visuals}</ol><h4>Posting caption</h4><p>{esc(e['caption'])}</p><h4>Review boundary</h4><p>{esc(e['comprehension']['critical_error'])}</p><p class="sources">Topic leads + research: {links}</p><p class="muted">{esc(e['reuse_note'])} Current narrated media and remaining review are documented in the production guide.</p></div></details>''')
    support = []
    for s in data['supporting_posts']:
        copy = ''.join('<li>' + esc(x) + '</li>' for x in s['slides']) if s['kind'] == 'carousel' else ''.join('<li>' + esc(f['text']) + ('<br><small>Poll: ' + esc(' / '.join(f['options'])) + '</small>' if 'options' in f else '') + '</li>' for f in s['frames'])
        support.append(f'<details id="{s["id"]}" class="brief support"><summary><span class="meta">{s["id"]} · NOV {s["day"]} · {s["kind"].upper()}</span><h3>{esc(s["title"])}</h3></summary><div class="body"><ol>{copy}</ol><p>{esc(s.get("caption", "Add the native poll in Instagram. Follow-up is educational copy, not a reported audience result."))}</p></div></details>')
    creator_items = ''.join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["channel"])}</a><p>{esc(s["title"])}</p><small>{f"{s['views_snapshot']:,} lifetime views at check" if s["views_snapshot"] else "Title-only indexed reference"} · {s["published"] or "date unverified"}</small></li>' for s in sources['creators'])
    template = (ROOT / 'tools/calendar/review_template.html').read_text()
    values = dict(DAYS=''.join(days), EPISODES=''.join(cards), SUPPORT=''.join(support), CREATORS=creator_items,
                  SOURCE_COUNTS=f'{len(sources["creators"])} creator assets · {len(sources["community"])} community threads · {len(sources["evidence"])} research records')
    for key, value in values.items():
        template = template.replace('{{' + key + '}}', value)
    return template


def generated_files(data, sources, plan):
    sm = source_map(sources)
    return {
        ROOT / 'content/month-one-v2/CALENDAR.md': calendar_md(data),
        ROOT / 'content/month-one-v2/SCRIPTS.md': scripts_md(data, sm),
        ROOT / 'content/month-one-v2/SUPPORTING_POSTS.md': supporting_md(data, sm),
        ROOT / 'content/month-one-v2/SOURCE_MAP.md': research_md(sources, data),
        ROOT / 'content/month-one-v2/calendar.ics': make_ics(data),
        ROOT / 'examples/month-one-v2/index.html': make_html(data, sources, plan),
        ROOT / 'examples/month-one-v2/validation.json': json.dumps(validate(data, sources, plan), indent=2) + '\n',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Validate and reject stale generated artifacts without writing')
    args = parser.parse_args()
    data, sources, plan = load()
    report = validate(data, sources, plan)
    for path, text in generated_files(data, sources, plan).items():
        payload = text.encode('utf-8')
        if args.check:
            if not path.exists() or path.read_bytes() != payload:
                raise SystemExit(f'Stale generated output: {path.relative_to(ROOT)}')
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
