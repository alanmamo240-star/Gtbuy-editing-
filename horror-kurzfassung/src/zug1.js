// DER ZUG OHNE MORGEN · Folge 1 – "Der letzte Zug" (30 s). Original story, fictional station, 1944. Cartoon, violence off screen.
// Paul: green jacket. Emil: brown cap. Lena: grey coat. A conductor with a lantern.
// Unlike the kit's first-person example this is a third-person scene: the camera is an invisible observer on the platform that
// whip-pans and dollies between a few stations. Every beat is placed on the script's time marks (0–8, 8–20, 20–30 s).
import { story } from './core.js';
import { POSES } from './toon.js';
import { makeSet } from './sets.js';
import { CAST } from './cast.js';
import { Q, towards, fogOff, texRep, loadTimings, sequencer, mover, breathPuffs } from './lib.js';
import { THREE, toon, lam, flat, box, rbox, sph, cyl, plane, torus, grp, at, noOutline, sameId, sign, glow, canvasTex, rng, clamp, lerp, smooth, easeIO, noise, rad, FONT } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

// ------------------------------------------------------------------------------------------------ camera stations
const PA = [6.2, 1.3, 0.75];     // shot A: down the platform, the kids run toward us
const PB = [3.3, 1.35, 1.1];     // the open door, Emil
const PE = [1.1, 1.3, 1.25];     // Lena close
const PF = [4.6, 1.32, -0.62];   // platform edge beyond the end of the carriage: the empty tracks, the conductor
const C5 = [0.25, 1.4, 2.1];     // beside the conductor, looking at the kids and the train door
const camPt = t => t < 3.3 ? PA : t < 8.3 ? PB : t < 9.9 ? PE : t < 19.0 ? PF : C5;

// ------------------------------------------------------------------------------------------------ the station
const FOG = new THREE.Color('#1a1f38'), FLASH = new THREE.Color('#6e4432');
const billboards = [], fogLayers = [];
const g = new THREE.Group();

// platform: paving slabs, curb, canopy with columns
const pave = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); x.strokeStyle = 'rgba(20,24,60,0.32)'; x.lineWidth = 5; x.strokeRect(2, 2, 252, 252); x.beginPath(); x.moveTo(128, 0); x.lineTo(128, 256); x.stroke();
  const r = rng(4); x.fillStyle = 'rgba(20,24,60,0.10)'; for (let i = 0; i < 260; i++) x.fillRect(r() * 256, r() * 256, 2 + r() * 4, 2 + r() * 4); }), 60 / 1.3, 7 / 1.3);
g.add(plane(60, 7, new THREE.MeshLambertMaterial({ color: '#575c7c', map: pave }), [-6, 0, 2.25], [-Math.PI / 2, 0, 0]));
g.add(box(60, 1.0, 7.0, lam('#363a56'), [-6, -0.502, 2.25]));
g.add(box(60, 0.07, 0.34, lam('#8d90aa'), [-6, 0.035, -1.08]));
g.add(box(42, 0.12, 4.6, lam('#262a40'), [-6, 4.12, 3.5]));
g.add(box(42, 0.4, 0.05, lam('#30344f'), [-6, 3.86, 1.22]));
for (const x of [-18, -12, -6, 0, 6]) { g.add(cyl(0.085, 0.11, 4.06, toon('#22263c'), [x, 2.03, 4.6])); g.add(box(0.5, 0.08, 0.5, toon('#22263c'), [x, 4.0, 4.6])); g.add(box(0.06, 0.06, 3.4, toon('#22263c'), [x, 3.95, 2.9])); }
// back wall of the station building behind the canopy
g.add(box(42, 4.2, 0.3, lam('#2d2f48'), [-6, 2.1, 5.9]));
for (const x of [-15, -10.5, -3, 1.5]) { g.add(box(1.1, 1.5, 0.05, toon('#1d1f33'), [x, 1.9, 5.74])); g.add(noOutline(box(0.95, 1.35, 0.02, flat('#3a3040'), [x, 1.9, 5.72]))); }
// track bed, two tracks, telegraph poles
const grav = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); const r = rng(9); for (let i = 0; i < 900; i++) { x.fillStyle = `rgba(20,22,50,${0.08 + r() * 0.18})`; x.beginPath(); x.arc(r() * 256, r() * 256, 1 + r() * 3.2, 0, 7); x.fill(); } }), 40, 7);
g.add(plane(90, 14, new THREE.MeshLambertMaterial({ color: '#34374f', map: grav }), [5, -1.0, -8.25], [-Math.PI / 2, 0, 0]));
function track(cz, x0, x1) {
  const T = new THREE.Group(); for (const dz of [-0.72, 0.72]) T.add(box(x1 - x0, 0.13, 0.07, toon('#8e94b2'), [(x0 + x1) / 2, -0.87, cz + dz]));
  for (let x = x0 + 0.3; x < x1; x += 0.62) T.add(box(0.25, 0.1, 2.5, toon('#3d3331'), [x, -0.955, cz])); return sameId(T);
}
g.add(track(-3.0, -22, 48)); g.add(track(-7.5, -22, 48));
for (let x = -18; x < 46; x += 12) { g.add(cyl(0.09, 0.12, 6.5, toon('#2a2434'), [x, 2.25, -11.5])); g.add(box(1.3, 0.08, 0.08, toon('#2a2434'), [x, 5.2, -11.5])); }

