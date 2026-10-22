/* Beginner decision stories. Brand systems are packages, not color-only experiments. */
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process'),{once}=require('node:events');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..'),BRANDS=JSON.parse(fs.readFileSync(path.join(ROOT,'brand/v3/tokens.json')));
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>1-(1-clamp(x))**3;
function createRenderer(tl,{width=1080,treatment='motion',captions=true}={}){
 const design=tl.episode.graphics,brand=design.brand||'club',C=BRANDS[brand];if(!C)throw Error('Unknown brand');
 const canvas=createCanvas(width,Math.round(width*16/9)),g=canvas.getContext('2d'),checks=[];let idx=0,local=0,p=1,t=0;
 const motion=treatment==='motion',dark=brand==='lab',club=brand==='club',paper=brand==='notebook';
 const graphicInk=dark?'#F4F7EF':C.ink,chipInk=club?'#F5F3EA':C.ink;
 function rect(x,y,w,h,c,r=C.radius){g.fillStyle=c;g.beginPath();g.roundRect(x,y,w,h,r);g.fill();}
 function line(x,y,xx,yy,c,w=5){g.strokeStyle=c;g.lineWidth=w;g.lineCap='round';g.beginPath();g.moveTo(x,y);g.lineTo(xx,yy);g.stroke();}
 function dot(x,y,r,c){g.fillStyle=c;g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fill();}
 function text(s,x,y,size=42,color=C.ink,align='left',max=820,weight=C.weight){
  const font=n=>{g.font=`${weight} ${n}px Space`;};font(size);while(g.measureText(s).width>max&&size>24)font(--size);
  const w=g.measureText(s).width,left=align==='center'?x-w/2:align==='right'?x-w:x;
  checks.push({text:s,x:left,y,size,width:w,right:left+w,bottom:y+size*1.2,color,brand});
  g.textAlign=align;g.textBaseline='top';g.fillStyle=color;g.fillText(s,x,y);
 }
 function tick(x,y,c){line(x-13,y,x-1,y+12,c,7);line(x-1,y+12,x+24,y-18,c,7);}
 function arrow(x,y,xx,yy,c=C.accent,w=9){line(x,y,xx,yy,c,w);let a=Math.atan2(yy-y,xx-x);line(xx,yy,xx-24*Math.cos(a-.65),yy-24*Math.sin(a-.65),c,w);line(xx,yy,xx-24*Math.cos(a+.65),yy-24*Math.sin(a+.65),c,w);}
 function tag(s,y=1078){const bg=paper?C.accent:club?C.ink:C.accent,fg=paper?C.accentInk:club?C.bg:C.accentInk;rect(100,y,800,62,bg);text(s,500,y+13,30,fg,'center',764);}
 function rows(items,active=Math.min(2,idx),y=640){items.forEach((s,i)=>{let yy=y+i*143,selected=i===active;const bg=selected?C.accent:paper?C.panel:club?C.panel:'#203650',fg=selected?C.accentInk:club?'#F5F3EA':C.ink;rect(100,yy,800,116,bg);text(String(i+1).padStart(2,'0'),131,yy+30,42,fg);text(s,232,yy+33,40,fg,'left',625);if(selected&&idx>0)tick(849,yy+55,fg);});}
 function two(a,b){for(let i=0;i<2;i++){let x=100+i*420;rect(x,632,380,400,paper?C.panel:club?C.panel:'#203650');text(i?b:a,x+190,661,30,club?'#F5F3EA':C.ink,'center',346);} }
 const objectColor=club?C.accent:paper?C.accent:C.accent;
 function machine(x,y,scale=1,c=objectColor){g.save();g.translate(x,y);g.scale(scale,scale);line(-72,110,75,110,c,11);line(-62,105,-62,-110,c,11);line(-62,-110,68,-110,c,11);line(68,-110,68,110,c,11);for(let j=0;j<5;j++)rect(-39,-59+j*23,60,16,c,3);line(44,-93,44,-8,c,5);line(26,-8,63,-8,c,8);rect(-13,64,85,18,c,4);g.restore();}
 function dumbbell(x,y,s=1,c=objectColor){g.save();g.translate(x,y);g.scale(s,s);rect(-82,-10,164,20,c,5);for(let sign of [-1,1]){rect(sign*65-15,-58,30,116,c,6);rect(sign*94-10,-43,20,86,c,6);}g.restore();}
 function sevenDay(){const days=['M','T','W','T','F','S','S'];days.forEach((s,i)=>{const x=100+i*116,gym=i===1||i===5;rect(x,710,104,228,gym?C.accent:paper?C.panel:club?C.panel:'#203650');text(s,x+52,735,38,gym?C.accentInk:club?'#F5F3EA':C.ink,'center',80);if(gym){text('GYM',x+52,831,26,C.accentInk,'center',90);tick(x+50,895,C.accentInk);}else text('—',x+52,830,40,club?'#F5F3EA':C.ink,'center',80);});}
 function graphic(){
  const k=design.kind;
  if(['checklist','weight','scorecard','program'].includes(k)){rows(design.labels,Math.min(2,Math.max(0,idx-1)));tag(k==='weight'?'NO UNIVERSAL STARTING NUMBER':k==='scorecard'?'REVIEW YOUR PROCESS':k==='program'?'A PLAN YOU CAN FOLLOW':'BEFORE YOU WALK IN');}
  else if(k==='machine'){two('MACHINE','FREE WEIGHT');machine(290,873,1.1);dumbbell(710,873,1.25);if(idx>=4){rect(131,963,318,45,C.accent);text('SAVE SETTINGS',290,970,25,C.accentInk,'center',300);}tag(idx===3?'EACH EXERCISE HAS A PURPOSE':'LEARN THE SETUP');}
  else if(k==='timer'){two('SHORTER REST','LONGER REST');for(let i=0;i<2;i++){const x=290+i*420;g.beginPath();g.arc(x,864,121,0,Math.PI*2);g.strokeStyle=objectColor;g.lineWidth=14;g.stroke();const a=-Math.PI/2+(motion?p:1)*Math.PI*(i?1.7:.6);line(x,864,x+84*Math.cos(a),864+84*Math.sin(a),objectColor,8);text(i?'3:00':'1:00',x,957,37,club?'#F5F3EA':C.ink,'center',280);}tag(idx>=3?'NOT A RULE FOR EVERY EXERCISE':'ONE SMALL STUDY IN TRAINED MEN');}
  else if(k==='sets'){for(let r=0;r<3;r++){let yy=640+r*143;rect(100,yy,800,117,paper?C.panel:club?C.panel:'#203650');text('SET '+(r+1),124,yy+17,26,club?'#F5F3EA':C.ink);for(let j=0;j<8;j++){let active=idx===0||idx>1||j<Math.ceil(p*8);dot(296+j*78,yy+59,25,active?objectColor:dark?'#66809F':'#7D8B75');}if(r<2)text('REST',865,yy+118,20,C.muted,'right',120);}tag('3 SETS × 8 REPS · EXAMPLE');}
  else if(k==='soreness'){two('SORENESS','TRAINING LOG');dot(290,858,97,objectColor);dot(261,838,8,C.accentInk);dot(319,838,8,C.accentInk);line(256,889,324,889,C.accentInk,8);for(let i=0;i<3;i++){rect(585,780+i*70,45,45,objectColor,6);tick(607,803+i*70,C.accentInk);line(659,803+i*70,827,803+i*70,club?'#F5F3EA':C.ink,6);}tag('A FEELING IS NOT A GROWTH MEASURE');}
  else if(k==='reps'){two('LAST TIME','TODAY');text('8',290,753,180,club?'#F5F3EA':C.ink,'center',300,700);const at=tl.words?.find(w=>w.text.toLowerCase().replace(/[^a-z]/g,'')==='nine')?.start;const revealed=at!==undefined?t>=at:idx>=2;text(revealed?'9':'?',710,753,180-(motion&&revealed?10*(1-ease((t-(at??tl.beats[2].start))/.55)):0),objectColor,'center',300,700);arrow(477,860,516,860,paper?C.accent:club?C.ink:C.accent,6);tag(idx>=3?'PERFORMANCE ≠ PROOF OF NEW MUSCLE':'SAME EXERCISE · SETUP · STOPPING RULE');}
  else if(k==='calendar'){sevenDay();tag(idx===3?'DOES NOT COVER ALL ACTIVITY NEEDS':'AN ILLUSTRATIVE WEEK');}
  else if(k==='food'){two('FOOD','POWDER');dot(290,850,118,objectColor);dot(290,850,90,club?C.panel:paper?C.panel:'#203650');text('BEANS',290,794,32,club?'#F5F3EA':C.ink,'center',200);text('TOFU',290,842,32,club?'#F5F3EA':C.ink,'center',200);text('EGGS',290,890,32,club?'#F5F3EA':C.ink,'center',200);rect(630,762,160,215,objectColor,18);rect(644,738,132,33,objectColor,8);text('OPTIONAL',710,844,29,C.accentInk,'center',146);tag(idx>=3?'A VARIED DIET STILL MATTERS':'MORE THAN ONE WAY TO GET PROTEIN');}
  else if(k==='trend'){rows(['EXERCISE + SETUP','LOAD + REPS','REST + STOPPING RULE'],idx>=4?2:Math.min(2,idx));tag('COMPARE SEVERAL SIMILAR SESSIONS');}
  else if(k==='backup'){two('OCCUPIED','YOUR BACKUP');machine(290,855,1.0);text('?',710,763,180,objectColor,'center',300,700);arrow(477,860,516,860,paper?C.accent:club?C.ink:C.accent,6);tag(idx>=3?'DIFFERENT MOVEMENT · SEPARATE LOG':'ASK FOR A SUITABLE ALTERNATIVE');}
  else if(k==='effort'){text('EFFORT',100,650,42,C.ink);rect(100,756,800,69,paper?C.panel:club?C.panel:'#203650',35);rect(100,756,Math.max(70,610*p),69,C.accent,35);line(900,723,900,859,paper?C.accent:club?C.secondary:C.ink,8);text('CHALLENGING',100,891,35,C.ink);text('FAILURE',900,891,35,C.ink,'right',250);text('CONCEPTUAL SCALE',100,984,26,C.muted);tag('FOLLOW YOUR ROUTINE’S EFFORT TARGET');}
  else if(k==='log'){two('MACHINE A','MACHINE B');for(let i=0;i<2;i++){let x=132+i*420;['SETTING','LOAD','REPS'].forEach((s,j)=>{text(s,x,758+j*79,27,club?'#F5F3EA':C.ink,'left',170);line(x+176,782+j*79,x+308,782+j*79,objectColor,5);});}tag('COMPARE EACH SETUP WITH ITSELF');}
  else if(k==='return'){two('MISSED','NEXT VISIT');text('×',290,755,172,club?'#F5F3EA':C.ink,'center',280);rect(595,773,230,174,objectColor);tick(710,858,C.accentInk);arrow(477,860,516,860,paper?C.accent:club?C.ink:C.accent,6);tag(idx===3?'NO AUTOMATIC DOUBLE WORKOUT':'CHECK YOUR ROUTINE · PLAN THE RETURN');}
  else throw Error('Unknown graphic '+k);
 }
 function frame(time,{burn=captions}={}){
  t=time;idx=tl.beats.findIndex(b=>t>=b.start&&t<b.end);if(idx<0)idx=t<tl.beats[0].start?0:tl.beats.length-1;local=Math.max(0,t-tl.beats[idx].start);p=motion?ease(local/.6):1;checks.length=0;
  g.resetTransform();g.scale(width/1080,width/1080);g.fillStyle=C.bg;g.fillRect(0,0,1080,1920);
  if(dark){for(let x=60;x<1050;x+=80)line(x,190,x,1530,'#162D48',1);for(let y=190;y<1530;y+=80)line(60,y,1020,y,'#162D48',1);}
  if(club){rect(0,0,1080,180,C.secondary,0);rect(0,1560,1080,360,C.secondary,0);rect(54,240,12,1240,C.ink,0);}
  if(paper){rect(72,580,860,584,C.panel,28);line(118,604,118,1136,'#D8A28D',2);for(let y=637;y<1140;y+=64)line(135,y,909,y,'#E7DFD3',1);}
  const markBg=paper?C.accent:C.accent,markFg=C.accentInk;rect(84,250,70,61,markBg,paper?19:4);text(club?'R/R':dark?'R²':'R',119,263,27,markFg,'center',62,700);text('REP & REASON',177,265,28,C.ink,'left',380,700);text(tl.episode.id+' / '+tl.episode.pillar.toUpperCase(),915,267,23,C.muted,'right',310);
  design.headlines[idx].forEach((s,i)=>text(s,84,354+i*99,88,C.ink,'left',835,club?700:C.weight));
  for(let j=0;j<tl.beats.length;j++)rect(85+j*141,557,125,6,j<=idx?(paper?C.accent:club?C.secondary:C.accent):(dark?'#39516F':'#D0D7C5'),2);
  graphic();text(design.scope_label,500,1171,23,C.muted,'center',820,500);
  const ci=tl.captions.findIndex(c=>t>=c.start&&t<c.end);
  if(burn&&ci>=0){const c=tl.captions[ci];rect(76,1242,850,c.lines.length*60+32,dark?'#F4F7EF':C.ink,paper?22:8);c.lines.forEach((s,i)=>text(s,501,1257+i*60,43,dark?'#0A1930':C.bg,'center',798,600));}
  text(tl.timing==='estimated_visual_draft'?'VISUAL DRAFT · VOICE TIMING PENDING':'KNOW WHY. TRAIN BETTER.',84,1460,24,C.muted,'left',830,600);
  return canvas;
 }
 return {canvas,frame,checks};
}

