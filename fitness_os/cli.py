from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from .common import OSFailure, read_json, write_json, identifier, fingerprint
from .catalog import validate, pilot_paths, load_pilot
from .store import Store
from .experiments import analyze, sample_size, current_protocol, assert_screening_ready
from .commerce import verify_event, import_event
from .metrics import import_csv, observations
from .economics import scenario
from .captions import import_captions
from .tasks import packet, ROLES
from .pipeline import build, build_all, check_bundle, import_audio, approve, release, gallery


def parser():
    p=argparse.ArgumentParser(description="Project Fitness: research → reviewed content → measured experiments")
    p.add_argument("--root",default=os.getenv("FITNESS_OS_ROOT","."))
    commands=p.add_subparsers(dest="command",required=True)
    for name in ("init","check","status","jobs"):
        commands.add_parser(name)
    r=commands.add_parser("render");r.add_argument("pilot",nargs="?");r.add_argument("--variant",default="A");r.add_argument("--all",action="store_true");r.add_argument("--mode",choices=["preview","recorded"],default="preview");r.add_argument("--workers",type=int,default=2)
    r=commands.add_parser("gallery");r.add_argument("--mode",choices=["preview","recorded"],default="preview")
    b=commands.add_parser("check-bundle");b.add_argument("path")
    a=commands.add_parser("audio");a.add_argument("pilot");a.add_argument("beat");a.add_argument("path");a.add_argument("--reviewer",required=True)
    a=commands.add_parser("captions");a.add_argument("pilot");a.add_argument("variant");a.add_argument("path");a.add_argument("--reviewer",required=True)
    a=commands.add_parser("approve");a.add_argument("path");a.add_argument("--reviewer",required=True);a.add_argument("--checks",required=True);a.add_argument("--note",required=True)
    a=commands.add_parser("release");a.add_argument("path")
    b=commands.add_parser("budget");b.add_argument("provider");b.add_argument("--ceiling-cents",type=int,required=True);b.add_argument("--concurrency",type=int,default=1)
    j=commands.add_parser("reserve");j.add_argument("provider");j.add_argument("content_id");j.add_argument("input_file");j.add_argument("--estimated-cents",type=int,required=True)
    j=commands.add_parser("start-job");j.add_argument("job_id")
    j=commands.add_parser("reconcile");j.add_argument("job_id");j.add_argument("status",choices=["unknown","succeeded","failed","cancelled"]);j.add_argument("--request-id");j.add_argument("--actual-cents",type=int);j.add_argument("--result")
    e=commands.add_parser("experiment");sub=e.add_subparsers(dest="action",required=True)
    for name in ("register","analyze","stop-enrollment","close"):
        q=sub.add_parser(name);q.add_argument("id")
    q=sub.add_parser("assign");q.add_argument("id");q.add_argument("participant")
    q=sub.add_parser("respond");q.add_argument("id");q.add_argument("participant");q.add_argument("--correct",type=int,required=True);q.add_argument("--critical-error",type=int,choices=[0,1],required=True);q.add_argument("--trust",type=int,required=True);q.add_argument("--useful",type=int,required=True)
    q=commands.add_parser("power");q.add_argument("--baseline",type=float,required=True);q.add_argument("--lift",type=float,required=True);q.add_argument("--comparisons",type=int,default=1)
    q=commands.add_parser("commerce-import");q.add_argument("body");q.add_argument("signature_file");q.add_argument("--secret-env",default="STRIPE_WEBHOOK_SECRET")
    q=commands.add_parser("metrics-import");q.add_argument("path")
    commands.add_parser("metrics-report")
    q=commands.add_parser("economics");q.add_argument("path")
    q=commands.add_parser("task-packet");q.add_argument("pilot");q.add_argument("--role",choices=ROLES,required=True)
    return p


def run(args):
    root=Path(args.root).resolve()
    command=args.command
    if command=="init":
        Store(root,create=True)
        return {"status":"initialized","paid_execution":"disabled; ledger only","public_upload":"not implemented; reviewed export only"}
    if command=="check":
        return validate(root)
    if command=="status":
        return {"pilots":[{"id":read_json(p)["id"],"status":read_json(p)["status"]} for p in pilot_paths(root)],"research":read_json(root/"research/workstreams.json"),"runtime_initialized":(root/".local/state.sqlite3").exists()}
    if command=="render":
        result=validate(root)
        if not result["valid"]:
            raise OSFailure("; ".join(result["errors"]))
        if args.all:
            return build_all(root,args.workers,args.mode)
        if not args.pilot:
            raise OSFailure("Specify a pilot or --all")
        return build(root,args.pilot,args.variant,args.mode)
    if command=="check-bundle":return check_bundle(root,args.path)
    if command=="gallery":return gallery(root,args.mode)
    if command=="audio":return import_audio(root,args.pilot,args.beat,args.path,args.reviewer)
    if command=="captions":return import_captions(root,args.pilot,args.variant,args.path,args.reviewer)
    if command=="approve":return approve(root,args.path,args.reviewer,args.checks.split(","),args.note)
    if command=="release":return release(root,args.path)
    if command=="power":return sample_size(args.baseline,args.lift,comparisons=args.comparisons)
    if command=="economics":return scenario(read_json(args.path))
    if command=="metrics-import":return import_csv(root,args.path)
    if command=="metrics-report":return observations(root)
    if command=="task-packet":return packet(root,args.pilot,args.role)
    store=Store(root)
    if command=="commerce-import":
        event=verify_event(Path(args.body).read_bytes(),Path(args.signature_file).read_text().strip(),os.getenv(args.secret_env,""))
        return import_event(store,event)
    if command=="jobs":return store.jobs()
    if command=="budget":store.budget(args.provider,args.ceiling_cents,args.concurrency);return {"status":"configured"}
    if command=="reserve":return store.reserve(args.provider,args.content_id,fingerprint(read_json(args.input_file)),args.estimated_cents)
    if command=="start-job":store.start(args.job_id);return {"status":"running","note":"Ledger reservation only. No external request was submitted."}
    if command=="reconcile":store.reconcile(args.job_id,args.status,args.request_id,args.actual_cents,args.result);return {"status":"recorded"}
    if command=="experiment":
        identifier(args.id)
        if args.action=="register":
            protocol=current_protocol(root,args.id)
            store.register_experiment(protocol);return {"status":"registered","id":args.id}
        if args.action in ("assign","respond"):
            protocol=current_protocol(root,args.id)
            store.assert_protocol(protocol)
            if args.action=="assign":assert_screening_ready(root,protocol)
        if args.action=="assign":return store.assign(args.id,args.participant)
        if args.action=="respond":store.respond(args.id,args.participant,args.correct,args.critical_error,args.trust,args.useful);return {"status":"recorded"}
        if args.action=="analyze":return analyze(store,args.id)
        if args.action=="stop-enrollment":store.stop_enrollment(args.id);return {"status":"followup_only"}
        if args.action=="close":store.close_experiment(args.id);return {"status":"closed"}
    raise OSFailure("Unknown command")


def main():
    args=parser().parse_args()
    try:
        result=run(args)
        print(json.dumps(result,indent=2))
        return 1 if isinstance(result,dict) and result.get("valid") is False else 0
    except (OSFailure,OSError,KeyError) as exc:
        print(json.dumps({"error":str(exc)}),file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
