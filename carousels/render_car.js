const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const dir = process.argv[2]; const jobs = JSON.parse(fs.readFileSync(path.join(dir, 'html/jobs.json')));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const j of jobs) {
    const brand = j.replace(/-\d\d$/, ''); fs.mkdirSync(path.join(dir, brand), { recursive: true });
    await p.goto('file://' + path.join(dir, j + '.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(dir, brand, j + '.png') });
  }
  await b.close();
})();
