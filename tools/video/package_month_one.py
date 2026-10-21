"""Build local review hub, calendar, scripts and source-linked platform copy."""
import html
import hashlib
import json
from datetime import date,timedelta
from pathlib import Path
from month_one_core import ROOT,load_episodes,script,digest

def verify_narrated_export(path,episode,treatment):
    receipt=json.loads((path.parent/f'verification-{treatment}.json').read_text())
    if receipt.get('sha256')!=digest(path) or receipt.get('script_sha256')!=hashlib.sha256(script(episode).encode()).hexdigest() or not receipt.get('voice_present'):
        raise RuntimeError(f'{path.name}: stale narrated export; rebuild before packaging')

def main():
    data=json.loads((ROOT/'content/month-one/episodes.json').read_text());eps=data['episodes'];support=json.loads((ROOT/'content/month-one/supporting-posts.json').read_text());sources={s['id']:s for s in json.loads((ROOT/'research/month-one-sources.json').read_text())['sources']}
    out=ROOT/'.local/month-one/review';out.mkdir(parents=True,exist_ok=True);start=date.fromisoformat(data['start_date'])
    def day(n):return (start+timedelta(days=n-1)).isoformat()
    calendar={e['day']:('Short + Reel',e['id'],e['title']) for e in eps}
    calendar.update({c['day']:('IG carousel',c['id'],c['title']) for c in support['carousels']})
    calendar.update({s['day']:('IG Story',s['id'],s['question']) for s in support['stories']})
    calendar[29]=('Review','R01','Export mature 7-day observations and production time')
    calendar[30]=('Decision','R02','Provisional go / iterate / no-go / insufficient evidence')
    md=['# Rep & Reason — month-one calendar','',f"Proposed dates: {day(1)} through {day(30)}. Timezone: America/New_York. No posts are scheduled or published.",'','16 core videos cross-posted to Shorts and Reels, four five-slide carousels, eight story prompts with follow-up frames, two review days. Suggested publishing time: 18:00 local, a consistent working slot rather than an asserted optimal time.','', '| Day | Date | Format | Asset | Topic |','|---|---|---|---|---|']
    for n in range(1,31):
        kind,asset,title=calendar[n];md.append(f'| {n} | {day(n)} | {kind} | {asset} | {title} |')
    md+=['',f'Final full-cohort readout: **{day(35)}**, seven days after the last video. The day-30 readout cannot include seven days of observation for the last three videos.','', 'Weeks 1–3 cover all three pillars. Week 4 contains prebuilt follow-ups; evidence from earlier posts may justify a documented revision. Do not overwrite the original version or pretend the follow-up was a controlled experiment.','', 'See [experiment protocol](../../experiments/month-one-v1.json) and [production guide](../../docs/MONTH_ONE.md).']
    (ROOT/'content/month-one/CALENDAR.md').write_text('\n'.join(md)+'\n')
    scripts=['# Month-one scripts and posting copy','','Generated from episodes.json. Editorial drafts; no publication approval implied.']
    cards=[]
    for e in eps:
        links=[sources[i]['url'] for i in e['source_ids'] if sources[i].get('url')]
        description=e['takeaway']+'\n\n'+e['disclosure']+'\n\n'+e['comment_prompt']
        if links:description+='\n\nSources:\n'+'\n'.join(links)
        description+='\n\nRep & Reason — Know why. Train better.\n#StrengthTraining #FitnessEducation #RepAndReason'
        (out/e['id']).mkdir(exist_ok=True)
        package={'id':e['id'],'proposed_date':day(e['day']),'youtube_title':e['title'],'youtube_description':description,'instagram_caption':description,'comment_prompt':e['comment_prompt'],'cover_text':e['cover'],'public_upload':False,'human_review_pending':True}
        (out/e['id']/'posting-copy.json').write_text(json.dumps(package,indent=2)+'\n')
        scripts+=['',f"## {e['id']} — {e['title']}",'',f"{day(e['day'])} · {e['pillar']} · {len(script(e).split())} words",'',script(e),'','Visual: '+e['visual']+'. Takeaway: '+e['takeaway'],'','Caption / description:','',description,'','Comprehension check: '+e['comprehension']['question'],'','Expected answer: '+e['comprehension']['answer']]
        mp4=out/e['id']/f"{e['id']}-motion.mp4";draft=out/e['id']/f"{e['id']}-motion-silent-draft.mp4";file=mp4 if mp4.exists() else draft
        if mp4.exists():verify_narrated_export(mp4,e,'motion')
        media=f'<video controls preload="none" playsinline poster="{e["id"]}/cover.png" src="{e["id"]}/{file.name}"></video>' if file.exists() else f'<img src="{e["id"]}/cover.png" alt="{html.escape(e["title"])} storyboard">'
        status='Narrated review export' if mp4.exists() else 'Silent visual draft' if draft.exists() else 'Storyboard; video pending'
        cards.append(f'<article id="{e["id"]}"><div class="media">{media}</div><div class="copy"><p class="eyebrow">{day(e["day"])} · {e["id"]} · {e["pillar"]}</p><h2>{html.escape(e["title"])}</h2><p class="status">{status}</p><p>{html.escape(e["takeaway"])}</p><details><summary>Script, evidence & posting copy</summary><p>{html.escape(script(e))}</p><p class="note">{html.escape(e["disclosure"])}</p>'+''.join(f'<p><a href="{u}">Primary source</a></p>' for u in links)+f'<a href="{e["id"]}/posting-copy.json">Posting copy</a> · <a href="{e["id"]}/{e["id"]}.srt">Captions</a><p><b>Viewer check:</b> {html.escape(e["comprehension"]["question"])}</p></details></div></article>')
    (ROOT/'content/month-one/SCRIPTS.md').write_text('\n'.join(scripts)+'\n')
    cal=''.join(f'<a class="day" href="#{calendar[n][1]}"><span>{day(n)[5:]}</span><b>{calendar[n][1]}</b><small>{html.escape(calendar[n][2])}</small></a>' for n in range(1,31))
    supporting=''
    for c in support['carousels']:
        supporting+=f'<section id="{c["id"]}"><h2>{c["id"]} · {html.escape(c["title"])}</h2><div class="strip">'+''.join(f'<a href="supporting/{c["id"]}/{i}.png"><img src="supporting/{c["id"]}/{i}.png" alt="Slide {i}"></a>' for i in range(1,6))+f'</div><p>{html.escape(c["caption"])}</p></section>'
    for s in support['stories']:
        supporting+=f'<section id="{s["id"]}"><h2>{s["id"]} · {html.escape(s["question"])}</h2><div class="strip"><img src="supporting/{s["id"]}/prompt.png" alt="Story prompt"><img src="supporting/{s["id"]}/followup.png" alt="Story follow-up"></div><p>Add native interactive stickers manually. No poll responses have been collected.</p></section>'
    experiments=''
    for treatment,label in [('compact','A · Compact static'),('large','B · Large static'),('motion','C · Large with motion')]:
        for suffix in ['', '-silent-draft']:
            file=out/'M01'/f'M01-{treatment}{suffix}.mp4'
            if file.exists():
                if not suffix:verify_narrated_export(file,eps[0],treatment)
                experiments+=f'<div><h3>{label}</h3><video controls preload="metadata" poster="M01/cover.png" src="M01/{file.name}"></video></div>';break
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rep & Reason · Month One</title><style>
    *{box-sizing:border-box}body{margin:0;background:#091522;color:#f7f4ea;font:17px/1.6 system-ui,sans-serif}main{max-width:1220px;margin:auto;padding:48px 24px}h1{font-size:clamp(42px,7vw,84px);line-height:1.05;max-width:900px;letter-spacing:-.04em}h2{line-height:1.2}a{color:#b9f227}header{padding-bottom:35px;border-bottom:1px solid #385269}.eyebrow{color:#b9f227;text-transform:uppercase;letter-spacing:.1em;font-size:12px}.note{color:#b4c3d1}.summary{display:flex;gap:28px;flex-wrap:wrap}.summary b{font-size:35px;display:block}.calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:8px}.day{background:#172c40;border-radius:8px;padding:12px;text-decoration:none;display:flex;flex-direction:column}.day span{color:#b4c3d1;font-size:12px}.day small{color:#f7f4ea;font-size:12px}.day b{font-size:19px}article{display:grid;grid-template-columns:300px 1fr;gap:36px;padding:32px 0;border-bottom:1px solid #385269}.media img,.media video{width:100%;border-radius:12px}.copy{padding:16px 0}.status{display:inline-block;border:1px solid #385269;border-radius:30px;padding:5px 14px;font-size:13px}.strip{display:flex;gap:12px;overflow-x:auto}.strip img{height:260px;border-radius:8px}section{padding:24px 0}summary{cursor:pointer;color:#b9f227}.experiments{display:flex;gap:20px}.experiments>div{flex:1}.experiments video{width:100%;height:540px;aspect-ratio:9/16;object-fit:contain;background:#07111e}.decision{background:#172c40;padding:28px;border-radius:12px}button{background:#b9f227;color:#10233e;border:0;padding:12px 18px;border-radius:8px;font-weight:700;cursor:pointer}@media(max-width:700px){article{grid-template-columns:1fr}.media{max-width:330px;margin:auto}.calendar{grid-template-columns:repeat(3,1fr)}.experiments{overflow-x:auto}.experiments>div{min-width:240px}main{padding:28px 18px}}
    </style><main><header><p class="eyebrow">Rep & Reason / November 2026 / Review package</p><h1>Make the next session<br><span style="color:#b9f227">make more sense.</span></h1><p>A 30-day pilot to test audience interest and sustainable production.</p><div class="summary"><div><b>16</b>core video stories</div><div><b>4</b>carousels</div><div><b>8</b>story prompts</div><div><b>3</b>visual treatments</div></div><p class="note">These are review assets. Nothing has been posted. Audience validation is still to come.</p><nav><a href="#visuals">Visual test</a> · <a href="#calendar">Calendar</a> · <a href="#M01">Watch the episodes</a> · <a href="#decision">Decision rules</a></nav></header>'''
    page+='<section id="visuals"><p class="eyebrow">One script. Matched timing. Three treatments.</p><h2>Make the explanation easier to follow.</h2><p>A/B varies diagram scale and placement. B/C varies motion. No audience winner has been established.</p><div class="experiments">'+experiments+'</div></section>'
    page+='<section id="calendar"><h2>The 30-day calendar</h2><p>Suggested dates and slot: November 1–30, 18:00 America/New_York. Each video goes to both Shorts and Reels. Days 29–30 are review days.</p><div class="calendar">'+cal+'</div></section>'+''.join(cards)+supporting
    page+='''<section id="decision" class="decision"><h2>Go / iterate / no-go / insufficient evidence</h2><p>First collect real seven-day platform snapshots, comprehension checks and hands-on labor. The protocol uses explicit provisional operating hurdles, not alleged algorithm benchmarks.</p><ul><li>Attention: median 60% stayed-to-watch and 70% average percentage viewed among eligible YouTube videos.</li><li>Usefulness: at least five distinct relevant audience responses; at least 80% comprehension pass across ten target viewers.</li><li>Coverage: twelve mature releases, including eight with at least 100 engaged views.</li><li>Sustainability: two measured weeks at or below 12 hands-on hours per week.</li></ul><p>Mixed results call for one bounded revision. Missing evidence is inconclusive. A repeated comprehension error needs repair. Reels is reviewed separately; do not pool unlike metrics.</p><p id="R01">November 29: collect mature observations and review production cost.</p><p id="R02">November 30: provisional decision. December 5: full seven-day readout for all sixteen videos.</p></section><footer><p class="note">Know why. Train better. · Source code, exact scripts and measurement protocol retained in the fitness repository.</p></footer></main></html>'''
    (out/'index.html').write_text(page)
    print(out/'index.html')

if __name__=='__main__':main()
