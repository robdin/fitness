/** Deterministic JS/Skia motion graphics, synchronized to the approved voice.
 * Install @napi-rs/canvas or supply NODE_PATH. Run after prepare_social_v3.py.
 * node tools/video/render_social_v3.cjs [work-dir] [output-dir] [--stills]
 */
const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const {once} = require('node:events');
const {createCanvas, loadImage, GlobalFonts} = require('@napi-rs/canvas');
const ROOT = path.resolve(__dirname, '../..');
const work = path.resolve(process.argv[2] || path.join(ROOT, '.local/social-v3'));
const out = path.resolve(process.argv[3] || work);
fs.mkdirSync(out, {recursive:true});
const tl = JSON.parse(fs.readFileSync(path.join(work, 'timeline.json')));
GlobalFonts.registerFromPath(path.join(ROOT, 'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'), 'Space Grotesk');
const W=1080,H=1920,FPS=30, cream='#F7F4EA',lime='#B9F227',blue='#74B9FF',coral='#FF8B6B',muted='#AABACD';
const colors=[lime,cream,blue,coral], values=[15,25,8,12], labels=['LIFTING','REST','SETUP','WAITING'];
const canvas=createCanvas(W,H),ctx=canvas.getContext('2d');
const clamp=x=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
const mix=(a,b,p)=>a+(b-a)*p;
function rect(x,y,w,h,r,fill,stroke){ctx.beginPath();ctx.roundRect(x,y,w,h,r);if(fill){ctx.fillStyle=fill;ctx.fill();}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.stroke();}}
function text(str,x,y,size=40,color=cream,weight=600,align='left'){
  ctx.font=`${weight} ${size}px "Space Grotesk"`;ctx.fillStyle=color;ctx.textAlign=align;ctx.textBaseline='top';ctx.fillText(str,x,y);
}
function line(x,y,xx,yy,color,width=3){ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(xx,yy);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function circle(x,y,r,color){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
function dumbbell(x,y,scale=1,color=lime){ctx.save();ctx.translate(x,y);ctx.scale(scale,scale);rect(-58,-8,116,16,5,color);for(let s of [-1,1]){rect(s*48-11,-33,22,66,6,color);rect(s*66-6,-23,12,46,4,color);}ctx.restore();}
const bg=createCanvas(W,H),b=bg.getContext('2d');
const grad=b.createLinearGradient(0,0,W,H);grad.addColorStop(0,'#081322');grad.addColorStop(.52,'#152E48');grad.addColorStop(1,'#081322');b.fillStyle=grad;b.fillRect(0,0,W,H);
for(let x=78;x<W;x+=48)for(let y=150;y<H;y+=48){b.fillStyle='#294158';b.fillRect(x,y,2,2);}
const clips={};
async function setup(){for(const name of ['minimax','seedance']){clips[name]=fs.readdirSync(path.join(work,name)).filter(f=>f.endsWith('.jpg')).sort();}}
async function background(s,t){
  ctx.drawImage(bg,0,0);
  if(s.id==='hook'||s.id==='rest'){
    const name=s.id==='hook'?'minimax':'seedance';
    const ix=Math.min(clips[name].length-1,Math.max(0,Math.floor((t-s.start)*FPS)));
    const im=await loadImage(path.join(work,name,clips[name][ix]));ctx.drawImage(im,0,0,W,H);
    const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'rgba(5,14,27,.85)');g.addColorStop(.28,'rgba(5,14,27,.36)');g.addColorStop(.48,'rgba(5,14,27,.12)');g.addColorStop(.65,'rgba(5,14,27,.88)');g.addColorStop(1,'#081322');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  }
  // Decorative field, deliberately outside the critical text region.
  ctx.save();ctx.globalAlpha=.22;ctx.strokeStyle='#668197';ctx.lineWidth=1;
  for(let r of [400,470,540]){ctx.beginPath();ctx.arc(980,1520,r,Math.PI,Math.PI*1.7);ctx.stroke();}ctx.restore();
}
function header(s,t){
  text('REP & REASON',78,286,27,cream,700);text('FIELD NOTE 001',895,289,21,muted,500,'right');
  line(78,333,900,333,'#526477',1);
  const titles={hook:['AN HOUR.','OF WHAT?'],audit:['FOUR BUCKETS.','ONE SESSION.'],friction:['FIND THE','FRICTION.'],rest:['REST IS PART','OF THE PLAN.'],action:['LOG. CHANGE.','COMPARE.'],close:['KNOW WHY.','TRAIN BETTER.']};
  const dy=12*(1-ease((t-s.start)/.25));
  titles[s.id].forEach((v,i)=>{if(s.id==='hook'&&i===1&&t<tl.cues[1].spoken_start)return;text(v,73,370+i*96+dy,87,i?lime:cream,700);});
  const idx=tl.scenes.indexOf(s);
  for(let j=0;j<6;j++){rect(80+j*138,565,118,4,2,'#334B60');if(j<=idx)rect(80+j*138,565,118*(j===idx?clamp((t-s.start)/(s.end-s.start)):1),4,2,lime);}
}
function audit(s,t){
  const morph=ease((t-(s.start+1.5))/1.0);
  text('60 MINUTES  /  60 TILES',80,609,24,muted,500);
  const starts=[tl.markers.lifting,tl.markers.rest,tl.markers.setup,tl.markers.waiting];
  let offset=0;
  for(let group=0;group<4;group++){
    for(let j=0;j<values[group];j++){
      const k=offset+j,angle=-Math.PI/2+k*Math.PI*2/60;
      const x=mix(490+205*Math.cos(angle),102+(k%10)*46,morph);
      const y=mix(826+205*Math.sin(angle),711+Math.floor(k/10)*46,morph);
      const amount=ease((t-starts[group]-j/values[group]*.35)/.22);
      ctx.save();ctx.globalAlpha=.7;rect(x-16,y-16,32,32,6,'#344B60');ctx.restore();
      if(amount>0){ctx.save();ctx.globalAlpha=amount;rect(x-16,y-16,32,32,6,colors[group]);ctx.restore();}
    }
    offset+=values[group];
  }
  ctx.save();ctx.globalAlpha=morph;
  labels.forEach((label,i)=>{
    const active=t>=starts[i];
    circle(641,710+i*80,5,active?colors[i]:'#52677C');
    text(active?String(values[i]).padStart(2,'0'):'—',659,684+i*80,48,active?colors[i]:'#52677C',700);
    text(label,738,698+i*80,26,active?cream:muted,600);
  });
  text('1 TILE = 1 MINUTE',84,1003,22,muted,500);
  ctx.restore();
  if(morph<1){ctx.save();ctx.globalAlpha=1-morph;text('60',490,753,100,cream,700,'center');text('MINUTES',490,866,23,muted,600,'center');ctx.restore();}
  rect(80,1040,820,46,10,'#213649');text('ILLUSTRATIVE EXAMPLE · INVENTED MINUTES',490,1052,22,lime,600,'center');
}
function friction(s,t){
  const local=t-s.start;
  text('ONE DELAY YOU CAN CHANGE',80,610,25,muted,500);
  const start=tl.cues[8].spoken_start;
  for(let [x,label,color] of [[235,'YOUR STATION',lime],[755,'EQUIPMENT',blue]]){
    rect(x-143,686,286,205,24,'#172F46','#426078');dumbbell(x,765,.85,color);text(label,x,844,23,cream,600,'center');
  }
  const running=clamp((t-start)/1.2),x=235+520*(.5-.5*Math.cos(Math.max(0,t-start)*Math.PI*2));
  line(235,937,755,937,'#506981',3);
  for(let k=0;k<3;k++){const yy=921+k*16;line(355,yy,630,yy, t>=start?coral:'#3F566C',2);}
  if(running>0){circle(x,937,14,coral);circle(x,937,5,cream);}
  text(t>=start?'REPEATED EQUIPMENT TRIPS':'FOUR BUCKETS. FOUR DIFFERENT ISSUES.',490,1004,t>=start?28:24,t>=start?coral:muted,600,'center');
}
function rest(s,t){
  const p=ease((t-s.start)/.6);
  // A calm proportional strip makes the key inference explicit.
  ctx.save();ctx.globalAlpha=p;rect(80,970,820,112,18,'rgba(8,20,35,.92)','#476079');
  text('BIGGEST BLOCK ≠ BIGGEST PROBLEM',490,992,29,lime,700,'center');
  text('Keep the purpose of your rest in view.',490,1034,24,cream,500,'center');ctx.restore();
}
function action(s,t){
  const step=t<tl.cues[13].spoken_start?0:t<tl.cues[14].spoken_start?1:2;
  ['LOG','CHANGE','COMPARE'].forEach((label,i)=>{
    rect(80+i*280,620,260,63,14,step===i?lime:'#1E354C',step===i?null:'#3E5870');
    text(`${i+1}  ${label}`,210+i*280,640,25,step===i?'#10233E':muted,700,'center');
  });
  rect(80,717,820,345,24,'#142B42','#3D5871');
  if(step===0){
    text('YOUR NEXT SESSION',112,747,25,cream,600);
    labels.forEach((v,i)=>{const x=112+(i%2)*400,y=816+Math.floor(i/2)*104;circle(x+6,y+18,6,colors[i]);text(v,x+27,y,26,cream,600);text('___ min',x+233,y,25,muted,500);});
  }else if(step===1){
    text('ONE PRACTICAL CHANGE',490,747,26,lime,600,'center');
    const p=ease((t-tl.cues[13].spoken_start)/.65);
    rect(160,817,300,132,20,'#243E52');text('STATION',310,965,23,muted,500,'center');
    dumbbell(mix(750,310,p),883,.86,lime);
    text('Group the equipment you need.',490,1015,26,cream,500,'center');
  }else{
    text('SESSION 1',299,754,27,cream,600,'center');text('SESSION 2',701,754,27,cream,600,'center');
    for(let i=0;i<4;i++){rect(160,813+i*43,255,13,5,'#314B61');rect(565,813+i*43,255,13,5,'#314B61');circle(143,819+i*43,5,colors[i]);circle(548,819+i*43,5,colors[i]);}
    text('MEASURE → ADJUST → COMPARE',490,1015,27,lime,600,'center');
  }
}
function close(s,t){
  const p=ease((t-s.start)/.6);
  for(let i=0;i<60;i++){const a=i*Math.PI/30-Math.PI/2;circle(490+150*Math.cos(a),818+150*Math.sin(a),5,i<Math.round(60*p)?lime:'#324D65');}
  text('ONE',490,756,63,cream,700,'center');text('SESSION',490,826,37,cream,600,'center');
  text('TRY A ONE-SESSION TIME AUDIT',490,1016,29,lime,700,'center');
}
function captions(t){
  const c=tl.cues.find(v=>t>=v.start&&t<v.end);if(!c)return;
  const n=c.lines.length,h=n*53+30,y=1112;
  rect(70,y,850,h,16,'rgba(4,12,23,.96)');
  c.lines.forEach((s,i)=>text(s,495,y+15+i*53,43,cream,600,'center'));
}
async function frame(t,burn=true){
  const s=tl.scenes.find(s=>t>=s.start&&t<s.end)||tl.scenes.at(-1);
  await background(s,t);header(s,t);
  ({audit,friction,rest,action,close}[s.id]||(()=>{}))(s,t);
  if(burn)captions(t);
}
async function main(){
  await setup();
  const rangeAt=process.argv.indexOf('--range');
  const first=rangeAt<0?0:Number(process.argv[rangeAt+1]);
  const last=rangeAt<0?Math.round(tl.duration*FPS):Math.min(Math.round(tl.duration*FPS),first+Number(process.argv[rangeAt+2]));
  const stills=[.8,2.2,4.7,8.5,10.8,12.3,17.7,23.5,26.3,28.6,31.4,35.7];
  if(rangeAt<0)for(let i=0;i<stills.length;i++){await frame(stills[i]);fs.writeFileSync(path.join(out,`preview-${String(i).padStart(2,'0')}.jpg`),await canvas.encode('jpeg',85));}
  if(process.argv.includes('--stills'))return;
  const target=path.join(out,rangeAt<0?'Rep_and_Reason_Time_Audit_V3.mp4':`segment-${String(first).padStart(5,'0')}.mp4`);
  const args=['-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgba','-s',`${W}x${H}`,'-r',String(FPS),'-i','pipe:0'];
  if(rangeAt<0)args.push('-i',path.join(work,'mix.wav'),'-map','0:v:0','-map','1:a:0');
  args.push('-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p');
  if(rangeAt<0)args.push('-c:a','aac','-b:a','192k');
  args.push('-t',String((last-first)/FPS),'-movflags','+faststart',target);
  const ff=spawn('ffmpeg',args,{stdio:['pipe','inherit','inherit']});
  const complete=once(ff,'close');
  for(let f=first;f<last;f++){
    await frame(f/FPS);const bytes=ctx.getImageData(0,0,W,H).data;
    if(!ff.stdin.write(Buffer.from(bytes.buffer,bytes.byteOffset,bytes.byteLength)))await once(ff.stdin,'drain');
    if(f%150===0)process.stderr.write(`Rendered ${f}/${Math.round(tl.duration*FPS)} frames\n`);
    if(f%15===0&&global.gc)global.gc();
  }
  ff.stdin.end();const [code]=await complete;if(code)throw new Error(`ffmpeg exited ${code}`);
  console.log(target);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
