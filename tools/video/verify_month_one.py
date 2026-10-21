"""Verify retained narrated exports and write an honest local/Git receipt."""
import hashlib
import json
import subprocess
from pathlib import Path
from month_one_core import ROOT,load_episodes,digest,script,normalized
from build_month_one import probe
from package_month_one import verify_narrated_export

def main():
    review=ROOT/'.local/month-one/review'; outputs=[];reports=[];audio_hashes=[]
    for ep in load_episodes():
        folder=review/ep['id'];tl=json.loads((folder/'timeline.json').read_text())
        expected=hashlib.sha256(script(ep).encode()).hexdigest()
        assert tl['script_sha256']==expected and tl['timing']=='provider_word_alignment'
        assert normalized(' '.join(c['text'] for c in tl['captions']))==normalized(script(ep))
        assert all(0<=c['start']<c['end']<=tl['duration'] and c['cps']<=20.01 for c in tl['captions'])
        assert all(a['end']<=b['start']+.001 for a,b in zip(tl['captions'],tl['captions'][1:]))
        for treatment in (['compact','large','motion'] if ep['id']=='M01' else ['motion']):
            path=folder/f"{ep['id']}-{treatment}.mp4"; verify_narrated_export(path,ep,treatment)
            report=json.loads((folder/f'verification-{treatment}.json').read_text())
            assert report['full_decode']=='passed' and report['timeline_sha256']==digest(folder/'timeline.json')
            assert report['renderer_sha256']==digest(ROOT/'tools/video/render_month_one.cjs')
            meta=probe(path);v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
            assert (v['width'],v['height'],v['codec_name'],v['r_frame_rate'])==(1080,1920,'h264','30/1')
            assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
            assert int(v['nb_frames'])==round(tl['duration']*30)
            assert abs(float(meta['format']['duration'])-tl['duration'])<.04
            assert -18<=float(report['loudness']['input_i'])<=-14 and float(report['loudness']['input_tp'])<=-1
            if ep['id']=='M01':
                audio_hashes.append(subprocess.run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','md5','-'],capture_output=True,text=True,check=True).stdout.strip())
            outputs.append({'file':str(path.relative_to(review)),'sha256':digest(path),'bytes':path.stat().st_size,
                'duration':float(meta['format']['duration']),'frames':int(v['nb_frames']),'width':v['width'],'height':v['height'],'audio_present':True})
            reports.append(report)
    assert len(set(audio_hashes))==1,'Comparisons must have byte-identical encoded audio'
    current=list((ROOT/'.local/month-one/voice').glob('M*/generation.json'))
    historical=list((ROOT/'.local/month-one/voice-history').glob('M*/v*/generation.json'))
    result={'date':'2026-10-21','status':'narrated_review_exports_complete_human_review_pending','core_episodes':16,
       'video_exports':len(outputs),'carousel_images':20,'story_images':16,'captions':'provider_word_alignment_with_bounded_reading_time',
       'max_caption_cps':max(r['max_cps'] for r in reports),'decode_passes':len(reports),
       'loudness_lufs_range':[min(float(r['loudness']['input_i']) for r in reports),max(float(r['loudness']['input_i']) for r in reports)],
       'comparison_encoded_audio_identical':True,'new_openart_generation_calls':0,
       'fish_synthesis_requests_submitted':len(current)+len(historical),'retained_voice_revisions':len(historical),
       'human_listening_review':False,'target_uploader_preview':False,'live_audience_observations':0,'public_upload':False,
       'provider_actual_charge':None,'historical_source_changes':False,'outputs':outputs}
    encoded=json.dumps(result,indent=2)+'\n'
    (ROOT/'examples/month-one/verification.json').write_text(encoded)
    (review/'verification-summary.json').write_text(encoded)
    print(json.dumps({k:v for k,v in result.items() if k!='outputs'},indent=2))

if __name__=='__main__':main()
