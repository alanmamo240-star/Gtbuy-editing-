// Sets and props for FLUCHT AUS ASCHENTAL (a fictional city in a war that is never named).
// Everything faces +z at rotation 0 unless noted. One unit = one metre.
import { THREE, toon, lam, flat, box, rbox, sph, cyl, plane, disc, torus, grp, at, noOutline, sameId, glow, canvasTex, rng, clamp, lerp, smooth, noise, rad, FONT } from './util.js';
import { makeSet } from './sets.js';
import { texRep } from './lib.js';

const OLIVE = '#56603f', OLIVE_D = '#3a4130', RUBBER = '#1c1d20';

// ---------------------------------------------------------------------------------------------- keyframed paths
// keys: [[t, x, y, z], ...] -> position at t (smooth between keys, held before the first and after the last)
export function pathPos(keys, t, out = [0, 0, 0]) {
  if (t <= keys[0][0]) { out[0] = keys[0][1]; out[1] = keys[0][2]; out[2] = keys[0][3]; return out; }
  for (let i = 1; i < keys.length; i++) {
    const a = keys[i - 1], b = keys[i];
    if (t <= b[0]) {                                     // Catmull-Rom through the keys, so turns are round
      const p0 = keys[i - 2] || a, p3 = keys[i + 1] || b, u = (t - a[0]) / Math.max(1e-6, b[0] - a[0]), u2 = u * u, u3 = u2 * u;
      for (let k = 1; k <= 3; k++) out[k - 1] = 0.5 * (2 * a[k] + (-p0[k] + b[k]) * u + (2 * p0[k] - 5 * a[k] + 4 * b[k] - p3[k]) * u2 + (-p0[k] + 3 * a[k] - 3 * b[k] + p3[k]) * u3);
      return out;
    }
  }
  const l = keys[keys.length - 1]; out[0] = l[1]; out[1] = l[2]; out[2] = l[3]; return out;
}
// 1-D keys [[t, v], ...] with eased segments
export function keyed(keys, t) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) { const a = keys[i - 1], b = keys[i]; if (t <= b[0]) return lerp(a[1], b[1], smooth((t - a[0]) / Math.max(1e-6, b[0] - a[0]))); }
  return keys[keys.length - 1][1];
}

// ---------------------------------------------------------------------------------------------- facades
const SHOPS = ['BÄCKEREI', 'APOTHEKE', 'KIOSK', 'FRISEUR', 'ELEKTRO', 'WÄSCHEREI', 'CAFÉ', 'BLUMEN', 'METZGEREI', 'BÜCHER', 'OPTIK', 'SCHUHE'];
const SHOPC = ['#c8443a', '#2f7a4a', '#2f5fb8', '#8a4a9a', '#d08a2a', '#3a8a8a'];
// a whole facade drawn on one canvas: windows per floor, a shop or a door on the ground floor, soot over burnt windows
function facadeTex(w, h, o = {}) {
  const PX = 24, cw = Math.max(32, Math.round(w * PX)), ch = Math.max(32, Math.round(h * PX)), r = rng(o.seed ?? 1);
  return canvasTex(cw, ch, x => {
    x.fillStyle = o.color || '#c8b8a0'; x.fillRect(0, 0, cw, ch);
    for (let i = 0; i < 260; i++) { x.fillStyle = `rgba(40,30,30,${0.02 + r() * 0.04})`; x.fillRect(r() * cw, r() * ch, 2 + r() * 8, 2 + r() * 8); }
    const floorH = 3.1 * PX, nF = Math.floor((h - 0.4) / 3.1), bays = Math.max(1, Math.round(w / 2.3)), bw = cw / bays;
    x.fillStyle = 'rgba(0,0,0,0.12)'; for (let f = 1; f <= nF; f++) x.fillRect(0, ch - f * floorH - 4, cw, 4);
    for (let f = 1; f < nF; f++) for (let b = 0; b < bays; b++) {
      const wx = b * bw + bw * 0.27, wy = ch - (f + 1) * floorH + floorH * 0.22, ww = bw * 0.46, wh = floorH * 0.56, roll = r();
      x.fillStyle = 'rgba(255,255,255,0.55)'; x.fillRect(wx - 3, wy - 3, ww + 6, wh + 6);
      const burnt = roll < (o.burnt ?? 0.06), lit = !burnt && roll > 1 - (o.lit ?? 0);
      x.fillStyle = burnt ? '#120e0e' : lit ? '#f2c27a' : (roll < 0.5 ? '#2c3444' : '#3a4558'); x.fillRect(wx, wy, ww, wh);
      if (!burnt && !lit) { x.fillStyle = 'rgba(255,255,255,0.12)'; x.fillRect(wx + ww * 0.1, wy + wh * 0.1, ww * 0.2, wh * 0.7); }
      x.fillStyle = 'rgba(0,0,0,0.35)'; x.fillRect(wx + ww / 2 - 1, wy, 2, wh); x.fillRect(wx, wy + wh * 0.35, ww, 2);
      if (burnt) { const g = x.createLinearGradient(0, wy - floorH * 0.9, 0, wy); g.addColorStop(0, 'rgba(10,8,8,0)'); g.addColorStop(1, 'rgba(10,8,8,0.75)'); x.fillStyle = g; x.fillRect(wx - ww * 0.2, wy - floorH * 0.9, ww * 1.4, floorH * 0.9); }
      if (r() < 0.25 && !burnt) { x.fillStyle = 'rgba(30,30,40,0.6)'; x.fillRect(wx - 6, wy + wh + 2, ww + 12, 6); }       // balcony rail
    }
    // ground floor
    const gy = ch - floorH;
    if (o.shop !== false) {
      const k = Math.floor(r() * SHOPS.length), c = SHOPC[Math.floor(r() * SHOPC.length)], sw = Math.min(cw - 16, 10 * PX);
      x.fillStyle = c; x.fillRect(8, gy + 6, sw, floorH * 0.18); x.fillStyle = '#fff'; x.font = `800 ${Math.round(floorH * 0.13)}px ${FONT}`; x.textBaseline = 'middle'; x.fillText(o.label || SHOPS[k], 16, gy + 6 + floorH * 0.09);
      x.fillStyle = '#8a8c90'; x.fillRect(8, gy + floorH * 0.28, sw, floorH * 0.72); x.fillStyle = 'rgba(0,0,0,0.25)'; for (let yy = gy + floorH * 0.3; yy < ch; yy += 6) x.fillRect(8, yy, sw, 2);   // rolled-down shutter
      if (r() < 0.5) { x.strokeStyle = ['#2a6ad8', '#d8402a', '#2aa860'][Math.floor(r() * 3)]; x.lineWidth = 5; x.beginPath(); const sx = 20 + r() * sw * 0.5, sy = gy + floorH * 0.6; x.moveTo(sx, sy); for (let i = 0; i < 6; i++) x.lineTo(sx + i * 14, sy + (i % 2 ? -12 : 10)); x.stroke(); }   // graffiti scrawl
    }
    x.fillStyle = '#4a3a32'; x.fillRect(cw - 2.2 * PX, gy + floorH * 0.25, 1.2 * PX, floorH * 0.75);   // house door
    x.fillStyle = 'rgba(0,0,0,0.3)'; x.fillRect(0, 0, cw, 6); x.fillRect(0, ch - 6, cw, 6);
  });
}
// a building block: body box + painted facade on the street side. side: +1 = facade faces +x, -1 = faces -x, 2 = faces +z, -2 = faces -z
export function building(g, { x, z, w, h, d = 9, side, color, seed, burnt, lit, shop, label }) {
  const along = Math.abs(side) === 1 ? [d, h, w] : [w, h, d], cx = Math.abs(side) === 1 ? x - Math.sign(side) * d / 2 : x, cz = Math.abs(side) === 2 ? z - Math.sign(side) * d / 2 : z;
  g.add(box(along[0], h, along[2], lam(new THREE.Color(color).multiplyScalar(0.82).getHex()), [cx, h / 2, cz]));
  const tex = facadeTex(w, h, { color, seed, burnt, lit, shop, label }), f = plane(w, h, new THREE.MeshLambertMaterial({ map: tex }), [0, h / 2, 0]);
  f.userData.noOutline = true;
  if (Math.abs(side) === 1) { f.rotation.y = side > 0 ? Math.PI / 2 : -Math.PI / 2; f.position.set(x + 0.02 * Math.sign(side), h / 2, z); }
  else { f.rotation.y = side > 0 ? 0 : Math.PI; f.position.set(x, h / 2, z + 0.02 * Math.sign(side)); }
  g.add(f);
  const roofM = lam('#5a5050'); g.add(box(along[0] + 0.3, 0.35, along[2] + 0.3, roofM, [cx, h + 0.17, cz]));
  return f;
}

