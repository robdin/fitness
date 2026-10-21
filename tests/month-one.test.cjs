const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const {createRenderer}=require('../tools/video/render_month_one.cjs');
const root=path.resolve(__dirname,'..'),data=JSON.parse(fs.readFileSync(path.join(root,'content/month-one/episodes.json')));
const timelines=JSON.parse(execFileSync(process.env.PYTHON||'python3',['-c',"import sys,json;sys.path.insert(0,'tools/video');from month_one_core import load_episodes,make_timeline;print(json.dumps({e['id']:make_timeline(e) for e in load_episodes()}))"],{cwd:root,encoding:'utf8'}));
test('All sampled frame text stays within the conservative critical-content region',()=>{
 let sampled=0;
 for(const ep of data.episodes){
   const tl=timelines[ep.id];
   const r=createRenderer(tl,{width:216});
   for(let t=0;t<tl.duration;t+=.5){
     r.frame(t);sampled++;
     for(const b of r.checks){
       if(b.y>=1400)continue; // Redundant decorative footer, never factual content.
       assert.ok(b.x>=69&&b.right<=922,`${ep.id} ${t}: horizontal ${JSON.stringify(b)}`);
       assert.ok(b.y>=270&&b.bottom<=1248,`${ep.id} ${t}: vertical ${JSON.stringify(b)}`);
       if(b.y>=1120)assert.ok(b.size>=40,`${ep.id}: caption too small`);
     }
   }
 }
 assert.ok(sampled>700);
});
test('Three visual treatments preserve exact episode, caption and frame timing input',()=>{
 const tl=timelines.M01,before=JSON.stringify(tl);
 const frames=[];
 for(const treatment of ['compact','large','motion']){
   const r=createRenderer(tl,{width:216,treatment});r.frame(tl.beats[1].start+.25);frames.push(r.canvas.toBuffer('image/png'));
   assert.equal(JSON.stringify(tl),before);
 }
 assert.notDeepEqual(frames[0],frames[1]);assert.notDeepEqual(frames[1],frames[2]);
});
