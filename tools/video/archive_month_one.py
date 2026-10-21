"""Retain a review ZIP and a credential-free production source ZIP."""
import json
import zipfile
from pathlib import Path
from month_one_core import ROOT,digest

def main():
    review=ROOT/'.local/month-one/review';delivery=ROOT.parent/'fitness-deliverables/month-one';delivery.mkdir(parents=True,exist_ok=True)
    review_zip=delivery/'Rep_and_Reason_Month_One_Review.zip'
    with zipfile.ZipFile(review_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(review.rglob('*')):
            if p.is_file():z.write(p,Path('Rep_and_Reason_Month_One')/p.relative_to(review))
    source_zip=delivery/'Rep_and_Reason_Month_One_Sources.zip'
    paths=[]
    for pattern in ['content/month-one/*','research/month-one-sources.json','experiments/month-one-v1.json','measurement/month-one-*','tools/video/*month_one*','tools/video/render_supporting_posts.cjs','content/mvp/time-audit/fonts/*','tests/*month*','docs/MONTH_ONE.md','examples/month-one/*.json','package.json','package-lock.json']:
        paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
    # Allowlist voice artifacts: never bundle arbitrary .local content or credentials.
    voice=ROOT/'.local/month-one/voice'
    for name in ['narration.wav','alignment.json','generation.json']:
        paths.extend(p for p in voice.glob('M*/'+name) if p.is_file())
    paths.extend(p for p in (ROOT/'.local/month-one/audio-qa').rglob('*.json') if p.is_file())
    for name in ['narration.wav','alignment.json','generation.json','revision.json','base.en-asr.json','small.en-asr.json']:
        paths.extend(p for p in (ROOT/'.local/month-one/voice-history').glob('M*/v*/'+name) if p.is_file())
    manifest=[]
    with zipfile.ZipFile(source_zip,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(set(paths)):
            name=str(Path('fitness')/p.relative_to(ROOT));z.write(p,name);manifest.append({'path':name,'sha256':digest(p),'bytes':p.stat().st_size})
        z.writestr('source-manifest.json',json.dumps(manifest,indent=2)+'\n')
        z.writestr('RESTORE.txt','Clone the current fitness repository. Extract only fitness/.local/month-one/voice/ to restore retained voice inputs. Never overwrite newer code without reviewing the snapshot. This archive contains no API key or private profile configuration. Review assets are in the separate Review ZIP.\n')
    receipt={'review_zip':{'path':str(review_zip),'sha256':digest(review_zip),'bytes':review_zip.stat().st_size},'source_zip':{'path':str(source_zip),'sha256':digest(source_zip),'bytes':source_zip.stat().st_size},'source_file_count':len(manifest),'public_upload':False}
    for p in [review_zip,source_zip]:
        with zipfile.ZipFile(p) as z:
            if z.testzip():raise RuntimeError('Archive integrity failure')
            if any('fish.env' in n or 'fish-profile' in n for n in z.namelist()):raise RuntimeError('Credential path in archive')
    (delivery/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
