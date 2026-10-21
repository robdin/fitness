"""Conservative go/no-go support from real, non-overlapping 7-day snapshots."""
import argparse
import csv
import json
import statistics
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FIELDS=['episode_id','platform','published_at','observed_at','window_hours','duration_seconds','views','engaged_views','stayed_to_watch_pct','average_view_duration_seconds','average_percentage_viewed','reach','saves','shares','subscribers_gained','source_export']

def number(row,key):
    value=row.get(key,'')
    if value is None or str(value).strip()=='': return None
    n=float(value)
    if not math.isfinite(n):raise ValueError(f'{key} must be finite')
    if n<0:raise ValueError(f'{key} cannot be negative')
    if key=='stayed_to_watch_pct' and n>100:raise ValueError('Stayed-to-watch must be 0–100')
    return n

def analyze(rows,ops,plan):
    from datetime import datetime
    selected=[];seen=set();known=set(plan.get('episode_ids',[f'M{i:02}' for i in range(1,17)]))
    for row in rows:
        if row['episode_id'] not in known:raise ValueError('Unknown episode ID')
        if row['platform'] not in ['youtube_shorts','instagram_reels']:raise ValueError('Unknown platform')
        for field in FIELDS[4:-1]:number(row,field)
        if number(row,'window_hours')!=plan['observation_window_hours']:continue
        key=(row['episode_id'],row['platform'])
        if key in seen:raise ValueError('Duplicate 7-day snapshot; do not sum overlapping windows')
        seen.add(key)
        if not row.get('source_export'):raise ValueError('An observation needs its source export reference')
        published=datetime.fromisoformat(row['published_at']);observed=datetime.fromisoformat(row['observed_at'])
        if not published.tzinfo or not observed.tzinfo:raise ValueError('Use timezone-aware observation timestamps')
        elapsed=(observed-published).total_seconds()/3600
        if elapsed<plan['observation_window_hours']:raise ValueError('Snapshot is not mature')
        if plan.get('require_reporting_window_label') and row.get('reporting_window')!=f'first_{plan["observation_window_hours"]}_hours':
            raise ValueError('V2 observations require the exact first-seven-day reporting window')
        grace=plan.get('maximum_snapshot_delay_hours')
        if grace is not None and elapsed>plan['observation_window_hours']+grace:
            raise ValueError('Snapshot collected outside the allowed export grace period')
        if row['platform']=='youtube_shorts':selected.append(row)
    eligible=[r for r in selected if (number(r,'engaged_views') or 0)>=plan['minimum_engaged_views_per_eligible_video']]
    complete=[r for r in eligible if number(r,'stayed_to_watch_pct') is not None and number(r,'average_percentage_viewed') is not None]
    missing=[]
    if len(selected)<plan['minimum_released_videos']:missing.append(f'Fewer than {plan["minimum_released_videos"]} mature YouTube releases')
    if len(eligible)<plan['minimum_eligible_youtube_videos']:missing.append(f'Fewer than {plan["minimum_eligible_youtube_videos"]} YouTube videos with at least {plan["minimum_engaged_views_per_eligible_video"]} engaged views')
    if len(complete)!=len(eligible):missing.append('Missing attention metrics on eligible videos')
    checks=ops.get('comprehension_checks');passed=ops.get('comprehension_passes');useful=ops.get('distinct_useful_responses')
    for name,value in [('comprehension_checks',checks),('comprehension_passes',passed),('distinct_useful_responses',useful)]:
        if value is not None and (isinstance(value,bool) or not isinstance(value,int) or value<0):
            raise ValueError(f'{name} must be a nonnegative integer or null')
    if checks is None or checks<plan['minimum_target_viewer_comprehension_checks'] or passed is None:missing.append('Insufficient comprehension checks')
    if useful is None:missing.append('Useful audience responses not reviewed')
    hours=ops.get('weekly_operator_hours',[]);limit=plan['weekly_operator_hours_limit']
    if not isinstance(hours,list) or any(isinstance(h,bool) or not isinstance(h,(int,float)) or not math.isfinite(h) or h<0 for h in hours):
        raise ValueError('Invalid labor hours: require finite nonnegative numbers')
    if limit is None or len(hours)<plan['production_weeks_required']:missing.append('Capacity limit or measured production weeks missing')
    if passed is not None and checks is not None and not 0<=passed<=checks:raise ValueError('Invalid comprehension counts')
    stw=statistics.median(number(r,'stayed_to_watch_pct') for r in complete) if complete else None
    apv=statistics.median(number(r,'average_percentage_viewed') for r in complete) if complete else None
    attention=stw is not None and stw>=plan['median_stayed_to_watch_target_pct'] and apv>=plan['median_average_percentage_viewed_target_pct']
    usefulness=useful is not None and useful>=plan['minimum_distinct_useful_responses']
    comprehension=bool(checks and passed is not None and passed/checks*100>=plan['comprehension_pass_target_pct'])
    weeks=plan['production_weeks_required']
    sustainable=limit is not None and len(hours)>=weeks and max(hours[-weeks:])<=limit
    critical=ops.get('unresolved_recurring_critical_error')
    if critical is not None and not isinstance(critical,bool):raise ValueError('Critical-error review must be boolean or null')
    if not isinstance(ops.get('simplification_attempted',False),bool):raise ValueError('Simplification status must be boolean')
    if critical is None:missing.append('Critical-misunderstanding review missing')
    if missing:decision='INSUFFICIENT_EVIDENCE'
    elif critical:decision='ITERATE'
    elif attention and usefulness and comprehension and sustainable:decision='GO_BOUNDED_MONTH_TWO'
    elif (not attention and not usefulness) or (not sustainable and ops.get('simplification_attempted') is True):decision='NO_GO_CURRENT_FORMAT'
    else:decision='ITERATE'
    return {'decision':decision,'missing':missing,'mature_youtube_episodes':len(selected),'eligible_youtube_episodes':len(eligible),'median_stayed_to_watch_pct':stw,'median_average_percentage_viewed':apv,'gates':{'attention':attention,'usefulness':usefulness,'comprehension':comprehension,'sustainable':sustainable},'note':'Operating decision support, not statistical proof. Reels remains a separate secondary report.'}

