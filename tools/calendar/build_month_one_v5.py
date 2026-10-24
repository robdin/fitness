"""Validate and compile the Blueprint content calendar; never schedules posts."""
import argparse
import collections
import datetime
import json
from pathlib import Path
from build_month_one_v3 import outputs as base_outputs, source_map

ROOT=Path(__file__).resolve().parents[2]
CONTENT=ROOT/'content/month-one-v5'
def load():
    return tuple(json.loads(p.read_text()) for p in [CONTENT/'calendar.json',ROOT/'research/blueprint-v5/sources.json',ROOT/'experiments/month-one-v5.json'])

def validate(d,s,p):
    ids=[f'BP{i:02}' for i in range(1,17)]
    assert d['episode_ids']==p['episode_ids']==ids
    assert [e['id'] for e in d['episodes']]==ids
    sm=source_map(s)
    assert len(sm)==sum(len(s[k]) for k in ['sources','community','creators'])
    for e in d['episodes']:
        assert [b['role'] for b in e['beats']]==['hook','answer','example','boundary','action','close']
        words=len(' '.join(b['narration'] for b in e['beats']).split())
        assert 45<=words<=85 and e['script_words']==words
        assert all(i in sm for i in e['evidence_ids']+e['community_ids']+e['creator_ids'])
        assert e['comprehension']['critical_error'] and e['alternate_hook_not_scheduled']
        assert datetime.datetime.fromisoformat(e['publish_at']).day==e['day']
    for week in range(1,5):
        assert collections.Counter(e['hook_type'] for e in d['episodes'] if e['week']==week)=={'Q':2,'A':2}
    for weekday in [6,1,3,5]:
        assert collections.Counter(e['hook_type'] for e in d['episodes'] if datetime.datetime.fromisoformat(e['publish_at']).weekday()==weekday)=={'Q':2,'A':2}
    assert {'strength','movement','food','recovery','planning'}=={e['cluster'] for e in d['episodes']}
    assert len(d['supporting_posts'])==12
    assert sorted([e['day'] for e in d['episodes']]+[x['day'] for x in d['supporting_posts']]+[x['day'] for x in d['review_days']])==list(range(1,31))
    assert sum(x['hours'] for x in d['weekly_capacity'])==12
    assert datetime.datetime.fromisoformat(d['final_readout_at'])-max(datetime.datetime.fromisoformat(e['publish_at']) for e in d['episodes'])==datetime.timedelta(days=7)
    for post in d['supporting_posts']:
        assert all(i in ids for i in post['episode_ids'])
        if post['kind']=='carousel':assert len(post['slides'])==5
        else:assert len(post['frames'])==2 and len(post['frames'][0]['options'])==2
    return True

def posting_copy(e,sm,platform):
    lines=[e['caption'],e['cta'],'','Your dream body. Your real life.']
    if e['evidence_ids']:
        lines+=['','Sources and scope:']+[sm[i]['title']+' — '+sm[i]['url'] for i in e['evidence_ids']]
    else:lines+=['','Original editorial checklist; not a study result.']
    lines+=['Scope: '+e['age_scope']]
    if platform=='instagram':lines+=['#BeginnerFitness #FitnessForRealLife']
    return '\n'.join(lines)

def outputs(d,s,p):
    result=base_outputs(d,s,p)
    for name,body in result.items():
        result[name]=body.replace('B-series','Blueprint month').replace('B16','BP16').replace('rr-v3-','blueprint-v5-').replace('Rep and Reason//','Body of our dreams//').replace('rep-and-reason.local','blueprint.local').replace('20261022T160000Z','20261023T160000Z').replace('../../brand/v3/STYLE_GUIDE.md','../../brand/blueprint/STYLE_GUIDE.md').replace('../../research/audience-v3/06_INTEGRATION_AND_TESTING.md','../../experiments/month-one-v5.json')
    result['CALENDAR.md']+='\nBlueprint was selected by the owner. Public name remains undecided. Eight question/answer openings are balanced by week and weekday, not by the broader content pillars. Read group comparisons descriptively.\n'
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    d,s,p=load();validate(d,s,p)
    for name,body in outputs(d,s,p).items():
        target=CONTENT/name
        if args.check:assert target.read_bytes()==body.encode(),'Stale file '+name
        else:target.write_bytes(body.encode())
    print('Blueprint calendar, sources, hook assignment and capacity verified.')
if __name__=='__main__':main()
