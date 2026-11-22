// Serve this folder over HTTP (ES modules) and render ocean.html frame by frame.
// Usage: node render3.js land|port [--stills t1,t2]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const mode = process.argv[2] || 'land';
const si = process.argv.indexOf('--stills'); const stills = si > 0 ? process.argv[si + 1].split(',').map(Number) : null;
const [W, H] = mode === 'port' ? [1080, 1920] : [1920, 1080];
const FPS = 30, OUT = path.join(__dirname, 'build'); fs.mkdirSync(OUT, { recursive: true });
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.ttf': 'font/ttf' };
const srv = http.createServer((q, r) => { const f = path.join(__dirname, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); });
srv.listen(0, async () => {
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  page.on('console', m => { if (m.type() === 'error') console.log('PAGE', m.text()); });
  page.on('pageerror', e => console.log('PAGEERR', e.message));
  await page.goto(`http://127.0.0.1:${port}/ocean.html`);
  await page.waitForFunction(() => typeof window.setup === 'function');
  await page.evaluate(m => window.setup(m), mode);
  const END = await page.evaluate(() => window.TIMELINE.END);
  if (stills) {
    for (const t of stills) { await page.evaluate(t => window.render(t), t); await page.screenshot({ path: path.join(OUT, `st_${mode}_${t}.jpg`), type: 'jpeg', quality: 85 }); }
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path.join(OUT, `silent_${mode}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round(END * FPS);
    for (let f = 0; f < n; f++) {
      await page.evaluate(t => window.render(t), f / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 90 === 0) console.log(`${mode} ${f}/${n}`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close(); srv.close();
});
