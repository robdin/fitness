const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createRenderer}=require('./render_month_one_v3.cjs');
const ROOT=path.resolve(__dirname,'../..'),base=path.join(ROOT,'.local/month-one-v3/review');let frames=0,textBoxes=0;
const candidates=[];for(let i=1;i<=16;i++)candidates.push([`B${String(i).padStart(2,'0')}`,'club',base,'motion']);
for(const brand of ['lab','notebook'])candidates.push(['B01',brand,path.join(ROOT,`.local/month-one-v3-${brand}/review`),'motion']);
candidates.push(['B07','club',base,'static']);
for(const [id,brand,root,treatment] of candidates){
 const tl=JSON.parse(fs.readFileSync(path.join(root,id,'timeline.json'))),r=createRenderer(tl,{width:216,treatment});assert.equal(tl.timing,'provider_word_alignment');
 for(let f=0;f<Math.round(tl.duration*30);f++){
  r.frame(f/30);frames++;
  for(const b of r.checks){assert.ok(b.x>=75&&b.right<=925&&b.y>=240&&b.bottom<=1500,`${id}/${brand} f${f}: ${JSON.stringify(b)}`);if(b.y>=1242&&b.y<1430)assert.ok(b.size>=40,`${id}: captions too small`);textBoxes++;}
 }
}
const report={status:'passed',exports:19,frames,textBoxes,scope:'All frames in final B-series, two brand alternatives and the static control; text bounds and caption type size. Does not certify uploader overlays or human comprehension.'};fs.writeFileSync(path.join(base,'frame-check.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
