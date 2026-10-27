/* Deterministic typography/vector assets extending the existing Blueprint system. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {createCanvas,GlobalFonts}=require('@napi-rs/canvas');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'brand/blueprint/profiles');
require('node:child_process').execFileSync('python3',[path.join(root,'tools/brand/check_copy.py'),'--scope','profiles']);
const t=JSON.parse(fs.readFileSync(path.join(root,'brand/blueprint/tokens.json'))),copy=JSON.parse(fs.readFileSync(path.join(out,'profile-copy.json')));
GlobalFonts.registerFromPath(path.join(root,'brand/blueprint/fonts/Fraunces-Italic.ttf'),'Dream');
GlobalFonts.registerFromPath(path.join(root,'content/mvp/time-audit/fonts/SpaceGrotesk.ttf'),'Space');
fs.mkdirSync(out,{recursive:true});
function star(g,x,y,r){g.beginPath();g.moveTo(x,y-r);g.bezierCurveTo(x+r*.22,y-r*.22,x+r*.22,y-r*.22,x+r,y);g.bezierCurveTo(x+r*.22,y+r*.22,x+r*.22,y+r*.22,x,y+r);g.bezierCurveTo(x-r*.22,y+r*.22,x-r*.22,y+r*.22,x-r,y);g.bezierCurveTo(x-r*.22,y-r*.22,x-r*.22,y-r*.22,x,y-r);g.closePath();g.fill();}
function mark(g,x,y,size,circle=false){g.save();g.translate(x,y);g.scale(size/1024,size/1024);if(circle){g.beginPath();g.arc(512,512,512,0,Math.PI*2);g.clip();}g.fillStyle=t.bg;g.fillRect(0,0,1024,1024);g.fillStyle=t.ink;g.font='700 690px Dream';g.textAlign='center';g.textBaseline='alphabetic';g.fillText('B',472,765);g.fillStyle=t.accent;star(g,769,292,81);g.restore();}
const avatar=createCanvas(1024,1024);mark(avatar.getContext('2d'),0,0,1024);fs.writeFileSync(path.join(out,'profile-picture-1024.png'),avatar.toBuffer('image/png'));
const yt=createCanvas(800,800);yt.getContext('2d').drawImage(avatar,0,0,800,800);fs.writeFileSync(path.join(out,'youtube-profile-800.png'),yt.toBuffer('image/png'));
const wm=createCanvas(150,150);mark(wm.getContext('2d'),0,0,150,true);fs.writeFileSync(path.join(out,'youtube-watermark-150.png'),wm.toBuffer('image/png'));
const banner=createCanvas(2560,1440),g=banner.getContext('2d');g.fillStyle=t.bg;g.fillRect(0,0,2560,1440);
g.strokeStyle='#ffffff12';g.lineWidth=1;for(let x=0;x<2560;x+=80){g.beginPath();g.moveTo(x,0);g.lineTo(x,1440);g.stroke();}for(let y=0;y<1440;y+=80){g.beginPath();g.moveTo(0,y);g.lineTo(2560,y);g.stroke();}
const glow=g.createRadialGradient(1450,1460,50,1450,1460,900);glow.addColorStop(0,'#DDD6F599');glow.addColorStop(1,'#DDD6F500');g.fillStyle=glow;g.fillRect(0,0,2560,1440);
// All meaningful content stays inside the centered 1544 × 423 device-safe region.
mark(g,558,592,245,true);
const boxes=[];
function line(text,x,y,font,color){g.font=font;g.fillStyle=color;g.textBaseline='top';g.fillText(text,x,y);const m=g.measureText(text);boxes.push({text,left:x,top:y,right:x+m.width,bottom:y+parseFloat(font.match(/([\d.]+)px/)[1])*1.2});}
line('BODY OF OUR DREAMS',850,552,'600 34px Space',t.cloud);
line('Your dream body.',844,608,'600 98px Dream',t.ink);
line('Your real life.',850,718,'600 92px Space',t.ink);
line('Science-backed fitness that fits.',854,838,'500 36px Space',t.cloud);
for(const b of boxes)if(b.left<508||b.right>2052||b.top<508.5||b.bottom>931.5)throw Error('Banner text leaves safe area: '+b.text);
fs.writeFileSync(path.join(out,'youtube-banner-2560x1440.png'),banner.toBuffer('image/png'));
const proof=createCanvas(1500,1080),p=proof.getContext('2d');p.fillStyle=t.panel;p.fillRect(0,0,1500,1080);
p.fillStyle=t.panelInk;p.font='600 34px Space';p.fillText('BODY OF OUR DREAMS / PROFILE KIT',70,65);
mark(p,70,110,300,true);p.font='500 25px Space';p.fillText('Circular crop',98,455);
for(const [i,size] of [32,48,96].entries()){mark(p,440+i*170,175,size,true);p.font='500 23px Space';p.fillStyle=t.panelInk;p.fillText(size+' px',440+i*170,320);}
p.fillStyle=t.panelInk;p.font='600 28px Space';p.fillText('Small-size checks',440,130);
p.drawImage(banner,508,508,1544,424,70,520,1360,374);p.font='500 25px Space';p.fillText('YouTube mobile-safe crop',70,945);
fs.writeFileSync(path.join(out,'profile-kit-preview.png'),proof.toBuffer('image/png'));
if(copy.instagram.bio.length>150||copy.tiktok.bio.length>80||copy.youtube.description.length>1000||copy.instagram.name.length>30)throw Error('Copy exceeds conservative platform limits');
const files=['profile-picture-1024.png','youtube-profile-800.png','youtube-watermark-150.png','youtube-banner-2560x1440.png','profile-kit-preview.png'];
const record={version:'blueprint-profiles-v1',brand_tokens_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'brand/blueprint/tokens.json'))).digest('hex'),files:files.map(name=>({file:name,bytes:fs.statSync(path.join(out,name)).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,name))).digest('hex')})),banner_text_bounds:boxes,copy_characters:{instagram:copy.instagram.bio.length,tiktok:copy.tiktok.bio.length,youtube:copy.youtube.description.length},native_upload_verified:false};
if(record.files.find(x=>x.file==='youtube-banner-2560x1440.png').bytes>6e6)throw Error('Banner too large');
fs.writeFileSync(path.join(out,'asset-verification.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({files:files.length,copy_characters:record.copy_characters,banner_safe_area:'passed'}));
