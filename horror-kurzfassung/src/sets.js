// Sets and props. One unit = one metre, floor at y = 0. A room is centred on the origin: front wall at z = -d/2 (the one the
// viewer mostly looks at), back wall at z = +d/2, left wall x = -w/2, right wall x = +w/2.
import { THREE, toon, lam, flat, box, rbox, sph, cyl, plane, disc, grp, at, noOutline, sameId, sign, glow, canvasTex, rng, clamp } from './util.js';

// ---------------------------------------------------------------- lighting moods
// amb = flat fill, key = soft directional that gives the toon bands, sky/ground = hemisphere tint
export const MOODS = {
  lockdown: { bg: '#070820', amb: ['#666eb4', 1.2], hemi: ['#8388cc', '#15173f', 0.85], key: ['#9aa4f0', 0.45, [2, 5, 4]], pulse: ['#ff4f9e', 3.2], spill: ['#e6ecff', 4.2] },   // lights off, alarm beacon, light under the door
  night:    { bg: '#060718', amb: ['#4a55b8', 1.5], hemi: ['#5d68d8', '#161838', 1.0], key: ['#9fb0ff', 1.0, [-3, 6, 3]], pulse: ['#ff4f9e', 0], spill: ['#dfe8ff', 4] },
  dark:     { bg: '#030410', amb: ['#2c3382', 1.2], hemi: ['#3a4298', '#0c0d24', 0.8], key: ['#7f8cff', 0.5, [1, 5, 3]], pulse: ['#ff2a2a', 0], spill: ['#fff1d0', 5] },
  red:      { bg: '#120408', amb: ['#a8324a', 1.5], hemi: ['#c8405a', '#2a0a14', 1.0], key: ['#ff8a8a', 0.8, [2, 5, 4]], pulse: ['#ff2020', 5], spill: ['#ffe0e0', 4] },      // emergency lighting
  dusk:     { bg: '#1a1030', amb: ['#8a6fc0', 1.9], hemi: ['#b48ad8', '#3a2850', 1.3], key: ['#ffb07a', 1.5, [-4, 4, 3]], pulse: ['#ff4f9e', 0], spill: ['#ffe9c8', 3] },
  day:      { bg: '#bfe3ff', amb: ['#ffffff', 1.55], hemi: ['#ffffff', '#b9b2a8', 0.9], key: ['#fff4e0', 0.95, [3, 6, 4]], pulse: ['#ff4f9e', 0], spill: ['#ffffff', 0] },
  warm:     { bg: '#1c120c', amb: ['#c89a78', 1.15], hemi: ['#ffd9a8', '#4a3226', 0.8], key: ['#ffd9a0', 0.8, [2, 5, 3]], pulse: ['#ff4f9e', 0], spill: ['#fff1d0', 3] },
  green:    { bg: '#04100c', amb: ['#3a9a78', 1.5], hemi: ['#52c89a', '#0c2a20', 1.0], key: ['#9fffd0', 0.8, [2, 5, 4]], pulse: ['#40ff9a', 4], spill: ['#e0fff0', 4] },      // toxic / sci-fi
};
// makeSet(group, { mood, pov, look, targets, spillAt, pulseAt }) -> the object the story uses
export function makeSet(group, o = {}) {
  const M = { ...MOODS[o.mood || 'lockdown'], ...(o.moodOverride || {}) }, scene = new THREE.Scene(); scene.add(group);
  const amb = new THREE.AmbientLight(M.amb[0], M.amb[1]), hemi = new THREE.HemisphereLight(M.hemi[0], M.hemi[1], M.hemi[2]), key = new THREE.DirectionalLight(M.key[0], M.key[1]); key.position.set(...M.key[2]);
  const pulse = new THREE.PointLight(M.pulse[0], 0, 14, 1.4), spill = new THREE.PointLight(M.spill[0], 0, 9, 1.5); pulse.position.set(...(o.pulseAt || [0, 2.7, 0])); spill.position.set(...(o.spillAt || [0, 0.25, -3.6]));
  scene.add(amb, hemi, key, pulse, spill);
  const S = { scene, group, bg: new THREE.Color(M.bg).getHex(), pov: o.pov || [0, 1.5, 3], look: o.look || [0, 1.2, -4], targets: o.targets || {}, parts: o.parts || {}, mood: M,
    // vars the story can animate: pulse (alarm strength 0..1), spill (light under the door 0..1), feet (shadow of someone standing outside 0..1), door (0 shut..1 open), lights (ceiling lights 0..1), dim (0..1 darker)
    update(v, t) {
      const p = v.pulse ?? o.pulse ?? (M.pulse[1] ? 1 : 0), period = v.pulsePeriod ?? 0.8, w = Math.pow(0.5 + 0.5 * Math.sin(t * 2 * Math.PI / period), 1.6);
      pulse.intensity = M.pulse[1] * p * (0.12 + 0.88 * w); const sp = v.spill ?? o.spill ?? 1; spill.intensity = M.spill[1] * sp * (1 - 0.35 * (v.feet ?? 0));
      const L = v.lights ?? 0, dim = 1 - 0.6 * (v.dim ?? 0); amb.intensity = (M.amb[1] + 2.2 * L) * dim; hemi.intensity = (M.hemi[2] + 1.0 * L) * dim; key.intensity = M.key[1] * dim;
      amb.color.set(M.amb[0]).lerp(new THREE.Color('#ffffff'), L * 0.8);
      o.onUpdate?.(v, t, S);
    } };
  return S;
}