async function main(){
 const args=process.argv.slice(2),tl=JSON.parse(fs.readFileSync(args[0])),out=path.resolve(args[1]);fs.mkdirSync(out,{recursive:true});
 const treatment=args.includes('--treatment')?args[args.indexOf('--treatment')+1]:'motion',width=args.includes('--width')?Number(args[args.indexOf('--width')+1]):1080;
 const r=createRenderer(tl,{width,treatment,captions:!args.includes('--clean')});
 if(args.includes('--stills')){
  const report=[];for(let i=0;i<tl.beats.length;i++){const t=tl.beats[i].start+Math.min(1.2,(tl.beats[i].end-tl.beats[i].start)/2);r.frame(t);fs.writeFileSync(path.join(out,`scene-${i}.png`),r.canvas.toBuffer('image/png'));report.push({time:t,text:[...r.checks]});}
  r.frame(.18);fs.writeFileSync(path.join(out,'cover.png'),r.canvas.toBuffer('image/png'));fs.writeFileSync(path.join(out,'layout.json'),JSON.stringify(report,null,2));return;
 }
 const first=args.includes('--range')?Number(args[args.indexOf('--range')+1]):0,count=args.includes('--range')?Number(args[args.indexOf('--range')+2]):Math.round(tl.duration*30),last=Math.min(Math.round(tl.duration*30),first+count);
 const file=path.join(out,`segment-${String(first).padStart(5,'0')}.mp4`);
 const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${r.canvas.width}x${r.canvas.height}`,'-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-pix_fmt','yuv420p',file],{stdio:['pipe','inherit','inherit']});
 const done=once(ff,'close');ff.stdin.on('error',()=>{});
 for(let f=first;f<last;f++){r.frame(f/30);if(!ff.stdin.write(r.canvas.data()))await once(ff.stdin,'drain');}
 ff.stdin.end();const [code]=await done;if(code!==0)throw Error('FFmpeg failed: '+code);console.log(file);
}
module.exports={createRenderer};
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