// the carriage. Its front end (x = 3) has buffers and a loose coupling: no locomotive.
const CZ = -3.0, ZS = -1.6, bodyM = lam('#6b302c'), lowM = lam('#4b2220'), trimM = toon('#c4a56c'), frameM = toon('#3a1816');
for (const [a, b] of [[-12, 0.35], [1.2, 3.0]]) {
  g.add(box(b - a, 2.75, 2.8, bodyM, [(a + b) / 2, 1.125, CZ]));
  g.add(box(b - a, 0.82, 0.02, lowM, [(a + b) / 2, 0.16, ZS + 0.01]));
  g.add(noOutline(box(b - a, 0.05, 0.02, trimM, [(a + b) / 2, 0.98, ZS + 0.012])));
}
g.add(box(0.85, 0.3, 2.8, bodyM, [0.775, 2.35, CZ])); g.add(box(0.85, 0.45, 2.8, bodyM, [0.775, -0.025, CZ]));
const winGlass = flat('#4a3524');
for (const x of [-10.4, -9.15, -7.9, -6.65, -4.15, -2.9, -1.65, -0.45, 2.15]) { g.add(box(1.03, 0.8, 0.03, frameM, [x, 1.55, ZS + 0.015])); g.add(plane(0.93, 0.7, winGlass, [x, 1.55, ZS + 0.033])); }
for (const x of [-11.5, -5.4]) {   // the other doors (shut)
  g.add(box(0.85, 2.0, 0.03, lam('#5e2a27'), [x, 1.2, ZS + 0.016])); g.add(box(0.5, 0.55, 0.012, frameM, [x, 1.55, ZS + 0.035])); g.add(plane(0.42, 0.47, winGlass, [x, 1.55, ZS + 0.042]));
  g.add(box(0.04, 0.18, 0.04, trimM, [x + 0.33, 1.0, ZS + 0.05])); for (const s of [-1, 1]) g.add(cyl(0.017, 0.017, 1.1, trimM, [x + s * 0.52, 1.15, ZS + 0.06]));
}
for (const s of [-1, 1]) g.add(cyl(0.017, 0.017, 1.1, trimM, [0.775 + s * 0.52, 1.15, ZS + 0.06]));
g.add(box(15, 0.14, 2.9, lam('#383a50'), [-4.5, 2.57, CZ]));
g.add(at(cyl(1.45, 1.45, 15, lam('#383a50')), [-4.5, 2.6, CZ], [0, 0, Math.PI / 2], [0.24, 1, 1]));
for (let x = -11; x < 2.6; x += 2.5) g.add(box(0.32, 0.14, 0.32, toon('#2c2e40'), [x, 2.98, CZ]));
g.add(box(14.4, 0.28, 2.3, lam('#151726'), [-4.5, -0.39, CZ]));
for (const bx of [-9.8, 0.6]) { g.add(box(2.8, 0.32, 2.0, toon('#14151f'), [bx, -0.58, CZ])); for (const dx of [-0.85, 0.85]) for (const dz of [-0.72, 0.72]) g.add(cyl(0.42, 0.42, 0.1, toon('#20222e'), [bx + dx, -0.43, CZ + dz], [Math.PI / 2, 0, 0])); }
// front end
g.add(box(0.14, 0.34, 2.8, toon('#2a1514'), [3.07, 0.1, CZ]));
g.add(box(0.03, 1.9, 0.75, lam('#55262a'), [3.005, 1.2, CZ]));
for (const dz of [-0.95, 0.95]) g.add(plane(0.42, 0.5, flat('#2a1d18'), [3.013, 1.62, CZ + dz], [0, Math.PI / 2, 0]));
for (const dz of [-0.75, 0.75]) { g.add(cyl(0.075, 0.075, 0.36, toon('#2a2c3a'), [3.3, 0.12, CZ + dz], [0, 0, Math.PI / 2])); g.add(cyl(0.2, 0.2, 0.05, toon('#8a8fa8'), [3.5, 0.12, CZ + dz], [0, 0, Math.PI / 2])); }
g.add(box(0.22, 0.07, 0.07, toon('#2a2c3a'), [3.25, 0.12, CZ]));
const chain = new THREE.Group(); chain.position.set(3.36, 0.1, CZ);
for (let i = 0; i < 4; i++) chain.add(torus(0.045, 0.013, toon('#3a3c4c'), [0, -0.05 - i * 0.075, 0], [0, i % 2 ? Math.PI / 2 : 0, Math.PI / 2]));
chain.add(cyl(0.02, 0.02, 0.22, toon('#3a3c4c'), [0, -0.42, 0])); g.add(sameId(chain));
// the open door: hinge on the left edge, swings out over the platform. Behind it a warm, empty vestibule.
const hinge = new THREE.Group(); hinge.position.set(0.35, 0.2, ZS + 0.02);
hinge.add(box(0.85, 2.0, 0.04, lam('#5e2a27'), [0.425, 1.0, 0])); hinge.add(box(0.5, 0.55, 0.012, frameM, [0.425, 1.35, 0.026])); hinge.add(plane(0.42, 0.47, winGlass, [0.425, 1.35, 0.034]));
hinge.add(box(0.04, 0.18, 0.05, trimM, [0.76, 0.8, 0.04])); hinge.add(at(sign('3', 0.17, 0.17, { bg: '#c4a56c', fg: '#2a1414', weight: 900, size: 0.8 }), [0.425, 0.48, 0.024]));
g.add(hinge);
const inside = canvasTex(64, 256, x => { const gr = x.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, '#ffd99a'); gr.addColorStop(0.5, '#d9a060'); gr.addColorStop(1, '#7a4a28'); x.fillStyle = gr; x.fillRect(0, 0, 64, 256); });
const inM = new THREE.MeshBasicMaterial({ map: inside });
const vest = new THREE.Group();
vest.add(plane(0.85, 2.0, inM, [0.775, 1.2, -4.38])); vest.add(plane(2.78, 2.0, inM, [0.36, 1.2, -3.0], [0, Math.PI / 2, 0])); vest.add(plane(2.78, 2.0, inM, [1.19, 1.2, -3.0], [0, -Math.PI / 2, 0]));
vest.add(plane(0.85, 2.78, flat('#5a3a22'), [0.775, 0.205, -3.0], [-Math.PI / 2, 0, 0])); vest.add(plane(0.85, 2.78, flat('#f0cc90'), [0.775, 2.195, -3.0], [Math.PI / 2, 0, 0]));
vest.add(box(0.4, 1.7, 0.02, toon('#8a5630'), [0.37, 1.05, -3.6], [0, Math.PI / 2, 0])); vest.add(noOutline(sph(0.06, flat('#fff3d0'), [0.775, 2.1, -2.4])));
g.add(vest);
const doorGlow = glow(2.2, 2.8, '#ffc27a', 0, [0.775, 1.15, -1.45]); fogOff(doorGlow); g.add(doorGlow);
const doorPool = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(1.6, 2.6), new THREE.MeshBasicMaterial({ map: canvasTex(128, 128, x => { const gr = x.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.beginPath(); x.moveTo(30, 0); x.lineTo(98, 0); x.lineTo(128, 128); x.lineTo(0, 128); x.fill(); }), color: '#ffb866', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })));
at(doorPool, [0.775, 0.012, -0.0], [-Math.PI / 2, 0, 0]); g.add(doorPool);

