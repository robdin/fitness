/* Blueprint: aspiration in the cover, precision in the explanation. */
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process'),{once}=require('node:events');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..'),C=JSON.parse(fs.readFileSync(path.join(ROOT,'brand/blueprint/tokens.json')));
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
GlobalFonts.registerFromPath(path.join(ROOT,'brand/blueprint/fonts/Fraunces-Italic.ttf'),'Dream');
const clamp=x=>Math.max(0,Math.min(1,x)),ease=x=>1-(1-clamp(x))**3;
async function createRenderer(tl,{width=1080,treatment='motion',captions=true}={}){
 const design=tl.episode.graphics,brand=design.brand;if(brand!=='blueprint')throw Error('Blueprint renderer needs Blueprint content');
 const canvas=createCanvas(width,Math.round(width*16/9)),g=canvas.getContext('2d'),checks=[];let idx=0,local=0,p=1,t=0,diagram=false;
 const motion=treatment==='motion',dark=false,club=true,paper=false;
 const graphicInk=dark?'#F4F7EF':C.ink,chipInk=C.panelInk;
 function rect(x,y,w,h,c,r=C.radius){g.fillStyle=c;g.beginPath();g.roundRect(x,y,w,h,r);g.fill();}
 function line(x,y,xx,yy,c,w=5){g.strokeStyle=c;g.lineWidth=w;g.lineCap='round';g.beginPath();g.moveTo(x,y);g.lineTo(xx,yy);g.stroke();}
 function dot(x,y,r,c){g.fillStyle=c;g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fill();}
 function text(s,x,y,size=42,color=C.ink,align='left',max=820,weight=C.weight,family='Space'){
  const font=n=>{g.font=`${weight} ${n}px ${family}`;};font(size);while(g.measureText(s).width>max&&size>24)font(--size);
  const w=g.measureText(s).width,left=align==='center'?x-w/2:align==='right'?x-w:x;
  const box={text:s,x:left,y,size,width:w,right:left+w,bottom:y+size*1.2,color,brand};
  if(diagram){box.y+=32;box.bottom+=32;}checks.push(box);
  g.textAlign=align;g.textBaseline='top';g.fillStyle=color;g.fillText(s,x,y);
 }
 function tick(x,y,c){line(x-13,y,x-1,y+12,c,7);line(x-1,y+12,x+24,y-18,c,7);}
 function arrow(x,y,xx,yy,c=C.accent,w=9){line(x,y,xx,yy,c,w);let a=Math.atan2(yy-y,xx-x);line(xx,yy,xx-24*Math.cos(a-.65),yy-24*Math.sin(a-.65),c,w);line(xx,yy,xx-24*Math.cos(a+.65),yy-24*Math.sin(a+.65),c,w);}
 function tag(s,y=1078){const bg=paper?C.accent:club?C.ink:C.accent,fg=paper?C.accentInk:club?C.bg:C.accentInk;rect(100,y,800,62,bg);text(s,500,y+13,30,fg,'center',764);}
 function rows(items,active=Math.min(2,idx),y=640){items.forEach((s,i)=>{let yy=y+i*143,selected=i===active;const bg=selected?C.accent:paper?C.panel:club?C.panel:'#203650',fg=selected?C.accentInk:C.panelInk;rect(100,yy,800,116,bg);text(String(i+1).padStart(2,'0'),131,yy+30,42,fg);text(s,232,yy+33,40,fg,'left',625);if(selected&&idx>0)tick(849,yy+55,fg);});}
 function two(a,b){for(let i=0;i<2;i++){let x=100+i*420;rect(x,632,380,400,paper?C.panel:club?C.panel:'#203650');text(i?b:a,x+190,661,30,C.panelInk,'center',346);} }
 const objectColor=C.panelInk;
 function machine(x,y,scale=1,c=objectColor){g.save();g.translate(x,y);g.scale(scale,scale);line(-72,110,75,110,c,11);line(-62,105,-62,-110,c,11);line(-62,-110,68,-110,c,11);line(68,-110,68,110,c,11);for(let j=0;j<5;j++)rect(-39,-59+j*23,60,16,c,3);line(44,-93,44,-8,c,5);line(26,-8,63,-8,c,8);rect(-13,64,85,18,c,4);g.restore();}
 function dumbbell(x,y,s=1,c=objectColor){g.save();g.translate(x,y);g.scale(s,s);rect(-82,-10,164,20,c,5);for(let sign of [-1,1]){rect(sign*65-15,-58,30,116,c,6);rect(sign*94-10,-43,20,86,c,6);}g.restore();}
 function sevenDay(){const days=['M','T','W','T','F','S','S'];days.forEach((s,i)=>{const x=100+i*116,gym=i===1||i===5;rect(x,710,104,228,gym?C.accent:paper?C.panel:club?C.panel:'#203650');text(s,x+52,735,38,gym?C.accentInk:C.panelInk,'center',80);if(gym){text('GYM',x+52,831,26,C.accentInk,'center',90);tick(x+50,895,C.accentInk);}else text('—',x+52,830,40,C.panelInk,'center',80);});}
 function exampleCard(card){
  rect(100,650,800,412,C.panel);
  text(card.title,132,674,33,C.panelInk,'left',736,700);
  card.rows.forEach((copy,i)=>{
   const yy=735+i*101;dot(142,yy+16,6,C.bg);
   g.font='600 35px Space';let lines=[],row='';
   for(const word of copy.split(' ')){const next=(row?row+' ':'')+word;if(g.measureText(next).width>690&&row){lines.push(row);row=word;}else row=next;}
   if(row)lines.push(row);if(lines.length>2)throw Error('Example row too long: '+copy);
   lines.forEach((line,j)=>text(line,166,yy+j*43,35,C.panelInk,'left',696,600));
  });
  tag(card.footer);
 }
 function graphic(){
  if(design.example_card?.show_beats.includes(idx)){exampleCard(design.example_card);return;}
  const k=design.kind;
  if(['checklist','weight','scorecard','program'].includes(k)){rows(design.labels,Math.min(2,Math.max(0,idx-1)));tag(design.base_tag||(k==='weight'?'NO UNIVERSAL STARTING NUMBER':k==='scorecard'?'REVIEW YOUR PROCESS':k==='program'?'A PLAN YOU CAN FOLLOW':'BEFORE YOU WALK IN'));}
  else if(k==='machine'){two('MACHINE','FREE WEIGHT');machine(290,873,1.1);dumbbell(710,873,1.25);if(idx>=4){rect(131,963,318,45,C.accent);text('SAVE SETTINGS',290,970,25,C.accentInk,'center',300);}tag(idx===3?'EACH EXERCISE HAS A PURPOSE':'LEARN THE SETUP');}
  else if(k==='timer'){two('SHORTER REST','LONGER REST');for(let i=0;i<2;i++){const x=290+i*420;g.beginPath();g.arc(x,842,105,0,Math.PI*2);g.strokeStyle=objectColor;g.lineWidth=14;g.stroke();const a=-Math.PI/2+(motion?p:1)*Math.PI*(i?1.7:.6);line(x,842,x+76*Math.cos(a),842+76*Math.sin(a),objectColor,8);text(i?'3:00':'1:00',x,957,37,C.panelInk,'center',280);}tag(idx>=3?'NOT A RULE FOR EVERY EXERCISE':'ONE SMALL STUDY IN TRAINED MEN');}
  else if(k==='sets'){for(let r=0;r<3;r++){let yy=640+r*143;rect(100,yy,800,117,paper?C.panel:club?C.panel:'#203650');text('SET '+(r+1),124,yy+17,26,C.panelInk);for(let j=0;j<8;j++){let active=idx===0||idx>1||j<Math.ceil(p*8);dot(296+j*78,yy+59,25,active?objectColor:dark?'#66809F':'#7D8B75');}if(r<2)text('REST',865,yy+118,20,C.muted,'right',120);}tag('3 SETS × 8 REPS · EXAMPLE');}
  else if(k==='soreness'){two('SORENESS','TRAINING LOG');dot(290,858,97,objectColor);dot(261,838,8,C.panel);dot(319,838,8,C.panel);line(256,889,324,889,C.panel,8);for(let i=0;i<3;i++){rect(585,780+i*70,45,45,objectColor,6);tick(607,803+i*70,C.panel);line(659,803+i*70,827,803+i*70,C.panelInk,6);}tag('A FEELING IS NOT A GROWTH MEASURE');}
  else if(k==='reps'){two('LAST TIME','TODAY');text('8',290,753,180,C.panelInk,'center',300,700);const at=tl.words?.find(w=>w.text.toLowerCase().replace(/[^a-z]/g,'')==='nine')?.start;const revealed=at!==undefined?t>=at:idx>=2;text(revealed?'9':'?',710,753,180-(motion&&revealed?10*(1-ease((t-(at??tl.beats[2].start))/.55)):0),objectColor,'center',300,700);arrow(477,860,516,860,paper?C.accent:club?C.ink:C.accent,6);tag(idx>=3?'PERFORMANCE ≠ PROOF OF NEW MUSCLE':'SAME EXERCISE · SETUP · STOPPING RULE');}
  else if(k==='trip'){
   two('TIME TRAINING','THE WHOLE TRIP');
   rect(136,810,308,88,C.accent);text('YOUR SESSION',290,835,32,C.panelInk,'center',290);
   ['GET THERE','CHANGE + TRAIN','GET HOME'].forEach((label,i)=>{rect(554,743+i*89,312,70,i===1?C.accent:'#DCEAF5');text(label,710,761+i*89,31,C.panelInk,'center',294);});
   tag('USE YOUR ACTUAL TRAVEL AND SESSION TIMES');
  }
  else if(k==='calendar'){sevenDay();tag(idx===3?'DOES NOT COVER ALL ACTIVITY NEEDS':'AN ILLUSTRATIVE WEEK');}
  else if(k==='food'){two('FOOD','POWDER');dot(290,850,118,objectColor);dot(290,850,90,club?C.panel:paper?C.panel:'#203650');text('BEANS',290,794,32,C.panelInk,'center',200);text('TOFU',290,842,32,C.panelInk,'center',200);text('EGGS',290,890,32,C.panelInk,'center',200);rect(630,762,160,215,objectColor,18);rect(644,738,132,33,objectColor,8);text('OPTIONAL',710,844,29,C.panel,'center',146);tag(idx>=3?'A VARIED DIET STILL MATTERS':'MORE THAN ONE WAY TO GET PROTEIN');}
  else if(k==='trend'){rows(['EXERCISE + SETUP','LOAD + REPS','REST + STOPPING RULE'],idx>=4?2:Math.min(2,idx));tag('COMPARE SEVERAL SIMILAR SESSIONS');}
  else if(k==='backup'){two('OCCUPIED','YOUR BACKUP');machine(290,855,1.0);text('?',710,763,180,objectColor,'center',300,700);arrow(477,860,516,860,paper?C.accent:club?C.ink:C.accent,6);tag(idx>=3?'DIFFERENT MOVEMENT · SEPARATE LOG':'ASK FOR A SUITABLE ALTERNATIVE');}
  else if(k==='effort'){text('EFFORT',100,650,42,C.ink);rect(100,756,800,69,C.panelInk,35);rect(100,756,Math.max(70,610*p),69,C.accent,35);line(900,723,900,859,paper?C.accent:club?C.secondary:C.ink,8);text('CHALLENGING',100,891,35,C.ink);text('FAILURE',900,891,35,C.ink,'right',250);text('CONCEPTUAL SCALE',100,984,26,C.muted);tag('FOLLOW YOUR ROUTINE’S EFFORT TARGET');}
  else if(k==='log'){two('MACHINE A','MACHINE B');for(let i=0;i<2;i++){let x=132+i*420;['SETTING','LOAD','REPS'].forEach((s,j)=>{text(s,x,758+j*79,27,C.panelInk,'left',170);line(x+176,782+j*79,x+308,782+j*79,objectColor,5);});}tag('COMPARE EACH SETUP WITH ITSELF');}
  else if(k==='return'){two('MISSED','NEXT VISIT');text('×',290,755,172,C.panelInk,'center',280);rect(595,773,230,174,objectColor);tick(710,858,C.panel);arrow(477,860,516,860,paper?C.accent:club?C.ink:C.accent,6);tag(idx===3?'NO AUTOMATIC DOUBLE WORKOUT':'CHECK YOUR ROUTINE · PLAN THE RETURN');}
  else if(k==='walk'){
   rect(100,668,800,358,C.panel);
   text('AFTER LUNCH?',132,702,36,C.panelInk);text('FAMILIAR ROUTE',868,702,29,C.panelInk,'right',400);
   const end=190+620*(motion?p:1);line(190,862,end,862,C.panelInk,9);dot(190,862,18,C.panelInk);dot(end,862,22,C.panelInk);
   text('START',150,913,30,C.panelInk);text('YOUR RETURN',860,913,30,C.panelInk,'right',330);
   tag(idx===3?'PART OF A BROADER ACTIVITY PLAN':'PLANNING EXAMPLE · CHOOSE YOUR OWN ROUTE');
  }
  else if(k==='club-check'||k==='activity'){
   rows(design.labels,Math.min(2,Math.max(0,idx-1)));
   tag(k==='club-check'?'CHECK THE ACTUAL EVENT':'TRYOUT CHECKLIST · NO HABIT GUARANTEE');
  }
  else if(k==='groceries'){
   if(idx===2){
    ['BEANS','RICE','FROZEN VEG'].forEach((label,i)=>{const x=100+i*275;rect(x,700,250,310,C.panel);dot(x+125,825,65,C.panelInk);dot(x+125,825,46,C.panel);text(label,x+125,936,31,C.panelInk,'center',230);});
    tag('AN ADAPTABLE MEAL IDEA');
   }else{rows(design.labels,Math.min(2,Math.max(0,idx-1)));tag('CHECK FIRST · LIST WHAT IS MISSING');}
  }
  else if(k==='sleep'){
   two('BEDTIME','WAKE TIME');
   for(let i=0;i<2;i++){const x=290+i*420;g.beginPath();g.arc(x,838,91,0,Math.PI*2);g.strokeStyle=C.panelInk;g.lineWidth=9;g.stroke();const angle=-Math.PI/2+(motion?p:1)*Math.PI*(i?.8:1.3);line(x,838,x+58*Math.cos(angle),838+58*Math.sin(angle),C.panelInk,8);dot(x,838,8,C.panelInk);text('YOUR TIME',x,962,30,C.panelInk,'center',310);}
   tag('ILLUSTRATIVE CLOCKS · SET YOUR OWN');
  }
  else throw Error('Unknown graphic '+k);
 }
 function frame(time,{burn=captions}={}){
  t=time;idx=tl.beats.findIndex(b=>t>=b.start&&t<b.end);if(idx<0)idx=t<tl.beats[0].start?0:tl.beats.length-1;local=Math.max(0,t-tl.beats[idx].start);p=motion?ease(local/.6):1;checks.length=0;
  g.resetTransform();g.scale(width/1080,width/1080);g.fillStyle=C.bg;g.fillRect(0,0,1080,1920);
  if(dark){for(let x=60;x<1050;x+=80)line(x,190,x,1530,'#162D48',1);for(let y=190;y<1530;y+=80)line(60,y,1020,y,'#162D48',1);}
  if(club){
   const halo=g.createRadialGradient(600,1770,0,600,1770,480);halo.addColorStop(0,'#DDD6F5');halo.addColorStop(.45,'#6C82D8');halo.addColorStop(1,C.bg);g.fillStyle=halo;g.fillRect(0,1530,1080,390);
   for(let x=84;x<=916;x+=104)line(x,662,x,1168,'#667FD5',1);
   for(let y=662;y<=1168;y+=84)line(84,y,916,y,'#667FD5',1);
   line(84,323,914,323,'#94A8E0',1);
  }
  if(paper){rect(72,580,860,584,C.panel,28);line(118,604,118,1136,'#D8A28D',2);for(let y=637;y<1140;y+=64)line(135,y,909,y,'#E7DFD3',1);}
  text('BODY OF OUR DREAMS',84,260,28,C.ink,'left',620,600);
  text(design.series.toUpperCase(),84,298,22,C.muted,'left',400,500);
  text(tl.episode.id+' / '+tl.episode.pillar.toUpperCase(),915,298,22,C.muted,'right',830,500);
  design.headlines[idx].forEach((s,i)=>{const expressive=idx===0&&i===0;const copy=expressive?s.charAt(0)+s.slice(1).toLowerCase():s;text(copy,84,354+i*99,88,C.ink,'left',830,expressive?500:700,expressive?'Dream':'Space');});
  const phases=['START HERE','THE ANSWER','SEE IT','KEEP THE CONTEXT','YOUR NEXT STEP','TAKE IT WITH YOU'];
  rect(84,574,830,42,C.accent,4);text(phases[idx],101,581,25,C.accentInk,'left',796,700);
  for(let j=0;j<tl.beats.length;j++)rect(85+j*141,637,125,6,j<=idx?C.secondary:'#667FD5',2);
  g.save();g.translate(0,32);diagram=true;graphic();diagram=false;g.restore();
  text(design.scope_label,500,1206,25,C.muted,'center',820,500);
  if(design.source_cue_visible)text(design.source_cue.label,500,1250,27,C.secondary,'center',820,600);
  const ci=tl.captions.findIndex(c=>t>=c.start&&t<c.end);
  if(burn&&ci>=0){const c=tl.captions[ci];rect(76,1300,850,c.lines.length*60+32,C.panel,paper?22:8);c.lines.forEach((s,i)=>text(s,501,1315+i*60,43,C.panelInk,'center',798,600));}
  text(tl.timing==='estimated_visual_draft'?'VISUAL DRAFT · VOICE TIMING PENDING':C.tagline,84,1470,24,C.muted,'left',830,600);
  return canvas;
 }
 return {canvas,frame,checks};
}

async function main(){
 const args=process.argv.slice(2),tl=JSON.parse(fs.readFileSync(args[0])),out=path.resolve(args[1]);fs.mkdirSync(out,{recursive:true});
 const treatment=args.includes('--treatment')?args[args.indexOf('--treatment')+1]:'motion',width=args.includes('--width')?Number(args[args.indexOf('--width')+1]):1080;
 const r=await createRenderer(tl,{width,treatment,captions:!args.includes('--clean')});
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
