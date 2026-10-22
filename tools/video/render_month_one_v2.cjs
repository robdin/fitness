/* Original N-series motion design. No external imagery or invented study data. */
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process'),{once}=require('node:events');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..');
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
const C={navy:'#10233E',ink:'#071827',cream:'#F7F4EA',paper:'#FFFDF7',lime:'#B9F227',blue:'#88C7EE',coral:'#FF937A',muted:'#B5C5D2',line:'#385269',shadow:'#D7DACE'};
const clamp=x=>Math.min(1,Math.max(0,x)),ease=x=>1-Math.pow(1-clamp(x),3),mix=(a,b,p)=>a+(b-a)*p,norm=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');

function createRenderer(tl,{width=1080,treatment='motion',captions=true}={}){
 const canvas=createCanvas(width,Math.round(width*16/9)),g=canvas.getContext('2d'),checks=[];
 const motion=treatment==='motion';let idx=0,p=1,t=0,local=0;
 const glyph=(s,size,weight=600)=>{g.font=`${weight} ${size}px Space`;return g.measureText(s).width;};
 function rect(x,y,w,h,color,r=22,stroke){g.beginPath();g.roundRect(x,y,w,h,r);if(color){g.fillStyle=color;g.fill();}if(stroke){g.strokeStyle=stroke;g.lineWidth=2;g.stroke();}}
 function line(x,y,xx,yy,color=C.muted,w=4){g.beginPath();g.moveTo(x,y);g.lineTo(xx,yy);g.strokeStyle=color;g.lineWidth=w;g.lineCap='round';g.stroke();}
 function circle(x,y,r,color){g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fillStyle=color;g.fill();}
 function text(s,x,y,size=42,color=C.cream,align='left',max=800,weight=600){
  let actual=size;while(glyph(s,actual,weight)>max&&actual>24)actual--;
  const w=glyph(s,actual,weight),left=align==='center'?x-w/2:align==='right'?x-w:x;
  checks.push({text:s,size:actual,x:left,y,width:w,right:left+w,bottom:y+actual*1.2});
  g.textBaseline='top';g.textAlign=align;g.fillStyle=color;g.fillText(s,x,y);
 }
 function pill(s,x,y,w=330,color=C.lime,size=28){rect(x,y,w,56,color,28);text(s,x+w/2,y+13,size,C.navy,'center',w-24);}
 function card(x,y,w,h,color='#1C354D'){rect(x+7,y+10,w,h,'#071421',24);rect(x,y,w,h,color,24);}
 function arrow(x,y,xx,yy,color=C.lime,w=7){line(x,y,xx,yy,color,w);const a=Math.atan2(yy-y,xx-x);line(xx,yy,xx-19*Math.cos(a-.65),yy-19*Math.sin(a-.65),color,w);line(xx,yy,xx-19*Math.cos(a+.65),yy-19*Math.sin(a+.65),color,w);}
 function tick(x,y,color=C.lime){line(x-12,y,x-2,y+11,color,6);line(x-2,y+11,x+20,y-14,color,6);}
 function dumbbell(x,y,s=1,color=C.lime){g.save();g.translate(x,y);g.rotate(motion?Math.sin(local*.6)*.025:0);g.scale(s,s);rect(-64,-8,128,16,color,5);for(const sign of [-1,1]){rect(sign*52-13,-48,26,96,color,7);rect(sign*77-9,-34,18,68,color,6);}g.restore();}
 function machine(x,y,s=1,color=C.blue){g.save();g.translate(x,y);g.scale(s,s);line(-65,75,65,75,color,9);line(-50,70,-50,-80,color,9);line(-50,-80,52,-80,color,9);line(52,-80,52,75,color,9);for(let j=0;j<5;j++)rect(-32,-40+j*19,43,12,color,3);line(33,-70,33,-12,C.cream,4);line(15,-12,52,-12,C.cream,6);rect(-5,35,60,14,color,4);g.restore();}
 function person(x,y,color=C.muted,s=1){circle(x,y,12*s,color);rect(x-14*s,y+18*s,28*s,48*s,color,10*s);line(x-7*s,y+60*s,x-16*s,y+92*s,color,9*s);line(x+7*s,y+60*s,x+16*s,y+92*s,color,9*s);}
 function list(items,y=686,{x=134,w=724,active=idx%3,step=108}={}){items.forEach((s,i)=>{const yy=y+i*step;rect(x,yy,w,82,i===active?C.lime:'#1D384E',17);circle(x+40,yy+41,17,i===active?C.navy:C.line);text(String(i+1),x+40,yy+25,27,i===active?C.lime:C.cream,'center',30);text(s,x+82,yy+25,31,i===active?C.navy:C.cream,'left',w-106);});}
 function scope(extra){text(extra||tl.episode.graphics.scope_label,495,1100,24,C.muted,'center',800);}
 function twoCards(left,right,{leftColor=C.lime,rightColor=C.blue}={}){card(125,650,340,346);card(525,650,340,346);text(left,295,682,31,leftColor,'center',308);text(right,695,682,31,rightColor,'center',308);}
 function calendar(){
  if(idx===0){
   for(let i=0;i<2;i++){const x=125+i*400,yy=650+(motion?24*(1-p)*(i?1:-1):0);card(x,yy,340,350,i?C.lime:C.paper);rect(x,yy,340,72,i?C.navy:C.lime,22);text(i?'SATURDAY':'TUESDAY',x+170,yy+20,30,i?C.lime:C.navy,'center',300);text('GYM',x+170,yy+112,86,C.navy,'center',300,700);dumbbell(x+170,yy+274,.9,C.navy);}
   pill('TWO AVAILABLE DAYS',255,1023,480);
  }else{
   const names=['M','T','W','T','F','S','S'];
   names.forEach((name,i)=>{const xx=126+i*106;const gym=i===1||i===5;text(name,xx+41,651,28,C.muted,'center',70);rect(xx,703,82,120,gym?C.lime:'#263E53',13);text(gym?'GYM':'—',xx+41,748,25,gym?C.navy:C.muted,'center',72);});
   if(idx===1){text('A WEEK WITH REAL CONSTRAINTS',495,884,34,C.cream,'center',720);pill('WORK',155,970,190,C.blue);pill('TRAVEL',399,970,190,C.coral);pill('LIFE',643,970,190,C.paper);}
   else if(idx===2||idx===3){card(157,872,678,165);text(idx===2?'STRUCTURED WEEKLY WORK':'VISITS ALONE ≠ TRAINING DOSE',495,902,35,C.lime,'center',630);text('PLAN + EFFORT + CONSISTENCY',495,974,28,C.cream,'center',630);}
   else{['PLAN','LOG','REVIEW'].forEach((s,i)=>{const x=155+i*243;rect(x,896,190,122,i===Math.min(2,Math.floor(local/1.4))?C.lime:'#244158',18);text(s,x+95,940,32,i===Math.min(2,Math.floor(local/1.4))?C.navy:C.cream,'center',170);});}
  }
 }
 function effort(){
  if(tl.episode.id==='N05'){
   text('≈ 2',495,632,164,C.lime,'center',650,700);text('REPETITIONS REMAINING',495,815,30,C.cream,'center');
   for(let i=0;i<2;i++){rect(334+i*190,888,140,110,null,21,C.lime);text('?',404+i*190,911,68,C.lime,'center',100);}
   if(idx>=4)pill('ESTIMATE → RECORD → REFINE',175,1018,640,C.paper,27);
  }else{
   text('EFFORT IS A CONTINUUM',495,658,36,C.cream,'center');
   const x=150,y=815,w=680;rect(x,y,w,40,C.line,20);rect(x,y,w*.78,40,C.lime,20);
   const marker=x+w*(motion?mix(.63,.78,p):.78);circle(marker,y+20,26,C.paper);circle(marker,y+20,11,C.navy);
   line(x+w,y-60,x+w,y+74,C.coral,7);text('EASIER',x,906,28,C.muted);text('FAILURE',x+w,906,28,C.coral,'right',220);
   pill(idx>=4?'FOLLOW YOUR PROGRAM’S TARGET':'CHALLENGING ≠ ALWAYS FAILURE',164,1003,662,C.lime,28);
   text('CONCEPT ONLY · NO EXACT RIR TARGET',495,745,25,C.muted,'center');
  }
 }
 function equipment(){
  const light=tl.episode.id==='N09';
  if(idx===4){list(['A clear training goal','A repeatable setup','A comparable training log'],690,{active:1});return;}
  twoCards(light?'LIGHTER':'MACHINES',light?'HEAVIER':'FREE WEIGHTS');
  if(light){dumbbell(295,850,.92,C.lime);dumbbell(695,850,1.35,C.blue);}else{machine(295,850,1.15,C.lime);dumbbell(695,850,1.35,C.blue);}
  if(idx===2){pill(light?'GROWTH ≠ MAXIMUM STRENGTH':'GROWTH ≠ SPECIFIC LIFT SKILL',146,1020,698,C.paper,28);}
  else if(idx===3){pill(light?'THE STUDIED SETS REACHED FAILURE':'NOT EVERY EXERCISE IS INTERCHANGEABLE',146,1020,698,C.coral,26);}
  else pill(light?'LOAD + EFFORT + YOUR GOAL':'CHOOSE FOR THE TASK',205,1020,580,C.lime,30);
 }
 function reps(){
  if(idx===4){list(['Keep the same exercise and setup','Follow the program’s rep range','Use its progression rule'],687,{active:2});return;}
  twoCards('LAST TIME','TODAY');text('8',295,753,150,C.cream,'center',250,700);
  const at=tl.words?.find(w=>norm(w.text)==='nine')?.start;const nine=at!==undefined?t>=at:idx>=1;
  text(nine?'9':'?',695,753,150,C.lime,'center',250,700);arrow(470,850,516,850);
  for(let i=0;i<9;i++){const y=968-i*17;rect(137,y,20,12,i<8?C.cream:C.line,2);rect(537,y,20,12,i<8?C.lime:nine?C.coral:C.line,2);}
  pill(idx===3?'REPS OR LOAD: TWO PROGRESSION OPTIONS':'SAME LOAD · TECHNIQUE · STOPPING RULE',132,1020,726,C.paper,25);
 }
 function route(){
  if(idx===2||idx===4){list(idx===2?['What is the training goal?','What equipment is available?','Is the alternative familiar?']:['Write one familiar backup','Keep its own log entry','Review what you completed'],689,{active:idx===2?Math.min(2,Math.floor(local/1.5)):1});return;}
  twoCards('OCCUPIED','YOUR BACKUP',{leftColor:C.coral,rightColor:C.lime});machine(295,825,1.0,C.coral);dumbbell(695,826,1.15,C.lime);arrow(466,827,521,827);
  for(let i=0;i<3;i++)person(223+i*70,927,C.muted,.5);
  pill(idx===3?'A DIFFERENT EXERCISE NEEDS ITS OWN LOG':'PREPARE THE DECISION BEFORE YOU ARRIVE',140,1020,710,C.paper,25);
 }
 function trainingLog(){
  const machineLog=tl.episode.id==='N16';
  if(machineLog&&idx<=1){twoCards('MACHINE A','MACHINE B');machine(295,835,1.05,C.lime);machine(695,835,1.05,C.blue);text('SAME LABEL?',495,1030,44,C.cream,'center',720);return;}
  if(machineLog&&idx>=2){
   ['A','B'].forEach((name,i)=>{const x=126+i*400;card(x,655,340,377);pill('LOG '+name,x+40,676,260,i?C.blue:C.lime);['MACHINE','SETTING','LOAD','REPS'].forEach((s,j)=>{text(s,x+25,760+j*57,24,C.muted,'left',140);line(x+198,779+j*57,x+309,779+j*57,C.cream,3);});});return;
  }
  card(125,651,740,390);text('SESSION',155,680,25,C.muted);text('PERFORMANCE',384,680,25,C.muted);text('CONTEXT',708,680,25,C.muted,'left',130);
  ['PREVIOUS','LAST','TODAY'].forEach((s,i)=>{const y=752+i*81;rect(143,y-9,704,67,i===2?'#345066':'#203C52',10);text(s,162,y+9,25,C.cream,'left',190);line(393,y+23,619,y+23,i===2?C.lime:C.line,8);text('?',759,y+2,40,i===2?C.coral:C.muted,'center',70);});
  if(idx===2||idx===4)pill('EXERCISE · LOAD · REPS · REST · SETUP',137,1050,716,C.lime,25);
  else text('COMPARE SIMILAR CONDITIONS',495,1060,29,C.cream,'center');
 }
 function rest(){
  if(idx>=4){list(['Planned recovery','Changing the setup','Waiting for equipment'],689,{active:0});return;}
  twoCards('SHORTER REST','LONGER REST');
  for(let i=0;i<2;i++){const x=295+i*400;g.beginPath();g.arc(x,838,106,0,Math.PI*2);g.strokeStyle=i?C.lime:C.blue;g.lineWidth=10;g.stroke();text(i?'3:00':'1:00',x,794,72,i?C.lime:C.cream,'center',250);}
  pill(idx===3?'A SPECIFIC TRIAL · NOT EVERY EXERCISE':'READ THE STUDY CONDITIONS',147,1020,696,C.paper,27);
 }
 function range(){
  if(idx>=4){list(['Which exercise?','Compared with what?','Which measured outcome?'],689,{active:idx===4?1:2});return;}
  twoCards('FULL RANGE','LENGTHENED PART');
  for(let i=0;i<2;i++){const x=295+i*400,y=837,r=103,start=Math.PI*.12,end=Math.PI*.88;g.beginPath();g.arc(x,y,r,start,end);g.strokeStyle=C.line;g.lineWidth=19;g.stroke();g.beginPath();g.arc(x,y,r,start,i?Math.PI*.46:end);g.strokeStyle=i?C.lime:C.blue;g.lineWidth=19;g.stroke();const a=i?mix(start,Math.PI*.46,p):mix(start,end,p);circle(x+r*Math.cos(a),y+r*Math.sin(a),17,C.cream);}
  text('CONCEPTUAL RANGE · NOT AN EXERCISE TUTORIAL',495,748,23,C.muted,'center',790);
  pill(idx===3?'SMALL STUDY ≠ UNIVERSAL EQUALITY':'SPECIFIC STUDIES · LIMITED GENERALIZATION',135,1020,720,C.paper,25);
 }
 function supersets(){
  if(idx===3||idx===4){list(['Keep equipment access practical','Watch exercise performance','Allow for extra effort'],689,{active:idx===3?0:1});return;}
  const yy=[738,936];text('ILLUSTRATIVE TIMELINES · NO FIXED TIME SAVING',495,652,25,C.muted,'center',790);
  ['SEPARATE SETS','SUPERSET PAIR'].forEach((s,i)=>text(s,132,yy[i]-55,30,i?C.lime:C.cream));
  const blocks=[[[148,'A',C.blue],[232,'REST',C.line],[148,'B',C.lime]],[[148,'A',C.blue],[148,'B',C.lime],[122,'REST',C.line]]];
  blocks.forEach((row,i)=>{let x=135;row.forEach(([w,s,c])=>{rect(x,yy[i],w,88,c,16);text(s,x+w/2,yy[i]+26,29,c===C.line?C.cream:C.navy,'center',w-18);x+=w+18;});});
  text('HIGHER PERCEIVED EFFORT',495,1051,29,C.coral,'center');
 }
 function soreness(){
  if(idx>=4){list(['Completed training','Comparable performance records','A pattern across time'],689,{active:1});return;}
  twoCards('SORENESS','GROWTH MEASURED',{leftColor:C.coral,rightColor:C.blue});
  circle(295,840,86,C.coral);circle(268,825,7,C.navy);circle(322,825,7,C.navy);line(267,870,322,870,C.navy,7);
  rect(660,754,70,170,C.blue,9);for(let j=0;j<7;j++)line(660,776+j*21,681+(j%2?0:12),776+j*21,C.navy,4);
  text('≠',495,798,85,C.cream,'center',80);pill(idx===3?'DO NOT ADD SETS JUST TO CHASE SORENESS':'DIFFERENT QUESTIONS',140,1020,710,C.paper,26);
 }
 function program(){
  if(idx>=2){list(['A clear goal and schedule','Planned work and effort','A way to progress'],689,{active:idx===2?0:idx===3?1:2});return;}
  for(let i=0;i<3;i++){const x=155+i*213,y=679+i*34;card(x,y,244,282,i?C.paper:C.lime);text(['S','A','B'][i],x+122,y+49,116,C.navy,'center',210,700);text('AN IDEA',x+122,y+200,27,C.navy,'center',200);}
  pill('IDEAS STILL NEED A WEEKLY PLAN',170,1020,650,C.paper,28);
 }
 function split(){
  if(idx>=4){calendar();return;}
  twoCards('FULL BODY','SPLIT');
  for(let i=0;i<2;i++)for(let j=0;j<6;j++){const x=224+(j%2)*137+i*400,y=790+Math.floor(j/2)*65;rect(x-37,y,74,42,j%2?C.blue:C.lime,10);}
  pill(idx===3?'DIFFERENT WEEKLY WORK? DIFFERENT COMPARISON.':'THE COMPARISON MATCHED WEEKLY VOLUME',125,1020,740,C.paper,24);
 }
 function volume(){
  if(idx>=4){list(['Complete the current plan','Review comparable performance','Track one deliberate change'],689,{active:idx===4?1:2});return;}
  text('MORE WEEKLY WORK',495,651,36,C.cream,'center');
  for(let i=0;i<3;i++){const x=210+i*270;rect(x-77,745,154,175,C.blue,18);line(x,765,x,900,C.navy,3);text('+ WORK',x,800,29,C.navy,'center',140);const len=[115,78,49][i];arrow(x,1000,x,1000-len,C.lime,10);}
  text('SMALLER EXTRA BENEFITS',495,1040,32,C.lime,'center');
  if(idx===2)pill('GROUP EVIDENCE ≠ YOUR PERSONAL TARGET',139,704,712,C.paper,25);
 }
 const visuals={N01:calendar,N02:effort,N03:equipment,N04:reps,N05:effort,N06:route,N07:trainingLog,N08:rest,N09:equipment,N10:range,N11:supersets,N12:soreness,N13:program,N14:split,N15:volume,N16:trainingLog};
 let cursor=0;const cueOffsets=tl.captions.map(c=>{const a=cursor;cursor+=norm(c.text).length;return a;});
 function captionsAt(c,ci){
  const h=c.lines.length*57+34;rect(76,1183,844,h,C.navy,22);let pos=cueOffsets[ci];
  c.lines.forEach((s,i)=>{
   let size=43;while(glyph(s,size)>794&&size>35)size--;
   const x=498-glyph(s,size)/2,y=1200+i*57;
   text(s,498,y,size,C.cream,'center',794);
   let advance=0;for(const token of s.split(' ')){const n=norm(token).length;const active=(tl.words||[]).some(w=>w.b>pos&&w.a<pos+n&&t>=w.start&&t<w.end);if(active){const ww=glyph(token,size);rect(x+advance-2,y+size+4,ww+4,4,C.lime,2);}pos+=n;advance+=glyph(token+' ',size);}
  });
 }
 function frame(time,{burn=captions}={}){
  t=time;checks.length=0;g.resetTransform();g.scale(width/1080,width/1080);g.fillStyle=C.cream;g.fillRect(0,0,1080,1920);
  // Quiet framing leaves the platform overlays clear; no information below 1510.
  for(let x=0;x<1080;x+=90)line(x,180,x,1570,'#ECEDE2',1);
  rect(58,590,886,561,C.shadow,35);rect(70,576,860,568,C.navy,35);
  idx=tl.beats.findIndex(b=>t>=b.start&&t<b.end);if(idx<0)idx=tl.beats.length-1;
  local=Math.max(0,t-tl.beats[idx].start);p=motion?ease(local/.55):1;
  rect(78,252,288,56,C.navy,28);
  text('REP & REASON',222,265,27,C.cream,'center',260);
  text(tl.episode.id+' · '+tl.episode.pillar.toUpperCase(),914,270,24,C.navy,'right',370);
  tl.episode.graphics.headlines[idx].forEach((s,i)=>text(s,78,354+i*96+(motion?8*(1-p):0),84,C.navy,'left',837,700));
  for(let j=0;j<6;j++){rect(80+j*142,547,127,5,'#C8D0BE',2);if(j<=idx)rect(80+j*142,547,127*(j<idx?1:clamp((t-tl.beats[idx].start)/(tl.beats[idx].end-tl.beats[idx].start))),5,C.navy,2);}
  visuals[tl.episode.id]();scope();
  const ci=tl.captions.findIndex(c=>t>=c.start&&t<c.end);if(burn&&ci>=0)captionsAt(tl.captions[ci],ci);
  text(tl.timing==='estimated_visual_draft'?'STORYBOARD · FINAL VOICE TIMING PENDING':'KNOW WHY. TRAIN BETTER.',80,1450,25,C.navy,'left',830);
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
