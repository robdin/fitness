const test=require('node:test'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),{execFileSync}=require('node:child_process');
const {createRenderer}=require('../tools/video/render_month_one_v6.cjs'),{renderPost}=require('../tools/video/render_supporting_v6.cjs');
const root=path.resolve(__dirname,'..');
test('Blueprint essential text pairs exceed 4.5:1 contrast',()=>{
 const c=JSON.parse(fs.readFileSync(path.join(root,'brand/blueprint/tokens.json')));
 const lum=hex=>{const rgb=hex.slice(1).match(/../g).map(x=>parseInt(x,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;};
 for(const [a,b] of [['ink','bg'],['panelInk','panel'],['accentInk','accent'],['muted','bg'],['secondary','bg'],['panel','bg'],['bg','accent']]){const x=lum(c[a]),y=lum(c[b]);assert.ok((Math.max(x,y)+.05)/(Math.min(x,y)+.05)>=4.5,`${a}/${b}`);}
});
const timelines=JSON.parse(execFileSync(process.env.PYTHON||'python3',['-c',"import sys,json;sys.path.insert(0,'tools/video');from produce_month_one_v6 import episodes;from month_one_core import make_timeline;print(json.dumps([make_timeline(e) for e in episodes()]))"],{cwd:root,encoding:'utf8'}));
test('Blueprint scenes keep all text and captions in the production safe region',async()=>{
 for(const tl of timelines){const r=await createRenderer(tl,{width:216});for(let t=0;t<tl.duration;t+=.4){r.frame(t);for(const b of r.checks){assert.ok(b.x>=75&&b.right<=925&&b.y>=240&&b.bottom<=1500,`${tl.episode.id}: ${JSON.stringify(b)}`);if(b.y>=1300&&b.y<1460)assert.ok(b.size>=43);}}}
});
test('Blueprint citation pair differs only inside the source-label strip',async()=>{
 const a=timelines.find(t=>t.episode.id==='BC03'),b=structuredClone(a);b.episode.graphics.source_cue_visible=false;
 const x=await createRenderer(a,{width:216}),y=await createRenderer(b,{width:216});x.frame(5);y.frame(5);
 assert.deepEqual(x.checks.filter(z=>z.text!==a.episode.graphics.source_cue.label),y.checks);
 const aa=x.canvas.data(),bb=y.canvas.data();let changed=0;
 for(let row=0;row<384;row++)for(let col=0;col<216;col++)for(let c=0;c<4;c++){const i=(row*216+col)*4+c;if(row<249||row>258)assert.equal(aa[i],bb[i]);else changed+=aa[i]!==bb[i];}assert.ok(changed>100);
});
test('Walking motion control changes the explanatory route only',async()=>{
 const tl=timelines.find(t=>t.episode.id==='BC04'),a=await createRenderer(tl,{width:216,treatment:'motion'}),b=await createRenderer(tl,{width:216,treatment:'static'});
 const t=tl.beats[1].start+.18;a.frame(t);b.frame(t);assert.deepEqual(a.checks,b.checks);
 const x=a.canvas.data(),y=b.canvas.data();let changed=0;
 for(let row=0;row<384;row++)for(let col=0;col<216;col++)for(let c=0;c<4;c++){let i=(row*216+col)*4+c;if(row<172||row>184)assert.equal(x[i],y[i]);else changed+=x[i]!==y[i];}assert.ok(changed>50);
});
test('All 36 supporting frames preserve exact copy and native poll space',async()=>{
 const data=JSON.parse(fs.readFileSync(path.join(root,'content/month-one-v6/calendar.json')));
 for(const p of data.supporting_posts)for(let i=0;i<(p.kind==='story'?2:5);i++){const r=await renderPost(p,i),copy=p.kind==='story'?p.frames[i].text:p.slides[i];assert.ok(r.bounds.map(x=>x.text).join(' ').includes(copy));for(const b of r.bounds){assert.ok(b.x>=70&&b.right<=930&&b.bottom<=(p.kind==='story'?1510:1280),JSON.stringify(b));if(p.kind==='story'&&i===0)assert.ok(b.bottom<=1010||b.y>=1215);}}
});
