/* Original supporting images; native poll controls are added by the uploader. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..');
require('node:child_process').execFileSync('python3',[path.join(ROOT,'tools/brand/check_copy.py'),'--scope','month']);
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
GlobalFonts.registerFromPath(path.join(ROOT,'brand/blueprint/fonts/Fraunces-Italic.ttf'),'Dream');
const TOKENS=path.join(ROOT,'brand/blueprint/tokens.json'),C=JSON.parse(fs.readFileSync(TOKENS));
async function renderPost(post,index){
 const story=post.kind==='story',h=story?1920:1350,canvas=createCanvas(1080,h),g=canvas.getContext('2d'),bounds=[];
 const cream=C.panel,navy=C.bg,lime=C.accent,muted=C.cloud;
 const rect=(x,y,w,h,c,r=24)=>{g.fillStyle=c;g.beginPath();g.roundRect(x,y,w,h,r);g.fill();};
 function text(s,x,y,size,color,max=900,family='Space'){g.font=`600 ${size}px ${family}`;g.textBaseline='top';g.fillStyle=color;g.fillText(s,x,y);const width=g.measureText(s).width;bounds.push({text:s,x,y,size,right:x+width,bottom:y+size*1.2});if(width>max+.1)throw Error('Text too wide: '+s);}
 function wrap(s,size,width,family='Space'){g.font=`600 ${size}px ${family}`;let lines=[],line='';for(const w of s.split(' ')){const trial=(line?line+' ':'')+w;if(g.measureText(trial).width>width&&line){lines.push(line);line=w;}else line=trial;}if(line)lines.push(line);return lines;}
 g.fillStyle=cream;g.fillRect(0,0,1080,h);
 rect(0,0,1080,story?170:28,C.bg,0);rect(0,h-(story?350:35),1080,story?350:35,C.bg,0);
 const top=story?280:90;
 rect(70,top,860,story?1120:1130,navy,32);
 text('BODY OF OUR DREAMS',112,top+42,28,cream,680);
 text(story?`${index+1}/2`:`${index+1}/5`,825,top+42,28,lime,70);
 const label=story?(index===0?'YOUR TURN':'KEEP THE CONTEXT'):(post.id==='BCK03'?'CHECK THE CLAIM':'YOUR NEXT STEP');
 text(label,112,top+125,25,muted,760);
 if(story)text('YOUR DREAM BODY. YOUR REAL LIFE.',112,top+176,22,lime,600);
 const copy=story?post.frames[index].text:post.slides[index];
 const family=index===0?'Dream':'Space';let size=story?76:72,lines=wrap(copy,size,762,family);while(lines.length>6&&size>54){size-=2;lines=wrap(copy,size,762,family);}
 const bodyY=top+(story?223:328);
 if(!story){rect(112,top+201,104,94,lime,16);text(String(index+1).padStart(2,'0'),130,top+216,56,navy,84);}
 lines.forEach((s,i)=>text(s,112,bodyY+i*size*1.2,size,cream,762,family));
 // The prompt deliberately leaves a clear blank region for a real native poll.
 if(story&&index===0)rect(112,1010,762,205,'#1837A0',22);
 if(!story){for(let i=0;i<5;i++)rect(112+i*154,top+951,131,8,i<=index?lime:'#667FD5',3);}
 text('BIG DREAM. REAL-LIFE PLAN.',112,top+(story?1024:1035),27,lime,762);
 return {canvas,bounds};
}
async function main(){
 const data=JSON.parse(fs.readFileSync(path.join(ROOT,'content/month-one-v6/calendar.json')));
 const out=path.join(ROOT,'.local/month-one-v6-conversational/review/supporting'),report=[];
 for(const post of data.supporting_posts){const dir=path.join(out,post.id);fs.mkdirSync(dir,{recursive:true});const count=post.kind==='story'?2:5;
  for(let i=0;i<count;i++){const r=await renderPost(post,i),name=post.kind==='story'?(i?'followup.png':'prompt.png'):`${i+1}.png`;fs.writeFileSync(path.join(dir,name),r.canvas.toBuffer('image/png'));report.push({id:post.id,file:`${post.id}/${name}`,text:r.bounds});}
 }
 fs.writeFileSync(path.join(out,'layout.json'),JSON.stringify(report,null,2)+'\n');
 const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 const font_sha256=Object.fromEntries(['content/mvp/time-audit/fonts/SpaceGrotesk.ttf','brand/blueprint/fonts/Fraunces-Italic.ttf'].map(p=>[path.basename(p),hash(path.join(ROOT,p))]));
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({content_sha256:hash(path.join(ROOT,'content/month-one-v6/calendar.json')),renderer_sha256:hash(__filename),tokens_sha256:hash(TOKENS),font_sha256,character_assets:0,outputs:report.map(r=>({file:r.file,sha256:hash(path.join(out,r.file))}))},null,2)+'\n');
 console.log('Rendered 20 carousel panels and 16 story frames.');
}
module.exports={renderPost};if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
