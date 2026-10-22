"""Validate and compile the B-series calendar from canonical authored JSON."""
import argparse,collections,datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CONTENT=ROOT/'content/month-one-v3'
def load():
 return tuple(json.loads(p.read_text()) for p in [CONTENT/'calendar.json',ROOT/'research/audience-v3/sources.json',ROOT/'experiments/month-one-v3.json'])
def source_map(s):return {r['id']:r for group in ['sources','community','creators'] for r in s[group]}
def validate(d,s,p):
 ids=[f'B{i:02}' for i in range(1,17)];assert d['episode_ids']==p['episode_ids']==ids
 sm=source_map(s);assert len(sm)==sum(len(s[g]) for g in ['sources','community','creators'])
 for e in d['episodes']:
  assert len(e['beats'])==6 and e['title'] and all(b['narration'] for b in e['beats'])
  assert 45<=len(' '.join(b['narration'] for b in e['beats']).split())<=85
  assert all(i in sm for i in e['evidence_ids']+e['community_ids']+e['creator_ids'])
  assert e['comprehension']['critical_error'] and e['alternate_hook_not_scheduled']
  assert datetime.datetime.fromisoformat(e['publish_at']).day==e['day']
 for key in ['week','cluster']:
  for value in {e[key] for e in d['episodes']}:
   assert collections.Counter(e['hook_type'] for e in d['episodes'] if e[key]==value)=={'Q':2,'A':2}
 for weekday in [6,1,3,5]:
  eps=[e for e in d['episodes'] if datetime.datetime.fromisoformat(e['publish_at']).weekday()==weekday]
  assert collections.Counter(e['hook_type'] for e in eps)=={'Q':2,'A':2}
  assert len({e['cluster'] for e in eps})==4
 assert len(d['supporting_posts'])==12
 days=[e['day'] for e in d['episodes']]+[x['day'] for x in d['supporting_posts']]+[x['day'] for x in d['review_days']]
 assert sorted(days)==list(range(1,31))
 assert sum(x['hours'] for x in d['weekly_capacity'])==12
 assert datetime.datetime.fromisoformat(d['final_readout_at'])-max(datetime.datetime.fromisoformat(e['publish_at']) for e in d['episodes'])==datetime.timedelta(days=7)
 for post in d['supporting_posts']:
  assert all(i in ids for i in post['episode_ids'])
  if post['kind']=='carousel':assert len(post['slides'])==5
  else:assert len(post['frames'])==2 and len(post['frames'][0]['options'])==2
 return True

def posting_copy(e,sm,platform):
 lines=[e['caption'],e['cta'],'']
 if e['evidence_ids']:lines+=['Sources and scope:']+[sm[i]['url'] for i in e['evidence_ids']]
 else:lines+=['Original planning or measurement checklist; not a trial result or personal prescription.']
 if platform=='instagram':lines+=['#BeginnerFitness #StrengthTraining #RepAndReason']
 return '\n'.join(lines)

