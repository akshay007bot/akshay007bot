import { chromium } from 'playwright';
import path from 'path';
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
await p.goto('file://' + path.resolve('carousel.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
const issues = await p.evaluate(() => [...document.querySelectorAll('.slide')].map((s) => {
  const sb = s.getBoundingClientRect(), lim = sb.bottom - 104, out = [];
  s.querySelectorAll('.body *').forEach((e) => { const r = e.getBoundingClientRect(); if (r.height && (r.bottom > lim + 1 || r.right > sb.right - 87)) out.push(e.tagName + '.' + e.className + ' bottom+' + Math.round(r.bottom - lim) + ' right+' + Math.round(r.right - (sb.right - 88))); });
  const used = Math.max(...[...s.querySelectorAll('.body > *')].map((e) => e.getBoundingClientRect().bottom)) - sb.top;
  return s.id + ' content bottom ' + Math.round(used) + '/1246 ' + (out.slice(0, 3).join('; ') || 'ok');
}));
console.log(issues.join('\n'));
for (const id of await p.$$eval('.slide', (s) => s.map((x) => x.id))) await p.locator('#' + id).screenshot({ path: `out/${id}.png` });
await b.close();