// ---------------------------------------------------------------------------------------------- smoke, fire, debris
export function plume(x, y, z, h, r0, seed = 1, wind = [0.25, 0]) {
  const g = new THREE.Group(), r = rng(seed), balls = [], n = Math.max(6, Math.round(h / (r0 * 0.9)));
  for (let i = 0; i < n; i++) {
    const k = i / (n - 1), rr = r0 * (0.55 + 1.1 * k) * (0.85 + 0.3 * r()), c = ['#2c2a2e', '#3a383c', '#47454a', '#57555a'][Math.floor(r() * 4)];
    const b = sph(1, lam(c), [wind[0] * h * k * k + (r() - 0.5) * r0 * 0.8, k * h, wind[1] * h * k * k + (r() - 0.5) * r0 * 0.6]); b.scale.setScalar(rr);
    b.userData.base = [b.position.x, b.position.y, b.position.z, rr, r() * 10]; g.add(b); balls.push(b);
    if (r() < 0.7) { const b2 = sph(1, lam(c), [b.position.x + (r() - 0.5) * rr * 1.4, b.position.y + (r() - 0.3) * rr * 0.8, b.position.z + (r() - 0.5) * rr]); b2.scale.setScalar(rr * (0.55 + 0.3 * r())); b2.userData.base = [b2.position.x, b2.position.y, b2.position.z, b2.scale.x, r() * 10]; g.add(b2); balls.push(b2); }
  }
  g.position.set(x, y, z);
  g.userData.update = t => { for (const b of balls) { const [bx, by, bz, s, ph] = b.userData.base; b.position.set(bx + 0.35 * noise(t * 0.25, ph), by + 0.25 * noise(t * 0.2, ph + 3), bz); b.scale.setScalar(s * (1 + 0.06 * Math.sin(t * 0.7 + ph))); } };
  return g;
}
export function fire(s = 1) {
  const g = new THREE.Group(), cones = [];
  for (const [dx, h, c] of [[0, 1.3, '#ff7a1a'], [-0.28, 0.9, '#ff9a2a'], [0.3, 1.0, '#ff8a20'], [0, 0.7, '#ffd34a']]) { const k = noOutline(new THREE.Mesh(new THREE.ConeGeometry(0.28, 1, 10), flat(c))); k.position.set(dx * s, h * s / 2, (c === '#ffd34a' ? 0.08 : 0) * s); k.scale.set(s, h * s, s); g.add(k); cones.push([k, h]); }
  const gl = glow(3.2 * s, 3.2 * s, '#ff8a3a', 0.8, [0, 0.7 * s, 0.05]); g.add(gl);
  g.userData.update = (t, seed = 0) => { cones.forEach(([k, h], i) => { k.scale.y = h * s * (0.75 + 0.35 * (0.5 + 0.5 * noise(t * 7 + i * 3.1, seed))); k.position.y = k.scale.y / 2; }); gl.material.opacity = 0.6 + 0.25 * noise(t * 5, seed + 9); };
  return g;
}
export function rubble(x, z, w, seed = 2) { const g = new THREE.Group(), r = rng(seed); for (let i = 0; i < 14; i++) { const s = 0.2 + r() * 0.5; g.add(box(s * 1.4, s, s, lam(['#8a8480', '#6a6460', '#9a9088'][i % 3]), [x + (r() - 0.5) * w, s / 2, z + (r() - 0.5) * w * 0.6], [r(), r() * 3, r()])); } return g; }

// ---------------------------------------------------------------------------------------------- street furniture
export function tree(x, z, s = 1, seed = 1) {
  const r = rng(seed), g = new THREE.Group(); g.add(cyl(0.12 * s, 0.18 * s, 3.2 * s, toon('#5a4030'), [0, 1.6 * s, 0]));
  for (let i = 0; i < 5; i++) g.add(sph((0.9 + r() * 0.5) * s, toon(['#4f7a3a', '#5a8a42', '#46703a'][i % 3]), [(r() - 0.5) * 1.4 * s, (3.4 + r() * 1.3) * s, (r() - 0.5) * 1.4 * s]));
  g.add(box(1.1 * s, 0.05, 1.1 * s, lam('#4a3a2a'), [0, 0.17, 0])); g.position.set(x, 0, z); return sameId(g);
}
export function lamp(x, z, ry = 0) { const g = grp(cyl(0.07, 0.09, 5.2, toon('#2a2d34'), [0, 2.6, 0]), box(0.08, 0.08, 1.0, toon('#2a2d34'), [0, 5.15, 0.45]), box(0.36, 0.12, 0.5, toon('#3a3d44'), [0, 5.1, 0.95])); g.position.set(x, 0, z); g.rotation.y = ry; return g; }
export function car(color = '#3a6aa8', burnt = false) {
  const g = new THREE.Group(), body = toon(burnt ? '#2a2624' : color), glass = flat(burnt ? '#0a0a0a' : '#2a3444');
  g.add(rbox(1.8, 0.7, 4.2, 0.18, body, [0, 0.62, 0])); g.add(rbox(1.6, 0.62, 2.2, 0.2, body, [0, 1.22, -0.2]));
  for (const s of [-1, 1]) g.add(noOutline(box(0.02, 0.42, 1.8, glass, [s * 0.81, 1.25, -0.2])));
  g.add(noOutline(box(1.4, 0.45, 0.02, glass, [0, 1.25, 0.92]))); g.add(noOutline(box(1.4, 0.45, 0.02, glass, [0, 1.25, -1.32])));
  for (const zz of [1.35, -1.35]) for (const s of [-1, 1]) g.add(cyl(0.34, 0.34, 0.26, toon(burnt ? '#141414' : RUBBER), [s * 0.82, 0.34, zz], [0, 0, Math.PI / 2]));
  if (!burnt) { g.add(noOutline(box(1.2, 0.12, 0.03, flat('#f0f0e0'), [0, 0.7, 2.11]))); g.add(noOutline(box(1.3, 0.1, 0.03, flat('#c83030'), [0, 0.75, -2.11]))); }
  else for (let i = 0; i < 5; i++) g.add(noOutline(box(0.3, 0.02, 0.3, flat('#5a3a24'), [(i % 2 - 0.5) * 0.9, 1.54, -0.8 + i * 0.35])));
  return sameId(g);
}
export function sandbags(n = 6) { const g = new THREE.Group(); for (let i = 0; i < n; i++) for (let row = 0; row < 2; row++) g.add(rbox(0.62, 0.24, 0.36, 0.1, toon(row ? '#a8987a' : '#9a8a6a'), [i * 0.58 - n * 0.29 + (row ? 0.28 : 0), 0.13 + row * 0.23, 0])); return g; }
export function barrier(w = 3) { const g = new THREE.Group(), stripes = canvasTex(128, 16, x => { for (let i = 0; i < 8; i++) { x.fillStyle = i % 2 ? '#d83a2a' : '#f2f2ee'; x.fillRect(i * 16, 0, 16, 16); } }); g.add(box(w, 0.22, 0.12, new THREE.MeshLambertMaterial({ map: stripes }), [0, 1.0, 0])); for (const s of [-1, 1]) g.add(box(0.12, 1.0, 0.5, toon('#2a2d34'), [s * (w / 2 - 0.15), 0.5, 0])); return g; }
// a suitcase / bag hanging from a hand (add it to av.handR)
export function suitcase(color = '#6a4a3a', kind = 'case') {
  const g = new THREE.Group();
  if (kind === 'bag') { g.add(rbox(0.42, 0.26, 0.2, 0.08, toon(color), [0, -0.2, 0])); g.add(torus(0.08, 0.012, toon('#2a2020'), [0, -0.05, 0])); }
  else { g.add(rbox(0.5, 0.36, 0.16, 0.04, toon(color), [0, -0.27, 0])); g.add(box(0.14, 0.03, 0.03, toon('#1a1a1a'), [0, -0.075, 0])); g.add(noOutline(box(0.5, 0.03, 0.162, flat('#2a2020'), [0, -0.2, 0]))); }
  return sameId(g);
}
export function flashlight() { const g = grp(cyl(0.025, 0.03, 0.2, toon('#1a1a1e'), [0, -0.03, 0.06], [Math.PI / 2, 0, 0]), noOutline(disc(0.024, flat('#fffbe0'), [0, -0.03, 0.161]))); const beam = noOutline(new THREE.Mesh(new THREE.ConeGeometry(0.5, 3.2, 20, 1, true), new THREE.MeshBasicMaterial({ color: '#fff4c8', transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }))); beam.rotation.x = -Math.PI / 2; beam.position.set(0, -0.03, 1.75); g.add(beam); g.userData.beam = beam; return g; }