// ---------------------------------------------------------------- props (all face +z, origin on the floor or wall plane)
const WOOD = '#c9996a', METAL = '#8c9cd4', CHAIR = '#4a68cc';
let tileTex;
export function shell(w, d, h, { wall = '#d6d7ea', floor = '#6f7cc8', ceil = '#c9cbe4', wains = null, tiles = true, trim = '#7f88bd' } = {}) {
  tileTex ||= canvasTex(256, 256, (x) => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); x.strokeStyle = 'rgba(40,46,110,0.22)'; x.lineWidth = 5; x.strokeRect(0, 0, 256, 256); });
  const ft = tileTex.clone(); ft.wrapS = ft.wrapT = THREE.RepeatWrapping; ft.repeat.set(w / 0.9, d / 0.9); ft.needsUpdate = true;
  const g = new THREE.Group(), fm = tiles ? new THREE.MeshLambertMaterial({ color: floor, map: ft }) : lam(floor);
  g.add(plane(w, d, fm, [0, 0, 0], [-Math.PI / 2, 0, 0])); g.add(plane(w, d, lam(ceil), [0, h, 0], [Math.PI / 2, 0, 0]));
  const walls = [[0, -d / 2, 0, w], [0, d / 2, Math.PI, w], [-w / 2, 0, Math.PI / 2, d], [w / 2, 0, -Math.PI / 2, d]];
  for (const [x, z, ry, len] of walls) { g.add(plane(len, h, lam(wall), [x, h / 2, z], [0, ry, 0]));
    if (wains) { const p = plane(len, 1.0, lam(wains), [x, 0.5, z], [0, ry, 0]); p.translateZ(0.012); g.add(p); const r = box(len, 0.05, 0.03, lam(trim), [x, 1.02, z], [0, ry, 0]); r.translateZ(0.02); g.add(r); }
    const b = box(len, 0.12, 0.03, lam(trim), [x, 0.06, z], [0, ry, 0]); b.translateZ(0.02); g.add(b); }
  return g;
}
// put a wall prop on a wall: wall = 'front' | 'back' | 'left' | 'right', u = position along it, y = height of the prop origin
export function onWall(obj, wall, u, y, w, d, off = 0.03) {
  if (wall === 'front') at(obj, [u, y, -d / 2 + off], [0, 0, 0]); else if (wall === 'back') at(obj, [u, y, d / 2 - off], [0, Math.PI, 0]);
  else if (wall === 'left') at(obj, [-w / 2 + off, y, u], [0, Math.PI / 2, 0]); else at(obj, [w / 2 - off, y, u], [0, -Math.PI / 2, 0]); return obj;
}
// door with a lit window slot; light leaks under it. Returns { g, feet, leaf } — origin at floor centre of the doorway.
export function door({ color = '#6d84c8', frame = '#4a5ea6', lit = '#f2f6ff', w = 1.0, h = 2.15, window = true, handle = 'right' } = {}) {
  const g = new THREE.Group(), leaf = new THREE.Group(); g.add(box(w + 0.2, h + 0.1, 0.06, lam(frame), [0, (h + 0.1) / 2, 0])); leaf.add(box(w, h, 0.05, lam(color), [0, h / 2, 0.03]));
  leaf.add(box(w - 0.16, h * 0.34, 0.012, lam(new THREE.Color(color).multiplyScalar(0.93).getHex()), [0, h * 0.24, 0.06]));
  if (window) { leaf.add(noOutline(box(0.2, 0.74, 0.02, flat(lit), [0.1, h * 0.69, 0.055]))); leaf.add(box(0.26, 0.8, 0.012, lam(frame), [0.1, h * 0.69, 0.05])); leaf.add(glow(1.0, 1.6, lit, 0.3, [0.1, h * 0.69, 0.09])); }
  const hs = handle === 'right' ? 1 : -1; leaf.add(box(0.07, 0.2, 0.02, toon('#c9cfe8'), [0.36 * hs, 1.02, 0.065])); leaf.add(box(0.17, 0.035, 0.035, toon('#c9cfe8'), [0.3 * hs, 1.0, 0.09]));
  g.add(leaf);
  // light under the door + its pool on the floor + the shadows of two feet
  const strip = noOutline(box(w + 0.02, 0.035, 0.02, flat('#ffffff'), [0, 0.02, 0.06])); g.add(strip);
  const poolTex = canvasTex(128, 128, (x) => { const gr = x.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, 'rgba(255,255,255,0.95)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.3)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.beginPath(); x.moveTo(24, 0); x.lineTo(104, 0); x.lineTo(128, 128); x.lineTo(0, 128); x.fill(); });
  const pool = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(w * 2.2, 1.7), new THREE.MeshBasicMaterial({ map: poolTex, color: lit, transparent: true, opacity: 0.42, blending: THREE.AdditiveBlending, depthWrite: false }))); at(pool, [0, 0.008, 0.9], [-Math.PI / 2, 0, 0]); g.add(pool);
  g.add(glow(w * 2.6, 0.5, lit, 0.5, [0, 0.1, 0.12]));
  const feet = new THREE.Group(); for (const s of [-1, 1]) { feet.add(noOutline(box(0.13, 0.04, 0.03, flat('#0a0c26'), [s * 0.14 - 0.08, 0.02, 0.065])));
    const sh = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(0.15, 1.1), new THREE.MeshBasicMaterial({ color: '#0a0c26', transparent: true, opacity: 0.5, depthWrite: false }))); at(sh, [s * 0.16 - 0.08, 0.011, 0.6], [-Math.PI / 2, 0, s * -0.08]); feet.add(sh); }
  g.add(feet);
  const feet2 = new THREE.Group(); for (const x of [-0.5, 0.38]) { feet2.add(noOutline(box(0.13, 0.04, 0.03, flat('#0a0c26'), [x, 0.02, 0.065])));
    const sh = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(0.15, 1.1), new THREE.MeshBasicMaterial({ color: '#0a0c26', transparent: true, opacity: 0.5, depthWrite: false }))); at(sh, [x * 1.25, 0.011, 0.6], [-Math.PI / 2, 0, x * -0.3]); feet2.add(sh); }
  g.add(feet2); const setFeet = n => { feet.visible = n > 0.5; feet2.visible = n > 1.5; }; setFeet(0);
  return { g, feet, feet2, setFeet, leaf, strip, pool };
}
export function desk({ top = WOOD, body = METAL, w = 1.15, panel = true } = {}) {
  const g = new THREE.Group(), m = toon(body); g.add(box(w, 0.045, 0.62, toon(top), [0, 0.74, 0])); g.add(box(w - 0.1, 0.11, 0.5, m, [0, 0.665, 0]));
  for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) g.add(box(0.045, 0.62, 0.045, m, [x * (w / 2 - 0.06), 0.31, z * 0.26]));
  if (panel) g.add(box(w - 0.14, 0.36, 0.02, m, [0, 0.43, -0.27])); return sameIdPart(g);
}
export function chair({ color = CHAIR, leg = METAL } = {}) {
  const g = new THREE.Group(), m = toon(color), l = toon(leg); g.add(rbox(0.42, 0.045, 0.42, 0.02, m, [0, 0.45, 0])); g.add(rbox(0.42, 0.4, 0.04, 0.02, m, [0, 0.74, -0.2], [-0.1, 0, 0]));
  for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) g.add(box(0.03, 0.45, 0.03, l, [x * 0.18, 0.225, z * 0.18])); for (const x of [-1, 1]) g.add(box(0.03, 0.34, 0.03, l, [x * 0.18, 0.62, -0.2])); return g;
}
function sameIdPart(g) { return g; }
export function lockers(n = 4, { color = '#8f9fd6', h = 1.9 } = {}) {
  const g = new THREE.Group(), m = toon(color), dk = toon(new THREE.Color(color).multiplyScalar(0.72).getHex());
  for (let i = 0; i < n; i++) { const x = (i - (n - 1) / 2) * 0.46; g.add(box(0.44, h, 0.45, m, [x, h / 2, 0.225])); g.add(noOutline(box(0.2, 0.14, 0.01, dk, [x, h * 0.78, 0.456]))); for (let k = 0; k < 3; k++) g.add(noOutline(box(0.16, 0.012, 0.012, m, [x, h * 0.78 - 0.04 + k * 0.04, 0.462]))); g.add(noOutline(box(0.03, 0.1, 0.02, dk, [x + 0.15, h * 0.5, 0.46]))); }
  return g;
}
export function bookshelf({ w = 1.5, h = 1.5, wood = '#7b4c34', rows = 3, seed = 3 } = {}) {
  const g = new THREE.Group(), m = toon(wood), r = rng(seed), cols = ['#3d58c8', '#c7473f', '#d9a531', '#3f9a78', '#7a4bc0', '#d06a2c', '#2f8fb8'];
  g.add(box(w, h, 0.32, m, [0, h / 2, 0.16])); g.add(noOutline(box(w - 0.1, h - 0.1, 0.02, toon(new THREE.Color(wood).multiplyScalar(0.6).getHex()), [0, h / 2, 0.315])));
  for (let k = 0; k < rows; k++) { const y0 = 0.07 + k * (h - 0.1) / rows, sh = (h - 0.1) / rows; g.add(box(w - 0.08, 0.035, 0.3, m, [0, y0, 0.19])); let x = -w / 2 + 0.1;
    while (x < w / 2 - 0.14) { const bw = 0.05 + r() * 0.05, bh = sh * (0.55 + r() * 0.3); if (r() > 0.14) g.add(noOutline(box(bw, bh, 0.2, toon(cols[Math.floor(r() * cols.length)]), [x + bw / 2, y0 + 0.02 + bh / 2, 0.24]))); x += bw + 0.012; } }
  return g;
}
export function bulletin({ w = 1.5, h = 1.1, seed = 5 } = {}) {
  const g = new THREE.Group(), r = rng(seed), cols = ['#f1ead2', '#f3b6c4', '#b9d7f5', '#c7e6b9', '#f6dd9a', '#d9c2f0']; g.add(box(w, h, 0.05, toon('#8b5a36'), [0, 0, 0])); g.add(noOutline(box(w - 0.12, h - 0.12, 0.012, lam('#c9a26c'), [0, 0, 0.03])));
  const nx = Math.round(w / 0.36), ny = Math.round(h / 0.42); for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const pw = 0.24, ph = 0.31, px = (i - (nx - 1) / 2) * (w - 0.2) / nx, py = (j - (ny - 1) / 2) * (h - 0.16) / ny;
    const p = sign('', pw, ph, { bg: cols[Math.floor(r() * cols.length)] }); const c = p.material.map.image.getContext('2d'); c.fillStyle = 'rgba(40,40,90,0.45)'; for (let k = 0; k < 6; k++) c.fillRect(20, 46 + k * 30, 100 + r() * 60, 9); p.material.map.needsUpdate = true; at(p, [px, py, 0.04], [0, 0, (r() - 0.5) * 0.12]); g.add(p); }
  return g;
}
export function chalkboard({ w = 2.6, h = 1.25, title = 'BIOLOGY FINAL', lines = ['10:00 - 11:30', 'NO TALKING'], color = '#2c6652' } = {}) {
  const tex = canvasTex(832, 400, (x) => { x.fillStyle = color; x.fillRect(0, 0, 832, 400); x.fillStyle = 'rgba(255,255,255,0.9)'; x.font = '800 62px Rubik, sans-serif'; x.textBaseline = 'middle'; x.fillText(title, 36, 64); x.font = '600 36px Rubik, sans-serif'; x.fillStyle = 'rgba(255,255,255,0.7)'; lines.forEach((l, i) => x.fillText(l, 36, 132 + i * 46));
    x.strokeStyle = 'rgba(255,255,255,0.75)'; x.lineWidth = 5; for (const ph of [0, Math.PI]) { x.beginPath(); for (let i = 0; i <= 120; i++) { const px = 60 + i * 5.6, py = 300 + Math.sin(i * 0.26 + ph) * 44; i ? x.lineTo(px, py) : x.moveTo(px, py); } x.stroke(); } for (let i = 0; i < 24; i++) { const px = 74 + i * 28; x.beginPath(); x.moveTo(px, 300 - Math.sin(i * 1.3 + 0.35) * 40); x.lineTo(px, 300 + Math.sin(i * 1.3 + 0.35) * 40); x.stroke(); } });
  const g = new THREE.Group(); g.add(box(w + 0.14, h + 0.14, 0.05, toon('#7a5433'), [0, 0, 0])); g.add(noOutline(at(new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshLambertMaterial({ map: tex })), [0, 0, 0.03]))); g.add(box(w, 0.04, 0.09, toon('#7a5433'), [0, -h / 2 - 0.03, 0.05])); return g;
}
export function clock() { const tex = canvasTex(128, 128, (x) => { x.fillStyle = '#f4f5fb'; x.beginPath(); x.arc(64, 64, 62, 0, 7); x.fill(); x.strokeStyle = '#141632'; x.lineWidth = 6; x.lineCap = 'round'; x.beginPath(); x.moveTo(64, 64); x.lineTo(64, 22); x.moveTo(64, 64); x.lineTo(46, 40); x.stroke(); for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; x.lineWidth = 3; x.beginPath(); x.moveTo(64 + Math.cos(a) * 50, 64 + Math.sin(a) * 50); x.lineTo(64 + Math.cos(a) * 56, 64 + Math.sin(a) * 56); x.stroke(); } });
  const g = new THREE.Group(); g.add(cyl(0.2, 0.2, 0.04, toon('#141632'), [0, 0, 0], [Math.PI / 2, 0, 0], 28)); g.add(noOutline(at(new THREE.Mesh(new THREE.CircleGeometry(0.17, 28), new THREE.MeshLambertMaterial({ map: tex })), [0, 0, 0.025]))); return g; }
