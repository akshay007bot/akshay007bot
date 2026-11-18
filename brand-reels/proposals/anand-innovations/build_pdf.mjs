import { chromium } from 'playwright'; import path from 'path'; import fs from 'fs';
const dir=process.argv[2]; const b=await chromium.launch();
const p=await b.newPage({viewport:{width:794,height:1123},deviceScaleFactor:2.5});
await p.goto('file://'+path.join(dir,'proposal.html')); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(800);
const n=await p.$$eval('.page',x=>x.length); fs.mkdirSync(path.join(dir,'pages'),{recursive:true}); const imgs=[];
for(let i=0;i<n;i++){const f=`page_${i+1}.jpg`; await p.locator('.page').nth(i).screenshot({path:path.join(dir,'pages',f),type:'jpeg',quality:92}); imgs.push(f);}
fs.writeFileSync(path.join(dir,'_imgs.html'),'<style>@page{size:A4;margin:0}body{margin:0}img{width:210mm;height:297mm;display:block;page-break-after:always}</style>'+imgs.map(f=>`<img src="pages/${f}">`).join(''));
const q=await b.newPage(); await q.goto('file://'+path.join(dir,'_imgs.html')); await q.waitForTimeout(500);
await q.pdf({path:path.join(dir,'iOceane_Proposal_Anand_Innovations.pdf'),preferCSSPageSize:true,printBackground:true}); await b.close(); fs.unlinkSync(path.join(dir,'_imgs.html'));