// hanging lamps with a beam of light in the fog
const beamTex = canvasTex(8, 128, x => { const gr = x.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 8, 128); });
function platLamp(k) {
  const L = new THREE.Group(); L.add(cyl(0.012, 0.012, 0.6, toon('#1f2236'), [0, -0.3, 0])); L.add(cyl(0.06, 0.26, 0.18, toon('#2a2d44'), [0, -0.66, 0])); L.add(noOutline(sph(0.085, flat('#ffe4ad'), [0, -0.77, 0])));
  const gl = fogOff(glow(1.7, 1.7, '#ffc27a', 0.55 * k, [0, -0.8, 0])); L.add(gl); billboards.push(gl);
  const beam = noOutline(new THREE.Mesh(new THREE.CylinderGeometry(0.16, 1.35, 3.0, 24, 1, true), new THREE.MeshBasicMaterial({ map: beamTex, color: '#ffbf7a', transparent: true, opacity: 0.075 * k, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false })));
  beam.position.y = -2.32; L.add(beam);
  const pool = fogOff(glow(3.2, 3.2, '#ffb866', 0.32 * k, [0, -3.93, 0], [-Math.PI / 2, 0, 0])); L.add(pool);
  const pl = new THREE.PointLight('#ffbe73', 2.4, 9, 1.6); pl.position.set(0, -0.95, 0); L.add(pl); return L;
}
for (const x of [-15, -9, -3, 3]) g.add(at(platLamp(clamp(1 - Math.abs(x + 3) / 22, 0.45, 1)), [x, 3.95, 1.45]));
// hanging station sign and a clock stuck at one minute to midnight
const signB = sign('', 2.1, 0.62, { bg: '#e6e1d2', lines: ['NEBELBRÜCK', 'Gleis 3'], fg: '#1b1f3a', weight: 800, size: 0.7, border: '#1b1f3a' });
g.add(at(signB, [-6.6, 3.3, 2.5], [0, Math.PI / 2, 0])); for (const dz of [-0.8, 0.8]) g.add(cyl(0.008, 0.008, 0.55, toon('#1f2236'), [-6.6, 3.88, 2.5 + dz]));
const clockTex = canvasTex(256, 256, x => { x.fillStyle = '#f2efe4'; x.beginPath(); x.arc(128, 128, 124, 0, 7); x.fill(); x.strokeStyle = '#141632'; x.lineCap = 'round';
  for (let i = 0; i < 60; i++) { const a = i * Math.PI / 30; x.lineWidth = i % 5 ? 3 : 8; const r0 = i % 5 ? 104 : 92; x.beginPath(); x.moveTo(128 + Math.sin(a) * r0, 128 - Math.cos(a) * r0); x.lineTo(128 + Math.sin(a) * 114, 128 - Math.cos(a) * 114); x.stroke(); }
  const hand = (a, l, w) => { x.lineWidth = w; x.beginPath(); x.moveTo(128, 128); x.lineTo(128 + Math.sin(a) * l, 128 - Math.cos(a) * l); x.stroke(); };
  hand(-0.009, 62, 14); hand(-Math.PI * 2 / 60, 96, 9); x.fillStyle = '#141632'; x.beginPath(); x.arc(128, 128, 10, 0, 7); x.fill(); });
