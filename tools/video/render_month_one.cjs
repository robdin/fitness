/* Exact short-form graphics. No generated numeric labels or external assets. */
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process'),{once}=require('node:events');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..');
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
const C={navy:'#10233E',deep:'#081524',cream:'#F7F4EA',lime:'#B9F227',blue:'#74B9FF',coral:'#FF8B6B',muted:'#B4C3D1',line:'#385269'};
const clamp=x=>Math.min(1,Math.max(0,x)),ease=x=>1-Math.pow(1-clamp(x),3),mix=(a,b,p)=>a+(b-a)*p;
function createRenderer(tl,{width=1080,treatment='motion',captions=true}={}){
 const canvas=createCanvas(width,Math.round(width*16/9)),g=canvas.getContext('2d'),checks=[];
 const scale=width/1080;
 function rect(x,y,w,h,color,r=18,stroke){g.beginPath();g.roundRect(x,y,w,h,r);if(color){g.fillStyle=color;g.fill();}if(stroke){g.strokeStyle=stroke;g.lineWidth=2;g.stroke();}}
 function line(x,y,xx,yy,color=C.muted,w=3){g.beginPath();g.moveTo(x,y);g.lineTo(xx,yy);g.strokeStyle=color;g.lineWidth=w;g.stroke();}
 function circle(x,y,r,color){g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fillStyle=color;g.fill();}
 function text(s,x,y,size=40,color=C.cream,align='left',max=820,weight=600){
   let actual=size;g.textBaseline='top';g.textAlign=align;
   do{g.font=`${weight} ${actual}px Space`;if(g.measureText(s).width<=max)break;actual--;}while(actual>21);
   let w=g.measureText(s).width;const left=align==='center'?x-w/2:align==='right'?x-w:x;
   checks.push({text:s,size:actual,x:left,y,width:w,right:left+w,bottom:y+actual*1.18});
   g.fillStyle=color;g.fillText(s,x,y);
 }
 function label(s,y=1030,color=C.muted){text(s,490,y,25,color,'center',810);}
 function pill(s,x,y,color=C.lime,w=300){rect(x,y,w,50,color,25);text(s,x+w/2,y+11,25,C.navy,'center',w-28);}
 function arrow(x,y,xx,yy,color=C.lime){line(x,y,xx,yy,color,6);const a=Math.atan2(yy-y,xx-x);line(xx,yy,xx-18*Math.cos(a-.6),yy-18*Math.sin(a-.6),color,6);line(xx,yy,xx-18*Math.cos(a+.6),yy-18*Math.sin(a+.6),color,6);}
 function bell(x,y,s=1,color=C.lime){g.save();g.translate(x,y);g.scale(s,s);rect(-65,-8,130,16,color,5);for(const k of[-1,1]){rect(k*53-12,-40,24,80,color,5);rect(k*76-8,-28,16,56,color,5);}g.restore();}
 function person(x,y,color=C.lime){circle(x,y,16,color);rect(x-22,y+25,44,72,color,12);line(x-12,y+90,x-23,y+139,color,14);line(x+12,y+90,x+23,y+139,color,14);}
 function card(x,y,w,h,title,sub,color=C.lime){rect(x,y,w,h,'#182F46',20,C.line);text(title,x+w/2,y+28,52,color,'center',w-28);if(sub)text(sub,x+w/2,y+h-50,24,C.cream,'center',w-28);}
 function header(ep,beat,idx,t){
   text('REP & REASON',80,285,25,C.cream);text(ep.id+' / '+ep.pillar.toUpperCase(),900,288,21,C.muted,'right',310);
   const headlines={question:ep.cover,example:['LOOK AT THE','ACTUAL NUMBERS.'],buckets:['FOUR JOBS.','ONE SESSION.'],caveat:['KEEP THE','CONTEXT.'],action:['ONE USEFUL','NEXT STEP.'],close:['KNOW WHY.','TRAIN BETTER.'],goal:['WHAT IS','THE GOAL?'],constraints:['MAKE THE','LIMITS VISIBLE.'],relative:['+1 POINT.','+50 PERCENT.'],study:['WHAT WAS','ACTUALLY TESTED?'],result:['READ THE','SPECIFIC RESULT.'],before:['SPOT THE','REPEATED TRIP.'],map:['FIND THE','AVOIDABLE LOOP.'],sample:['8 PEOPLE.','PAIRED LEGS.'],full:['90 AND 100.','START AT ZERO.'],zoom:['SAME SCORES.','DIFFERENT SCALE.'],detail:['RECORD THE','MISSING CONTEXT.'],many:['FIVE CHANGES.','WHICH HELPED?'],one:['TRY ONE','SETUP CHANGE.'],timeline:['BEFORE. AFTER.','EIGHT WEEKS.'],who:['WHO WAS','STUDIED?'],what:['COMPARED','WITH WHAT?'],outcome:['WHICH OUTCOME?','OVER HOW LONG?']};
   const recap={who:['WHERE DID','THE TIME GO?'],what:['WHY THIS','EXERCISE?'],outcome:['WHAT WOULD','CHANGE YOUR MIND?']};
   const lines=(ep.id==='M16'&&recap[beat.kind])||headlines[beat.kind]||ep.cover; const p=treatment==='motion'?ease((t-beat.start)/.28):1;
   lines.forEach((s,i)=>text(s,78,352+i*97+10*(1-p),88,i?C.lime:C.cream,'left',830,700));
   for(let j=0;j<tl.beats.length;j++){rect(80+j*138,560,120,5,C.line,2);if(j<=idx)rect(80+j*138,560,120*(j<idx?1:clamp((t-beat.start)/(beat.end-beat.start))),5,C.lime,2);}
 }
 function audit(k,p,local,t){
   const values=[15,25,8,12],colors=[C.lime,C.cream,C.blue,C.coral],names=['LIFT','REST','SETUP','WAIT'];
   const isHook=k==='question';const full=['buckets','caveat','action','close'].includes(k);
   const reveal=['fifteen','twentyfive','eight','twelve'].filter(key=>t>=(tl.markers?.[key]??Infinity)).length;
   const compact=treatment==='compact',cell=compact?42:66,gap=compact?9:12,ox=compact?80:102,oy=compact?716:649;
   const morph=treatment==='motion'?ease((t-tl.beats[1].start)/.7):(isHook?0:1);
   let index=0;
   for(let group=0;group<4;group++)for(let n=0;n<values[group];n++){
     let a=index/60*Math.PI*2-Math.PI/2,rx=490+226*Math.cos(a),ry=808+226*Math.sin(a);
     const x=mix(rx,ox+(index%10)*(cell+gap)+cell/2,morph),y=mix(ry,oy+Math.floor(index/10)*(compact?(cell+gap):58)+(compact?cell/2:23),morph);
     const size=mix(12,cell,morph);
     const height=mix(12,compact?cell:46,morph);
     rect(x-size/2,y-height/2,size,height,group<reveal?colors[group]:C.line,Math.min(8,size/3));index++;
   }
   if(morph<.98){text('60',490,698,185,C.cream,'center',500,700);text('MINUTES',490,900,35,C.lime,'center');}
   if(morph>.5){
     if(compact){names.forEach((s,i)=>{text(values[i]+'',670,674+i*89,53,colors[i]);text(s,761,690+i*89,26,C.cream);});}
     else names.forEach((s,i)=>{text(i<reveal?values[i]+'':'—',185+i*205,1022,41,colors[i],'center');text(s,185+i*205,1067,22,C.muted,'center');});
   }
   if(isHook)label('THE CLOCK DOES NOT TELL THE WHOLE STORY',1063);
   else if(k!=='caveat')label('INVENTED MINUTES · NOT A TARGET',610,C.coral);
   if(k==='caveat')text('INVENTED EXAMPLE',490,995,22,C.coral,'center');
   if(k==='caveat')pill('LARGEST ≠ WASTE',315,594,C.lime,350);
 }
 function decision(k,p){
   const goal=k==='goal',cons=k==='constraints',action=['action','close'].includes(k);
   card(80,654,360,172,'THE GOAL','Why this exercise?',goal?C.lime:C.cream);
   card(540,654,360,172,'THE LIMIT','What is available?',cons?C.lime:C.blue);
   arrow(440,740,530,740,C.coral);
   arrow(260,839,440,929,C.line);arrow(720,839,540,929,C.line);
   rect(215,928,550,113,action?C.lime:'#243E52',24);
   text(k==='caveat'?'SAME LABEL ≠ SAME TASK':'A CONTEXTUAL CHOICE',490,966,34,action?C.navy:C.cream,'center',510);
   label('A DECISION CHECKLIST · NOT A SWAP PRESCRIPTION',1083);
 }
 function relative(k,p){
   const progressed=['relative','caveat','action','close'].includes(k);
   text('2',260,627,180,C.cream,'center');arrow(397,742,584,742);text('3',744,627,180,C.lime,'center');
   for(let i=0;i<2;i++)rect(177,838+i*54,166,40,C.cream,7);
   for(let i=0;i<3;i++)rect(661,784+i*54,166,40,i===2?C.lime:C.cream,7);
   if(progressed){pill('+1 POINT',104,1000,C.blue,340);pill('+50%',536,1000,C.lime,340);}
   label('INVENTED SCORE · (3 − 2) ÷ 2 = 50%',1080,C.muted);
 }
 function rest(k,p){
   const result=['result','caveat','action','close'].includes(k);
   for(let i=0;i<2;i++){
     const x=270+i*440;g.beginPath();g.arc(x,785,132,0,Math.PI*2);g.lineWidth=17;g.strokeStyle=i?C.lime:C.blue;g.stroke();
     const a=-Math.PI/2+(i?3:1)*Math.PI/2*(treatment==='motion'?p:1);line(x,785,x+80*Math.cos(a),785+80*Math.sin(a),C.cream,8);
     text(i?'3 MIN':'1 MIN',x,964,42,i?C.lime:C.blue,'center');
   }
   if(result)label(k==='caveat'?'NOT A UNIVERSAL REST RULE':'GREATER SQUAT / BENCH GAINS: 3-MIN GROUP',608,C.lime);
   label('21 TRAINED YOUNG MEN · 8 WEEKS · 2016 TRIAL',1066);
 }
 function route(k,p,local){
   card(80,660,280,178,'STATION','Your exercise',C.lime);card(620,660,280,178,'EQUIPMENT','Shared space',C.blue);
   bell(220,915,.8);bell(760,915,.8,C.blue);
   for(let i=0;i<3;i++){
     const y=856+i*62;g.beginPath();g.moveTo(360,y);g.bezierCurveTo(440,y-60,540,y+60,620,y);g.strokeStyle=C.line;g.lineWidth=4;g.stroke();
     if(['question','before','map'].includes(k)){const q=treatment==='motion'?(local*.3+i*.3)%1:.5;circle(360+260*q,y+Math.sin(q*Math.PI*2)*20,12,C.coral);}
   }
   if(['action','caveat','close'].includes(k))pill(k==='caveat'?'KEEP EQUIPMENT SHARED':'CHECK THE SETUP FIRST',195,990,C.lime,590);
   label('ILLUSTRATIVE ROUTE · NO TIME SAVINGS CLAIM',1080);
 }
 function sample(k,p){
   for(let i=0;i<8;i++){
     const x=155+(i%4)*222,y=642+Math.floor(i/4)*210;person(x,y,i<4?C.lime:C.blue);
     circle(x-23,y+139,10,C.coral);circle(x+23,y+139,10,C.cream);
     text(String(i+1),x,y+156,24,C.muted,'center');
   }
   label(k==='result'?'COMPARABLE GROWTH IN MEASURED THIGH REGIONS':'8 WOMEN · 9 WEEKS · TWO LEGS PER PERSON',1058,C.cream);
   label('SMALL, SPECIFIC COMPARISON · NOT UNIVERSAL EQUIVALENCE',1082,C.muted);
 }
 function budget(k,p){
   const half=['constraints','action','close'].includes(k);
   text('30',490,623,184,C.lime,'center');text('MINUTES AVAILABLE',490,824,31,C.cream,'center');
   for(let i=0;i<12;i++)rect(93+i*67,910,53,78,i<6?C.lime:C.line,9);
   line(490,892,490,1010,C.coral,6);
   text('YOUR WINDOW',290,1019,26,C.lime,'center');text('DOES NOT FIT',705,1019,26,C.coral,'center');
   label('ILLUSTRATIVE CONSTRAINT · NOT A WORKOUT',1090);
 }
 function axis(k,p){
   const zoom=['zoom','caveat','action','close'].includes(k),min=zoom?80:0;
   const bottom=1000,top=660,left=235,right=835;
   for(let i=0;i<3;i++){const value=min+(100-min)*i/2,y=bottom-(value-min)/(100-min)*(bottom-top);line(left,y,right,y,C.line,2);text(String(value),197,y-17,28,C.muted,'right');}
   for(let i=0;i<2;i++){const value=90+i*10,h=(value-min)/(100-min)*(bottom-top);rect(305+i*290,bottom-h,160,h,i?C.lime:C.blue,3);text(String(value),385+i*290,bottom-h-55,45,C.cream,'center');text(i?'B':'A',385+i*290,1020,30,C.muted,'center');}
   text('SCORE',112,591,22,C.muted);label('INVENTED SCORES · AXIS STARTS AT '+min,1080,zoom?C.coral:C.muted);
 }
 function log(k,p){
   for(let i=0;i<2;i++){const x=80+i*430;rect(x,650,390,370,'#193249',22,C.line);text(i?'GYM B':'GYM A',x+195,684,30,C.muted,'center');text('50',x+195,742,136,i?C.blue:C.lime,'center');
     text(['detail','action','close'].includes(k)?(i?'MACHINE B · kg':'MACHINE A · lb'):'WHICH MACHINE? UNITS?',x+195,924,25,C.cream,'center',355);}
   label('ILLUSTRATIVE LOG · MATCHING NUMBERS ≠ SAME TASK',1080);
 }
 function variables(k,p){
   const one=['one','action','close'].includes(k),names=['TIME','GYM','EXERCISE','REST','SETUP'];
   names.forEach((s,i)=>{let y=638+i*81;rect(110,y,760,63,one&&i===4?C.lime:'#1D354C',14);text(s,145,y+17,27,one&&i===4?C.navy:C.cream);rect(712,y+14,116,35,one&&i!==4?C.line:C.coral,18);circle(one&&i!==4?730:810,y+31,12,C.cream);});
   label(one?'ONE CHANGE · STILL NOT CAUSAL PROOF':'MANY CHANGES · MANY POSSIBLE EXPLANATIONS',1085);
 }
 function weeks(k,p){
   const progress=treatment==='motion'?p:1;
   for(let i=0;i<8;i++){const x=100+(i%4)*205,y=666+Math.floor(i/4)*152;rect(x,y,175,120,i<=Math.floor(progress*7)?C.lime:'#1E354C',19);text('WEEK '+(i+1),x+87,y+43,30,i<=Math.floor(progress*7)?C.navy:C.muted,'center');}
   line(140,1010,840,1010,C.muted);circle(140,1010,9,C.blue);circle(840,1010,9,C.lime);text('PRETEST',140,1040,28,C.blue);text('POSTTEST',840,1040,28,C.lime,'right');
   label('STUDY TIME HORIZON · NOT YOUR PERSONAL FORECAST',1080);
 }
 function checklist(k,p){
   const recap=tl.episode.id==='M16',items=recap?['WHERE DID TIME GO?','WHY THIS EXERCISE?','WHAT WOULD CHANGE?']:['WHO WAS STUDIED?','WHAT WAS COMPARED?','WHICH OUTCOME?'];
   const active={who:0,what:1,outcome:2}[k];
   items.forEach((s,i)=>{const y=665+i*136;rect(90,y,800,105,active===i?C.lime:'#1C354C',21);text(String(i+1).padStart(2,'0'),130,y+28,42,active===i?C.navy:C.lime);text(s,235,y+34,34,active===i?C.navy:C.cream,'left',620);});
   label('A STARTING QUESTION · NOT A COMPLETE APPRAISAL',1080);
 }
 const visuals={audit,decision,relative,rest,route,sample,budget,axis,log,variables,weeks,checklist};
 function frame(t,{burn=captions}={}){
   checks.length=0;g.resetTransform();g.scale(scale,scale);
   const bg=g.createLinearGradient(0,0,1080,1920);bg.addColorStop(0,C.deep);bg.addColorStop(.5,C.navy);bg.addColorStop(1,'#07111E');g.fillStyle=bg;g.fillRect(0,0,1080,1920);
   // Large tonal shapes create depth without competing with factual marks.
   g.globalAlpha=.12;circle(1120,620,430,C.blue);circle(-180,1480,550,C.lime);g.globalAlpha=1;
   let idx=tl.beats.findIndex(b=>t>=b.start&&t<b.end);if(idx<0)idx=tl.beats.length-1;
   const b=tl.beats[idx],local=Math.max(0,t-b.start),p=treatment==='motion'?ease(local/.65):1;
   header(tl.episode,b,idx,t);
   visuals[tl.episode.visual](b.kind,p,local,t);
   const c=tl.captions.find(c=>t>=c.start&&t<c.end);
   if(burn&&c){const h=c.lines.length*51+24;rect(70,1120,850,h,'#050E1A',15);c.lines.forEach((s,i)=>text(s,495,1132+i*51,43,C.cream,'center',816));}
   text(tl.timing==='estimated_visual_draft'?'VISUAL DRAFT · VOICE TIMING PENDING':'KNOW WHY. TRAIN BETTER.',80,1450,22,C.muted,'left',810);
   return canvas;
 }
 return {canvas,frame,checks};
}
async function main(){
 const args=process.argv.slice(2),tl=JSON.parse(fs.readFileSync(args[0])),out=path.resolve(args[1]);
 fs.mkdirSync(out,{recursive:true});let treatment=args.includes('--treatment')?args[args.indexOf('--treatment')+1]:'motion';
 const width=args.includes('--width')?Number(args[args.indexOf('--width')+1]):1080;
 const r=createRenderer(tl,{width,treatment,captions:!args.includes('--clean')});
 if(args.includes('--stills')){
   const report=[];
   for(let i=0;i<tl.beats.length;i++){const t=tl.beats[i].start+Math.min(1.2,(tl.beats[i].end-tl.beats[i].start)/2);r.frame(t);fs.writeFileSync(path.join(out,`scene-${i}.png`),r.canvas.toBuffer('image/png'));report.push({time:t,text:[...r.checks]});}
   r.frame(.18);fs.writeFileSync(path.join(out,'cover.png'),r.canvas.toBuffer('image/png'));
   fs.writeFileSync(path.join(out,'layout.json'),JSON.stringify(report,null,2));return;
 }
 const first=args.includes('--range')?Number(args[args.indexOf('--range')+1]):0;
 const count=args.includes('--range')?Number(args[args.indexOf('--range')+2]):Math.round(tl.duration*30);
 const last=Math.min(Math.round(tl.duration*30),first+count);
 const file=path.join(out,`segment-${String(first).padStart(5,'0')}.mp4`);
 const ff=spawn('ffmpeg',['-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${r.canvas.width}x${r.canvas.height}`,'-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',file],{stdio:['pipe','inherit','inherit']});
 const finished=once(ff,'close');ff.stdin.on('error',()=>{});
 for(let f=first;f<last;f++){r.frame(f/30);const data=r.canvas.data();if(!ff.stdin.write(data))await once(ff.stdin,'drain');}
 ff.stdin.end();const [code]=await finished;if(code!==0)throw Error('FFmpeg failed: '+code);
 console.log(file);
}
module.exports={createRenderer};
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
