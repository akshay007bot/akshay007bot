// Render proposal HTML files to PDF + per-page preview PNGs.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const out = path.join(__dirname, 'output');
  const files = fs.readdirSync(out).filter(f => f.endsWith('.html'));
  const browser = await chromium.launch();
  for (const f of files) {
    const page = await browser.newPage({ viewport: { width: 794, height: 1123 } });
    await page.goto('file://' + path.join(out, f), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const pdf = path.join(out, f.replace('.html', '.pdf'));
    await page.pdf({ path: pdf, format: 'A4', printBackground: true, preferCSSPageSize: true });
    // overflow check: any page whose content runs into the footer
    const issues = await page.evaluate(() => [...document.querySelectorAll('.page')].map((p, i) => {
      const ftr = p.querySelector('.ftr'); if (!ftr) return null;
      const limit = ftr.getBoundingClientRect().top;
      let max = 0;
      p.querySelectorAll('.sec, .sec *').forEach(el => { const b = el.getBoundingClientRect().bottom; if (b > max) max = b; });
      return max > limit - 2 ? `page ${i + 1} overflows by ${Math.round(max - limit)}px` : null;
    }).filter(Boolean));
    console.log(pdf, issues.length ? issues : 'fits');
    if (process.argv.includes('--shots')) {
      const dir = path.join(__dirname, '..', '..', 'shots'); fs.mkdirSync(dir, { recursive: true });
      const n = await page.locator('.page').count();
      for (let i = 0; i < n; i++) await page.locator('.page').nth(i).screenshot({ path: path.join(process.env.SHOTS || out, `${f.replace('.html', '')}-p${i + 1}.png`) });
    }
    await page.close();
  }
  await browser.close();
})();
