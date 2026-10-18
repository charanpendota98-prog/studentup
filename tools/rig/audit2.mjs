import puppeteer from 'puppeteer-core'; import chromium from '@sparticuz/chromium';
const B='http://localhost:8099';
const urls=(process.argv.slice(2).length?process.argv.slice(2):['/','/tspsc-group-2-notification-2026-783-posts/','/category/jobs/','/latest-jobs/','/daily-quiz/','/today/','/?s=zzzqqq','/does-not-exist-xyz/','/jobs/degree/','/category/jobs/page/2/']);
const b=await puppeteer.launch({executablePath:'/tmp/chromium',args:chromium.args,headless:true});
function lum(c){const m=c.match(/\d+(\.\d+)?/g);if(!m)return null;const [r,g,bb]=m.map(Number);const a=m[3]!==undefined?Number(m[3]):1;if(a===0)return null;const f=v=>{v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)};return .2126*f(r)+.7152*f(g)+.0722*f(bb)}
for(const mobile of [true,false]){
 for(const u of urls){
  const p=await b.newPage(); await p.setViewport(mobile?{width:390,height:800,isMobile:true,deviceScaleFactor:2}:{width:1366,height:800});
  await Promise.all([p.coverage.startCSSCoverage(),p.coverage.startJSCoverage()]);
  const reqs=[];p.on('response',r=>{reqs.push({u:r.url(),s:r.status(),t:(r.headers()['content-type']||'').split(';')[0]})});
  await p.evaluateOnNewDocument(()=>{window.__cls=0;window.__lcp=null;new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});new PerformanceObserver(l=>{const e=l.getEntries().pop();if(e)window.__lcp={t:Math.round(e.startTime),el:e.element?e.element.tagName+'.'+(e.element.className||'').toString().slice(0,30):''}}).observe({type:'largest-contentful-paint',buffered:true});});
  let status=0;try{const r=await p.goto(B+u,{waitUntil:'networkidle0',timeout:60000});status=r.status();}catch(e){console.log(u,'NAV FAIL',e.message);await p.close();continue}
  await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight));await new Promise(r=>setTimeout(r,800));await p.evaluate(()=>window.scrollTo(0,0));await new Promise(r=>setTimeout(r,400));
  const [css,js]=await Promise.all([p.coverage.stopCSSCoverage(),p.coverage.stopJSCoverage()]);
  const sum=(arr)=>{let t=0,used=0;for(const e of arr){t+=e.text.length;for(const r of e.ranges)used+=r.end-r.start}return {total:t,used}};
  const cs=sum(css),jss=sum(js);
  const r=await p.evaluate((lumSrc)=>{
    const lum=new Function('return '+lumSrc)();
    const out={};
    out.cls=+window.__cls.toFixed(3);out.lcp=window.__lcp;
    out.dom=document.querySelectorAll('*').length;
    out.landmarks={header:!!document.querySelector('header,[role=banner]'),main:document.querySelectorAll('main,[role=main]').length,nav:document.querySelectorAll('nav').length,footer:!!document.querySelector('footer,[role=contentinfo]')};
    const sk=document.querySelector('a.skip-link,a[href^="#"][class*=skip]');out.skip=sk?!!document.querySelector(sk.getAttribute('href')):'none';
    out.imgsNoDim=[...document.images].filter(i=>!i.getAttribute('width')||!i.getAttribute('height')).length;
    out.imgsNoAlt=[...document.images].filter(i=>!i.hasAttribute('alt')).length;
    out.imgsEagerBelowFold=[...document.images].filter(i=>i.loading!=='lazy'&&i.getBoundingClientRect().top>900).length;
    out.iframes=document.querySelectorAll('iframe').length;
    out.inlineScriptKB=Math.round([...document.querySelectorAll('script:not([src])')].reduce((a,s)=>a+s.textContent.length,0)/1024);
    out.inlineStyleKB=Math.round([...document.querySelectorAll('style')].reduce((a,s)=>a+s.textContent.length,0)/1024);
    out.blockingCSS=[...document.querySelectorAll('link[rel=stylesheet]')].filter(l=>!l.media||l.media==='all').length;
    out.syncScripts=[...document.querySelectorAll('script[src]')].filter(s=>!s.defer&&!s.async&&!s.type?.includes('module')).length;
    out.positiveTabindex=document.querySelectorAll('[tabindex]:not([tabindex="0"]):not([tabindex="-1"])').length;
    out.buttonInA=document.querySelectorAll('a button, button a').length;
    out.blockInP=[...document.querySelectorAll('p')].filter(p=>p.querySelector('div,ul,ol,table,h1,h2,h3,section')).length;
    out.emptyLinks=[...document.querySelectorAll('a')].filter(a=>!a.getAttribute('href')||a.getAttribute('href')==='#').length;
    out.dupLinksSameText=(()=>{const m={};for(const a of document.querySelectorAll('main a,article a')){const t=a.textContent.trim();if(!t)continue;(m[t]=m[t]||new Set()).add(a.href)}return Object.entries(m).filter(([t,s])=>s.size>1).map(([t])=>t.slice(0,20)).slice(0,5)})();
    // focus visibility: elements whose :focus-visible outline is none and no box-shadow
    let noFocus=0;const sample=[...document.querySelectorAll('a[href],button,input,select,textarea')].slice(0,80);
    for(const el of sample){el.focus({preventScroll:true});const cs=getComputedStyle(el);if((cs.outlineStyle==='none'||cs.outlineWidth==='0px')&&cs.boxShadow==='none')noFocus++;}
    if(document.activeElement)document.activeElement.blur();
    out.noFocusStyle=noFocus+'/'+sample.length;
    // contrast
    const low=[];const seen=new Set();
    const bgOf=(el)=>{let e=el;while(e){const c=getComputedStyle(e).backgroundColor;const L=lum(c);if(L!==null)return c;e=e.parentElement}return 'rgb(255,255,255)'};
    const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n,count=0;
    while((n=w.nextNode())&&count<4000){const t=n.textContent.trim();if(t.length<3)continue;const el=n.parentElement;if(!el)continue;const cs=getComputedStyle(el);if(cs.visibility==='hidden'||cs.display==='none'||parseFloat(cs.opacity)===0)continue;const rc=el.getBoundingClientRect();if(!rc.width||!rc.height)continue;count++;const fg=lum(cs.color),bg=lum(bgOf(el));if(fg===null||bg===null)continue;const ratio=(Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05);const fs=parseFloat(cs.fontSize),bold=parseInt(cs.fontWeight)>=700;const large=fs>=24||(fs>=18.66&&bold);const need=large?3:4.5;if(ratio<need){const k=el.tagName+'.'+(el.className||'').toString().split(' ')[0];if(!seen.has(k)){seen.add(k);low.push(k+' '+ratio.toFixed(1)+' "'+t.slice(0,14)+'"')}}}
    out.lowContrast=low.slice(0,12);out.lowContrastN=low.length;
    // schema required fields
    const sch=[];for(const s of document.querySelectorAll('script[type="application/ld+json"]')){try{const j=JSON.parse(s.textContent);const g=j['@graph']||[j];for(const o of g){const t=o['@type'];const miss=[];const req={NewsArticle:['headline','datePublished','dateModified','author','image','publisher','mainEntityOfPage'],Article:['headline','datePublished','author','image'],JobPosting:['title','description','datePosted','hiringOrganization','jobLocation','validThrough'],FAQPage:['mainEntity'],BreadcrumbList:['itemListElement'],ItemList:['itemListElement'],WebSite:['url','name'],Organization:['name','url','logo'],Person:['name']}[Array.isArray(t)?t[0]:t];if(req)for(const k of req)if(!(k in o))miss.push(k);if(t==='NewsArticle'&&o.headline&&o.headline.length>110)miss.push('headline>110');if(t==='JobPosting'&&o.validThrough&&new Date(o.validThrough)<new Date())miss.push('validThrough-past');if(miss.length)sch.push(t+':'+miss.join(','))}}catch(e){sch.push('PARSE')}}
    out.schemaMissing=sch;
    out.canonical=document.querySelector('link[rel=canonical]')?.href?.replace(location.origin,'');
    out.robots=document.querySelector('meta[name=robots]')?.content;
    out.prevNext=[!!document.querySelector('link[rel=prev]'),!!document.querySelector('link[rel=next]')];
    out.manifest=!!document.querySelector('link[rel=manifest]');out.themeColor=!!document.querySelector('meta[name=theme-color]');out.appleIcon=!!document.querySelector('link[rel=apple-touch-icon]');
    out.ogImage=document.querySelector('meta[property="og:image"]')?.content?.slice(-40);
    out.h1=document.querySelectorAll('h1').length; out.title=document.title.length;
    out.externalNoRel=[...document.querySelectorAll('a[href^=http]')].filter(a=>!a.href.includes(location.host)&&!/noopener/.test(a.rel)).length;
    out.fontDisplay=[...document.styleSheets].some(s=>{try{return [...s.cssRules].some(r=>r.type===5&&!/swap|optional|fallback/.test(r.cssText))}catch(e){return false}})?'some-no-swap':'ok';
    out.fixedCount=[...document.querySelectorAll('body *')].filter(e=>getComputedStyle(e).position==='fixed'&&e.getBoundingClientRect().height>0).length;
    out.vh100=[...document.querySelectorAll('body *')].filter(e=>/100vh/.test(e.getAttribute('style')||'')).length;
    out.bodyText=document.body.innerText.length;
    out.lazyAboveFold=[...document.images].filter(i=>i.loading==='lazy'&&i.getBoundingClientRect().top<700&&i.getBoundingClientRect().height>0).length;
    return out;},lum.toString());
  const bad=reqs.filter(x=>x.s>=400).map(x=>x.s+' '+x.u.replace(B,'').slice(0,50));
  const bytes=reqs.length;
  console.log(JSON.stringify({u,m:mobile?'M':'D',status,reqs:bytes,bad,cssKB:Math.round(cs.total/1024),cssUsed:cs.total?Math.round(100*cs.used/cs.total)+'%':'-',jsKB:Math.round(jss.total/1024),jsUsed:jss.total?Math.round(100*jss.used/jss.total)+'%':'-',...r}));
  await p.close();
 }}
await b.close();process.exit(0);