def outputs(d,s,p):
 sm=source_map(s);entries=sorted([(e['day'],e['id'],'Short + Reel',e['title']) for e in d['episodes']]+[(x['day'],x['id'],x['kind'],x['title']) for x in d['supporting_posts']]+[(x['day'],'REVIEW','internal',x['title']) for x in d['review_days']])
 cal=['# November 2026 · beginner content calendar','\nProposed schedule, not scheduled or published. All posts at 18:00 America/New_York (UTC−05:00 on these dates). This is a convenient fixed slot, not a claimed best time. Shift the whole schedule if review delays launch.\n','| Date | ID | Format | Topic |','|---|---|---|---|']+[f'| Nov {day} | {id} | {kind} | {title} |' for day,id,kind,title in entries]
 cal+=['\nDecember 5, 18:00: final seven-day readout for B16. November 30 is interim only. Review 24-hour diagnostics separately from the primary first-168-hour exports.','\n## Weekly hands-on capacity','\nThe user’s limit is 12 hours. These are planned allocations, not measurements. Production of a prebuilt month does not establish future weekly cost.\n']+[f"- {x['task']}: {x['hours']} hours" for x in d['weekly_capacity']]
 cal+=['\n[Testing protocol](../../research/audience-v3/06_INTEGRATION_AND_TESTING.md) · [Scripts](SCRIPTS.md) · [Brand guide](../../brand/v3/STYLE_GUIDE.md)']
 scripts=['# B-series · complete narration and alternate hooks','\nExact canonical narration. Alternates are unscheduled. Research and audience validation are different; comprehension answers below are scoring rubrics, not observed results.\n']
 sources=['# Episode source and claim map','\nCommunity questions indicate a topic, not scientific truth. Source access and population limits are in the research register.\n']
 for e in d['episodes']:
  scripts += [f"## {e['id']} · November {e['day']} · {e['title']}",f"\n{e['hook_type']} opening · {e['cluster']} · {e['script_words']} words.\n",'\n\n'.join(f"**{b['role'].title()}:** {b['narration']}" for b in e['beats']),f"\n**Unscheduled alternative:** {e['alternate_hook_not_scheduled']}\n\n**Posting caption:** {e['caption']}\n\n**Comprehension:** {e['comprehension']['answer']}\n\n**Critical misunderstanding:** {e['comprehension']['critical_error']}\n"]
  sources += [f"## {e['id']} · {e['title']}",e['why_this_topic'],f"\n**Claim type:** {e['claim_type']}. **Limit to preserve:** {e['comprehension']['critical_error']}\n"]
  for label,key in [('Scientific/professional support','evidence_ids'),('Public question leads','community_ids'),('Creator packaging leads','creator_ids')]:
   sources += [f'\n**{label}**\n']+([f"- [{i} · {sm[i].get('title',sm[i].get('label',sm[i].get('question_paraphrase',sm[i].get('demand_paraphrase',i))))}]({sm[i]['url']})" for i in e[key]] or ['None: this portion is an original editorial workflow.'])
 supporting=['# Supporting post copy','\nFour five-panel carousels and eight two-frame stories. Add native poll controls only during upload; these images do not collect responses.\n']
 for x in d['supporting_posts']:
  supporting += [f"## {x['id']} · November {x['day']} · {x['title']}"]
  if x['kind']=='carousel':supporting += [f'{i+1}. {text}' for i,text in enumerate(x['slides'])]+['\n'+x['caption']]
  else:supporting += [f"1. {x['frames'][0]['text']} Poll: {' / '.join(x['frames'][0]['options'])}",f"2. {x['frames'][1]['text']}"]
  supporting += ['']
 def escape(t):return t.replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')
 ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Rep and Reason//B-series planning//EN','CALSCALE:GREGORIAN','METHOD:PUBLISH']
 # UTC events avoid ambiguous or missing timezone definitions; November dates are EST.
 for day,id,kind,title in entries:
  ics += ['BEGIN:VEVENT',f'UID:rr-v3-{day:02}@rep-and-reason.local','DTSTAMP:20261022T160000Z',f'DTSTART:202611{day:02}T230000Z',f'DTEND:202611{day:02}T233000Z','SUMMARY:'+escape(id+' '+title),'DESCRIPTION:'+escape('Planning only; no automatic publication. '+kind),'STATUS:TENTATIVE','END:VEVENT']
 ics+=['BEGIN:VEVENT','UID:rr-v3-final@rep-and-reason.local','DTSTAMP:20261022T160000Z','DTSTART:20261205T230000Z','DTEND:20261205T233000Z','SUMMARY:B-series final seven-day readout','STATUS:TENTATIVE','END:VEVENT','END:VCALENDAR']
 # Fold by UTF-8 octets for interoperable iCalendar import.
 folded=[]
 for line in ics:
  part=''
  for c in line:
   if len((part+c).encode())>74:folded.append(part);part=' '+c
   else:part+=c
  folded.append(part)
 return {'CALENDAR.md':'\n'.join(cal).rstrip()+'\n','SCRIPTS.md':'\n'.join(scripts).rstrip()+'\n','SOURCE_MAP.md':'\n'.join(sources).rstrip()+'\n','SUPPORTING_POSTS.md':'\n'.join(supporting).rstrip()+'\n','calendar.ics':'\r\n'.join(folded)+'\r\n'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,s,plan=load();validate(d,s,plan)
 for name,body in outputs(d,s,plan).items():
  target=CONTENT/name;expected=body.encode()
  if a.check:assert target.read_bytes()==expected,'Stale generated file '+name
  else:target.write_bytes(expected)
 print('B-series calendar, sources, balance, capacity and generated files verified.')
if __name__=='__main__':main()
