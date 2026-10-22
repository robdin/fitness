const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createRenderer}=require('./render_month_one_v2.cjs');
const root=path.resolve(__dirname,'../../.local/month-one-v2/review');let frames=0,textBoxes=0;
for(let i=1;i<=16;i++){
 const id=`N${String(i).padStart(2,'0')}`,tl=JSON.parse(fs.readFileSync(path.join(root,id,'timeline.json'))),r=createRenderer(tl,{width:216});
 assert.equal(tl.timing,'provider_word_alignment');
 for(let f=0;f<Math.round(tl.duration*30);f++){
  r.frame(f/30);frames++;
  for(const b of r.checks){
   assert.ok(b.x>=69&&b.right<=941&&b.y>=240&&b.bottom<=1510,`${id} frame ${f}: ${JSON.stringify(b)}`);
   if(b.y>=1183&&b.y<1400)assert.ok(b.size>=40,`${id}: caption too small`);
   textBoxes++;
  }
 }
}
const report={status:'passed',episodes:16,frames,textBoxes,scope:'All final motion frames; text bounds in 1080-coordinate space. Visual judgment and uploader overlays still require review.'};
fs.writeFileSync(path.join(root,'frame-check.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
