"""Evaluate real B-series observations; empty inputs remain insufficient evidence."""
import argparse,json
from pathlib import Path
from month_one_metrics import analyze,descriptive_groups
from month_one_core import ROOT

def evaluate(rows,ops,plan,content):
 ops=dict(ops);batches=ops.get('representative_production_batches',[])
 if not isinstance(batches,list):raise ValueError('Production batches must be a list')
 for b in batches:
  if not isinstance(b.get('core_videos_created_or_substantially_reworked'),int) or b['core_videos_created_or_substantially_reworked']<4 or not b.get('source_labor_log'):
   raise ValueError('Each representative batch needs at least four core videos and a labor-log reference')
 ops['weekly_operator_hours']=[b['hands_on_hours'] for b in batches]
 result=analyze(rows,ops,plan)
 if len(batches)<plan['production_weeks_required']:
  result['missing'].append('Two representative four-video production batches have not been measured; publishing prebuilt media is not production evidence')
  result['decision']='INSUFFICIENT_EVIDENCE'
 result['descriptive_comparisons']=descriptive_groups(rows,content,plan)
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--series',choices=['v3','v5'],default='v3');p.add_argument('--observations',type=Path);p.add_argument('--operations',type=Path);args=p.parse_args()
 args.observations=args.observations or ROOT/f'measurement/month-one-{args.series}-observations.json';args.operations=args.operations or ROOT/f'measurement/month-one-{args.series}-operations.json'
 plan=json.loads((ROOT/f'experiments/month-one-{args.series}.json').read_text());content=json.loads((ROOT/plan['content']).read_text())
 print(json.dumps(evaluate(json.loads(args.observations.read_text()),json.loads(args.operations.read_text()),plan,content),indent=2))
if __name__=='__main__':main()
