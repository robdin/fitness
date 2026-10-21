const fs=require('node:fs'),path=require('node:path');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..'),data=JSON.parse(fs.readFileSync(path.join(ROOT,'content/month-one/supporting-posts.json')));
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
const out=path.join(ROOT,'.local/month-one/review/supporting');fs.mkdirSync(out,{recursive:true});
function make(title,body,{story=false,page='',options=[]}={}){
 const h=story?1920:1350,canvas=createCanvas(1080,h),g=canvas.getContext('2d');
 g.fillStyle='#10233E';g.fillRect(0,0,1080,h);g.fillStyle='#1C344B';g.beginPath();g.arc(1110,580,420,0,Math.PI*2);g.fill();
 const y0=story?310:100;
 function t(s,x,y,size,color='#F7F4EA'){g.font=`600 ${size}px Space`;g.fillStyle=color;g.textBaseline='top';g.fillText(s,x,y);}
 function lines(s,max,size){g.font=`600 ${size}px Space`;let a=[],line='';for(const w of s.split(' ')){if(g.measureText(line+' '+w).width>max&&line){a.push(line);line=w;}else line+=(line?' ':'')+w;}if(line)a.push(line);return a;}
 t('REP & REASON',80,y0,27);t(page,870,y0,27,'#B9F227');
 const headline=lines(title,900,82);headline.forEach((s,i)=>t(s,80,y0+115+i*94,82,i?'#B9F227':'#F7F4EA'));
 const by=y0+140+headline.length*94;
 lines(body,880,42).forEach((s,i)=>t(s,80,by+i*58,42,'#D4DFE7'));
 if(story){options.forEach((s,i)=>{const y=950+i*94;g.fillStyle=i?'#253F55':'#B9F227';g.beginPath();g.roundRect(80,y,900,74,15);g.fill();t(s,110,y+18,34,i?'#F7F4EA':'#10233E');});}
 g.fillStyle='#B9F227';g.fillRect(80,h-(story?570:170),900,4);t('Know why. Train better.',80,h-(story?530:125),29);
 return canvas;
}
for(const c of data.carousels){const dir=path.join(out,c.id);fs.mkdirSync(dir,{recursive:true});c.slides.forEach(([title,body],i)=>fs.writeFileSync(path.join(dir,`${i+1}.png`),make(title,body,{page:`${i+1}/5`}).toBuffer('image/png')));}
for(const s of data.stories){const dir=path.join(out,s.id);fs.mkdirSync(dir,{recursive:true});fs.writeFileSync(path.join(dir,'prompt.png'),make(s.question,'Tap your answer below.',{story:true,page:s.id}).toBuffer('image/png'));fs.writeFileSync(path.join(dir,'followup.png'),make(s.type==='quiz'?'THE ANSWER':'KEEP THE CONTEXT',s.followup,{story:true,page:s.id}).toBuffer('image/png'));}
console.log('Rendered 20 carousel slides and 16 story prompt/follow-up images.');
