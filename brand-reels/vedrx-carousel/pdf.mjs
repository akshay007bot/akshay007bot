import { chromium } from 'playwright'; import path from 'path';
const b=await chromium.launch(); const p=await b.newPage();
await p.goto('file://'+path.resolve('carousel.html')); await p.evaluate(()=>document.fonts.ready);
await p.addStyleTag({content:'body{background:none}.slide{margin:0;break-after:page}@page{size:1080px 1350px;margin:0}'});
await p.pdf({path:'final/VedRxTours_Carousel.pdf',width:'1080px',height:'1350px',printBackground:true}); await b.close();
