import puppeteer from 'puppeteer-core'; import c from '@sparticuz/chromium'; import fs from 'fs';
const axe=fs.readFileSync('node_modules/axe-core/axe.min.js','utf8');
const b=await puppeteer.launch({executablePath:'/tmp/chromium',args:c.args,headless:true});let tot=0;
for(const u of ['/','/tspsc-group-2-notification-2026-783-posts/','/category/jobs/','/daily-quiz/','/latest-jobs/','/today/','/compare/','/post-your-news/','/?s=tspsc']){for(const mob of [1,0]){const p=await b.newPage();if(mob)await p.setViewport({width:390,height:800,isMobile:true,deviceScaleFactor:2});else await p.setViewport({width:1366,height:800});
await p.evaluateOnNewDocument(()=>{try{localStorage.setItem('su_theme','dark')}catch(e){}});
await p.goto('http://localhost:8099'+u,{waitUntil:'networkidle0'});await p.evaluate(axe);
const r=await p.evaluate(async()=>{const r=await axe.run(document,{resultTypes:['violations']});const out=[];r.violations.forEach(v=>v.nodes.forEach(n=>{const el=document.querySelector(n.target[0]);out.push(v.id+' | '+n.target[0].slice(0,60)+' | '+(n.any[0]&&n.any[0].message||'').replace(/Element has insufficient color contrast of /,'').slice(0,80)+' | '+(el?el.innerText.trim().slice(0,20):''))}));return out});
tot+=r.length;if(r.length)console.log((mob?'M ':'D ')+u+'\n  '+r.join('\n  '));await p.close();}}
console.log('dark axe total',tot);await b.close();process.exit(0);
