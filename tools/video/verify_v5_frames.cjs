const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {createRenderer}=require('./render_month_one_v5.cjs');
const ROOT=path.resolve(__dirname,'../..'),base=path.join(ROOT,'.local/month-one-v5-blueprint/review');
async function main(){
 let frames=0,textBoxes=0;const candidates=[];
 for(let i=1;i<=16;i++)candidates.push([`BP${String(i).padStart(2,'0')}`,'graphics',base,'motion']);
 candidates.push(['BP03','citation-off',path.join(ROOT,'.local/month-one-v5-blueprint-no-citation/review'),'motion']);
 candidates.push(['BP04','static',base,'static']);
 for(const [id,arm,root,treatment] of candidates){
  const tl=JSON.parse(fs.readFileSync(path.join(root,id,'timeline.json'))),r=await createRenderer(tl,{width:216,treatment});assert.equal(tl.timing,'provider_word_alignment');
  for(let f=0;f<Math.round(tl.duration*30);f++){
   r.frame(f/30);frames++;
   for(const b of r.checks){assert.ok(b.x>=75&&b.right<=925&&b.y>=240&&b.bottom<=1500,`${id}/${arm} f${f}: ${JSON.stringify(b)}`);if(b.y>=1300&&b.y<1460)assert.ok(b.size>=43);textBoxes++;}
  }
 }
 const report={status:'passed',exports:candidates.length,frames,textBoxes,scope:'All frames; text bounds and caption size. Citation pixel isolation also covered by unit tests. Uploader overlay and viewer comprehension checks remain pending.'};
 fs.writeFileSync(path.join(base,'frame-check.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});
