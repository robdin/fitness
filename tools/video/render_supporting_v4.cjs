/* Original supporting images; native poll controls are added by the uploader. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas,GlobalFonts,loadImage}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..');
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
async function renderPost(post,index){
 const story=post.kind==='story',h=story?1920:1350,canvas=createCanvas(1080,h),g=canvas.getContext('2d'),bounds=[];
 const cream='#F5F3EA',navy='#14221C',lime='#CAEF51',muted='#D4DED0';
 const rect=(x,y,w,h,c,r=24)=>{g.fillStyle=c;g.beginPath();g.roundRect(x,y,w,h,r);g.fill();};
 function text(s,x,y,size,color,max=900){g.font=`600 ${size}px Space`;g.textBaseline='top';g.fillStyle=color;g.fillText(s,x,y);const width=g.measureText(s).width;bounds.push({text:s,x,y,size,right:x+width,bottom:y+size*1.2});if(width>max+.1)throw Error('Text too wide: '+s);}
 function wrap(s,size,width){g.font=`600 ${size}px Space`;let lines=[],line='';for(const w of s.split(' ')){const trial=(line?line+' ':'')+w;if(g.measureText(trial).width>width&&line){lines.push(line);line=w;}else line=trial;}if(line)lines.push(line);return lines;}
 g.fillStyle=cream;g.fillRect(0,0,1080,h);
 rect(0,0,1080,story?170:28,'#2149CA',0);rect(0,h-(story?350:35),1080,story?350:35,'#2149CA',0);
 const top=story?280:90;
 rect(70,top,860,story?1120:1130,navy,32);
 text('REP & REASON',112,top+42,28,cream,600);
 text(story?`${index+1}/2`:`${index+1}/5`,825,top+42,28,lime,70);
 const label=story?(index===0?'YOUR TURN':'KEEP THE CONTEXT'):(post.id==='BK03'?'CHECK THE CLAIM':'YOUR NEXT STEP');
 text(label,112,top+125,25,muted,760);
 if(!story){const portrait=await loadImage(path.join(ROOT,'brand/v4/characters/guide-muscular.png'));g.drawImage(portrait,710,top+85,150,225);}
 else text('TRAINING CLUB',112,top+176,22,lime,600);
 const copy=story?post.frames[index].text:post.slides[index];
 let size=story?76:72,lines=wrap(copy,size,762);while(lines.length>6&&size>54){size-=2;lines=wrap(copy,size,762);}
 const bodyY=top+(story?223:328);
 if(!story){rect(112,top+201,104,94,lime,16);text(String(index+1).padStart(2,'0'),130,top+216,56,navy,84);}
 lines.forEach((s,i)=>text(s,112,bodyY+i*size*1.2,size,cream,762));
 // The prompt deliberately leaves a clear blank region for a real native poll.
 if(story&&index===0)rect(112,1010,762,205,'#304739',22);
 if(!story){for(let i=0;i<5;i++)rect(112+i*154,top+951,131,8,i<=index?lime:'#385269',3);}
 text('KNOW WHY. TRAIN BETTER.',112,top+(story?1024:1035),27,lime,762);
 return {canvas,bounds};
}
async function main(){
 const data=JSON.parse(fs.readFileSync(path.join(ROOT,'content/month-one-v3/calendar.json')));
 const out=path.join(ROOT,'.local/month-one-v4/review/supporting'),report=[];
 for(const post of data.supporting_posts){const dir=path.join(out,post.id);fs.mkdirSync(dir,{recursive:true});const count=post.kind==='story'?2:5;
  for(let i=0;i<count;i++){const r=await renderPost(post,i),name=post.kind==='story'?(i?'followup.png':'prompt.png'):`${i+1}.png`;fs.writeFileSync(path.join(dir,name),r.canvas.toBuffer('image/png'));report.push({id:post.id,file:`${post.id}/${name}`,text:r.bounds});}
 }
 fs.writeFileSync(path.join(out,'layout.json'),JSON.stringify(report,null,2)+'\n');
 const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({content_sha256:hash(path.join(ROOT,'content/month-one-v3/calendar.json')),renderer_sha256:hash(__filename),character_sha256:hash(path.join(ROOT,'brand/v4/characters/guide-muscular.png')),outputs:report.map(r=>({file:r.file,sha256:hash(path.join(out,r.file))}))},null,2)+'\n');
 console.log('Rendered 20 carousel panels and 16 story frames.');
}
module.exports={renderPost};if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