def descriptive_groups(rows,content,plan):
    """Call only after analyze validates the input; this is never a causal estimate."""
    results={}
    for factor in ('hook_type','cluster'):
        groups={}
        for ep in content['episodes']:
            groups.setdefault(ep[factor],[]).append(ep['id'])
        results[factor]={}
        for group,ids in groups.items():
            mature=[r for r in rows if r['episode_id'] in ids and r['platform']=='youtube_shorts' and number(r,'window_hours')==plan['observation_window_hours']]
            eligible=[r for r in mature if (number(r,'engaged_views') or 0)>=plan['minimum_engaged_views_per_eligible_video']]
            complete=[r for r in eligible if number(r,'stayed_to_watch_pct') is not None and number(r,'average_percentage_viewed') is not None]
            exposure=[number(r,'engaged_views') for r in mature if number(r,'engaged_views') is not None]
            results[factor][group]={'scheduled':len(ids),'mature':len(mature),'eligible':len(eligible),'complete':len(complete),'engaged_view_range':[min(exposure),max(exposure)] if exposure else None,'median_stayed_to_watch_pct':statistics.median(number(r,'stayed_to_watch_pct') for r in complete) if complete else None,'median_average_percentage_viewed':statistics.median(number(r,'average_percentage_viewed') for r in complete) if complete else None}
    return {'groups':results,'interpretation':'Descriptive only. Topics, traffic, duration and audiences differ; no causal lift, statistical winner or pooled-platform result.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('observations',type=Path);p.add_argument('--operations',type=Path,required=True);p.add_argument('--plan',type=Path,default=ROOT/'experiments/month-one-v1.json');args=p.parse_args()
    with args.observations.open(newline='') as f:rows=list(csv.DictReader(f))
    plan=json.loads(args.plan.read_text())
    result=analyze(rows,json.loads(args.operations.read_text()),plan)
    if plan.get('content'):
        result['descriptive_comparisons']=descriptive_groups(rows,json.loads((ROOT/plan['content']).read_text()),plan)
    print(json.dumps(result,indent=2))
