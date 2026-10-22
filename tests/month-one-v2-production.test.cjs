const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const {createRenderer}=require('../tools/video/render_month_one_v2.cjs');
const {renderPost}=require('../tools/video/render_supporting_v2.cjs');
const fs=require('node:fs');
const root=path.resolve(__dirname,'..');
const timelines=JSON.parse(execFileSync(process.env.PYTHON||'python3',['-c',"import sys,json;sys.path.insert(0,'tools/video');from produce_month_one_v2 import episodes;from month_one_core import make_timeline;print(json.dumps([make_timeline(e) for e in episodes()]))"],{cwd:root,encoding:'utf8'}));
test('All N-series frames keep factual text and full captions inside the phone safe area',()=>{
 let sampled=0;
 for(const tl of timelines){
  const r=createRenderer(tl,{width:216});
  for(let t=0;t<tl.duration;t+=.5){
   r.frame(t);sampled++;
   for(const b of r.checks){
    assert.ok(b.x>=69&&b.right<=941,`${tl.episode.id} ${t}: horizontal ${JSON.stringify(b)}`);
    assert.ok(b.y>=240&&b.bottom<=1510,`${tl.episode.id} ${t}: vertical ${JSON.stringify(b)}`);
    if(b.y>=1183&&b.y<1400)assert.ok(b.size>=40,`${tl.episode.id}: caption too small`);
   }
  }
 }
 assert.ok(sampled>800);
});
test('Motion and static controls preserve content and timing, changing only animation',()=>{
 const tl=timelines[0],before=JSON.stringify(tl);
 const a=createRenderer(tl,{width:216,treatment:'static'}),b=createRenderer(tl,{width:216,treatment:'motion'});
 a.frame(.1);b.frame(.1);
 assert.notDeepEqual(a.canvas.toBuffer('image/png'),b.canvas.toBuffer('image/png'));
 assert.deepEqual(a.checks.map(v=>v.text),b.checks.map(v=>v.text));
 assert.equal(JSON.stringify(tl),before);
});
test('Every supporting frame preserves exact copy without overflow or poll-region collisions',()=>{
 const data=JSON.parse(fs.readFileSync(path.join(root,'content/month-one-v2/calendar.json')));
 for(const p of data.supporting_posts){
  const story=p.kind==='story';
  for(let i=0;i<(story?2:5);i++){
   const r=renderPost(p,i),copy=story?p.frames[i].text:p.slides[i];
   assert.ok(r.bounds.map(b=>b.text).join(' ').includes(copy));
   for(const b of r.bounds){
    assert.ok(b.x>=70&&b.right<=930,`${p.id}: horizontal overflow`);
    assert.ok(b.y>=(story?240:70)&&b.bottom<=(story?1510:1280),`${p.id}: vertical overflow`);
    if(story&&i===0)assert.ok(b.bottom<=1010||b.y>=1215,`${p.id}: native poll collision`);
   }
  }
 }
});
