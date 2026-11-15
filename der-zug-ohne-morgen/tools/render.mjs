// Full-frame renderer, resumable. Run one worker per 2 CPU cores, e.g. on 4 cores:
//   nohup node tools/render.mjs 0 2 > r0.log 2>&1 &    nohup node tools/render.mjs 1 2 > r1.log 2>&1 &
// Writes frames/f00000.jpg ... and skips frames that already exist.   env: SCALE=1 PORT=8123 FROM= TO= (frame range) OUT=frames
import { chromium } from 'playwright'; import fs from 'fs';
const wi = parseInt(process.argv[2] || '0'), wn = parseInt(process.argv[3] || '1'), scale = process.env.SCALE || '1', port = process.env.PORT || 8123, dir = process.env.OUT || 'frames';
fs.mkdirSync(dir, { recursive: true });
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
const p = await b.newPage({ viewport: { width: 540, height: 960 } }); p.on('pageerror', e => console.log('[pageerror]', e.message));
await p.goto(`http://localhost:${port}/index.html?scale=${scale}${process.env.STORY ? '&story=' + process.env.STORY : ''}`); await p.waitForFunction('window.READY===true', null, { timeout: 180000 });
const N = await p.evaluate('FRAMES'), from = parseInt(process.env.FROM || '0'), to = Math.min(N, parseInt(process.env.TO || N));
const t0 = Date.now(); let done = 0;
for (let f = from; f < to; f++) {
  if (f % wn !== wi) continue; const name = `${dir}/f${String(f).padStart(5, '0')}.jpg`; if (fs.existsSync(name)) continue;
  const url = await p.evaluate(f => { renderAt((f + 0.5) / 30); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, f);
  fs.writeFileSync(name + '.tmp', Buffer.from(url.split(',')[1], 'base64')); fs.renameSync(name + '.tmp', name);
  if (++done % 20 === 0) console.log(`worker ${wi}: frame ${f}/${N}  ${((Date.now() - t0) / done / 1000).toFixed(2)} s/frame`);
}
console.log(`worker ${wi} done (${done} frames)`); await b.close();