export function exitSign(text = 'EXIT', color = '#2f9a63') { const g = new THREE.Group(); g.add(box(0.5, 0.2, 0.04, toon('#1d6b45'), [0, 0, 0])); g.add(noOutline(at(sign(text, 0.46, 0.16, { bg: color, fg: '#d9ffe9', weight: 900, size: 0.8, lit: true }), [0, 0, 0.022]))); return g; }
export function speaker() { const g = new THREE.Group(); g.add(rbox(0.3, 0.26, 0.06, 0.02, toon('#b9bdd8'), [0, 0, 0])); g.add(noOutline(disc(0.075, flat('#2a2d4a'), [0, 0, 0.032]))); g.add(noOutline(disc(0.03, flat('#555a80'), [0, 0, 0.034]))); return g; }
export function poster(title, lines = [], { w = 0.46, h = 0.6, bg = '#f4f1e6', head = '#d8423c' } = {}) {
  const tex = canvasTex(368, 480, (x) => { x.fillStyle = bg; x.fillRect(0, 0, 368, 480); x.fillStyle = head; x.fillRect(0, 0, 368, 96); x.fillStyle = '#fff'; x.textAlign = 'center'; x.textBaseline = 'middle'; let f = 58; x.font = `900 ${f}px Rubik, sans-serif`; while (x.measureText(title).width > 330) { f -= 3; x.font = `900 ${f}px Rubik, sans-serif`; } x.fillText(title, 184, 52);
    x.fillStyle = '#23264a'; x.textAlign = 'left'; lines.forEach((l, i) => { let f = 46; x.font = `800 ${f}px Rubik, sans-serif`; while (x.measureText(l).width > 310) { f -= 3; x.font = `800 ${f}px Rubik, sans-serif`; } x.fillText(l, 30, 160 + i * 74); }); });
  const g = new THREE.Group(); g.add(box(w + 0.03, h + 0.03, 0.012, toon('#23264a'), [0, 0, 0])); g.add(noOutline(at(new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshLambertMaterial({ map: tex })), [0, 0, 0.009]))); return g;
}
export function ceilingPanel(w = 1.3, d = 0.45) { const g = new THREE.Group(); g.add(box(w, 0.05, d, lam('#aab1dc'), [0, -0.03, 0])); for (let i = 1; i < 5; i++) g.add(noOutline(box(0.015, 0.012, d - 0.04, lam('#7f88bd'), [-w / 2 + i * w / 5, -0.058, 0]))); return g; }
// window with blinds; lit = colour of the light behind it (street lamp orange, moon blue, daylight)
export function windowBlinds({ w = 1.5, h = 1.2, lit = '#ff9a5a', slats = 9, strength = 0.9 } = {}) { const g = new THREE.Group(); g.add(box(w + 0.14, h + 0.14, 0.06, toon('#5a66a8'), [0, 0, 0])); g.add(noOutline(box(w, h, 0.02, flat(new THREE.Color(lit).multiplyScalar(strength).getHex()), [0, 0, 0.03])));
  for (let i = 0; i < slats; i++) g.add(noOutline(box(w, h / slats * 0.42, 0.012, flat(new THREE.Color(lit).multiplyScalar(0.38).getHex()), [0, -h / 2 + (i + 0.5) * h / slats, 0.045]))); g.add(glow(w * 1.6, h * 1.6, lit, 0.22, [0, 0, 0.1])); return g; }
