const fs=require('node:fs'),path=require('node:path'),{createCanvas}=require('@napi-rs/canvas');
const {createRenderer}=require('./render_month_one_v3.cjs');
const ROOT=path.resolve(__dirname,'../..'),out=path.join(ROOT,'.local/month-one-v3/review/brand');fs.mkdirSync(out,{recursive:true});
const canvas=createCanvas(1560,1170),g=canvas.getContext('2d');g.fillStyle='#F5F3EA';g.fillRect(0,0,1560,1170);
g.fillStyle='#14221C';g.font='700 49px Space';g.fillText('REP & REASON / THREE DIRECTIONS',52,76);
g.font='500 23px Space';g.fillText('Same first-visit idea. Different visual character. Preference has not been tested.',52,119);
const copy=[['lab','A / TRAINING LAB','Precise · analytical · modular'],['club','B / TRAINING CLUB','Direct · energetic · welcoming'],['notebook','C / COACH’S NOTEBOOK','Calm · practical · personal']];
for(let i=0;i<3;i++){const [brand,title,desc]=copy[i],x=52+i*505;const dir=brand==='club'?'month-one-v3':'month-one-v3-'+brand;const tl=JSON.parse(fs.readFileSync(path.join(ROOT,'.local',dir,'review/B01/timeline.json')));const r=createRenderer(tl,{width:432});r.frame(tl.beats[1].start+1);g.drawImage(r.canvas,x,220,432,768);g.fillStyle='#14221C';g.font='700 24px Space';g.fillText(title,x,177);g.font='500 20px Space';g.fillText(desc,x,207);fs.writeFileSync(path.join(out,brand+'.png'),r.canvas.toBuffer('image/png'));}
g.fillStyle='#14221C';g.font='600 24px Space';g.fillText('Selected by project owner: B. Audience clarity and preference remain untested.',52,1050);
g.font='500 21px Space';g.fillText('Final narration timing. All three comparisons use identical audio.',52,1091);
fs.writeFileSync(path.join(out,'comparison.png'),canvas.toBuffer('image/png'));
console.log(path.join(out,'comparison.png'));
