import puppeteer from 'puppeteer-core'; import c from '@sparticuz/chromium'; import fs from 'fs';
const url=process.argv.slice(2).find(a=>!a.startsWith('--'))||'/'; const mob=process.argv.includes('--mobile'); const name=(mob?'dm':'dd')+url.replace(/[^a-z0-9]+/gi,'_');
const b=await puppeteer.launch({executablePath:'/tmp/chromium',args:c.args,headless:true});const p=await b.newPage();
if(mob) await p.setViewport({width:390,height:800,isMobile:true,deviceScaleFactor:2}); else await p.setViewport({width:1366,height:800});
await p.evaluateOnNewDocument(()=>{try{localStorage.setItem('su_theme','dark')}catch(e){}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8099'+url,{waitUntil:'networkidle0'});await p.addStyleTag({content:'*{content-visibility:visible!important;animation:none!important;transition:none!important}'});
await new Promise(r=>setTimeout(r,1500));
const H=await p.evaluate(()=>document.documentElement.scrollHeight);const vh=800;let i=0;fs.mkdirSync('/tmp/shots',{recursive:true});
for(let y=0;y<H&&i<8;y+=vh,i++){await p.evaluate(y=>scrollTo(0,y),y);await new Promise(r=>setTimeout(r,400));await p.screenshot({path:`/tmp/shots/${name}.part${i}.png`});}
const dark=await p.evaluate(()=>document.body.classList.contains('dark'));
console.log(name,'dark',dark,'parts',i,'errors',errs.length);await b.close();process.exit(0);
