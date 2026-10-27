/* Preview composition only. The canonical Blueprint renderer is unchanged. */
const fs=require('node:fs'),path=require('node:path');
const {createCanvas,loadImage,GlobalFonts}=require('@napi-rs/canvas');
const ROOT=path.resolve(__dirname,'../..');
GlobalFonts.registerFromPath(path.join(ROOT,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
const scenes=[
 {id:'BP04',title:'A walk in your real week',crop:[0,3,627,884],pose:'commuting'},
 {id:'BP11',title:'Tomorrow’s lunch',crop:[629,3,567,884],pose:'cooking'},
 {id:'BP16',title:'Returning after a missed workout',crop:[1203,3,550,884],pose:'encouraging'}
];
async function main(){
 const out=path.join(ROOT,'.local/blueprint-character-d-preview');
 const atlas=await loadImage(path.join(out,'assets/off-duty-poses.png'));
 const reports=[];
 for(const s of scenes){
  const dir=path.join(out,s.id);fs.mkdirSync(dir,{recursive:true});
  const c=createCanvas(1080,1920),g=c.getContext('2d');
  // Portrait is decorative. Factual graphics, source cues and captions end above it.
  // Crop below the waist at the frame edge; retain the head and topic-specific hands.
  const h=500,w=h*s.crop[2]/s.crop[3],x=600-w/2,y=1510;
  g.drawImage(atlas,...s.crop,x,y,w,h);
  fs.writeFileSync(path.join(dir,'overlay.png'),c.toBuffer('image/png'));
  const head=createCanvas(2160,140),ctx=head.getContext('2d');ctx.fillStyle='#F3F5F4';ctx.fillRect(0,0,2160,140);
  ctx.font='600 42px Space';ctx.fillStyle='#173249';ctx.textBaseline='top';
  ctx.fillText('WITHOUT CHARACTER',65,24);ctx.fillText('WITH D · OFF-DUTY HERO',1145,24);
  ctx.font='400 30px Space';ctx.fillStyle='#2348C6';
  ctx.fillText(s.title,65,82);ctx.fillText('Same narration, timing, captions and diagrams',1145,82);
  fs.writeFileSync(path.join(dir,'comparison-header.png'),head.toBuffer('image/png'));
  reports.push({...s,draw:{x,y,width:w,height:h},visible_region:{left:x,top:y,right:x+w,bottom:1920}});
 }
 fs.writeFileSync(path.join(out,'composition.json'),JSON.stringify({status:'preview_only',selected_character:'D / Off-Duty Hero',placement:'lower decorative region; native social overlays may cover it',scenes:reports},null,2)+'\n');
 console.log('Prepared three transparent overlays and comparison headings.');
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