export function backpack(color = '#6a3fd0', tag = null) { const g = new THREE.Group(); g.add(rbox(0.36, 0.44, 0.22, 0.09, toon(color), [0, 0.22, 0])); g.add(rbox(0.26, 0.18, 0.06, 0.03, toon(new THREE.Color(color).multiplyScalar(0.8).getHex()), [0, 0.14, 0.12])); g.add(noOutline(sph(0.035, toon('#e0a52e'), [0, 0.14, 0.155])));
  if (tag) g.add(at(sign(tag, 0.13, 0.085, { bg: '#f4f1e6', fg: '#23264a', weight: 900, size: 0.7, border: '#23264a' }), [0.1, 0.36, 0.125], [0, 0, -0.2])); return g; }
export function bed({ cover = '#5a6fd0', pillow = '#e8eaf6', frame = '#7b4c34' } = {}) { const g = new THREE.Group(); g.add(box(1.1, 0.3, 2.1, toon(frame), [0, 0.15, 0])); g.add(rbox(1.04, 0.2, 2.0, 0.08, toon('#e8eaf6'), [0, 0.38, 0])); g.add(rbox(1.08, 0.14, 1.35, 0.06, toon(cover), [0, 0.46, 0.34])); g.add(rbox(0.7, 0.14, 0.4, 0.06, toon(pillow), [0, 0.52, -0.75])); g.add(box(1.1, 0.75, 0.08, toon(frame), [0, 0.5, -1.06])); return g; }
export function wardrobe({ color = '#8a5a3c', w = 1.4, h = 2.1 } = {}) { const g = new THREE.Group(); g.add(box(w, h, 0.55, toon(color), [0, h / 2, 0.275])); const dk = toon(new THREE.Color(color).multiplyScalar(0.8).getHex()); for (const s of [-1, 1]) { g.add(box(w / 2 - 0.05, h - 0.12, 0.02, dk, [s * w / 4, h / 2, 0.56])); g.add(noOutline(sph(0.03, toon('#e0c070'), [s * 0.07, h / 2, 0.585]))); } return g; }
export function sofa({ color = '#5a6fd0' } = {}) { const g = new THREE.Group(), m = toon(color); g.add(rbox(1.9, 0.38, 0.85, 0.1, m, [0, 0.27, 0])); g.add(rbox(1.9, 0.6, 0.24, 0.1, m, [0, 0.62, -0.33])); for (const s of [-1, 1]) g.add(rbox(0.24, 0.52, 0.85, 0.1, m, [s * 0.95, 0.4, 0])); return g; }
export function tv({ on = '#9fc4ff' } = {}) { const g = new THREE.Group(); g.add(box(1.5, 0.5, 0.42, toon('#5b4636'), [0, 0.25, 0])); g.add(box(1.3, 0.76, 0.06, toon('#12131c'), [0, 0.95, 0])); g.add(noOutline(box(1.22, 0.68, 0.01, flat(on), [0, 0.95, 0.035]))); g.add(glow(2.4, 1.6, on, 0.25, [0, 0.95, 0.1])); return g; }
export function table({ w = 1.4, d = 0.8, h = 0.74, color = WOOD } = {}) { const g = new THREE.Group(), m = toon(color); g.add(box(w, 0.05, d, m, [0, h, 0])); for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) g.add(box(0.06, h, 0.06, m, [x * (w / 2 - 0.07), h / 2, z * (d / 2 - 0.07)])); return g; }
export function counter({ w = 2.4, color = '#8c9cd4', top = '#e8eaf6' } = {}) { const g = new THREE.Group(); g.add(box(w, 0.95, 0.6, toon(color), [0, 0.475, 0])); g.add(box(w + 0.06, 0.05, 0.66, toon(top), [0, 0.975, 0])); return g; }
export function shelfUnit({ w = 1.6, h = 1.8, seed = 2, color = '#b9bdd8' } = {}) { const g = new THREE.Group(), r = rng(seed), cols = ['#d84a42', '#e2a52e', '#3f9a78', '#3d58c8', '#b65ad0', '#f08a24']; g.add(box(w, h, 0.4, toon(color), [0, h / 2, 0.2]));
  for (let k = 0; k < 4; k++) { const y = 0.12 + k * (h - 0.15) / 4; g.add(box(w - 0.06, 0.03, 0.4, toon('#eceef8'), [0, y, 0.22])); for (let x = -w / 2 + 0.14; x < w / 2 - 0.1; x += 0.17) if (r() > 0.2) g.add(noOutline(rbox(0.12, 0.16 + r() * 0.12, 0.12, 0.03, toon(cols[Math.floor(r() * cols.length)]), [x, y + 0.13, 0.3]))); } return g; }
