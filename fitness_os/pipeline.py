from __future__ import annotations
import html
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .common import OSFailure, atomic_write, file_hash, fingerprint, read_json, rooted, utcnow, write_json, identifier
from .catalog import inputs, load_pilot, pilot_paths
from . import render


def effective_inputs(root, pilot_id, variant, mode):
    value = inputs(root, pilot_id, variant, mode)
    value["environment"] = render.environment(root)
    return value


def check_bundle(root, bundle):
    bundle = Path(bundle).resolve()
    if not bundle.is_relative_to(Path(root).resolve() / ".local/builds"):
        raise OSFailure("Bundle must be inside .local/builds")
    manifest = read_json(bundle/"manifest.json")
    actual_inputs = effective_inputs(root, manifest["pilot_id"], manifest["variant"], manifest["mode"])
    if fingerprint(actual_inputs) != manifest["input_hash"]:
        raise OSFailure("Build inputs changed; rebuild before review or release")
    for relative, checksum in manifest["files"].items():
        if file_hash(rooted(bundle, relative)) != checksum:
            raise OSFailure(f"Build artifact changed: {relative}")
    return manifest


def build(root, pilot_id, variant, mode="preview"):
    root=Path(root).resolve()
    data=effective_inputs(root,pilot_id,variant,mode)
    digest=fingerprint(data)
    bundle=root/f".local/builds/{pilot_id}-{variant}-{digest[:16]}"
    if (bundle/"manifest.json").exists():
        check_bundle(root,bundle)
        return {"path": str(bundle), "cached": True}
    bundle.mkdir(parents=True,exist_ok=True)
    durations=render.media(root,bundle,data)
    from .captions import to_vtt, validate_srt
    if data.get("caption_override"):
        corrected = rooted(root, data["caption_override"]["path"]).read_text()
        validate_srt(corrected, sum(durations))
        atomic_write(bundle/"captions.srt", corrected)
    atomic_write(bundle/"captions.vtt", to_vtt((bundle/"captions.srt").read_text()))
    pilot=data["pilot"]
    for i, package in enumerate(pilot["packaging"],1):
        render.thumbnail(root,data["brand"],package["thumbnail_text"],bundle/f"thumbnail-{i}.png",i>1)
    beats={b["id"]:b for b in pilot["beats"]}
    script="\n\n".join(beats[b]["narration"] for b in pilot["variants"][variant])
    atomic_write(bundle/"script.txt",script+"\n")
    write_json(bundle/"inputs.json",data)
    write_json(bundle/"publishing.json",{"pilot_id":pilot_id,"packages":pilot["packaging"],"description":pilot["description"],"status":"draft","channel_id":data["brand"].get("channel_id"),"publish_at":None})
    panels="".join(f'<section><img src="scene-{i:02}.png" alt="{html.escape(beats[b]["heading"])}"><p>{html.escape(beats[b]["narration"])}</p></section>' for i,b in enumerate(pilot["variants"][variant],1))
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(pilot['title'])}</title><style>body{{margin:0;background:#10233e;color:#f7f4ea;font:18px/1.6 system-ui}}main{{max-width:1040px;margin:auto;padding:32px}}h1{{line-height:1.15}}.tag{{color:#b9f227}}video,img{{width:100%;border-radius:12px}}section{{margin:36px 0;padding:18px;background:#192e49;border-radius:16px}}a{{color:#b9f227}}</style><main><p class="tag">PROJECT FITNESS / {html.escape(pilot_id)} / {variant}</p><h1>{html.escape(pilot['title'])}</h1><p>{'Silent storyboard prototype. Narration and editorial review are pending.' if mode=='preview' else 'Recorded review copy. Check captions, evidence, rights and the complete viewing experience.'}</p><video controls preload="metadata" src="video.mp4" poster="scene-01.png"></video><p><a href="script.txt">Narration script</a> · <a href="captions.srt">Draft captions</a></p>{panels}</main></html>'''
    atomic_write(bundle/"index.html",page)
    files={p.name:file_hash(p) for p in sorted(bundle.iterdir()) if p.is_file() and p.name not in ("manifest.json","approval.json")}
    write_json(bundle/"manifest.json",{"schema_version":1,"pilot_id":pilot_id,"variant":variant,"mode":mode,"input_hash":digest,"created_at":utcnow(),"duration_seconds":sum(durations),"files":files,"caption_timing":"imported correction; final viewing review required" if data.get("caption_override") else "estimated within each beat; requires manual review","publication_ready":False})
    return {"path":str(bundle),"cached":False}


def build_all(root, workers=2, mode="preview"):
    if workers <1 or workers>4:
        raise OSFailure("Render workers must be 1–4")
    jobs=[]
    for path in pilot_paths(root):
        p=read_json(path)
        jobs.extend((p["id"],v) for v in p["variants"])
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda pair:build(root,*pair,mode),jobs))