// ---------------------------------------------------------------------------------------------- vehicles (face +z)
export function tank(c = OLIVE) {
  const g = new THREE.Group(), m = toon(c), d = toon(OLIVE_D), wheels = [];
  g.add(rbox(3.0, 0.9, 6.6, 0.12, m, [0, 1.05, 0])); g.add(at(box(2.9, 0.5, 1.2, m), [0, 1.2, 3.35], [0.5, 0, 0]));
  for (const s of [-1, 1]) { g.add(rbox(0.75, 0.95, 7.0, 0.3, toon(RUBBER), [s * 1.55, 0.55, 0])); for (let i = 0; i < 6; i++) { const w = cyl(0.36, 0.36, 0.12, d, [s * 1.95, 0.48, -2.6 + i * 1.04], [0, 0, Math.PI / 2]); g.add(w); wheels.push(w); } }
  const tur = new THREE.Group(); tur.position.set(0, 1.5, -0.4); tur.add(rbox(2.3, 0.75, 2.9, 0.25, m, [0, 0.37, 0])); tur.add(cyl(0.11, 0.13, 4.2, d, [0, 0.42, 3.4], [Math.PI / 2, 0, 0])); tur.add(cyl(0.3, 0.3, 0.12, d, [0.5, 0.8, -0.4])); tur.add(cyl(0.015, 0.015, 2.2, d, [-0.8, 1.8, -1.0])); g.add(tur);
  return { g: sameId(g), wheels, turret: tur, r: 0.36 };
}
export function apc(c = OLIVE) {
  const g = new THREE.Group(), m = toon(c), d = toon(OLIVE_D), wheels = [];
  g.add(rbox(2.7, 1.35, 6.0, 0.15, m, [0, 1.35, 0])); g.add(at(box(2.6, 0.9, 1.4, m), [0, 1.35, 3.25], [0.75, 0, 0]));
  for (const s of [-1, 1]) for (let i = 0; i < 4; i++) { const w = cyl(0.55, 0.55, 0.42, toon(RUBBER), [s * 1.32, 0.55, -2.2 + i * 1.45], [0, 0, Math.PI / 2]); g.add(w); wheels.push(w); g.add(cyl(0.22, 0.22, 0.44, d, [s * 1.33, 0.55, -2.2 + i * 1.45], [0, 0, Math.PI / 2])); }
  const tur = new THREE.Group(); tur.position.set(0, 2.05, 0.2); tur.add(rbox(1.1, 0.45, 1.3, 0.15, m, [0, 0.22, 0])); tur.add(cyl(0.05, 0.05, 1.2, d, [0, 0.25, 1.1], [Math.PI / 2, 0, 0])); g.add(tur);
  for (const s of [-1, 1]) g.add(noOutline(box(0.5, 0.18, 0.02, flat('#1a1e18'), [s * 0.7, 1.75, 3.0])));
  return { g: sameId(g), wheels, turret: tur, r: 0.55 };
}
export function truck(c = OLIVE) {
  const g = new THREE.Group(), m = toon(c), d = toon(OLIVE_D), wheels = [];
  g.add(rbox(2.4, 1.6, 1.9, 0.15, m, [0, 1.65, 2.5])); g.add(rbox(2.3, 0.9, 1.2, 0.1, m, [0, 1.1, 3.9])); g.add(noOutline(box(2.0, 0.6, 0.02, flat('#1c2228'), [0, 2.0, 3.46])));
  g.add(box(2.5, 0.3, 4.6, d, [0, 1.05, -0.9]));
  const canvas = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.25, 4.6, 20, 1, false, -Math.PI / 2, Math.PI), toon('#6a6a4a')); canvas.rotation.x = Math.PI / 2; canvas.position.set(0, 1.55, -0.9); canvas.scale.set(1, 1, 1.15); g.add(canvas);
  g.add(box(2.5, 0.5, 4.6, toon('#6a6a4a'), [0, 1.45, -0.9]));
  for (const zz of [3.3, -0.2, -1.9]) for (const s of [-1, 1]) { const w = cyl(0.5, 0.5, 0.36, toon(RUBBER), [s * 1.1, 0.5, zz], [0, 0, Math.PI / 2]); g.add(w); wheels.push(w); }
  return { g: sameId(g), wheels, r: 0.5 };
}
const VEH = { tank, apc, truck };
// a column of vehicles. spec: { kind, x, y, keys: [[t, z], ...], ry, color } (z along the road; ry 0 = driving +z, 180 = driving -z)
export function convoy(g, specs) {
  const list = specs.map(s => { const v = VEH[s.kind](s.color); v.g.rotation.y = rad(s.ry ?? 180); g.add(v.g); return { ...s, v }; });
  return (t) => { for (const c of list) { const z = keyed(c.keys, t), zx = c.axis === 'x'; if (zx) c.v.g.position.set(z, c.y ?? 0, c.x); else c.v.g.position.set(c.x, c.y ?? 0, z); const dist = z;
      for (const w of c.v.wheels) w.rotation.x = dist / c.v.r; c.v.g.position.y = (c.y ?? 0) + 0.02 * Math.sin(t * 13 + c.x); } };
}

// ---------------------------------------------------------------------------------------------- helicopter
export function heli(c = '#4a5438') {
  const g = new THREE.Group(), body = new THREE.Group(), m = toon(c), d = toon('#262a22');
  body.add(rbox(1.4, 1.4, 3.2, 0.45, m, [0, 0, 0.2])); body.add(noOutline(rbox(1.25, 0.75, 1.1, 0.3, flat('#1a2028'), [0, 0.18, 1.45])));
  body.add(cyl(0.24, 0.12, 3.8, m, [0, 0.25, -3.0], [Math.PI / 2, 0, 0])); body.add(box(0.08, 1.0, 0.7, m, [0, 0.72, -4.75])); body.add(box(1.4, 0.06, 0.4, m, [0, 0.3, -4.4]));
  for (const s of [-1, 1]) { body.add(box(0.07, 0.07, 2.8, d, [s * 0.7, -0.95, 0.2])); for (const zz of [-0.5, 0.9]) body.add(box(0.05, 0.4, 0.05, d, [s * 0.62, -0.75, zz])); }
  body.add(cyl(0.09, 0.09, 0.45, d, [0, 0.9, 0.2]));
  const rotor = new THREE.Group(); rotor.position.set(0, 1.12, 0.2); for (const a of [0, Math.PI / 2]) rotor.add(box(9.6, 0.04, 0.26, d, [0, 0, 0], [0, a, 0]));
  const blur = noOutline(new THREE.Mesh(new THREE.CircleGeometry(4.8, 40), new THREE.MeshBasicMaterial({ color: '#2a2e30', transparent: true, opacity: 0.16, depthWrite: false, side: THREE.DoubleSide }))); blur.rotation.x = -Math.PI / 2; blur.position.set(0, 1.12, 0.2);
  const trotor = new THREE.Group(); trotor.position.set(0.1, 0.75, -4.75); trotor.add(box(0.03, 1.3, 0.12, d)); trotor.add(box(0.03, 0.12, 1.3, d));
  body.add(rotor, blur, trotor); g.add(body);
  // searchlight under the nose: a soft visible cone and a real spot
  const beam = noOutline(new THREE.Mesh(new THREE.ConeGeometry(2.6, 22, 24, 1, true), new THREE.MeshBasicMaterial({ color: '#fff6d8', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide })));
  beam.geometry.translate(0, -11, 0); const beamG = new THREE.Group(); beamG.position.set(0, -0.6, 1.2); beamG.add(beam); body.add(beamG);
  const spot = new THREE.SpotLight('#fff4d8', 0, 60, rad(12), 1.0, 1.2); spot.position.set(0, -0.6, 1.2); const tgt = new THREE.Object3D(); tgt.position.set(0, -20, 4); body.add(spot, tgt); spot.target = tgt;
  return { g, body, rotor, trotor, beam, beamG, spot, tgt };
}
// keys [[t, x, y, z], ...]; light: 0..1 searchlight; aim: [pitch°] of the beam (0 = straight down)
export function flyHeli(H, keys, t, o = {}) {
  const p = pathPos(keys, t), q = pathPos(keys, t + 0.25); const vx = q[0] - p[0], vz = q[2] - p[2], sp = Math.hypot(vx, vz) / 0.25;
  H.g.position.set(p[0], p[1] + 0.15 * Math.sin(t * 1.3), p[2]);
  if (sp > 0.3) H.g.rotation.y = Math.atan2(vx, vz); else if (o.ry != null) H.g.rotation.y = rad(o.ry);
  H.body.rotation.x = clamp(sp / 22, 0, 0.32) + 0.02 * Math.sin(t * 0.9); H.body.rotation.z = 0.03 * Math.sin(t * 0.7);
  H.rotor.rotation.y = t * 29; H.trotor.rotation.x = t * 45;
  const L = o.light ?? 0; H.beam.material.opacity = 0.11 * L; H.spot.intensity = 160 * L; H.beamG.rotation.x = rad(o.aim ?? 20); H.tgt.position.set(0, -20, 20 * Math.tan(rad(o.aim ?? 20)) + 1.2);
}