export function plant() { const g = new THREE.Group(); g.add(cyl(0.16, 0.12, 0.26, toon('#c7683f'), [0, 0.13, 0])); const l = sameId(grp(sph(0.2, toon('#3f9a63'), [0, 0.5, 0]), sph(0.15, toon('#3f9a63'), [0.13, 0.42, 0.05]), sph(0.15, toon('#3f9a63'), [-0.12, 0.44, -0.04]))); l.traverse(o => { o.userData.inkFlat = true; }); g.add(l); return g; }
export function lamp({ on = true, color = '#ffd98a' } = {}) { const g = new THREE.Group(); g.add(cyl(0.1, 0.12, 0.03, toon('#5b4636'), [0, 0.015, 0])); g.add(cyl(0.015, 0.015, 0.36, toon('#5b4636'), [0, 0.2, 0])); g.add(noOutline(cyl(0.1, 0.16, 0.2, on ? flat(color) : toon('#d8d0c0'), [0, 0.46, 0]))); if (on) g.add(glow(1.2, 1.2, color, 0.45, [0, 0.46, 0.05])); return g; }
export function streetLamp({ color = '#ffd98a' } = {}) { const g = new THREE.Group(); g.add(cyl(0.05, 0.07, 4, toon('#2a2d4a'), [0, 2, 0])); g.add(box(0.7, 0.06, 0.08, toon('#2a2d4a'), [0.3, 4, 0])); g.add(noOutline(box(0.3, 0.07, 0.16, flat(color), [0.58, 3.94, 0]))); g.add(glow(2.6, 2.6, color, 0.5, [0.58, 3.9, 0.1])); return g; }
export function house({ w = 5, h = 3.4, color = '#8f7fb8', roof = '#4a3f6e', lit = '#ffd98a', door: dc = '#5b4636', seed = 1 } = {}) { const g = new THREE.Group(), r = rng(seed); g.add(box(w, h, 3, lam(color), [0, h / 2, -1.5])); const rf = new THREE.Mesh(new THREE.CylinderGeometry(0.02, w * 0.62, 1.5, 4), toon(roof)); at(rf, [0, h + 0.75, -1.5], [0, Math.PI / 4, 0], [1, 1, 0.75]); g.add(rf);
  g.add(box(0.9, 1.9, 0.06, toon(dc), [0, 0.95, 0.02])); for (const s of [-1, 1]) { const on = r() > 0.4; g.add(box(1.0, 0.9, 0.05, toon('#3a3560'), [s * w * 0.3, h * 0.55, 0.02])); g.add(noOutline(box(0.86, 0.76, 0.02, flat(on ? lit : '#1c1d3c'), [s * w * 0.3, h * 0.55, 0.05]))); if (on) g.add(glow(2, 2, lit, 0.28, [s * w * 0.3, h * 0.55, 0.12])); } return g; }