def gallery(root, mode="preview"):
    root = Path(root).resolve()
    selected = []
    for path in pilot_paths(root):
        pilot = read_json(path)
        for variant in pilot["variants"]:
            digest = fingerprint(effective_inputs(root, pilot["id"], variant, mode))
            bundle = root/f".local/builds/{pilot['id']}-{variant}-{digest[:16]}"
            manifest = check_bundle(root, bundle)
            selected.append((pilot, variant, bundle, manifest))
    review_id = fingerprint([m for _,_,_,m in selected])[:16]
    destination = root/f".local/reviews/{review_id}"
    destination.mkdir(parents=True, exist_ok=True)
    panels = []
    for pilot, variant, bundle, manifest in selected:
        relative = f"{pilot['id']}-{variant}"
        target = destination/relative
        if target.exists():
            for filename, checksum in manifest["files"].items():
                if file_hash(rooted(target, filename)) != checksum:
                    raise OSFailure("Existing review export has changed; retain it separately and export again")
        else:
            shutil.copytree(bundle, target)
        label = "Decision before evidence" if variant == "A" else "Evidence before decision"
        panels.append(f'<article><p class="eyebrow">{html.escape(pilot["id"])} / VARIANT {variant}</p><h2>{html.escape(pilot["title"])}</h2><p>{label} · {round(manifest["duration_seconds"])} seconds</p><video controls preload="metadata" poster="{relative}/scene-02.png" src="{relative}/video.mp4"></video><p><a href="{relative}/index.html">Full storyboard and script</a> · <a href="{relative}/captions.srt">Caption draft</a></p></article>')
    notice = "Six silent prototypes. Read the scripts alongside the cards; narration and editorial review are pending." if mode == "preview" else "Narrated review copies. These files are not evidence of release approval or completed audience testing."
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DEX · Pilot review</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#10233e;color:#f7f4ea;font:16px/1.55 system-ui}}main{{max-width:1400px;margin:auto;padding:48px 28px}}.eyebrow{{font-size:13px;letter-spacing:.14em;color:#b9f227;font-weight:750}}h1{{font-size:clamp(40px,6vw,76px);line-height:1.05;margin:20px 0}}header{{max-width:880px;margin-bottom:40px}}.notice{{padding:18px 22px;border-left:4px solid #b9f227;background:#192e49}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}}article{{background:#192e49;padding:24px;border-radius:16px}}h2{{font-size:23px;line-height:1.25;min-height:60px}}video{{width:100%;border-radius:10px}}a{{color:#b9f227}}footer{{margin-top:36px;max-width:850px;color:#c4cdd9}}@media(max-width:760px){{.grid{{grid-template-columns:1fr}}h2{{min-height:0}}}}</style><main><header><div class="eyebrow">PROJECT FITNESS / DEX</div><h1>One decision.<br>Two ways to explain it.</h1><p>Know why. Train better.</p><p class="notice">{notice}</p><p>Compare A and B within the same topic. They use the same words, cards and estimated duration; the decision/example block moves relative to the evidence. Topic preference and YouTube packaging are separate questions.</p></header><div class="grid">{''.join(panels)}</div><footer>Review the reasoning, evidence limits and useful next action first. These short prototypes do not test final mascot animation, recording quality or a long-form publishing cadence. No viewers have been assigned and no winning format is claimed.</footer></main></html>'''
    atomic_write(destination/"index.html", page)
    write_json(destination/"review_manifest.json", {"review_id":review_id,"mode":mode,"builds":[{"pilot":p["id"],"variant":v,"input_hash":m["input_hash"]} for p,v,b,m in selected]})
    return {"path":str(destination/"index.html"),"mode":mode,"variants":len(selected)}