// ---------------------------------------------------------------------------------------------- the main street (episode 1)
// Road along z (x -3.5..3.5), pavements to x ±7, facades at x = ±7. A side street opens on the +x side at z -15..-22.
// o.helis: [{ keys, light, aim }], o.convoy: convoy specs, o.fires: [[x, y, z, s]], o.plumes: [[x, y, z, h, r]]
export function street(o = {}) {
  const g = new THREE.Group();
  const asph = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); const r = rng(3); for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(20,20,30,${0.04 + r() * 0.1})`; x.fillRect(r() * 256, r() * 256, 3, 3); } x.fillStyle = 'rgba(255,255,255,0.75)'; x.fillRect(122, 0, 12, 110); }), 1, 14);
  g.add(plane(7, 120, new THREE.MeshLambertMaterial({ color: '#5c5a5e', map: asph }), [0, 0, -40], [-Math.PI / 2, 0, 0]));
  const paveT = texRep(canvasTex(128, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); x.strokeStyle = 'rgba(40,40,50,0.22)'; x.lineWidth = 3; x.strokeRect(0, 0, 128, 128); x.beginPath(); x.moveTo(64, 0); x.lineTo(64, 128); x.stroke(); }), 3, 60);
  for (const s of [-1, 1]) { g.add(box(3.5, 0.15, 120, new THREE.MeshLambertMaterial({ color: '#b4b0aa', map: paveT }), [s * 5.25, 0.075, -40])); g.add(box(0.2, 0.17, 120, lam('#9a968e'), [s * 3.55, 0.085, -40])); }
  // side street to +x
  g.add(plane(40, 7, new THREE.MeshLambertMaterial({ color: '#5c5a5e', map: asph.clone() }), [27, 0.005, -18.5], [-Math.PI / 2, 0, 0]));
  for (const zz of [-14.25, -22.75]) g.add(box(40, 0.15, 1.5, lam('#b4b0aa'), [27, 0.075, zz]));
  // facades
  const r = rng(7), COL = ['#d8c4a8', '#c8a890', '#b8a8b8', '#a8b4a0', '#d0b0a0', '#a8a49c', '#c4b49a', '#b89488'];
  let i = 0;
  const row = (x, side, z0, z1) => { let z = z0; while (z > z1 + 0.5) { const w = Math.min(z - z1, 7 + Math.floor(r() * 6)); building(g, { x, z: z - w / 2, w, h: 11 + Math.floor(r() * 7), side, color: COL[(i * 3 + (side > 0 ? 0 : 1)) % COL.length], seed: 30 + i, burnt: 0.08 + (i % 4 === 1 ? 0.22 : 0) }); z -= w; i++; } };
  row(-7, 1, 14, -84); row(7, -1, 14, -14); row(7, -1, -23, -84);
  for (let k = 0; k < 4; k++) { building(g, { x: 9 + k * 9 + 4, z: -14.0, w: 8.6, h: 12 + (k % 2) * 3, side: -2, color: COL[(k + 2) % COL.length], seed: 90 + k, d: 8 }); building(g, { x: 9 + k * 9 + 4, z: -23.0, w: 8.6, h: 11 + (k % 3) * 2, side: 2, color: COL[(k + 5) % COL.length], seed: 95 + k, d: 8 }); }
  building(g, { x: 45, z: -18.5, w: 9.2, h: 16, side: -1, color: '#b8a898', seed: 99, d: 6, label: 'APOTHEKE' });
  // far end: a dark skyline and the haze
  const sky = canvasTex(512, 128, x => { x.fillStyle = 'rgba(0,0,0,0)'; x.fillRect(0, 0, 512, 128); x.fillStyle = '#6a646a'; const rr = rng(4); let xx = 0; while (xx < 512) { const w = 20 + rr() * 50, h = 30 + rr() * 80; x.fillRect(xx, 128 - h, w, h); xx += w + 2; } });
  g.add(noOutline(plane(160, 40, new THREE.MeshBasicMaterial({ map: sky, transparent: true, color: '#9a9496' }), [0, 18, -110])));
  // trees, lamps, cars, debris
  for (const zz of [8, -6, -30, -42, -54, -66]) { g.add(tree(-5.4, zz, 1, Math.abs(zz) + 1)); g.add(tree(5.4, zz + 4, 0.95, Math.abs(zz) + 9)); }
  for (const zz of [2, -26, -50]) { g.add(lamp(-3.9, zz, 0)); g.add(lamp(3.9, zz - 12, Math.PI)); }
  const cars = [[-2.6, 5, 0, '#c8443a'], [-2.6, -10, 0, '#e8e2d0'], [2.6, -32, Math.PI, '#3a6aa8'], [-2.6, -38, 0, '#4a8a5a', true], [2.6, 10, Math.PI, '#d8b84a'], [2.6, -58, Math.PI, '#8a8a92']];
  for (const [x, zz, ry, c, b] of cars) g.add(at(car(c, b), [x, 0, zz], [0, ry, 0]));
  const wreck = at(car('#4a4a50', true), [9.8, 0, -16.2], [0, rad(-70), rad(4)]); g.add(wreck);            // burnt car at the side-street corner
  g.add(rubble(-6.0, -24, 3, 5)); g.add(rubble(6.2, -46, 3, 8)); g.add(rubble(14, -21.5, 3, 11));
  for (const [x, zz, ry, c] of [[-4.6, -3, 0.4, '#6a4a3a'], [4.8, -18, 1.2, '#3a4a6a'], [-1.0, -21, 2.2, '#8a3a3a']]) g.add(at(suitcase(c), [x, 0.35, zz], [rad(90), ry, 0]));
  const papers = canvasTex(64, 64, x => { x.fillStyle = '#f0ece0'; x.fillRect(0, 0, 64, 64); x.fillStyle = '#888'; for (let k = 0; k < 6; k++) x.fillRect(8, 8 + k * 8, 40, 3); });
  const pr = rng(12); for (let k = 0; k < 14; k++) g.add(noOutline(plane(0.28, 0.36, new THREE.MeshLambertMaterial({ map: papers, side: THREE.DoubleSide }), [(pr() - 0.5) * 9, 0.17 + 0.01 * k, 4 - pr() * 40], [-Math.PI / 2, 0, pr() * 6])));
  // a checkpoint far down the street
  g.add(at(barrier(5), [0, 0, -70])); g.add(at(sandbags(6), [-5, 0, -69])); g.add(at(sandbags(6), [5, 0, -69]));
  // smoke and fire
  const plumes = (o.plumes || [[-14, 10, -30, 34, 3.0], [16, 12, -52, 40, 3.6], [-12, 14, -64, 30, 2.6], [22, 10, -8, 26, 2.4], [-26, 8, -10, 30, 3.0], [4, 14, -92, 44, 4.4]]).map(([x, y, zz, h, rr], k) => { const p = plume(x, y, zz, h, rr, 40 + k); g.add(p); return p; });
  const fires = (o.fires || [[-6.9, 6.4, -27.5, 1.3], [6.9, 9.6, -48.5, 1.5], [-6.9, 0.2, -61, 1.8], [14, 0.2, -21.6, 1.0]]).map(([x, y, zz, s], k) => { const f = fire(s); f.position.set(x, y, zz); f.rotation.y = x < 0 ? Math.PI / 2 : -Math.PI / 2; g.add(f); return f; });
  const fl = fires.map(f => { const l = new THREE.PointLight('#ff8a3a', 0, 9, 1.6); l.position.copy(f.position).add(new THREE.Vector3(Math.sign(-f.position.x) * 1.2, 1.0, 0)); g.add(l); return l; });
  // helicopters and the convoy
  const helis = (o.helis || []).map(h => { const H = heli(); g.add(H.g); return { ...h, H }; });
  const runConvoy = convoy(g, o.convoy || []);
  const set = makeSet(g, {
    mood: 'day', moodOverride: { bg: o.bg || '#a29a94', amb: ['#d8ccc4', 1.15], hemi: ['#e8dcd4', '#5a5048', 0.75], key: ['#ffe2c0', 0.75, [-6, 9, 4]] },
    pov: o.pov || [-4.6, 1.55, 2.0], look: o.look || [0, 1.4, -20], targets: { street: [0, 1.4, -30], sideStreet: [14, 1.4, -18.5], wreck: [9.8, 1.1, -16.2], far: [0, 2.0, -70], sky: [0, 14, -30], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      plumes.forEach(p => p.userData.update(t)); fires.forEach((f, k) => f.userData.update(t, k * 7)); fl.forEach((l, k) => { l.intensity = 2.2 * (0.8 + 0.2 * noise(t * 6, k)); });
      helis.forEach(h => flyHeli(h.H, h.keys, t, { light: typeof h.light === 'function' ? h.light(t) : h.light, aim: h.aim, ry: h.ry }));
      runConvoy(t); o.onUpdate?.(v, t, S);
    },
  });
  set.scene.fog = new THREE.Fog(o.bg || '#a29a94', 18, 105); set.parts = { helis, fires };
  return set;
}

// ---------------------------------------------------------------------------------------------- the courtyard (episode 2, dusk)
// Courtyard x -8..8, z -7..7. The archway from the street in the +z wall (x -1.5..1.5), the stairwell door of house B in the
// -z wall at x 3. Bins, bikes, a washing line, a tree. o.helis as in street().
export function courtyard(o = {}) {
  const g = new THREE.Group(), r = rng(21);
  const cob = texRep(canvasTex(128, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); x.strokeStyle = 'rgba(30,30,40,0.25)'; x.lineWidth = 2; for (let i = 0; i < 8; i++) for (let j = 0; j < 8; j++) x.strokeRect(i * 16 + (j % 2) * 8, j * 16, 16, 16); }), 10, 10);
  g.add(plane(16, 14, new THREE.MeshLambertMaterial({ color: '#7a7672', map: cob }), [0, 0, 0], [-Math.PI / 2, 0, 0]));
  const C = ['#b8a890', '#a89888', '#9a9aa4', '#b0a088'];
  building(g, { x: 0, z: -7, w: 16, h: 13, side: 2, color: C[0], seed: 201, shop: false, lit: 0.12, d: 8 });
  building(g, { x: -8, z: 0, w: 14, h: 14, side: 1, color: C[1], seed: 202, shop: false, lit: 0.1, d: 8 });
  building(g, { x: 8, z: 0, w: 14, h: 12, side: -1, color: C[2], seed: 203, shop: false, lit: 0.1, d: 8 });
  for (const [x0, w] of [[-5, 6], [5, 6]]) building(g, { x: x0, z: 7, w, h: 13, side: -2, color: C[3], seed: 204 + x0, shop: false, lit: 0.12, d: 8 });
  g.add(box(3, 13 - 3.2, 8, lam('#8a7e70'), [0, 3.2 + (13 - 3.2) / 2, 11])); g.add(box(3, 3.2, 0.1, flat('#1a1820'), [0, 1.6, 15]));     // the archway
  for (const s of [-1, 1]) g.add(box(0.1, 3.2, 8, lam('#6a6058'), [s * 1.5, 1.6, 11]));
  // house B stairwell door (opens inward to -z, hinge on +x)
  g.add(box(1.4, 2.5, 0.1, toon('#3a3430'), [3, 1.25, -6.96])); const door = new THREE.Group(); door.position.set(3.6, 0, -6.9); door.add(box(1.15, 2.25, 0.07, toon('#5a4a3e'), [-0.575, 1.125, 0])); door.add(box(0.05, 0.14, 0.06, toon('#c8c0a8'), [-1.0, 1.05, 0.04])); g.add(door);
  g.add(noOutline(box(1.1, 2.2, 0.02, flat('#1a1612'), [3, 1.12, -6.95]))); g.add(noOutline(box(0.4, 0.25, 0.04, flat('#f2e2b0'), [3, 2.7, -6.9])));
  const stairLight = new THREE.PointLight('#f2d8a0', 1.6, 6, 1.6); stairLight.position.set(3, 2.6, -6.3); g.add(stairLight);
  // props
  for (const [x, z, c] of [[-6.6, -5.6, '#3f6a4a'], [-6.6, -4.2, '#4a4a5a'], [-6.6, -2.8, '#8a6a3a']]) g.add(rbox(1.0, 1.2, 1.0, 0.06, toon(c), [x, 0.6, z]));
  for (const [x, z, ry] of [[6.8, 3.5, 0.3], [6.6, 2.4, -0.2]]) { const b = new THREE.Group(); for (const zz of [-0.5, 0.5]) b.add(torus(0.32, 0.03, toon('#1a1a1e'), [0, 0.34, zz], [0, Math.PI / 2, 0])); b.add(box(0.04, 0.04, 1.0, toon('#c83a3a'), [0, 0.5, 0], [0.3, 0, 0])); b.add(box(0.04, 0.4, 0.04, toon('#c83a3a'), [0, 0.55, -0.3])); b.position.set(x, 0, z); b.rotation.y = ry; g.add(b); }
  g.add(tree(-3.5, 1.5, 0.9, 7));
  const line = new THREE.Group(); line.add(noOutline(box(0.015, 0.015, 9, flat('#d8d8d8'), [0, 2.5, 0]))); const lc = ['#e8e4d8', '#c84a4a', '#4a7ac8', '#e8d070', '#d8d8e8'];
  for (let i = 0; i < 6; i++) line.add(plane(0.6 + r() * 0.4, 0.7 + r() * 0.5, new THREE.MeshLambertMaterial({ color: lc[i % 5], side: THREE.DoubleSide }), [0, 2.1, -3.5 + i * 1.4], [0, Math.PI / 2, 0]));
  line.position.x = 1.5; g.add(line);
  for (const [x, z] of [[-2, 3.5], [4, -2.5]]) g.add(noOutline(at(disc(0.9 + r(), new THREE.MeshLambertMaterial({ color: '#3a4458', transparent: true, opacity: 0.7 })), [x, 0.012, z], [-Math.PI / 2, 0, 0], [1.4, 1, 1])));
  const helis = (o.helis || []).map(h => { const H = heli(); g.add(H.g); return { ...h, H }; });
  const set = makeSet(g, {
    mood: 'dusk', moodOverride: { bg: '#2a2438', amb: ['#8a7aa8', 1.3], hemi: ['#a890c0', '#2a2030', 0.9], key: ['#ffa070', 0.8, [-6, 10, 4]] },
    pov: o.pov || [0, 1.5, 9], look: o.look || [3, 1.3, -6.9], targets: { door: [3, 1.2, -6.9], arch: [0, 1.5, 7], sky: [0, 14, -4], ...(o.targets || {}) },
    onUpdate(v, t, S) { door.rotation.y = -(v.hofDoor ?? 0) * rad(100); helis.forEach(h => flyHeli(h.H, h.keys, t, { light: typeof h.light === 'function' ? h.light(t) : h.light, aim: h.aim, ry: h.ry })); o.onUpdate?.(v, t, S); },
  });
  set.scene.fog = new THREE.Fog('#2a2438', 14, 60); set.parts = { helis, door };
  return set;
}

// ---------------------------------------------------------------------------------------------- the hiding place (episode 2, night)
// A flat on the top floor. Hallway x -1.2..1.2, z -3..0 with the front door in the z = -3 wall (light under it from the stairwell);
// living room x -3.4..1.2, z 0..3.4 with a window in the x = -3.4 wall (z 1.0..2.2) onto a flat roof outside (x < -3.4).
// Across the courtyard (x -16..-24) another roof, a little higher. o.helis as in street().
export function hideout(o = {}) {
  const g = new THREE.Group(), H = 2.6;
  const floorT = texRep(canvasTex(128, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); x.strokeStyle = 'rgba(60,40,20,0.25)'; x.lineWidth = 2; for (let i = 0; i < 8; i++) { x.beginPath(); x.moveTo(0, i * 16); x.lineTo(128, i * 16); x.stroke(); } }), 4, 6);
  const wallM = lam('#b8b0a4'), wallM2 = lam('#a8a094');
  g.add(plane(4.6, 6.4, new THREE.MeshLambertMaterial({ color: '#8a6a4a', map: floorT }), [-1.1, 0, 0.2], [-Math.PI / 2, 0, 0])); g.add(plane(4.6, 6.4, lam('#d0ccc4'), [-1.1, H, 0.2], [Math.PI / 2, 0, 0]));
  g.add(plane(2.4, H, wallM, [0, H / 2, -3], [0, 0, 0])); g.add(plane(3.0, H, wallM2, [1.2, H / 2, -1.5], [0, -Math.PI / 2, 0])); g.add(plane(3.4, H, wallM2, [1.2, H / 2, 1.7], [0, -Math.PI / 2, 0]));
  g.add(plane(3.0, H, wallM2, [-1.2, H / 2, -1.5], [0, Math.PI / 2, 0])); g.add(plane(4.6, H, wallM, [-1.1, H / 2, 3.4], [0, Math.PI, 0])); g.add(plane(2.2, H, wallM, [-2.3, H / 2, 0], [0, 0, 0]));
  // window wall x = -3.4 with the opening z 1.0..2.2, y 0.8..2.1
  const WX = -3.4; g.add(box(0.2, 0.8, 3.4, wallM2, [WX, 0.4, 1.7])); g.add(box(0.2, H - 2.1, 3.4, wallM2, [WX, 2.1 + (H - 2.1) / 2, 1.7])); g.add(box(0.2, 1.3, 1.0, wallM2, [WX, 1.45, 0.5])); g.add(box(0.2, 1.3, 1.2, wallM2, [WX, 1.45, 2.8]));
  const sash = new THREE.Group(); sash.position.set(WX + 0.05, 0.8, 2.2); sash.add(box(0.05, 1.3, 1.2, toon('#e8e4dc'), [0, 0.65, -0.6])); sash.add(noOutline(box(0.02, 1.15, 1.05, new THREE.MeshBasicMaterial({ color: '#2a3048', transparent: true, opacity: 0.35 }), [0, 0.65, -0.6]))); g.add(sash);
  // front door with a peephole, the light under it
  g.add(box(1.25, 2.3, 0.08, toon('#4a3e34'), [0, 1.15, -2.98])); const fd = grp(box(1.0, 2.1, 0.06, toon('#6a5444'), [0, 1.05, -2.94]), box(0.05, 0.14, 0.06, toon('#c8c0a8'), [0.38, 1.05, -2.9]), noOutline(disc(0.018, flat('#d8d0b0'), [0, 1.55, -2.905])), box(0.4, 0.5, 0.02, toon('#5a4636'), [0, 1.6, -2.905]), box(0.4, 0.5, 0.02, toon('#5a4636'), [0, 0.6, -2.905])); g.add(fd);
  const gap = noOutline(box(0.95, 0.02, 0.02, flat('#f2d8a0'), [0, 0.012, -2.9])); g.add(gap);
  const gapLight = new THREE.PointLight('#f2d8a0', 0, 3.2, 1.6); gapLight.position.set(0, 0.15, -2.7); g.add(gapLight);
  const beams = [0, 1].map(i => { const b = noOutline(plane(0.5, 0.02, new THREE.MeshBasicMaterial({ color: '#fff4c8', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }), [0, 0.011, -2.6], [-Math.PI / 2, 0, 0])); b.scale.set(1, 1, 1); g.add(b); return b; });
  // furniture: coat rack, a mirror, a sofa, a table with a candle, a photo of two boys
  g.add(cyl(0.03, 0.03, 1.8, toon('#3a2a20'), [0.9, 0.9, -2.3])); g.add(rbox(0.4, 0.7, 0.2, 0.08, toon('#5a6a4a'), [0.85, 1.3, -2.2]));
  g.add(box(0.05, 0.9, 0.6, toon('#c8b890'), [-1.17, 1.5, -1.2])); g.add(noOutline(box(0.02, 0.8, 0.5, flat('#3a4258'), [-1.14, 1.5, -1.2])));
  g.add(rbox(2.0, 0.45, 0.85, 0.1, toon('#6a4a5a'), [-1.0, 0.32, 3.0])); g.add(rbox(2.0, 0.55, 0.25, 0.1, toon('#6a4a5a'), [-1.0, 0.7, 3.32]));
  g.add(box(0.9, 0.05, 0.6, toon('#8a6a4a'), [-1.2, 0.5, 1.6])); for (const [x, z] of [[-1.6, 1.35], [-0.8, 1.35], [-1.6, 1.85], [-0.8, 1.85]]) g.add(box(0.04, 0.5, 0.04, toon('#6a4a3a'), [x, 0.25, z]));
  const photo = canvasTex(96, 72, x => { x.fillStyle = '#e8e0d0'; x.fillRect(0, 0, 96, 72); x.fillStyle = '#9ab0c8'; x.fillRect(6, 6, 84, 60); x.fillStyle = '#e9b999'; for (const [cx, cy, rr] of [[34, 34, 11], [62, 30, 13]]) { x.beginPath(); x.arc(cx, cy, rr, 0, 7); x.fill(); } x.fillStyle = '#5a3a22'; x.fillRect(22, 20, 24, 8); x.fillRect(48, 14, 28, 9); x.fillStyle = '#8a2a2e'; x.fillRect(48, 44, 28, 22); x.fillStyle = '#3d6a8a'; x.fillRect(22, 46, 24, 20); });
  g.add(at(box(0.32, 0.24, 0.02, new THREE.MeshLambertMaterial({ map: photo })), [-1.4, 0.65, 1.55], [-0.35, 0.3, 0]));
  // outside: the flat roof, chimneys, the roofs across the courtyard, the burning city on the horizon
  const roofM = lam('#5a565a'); g.add(box(14, 0.4, 18, roofM, [WX - 7.1, -0.2, 0])); g.add(box(0.3, 0.6, 18, lam('#6a6266'), [WX - 14.0, 0.3, 0]));
  for (const [x, z, h] of [[-6, -3, 1.4], [-9, 4, 1.8], [-12, -6, 1.2], [-7.5, 6.5, 1.0]]) { g.add(box(0.7, h, 0.7, lam('#8a6a5a'), [x, h / 2, z])); g.add(box(0.85, 0.12, 0.85, lam('#5a4a44'), [x, h + 0.06, z])); }
  for (const [x, z] of [[-8, -1], [-11, 2.5]]) g.add(box(1.2, 0.5, 0.9, lam('#7a7a80'), [x, 0.25, z]));
  g.add(cyl(0.02, 0.02, 2.5, toon('#2a2a30'), [-10, 1.25, -2])); g.add(box(1.2, 0.03, 0.03, toon('#2a2a30'), [-10, 2.3, -2]));
  g.add(box(10, 0.5, 20, lam('#4a464c'), [-24, 1.0, 0])); g.add(box(10, 8, 20, lam('#6a6266'), [-24, -3.25, 0])); g.add(box(0.3, 0.6, 20, lam('#5a5258'), [-19.1, 1.55, 0]));
  for (const [x, z, h] of [[-22, -5, 1.5], [-26, 3, 1.8]]) g.add(box(0.7, h, 0.7, lam('#7a5a4a'), [x, 1.25 + h / 2, z]));
  g.add(box(10, 14, 0.3, lam('#2a2830'), [-14, -7, 0], [0, Math.PI / 2, 0]));    // the drop into the courtyard (dark)
  const sky = canvasTex(512, 128, x => { x.fillStyle = 'rgba(0,0,0,0)'; x.fillRect(0, 0, 512, 128); x.fillStyle = '#1c1820'; const rr = rng(9); let xx = 0; while (xx < 512) { const w = 16 + rr() * 40, h = 20 + rr() * 70; x.fillRect(xx, 128 - h, w, h); if (rr() < 0.4) { x.fillStyle = '#ff8a3a'; x.fillRect(xx + 4, 128 - h + 8, 4, 4); x.fillStyle = '#1c1820'; } xx += w + 2; } });
  g.add(noOutline(at(plane(140, 34, new THREE.MeshBasicMaterial({ map: sky, transparent: true }), [-60, 4, 0], [0, Math.PI / 2, 0]))));
  for (const [z, s] of [[-20, 18], [8, 24], [28, 14]]) g.add(glow(s * 1.6, s * 0.7, '#ff7a2a', 0.45, [-58, 2, z], [0, Math.PI / 2, 0]));
  const plumes = [[-48, 4, -14, 24, 3.0], [-52, 6, 16, 30, 3.4]].map(([x, y, z, h, rr], k) => { const p = plume(x, y, z, h, rr, 70 + k, [0, 0.2]); g.add(p); return p; });
  const helis = (o.helis || []).map(h => { const Hh = heli(); g.add(Hh.g); return { ...h, H: Hh }; });
  const winLight = new THREE.PointLight('#dfe8ff', 0, 7, 1.4); winLight.position.set(WX + 0.6, 1.6, 1.6); g.add(winLight);
  const set = makeSet(g, {
    mood: 'night', moodOverride: { bg: '#0c0a14', amb: ['#5a5a86', 1.75], hemi: ['#6a6aa8', '#1a1626', 1.05], key: ['#ff9a6a', 0.75, [-20, 6, 2]], spill: ['#f2d8a0', 0] },
    pov: o.pov || [-0.6, 1.5, 2.2], look: o.look || [0, 1.2, -3], targets: { door: [0, 1.2, -2.95], peep: [0, 1.55, -2.95], gap: [0, 0.05, -2.9], window: [WX, 1.45, 1.6], roof: [-9, 0.6, 0], across: [-22, 2.6, -1], photo: [-1.4, 0.65, 1.55], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      const L = v.gapLight ?? 1; gap.material.color.setRGB(0.95 * L + 0.05, 0.85 * L + 0.05, 0.63 * L + 0.05); gapLight.intensity = 0.8 * L * (1 - 0.8 * (v.feet ?? 0));
      if (v.feet) gap.material.color.multiplyScalar(1 - 0.75 * v.feet);
      beams.forEach((b, i) => { const k = v.torch ?? 0; b.material.opacity = 0.28 * k * (0.6 + 0.4 * Math.sin(t * 3 + i * 2)); b.position.x = 0.3 * Math.sin(t * 1.3 + i * 2.2); b.scale.x = 1 + 0.6 * Math.sin(t * 0.9 + i); });
      sash.rotation.y = -(v.window ?? 0) * rad(100);
      helis.forEach(h => flyHeli(h.H, h.keys, t, { light: typeof h.light === 'function' ? h.light(t) : h.light, aim: h.aim, ry: h.ry }));
      winLight.intensity = 3.5 * (v.sweep ?? 0); plumes.forEach(p => p.userData.update(t)); o.onUpdate?.(v, t, S);
    },
  });
  set.scene.fog = new THREE.Fog('#0c0a14', 16, 80); set.parts = { fd, sash, helis };
  return set;
}

// ---------------------------------------------------------------------------------------------- the river, the bridge and the jetty (episodes 3 and 4)
// Street and promenade at y 0 for z > 0, the city behind (z > 9). Embankment down to the riverside path (y -4.2, z -5.5..-7),
// water (y -4.7) to the far bank at z -40, a dark forest beyond. The stone bridge runs along z at x -4..4 (deck y 0.6),
// a checkpoint at its near end (barriers, sandbags, trucks, floodlights, the officer's table, a queue on the street).
// The old wooden jetty is downstream at x -34 (z -7 -> -15), a rowboat at its end. mood: 'night' | 'dawn'.
export function river(o = {}) {
  const g = new THREE.Group(), dawn = o.mood === 'dawn', WY = -4.7;
  const grass = texRep(canvasTex(128, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); const r = rng(12); for (let i = 0; i < 500; i++) { x.fillStyle = `rgba(30,50,30,${0.06 + r() * 0.14})`; x.fillRect(r() * 128, r() * 128, 1.5, 4); } }), 30, 4);
  const grassM = new THREE.MeshLambertMaterial({ color: dawn ? '#6a7a62' : '#4a5a4a', map: grass });
  g.add(plane(160, 30, lam('#6a6862'), [0, 0, 15], [-Math.PI / 2, 0, 0]));                                    // street / promenade
  const slope = plane(160, Math.hypot(5.5, 4.2), grassM, [0, -2.1, -2.75]); slope.rotation.x = -Math.PI / 2 + Math.atan2(4.2, 5.5); g.add(slope);
  g.add(box(160, 0.3, 1.6, lam('#8a8278'), [0, -4.35, -6.3]));                                                 // riverside path
  const waterTex = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); const r = rng(21); for (let i = 0; i < 140; i++) { x.strokeStyle = `rgba(255,255,255,${0.2 + r() * 0.5})`; x.lineWidth = 2; const y = r() * 256, x0 = r() * 256; x.beginPath(); x.moveTo(x0, y); x.lineTo(x0 + 20 + r() * 30, y); x.stroke(); } }), 30, 8);
  const water = noOutline(plane(200, 36, new THREE.MeshLambertMaterial({ color: dawn ? '#7a8a96' : '#2a3448', map: waterTex }), [0, WY, -25], [-Math.PI / 2, 0, 0])); g.add(water);
  const farSlope = plane(200, 8, grassM, [0, WY + 2, -44]); farSlope.rotation.x = -Math.PI / 2 - 0.55; g.add(farSlope); g.add(plane(200, 60, grassM, [0, -0.5, -78], [-Math.PI / 2, 0, 0]));
  const r = rng(31); for (let i = 0; i < 46; i++) { const x = -90 + i * 4 + r() * 3, z = -50 - r() * 22, h = 6 + r() * 6; g.add(cyl(0.2, 0.3, h * 0.5, toon('#3a2e26'), [x, -0.5 + h * 0.25, z])); g.add(new THREE.Mesh(new THREE.ConeGeometry(1.6 + r(), h * 0.85, 8), toon(['#2e4232', '#344a38', '#28382c'][i % 3]))); g.children[g.children.length - 1].position.set(x, -0.5 + h * 0.55, z); }
  for (let i = 0; i < 18; i++) g.add(sph(0.6 + r() * 0.5, toon(['#3e5a3a', '#4a6a44'][i % 2]), [-70 + i * 8 + r() * 4, -1.6 - r() * 1.5, -2.5 - r() * 2], [1.3, 0.8, 1]));   // bushes on the slope
  // city behind the promenade
  const C = ['#9a8a7a', '#8a8a96', '#a08a78', '#8a9098', '#968478'];
  for (let k = 0; k < 12; k++) building(g, { x: -66 + k * 12, z: 9, w: 11.6, h: 10 + (k % 4) * 3, side: -2, color: C[k % 5], seed: 300 + k, lit: dawn ? 0 : 0.12, burnt: 0.15, d: 9 });
  for (let x = -80; x <= 80; x += 1.6) if (Math.abs(x) > 4.3) g.add(box(0.07, 1.0, 0.07, toon('#3a3a40'), [x, 0.5, -0.1]));   // promenade railing
  for (const s of [-1, 1]) g.add(box(75.5, 0.07, 0.07, toon('#3a3a40'), [s * 42.15, 0.98, -0.1]));
  // the bridge
  const stone = lam(dawn ? '#9a948a' : '#6a665e'), stoneD = lam(dawn ? '#7a746c' : '#4a4640');
  g.add(box(8, 1.0, 46, stone, [0, 0.1, -21])); g.add(box(8.6, 0.3, 46, stoneD, [0, -0.5, -21]));
  for (const z of [-14, -28]) { g.add(box(7, 5.2, 3, stone, [0, WY + 2.2, z])); g.add(box(7.4, 0.6, 3.4, stoneD, [0, WY + 0.2, z])); }
  for (const s of [-1, 1]) { g.add(box(0.3, 0.9, 46, stone, [s * 3.85, 1.05, -21])); for (let z = 1; z > -44; z -= 2.2) g.add(box(0.36, 1.1, 0.36, stoneD, [s * 3.85, 1.1, z])); }
  g.add(box(8, 6, 0.5, lam('#1a1a1e'), [0, WY + 2.6, -5.8]));                                                  // the dark under the arch, seen from the path
  // the checkpoint
  const cp = new THREE.Group();
  cp.add(at(barrier(5.4), [0, 0.6, -3.0])); cp.add(at(barrier(5.4), [0, 0.6, -9.5])); cp.add(at(sandbags(5), [-2.5, 0.6, -5.5], [0, Math.PI / 2, 0])); cp.add(at(sandbags(5), [2.6, 0.6, -6.5], [0, Math.PI / 2, 0]));
  const tr1 = truck(), tr2 = truck(); tr1.g.position.set(-1.6, 0.6, -15); tr2.g.position.set(1.6, 0.6, -21); tr2.g.rotation.y = Math.PI; cp.add(tr1.g, tr2.g);
  cp.add(box(1.6, 0.06, 0.8, toon('#4a4a3a'), [2.2, 1.35, -1.6])); for (const [x, z] of [[1.5, -1.3], [2.9, -1.3], [1.5, -1.9], [2.9, -1.9]]) cp.add(box(0.05, 0.75, 0.05, toon('#2a2a22'), [x, 0.97, z]));
  const photos = canvasTex(128, 64, x => { x.fillStyle = '#4a4a3a'; x.fillRect(0, 0, 128, 64); for (let i = 0; i < 6; i++) { x.fillStyle = '#e8e0d0'; x.fillRect(4 + i * 21, 8, 18, 22); x.fillStyle = ['#e9b999', '#c98f68', '#f3cdb6'][i % 3]; x.beginPath(); x.arc(13 + i * 21, 17, 5, 0, 7); x.fill(); } x.fillStyle = '#e8e0d0'; x.fillRect(40, 34, 30, 26); x.fillStyle = '#e9b999'; x.beginPath(); x.arc(55, 44, 8, 0, 7); x.fill(); x.fillStyle = '#5a3a22'; x.fillRect(46, 34, 18, 5); x.fillStyle = '#c83a3a'; x.fillRect(72, 52, 22, 4); });
  cp.add(noOutline(at(plane(1.5, 0.75, new THREE.MeshLambertMaterial({ map: photos })), [2.2, 1.39, -1.6], [-Math.PI / 2, 0, 0])));
  const deskLamp = new THREE.PointLight('#ffe0a0', dawn ? 0 : 1.4, 4, 1.6); deskLamp.position.set(2.2, 2.0, -1.6); cp.add(deskLamp);
  const flood = []; for (const [x, z] of [[-3.6, -2.4], [3.6, -4.2]]) { cp.add(cyl(0.06, 0.08, 4.4, toon('#2a2d34'), [x, 2.8, z])); cp.add(at(rbox(0.6, 0.45, 0.4, 0.06, toon('#3a3d44')), [x, 5.0, z], [0.5, 0, 0])); cp.add(noOutline(at(disc(0.2, flat('#fffbe8')), [x, 4.92, z + 0.2], [0.5 - Math.PI / 2 + Math.PI / 2, 0, 0])));
    const s = new THREE.SpotLight('#fff4d8', dawn ? 0 : 26, 30, rad(34), 0.8, 1.3); s.position.set(x, 5, z); const tg = new THREE.Object3D(); tg.position.set(x * 0.2, 0, z + 6); cp.add(s, tg); s.target = tg; flood.push(s); cp.add(glow(1.6, 1.6, '#fff4d0', dawn ? 0 : 0.6, [x, 5.0, z + 0.3])); }
  g.add(cp);
  // the old jetty and the rowboat
  const JX = -34, wood = toon(dawn ? '#8a7258' : '#5a4a3a'), woodD = toon(dawn ? '#6a5642' : '#3a3028');
  for (let z = -6.8; z > -15.2; z -= 0.42) g.add(box(2.0, 0.08, 0.36, wood, [JX, -4.15, z]));
  for (let z = -7.5; z > -15.5; z -= 2.5) for (const s of [-1, 1]) g.add(cyl(0.1, 0.1, 2.2, woodD, [JX + s * 1.0, -4.9, z]));
  g.add(cyl(0.1, 0.1, 1.0, woodD, [JX + 1.0, -3.6, -15.0]));
  const boat = new THREE.Group(); const hullM = toon(dawn ? '#6a7a8a' : '#4a5a6a'), inM = toon('#7a6a52');
  boat.add(rbox(1.3, 0.45, 3.4, 0.2, hullM, [0, 0.0, 0])); boat.add(noOutline(rbox(1.1, 0.3, 3.1, 0.15, inM, [0, 0.12, 0]))); for (const zz of [-0.9, 0.3, 1.2]) boat.add(box(1.1, 0.06, 0.3, woodD, [0, 0.2, zz]));
  const oars = [-1, 1].map(s => { const o2 = new THREE.Group(); o2.position.set(s * 0.6, 0.3, 0.3); o2.add(box(0.05, 0.05, 2.2, woodD, [s * 0.9, 0, 0], [0, s * 1.2, 0])); o2.add(box(0.06, 0.25, 0.5, woodD, [s * 1.85, -0.05, 0.05], [0, s * 1.2, 0])); boat.add(o2); return o2; });
  boat.position.set(JX + 2.0, WY + 0.2, -14.4); g.add(boat);
  if (dawn) g.children.forEach(c => { if (Math.hypot(c.position.x - JX, c.position.z + 11) > 16) noOutline(c); });   // no ink lines floating in the fog
  const helis = (o.helis || []).map(h => { const H = heli(); g.add(H.g); return { ...h, H }; });
  const runConvoy = convoy(g, o.convoy || []);
  const bg = dawn ? '#9aa4b0' : '#0a0c16';
  const set = makeSet(g, {
    mood: dawn ? 'day' : 'night', moodOverride: dawn ? { bg, amb: ['#c4ccd8', 1.3], hemi: ['#dfe6f2', '#5a6060', 0.8], key: ['#ffe0c0', 0.5, [10, 8, -10]] } : { bg, amb: ['#5a62a0', 1.85], hemi: ['#6a74b8', '#1a1c28', 1.1], key: ['#9fb0ff', 0.8, [-6, 8, 4]], spill: ['#fff', 0] },
    pov: o.pov || [-12, -1.2, -2.6], look: o.look || [0, 1.4, -4], targets: { bridge: [0, 1.5, -6], table: [2.2, 1.5, -1.6], queue: [0, 1.4, 3], under: [0, WY + 1.8, -6], jetty: [JX, -3.8, -11], boat: [JX + 2.0, WY + 0.6, -14.4], farBank: [0, 0, -46], water: [0, WY, -20], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      waterTex.offset.x = t * 0.04; waterTex.offset.y = t * 0.01;
      if (o.boatAt) { const [bx, bz, bry] = o.boatAt(t); boat.position.set(bx, WY + 0.2 + 0.03 * Math.sin(t * 1.4), bz); boat.rotation.y = rad(bry); } else { const bp = v.boat ?? 0; boat.position.set(JX + 2.0 + (v.boatX ?? 0), WY + 0.2 + 0.03 * Math.sin(t * 1.4), -14.4 - bp * (o.boatDist ?? 16)); boat.rotation.y = rad(v.boatRy ?? 0); } boat.rotation.z = 0.02 * Math.sin(t * 1.1);
      const row = v.row ?? 0; oars.forEach((oa, i) => { oa.rotation.y = row * 0.45 * Math.sin(t * 2.4) * (i ? -1 : 1); oa.rotation.z = row * 0.12 * Math.cos(t * 2.4) * (i ? -1 : 1); });
      helis.forEach(h => flyHeli(h.H, h.keys, t, { light: typeof h.light === 'function' ? h.light(t) : h.light, aim: h.aim, ry: h.ry })); runConvoy(t);
      o.onUpdate?.(v, t, S);
    },
  });
  set.scene.fog = dawn ? new THREE.Fog(bg, 3, o.fogFar ?? 34) : new THREE.Fog(bg, 18, 90); set.parts = { boat, helis, flood, cp }; set.JX = JX; set.WY = WY;
  return set;
}

// the photo the officer holds up: a boy in a petrol jacket (Luca), on white card
export function photoCard() {
  const tex = canvasTex(96, 128, x => { x.fillStyle = '#f2ece0'; x.fillRect(0, 0, 96, 128); x.fillStyle = '#8a9aa8'; x.fillRect(8, 8, 80, 92); x.fillStyle = '#3d6a8a'; x.fillRect(22, 70, 52, 30);
    x.fillStyle = '#e9b999'; x.fillRect(40, 58, 16, 14); x.beginPath(); x.arc(48, 46, 18, 0, 7); x.fill(); x.fillStyle = '#4a3020'; x.beginPath(); x.arc(48, 40, 18, Math.PI, 0); x.fill();
    x.fillStyle = '#fff'; for (const ex of [41, 55]) { x.beginPath(); x.arc(ex, 47, 5, 0, 7); x.fill(); } x.fillStyle = '#111'; for (const ex of [41, 55]) { x.beginPath(); x.arc(ex, 48, 2.2, 0, 7); x.fill(); }
    x.fillStyle = '#c83a3a'; x.font = `800 13px ${FONT}`; x.fillText('LUCA', 30, 118); });
  const m = noOutline(plane(0.34, 0.46, new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide }))); return m;
}
