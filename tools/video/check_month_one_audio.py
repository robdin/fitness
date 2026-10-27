"""Independent local ASR comparison; differences require review, not regeneration.

Optional dependency: faster-whisper and numpy. The default base.en model must
already be cached: this check never uploads narration or silently downloads it.
--check-inputs uses only the standard library and never imports ASR dependencies.
"""
import argparse
import difflib
import json
import re
import subprocess
from pathlib import Path
from month_one_core import ROOT, load_episodes, script, digest
from voice_contract import validate_voice_receipt

def tokens(text):
    return re.findall(r"[a-z0-9]+",text.lower())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ids',nargs='+');p.add_argument('--model',default='base.en')
    p.add_argument('--series',choices=['v1','v2','v3','v5','v6'],default='v1')
    p.add_argument('--check-inputs',action='store_true',help='Verify selected retained scripts/audio/alignment without ASR, downloads or writes')
    args=p.parse_args()
    if args.series=='v1':
        workspace=ROOT/'.local/month-one';episodes=load_episodes()
    elif args.series=='v2':
        from produce_month_one_v2 import episodes as v2_episodes, WORKSPACE
        workspace=WORKSPACE;episodes=v2_episodes()
    elif args.series=='v3':
        from produce_month_one_v3 import episodes as v3_episodes, WORKSPACE
        workspace=WORKSPACE;episodes=v3_episodes()
    elif args.series=='v5':
        from produce_month_one_v5 import episodes as v5_episodes, WORKSPACE
        workspace=WORKSPACE;episodes=v5_episodes()
    elif args.series=='v6':
        from produce_month_one_v6 import episodes as v6_episodes, WORKSPACE
        workspace=WORKSPACE;episodes=v6_episodes()
    if args.ids:
        unknown=set(args.ids)-{ep['id'] for ep in episodes}
        if unknown:p.error('Unknown IDs: '+', '.join(sorted(unknown)))
        episodes=[ep for ep in episodes if ep['id'] in args.ids]
    expected={}
    if args.series=='v6':
        voice=json.loads((ROOT/'content/month-one-v6/production.json').read_text())['voice']
        expected=dict(expected_model=voice['model'],expected_delivery_tag=voice['delivery_tag'],expected_prosody_speed=voice['prosody_speed'])
    verified=[]
    for ep in episodes:
        verified.append({'id':ep['id'],**validate_voice_receipt(ep,workspace/'voice'/ep['id'],**expected)})
    if args.check_inputs:
        print(json.dumps({'status':'inputs_verified','series':args.series,'count':len(verified),'inputs':verified,
                          'asr_run':False,'provider_requests':0,'human_listening_review':False},indent=2))
        return
    import numpy as np
    from faster_whisper import WhisperModel
    model=WhisperModel(args.model,device='cpu',compute_type='int8',cpu_threads=4,
                      download_root=str(ROOT/'.local/month-one/asr-models'),local_files_only=True)
    out=workspace/'audio-qa'/args.model.replace('/','_');out.mkdir(parents=True,exist_ok=True)
    for ep in episodes:
        path=workspace/'voice'/ep['id']/'narration.wav'
        # Decode with the installed FFmpeg, avoiding a PyAV API/version mismatch.
        raw=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar','16000','-ac','1','-'],check=True,capture_output=True).stdout
        segments,info=model.transcribe(np.frombuffer(raw,dtype=np.float32),language='en',beam_size=5,condition_on_previous_text=False)
        observed=[{'start':s.start,'end':s.end,'text':s.text} for s in segments]
        text=' '.join(s['text'].strip() for s in observed)
        expected_tokens,heard_tokens=tokens(script(ep)),tokens(text)
        differences=[]
        for tag,a,b,c,d in difflib.SequenceMatcher(None,expected_tokens,heard_tokens,autojunk=False).get_opcodes():
            if tag!='equal':differences.append({'kind':tag,'expected':' '.join(expected_tokens[a:b]),'recognized':' '.join(heard_tokens[c:d])})
        report={'id':ep['id'],'audio_sha256':digest(path),'model':args.model,'engine':'faster-whisper',
                'expected_script':script(ep),'transcript':text,'segments':observed,'differences':differences,
                'human_listening_review':False,'interpretation':'ASR is fallible; punctuation, number spelling and recognition errors are not proof of synthesis errors.'}
        (out/(ep['id']+'.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'id':ep['id'],'transcript':text,'differences':differences}),flush=True)

if __name__=='__main__':main()