def import_audio(root,pilot_id,beat_id,path,reviewer):
    if not reviewer.strip():
        raise OSFailure("An accountable reviewer is required")
    pilot=load_pilot(root,pilot_id)
    beats={b["id"]:b for b in pilot["beats"]}
    if beat_id not in beats:
        raise OSFailure("Unknown beat")
    source=Path(path).resolve()
    duration=render.probe_duration(source)
    digest=file_hash(source)
    suffix=source.suffix.lower()
    if suffix not in (".wav",".mp3",".m4a",".aiff",".flac"):
        raise OSFailure("Supported audio: wav, mp3, m4a, aiff, flac")
    dest=Path(root)/f".local/raw_audio/{digest}{suffix}"
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():
        shutil.copyfile(source,dest)
    if file_hash(dest)!=digest:
        raise OSFailure("Retained source checksum mismatch")
    record={"path":str(dest.relative_to(root)),"sha256":digest,"duration":duration,"script_hash":fingerprint(beats[beat_id]["narration"]),"reviewer":reviewer,"at":utcnow()}
    write_json(Path(root)/f".local/audio/{pilot_id}/{identifier(beat_id)}.json",record)
    return record


REVIEW_CHECKS={"evidence","script","visual","audio","captions","rights","packaging"}


def approve(root,bundle,reviewer,checks,note):
    manifest=check_bundle(root,bundle)
    if manifest["mode"]!="recorded":
        raise OSFailure("Silent prototypes cannot be approved for publication")
    if set(checks)!=REVIEW_CHECKS or not reviewer.strip() or len(note.strip())<20:
        raise OSFailure("Record all seven review checks, a reviewer, and a substantive review note")
    brand=read_json(Path(root)/"config/brand.json")
    if not brand.get("channel_id"):
        raise OSFailure("Set the intended channel ID before public-release approval")
    data=read_json(Path(bundle)/"inputs.json")
    if any(c.get("review_status")!="approved" or not c.get("reviewer") for c in data["claims"]):
        raise OSFailure("Every used claim needs documented editorial approval")
    record={"manifest_hash":file_hash(Path(bundle)/"manifest.json"),"reviewer":reviewer,"checks":sorted(checks),"note":note,"at":utcnow(),"channel_id":brand["channel_id"]}
    write_json(Path(bundle)/"approval.json",record)
    return record


def release(root,bundle):
    bundle=Path(bundle)
    manifest=check_bundle(root,bundle)
    approval=read_json(bundle/"approval.json")
    if manifest["mode"]!="recorded" or approval["manifest_hash"]!=file_hash(bundle/"manifest.json"):
        raise OSFailure("Current recorded package does not have matching approval")
    if set(approval["checks"])!=REVIEW_CHECKS:
        raise OSFailure("Approval is incomplete")
    if approval["channel_id"] != read_json(Path(root)/"config/brand.json").get("channel_id"):
        raise OSFailure("Release destination differs from the reviewed channel")
    release_id=f"{manifest['pilot_id']}-{manifest['variant']}-{manifest['input_hash'][:16]}"
    dest=Path(root)/f".local/releases/{release_id}"
    if dest.exists():
        old=read_json(dest/"manifest.json")
        if old!=manifest:
            raise OSFailure("Existing release differs; do not overwrite")
        for relative, checksum in manifest["files"].items():
            if file_hash(rooted(dest, relative)) != checksum:
                raise OSFailure(f"Retained release artifact changed: {relative}")
    else:
        shutil.copytree(bundle,dest)
    return {"release_id":release_id,"path":str(dest),"status":"prepared_not_uploaded","channel_id":approval["channel_id"]}
