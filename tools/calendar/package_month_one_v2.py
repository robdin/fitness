"""Export only the explicit public planning-file allowlist, never local runtime data."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from build_month_one_v2 import ROOT, load, generated_files, validate


def package(output):
    data,sources,plan=load()
    validate(data,sources,plan)
    generated=generated_files(data,sources,plan)
    for path,text in generated.items():
        if path.read_bytes()!=text.encode():
            raise ValueError(f'Stale artifact: {path.relative_to(ROOT)}')
    paths=list(generated)+[ROOT/p for p in [
        'content/month-one-v2/calendar.json','research/month-one-demand-v2.json',
        'experiments/month-one-v2.json','docs/MONTH_ONE_V2.md','docs/MONTH_ONE_V2_PRODUCTION.md','examples/month-one-v2/production-verification.json',
        'measurement/month-one-observations.csv','measurement/month-one-v2-operations.example.json',
        'tools/calendar/build_month_one_v2.py','tools/calendar/review_template.html',
        'tools/calendar/package_month_one_v2.py','tools/video/month_one_metrics.py',
        'tests/test_month_one_v2.py',
    ]]
    output.mkdir(parents=True,exist_ok=True)
    manifest=[]
    payloads={}
    for path in paths:
        relative=path.relative_to(ROOT).as_posix()
        if '.local' in path.relative_to(ROOT).parts or path.is_symlink():
            raise ValueError('Only explicit regular public source files may be packaged')
        payload=path.read_bytes();payloads[relative]=payload
        target=output/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        manifest.append(dict(path=relative,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest()))
    payloads['README.txt']=b'Rep & Reason: demand-led month-one content calendar\n\nOpen examples/month-one-v2/index.html in a browser.\nRead docs/MONTH_ONE_V2.md for the complete protocol.\nThe ICS file contains proposed planning events, not social uploads.\nN-series review media is in the separate November Content Review ZIP. Nothing has been published. Existing M-series media is also separate.\nNo credentials, raw audience records or local provider files are included.\n'
    payloads['manifest.json']=(json.dumps(dict(status='planning_package_not_rendered_media',files=manifest),indent=2)+'\n').encode()
    for name in ('README.txt','manifest.json'):(output/name).write_bytes(payloads[name])
    archive=output.parent/'Rep_and_Reason_Demand_Calendar_V2.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as writer:
        for name,payload in sorted(payloads.items()):writer.writestr(name,payload)
    with zipfile.ZipFile(archive) as reader:
        if reader.testzip() is not None or set(reader.namelist())!=set(payloads):
            raise ValueError('Archive verification failed')
        for name,payload in payloads.items():
            if reader.read(name)!=payload:raise ValueError('Archive content mismatch')
    return dict(archive=str(archive),review=str(output/'examples/month-one-v2/index.html'),files=len(payloads),bytes=archive.stat().st_size,sha256=hashlib.sha256(archive.read_bytes()).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT.parent/'fitness-deliverables/month-one-v2')
    print(json.dumps(package(parser.parse_args().output),indent=2))
