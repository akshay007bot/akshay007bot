// node render.mjs <brand> [Name]  -> <brand>/final/<Name>_Carousel_NN.png + PDF, with overflow check
import { chromium } from 'playwright'; import path from 'path'; import fs from 'fs';
const [,, brand, name = brand] = process.argv;
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 1500 } });
await p.goto('file://' + path.resolve(brand, 'carousel.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(800);
const rep = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s) => {
  const sb = s.getBoundingClientRect(); const bad = [];
  s.querySelectorAll('h1,h2,h3,p,b,span,small,div.c,img').forEach((e) => { const r = e.getBoundingClientRect(); if (!r.height || e.closest('.orb,.orb2,.ring,.deco')) return;
    if (r.bottom > sb.bottom - 40 || r.right > sb.right - 40 || r.left < sb.left + 40 && !e.closest('.bleed')) bad.push(`${e.tagName}.${e.className}:"${(e.textContent||'').trim().slice(0,24)}" b${Math.round(r.bottom-sb.top)} r${Math.round(r.right-sb.left)}`); });
  // collisions between foot and content
  const foot = s.querySelector('.foot'); const fr = foot && foot.getBoundingClientRect(); let maxb = 0;
  [...s.children].forEach((c) => { if (c === foot || c.classList.contains('orb') || c.classList.contains('orb2') || c.classList.contains('ring') || c.classList.contains('deco') || c.classList.contains('bg')) return; maxb = Math.max(maxb, c.getBoundingClientRect().bottom); });
  return `${s.id}: content→${Math.round(maxb - sb.top)} foot@${fr ? Math.round(fr.top - sb.top) : '-'} ${bad.slice(0, 3).join(' | ')}`;
}));
console.log(rep.join('\n'));
fs.mkdirSync(path.join(brand, 'final'), { recursive: true });
const ids = await p.$$eval('.slide', (s) => s.map((x) => x.id));
for (const [i, id] of ids.entries()) await p.locator('#' + id).screenshot({ path: path.join(brand, 'final', `${name}_Carousel_${String(i + 1).padStart(2, '0')}.png`) });
await p.addStyleTag({ content: 'body{background:none}.slide{margin:0;break-after:page}@page{size:1080px 1350px;margin:0}' });
await p.pdf({ path: path.join(brand, 'final', `${name}_Carousel.pdf`), width: '1080px', height: '1350px', printBackground: true });
await b.close();
