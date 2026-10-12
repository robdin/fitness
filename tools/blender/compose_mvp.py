"""Narrate and assemble the Blender MVP. See examples/blender-mvp/README.md."""
import argparse,hashlib,json,math,subprocess,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.signal import resample_poly
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'content/mvp/time-audit/episode.json'
W,H,FPS,SR=1080,1920,30,48000
LIME,CREAM,NAVY,MUTED,CORAL,BLUE='#B9F227','#F7F4EA','#10233E','#9EADBF','#FF6B4A','#74B9FF'
COLORS=[LIME,CREAM,BLUE,CORAL]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def wav(path,a):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1 if a.ndim==1 else a.shape[1]);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((np.clip(a,-.99,.99)*32767).astype('<i2').tobytes())
def readwav(path):
    with wave.open(str(path),'rb') as w:
        assert w.getsampwidth()==2
        rate=w.getframerate();channels=w.getnchannels();a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
    if channels>1:a=a.reshape(-1,channels).mean(axis=1)
    if rate!=SR:
        g=math.gcd(rate,SR);a=resample_poly(a,SR//g,rate//g)
    return a
def audio(episode,work,model):
    from local_speech import LocalVoice
    voice=LocalVoice(model)
    model_hash=sha(model);segments=[];scenes=[];all_cues=[];cursor=0
    for scene in episode['scenes']:
        parts=[np.zeros(round(.42*SR))];local=.42;cues=[]
        for caption in scene['captions']:
            key=hashlib.sha256((caption+model_hash+'openvino/.99/.58/.75').encode()).hexdigest()[:20]
            path=work/('voice-'+key+'.wav')
            if not path.exists() or path.stat().st_size<=44:
                with wave.open(str(path),'wb') as w:voice.synthesize_wav(caption,w)
            a=readwav(path);active=np.where(np.abs(a)>.004)[0]
            if len(active):a=a[max(0,active[0]-round(.08*SR)):min(len(a),active[-1]+round(.13*SR))]
            a=a/(float(np.max(np.abs(a))) or 1)*.70
            end=local+len(a)/SR;cues.append({'start':round(cursor+local,4),'end':round(cursor+end,4),'text':caption})
            parts.extend([a,np.zeros(round(.15*SR))]);local=end+.15
        duration=math.ceil(max(scene['minimum_seconds'],local+.55)*FPS)/FPS
        a=np.concatenate(parts);a=np.pad(a,(0,max(0,round(duration*SR)-len(a))));segments.append(a)
        scenes.append({**scene,'start':round(cursor,4),'end':round(cursor+duration,4),'duration':duration,'cues':cues})
        all_cues.extend(cues);cursor+=duration
    narration=np.concatenate(segments);wav(work/'narration.wav',narration)
    n=len(narration);bed=np.zeros((n,2));rng=np.random.default_rng(20261011)
    def place(signal,start,pan=0):
        a=max(0,round(start*SR));b=min(n,a+len(signal))
        if b>a:
            bed[a:b,0]+=signal[:b-a]*math.sqrt((1-pan)/2);bed[a:b,1]+=signal[:b-a]*math.sqrt((1+pan)/2)
    notes=[130.8128,164.8138,195.9977,246.9417]
    for i in range(math.ceil(cursor/.6)):
        t=np.arange(round(.55*SR))/SR
        if i%2==0:
            f=notes[(i//2)%4];s=(np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t))*np.exp(-8*t)*np.minimum(1,t/.012)*.023
            place(s,i*.6,.35 if i%4==0 else -.35)
        if i%4==0:place(np.sin(2*np.pi*(48*t+5*(1-np.exp(-20*t))))*np.exp(-15*t)*.045,i*.6)
        if i%2:place(rng.normal(0,1,len(t))*np.exp(-80*t)*.008,i*.6,.15)
    for s in scenes[1:]:
        t=np.arange(round(.38*SR))/SR;noise=rng.normal(0,1,len(t));smooth=np.convolve(noise,np.ones(13)/13,'same')
        place(smooth*np.sin(np.pi*t/.38)**2*.055,max(0,s['start']-.2),-.2)
    fade=np.minimum(1,np.arange(n)/(SR*1.2))*np.minimum(1,(n-1-np.arange(n))/(SR*1.5))
    wav(work/'mix.wav',(bed+narration[:,None])*fade[:,None])
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(work/'mix.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-ar',str(SR),str(work/'master.wav')],check=True)
    timeline={'episode_id':episode['id'],'fps':FPS,'duration':round(cursor,4),'scenes':scenes,'cues':all_cues,'source_sha256':sha(SOURCE),'voice_model':Path(model).name,'voice_model_sha256':model_hash,'narration':'synthetic prototype, no voice cloning','audio':'original procedural score and effects'}
    (work/'timeline.json').write_text(json.dumps(timeline,indent=2)+'\n');return timeline
def font(size,weight=500):
    f=ImageFont.truetype(str(ROOT/'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),size)
    f.set_variation_by_axes([weight]);return f
F={n:font(s,w) for n,s,w in [('brand',34,700),('micro',25,500),('eyebrow',28,600),('head',102,700),('body',42,500),('label',34,500),('number',48,700),('caption',43,500)]}
def center(d,y,text,f,color=CREAM):d.text(((W-d.textlength(text,font=f))/2,y),text,font=f,fill=color)
def wrap(d,text,f,width):
    lines=[];line=''
    for word in text.split():
        test=(line+' '+word).strip()
        if d.textlength(test,font=f)>width and line:lines.append(line);line=word
        else:line=test
    if line:lines.append(line)
    return lines
def background():
    y,x=np.mgrid[0:H,0:W];g=np.exp(-(((x-W*.55)/(W*.85))**2+((y-H*.49)/(H*.44))**2)*3)
    rgb=np.zeros((H,W,3),dtype=np.uint8)
    for i,(a,b) in enumerate([(6,16),(15,35),(28,59)]):rgb[:,:,i]=(a+(b-a)*g).astype(np.uint8)
    im=Image.fromarray(rgb).convert('RGBA');d=ImageDraw.Draw(im)
    for xx in range(70,W,55):
        for yy in range(180,1730,55):d.ellipse((xx,yy,xx+1,yy+1),fill=(60,81,107,55))
    return im
BG=background()
def load_assets(work):
    assets={}
    for name in ['clock','ring','dumbbell','tiles']:
        paths=sorted((work/name).glob('frame-*.png'))
        if len(paths)!=48:raise ValueError(f'{name}: expected 48 rendered frames, found {len(paths)}')
        assets[name]=[Image.open(p).convert('RGBA') for p in paths]
    return assets
def frame(t,timeline,assets):
    idx=next((i for i,s in enumerate(timeline['scenes']) if t<s['end']),len(timeline['scenes'])-1)
    s=timeline['scenes'][idx];local=t-s['start'];entry=1-(1-min(1,max(0,local/.55)))**3
    im=BG.copy();d=ImageDraw.Draw(im)
    d.text((78,110),'REP / REASON',font=F['brand'],fill=CREAM)
    d.rounded_rectangle((792,107,1000,154),radius=23,outline='#395063',width=1)
    d.text((817,116),'FIELD NOTE 001',font=F['micro'],fill=MUTED);d.line((80,198,1000,198),fill='#283749',width=2)
    yoff=round(26*(1-entry));d.text((80,263+yoff),s['eyebrow'],font=F['eyebrow'],fill=LIME)
    for k,line in enumerate(s['headline']):d.text((73,328+k*112+yoff),line,font=F['head'],fill=CREAM if k==0 else LIME)
    frames=assets[s['asset']];asset=frames[int(local*24)%len(frames)]
    size=970 if s['id'] in ['hook','rest'] else 930;cy=948
    if s['id']=='audit':size=720;cy=900
    if s['id']=='action':size=760;cy=926
    size=round(size*(.94+.06*entry));asset=asset.resize((size,size),Image.Resampling.LANCZOS)
    im.alpha_composite(asset,((W-size)//2,round(cy-size/2+32*(1-entry))));d=ImageDraw.Draw(im)
    sid=s['id']
    if sid=='hook':
        d.rounded_rectangle((339,1215,741,1293),radius=39,fill=LIME);center(d,1221,'60 MINUTES',F['number'],NAVY)
    elif sid=='audit':
        for k,(label,value) in enumerate([('LIFTING',15),('REST',25),('SETUP',8),('WAITING',12)]):
            x=96+(k%2)*475;y=1152+(k//2)*110
            d.rounded_rectangle((x,y,x+439,y+92),radius=18,fill='#14263B',outline='#2C4258')
            d.ellipse((x+21,y+35,x+37,y+51),fill=COLORS[k]);d.text((x+52,y+30),label,font=F['micro'],fill=CREAM)
            d.text((x+326,y+20),str(value)+'m',font=F['number'],fill=COLORS[k])
        center(d,1380,'ILLUSTRATIVE EXAMPLE / NOT MEASURED DATA',F['micro'],MUTED)
    elif sid=='friction':
        d.line((150,1235,930,1235),fill='#40556A',width=3);x=150+780*((local*.18)%1);d.ellipse((x-8,1227,x+8,1243),fill=LIME)
        for x,label in [(150,'SETUP'),(540,'WALK'),(930,'WAIT')]:
            d.ellipse((x-15,1220,x+15,1250),fill=NAVY,outline=LIME,width=3);d.text((x-d.textlength(label,font=F['micro'])/2,1275),label,font=F['micro'],fill=MUTED)
    elif sid=='rest':
        d.rounded_rectangle((176,1258,904,1345),radius=24,fill='#142B36',outline='#789C34',width=2);center(d,1275,'TIME AUDIT ≠ REST PRESCRIPTION',F['eyebrow'])
    elif sid=='action':
        for k,label in enumerate(['01  LOG ONE SESSION','02  CHANGE ONE THING','03  COMPARE NEXT TIME']):d.text((137,1190+k*65),label,font=F['label'],fill=LIME if k==min(2,int(local/3)) else CREAM)
    elif sid=='close':
        d.rounded_rectangle((158,1185,922,1317),radius=28,fill=LIME);center(d,1214,'TRY ONE SESSION AUDIT',F['body'],NAVY);center(d,1360,'LIFTING  /  REST  /  SETUP  /  WAITING',F['micro'],MUTED)
    cue=next((c for c in s['cues'] if c['start']<=t<c['end']+.10),None)
    if cue:
        lines=wrap(d,cue['text'],F['caption'],844);top=1515
        d.rounded_rectangle((72,top-22,1008,top+len(lines)*57+23),radius=24,fill='#081321',outline='#26384C',width=1)
        for k,line in enumerate(lines):center(d,top+k*57,line,F['caption'])
    d.text((80,1773),'KNOW WHY. TRAIN BETTER.',font=F['micro'],fill=MUTED);d.text((858,1773),f'{idx+1:02d} / 06',font=F['micro'],fill=MUTED)
    for k in range(6):
        x=80+k*157;d.rounded_rectangle((x,1835,x+136,1840),radius=2,fill=LIME if k<=idx else '#27394D')
    fade=min(1,max(0,local/.14),max(0,(s['end']-t)/.14))
    if fade<1:im=Image.blend(BG,im,fade)
    return im.convert('RGB')
def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
def compose(timeline,work,out,stills=False):
    if timeline['source_sha256']!=sha(SOURCE):raise ValueError('Episode changed: regenerate narration before composing')
    assets=load_assets(work);contact=Image.new('RGB',(810,960),'#081321')
    for i,s in enumerate(timeline['scenes']):
        im=frame(s['start']+min(2.5,s['duration']/2),timeline,assets);im.save(work/f'scene-{i+1:02d}.jpg',quality=93)
        contact.paste(im.resize((270,480)),((i%3)*270,(i//3)*480))
    contact.save(out/'contact-sheet.jpg',quality=94);frame(2,timeline,assets).save(out/'poster.jpg',quality=94)
    if stills:return
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(work/'master.wav'),'-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(out/'Rep_and_Reason_Blender_MVP.mp4')]
    process=subprocess.Popen(command,stdin=subprocess.PIPE);count=round(timeline['duration']*FPS)
    try:
        for i in range(count):
            process.stdin.write(frame(i/FPS,timeline,assets).tobytes())
            if i%300==0:print(f'COMPOSE {i}/{count}',flush=True)
        process.stdin.close()
        if process.wait()!=0:raise RuntimeError('FFmpeg failed')
    finally:
        if process.poll() is None:process.terminate()
    (out/'captions.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(timeline['cues']))+'\n')
    (out/'timeline.json').write_text(json.dumps(timeline,indent=2)+'\n')
    receipt={'episode_id':timeline['episode_id'],'width':W,'height':H,'fps':FPS,'duration':timeline['duration'],'video_sha256':sha(out/'Rep_and_Reason_Blender_MVP.mp4'),'episode_sha256':sha(SOURCE),'scene_script_sha256':sha(Path(__file__).with_name('build_scene.py')),'composition_script_sha256':sha(__file__),'speech_adapter_sha256':sha(Path(__file__).with_name('local_speech.py')),'blender_project_sha256':sha(out/'time-audit.blend'),'voice_model_sha256':timeline['voice_model_sha256'],'public_release_approval':False,'status':'internal visual MVP','example':'15+25+8+12=60 invented minutes'}
    (out/'build-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('MVP_COMPLETE',flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--voice-model',type=Path);p.add_argument('--work',type=Path,default=ROOT/'.local/blender-mvp');p.add_argument('--out',type=Path,default=ROOT/'examples/blender-mvp');p.add_argument('--audio-only',action='store_true');p.add_argument('--stills-only',action='store_true');a=p.parse_args()
    a.work.mkdir(parents=True,exist_ok=True);a.out.mkdir(parents=True,exist_ok=True);episode=json.loads(SOURCE.read_text());assert sum(episode['example_minutes'].values())==60
    timeline=audio(episode,a.work,a.voice_model) if a.voice_model else json.loads((a.work/'timeline.json').read_text())
    print('TIMELINE_SECONDS',timeline['duration'],flush=True)
    if not a.audio_only:compose(timeline,a.work,a.out,a.stills_only)
if __name__=='__main__':main()