export function tree({ h = 3.2, leaf = '#2f6b5a' } = {}) { const g = new THREE.Group(); g.add(cyl(0.12, 0.16, h * 0.5, toon('#5b4636'), [0, h * 0.25, 0])); const c = sameId(grp(sph(h * 0.26, toon(leaf), [0, h * 0.68, 0]), sph(h * 0.2, toon(leaf), [h * 0.16, h * 0.56, 0.1]), sph(h * 0.2, toon(leaf), [-h * 0.15, h * 0.58, -0.1]))); c.traverse(o => { o.userData.inkFlat = true; }); g.add(c); return g; }
export function sky({ top = '#0b1038', bottom = '#3a2a6e', stars = true, moon = true } = {}) { const tex = canvasTex(64, 512, (x) => { const gr = x.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, top); gr.addColorStop(1, bottom); x.fillStyle = gr; x.fillRect(0, 0, 64, 512); });
  const g = new THREE.Group(), m = noOutline(new THREE.Mesh(new THREE.SphereGeometry(60, 24, 16), new THREE.MeshBasicMaterial({ map: tex, side: THREE.BackSide }))); g.add(m);
  if (stars) { const r = rng(9); for (let i = 0; i < 70; i++) { const a = r() * Math.PI * 2, e = 0.15 + r() * 1.2; g.add(noOutline(sph(0.1 + r() * 0.12, flat('#dfe6ff'), [Math.cos(a) * Math.cos(e) * 55, Math.sin(e) * 55, Math.sin(a) * Math.cos(e) * 55]))); } }
  if (moon) { g.add(noOutline(sph(2.6, flat('#f4f1d8'), [-16, 30, -44]))); g.add(glow(18, 18, '#cfd8ff', 0.35, [-16, 30, -43])); } return g; }

