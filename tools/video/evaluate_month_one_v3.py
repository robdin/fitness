"""Evaluate real B-series observations; empty inputs remain insufficient evidence."""
import argparse,json
from pathlib import Path
from month_one_metrics import analyze,descriptive_groups,number
from month_one_core import ROOT
from month_one_evidence import uses_v6_evidence,validate_labor_batches,load_labor_evidence,SCHEMA

def evaluate(rows,ops,plan,content,*,labor_records=None,verified_labor_sources=None):
 ops=dict(ops);batches=ops.get('representative_production_batches',[])
 if not isinstance(batches,list):raise ValueError('Production batches must be a list')
 v6=uses_v6_evidence(plan);evidence_missing=[];audit=[]
 if v6:
  ops['weekly_operator_hours'],evidence_missing,audit=validate_labor_batches(batches,labor_records,verified_labor_sources)
 else:
  for b in batches:
   if not isinstance(b.get('core_videos_created_or_substantially_reworked'),int) or b['core_videos_created_or_substantially_reworked']<4 or not b.get('source_labor_log'):
    raise ValueError('Each representative batch needs at least four core videos and a labor-log reference')
  ops['weekly_operator_hours']=[b['hands_on_hours'] for b in batches]
 result=analyze(rows,ops,plan)
 result['missing'].extend(evidence_missing)
 if len(ops['weekly_operator_hours'])<plan['production_weeks_required']:
  result['missing'].append(f'{plan["production_weeks_required"]} representative four-video production weeks have not been measured; publishing prebuilt media is not production evidence')
 if result['missing']:
  result['decision']='INSUFFICIENT_EVIDENCE'
 result['descriptive_comparisons']=descriptive_groups(rows,content,plan)
 if v6:
  eligible=[r for r in rows if r['platform']=='youtube_shorts' and number(r,'window_hours')==plan['observation_window_hours'] and (number(r,'engaged_views') or 0)>=plan['minimum_engaged_views_per_eligible_video']]
  complete=[r for r in eligible if number(r,'stayed_to_watch_pct') is not None and number(r,'average_percentage_viewed') is not None]
  joint=[r['episode_id'] for r in complete if number(r,'stayed_to_watch_pct')>=plan['median_stayed_to_watch_target_pct'] and number(r,'average_percentage_viewed')>=plan['median_average_percentage_viewed_target_pct']]
  result['joint_attention_diagnostic']={'eligible_episodes':len(eligible),'complete_episodes':len(complete),'passing_both_count':len(joint),'passing_both_episode_ids':joint,'interpretation':'Descriptive only; the frozen separate-median attention gate is unchanged.'}
  result['labor_evidence']={'schema':SCHEMA,'verified_representative_weeks':audit,'note':'Hashes and reconciliation establish record integrity, not independent proof of human activity or completion quality.'}
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--series',choices=['v3','v5','v6'],default='v3');p.add_argument('--observations',type=Path);p.add_argument('--operations',type=Path);args=p.parse_args()
 args.observations=args.observations or ROOT/f'measurement/month-one-{args.series}-observations.json';args.operations=args.operations or ROOT/f'measurement/month-one-{args.series}-operations.json'
 plan=json.loads((ROOT/f'experiments/month-one-{args.series}.json').read_text());content=json.loads((ROOT/plan['content']).read_text())
 ops=json.loads(args.operations.read_text());records=verified=None;missing=[]
 if uses_v6_evidence(plan):records,verified,missing=load_labor_evidence(ops.get('representative_production_batches',[]),ROOT)
 result=evaluate(json.loads(args.observations.read_text()),ops,plan,content,labor_records=records,verified_labor_sources=verified)
 result['missing'].extend(missing)
 if missing:result['decision']='INSUFFICIENT_EVIDENCE'
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
