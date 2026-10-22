const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),{execFileSync}=require('node:child_process');
const {createRenderer}=require('../tools/video/render_month_one_v4.cjs'),{renderPost}=require('../tools/video/render_supporting_v4.cjs');
const root=path.resolve(__dirname,'..');
const timelines=JSON.parse(execFileSync(process.env.PYTHON||'python3',['-c',"import sys,json;sys.path.insert(0,'tools/video');from produce_month_one_v4 import episodes;from month_one_core import make_timeline;print(json.dumps([make_timeline(e) for e in episodes()]))"],{cwd:root,encoding:'utf8'}));
test('V4 every scene keeps text within the production safe region',async()=>{
 for(const tl of timelines){const r=await createRenderer(tl,{width:216});
  for(let t=0;t<tl.duration;t+=.5){r.frame(t);for(const b of r.checks){assert.ok(b.x>=75&&b.right<=925&&b.y>=240&&b.bottom<=1500,`${tl.episode.id} ${JSON.stringify(b)}`);if(b.y>=1300&&b.y<1460)assert.ok(b.size>=40);if(b.y>=350&&b.y<680)assert.ok(b.right<=610);}}
 }
});
test('Character edits affect only the fixed portrait region and are visible',async()=>{
 const tl=timelines[3],r=structuredClone(tl),g=structuredClone(tl);r.episode.graphics.character_asset='brand/v4/characters/guide-smaller.png';g.episode.graphics.character_asset=null;
 const renderers=await Promise.all([tl,r,g].map(x=>createRenderer(x,{width:216})));
 for(const time of [.12,2,10]){renderers.forEach(x=>x.frame(time));const buffers=renderers.map(x=>x.canvas.data());let mr=0,mg=0;
  for(let y=0;y<384;y++)for(let x=0;x<216;x++)for(let c=0;c<4;c++){const i=(y*216+x)*4+c;if(x<124||x>182||y<65||y>152){assert.equal(buffers[0][i],buffers[1][i]);assert.equal(buffers[0][i],buffers[2][i]);}else{mr+=buffers[0][i]!==buffers[1][i];mg+=buffers[0][i]!==buffers[2][i];}}
  assert.ok(mr>100&&mg>1000,'Portrait must load and differ');assert.deepEqual(renderers[0].checks,renderers[1].checks);
 }
});
test('Citation control removes only the specified source label',async()=>{
 const a=timelines[2],b=structuredClone(a);b.episode.graphics.source_cue_visible=false;
 const x=await createRenderer(a,{width:216}),y=await createRenderer(b,{width:216});x.frame(5);y.frame(5);
 assert.deepEqual(x.checks.filter(z=>z.text!==a.episode.graphics.source_cue.label),y.checks);
 const aa=x.canvas.data(),bb=y.canvas.data();let changed=0;for(let row=0;row<384;row++)for(let col=0;col<216;col++)for(let c=0;c<4;c++){let i=(row*216+col)*4+c;if(row<249||row>258)assert.equal(aa[i],bb[i]);else changed+=aa[i]!==bb[i];}assert.ok(changed>100);
});
test('V4 supporting copy and native-poll space survive the brand update',async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(root,'content/month-one-v3/calendar.json')));
 for(const p of data.supporting_posts)for(let i=0;i<(p.kind==='story'?2:5);i++){const r=await renderPost(p,i),copy=p.kind==='story'?p.frames[i].text:p.slides[i];assert.ok(r.bounds.map(x=>x.text).join(' ').includes(copy));for(const b of r.bounds){assert.ok(b.x>=70&&b.right<=930&&b.bottom<=(p.kind==='story'?1510:1280));if(p.kind==='story'&&i===0)assert.ok(b.bottom<=1010||b.y>=1215);}}
});