// ---------------------------------------------------------------- ready-made sets
export const SETS = {
  // empty lit room, for checking characters and props
  studio(o = {}) { const g = shell(o.w ?? 14, o.d ?? 8, 3.2, { wall: '#d9dbe8', floor: '#b9bdd0' }); return makeSet(g, { mood: o.mood || 'day', pov: o.pov || [0, 1.2, 3.2], look: [0, 1, -2], targets: o.targets || {} }); },
  // Classroom in lockdown. opts: board/boardLines (chalkboard text), sign, poster [title, lines], doorX, lockers 'right'|'back'|false, rows, window 'left'|false, windowLit,
  // bags [[x, z, colour, tag]], mood, pov, hideDesks: [[x,z]...] extra desks. Targets: door, board, window, shelf, lockers, lap.
  classroom(o = {}) {
    const w = o.w ?? 10, d = o.d ?? 9, h = 3.1, g = shell(w, d, h, { wains: o.wains ?? '#cfc08e' }), dx = o.doorX ?? 0.4;
    const D = door(o.door); at(D.g, [dx, 0, -d / 2 + 0.03]); g.add(D.g);
    g.add(onWall(exitSign(o.sign || 'EXIT'), 'front', dx, 2.48, w, d)); g.add(onWall(clock(), 'front', dx + 1.25, 2.3, w, d)); g.add(onWall(speaker(), 'front', dx - 1.7, 2.35, w, d));
    g.add(onWall(chalkboard({ title: o.board || 'BIOLOGY FINAL', lines: o.boardLines || ['10:00 - 11:30', 'NO TALKING'] }), 'front', dx - 3.0, 1.55, w, d));
    const P = o.poster || ['LOCKDOWN', ['1 LOCK', '2 LIGHTS', '3 OUT OF', '   SIGHT']]; g.add(onWall(poster(P[0], P[1]), 'front', dx + 1.2, 1.5, w, d));
    g.add(onWall(bulletin(), 'right', -2.3, 1.6, w, d)); const bs = bookshelf(); onWall(bs, 'right', 0.6, 0, w, d); g.add(bs);
    if (o.lockers !== false) { const L = lockers(5); onWall(L, o.lockers === 'back' ? 'back' : 'right', o.lockers === 'back' ? 2.6 : 3.1, 0, w, d); g.add(L); }
    if (o.window !== false) for (const z of [-1.8, 1.2]) g.add(onWall(windowBlinds({ lit: o.windowLit || '#5f7fe8', strength: o.windowStrength ?? 0.55 }), 'left', z, 1.75, w, d));
    for (const [x, z] of [[-2.5, -1.5], [0, -1.5], [2.5, -1.5], [-2.5, 1.5], [0, 1.5], [2.5, 1.5]]) g.add(at(ceilingPanel(), [x, h, z]));
    // desks in rows, each with a chair behind it (toward the back wall)
    const rows = o.rows || [[-3.3, -2.5], [-1.7, -2.5], [2.9, -2.7], [-3.3, -0.8], [-1.7, -0.8], [-3.3, 0.9], [-1.7, 0.9], [3.3, -0.4], [3.5, 1.4], ...(o.hideDesks || [])];
    for (const [x, z, ry] of rows) { const dk = desk(); at(dk, [x, 0, z], [0, ry || 0, 0]); g.add(dk); const ch = chair(); at(ch, [x, 0, z + 0.55], [0, (ry || 0) + Math.PI, 0]); g.add(ch); }
    for (const [x, z, c, tag] of o.bags || []) g.add(at(backpack(c, tag), [x, 0, z], [0, 0.3, 0]));
    return makeSet(g, { mood: o.mood || 'lockdown', pov: o.pov || [1.5, 0.62, 2.0], look: 'door', spillAt: [dx, 0.3, -d / 2 + 0.9], pulseAt: [0, 2.6, -0.5], pulse: o.pulse, spill: o.spill,
      targets: { door: [dx, 1.15, -d / 2], doorGap: [dx, 0.2, -d / 2 + 0.3], board: [dx - 3, 1.5, -d / 2], shelf: [w / 2, 1, 0.6], window: [-w / 2, 1.7, 0], ...(o.targets || {}) }, parts: { door: D },
      onUpdate(v) { D.setFeet(v.feet ?? 0); D.leaf.rotation.y = -(v.door ?? 0) * 1.3; D.leaf.position.x = 0; const sp = v.spill ?? 1; D.strip.visible = sp > 0.05; D.pool.material.opacity = 0.42 * sp; } });
  },
  // Corridor. opts: sign, doors (number per side), lockers, mood, endDoor. Targets: end, door1..n
  hallway(o = {}) {
    const w = 3.6, d = o.d ?? 16, h = 3, g = shell(w, d, h, { wains: '#9fa9d8', wall: '#d3d6ec' }); const D = door(o.door); at(D.g, [0, 0, -d / 2 + 0.03]); g.add(D.g); g.add(onWall(exitSign(o.sign || 'EXIT'), 'front', 0, 2.48, w, d));
    for (let i = 0; i < 4; i++) { const z = -d / 2 + 2.2 + i * 3.4; const L = lockers(4); onWall(L, i % 2 ? 'left' : 'right', z, 0, w, d); g.add(L); const dd = door({ window: i % 2 === 0, lit: '#8fa0e8' }); dd.strip.visible = false; dd.pool.visible = false; dd.setFeet(0); onWall(dd.g, i % 2 ? 'right' : 'left', z, 0, w, d); g.add(dd.g); g.add(at(ceilingPanel(1.1, 0.4), [0, h, z])); }
    return makeSet(g, { mood: o.mood || 'lockdown', pov: o.pov || [0, 1.5, d / 2 - 2], look: 'end', spillAt: [0, 0.3, -d / 2 + 0.9], pulseAt: [0, 2.6, 0], targets: { end: [0, 1.2, -d / 2], door: [0, 1.15, -d / 2], ...(o.targets || {}) }, parts: { door: D },
      onUpdate(v) { D.setFeet(v.feet ?? 0); D.leaf.rotation.y = -(v.door ?? 0) * 1.3; } });
  },
  // Bedroom at night. Door on the front wall, bed on the left, wardrobe right, window on the left wall. Targets: door, bed, wardrobe, window, underBed
  bedroom(o = {}) {
    const w = 6, d = 6.4, h = 2.8, g = shell(w, d, h, { wall: o.wall || '#c9c2e6', floor: '#a995c8', tiles: false }); const dx = o.doorX ?? 1.2, D = door({ window: false, color: '#b9a48e', frame: '#8a6f58', ...(o.door || {}) }); at(D.g, [dx, 0, -d / 2 + 0.03]); g.add(D.g);
    g.add(at(bed(o.bed), [-1.9, 0, -1.9])); const wd = wardrobe(); onWall(wd, 'right', -0.4, 0, w, d); g.add(wd); g.add(onWall(windowBlinds({ lit: o.windowLit || '#7f9cff', strength: 0.7 }), 'left', 0.6, 1.6, w, d));
    const tb = table({ w: 0.6, d: 0.5, h: 0.55 }); at(tb, [-0.9, 0, -2.75]); g.add(tb); g.add(at(lamp({ on: o.lamp ?? false }), [-0.9, 0.58, -2.75])); g.add(noOutline(plane(2.2, 1.5, lam('#7f6fc0'), [0.4, 0.006, 0.4], [-Math.PI / 2, 0, 0]))); g.add(onWall(poster(o.posterTitle || 'STAY IN BED', o.posterLines || ['AFTER', 'MIDNIGHT']), 'front', -0.6, 1.7, w, d)); g.add(at(plant(), [2.5, 0, 2.6]));
    return makeSet(g, { mood: o.mood || 'night', pov: o.pov || [-1.7, 0.95, -0.9], look: 'door', spillAt: [dx, 0.3, -d / 2 + 0.9], pulseAt: [0, 2.4, 0], targets: { door: [dx, 1.1, -d / 2], doorGap: [dx, 0.2, -d / 2 + 0.3], wardrobe: [w / 2, 1.1, -0.4], window: [-w / 2, 1.6, 0.6], underBed: [-1.9, 0.1, -1.0], ...(o.targets || {}) }, parts: { door: D },
      onUpdate(v) { D.setFeet(v.feet ?? 0); D.leaf.rotation.y = -(v.door ?? 0) * 1.3; const sp = v.spill ?? 1; D.strip.visible = sp > 0.05; D.pool.material.opacity = 0.42 * sp; } });
  },
  // Living room: sofa facing a TV, front door on the front wall, window with blinds. Targets: door, tv, window, sofa
  livingRoom(o = {}) {
    const w = 7, d = 7, h = 2.8, g = shell(w, d, h, { wall: o.wall || '#d6cfe0', floor: '#b08a68', tiles: false }); const dx = -2.2, D = door({ window: false, color: '#7b5a48', frame: '#5b4030', ...(o.door || {}) }); at(D.g, [dx, 0, -d / 2 + 0.03]); g.add(D.g);
    g.add(at(tv({ on: o.tv || '#9fc4ff' }), [1.2, 0, -3.1])); g.add(at(sofa(o.sofa), [1.2, 0, 0.9], [0, Math.PI, 0])); g.add(at(table({ w: 1.1, d: 0.6, h: 0.42 }), [1.2, 0, -0.6])); g.add(onWall(windowBlinds({ lit: o.windowLit || '#7f9cff' }), 'right', 0.3, 1.6, w, d)); g.add(at(plant(), [-3, 0, 2.8])); g.add(at(lamp({ on: o.lamp ?? true }), [3.0, 0, 2.6], null, 2.2)); g.add(noOutline(plane(3, 2.2, lam('#8a6fb8'), [1.2, 0.006, 0], [-Math.PI / 2, 0, 0])));
    return makeSet(g, { mood: o.mood || 'warm', pov: o.pov || [1.2, 1.0, 0.7], look: 'tv', spillAt: [dx, 0.3, -d / 2 + 0.9], targets: { door: [dx, 1.1, -d / 2], tv: [1.2, 0.95, -3.1], window: [w / 2, 1.6, 0.3], ...(o.targets || {}) }, parts: { door: D },
      onUpdate(v) { D.setFeet(v.feet ?? 0); D.leaf.rotation.y = -(v.door ?? 0) * 1.3; const sp = v.spill ?? 0; D.strip.visible = sp > 0.05; D.pool.material.opacity = 0.42 * sp; } });
  },
  // Small shop: counter, shelves, glass front door. Targets: door, counter, shelf
  shop(o = {}) {
    const w = 8, d = 7, h = 3, g = shell(w, d, h, { wall: '#d9dcee', floor: '#c2c7e2' }); const D = door({ color: '#7fa0d8', frame: '#3a4a88', ...(o.door || {}) }); at(D.g, [0, 0, -d / 2 + 0.03]); g.add(D.g); g.add(onWall(exitSign(o.sign || 'OPEN', '#d8423c'), 'front', 0, 2.48, w, d));
    g.add(at(counter(), [2.4, 0, 1.6], [0, -Math.PI / 2, 0])); for (const z of [-1.6, 0.4]) { const s = shelfUnit({ seed: z + 5 }); onWall(s, 'left', z, 0, w, d); g.add(s); } const s2 = shelfUnit({ seed: 8 }); at(s2, [-0.6, 0, -0.4], [0, Math.PI / 2, 0]); g.add(s2);
    for (const [x, z] of [[-2, -1], [2, -1], [0, 1.5]]) g.add(at(ceilingPanel(), [x, h, z])); g.add(onWall(poster(o.posterTitle || 'RULES', o.posterLines || ['NO REFUNDS', 'NO EXITS']), 'front', 1.6, 1.6, w, d));
    return makeSet(g, { mood: o.mood || 'night', pov: o.pov || [1.2, 1.5, 2.4], look: 'door', spillAt: [0, 0.3, -d / 2 + 0.9], targets: { door: [0, 1.15, -d / 2], counter: [2.4, 1.1, 1.6], shelf: [-w / 2, 1.2, -0.6], ...(o.targets || {}) }, parts: { door: D },
      onUpdate(v) { D.setFeet(v.feet ?? 0); D.leaf.rotation.y = -(v.door ?? 0) * 1.3; } });
  },
  // Street at night: road toward the horizon, houses both sides, street lamps. Targets: far, houseL, houseR, lamp
  street(o = {}) {
    const g = new THREE.Group(); g.add(sky(o.sky)); g.add(plane(60, 80, lam('#3a3f6e'), [0, 0, -20], [-Math.PI / 2, 0, 0])); g.add(noOutline(plane(7, 80, lam('#2a2d52'), [0, 0.01, -20], [-Math.PI / 2, 0, 0])));
    for (let i = 0; i < 10; i++) g.add(noOutline(plane(0.18, 1.6, lam('#c9cfe8'), [0, 0.02, 6 - i * 5], [-Math.PI / 2, 0, 0])));
    const cols = ['#8f7fb8', '#7f9ac8', '#b88f9a', '#8fb89f', '#b8a67f']; for (let i = 0; i < 5; i++) for (const s of [-1, 1]) { const hs = house({ color: cols[(i + (s > 0 ? 2 : 0)) % 5], seed: i * 3 + s + 4 }); at(hs, [s * 7.2, 0, 2 - i * 7.5], [0, -s * Math.PI / 2, 0]); g.add(hs); if (i % 2 === 0) g.add(at(tree(), [s * 4.6, 0, -1.5 - i * 7.5])); }
    for (let i = 0; i < 4; i++) g.add(at(streetLamp(), [-4.1, 0, 3 - i * 11])); g.add(at(streetLamp(), [4.1, 0, -2.5], [0, Math.PI, 0]));
    return makeSet(g, { mood: o.mood || 'night', pov: o.pov || [0.8, 1.5, 6], look: 'far', spillAt: [-3.5, 3.6, 3], spill: 1.4, targets: { far: [0, 1.4, -30], houseL: [-7.2, 1.6, 2], houseR: [7.2, 1.6, 2], lamp: [-3.5, 3.9, 3], ...(o.targets || {}) } });
  },
};
