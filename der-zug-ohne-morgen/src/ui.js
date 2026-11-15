// 2-D layer drawn over the 3-D picture: captions, speaker tag, part badge, phone notification, phone screen, choice card.
// All sizes are for a 1080x1920 frame and were measured from the reference (576x1024, scaled x1.875).
import { clamp, lerp, easeOut, backOut, FONT } from './util.js';

export const UI = {
  capX: 0.44, capY: 0.676, capSize: 68,         // captions sit left of centre (room for the app buttons on the right), 67.6% down
  ink: '#10143c', cardX: 0.465,
};
const font = (w, s) => `${w} ${s}px ${FONT}`;
function rr(x, X, Y, W, H, R) { x.beginPath(); x.roundRect(X, Y, W, H, R); }
function spaced(x, text, cx, y, sp, mode) { // centred text with extra letter spacing (px)
  const ws = [...text].map(ch => x.measureText(ch).width), total = ws.reduce((a, b) => a + b, 0) + sp * (text.length - 1); let px = cx - total / 2;
  const al = x.textAlign; x.textAlign = 'left'; [...text].forEach((ch, i) => { mode === 's' ? x.strokeText(ch, px, y) : x.fillText(ch, px, y); px += ws[i] + sp; }); x.textAlign = al;
}
// caption: bold rounded sans, coloured per speaker, dark navy outline + soft drop shadow. One short phrase at a time, hard switch.
export function drawCaption(x, W, H, text, color, { stretch = 0, alpha = 1, size = UI.capSize, y = UI.capY } = {}) {
  if (!text) return; const s = W / 1080, fs = size * s, cx = W * UI.capX, cy = H * y;
  x.save(); x.globalAlpha = alpha; x.font = font(900, fs); x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  let f = fs; while (x.measureText(text).width > W * 0.8 && f > 20) { f -= 2; x.font = font(900, f); }
  const sp = stretch * f * 0.34;
  x.shadowColor = 'rgba(8,10,40,0.75)'; x.shadowBlur = 10 * s; x.shadowOffsetY = 5 * s;
  x.strokeStyle = UI.ink; x.lineWidth = 11 * s; sp ? spaced(x, text, cx, cy, sp, 's') : x.strokeText(text, cx, cy);
  x.shadowColor = 'transparent'; x.fillStyle = color; sp ? spaced(x, text, cx, cy, sp, 'f') : x.fillText(text, cx, cy);
  x.restore();
}
// small pill above the caption that says where an unseen voice comes from ("FROM THE HALLWAY")
export function drawTag(x, W, H, text, alpha = 1) {
  if (!text) return; const s = W / 1080, fs = 27 * s; x.save(); x.globalAlpha = alpha; x.font = font(800, fs);
  const sp = 3.2 * s, tw = [...text].reduce((a, ch) => a + x.measureText(ch).width + sp, -sp), w = tw + 52 * s, h = 54 * s, cx = W * UI.capX, cy = H * (UI.capY - 0.0435);
  rr(x, cx - w / 2, cy - h / 2, w, h, 13 * s); x.fillStyle = 'rgba(18,22,58,0.92)'; x.fill(); x.lineWidth = 4 * s; x.strokeStyle = '#d5d8ff'; x.stroke();
  x.fillStyle = '#ffffff'; x.textBaseline = 'middle'; spaced(x, text, cx, cy + 2 * s, sp, 'f'); x.restore();
}
// top-left badge: "PART 2" + "You chose: KEEP IT LOCKED". k = 0..1 visibility
export function drawBadge(x, W, H, b, k) {
  if (!b || k <= 0) return; const s = W / 1080, X = 46 * s, Y = 200 * s; x.save(); x.globalAlpha = clamp(k); x.lineJoin = 'round'; x.textBaseline = 'middle'; x.textAlign = 'left';
  x.shadowColor = 'rgba(8,10,40,0.6)'; x.shadowBlur = 8 * s; x.shadowOffsetY = 4 * s;
  x.font = font(900, 82 * s); x.strokeStyle = UI.ink; x.lineWidth = 12 * s; x.strokeText(b.title, X, Y); x.shadowColor = 'transparent'; x.fillStyle = '#fff'; x.fillText(b.title, X, Y);
  if (b.label || b.value) { const y2 = Y + 75 * s; x.font = font(800, 38 * s); x.lineWidth = 8 * s; const lab = (b.label || '') + ' ';
    x.strokeText(lab, X, y2); x.fillStyle = '#fff'; x.fillText(lab, X, y2); const lw = x.measureText(lab).width;
    x.font = font(900, 38 * s); x.strokeText(b.value || '', X + lw, y2); x.fillStyle = b.color || '#ff5d55'; x.fillText(b.value || '', X + lw, y2); }
  x.restore();
}
function wrap(x, text, maxW) { const out = []; let line = ''; for (const w of text.split(' ')) { const t = line ? line + ' ' + w : w; if (x.measureText(t).width > maxW && line) { out.push(line); line = w; } else line = t; } if (line) out.push(line); return out; }
// phone notification banner at the top of the frame. n = { name, letter, color, text, hot, status, statusColor }, k = pop 0..1
export function drawBanner(x, W, H, n, k) {
  if (!n || k <= 0) return; const s = W / 1080, X = 66 * s, w = 790 * s, Y = 202 * s - (1 - easeOut(k)) * 26 * s; x.save(); x.globalAlpha = clamp(k * 1.6);
  x.font = font(800, 49 * s); const lines = wrap(x, n.text || ' ', w - 64 * s).slice(0, 3), hotLines = n.hot ? wrap(x, n.hot, w - 64 * s) : [];
  const h = (96 + (lines.length + hotLines.length) * 57 + 22) * s;
  x.shadowColor = 'rgba(0,0,20,0.5)'; x.shadowBlur = 22 * s; x.shadowOffsetY = 8 * s; rr(x, X, Y, w, h, 24 * s); x.fillStyle = '#fbf8ee'; x.fill(); x.shadowColor = 'transparent'; x.lineWidth = 5 * s; x.strokeStyle = '#0d1020'; x.stroke();
  const ax = X + 64 * s, ay = Y + 58 * s; x.beginPath(); x.arc(ax, ay, 30 * s, 0, 7); x.fillStyle = n.color || '#ff5c8d'; x.fill(); x.lineWidth = 4.5 * s; x.strokeStyle = '#0d1020'; x.stroke();
  x.fillStyle = '#0d1020'; x.font = font(900, 32 * s); x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText(n.letter || (n.name || '?')[0].toUpperCase(), ax, ay + 2 * s);
  x.textAlign = 'left'; x.font = font(800, 36 * s); x.fillText(n.name || '', ax + 50 * s, ay + 2 * s);
  x.textAlign = 'right'; x.font = font(800, 31 * s); x.fillStyle = n.statusColor || '#e23b3b'; x.fillText(n.status || '', X + w - 32 * s, ay + 2 * s);
  x.textAlign = 'left'; x.fillStyle = '#12142a'; x.font = font(800, 49 * s); let y = Y + 132 * s; for (const L of lines) { x.fillText(L, X + 32 * s, y); y += 57 * s; }
  x.fillStyle = '#e02a35'; x.font = font(900, 50 * s); for (const L of hotLines) { x.fillText(L, X + 32 * s, y); y += 57 * s; }
  x.restore();
}
// chat app on the phone screen (dark mode). Drawn into the phone's own canvas (w x h px).
// msgs: [{ me, text, style: 'alert' | undefined, k: pop 0..1, stamp }]  draft: text in the input bar
export function drawPhone(x, w, h, { name = 'Zoe', letter, color = '#ff5c8d', clock = '10:55', status = 'Active now', msgs = [], draft = '', delivered = 0 }) {
  const u = w / 400; x.fillStyle = '#0b0e17'; x.fillRect(0, 0, w, h); x.textBaseline = 'middle';
  x.fillStyle = '#fff'; x.font = font(700, 19 * u); x.textAlign = 'left'; x.fillText(clock, 34 * u, 40 * u);
  x.strokeStyle = '#cfd3e6'; x.lineWidth = 2 * u; x.strokeRect(w - 62 * u, 32 * u, 30 * u, 15 * u); x.fillStyle = '#ff4d5e'; x.fillRect(w - 59 * u, 35 * u, 8 * u, 9 * u);
  x.strokeStyle = '#3d8bff'; x.lineWidth = 4.5 * u; x.lineCap = 'round'; x.beginPath(); x.moveTo(40 * u, 80 * u); x.lineTo(30 * u, 91 * u); x.lineTo(40 * u, 102 * u); x.stroke();
  x.beginPath(); x.arc(84 * u, 92 * u, 25 * u, 0, 7); x.fillStyle = color; x.fill(); x.fillStyle = '#16182b'; x.font = font(900, 25 * u); x.textAlign = 'center'; x.fillText(letter || name[0].toUpperCase(), 84 * u, 94 * u);
  x.textAlign = 'left'; x.fillStyle = '#fff'; x.font = font(800, 25 * u); x.fillText(name, 124 * u, 82 * u); x.fillStyle = '#37d67a'; x.font = font(500, 16 * u); x.fillText(status, 124 * u, 107 * u);
  x.fillStyle = '#1c2130'; x.fillRect(22 * u, 138 * u, w - 44 * u, 2 * u);
  // input bar
  const by = h - 78 * u; rr(x, 22 * u, by, w - 106 * u, 48 * u, 24 * u); x.fillStyle = '#161b28'; x.fill();
  x.font = font(draft ? 700 : 500, 15.5 * u); x.fillStyle = draft ? '#fff' : '#6b7286'; let d = draft || 'Message'; while (x.measureText(d).width > w - 150 * u) d = d.slice(1); x.fillText(d, 40 * u, by + 25 * u);
  x.beginPath(); x.arc(w - 50 * u, by + 24 * u, 23 * u, 0, 7); x.fillStyle = draft ? '#2f7bf6' : '#1d2333'; x.fill(); x.strokeStyle = '#fff'; x.lineWidth = 3 * u; x.beginPath(); x.moveTo(w - 50 * u, by + 33 * u); x.lineTo(w - 50 * u, by + 15 * u); x.moveTo(w - 57 * u, by + 22 * u); x.lineTo(w - 50 * u, by + 15 * u); x.lineTo(w - 43 * u, by + 22 * u); x.stroke();
  // bubbles, bottom anchored; a new one pushes the others up while it pops in
  x.save(); x.beginPath(); x.rect(0, 142 * u, w, by - 150 * u); x.clip();
  const items = msgs.map(m => { const alert = m.style === 'alert'; x.font = font(alert ? 900 : 600, (alert ? 25 : 20.5) * u); const lines = m.stamp ? [m.stamp] : wrap(x, m.text, w * 0.56); const lh = (alert ? 30 : 26) * u;
    const bw = m.stamp ? 0 : Math.max(...lines.map(l => x.measureText(l).width)) + 34 * u, bh = m.stamp ? 30 * u : lines.length * lh + 24 * u; return { m, lines, lh, bw, bh, alert }; });
  let y = by - 16 * u + (delivered ? -20 * u * delivered : 0);
  for (let i = items.length - 1; i >= 0; i--) { const it = items[i], k = it.m.k == null ? 1 : clamp(it.m.k); const hh = (it.bh + 11 * u) * easeOut(k); y -= hh; if (y + it.bh < 140 * u || k <= 0) continue;
    if (it.m.stamp) { x.font = font(500, 14 * u); x.fillStyle = '#7c8398'; x.textAlign = 'center'; x.fillText(it.m.stamp, w / 2, y + 15 * u); continue; }
    const bx = it.m.me ? w - 30 * u - it.bw : 30 * u, sc = 0.82 + 0.18 * backOut(k); x.save(); x.globalAlpha = clamp(k * 2); x.translate(bx + (it.m.me ? it.bw : 0), y + it.bh); x.scale(sc, sc); x.translate(-(bx + (it.m.me ? it.bw : 0)), -(y + it.bh));
    rr(x, bx, y, it.bw, it.bh, 17 * u); x.fillStyle = it.alert ? (it.m.me ? '#2f7bf6' : '#a5242e') : it.m.me ? '#2f7bf6' : '#252b3a'; x.fill();
    x.font = font(it.alert ? 900 : 600, (it.alert ? 25 : 20.5) * u); x.fillStyle = it.alert && !it.m.me ? '#ffb9b9' : '#f2f4fb'; x.textAlign = 'left'; it.lines.forEach((l, j) => x.fillText(l, bx + 17 * u, y + 12 * u + it.lh * (j + 0.5))); x.restore(); }
  x.restore();
  if (delivered > 0) { x.globalAlpha = delivered; x.font = font(500, 13 * u); x.fillStyle = '#8089a0'; x.textAlign = 'right'; x.fillText('Delivered', w - 32 * u, by - 22 * u); x.globalAlpha = 1; }
}
function icon(x, kind, cx, cy, s) {
  x.save(); x.translate(cx, cy); x.lineJoin = 'round';
  if (kind === 'lock') { x.strokeStyle = '#1a1420'; x.lineWidth = 7 * s; x.beginPath(); x.arc(0, -10 * s, 13 * s, Math.PI, 0); x.stroke(); x.strokeStyle = '#fff4d0'; x.lineWidth = 3 * s; x.stroke(); rr(x, -19 * s, -10 * s, 38 * s, 31 * s, 6 * s); x.fillStyle = '#ffd23e'; x.fill(); x.lineWidth = 4.5 * s; x.strokeStyle = '#1a1420'; x.stroke(); }
  else if (kind === 'door') { rr(x, -16 * s, -23 * s, 32 * s, 46 * s, 4 * s); x.fillStyle = '#fff6ea'; x.fill(); x.lineWidth = 5 * s; x.strokeStyle = '#1a1420'; x.stroke(); x.beginPath(); x.arc(7 * s, 2 * s, 3.4 * s, 0, 7); x.fillStyle = '#1a1420'; x.fill(); }
  else if (kind === 'run') { x.fillStyle = '#fff6ea'; x.strokeStyle = '#1a1420'; x.lineWidth = 4.5 * s; x.beginPath(); x.moveTo(-16 * s, 0); x.lineTo(4 * s, -18 * s); x.lineTo(4 * s, -7 * s); x.lineTo(18 * s, -7 * s); x.lineTo(18 * s, 7 * s); x.lineTo(4 * s, 7 * s); x.lineTo(4 * s, 18 * s); x.closePath(); x.scale(-1, 1); x.fill(); x.stroke(); }
  else if (kind === 'eye') { x.fillStyle = '#fff6ea'; x.strokeStyle = '#1a1420'; x.lineWidth = 4.5 * s; x.beginPath(); x.ellipse(0, 0, 22 * s, 14 * s, 0, 0, 7); x.fill(); x.stroke(); x.beginPath(); x.arc(0, 0, 7 * s, 0, 7); x.fillStyle = '#1a1420'; x.fill(); }
  else if (kind === 'phone') { rr(x, -13 * s, -22 * s, 26 * s, 44 * s, 5 * s); x.fillStyle = '#fff6ea'; x.fill(); x.lineWidth = 5 * s; x.strokeStyle = '#1a1420'; x.stroke(); }
  else if (kind === 'x') { x.strokeStyle = '#1a1420'; x.lineWidth = 12 * s; x.lineCap = 'round'; x.beginPath(); x.moveTo(-13 * s, -13 * s); x.lineTo(13 * s, 13 * s); x.moveTo(13 * s, -13 * s); x.lineTo(-13 * s, 13 * s); x.stroke(); x.strokeStyle = '#fff6ea'; x.lineWidth = 6 * s; x.stroke(); }
  else if (kind === 'check') { x.strokeStyle = '#1a1420'; x.lineWidth = 12 * s; x.lineCap = 'round'; x.beginPath(); x.moveTo(-15 * s, 0); x.lineTo(-4 * s, 12 * s); x.lineTo(16 * s, -12 * s); x.stroke(); x.strokeStyle = '#fff6ea'; x.lineWidth = 6 * s; x.stroke(); }
  x.restore();
}
const BTN = { green: ['#2fa851', '#1f7d3a'], red: ['#d83a3a', '#a32626'], blue: ['#2f7bf6', '#1f58b8'], purple: ['#8a4be0', '#6331ad'], orange: ['#f08a24', '#b8630f'] };
// end card: dimmed + blurred last frame is already on the canvas. f = frames since the card started.
export function drawChoice(x, W, H, c, f) {
  const s = W / 1080, cx = W * UI.cardX; x.save(); x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  const pop = (f0, n = 5) => clamp((f - f0) / n);
  let k = pop(2, 4); if (k > 0) { const sc = 0.9 + 0.1 * backOut(k); x.save(); x.globalAlpha = k; x.translate(cx, 573 * s); x.scale(sc, sc); x.font = font(900, 91 * s);
    const L = c.question.split('\n'); L.forEach((l, i) => { const y = (i - (L.length - 1) / 2) * 104 * s; x.shadowColor = 'rgba(0,0,0,0.6)'; x.shadowBlur = 12 * s; x.shadowOffsetY = 6 * s; x.strokeStyle = '#0c0d18'; x.lineWidth = 13 * s; x.strokeText(l, 0, y); x.shadowColor = 'transparent'; x.fillStyle = '#fff'; x.fillText(l, 0, y); }); x.restore(); }
  const btn = (o, y, f0) => { const k = pop(f0, 6); if (k <= 0 || !o) return; const sc = 0.8 + 0.2 * backOut(k), w = 764 * s, h = 146 * s, [c1, c2] = BTN[o.color] || [o.color, o.color]; x.save(); x.globalAlpha = clamp(k * 1.5); x.translate(cx, y); x.scale(sc, sc);
    x.shadowColor = 'rgba(0,0,0,0.45)'; x.shadowBlur = 18 * s; x.shadowOffsetY = 8 * s; rr(x, -w / 2, -h / 2 + 7 * s, w, h, 24 * s); x.fillStyle = c2; x.fill(); x.shadowColor = 'transparent'; rr(x, -w / 2, -h / 2, w, h - 4 * s, 24 * s); x.fillStyle = c1; x.fill();
    x.font = font(900, 58 * s); const tw = x.measureText(o.text).width, iw = o.icon ? 76 * s : 0; if (o.icon) icon(x, o.icon, -tw / 2 - iw / 2 + 10 * s, -2 * s, s * 1.55);
    x.fillStyle = '#fff'; x.fillText(o.text, iw / 2, 1 * s); x.restore(); };
  btn(c.a, 851 * s, 18);
  k = pop(22, 4); if (k > 0) { x.globalAlpha = k; x.font = font(900, 41 * s); x.strokeStyle = '#0c0d18'; x.lineWidth = 8 * s; x.strokeText('OR', cx, 996 * s); x.fillStyle = '#ffc93c'; x.fillText('OR', cx, 996 * s); x.globalAlpha = 1; }
  btn(c.b, 1141 * s, 27);
  k = pop(42, 5); if (k > 0 && c.footer) { x.globalAlpha = k; x.font = font(900, 47 * s); const a = c.footer[0] + ' ', b = c.footer[1] || '', wa = x.measureText(a).width, wb = x.measureText(b).width, x0 = cx - (wa + wb) / 2, y = 1318 * s;
    x.textAlign = 'left'; x.strokeStyle = '#0c0d18'; x.lineWidth = 9 * s; x.strokeText(a + b, x0, y); x.fillStyle = '#fff'; x.fillText(a, x0, y); x.fillStyle = '#ffc93c'; x.fillText(b, x0 + wa, y);
    const ay = 1376 * s + Math.sin(f * 0.35) * 5 * s; x.strokeStyle = '#ffc93c'; x.lineWidth = 8 * s; x.lineCap = 'round'; x.beginPath(); x.moveTo(cx, ay - 20 * s); x.lineTo(cx, ay + 16 * s); x.moveTo(cx - 17 * s, ay); x.lineTo(cx, ay + 18 * s); x.lineTo(cx + 17 * s, ay); x.stroke(); x.globalAlpha = 1; }
  x.restore();
}
