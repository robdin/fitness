"""Prepare a hash-bound pilot checklist from actual exports; never uploads or approves."""
import datetime as dt
import html
import json
import shutil
from pathlib import Path
from month_one_core import ROOT, digest
from produce_month_one_v6 import WORKSPACE, episodes, RENDERER
from voice_contract import validate_voice_receipt

PLATFORMS=('youtube_shorts','instagram_reels')

def timestamp(value):
    try:
        result=dt.datetime.fromisoformat(value)
        if result.tzinfo is None:return None
        return result
    except (ValueError,TypeError):return None

def reviewed(reviews,episode_id,sha,kind,platform=None,account_native_id=None):
    matching=[r for r in reviews if r.get('episode_id')==episode_id and r.get('media_sha256')==sha
              and r.get('kind')==kind and r.get('platform')==platform and timestamp(r.get('reviewed_at'))
              and (kind!='native_preview' or (account_native_id and r.get('account_native_id')==account_native_id))]
    if not matching:return False
    latest_time=max(timestamp(r['reviewed_at']) for r in matching)
    latest=[r for r in matching if timestamp(r['reviewed_at'])==latest_time]
    return all(r.get('reviewer') and r.get('notes') and r.get('result')=='pass' for r in latest)

def account_verified(account):
    return bool(isinstance(account,dict) and all(account.get(k) for k in ['native_id','public_url','verified_by','timezone'])
                and timestamp(account.get('verified_at')) and account['public_url'].startswith('https://'))

def status_for(episode_id,sha,ops):
    listening=reviewed(ops.get('reviews',[]),episode_id,sha,'listening')
    platforms={p:{'account_verified':account_verified(ops.get('accounts',{}).get(p)),
                  'native_preview':reviewed(ops.get('reviews',[]),episode_id,sha,'native_preview',p,
                                            (ops.get('accounts',{}).get(p) or {}).get('native_id'))} for p in PLATFORMS}
    return {'listening':listening,'platforms':platforms,
            'release_review_complete':listening and all(all(v.values()) for v in platforms.values())}

def check_current_inputs(episode,file,receipt,renderer,voice_folder):
    timeline=file.parent/'timeline.json'
    if json.loads(timeline.read_text())['episode']!=episode:
        raise ValueError('Current content has not been rendered: '+episode['id'])
    if receipt.get('renderer_sha256')!=digest(renderer) or receipt.get('timeline_sha256')!=digest(timeline):
        raise ValueError('Renderer or timeline changed: '+episode['id'])
    if receipt.get('voice_provenance')!=validate_voice_receipt(episode,voice_folder,**episode['voice_contract']):
        raise ValueError('Narration settings changed: '+episode['id'])

def prepare():
    out=WORKSPACE/'pilot';out.mkdir(exist_ok=True)
    ledger=out/'operations.json'
    if not ledger.exists():shutil.copy2(ROOT/'content/month-one-v6/pilot-operations.template.json',ledger)
    ops=json.loads(ledger.read_text());calendar=json.loads((ROOT/'content/month-one-v6/calendar.json').read_text())
    assert ops['schema']=='bomd-pilot-operations-v1'
    entries=[];current={e['id']:e for e in episodes()}
    for e in [calendar['orientation_asset']]+calendar['episodes']:
        id=e['id'];file=WORKSPACE/'review'/id/f'{id}-motion.mp4';sha=digest(file)
        r=json.loads((file.parent/'verification-motion.json').read_text())
        if r['sha256']!=sha:raise ValueError('Export receipt is stale: '+id)
        check_current_inputs(current[id],file,r,RENDERER,WORKSPACE/'voice'/id)
        entry={'episode_id':id,'title':e['title'],'proposed_publish_at':e.get('publish_at'),
               'media_sha256':sha,'duration_seconds':r['duration'],**status_for(id,sha,ops)}
        actual=[x for x in ops.get('releases',[]) if x.get('episode_id')==id and x.get('media_sha256')==sha]
        entry['actual_releases']=actual
        entries.append(entry)
    report={'schema':'bomd-pilot-manifest-v1','protocol_sha256':digest(ROOT/'experiments/month-one-v6.json'),
            'calendar_sha256':digest(ROOT/'content/month-one-v6/calendar.json'),
            'entries':entries,'metric_export_rehearsal':ops.get('metric_export_rehearsal'),
            'published_by_this_tool':False,'visual_experiment_triggered':False,
            'note':'A checklist, not a platform receipt. Human reviews and account checks are supplied evidence; this tool never fabricates or performs them.'}
    (out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    esc=html.escape
    page=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BOMD pilot review</title><style>body{background:#F3F5F4;color:#173249;font:17px/1.6 system-ui;margin:auto;padding:32px;max-width:1000px}h1{color:#2348C6}article{border-top:1px solid #bbb;padding:24px 0;display:flex;gap:24px}video{width:270px;max-width:100%}a{color:#2348C6}pre{white-space:pre-wrap}@media(max-width:650px){article{display:block}}</style><h1>Your dream body. Your real life.</h1><p>First-week playback review, plus revised BC05. The Blueprint identity is unchanged. No posts have been published by this tool.</p><p><a href="../review/index.html">Full month</a> · <a href="../review/content/month-one-v6/ACCOUNT_ENTRY.html">Profile copy</a> · <a href="../review/docs/MONTH_ONE_V6_PILOT.html">Pilot execution sheet</a> · <a href="manifest.json">Exact files and review status</a></p>']
    for e in entries[:6]:
        id=e['episode_id'];folder='../review/'+id
        page.append(f'<article><video controls playsinline preload="metadata" poster="{folder}/cover.png" src="{folder}/{id}-motion.mp4"></video><div><h2>{id} · {esc(e["title"])}</h2><p>{e["duration_seconds"]:.1f} seconds · Human listening: {"recorded" if e["listening"] else "pending"}</p><p><a href="{folder}/posting-copy.json">Exact posting copy</a></p><p>Listen at normal speed. Check the takeaway, spoken words, caption timing, example readability and source limits. Then preview this export in both native uploaders.</p></div></article>')
    page.append('<p>Reviews persist in operations.json, bound to the exact media hash. Re-running preparation preserves that ledger. Audience comprehension and real recurring labor remain separate measurements.</p></html>')
    (out/'index.html').write_text(''.join(page))
    print(json.dumps({'manifest':str(out/'manifest.json'),'review':str(out/'index.html'),'core_exports':16,
                      'first_week_listening_reviews':sum(e['listening'] for e in entries[:5]),
                      'first_week_release_reviews_complete':sum(e['release_review_complete'] for e in entries[:5]),
                      'native_metric_rehearsal_recorded':ops.get('metric_export_rehearsal') is not None}))

if __name__=='__main__':prepare()
