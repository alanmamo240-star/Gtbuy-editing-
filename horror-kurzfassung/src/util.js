// Shared helpers: math, seeded noise, materials, mesh builders, canvas textures.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
THREE.ColorManagement.enabled = false;   // display-referred colours: a hex is the colour you get when fully lit
export { THREE };

export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smooth = t => { t = clamp(t); return t * t * (3 - 2 * t); };
export const easeIO = t => { t = clamp(t); return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
export const easeOut = t => 1 - Math.pow(1 - clamp(t), 3);
export const backOut = t => { t = clamp(t); const c = 1.70158; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
export const rad = d => d * Math.PI / 180;
export function rng(seed = 1) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
const hash = (i, seed) => { let x = Math.sin(i * 127.1 + seed * 311.7) * 43758.5453; return x - Math.floor(x); };
// smooth 1-D value noise in -1..1 (handheld camera, idle sway)
export function noise(t, seed = 0) { const i = Math.floor(t), f = t - i, u = f * f * (3 - 2 * f); return lerp(hash(i, seed), hash(i + 1, seed), u) * 2 - 1; }

// ---------- materials ----------
const gradData = new Uint8Array([120, 120, 120, 255, 185, 185, 185, 255, 232, 232, 232, 255, 255, 255, 255, 255]);
export const gradMap = new THREE.DataTexture(gradData, 4, 1, THREE.RGBAFormat); gradMap.minFilter = gradMap.magFilter = THREE.NearestFilter; gradMap.needsUpdate = true;
const cache = new Map();
const key = (k, c, o) => k + new THREE.Color(c).getHexString() + (o ? JSON.stringify(o) : '');
// toon(): characters and props (banded shading). lam(): room shell (smooth). flat(): unlit, for lit windows, screens, glows.
export function toon(color, o) { const k = key('t', color, o); if (!cache.has(k)) cache.set(k, new THREE.MeshToonMaterial({ color, gradientMap: gradMap, ...o })); return cache.get(k); }
export function lam(color, o) { const k = key('l', color, o); if (!cache.has(k)) cache.set(k, new THREE.MeshLambertMaterial({ color, ...o })); return cache.get(k); }
export function flat(color, o) { const k = key('f', color, o); if (!cache.has(k)) cache.set(k, new THREE.MeshBasicMaterial({ color, ...o })); return cache.get(k); }

// ---------- meshes ----------
const place = (m, p, r) => { if (p) m.position.set(p[0], p[1], p[2]); if (r) m.rotation.set(r[0], r[1], r[2]); return m; };
const asMat = m => (typeof m === 'string' || typeof m === 'number') ? toon(m) : m;
const geo = new Map();
const G = (k, f) => { if (!geo.has(k)) geo.set(k, f()); return geo.get(k); };
export const box = (w, h, d, m, p, r) => place(new THREE.Mesh(G(`b${w},${h},${d}`, () => new THREE.BoxGeometry(w, h, d)), asMat(m)), p, r);
export const rbox = (w, h, d, rr, m, p, r) => place(new THREE.Mesh(G(`r${w},${h},${d},${rr}`, () => new RoundedBoxGeometry(w, h, d, 4, Math.min(rr, w / 2, h / 2, d / 2))), asMat(m)), p, r);
export const sph = (rr, m, p, s) => { const o = place(new THREE.Mesh(G(`s${rr}`, () => new THREE.SphereGeometry(rr, 28, 20)), asMat(m)), p); if (s) o.scale.set(s[0], s[1], s[2]); return o; };
export const cyl = (rt, rb, h, m, p, r, seg = 20) => place(new THREE.Mesh(G(`c${rt},${rb},${h},${seg}`, () => new THREE.CylinderGeometry(rt, rb, h, seg)), asMat(m)), p, r);
// capsule hanging DOWN from its origin (origin = top joint), total length len
export function limb(rr, len, m) { const g = G(`l${rr},${len}`, () => { const q = new THREE.CapsuleGeometry(rr, Math.max(0.001, len - 2 * rr), 8, 16); q.translate(0, -len / 2, 0); return q; }); return new THREE.Mesh(g, asMat(m)); }
export const plane = (w, h, m, p, r) => place(new THREE.Mesh(G(`p${w},${h}`, () => new THREE.PlaneGeometry(w, h)), asMat(m)), p, r);
export const disc = (rr, m, p, r) => place(new THREE.Mesh(G(`d${rr}`, () => new THREE.CircleGeometry(rr, 28)), asMat(m)), p, r);
export const torus = (R, t, m, p, r) => place(new THREE.Mesh(G(`t${R},${t}`, () => new THREE.TorusGeometry(R, t, 10, 30)), asMat(m)), p, r);
export function grp(...kids) { const g = new THREE.Group(); for (const k of kids.flat()) if (k) g.add(k); return g; }
export const at = (o, p, r, s) => { place(o, p, r); if (s != null) (typeof s === 'number' ? o.scale.setScalar(s) : o.scale.set(s[0], s[1], s[2])); return o; };
// marks: noOutline = skipped by the ink pass (glows, light pools); sameId = share one ink id (no lines inside a cluster)
export const noOutline = o => { o.traverse(m => { m.userData.noOutline = true; }); return o; };
let gid = 1;
export const sameId = o => { const id = gid++; o.traverse(m => { m.userData.inkGroup = id; }); return o; };

// ---------- canvas textures ----------
export function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); draw(x, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.NoColorSpace; t.anisotropy = 8; return t;
}
export const FONT = 'Rubik, "Arial Black", sans-serif';
// a flat sign with text; lit:false = reacts to room light (posters), lit:true = glows (EXIT signs, screens)
export function sign(text, w, h, { bg = '#ffffff', fg = '#1b1f3a', weight = 800, size = 0.55, lit = false, border = null, align = 'center', lines = null } = {}) {
  const pxh = 256, pxw = Math.round(pxh * w / h);
  const tex = canvasTex(pxw, pxh, (x) => {
    x.fillStyle = bg; x.fillRect(0, 0, pxw, pxh);
    if (border) { x.strokeStyle = border; x.lineWidth = 14; x.strokeRect(7, 7, pxw - 14, pxh - 14); }
    const L = lines || String(text).split('\n'); const fs = pxh * size / Math.max(1, L.length * 0.92);
    x.fillStyle = fg; x.textAlign = align; x.textBaseline = 'middle'; x.font = `${weight} ${fs}px ${FONT}`;
    L.forEach((s, i) => { let f = fs; x.font = `${weight} ${f}px ${FONT}`; while (x.measureText(s).width > pxw * 0.9 && f > 8) { f -= 2; x.font = `${weight} ${f}px ${FONT}`; }
      x.fillText(s, align === 'center' ? pxw / 2 : pxw * 0.07, pxh / 2 + (i - (L.length - 1) / 2) * fs * 1.08); });
  });
  const M = lit ? new THREE.MeshBasicMaterial({ map: tex }) : new THREE.MeshLambertMaterial({ map: tex });
  return new THREE.Mesh(new THREE.PlaneGeometry(w, h), M);
}
// soft radial glow sprite (additive), used for light spill and lit windows
let glowTex;
export function glow(w, h, color, opacity = 1, p, r) {
  glowTex ||= canvasTex(128, 128, (x) => { const g = x.createRadialGradient(64, 64, 0, 64, 64, 64); g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.4, 'rgba(255,255,255,0.45)'); g.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 128, 128); });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: glowTex, color, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false }));
  m.userData.noOutline = true; return place(m, p, r);
}