const clock = grp(cyl(0.36, 0.36, 0.1, toon('#1f2236'), [0, 0, 0], [0, 0, Math.PI / 2]), at(new THREE.Mesh(new THREE.CircleGeometry(0.31, 40), new THREE.MeshLambertMaterial({ map: clockTex })), [0.052, 0, 0], [0, Math.PI / 2, 0]));
g.add(at(clock, [-3.2, 3.35, 2.3])); g.add(cyl(0.01, 0.01, 0.4, toon('#1f2236'), [-3.2, 3.85, 2.3]));
// left behind on the run
g.add(at(rbox(0.6, 0.42, 0.2, 0.04, toon('#6a4a32')), [-2.4, 0.21, 1.5], [0, 0.4, 0])); g.add(at(rbox(0.55, 0.18, 0.4, 0.05, toon('#4a5a70')), [-8.2, 0.09, 0.7], [0, 0.7, 0]));
for (const bx of [-4.5, -11]) { g.add(box(1.8, 0.06, 0.45, toon('#4a3a32'), [bx, 0.45, 5.25])); g.add(box(1.8, 0.45, 0.05, toon('#4a3a32'), [bx, 0.78, 5.5])); for (const dx of [-0.8, 0.8]) g.add(box(0.06, 0.45, 0.4, toon('#22263c'), [bx + dx, 0.22, 5.3])); }
// ground fog: two drifting soft layers over the platform, one over the tracks
const fogTex = canvasTex(512, 512, x => { const r = rng(11); for (let i = 0; i < 150; i++) { const cx = r() * 512, cy = r() * 512, rr = 30 + r() * 95, al = 0.14 + r() * 0.12;
  for (const [ox, oy] of [[0, 0], [512, 0], [-512, 0], [0, 512], [0, -512]]) { const gr = x.createRadialGradient(cx + ox, cy + oy, 0, cx + ox, cy + oy, rr); gr.addColorStop(0, `rgba(255,255,255,${al})`); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(cx + ox - rr, cy + oy - rr, rr * 2, rr * 2); } } });
