// node tools/snap.mjs info            -> prints the beat table, writes timeline.json + voices.json + script_<speaker>.txt
// node tools/snap.mjs beats           -> one frame from the middle of every beat into snaps/
// node tools/snap.mjs 12.3 12.5 ...   -> frames at those seconds        (env: SCALE=0.5 PORT=8123 NOTIMINGS=1)
// node tools/snap.mjs range 12 13     -> every frame between two times (to study a whip pan or a pop)
import { chromium } from 'playwright'; import fs from 'fs';
const args = process.argv.slice(2), scale = process.env.SCALE || '0.5', port = process.env.PORT || 8123;
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl'] });
const p = await b.newPage({ viewport: { width: 540, height: 960 } }); p.on('pageerror', e => console.log('[pageerror]', e.message)); p.on('console', m => { if (m.type() === 'error') console.log('[console]', m.text()); });
await p.goto(`http://localhost:${port}/index.html?scale=${scale}${process.env.NOTIMINGS ? '&notimings' : ''}${process.env.STORY ? '&story=' + process.env.STORY : ''}`); await p.waitForFunction('window.READY===true', null, { timeout: 180000 });
const info = await p.evaluate('INFO()'); fs.mkdirSync('snaps', { recursive: true });
const shot = async (t, name) => { const url = await p.evaluate(t => { renderAt(t); return document.getElementById('c').toDataURL('image/jpeg', 0.9); }, t); fs.writeFileSync(name, Buffer.from(url.split(',')[1], 'base64')); };
if (args[0] === 'info' || !args.length) {
  fs.writeFileSync('timeline.json', JSON.stringify(info, null, 1));
  const by = {}; for (const l of info.lines) (by[l.voice] ||= []).push(l);      // one voiceover per VOICE (speakers that share a voice share a file)
  const voices = {}; for (const [v, L] of Object.entries(by)) { const script = L.map(l => l.text).join('\n\n'); fs.writeFileSync(`script_${v}.txt`, script + '\n'); voices[v] = { lines: L.map(l => l.n), chars: script.length, file: `audio/vo_${v}.mp3`, script: `script_${v}.txt` }; }
  fs.writeFileSync('voices.json', JSON.stringify(voices, null, 1));
  console.log(`${info.duration.toFixed(1)} s, ${info.frames} frames, ${info.lines.length} lines, ${info.lines.reduce((a, l) => a + l.text.split(' ').length, 0)} words, timing: ${info.voiced ? 'REAL VOICE' : 'estimated'}`);
  if (info.target) console.log(`target ${info.target} s -> pauses scaled x${info.pace}` + (!info.voiced ? '  (estimate: the real length is known after tools/voice.py)' : '') + (Math.abs(info.duration - info.target) > 1.5 ? `  BUT the script runs ${info.duration.toFixed(1)} s: ${info.duration > info.target ? 'cut' : 'add'} about ${Math.round(Math.abs(info.duration - info.target) * 2.4)} words (or a hold / phone beat)` : ''));
  if (info.unvoiced?.length) console.log(`WARNING: lines ${info.unvoiced.join(', ')} changed since the voiceover was made (word count differs). Re-record that voice, run tools/voice.py again.`);
  for (const x of info.beats) console.log(`${String(x.i).padStart(2)} ${x.t0.toFixed(2).padStart(6)}-${x.t1.toFixed(2).padStart(6)} ${x.type.padEnd(6)} ${(x.who || '').padEnd(8)} ${x.moved ? '>' : ' '}${String(x.look).padEnd(9)} ${String(x.zoom).padEnd(7)} ${x.text || ''}`);
  console.log('voiceovers needed:', Object.entries(voices).map(([k, v]) => `${k}: ${v.script} -> ${v.file} (${v.lines.length} lines, ${v.chars} chars)`).join(' | '));
} else if (args[0] === 'beats') { for (const x of info.beats) await shot((x.t0 + x.t1) / 2, `snaps/b${String(x.i).padStart(2, '0')}.jpg`); console.log(info.beats.length + ' snaps'); }
else if (args[0] === 'range') { const a = parseFloat(args[1]), e = parseFloat(args[2]); let n = 0; for (let f = Math.round(a * 30); f <= Math.round(e * 30); f++) { await shot((f + 0.5) / 30, `snaps/r${String(f).padStart(5, '0')}.jpg`); n++; } console.log(n + ' frames'); }
else for (const a of args) await shot(parseFloat(a), `snaps/t${parseFloat(a).toFixed(2).padStart(6, '0')}.jpg`);
await b.close();
