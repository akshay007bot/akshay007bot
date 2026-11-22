// Render ad.html frame-by-frame and pipe to ffmpeg.
// Usage: node render.js land|port [fps] [--stills t1,t2,...]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const mode = process.argv[2] || 'land';
const fps = Number(process.argv[3] || 30);
const stillsArg = process.argv.indexOf('--stills');
const stills = stillsArg > 0 ? process.argv[stillsArg + 1].split(',').map(Number) : null;
const [W, H] = mode === 'port' ? [1080, 1920] : [1920, 1080];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'ad.html'));
  await page.evaluate(m => window.setup(m), mode);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  const END = await page.evaluate(() => window.TIMELINE.END);

  if (stills) {
    for (const t of stills) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(__dirname, 'build', `still_${mode}_${t}.jpg`), type: 'jpeg', quality: 80 });
    }
    await browser.close();
    return;
  }

  const out = path.join(__dirname, 'build', `silent_${mode}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(END * fps);
  for (let f = 0; f < N; f++) {
    await page.evaluate(t => window.render(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`${mode}: frame ${f}/${N}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('wrote', out);
})();