for (const [y, z, d, op, sp] of [[0.2, 2.0, 9, 0.75, 0.012], [0.6, 1.5, 10, 0.42, -0.008], [-0.5, -6.0, 10, 0.75, 0.01]]) {
  const t = fogTex.clone(); t.needsUpdate = true; texRep(t, 3, 1.2);
  const m = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(70, d), new THREE.MeshBasicMaterial({ map: t, color: '#8b94bc', transparent: true, opacity: op, depthWrite: false })));
  at(m, [0, y, z], [-Math.PI / 2, 0, 0]); g.add(m); fogLayers.push([t, sp]);
}
// drifting fog banks at head height, always turned to the camera
const sheetTex = canvasTex(256, 128, x => { const r = rng(5); for (let i = 0; i < 26; i++) { const cx = 30 + r() * 196, cy = 40 + r() * 48, rr = 22 + r() * 40; const gr = x.createRadialGradient(cx, cy, 0, cx, cy, rr); gr.addColorStop(0, 'rgba(255,255,255,0.22)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(cx - rr, cy - rr, rr * 2, rr * 2); } });
const sheets = [];
for (const [x, y, z, w, op] of [[-13, 1.3, 0.4, 9, 0.5], [-8.5, 1.0, 1.8, 8, 0.45], [-4.5, 1.6, -0.2, 7, 0.32], [8, 1.2, -2.5, 9, 0.5], [13, 1.0, -4, 10, 0.55], [-3, 1.3, 3.8, 8, 0.35], [2.5, 0.9, -5.5, 9, 0.5]]) {
  const m = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(w, w * 0.42), new THREE.MeshBasicMaterial({ map: sheetTex, color: '#9aa2c8', transparent: true, opacity: op, depthWrite: false })));
  m.position.set(x, y, z); g.add(m); billboards.push(m); sheets.push([m, x]);
}
const signal = grp(cyl(0.06, 0.08, 4.2, toon('#20222e'), [0, 2.1, 0]), box(0.32, 0.5, 0.18, toon('#1a1c28'), [0, 3.9, 0]), noOutline(sph(0.07, flat('#ff3a2a'), [0, 4.0, 0.1])));
const sgl = fogOff(glow(1.6, 1.6, '#ff3a2a', 0.6, [0, 4.0, 0.12])); signal.add(sgl); billboards.push(sgl); g.add(at(signal, [17, -1.0, -5.0], [0, -Math.PI / 2, 0]));
// the distant explosion: a flare on the horizon behind the kids and an orange rim light
const flare = fogOff(glow(70, 34, '#ff9446', 0, [-62, 7, -1], [0, Math.PI / 2, 0])); g.add(flare);
const flashLight = new THREE.DirectionalLight('#ff8f4a', 0); flashLight.position.set(-10, 4, 1); g.add(flashLight);
const T_X = 1.0;
const flash = t => { const u = t - T_X; if (u < 0) return 0; const a = (u < 0.05 ? u / 0.05 : 1) * Math.exp(-u / 0.5), v = u - 0.3, b = v < 0 ? 0 : (v < 0.04 ? v / 0.04 : 1) * Math.exp(-v / 0.4); return clamp(a + 0.55 * b + 0.07 * Math.exp(-u / 5)) * (1 + 0.12 * noise(t * 30, 3)); };

// ------------------------------------------------------------------------------------------------ people
const paulAv = CAST.paul(), emilAv = CAST.emil(), lenaAv = CAST.lena(), condAv = CAST.schaffner();
const lantern = new THREE.Group(); lantern.position.set(0, -0.13, 0.02);
lantern.add(torus(0.035, 0.008, toon('#2a2c3a'), [0, 0.02, 0])); lantern.add(box(0.1, 0.02, 0.1, toon('#2a2c3a'), [0, -0.03, 0])); lantern.add(box(0.11, 0.02, 0.11, toon('#2a2c3a'), [0, -0.19, 0]));
for (const [dx, dz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) lantern.add(box(0.012, 0.15, 0.012, toon('#2a2c3a'), [dx * 0.045, -0.11, dz * 0.045]));
lantern.add(noOutline(box(0.07, 0.12, 0.07, flat('#ffd58a'), [0, -0.11, 0])));
const lgl = fogOff(glow(0.9, 0.9, '#ffb060', 0.7, [0, -0.11, 0])); lantern.add(lgl); billboards.push(lgl);
const lanternLight = new THREE.PointLight('#ffb062', 2.4, 4.5, 1.4); lanternLight.position.set(0, -0.11, 0.05); lantern.add(lanternLight);
condAv.handL.add(lantern);
condAv.handR.add(noOutline(cyl(0.012, 0.016, 0.07, flat('#c9c9d4'), [0, -0.03, 0.05], [Math.PI / 2, 0, 0])));

// where everyone ends up after the run (x, z, rotation in degrees; 0 = facing +z, 90 = facing +x)
const EMIL_DOOR = [1.35, -0.85], FRONT = [7.5, -3.0];
const HOME = { emil: [1.45, -0.45, 100], paul: [0.15, 0.1, 120], lena: [-0.6, 0.75, 95], schaffner: [-0.9, 2.3, 0] };
HOME.schaffner[2] = towards(HOME.schaffner, HOME.paul) - 30;
const RUN = { emil: { from: [-11.2, 0.25], T: 4.45, ph: 0.0 }, paul: { from: [-12.9, 0.35], T: 4.65, ph: 0.23 }, lena: { from: [-13.9, 0.3], T: 4.95, ph: 0.41 } };
const WALK = { from: [-6.4, 2.9], T0: 11.6, T1: 15.35 };   // the conductor walks out of the fog
const FACE = { emil: (p) => towards(EMIL_DOOR, p), paul: (p) => towards(HOME.paul, p), lena: (p) => towards(HOME.lena, p) };
const PAUL_FACE = FACE.paul(HOME.schaffner);

// Paul's two hand poses for the ticket, and where the ticket is (worked out by posing his figure once)
const PICK = { ...POSES.crouch, hipY: 0.27, lean: 46, aR: [52, 4, 0], eR: 8, aL: [30, 10, 0], eL: 70, head: [30, 0, 0] };
const HOLD = { hipY: 0.83, aL: [42, -14, 0], eL: 98, aR: [42, -14, 0], eR: 98, head: [28, 0, 0] };
function handsWorld(av, home, ry, pose) { av.reset().size(av.P.height).place(home[0], home[1], ry).pose(pose); av.root.updateMatrixWorld(true); const a = new THREE.Vector3(), b = new THREE.Vector3(); av.handL.getWorldPosition(a); av.handR.getWorldPosition(b); return [a, b]; }
const pickHand = handsWorld(paulAv, HOME.paul, PAUL_FACE, PICK)[1];
const TICKET_FLOOR = [pickHand.x, 0.006, pickHand.z];
if (Q.has('debug')) console.error('ticket floor', pickHand.toArray().map(v => v.toFixed(2)).join(' '), 'paul', HOME.paul.join(' '));
const hh = handsWorld(paulAv, HOME.paul, PAUL_FACE, HOLD), TICKET_HELD = [(hh[0].x + hh[1].x) / 2, (hh[0].y + hh[1].y) / 2 + 0.045, (hh[0].z + hh[1].z) / 2];
const T_PICK = 21.0, T_UP = 0.5;
const ticketAt = t => { if (t < T_PICK) return TICKET_FLOOR; const u = easeIO((t - T_PICK) / T_UP); return TICKET_FLOOR.map((v, i) => lerp(v, TICKET_HELD[i], u)); };

// the ticket: his name on it
const ticketTex = canvasTex(560, 330, x => {
  x.fillStyle = '#ece2c2'; x.fillRect(0, 0, 560, 330); x.strokeStyle = '#5a3a2a'; x.lineWidth = 8; x.strokeRect(14, 14, 532, 302); x.lineWidth = 2; x.strokeRect(26, 26, 508, 278);
  x.fillStyle = '#5a3a2a'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.font = `800 40px ${FONT}`; x.fillText('FAHRKARTE', 280, 66);
  x.font = `900 128px ${FONT}`; x.fillStyle = '#1b1f3a'; x.fillText('PAUL', 280, 172);
  x.font = `700 30px ${FONT}`; x.fillStyle = '#5a3a2a'; x.fillText('EINFACHE FAHRT · GLEIS 3', 280, 268);
  x.fillStyle = '#ece2c2'; x.beginPath(); x.arc(500, 66, 14, 0, 7); x.fill(); x.strokeStyle = '#5a3a2a'; x.beginPath(); x.arc(500, 66, 14, 0, 7); x.stroke();
  x.save(); x.translate(470, 250); x.rotate(-0.25); x.strokeStyle = 'rgba(190,40,40,0.75)'; x.lineWidth = 5; x.beginPath(); x.arc(0, 0, 44, 0, 7); x.stroke(); x.fillStyle = 'rgba(190,40,40,0.8)'; x.font = `800 26px ${FONT}`; x.fillText('23:59', 0, 2); x.restore();
});
const ticket = new THREE.Mesh(new THREE.PlaneGeometry(0.19, 0.112), new THREE.MeshLambertMaterial({ map: ticketTex, emissive: '#ffffff', emissiveMap: ticketTex, emissiveIntensity: 0.32, side: THREE.DoubleSide }));
g.add(ticket);

const breathPeriod = (n, t) => n === 'paul' && t > 27.2 ? 0.46 : t < 9 ? 0.62 : t < 17 ? 0.9 : 0.7;
const AV = { paul: paulAv, emil: emilAv, lena: lenaAv };
const puffs = breathPuffs(g, AV, breathPeriod, (n, t) => t > RUN[n].T + 0.2 && t < 29.6);
// the run in, and the conductor's walk out of the fog
const MV = mover();
for (const n of ['paul', 'emil', 'lena']) MV.add(AV[n], n, { from: RUN[n].from, to: HOME[n].slice(0, 2), T0: 0, T1: RUN[n].T, endRy: HOME[n][2], ph: RUN[n].ph });
MV.add(condAv, 'schaffner', { from: WALK.from, to: HOME.schaffner.slice(0, 2), T0: WALK.T0, T1: WALK.T1, endRy: HOME.schaffner[2], mode: 'walk' });

// ------------------------------------------------------------------------------------------------ set
const v3 = new THREE.Vector3(), v4 = new THREE.Vector3(), q1 = new THREE.Quaternion();
const station = makeSet(g, {
  mood: 'night', moodOverride: { bg: '#1a1f38', amb: ['#4a55aa', 1.25], hemi: ['#5d68c8', '#141634', 0.85], key: ['#9fb0ff', 0.75, [-3, 6, 4]], spill: ['#ffbd72', 4.6] },
  pov: PA, look: [-8, 1.0, -0.4], spillAt: [0.78, 1.25, -1.35],
  targets: {
    runView: [-6, 1.1, -0.25], door: [0.78, 1.15, -1.6], groupA: [0.0, 0.95, 0.2], front: [7.5, 0.4, -3.0],
    trackPan: t => { const u = smooth((t - 10.3) / 3.3); return [lerp(3.2, 8.6, u), lerp(0.1, -0.55, u), -3.0]; },
    groupF: [-0.5, 1.0, 0.75], kidsJ: [-0.25, 1.0, 0.4], doorPaul: [0.45, 1.05, -0.9],
    ticketT: t => { const p = ticketAt(t), lift = 1 - smooth((t - T_PICK) / T_UP); return [p[0], p[1] + 0.58 * lift, p[2]]; },
    ticketLook: t => ticketAt(t),
    H_paul: [0.15, 1.41, 0.1], H_emil: [1.35, 1.44, -0.85], H_lena: [-0.6, 1.38, 0.75], H_schaffner: [-0.9, 1.66, 2.3], H_emilFwd: [3.6, 1.3, -1.0], H_whistle: [0.3, 1.4, 1.2],
  },
  onUpdate(v, t, S) {
    // explosion
    const f = flash(t); flashLight.intensity = 3.4 * f; flare.material.opacity = 0.95 * f; const fc = FOG.clone().lerp(FLASH, 0.8 * f); S.scene.fog.color.copy(fc); S.bg = fc.getHex();
    // door + warm light
    const d = v.door ?? 0; hinge.rotation.y = -d * rad(98); const sp = v.spill ?? 0; vest.visible = d > 0.01; doorGlow.material.opacity = 0.42 * sp; doorPool.material.opacity = 0.5 * sp;
    // kids running in, the conductor walking in; cold breath
    MV.update(t); puffs(t, camPt(t));
    // the ticket: on the floor, then in Paul's hands
    if (t < T_PICK) { ticket.position.set(...TICKET_FLOOR); ticket.rotation.set(-Math.PI / 2, 0, rad(PAUL_FACE - 180) + 0.3); }
    else { paulAv.root.updateMatrixWorld(true); paulAv.handL.getWorldPosition(v3); paulAv.handR.getWorldPosition(v4); const u = smooth((t - T_PICK) / 0.12);
      const w2 = smooth((t - T_PICK) / T_UP); v3.add(v4).multiplyScalar(0.5); const tp = [lerp(v4.x, v3.x, w2), lerp(v4.y, v3.y, w2) + 0.045, lerp(v4.z, v3.z, w2)]; const fl = TICKET_FLOOR;
      ticket.position.set(lerp(fl[0], tp[0], u), lerp(fl[1], tp[1], u), lerp(fl[2], tp[2], u));
      const w = smooth((t - T_PICK) / T_UP); ticket.rotation.set(-Math.PI / 2, 0, rad(PAUL_FACE - 180) + 0.3); q1.copy(ticket.quaternion); ticket.lookAt(...C5); ticket.rotateZ(-0.12); ticket.quaternion.slerpQuaternions(q1, ticket.quaternion.clone(), w); }
    // lantern sway, coupling chain, fog drift, glows facing the camera
    lantern.rotation.z = rad(6) * noise(t * 0.9, 4); lantern.rotation.x = rad(5) * noise(t * 0.8, 6); lanternLight.intensity = 2.4 * (0.9 + 0.1 * noise(t * 9, 2));
    chain.rotation.x = rad(7) * Math.sin(t * 1.4) + rad(2) * noise(t, 9);
    for (const [tx, s] of fogLayers) tx.offset.set(t * s, t * s * 0.3);
    for (const [m, x0] of sheets) m.position.x = x0 + 0.25 * t;
    const cp = camPt(t); for (const b of billboards) b.lookAt(cp[0], cp[1], cp[2]);
  },
});
station.scene.fog = new THREE.Fog(FOG.clone(), 2.2, 21);

// ------------------------------------------------------------------------------------------------ story
const S = story({
  set: station, lead: 0, tail: 0, shake: 0.8, vignette: 0.7, audioMood: 'tension',
  badge: { title: 'FOLGE 1', label: 'Der Zug ohne Morgen –', value: 'DER LETZTE ZUG', until: 3.6 },
  speakers: {
    emil:      { color: '#ffd84a', voice: 'Liam' },
    lena:      { color: '#7fe3ff', voice: 'Elli' },
    schaffner: { color: '#ff9ad0', voice: 'Clyde' },
    paul:      { color: '#ffffff', voice: 'Harry' },
  },
  pov: { phone: false },
  vars: { door: 0, spill: 0 },
});
S.cast('paul', paulAv, { at: HOME.paul, pose: 'stand', face: 'scared' });
S.cast('emil', emilAv, { at: HOME.emil, pose: 'stand', face: 'scared' });
S.cast('lena', lenaAv, { at: HOME.lena, pose: 'stand', face: 'worried' });
S.cast('schaffner', condAv, { at: HOME.schaffner, pose: 'stand', face: 'neutral', hide: true });

// timing: holds fill the gaps so every beat lands on its mark (line lengths come from the real voices once they exist)
const Z = sequencer(S, TM), hold = Z.hold, say = Z.say, abs = Z.abs;
const POINT_L = { hipY: 0.83, lean: 4, aL: [30, 80, 0], eL: 6, aR: [14, 10, 0], eR: 30 };
const REACH = { hipY: 0.83, lean: 4, aR: [38, 22, 0], eR: 34 };
const HOLD_UP = { ...HOLD, head: [4, 0, 0] };
const turn = (n, p, o = {}) => ({ at: [...(n === 'emil' ? EMIL_DOOR : HOME[n].slice(0, 2)), FACE[n](p)], dur: 0.32, ...o });

// 00:00–00:08 · they run across the foggy platform, a distant explosion, the train opens a door. EMIL: "Da! Wir müssen rein!"
hold(2.85, { look: 'runView', zoom: 54, push: 0.02, sfx: [...MV.steps(camPt), ['siren', 0, 0.8], ['explosion', T_X + 0.22]] });
hold(3.95, { look: 'door', zoom: 46, pov: PB, povDur: 1.1, camDur: 0.55, vars: { door: [1, 0.85, 0.1], spill: [1, 0.7, 0.2] }, sfx: [['latch', 0.08], ['creak', 0.2, 0.8], ['warm', 0.3]] });
say('emil', 'Da! | Wir müssen rein!', { look: 'emil', zoom: 36, camAt: -0.12, headroom: 0.15, do: { emil: [{ pose: POINT_L, face: 'shock', look: 'H_emilFwd', t: -0.1, dur: 0.22 }] } });
hold(8.0, { look: 'groupA', zoom: 60, sfx: [['pant', 0.05, 1]], do: {
  emil: [{ pose: 'stand', face: 'scared', look: 'door', t: abs(5.75) }, { at: [...EMIL_DOOR, 200], t: abs(6.3), dur: 0.7 }],
  paul: [{ look: 'door', t: abs(4.9) }], lena: [{ look: 'front', face: 'worried', t: abs(6.6), dur: 0.6 }] } });

// 00:08–00:20 · close on Lena, then the empty tracks in front of the car. LENA: "Wartet. Der hat keine Lok." The conductor steps behind them.
hold(8.45, { look: 'lena', zoom: 40, pov: PE, povDur: 0.75, camDur: 0.45, headroom: 0.1, sfx: [['pant_soft', 0]] });
say('lena', 'Wartet.', { do: { lena: { pose: REACH, look: 'H_emil', face: 'worried', t: -0.15, dur: 0.3 },
  emil: turn('emil', HOME.lena, { look: 'H_lena', t: 0.25 }), paul: turn('paul', HOME.lena, { look: 'H_lena', t: 0.35 }) } });
hold(9.75, { do: { lena: [{ look: 'front', t: 0.2, dur: 0.5 }, { pose: 'stand', at: [...HOME.lena.slice(0, 2), 105], t: 0.3, dur: 0.5 }] } });
say('lena', 'Der hat | keine Lok.', { look: 'trackPan', zoom: 50, pov: PF, povDur: 0.9, camDur: 0.6, camAt: -0.25, push: 0.02,
  do: { emil: turn('emil', FRONT, { look: 'front', t: 0.35, dur: 0.45 }), paul: turn('paul', FRONT, { look: 'front', t: 0.5, dur: 0.45 }) } });
hold(13.75, { sfx: [['wind', 0], ['chain', 0.6]], do: { schaffner: { hide: false, t: abs(WALK.T0), dur: 0 } } });
hold(15.55, { look: 'groupF', zoom: 66, sfx: [] });
say('schaffner', 'Heute braucht er keine.', { look: 'schaffner', zoom: 15, camAt: -0.15, headroom: 0.07, push: 0.03,
  do: { schaffner: { face: 'sus', look: 'H_paul', t: -0.1 },
        emil: turn('emil', HOME.schaffner, { look: 'H_schaffner', face: 'shock', tremble: 0.6, t: 0.35 }),
        paul: turn('paul', HOME.schaffner, { look: 'H_schaffner', face: 'shock', tremble: 0.5, t: 0.25 }),
        lena: turn('lena', HOME.schaffner, { look: 'H_schaffner', face: 'shock', tremble: 0.6, t: 0.42 }) } });
hold(18.6, { sfx: [['sting', 0.0, 0.55]] });
hold(20.0, { look: 'kidsJ', zoom: 60, pov: C5, povDur: 0.8, camDur: 0.5, sfx: [['pant', 0.2, 0.7]], do: { emil: { tremble: 1, t: 0.5 }, lena: { pose: 'gasp', t: 0.4, dur: 0.3 } } });

// 00:20–00:30 · Paul picks a ticket off the ground: his name. PAUL: "Woher kennt der mich?" Whistle. Doors slam. Cut to his scared face, black at 00:30.
hold(23.25, { look: 'ticketT', zoom: 36, camDur: 0.4, punch: { at: abs(T_PICK + T_UP + 0.1), zoom: 12, dur: 0.55 }, push: 0.02,
  do: { paul: [{ look: 'ticketLook', face: 'worried', t: 0.15, dur: 0.4 }, { pose: PICK, t: abs(T_PICK - 0.5), dur: 0.5 }, { pose: HOLD, t: abs(T_PICK), dur: T_UP }] },
  sfx: [['paper', abs(T_PICK)], ['heart', abs(22.0), 0.8], ['heart', abs(22.85), 0.9]] });
say('paul', 'Woher kennt der mich?', { look: 'paul', zoom: 32, camAt: -0.15, headroom: 0.1, do: { paul: { pose: HOLD_UP, look: 'H_schaffner', face: 'scared', t: 'p0', dur: 0.3 } } });
hold(24.85, {});
hold(26.2, { look: 'schaffner', zoom: 50, headroom: 0.12, do: { schaffner: { pose: 'stand+shh', look: 'H_whistle', t: 0.08, dur: 0.28 } }, sfx: [['whistle', 0.38]] });
hold(27.3, { look: 'doorPaul', zoom: 50, vars: { door: [0, 0.14, 0.2], spill: [0, 0.12, 0.26] }, sfx: [['slam', 0.3], ['slam_far', 0.55], ['slam_far', 0.82, 0.7], ['clank', 1.0]],
  do: { schaffner: { pose: 'stand', t: 0.2 }, paul: { look: 'door', face: 'shock', tremble: 1, t: 0.33, dur: 0.15 }, emil: { look: 'door', t: 0.35, dur: 0.15 }, lena: { look: 'door', pose: 'stand', t: 0.4, dur: 0.2 } } });
hold(29.6, { look: 'paul', zoom: 19, cut: true, push: 0.03, headroom: 0.05, do: { paul: { look: 'H_schaffner', face: 'shock', tremble: 1, t: 0 } }, sfx: [['gasp', 0.02], ['pant_fast', 0.35]] });
Z.hold(30.0, { overlay: (ctx, w, h) => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h); } });
S.start();
