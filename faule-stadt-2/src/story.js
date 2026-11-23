// Finale: "In dieser Stadt hat nur einer einen Wecker gestellt."  Erzähler in der dritten Person, Ronaldo stellt den Täter., deutsch, Cliffhanger-Ende "2?".
// Keywords marked with * show as yellow captions. // = 0.6 s silent hold, /// = 1.0 s.
import * as THREE from 'three';
import { start, shot, frame, W, H } from './core.js';
import { makeAvatar } from './avatar.js';
import { SETS, TEX, floor, building, lampPost, tree, bush, bench, sky, room, sofa, desk, chair, bookStack, windowPane, trashCan, bunting } from './sets.js';
import { makeEmote, makePuff, makeSparkles } from './fx.js';
import { skyDome, hills, drone, handheld, follow, car } from './town.js';
import { mat, glow, box, at, grp, sign, rng, clamp, remap, lerp, E, PRE } from './util.js';

// ───────────── props + effects made for this story
function alarmClock(text, color = '#d23a3a') {
  const g = grp(at(box(2.4, 2, 1.2, color, 0.3), 0, 1.25, 0));
  for (const s of [-1, 1]) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.5, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2), mat('#d9d9de')); b.position.set(s * 0.8, 2.2, 0); g.add(b); g.add(at(box(0.18, 0.5, 0.18, '#333'), s * 0.8, 0.12, 0)); }
  g.add(at(box(0.25, 0.4, 0.25, '#333'), 0, 2.4, 0));
  g.add(at(sign(text, 1.9, 0.95, { bg: '#0c0c0e', fg: '#ff3a2a', glowing: true, weight: 900 }), 0, 1.25, 0.62));
  return g;
}
function makeFire(parent, x, y, z, width = 14) {
  const g = grp(), r = rng(7), flames = [], smoke = [];
  const mats = [glow('#ff4a12', 1.15), glow('#ff8a1a', 1.25), glow('#ffd34a', 1.35)];
  for (let i = 0; i < 24; i++) { const m = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 6), mats[i % 3]); m.userData = { x: (r() - 0.5) * width, z: (r() - 0.5) * 3, y: r() * 7, ph: r() * 6, sp: 5 + r() * 6, w: 0.6 + r() * 0.8, h: 2 + r() * 3 }; g.add(m); flames.push(m); }
  const sm = new THREE.MeshLambertMaterial({ color: '#2b2a2e', transparent: true, opacity: 0.55, depthWrite: false });
  for (let i = 0; i < 16; i++) { const s = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 8), sm); s.userData = { x: (r() - 0.5) * width * 0.8, ph: r(), s: 1.6 + r() * 2 }; g.add(s); smoke.push(s); }
  const L = new THREE.PointLight('#ff7a2a', 0, 45, 1.8); L.position.set(0, 6, 4); g.add(L);
  g.position.set(x, y, z); parent.add(g);
  return {
    set(level, t, smokeLevel = level) {
      g.visible = level > 0.01 || smokeLevel > 0.01;
      for (const f of flames) { const u = f.userData, fl = 0.75 + 0.35 * Math.sin(t * u.sp + u.ph) + 0.12 * Math.sin(t * 23 + u.ph * 3); f.visible = level > 0.01; f.scale.set(u.w * level, u.h * level * fl, u.w * level); f.position.set(u.x * (0.5 + 0.5 * level), u.y * level + u.h * level * fl / 2, u.z); }
      for (const s of smoke) { const u = s.userData, k = (t * 0.25 + u.ph) % 1; s.visible = smokeLevel > 0.01; s.position.set(u.x + Math.sin(k * 5 + u.ph * 9) * 2, 6 + k * 26, -1 - k * 3); s.scale.setScalar(u.s * (0.6 + k * 1.6) * Math.max(smokeLevel, 0.01)); }
      L.intensity = 260 * level * (0.85 + 0.15 * Math.sin(t * 17));
    },
  };
}
function makeSpray(parent) {
  const g = grp(), m = new THREE.MeshBasicMaterial({ color: '#bfe6ff', transparent: true, opacity: 0.9 }), drops = [];
  for (let i = 0; i < 40; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), m); g.add(d); drops.push(d); }
  g.visible = false; parent.add(g); PRE.push(() => { g.visible = false; });
  return { at(t, a, b, hgt = 2.5) { g.visible = true; drops.forEach((d, i) => { const k = (t * 1.8 + i / drops.length) % 1, j = Math.sin(i * 12.9) * 0.4; d.position.set(lerp(a[0], b[0], k) + j, lerp(a[1], b[1], k) + Math.sin(k * Math.PI) * hgt, lerp(a[2], b[2], k) + j * 0.5); d.scale.setScalar(0.6 + k * 1.4); }); } };
}
// windows: one shared dark/warm material, ranked so a shot can switch the whole town's lights on progressively
function nightWindows(group, seed = 3) {
  const r = rng(seed), dark = mat('#1b2238'), warm = glow('#ffd98a', 1.5), list = [];
  group.traverse(o => { if (o.isMesh && o.material && o.material.isMeshBasicMaterial && o.geometry.type === 'PlaneGeometry' && o.material.color.b > 1.0 && o.material.color.r < 1.0) { o.userData.rank = r(); list.push(o); } });
  let cur = -1; const set = f => { if (f === cur) return; cur = f; list.forEach(o => { o.material = o.userData.rank < f ? warm : dark; }); }; set(0.1); return set;
}
function makeConfetti(parent, n = 90, seed = 4) {
  const g = grp(), r = rng(seed), cs = ['#ff5c8a', '#ffd34a', '#4ad1ff', '#7dff8a', '#c18cff', '#ff8a3a'], ps = [];
  for (let i = 0; i < n; i++) { const p = box(0.35, 0.05, 0.22, glow(cs[i % cs.length], 1.05)); p.castShadow = false; p.userData = { x: (r() - 0.5) * 30, z: (r() - 0.5) * 14, ph: r(), sp: 0.12 + r() * 0.1, rot: r() * 6 }; g.add(p); ps.push(p); }
  g.visible = false; parent.add(g); PRE.push(() => { g.visible = false; });
  return { at(t, cx, cz) { g.visible = true; for (const p of ps) { const u = p.userData, k = (t * u.sp + u.ph) % 1; p.position.set(cx + u.x + Math.sin(t * 2 + u.rot) * 0.6, 16 - k * 16, cz + u.z); p.rotation.set(t * 3 + u.rot, t * 2, u.rot); } } };
}

// ───────────── sets
const COLORS = ['#f2c7d0', '#bfe3ff', '#fff0b8', '#d6f2c4', '#e4d0ff', '#ffd2a8', '#c9f0ec', '#ffc2c2'];
function city(time) {
  const night = time === 'night', skyA = night ? skyDome('night') : sky(), skyB = skyDome('sunset'), g = grp(skyA, skyB, hills(night ? '#1d3320' : '#6fbf5a', -220));
  g.add(at(floor(460, 460, TEX.grass(night ? '#2b4a26' : '#5cb84a'), 6), 0, -0.03, 0));
  g.add(at(floor(460, 8, TEX.road(), 6), 0, 0.01, 0));
  for (const z of [-5.5, 5.5]) g.add(at(floor(460, 3.4, TEX.concrete(night ? '#8a8c92' : '#d9d4cc'), 4), 0, 0.02, z));
  for (const x of [-48, 48]) g.add(at(floor(8, 460, TEX.road(), 6), x, 0.012, 0));
  for (let i = -24; i <= 24; i++) g.add(at(box(3, 0.04, 0.4, '#f2f2f2'), i * 9, 0.04, 0));
  g.add(at(floor(30, 10, TEX.concrete(night ? '#9a9890' : '#e6dcc6'), 3), 0, 0.016, -11));
  let k = 0;
  for (const [z, rot] of [[-17, 0], [17, Math.PI], [-44, 0], [-71, 0], [-98, 0]]) for (let x = -110; x <= 110; x += 17) {
    if (Math.abs(Math.abs(x) - 48) < 8) continue; if (z === -17 && Math.abs(x) < 14) continue; if (z === 17 && Math.abs(x) < 36) continue; k++;
    g.add(at(building(14, 10 + (k % 3) * 4, 10, COLORS[k % COLORS.length], { windows: [3, 2], doorColor: COLORS[(k + 3) % COLORS.length] }), x, 0, z, rot));
  }
  g.add(at(building(20, 13, 12, '#f8c5c7', { sign: 'BÄCKEREI', signFg: '#c2264a', awning: '#e84b6a', windows: [3, 2], doorColor: '#e84b6a' }), 0, 0, -20));
  g.add(at(sign('CAFÉ', 8, 1.6, { bg: '#ffffff', fg: '#7a4a2a', border: '#7a4a2a' }), 26, 8.6, -11.4)); for (let i = 0; i < 7; i++) g.add(at(box(2, 0.3, 2.4, i % 2 ? '#ffffff' : '#7a4a2a'), 26 - 6 + i * 2, 7.2, -10.8));
  for (const x of [-30, -12, 12, 30]) g.add(at(lampPost(10), x, 0, 7.4));
  g.add(at(tree(9), -22, 0, 7.5), at(tree(9), 22, 0, 7.5), at(bench(), -8, 0, -8), at(bench(), 8, 0, -8), at(trashCan(), 12, 0, -7.5));
  // the door that opens (house at x=-25) and the alarm clock on its window ledge
  g.add(at(box(3, 6.2, 0.05, '#070709'), -25, 3.1, -11.7)); const hinge = grp(at(box(3, 6.2, 0.25, '#2f8fe6'), 1.5, 3.1, 0)); g.add(at(hinge, -26.5, 0, -11.5));
  const ledgeClock = at(alarmClock('03:00'), -20.3, 8.1, -11.3); ledgeClock.scale.setScalar(0.5); g.add(ledgeClock, at(box(3, 0.3, 0.8, '#ffffff'), -20.3, 7.95, -11.5));
  let setLit = () => { };
  if (night) { setLit = nightWindows(g); for (const x of [-30, 12]) { const L = new THREE.PointLight('#ffd9a0', 160, 24, 2); L.position.set(x, 10.2, 7.4); g.add(L); } }
  const ash = grp(at(box(9, 0.25, 5, '#2a2626', 0.2), 0, 0.12, -9)); const clockA = at(alarmClock('03:00'), 0.6, 0.1, -7.6); clockA.rotation.x = -0.25; clockA.scale.setScalar(0.55); ash.add(clockA); g.add(ash);
  const flags = at(bunting(40, ['#e94b5f', '#f2b01e', '#2f9e55', '#3d6fe0', '#8a4fd0']), 0, 11, -6); g.add(flags);
  const faceL = new THREE.PointLight('#fff6d0', 0, 20, 2); g.add(faceL);
  const set = { group: g, light: night ? 'townNight' : 'outdoor', setLit, hinge, ledgeClock, ash, flags, faceL, skyA, skyB,
    reset() { setLit(0.1); hinge.rotation.y = 0; ledgeClock.rotation.z = 0; ash.visible = false; flags.visible = !night; faceL.intensity = 0; skyA.visible = true; skyB.visible = false; } };
  return set;
}
const cityNight = city('night'), cityDay = city('day');
const bedNight = (() => {
  const g = room({ floorTex: TEX.wood('#6a4428'), tile: 6, wallColor: '#2e3a66', trim: '#222b4a', trimY: 0.6, w: 30, d: 22, h: 12, lights: 0, ceiling: '#141a2c' });
  g.add(at(windowPane(5, 4, '#1a2340'), 5, 7, -5.85), at(box(4.6, 0.7, 8, '#4a3220'), -8, 0.35, -1.2), at(box(4.6, 1.2, 8, '#d9d4cc', 0.15), -8, 1.3, -1.2), at(box(4.7, 0.5, 5.4, '#d8322a', 0.2), -8, 2.05, 0.2), at(box(3.2, 0.6, 1.6, '#ffffff', 0.25), -8, 2.2, -3.9), at(box(2.6, 2.2, 2, '#4a3220'), -3.2, 1.1, -3.8));
  g.add(at(alarmClock('02:59'), -3.2, 2.2, -3.6)); const L = new THREE.PointLight('#9fb6ff', 120, 30, 2); L.position.set(4, 8, 2); g.add(L);
  return { group: g, light: 'roomNight' };
})();
const bedDay = SETS.bedroom({ poster: 'NIE\nAUFGEBEN', bed: '#d8322a' });
const clock12 = at(alarmClock('12:00', '#2f7de1'), -2.5, 2.2, -3.4); bedDay.group.add(at(box(2.6, 2.2, 2, '#b9783f'), -2.5, 1.1, -3.6), clock12);
const station = room({ floorTex: TEX.concrete('#9a9a9a'), tile: 6, wallColor: '#b8342c', trim: '#f2c230', trimY: 4, w: 44, d: 28, h: 14, lights: 2 });
station.add(at(sign('FEUERWACHE', 14, 2.4, { bg: '#f4f4f4', fg: '#b8342c', border: '#b8342c', weight: 900 }), 0, 11, -5.85));
const truck = car('#d62828'); truck.scale.setScalar(1.6); station.add(at(truck, 15, 0, -1, -0.3));
const hammocks = [];
for (const [x, z] of [[-10, 0], [-2, 0], [6, 0]]) { const h = grp(at(box(0.4, 6, 0.4, '#4a3220'), 0, 3, -4.5), at(box(0.4, 6, 0.4, '#4a3220'), 0, 3, 4.5)); for (let i = 0; i < 9; i++) { const k = i / 8 - 0.5; h.add(at(box(2.2, 0.2, 1.05, i % 2 ? '#f2c230' : '#2f7de1'), 0, 3.2 - Math.cos(k * Math.PI) * 1.2, k * 8.4)); } station.add(at(h, x, 0, z)); hammocks.push([x, z]); }
const fstation = { group: station, light: 'indoor' };

// ───────────── cast (same looks as the first video; one copy per set)
const ME = { seed: 3, skin: 'light', hair: 'spiky', hairColor: '#1d1410', top: 'hoodie', topColor: '#d8322a', sleeves: 'long', bottom: 'jeans', bottomColor: '#2c3550', shoe: '#f2f2f2', face: 'smile' };
const POST = { seed: 21, skin: 'tan', hair: 'short', top: 'shirt', topColor: '#f6c915', sleeves: 'short', bottom: 'slacks', bottomColor: '#24305e', cap: '#f6c915', face: 'sleepy' };
const DAD = { seed: 31, skin: 'light', hair: 'messy', hairColor: '#4a2f1d', top: 'tee', topColor: '#f2f2f2', sleeves: 'short', bottom: 'joggers', bottomColor: '#6b6f78', face: 'sleepy' };
const TEACH = { seed: 41, skin: 'fair', hair: 'short', hairColor: '#9a9aa0', glasses: true, top: 'suit', topColor: '#7a5a3a', tie: '#2f7de1', sleeves: 'long', bottom: 'slacks', bottomColor: '#4a3a2a', face: 'sleepy' };
const FF = { skin: 'light', hair: 'short', top: 'stripes', topColor: '#2a2f45', stripe: '#f2c230', sleeves: 'long', bottom: 'slacks', bottomColor: '#2a2f45', cap: '#d62828', face: 'sleepy' };
const CHIEF = { ...FF, seed: 80, skin: 'fair', cap: '#f4f4f4', face: 'serious' };
const FOLK = [{ hair: 'bob', hairColor: '#c9c9c9', top: 'cardigan', topColor: '#9b6fd0', skin: 'fair' }, { hair: 'bald', top: 'vest', topColor: '#3f9b3f', skin: 'deep' }, { hair: 'long', hairColor: '#6a3a1a', top: 'sweater', topColor: '#e8632b', skin: 'light' }, { hair: 'curly', hairColor: '#2b1b14', top: 'tee', topColor: '#2e9e59', skin: 'brown' }, { hair: 'ponytail', hairColor: '#c98a3a', top: 'tee', topColor: '#e84b6a', skin: 'fair' }, { hair: 'afro', hairColor: '#1a1210', top: 'hoodie', topColor: '#2f7de1', skin: 'dark' }];
const add = (s, o) => { const a = makeAvatar(o); s.group.add(a.root); return a; };
const chiefOf = s => { const a = add(s, CHIEF); a.head.add(at(box(0.62, 0.13, 0.08, '#d9d9de'), 0, 0.5, 0.64)); return a; };
const N = { me: add(cityNight, ME), chief: chiefOf(cityNight), post: add(cityNight, POST), dad: add(cityNight, DAD), teach: add(cityNight, TEACH), folk: FOLK.map((o, i) => add(cityNight, { seed: 60 + i, sleeves: 'long', bottom: 'slacks', bottomColor: '#3a3d48', ...o })) };
const D = { me: add(cityDay, ME), chief: chiefOf(cityDay), post: add(cityDay, POST), dad: add(cityDay, DAD), teach: add(cityDay, TEACH), folk: FOLK.map((o, i) => add(cityDay, { seed: 60 + i, sleeves: 'long', bottom: 'slacks', bottomColor: '#3a3d48', ...o })) };
const meBedN = add(bedNight, ME), meBedD = add(bedDay, ME);
const firemen = [0, 1, 2].map(i => { const a = makeAvatar({ ...FF, seed: 70 + i, skin: ['light', 'tan', 'brown'][i] }); station.add(a.root); return a; });
const shadow = add(cityNight, { seed: 99, skin: '#121216', hair: 'short', hairColor: '#0b0b0d', top: 'hoodie', topColor: '#121216', sleeves: 'long', bottom: 'plain', bottomColor: '#121216', shoe: '#121216', sole: '#121216', face: 'blank' });
for (const s of [-1, 1]) shadow.head.add(at(box(0.2, 0.09, 0.05, glow('#ff2a2a', 3)), s * 0.24, 0.68, 0.64));
// match in the shadow's hand, flashlight + beam in Ronaldo's
const match = grp(at(box(0.08, 0.9, 0.08, '#e8d5b0'), 0, -0.45, 0), at(new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.5, 8), glow('#ffb03a', 2.2)), 0, -1.1, 0)); match.rotation.x = Math.PI; const matchL = new THREE.PointLight('#ff9a3a', 30, 10, 2); matchL.position.y = -1; match.add(matchL); shadow.handR.add(match);
const torch = grp(at(box(0.45, 1.1, 0.45, '#2a2a30', 0.1), 0, -0.3, 0)); const beam = new THREE.Mesh(new THREE.ConeGeometry(1.8, 10, 20, 1, true), new THREE.MeshBasicMaterial({ color: '#fff3b0', transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide })); beam.position.y = -5.4; torch.add(beam); N.me.handR.add(torch);
PRE.push(() => { match.visible = false; torch.visible = false; });
const zzzF = makeEmote(station, 'zzz', '#2f7de1'), zzzMe = makeEmote(bedDay.group, 'zzz', '#2f7de1'), exMe = makeEmote(cityNight.group, '!', '#ff3b30'), exChief = makeEmote(cityNight.group, '!!', '#ff3b30');
const confetti = makeConfetti(cityDay.group), spark = makeSparkles(cityDay.group, 5);
const lie = (a, x, y, z) => { a.reset().place(x, z, 0, y); a.root.rotation.x = -Math.PI / 2 + 0.22; a.pose({ aL: [10, 20], aR: [10, 20] }); return a; };
const crouch = (a, x, z, ry = 0) => a.reset().place(x, z, ry, -1.3).pose({ lL: 70, lR: 70, aL: [40, 10], aR: [40, 10] });
const CHX = 24, CHZ = -10, RX = 17.5;   // chief at the café door, Ronaldo facing him
// the crowd around the chief: [x, z, ry]
const RING = [[CHX - 3, CHZ + 2.2, 2.3], [CHX + 3, CHZ + 2.2, -2.3], [CHX - 4.5, CHZ - 0.5, 1.6], [CHX + 4.5, CHZ - 0.5, -1.6], [CHX - 2, CHZ + 5, 2.8], [CHX + 2, CHZ + 5, -2.8], [CHX, CHZ + 6.5, Math.PI], [CHX - 5.5, CHZ + 4, 2.2], [CHX + 5.5, CHZ + 4, -2.2]];
function crowd(S, c, faceOf, poseOf) { const all = [S.post, S.teach, S.dad, ...S.folk]; all.forEach((a, i) => { const [x, z, ry] = RING[i]; a.reset().place(x, z, ry).pose(poseOf ? poseOf(i) : 'reach').setFace(faceOf ? faceOf(i) : 'angry').idle(c.t + i); }); }

// ───────────── shots
async function build() {
  // HOOK
  shot({ line: 'In dieser Stadt hat nur *einer', set: cityNight, sfx: [['whoosh', 0, 0.8], ['drone', 0, 0.8]], cam: drone([0, 2, -10], { h: 50, back: 56, drift: [-8, -6, -10], fov: 52 }) });
  shot({ line: 'einen *Wecker gestellt.', set: cityNight, sfx: [['tick', 'wecker', 1]], cam: { pos: [1.0, 1.9, -5.6], look: [0.6, 0.8, -7.6], fov: 45, blur: 0.8, push: 0.12 }, act(lt, c) { cityNight.ash.visible = true; } });
  shot({ line: 'Und heute Nacht findet *Ronaldo heraus, *wer. //', set: cityNight, sfx: [['hit', 'wer', 0.9]], cam: frame(4, 2, { size: 'close', side: 10, push: 0.1 }),
    act(lt, c) { N.me.reset().place(4, 2, 0).setFace(lt > c.w('wer') ? 'angry' : 'serious').idle(c.t, 0.4); } });
  // THE TRAP
  shot({ line: 'In der nächsten Nacht stellte Ronaldo seinen eigenen *Wecker', set: bedNight, cam: frame(-5.4, -2.2, { size: 'medium', side: 35 }),
    act(lt, c) { meBedN.reset().place(-5.4, -2.2, 0.9).pose({ aR: [62, -12] }).setFace('serious').idle(c.t, 0.4); } });
  shot({ line: 'auf zwei Uhr *neunundfünfzig.', set: bedNight, sfx: [['tick', 'neunundfünfzig', 1]], cam: { pos: [-2.4, 4.2, 2.4], look: [-3.2, 3.3, -3.6], fov: 50, blur: 0.7, push: 0.12 } });
  shot({ line: 'Er versteckte sich hinter einer *Bank am Marktplatz', set: cityNight, sfx: [['steps', 0, 0.6]], cam: { pos: [8, 7, 6], look: [8, 2, -9], fov: 55, blur: 0.15, push: 0.06 },
    act(lt, c) { const k = clamp(lt / 1.2); if (k < 1) N.me.reset().place(8 + (1 - k) * 6, -9.8, -Math.PI / 2).run(c.t); else crouch(N.me, 8, -9.8).setFace('serious').idle(c.t, 0.3); } });
  shot({ line: 'und *wartete. //', set: cityNight, cam: { pos: [8.4, 3.4, -4.2], look: [8, 3.2, -9.8], fov: 50, blur: 0.6, push: 0.1 },
    act(lt, c) { crouch(N.me, 8, -9.8).setFace('uneasy').idle(c.t, 0.3); N.me.head.rotation.y = Math.sin(c.t * 1.5) * 0.4; } });
  // 3:00
  shot({ line: 'Punkt *drei Uhr', set: cityNight, sfx: [['alarm', 'drei', 0.9]], cam: { pos: [-20.1, 9.2, -8.6], look: [-20.3, 8.6, -11.3], fov: 45, blur: 0.6, push: 0.12 },
    act(lt, c) { cityNight.ledgeClock.rotation.z = lt > c.w('drei') ? Math.sin(c.t * 70) * 0.09 : 0; } });
  shot({ line: 'klingelte irgendwo ein *Wecker.', set: cityNight, sfx: [['alarm', 0, 0.6]], cam: { pos: [-14, 5, 6], look: [-23, 6.5, -12], fov: 55, blur: 0.1, push: 0.06 },
    act(lt, c) { cityNight.ledgeClock.rotation.z = Math.sin(c.t * 70) * 0.09; } });
  shot({ line: 'Dann ging eine *Tür auf. ///', set: cityNight, sfx: [['creak', 'tür', 1], ['drone', 'auf', 0.9]], cam: { pos: [-23.5, 4.2, -2], look: [-25, 3.8, -11.6], fov: 50, blur: 0.25, push: 0.08 },
    act(lt, c) { const k = E.out(remap(lt, c.w('tür'), c.w('tür') + 0.9)); cityNight.hinge.rotation.y = k * 1.7; if (lt > c.w('auf') + 0.3) shadow.reset().place(-25, -11.2, 0).setFace('blank').idle(c.t, 0.2); } });
  shot({ line: 'Die dunkle *Gestalt schlich zum *Café', set: cityNight, sfx: [['steps', 0, 0.4]], cam: (lt, s) => { const x = -18 + lt * 9; return { pos: [x - 2, 4.6, 7], look: [x, 3.6, -3.5], fov: 55, blur: 0.15, push: 0 }; },
    act(lt, c) { cityNight.hinge.rotation.y = 1.7; shadow.reset().place(-18 + lt * 9, -3.5, Math.PI / 2).walk(c.t, 0.6, 22).setFace('blank'); crouch(N.me, 8, -9.8).setFace('uneasy'); } });
  shot({ line: 'neben der Bäckerei und holte ein *Streichholz heraus.', set: cityNight, sfx: [['match', 'streichholz', 1]], cam: { pos: [CHX - 9, 4.6, CHZ + 4], look: [CHX, 3.2, CHZ], fov: 50, blur: 0.25, push: 0.08 },
    act(lt, c) { shadow.reset().place(CHX, CHZ, -Math.PI / 2 - 0.4).setFace('blank'); if (lt > c.w('streichholz')) { shadow.pose({ aR: [70, -10] }); match.visible = true; } } });
  // THE REVEAL
  shot({ line: 'Ronaldo sprang *hervor', set: cityNight, sfx: [['whoosh', 'hervor', 0.9]], cam: frame(11, -9.4, { size: 'full', side: -20, low: 0.4 }),
    act(lt, c) { const k = remap(lt, c.w('hervor') - 0.1, c.w('hervor') + 0.5); N.me.reset().place(lerp(8, 13, k), lerp(-9.8, -9, k), Math.PI / 2).pose('cheer', 0.5).jump(k, 2.5).setFace('angry'); exMe.at(lt - c.w('hervor'), N.me); } });
  shot({ line: 'und leuchtete ihr mit der *Taschenlampe', set: cityNight, sfx: [['click', 'taschenlampe', 1]], cam: { pos: [RX - 3, 5, CHZ + 4], look: [CHX, 4, CHZ], fov: 55, blur: 0.15, push: 0.06 },
    act(lt, c) { N.me.reset().place(RX, CHZ, Math.PI / 2).pose({ aR: [90, 0] }).setFace('angry'); torch.visible = lt > c.w('taschenlampe'); shadow.reset().place(CHX, CHZ, Math.PI).setFace('blank'); } });
  shot({ line: 'direkt ins *Gesicht. //', set: cityNight, sfx: [['hit', 'gesicht', 0.8]], flash: lt => Math.max(0, 0.7 - lt * 3), cam: frame(CHX, CHZ, { size: 'close', facing: -Math.PI / 2, side: 10 }),
    act(lt, c) { cityNight.faceL.position.set(CHX - 3, 5, CHZ); cityNight.faceL.intensity = 14; shadow.reset().place(CHX, CHZ, -Math.PI / 2).pose({ aL: [140, -30], aR: [70, -10] }).setFace('blank'); match.visible = true; } });
  shot({ line: 'Es war der *Feuerwehr-Chef. ///', set: cityNight, sfx: [['boom', 'feuerwehr-chef', 1]], cam: frame(CHX, CHZ, { size: 'face', facing: -Math.PI / 2, side: -8, push: 0.12 }),
    act(lt, c) { cityNight.faceL.position.set(CHX - 3, 5, CHZ); cityNight.faceL.intensity = 14; N.chief.reset().place(CHX, CHZ, -Math.PI / 2).setFace('shock').idle(c.t, 0.2); exChief.at(lt - c.w('feuerwehr-chef') - 0.2, N.chief); } });
  shot({ line: '„Ich wollte nur einmal ein *Held sein“, sagte er.', set: cityNight, cam: frame(CHX, CHZ, { size: 'close', facing: -Math.PI / 2, side: 16 }),
    act(lt, c) { cityNight.faceL.position.set(CHX - 3, 5, CHZ); cityNight.faceL.intensity = 10; N.chief.reset().place(CHX, CHZ, -Math.PI / 2).pose('shrug').setFace(lt < c.w('sagte') ? 'say' : 'sad').talk(c.t, lt < c.w('sagte') ? 1 : 0).idle(c.t, 0.3); } });
  shot({ line: '„Aber meine Männer sind zu *faul,', set: fstation, sfx: [['snore', 0, 0.9]], cam: { pos: [14, 10, 8], look: [-3, 2.8, 0], fov: 58, blur: 0.1, push: 0.06 },
    act(lt, c) { firemen.forEach((a, i) => { const [x, z] = hammocks[i]; lie(a, x, 2.3 + Math.sin(c.t * 2 + i) * 0.04, z + 2.6).setFace('sleepy'); }); zzzF.at(lt % 1.4, firemen[1]); } });
  shot({ line: 'um überhaupt zu kommen.“', set: cityNight, cam: frame(CHX, CHZ, { size: 'face', facing: -Math.PI / 2, side: -12 }),
    act(lt, c) { cityNight.faceL.position.set(CHX - 3, 5, CHZ); cityNight.faceL.intensity = 10; N.chief.reset().place(CHX, CHZ, -Math.PI / 2).setFace(lt > c.w('kommen') ? 'cry' : 'say').talk(c.t, 0.8); } });
  // WAKE UP, TOWN
  shot({ line: 'Da schrie Ronaldo so laut er konnte:', set: cityNight, cam: frame(RX, CHZ, { size: 'close', facing: Math.PI / 2, side: -14, low: 0.25 }),
    act(lt, c) { N.me.reset().place(RX, CHZ, Math.PI / 2).pose('idle').setFace('angry').idle(c.t, 0.5); } });
  shot({ line: '„Alle *aufwachen!“', set: cityNight, sfx: [['shout', 'alle', 1]], cam: (lt, s) => ({ ...frame(RX, CHZ, { size: 'face', facing: Math.PI / 2, side: 6, push: 0.3 }), roll: Math.sin(lt * 40) * 1.2 }),
    act(lt, c) { N.me.reset().place(RX, CHZ, Math.PI / 2).pose({ aL: [30, 60], aR: [30, 60], head: [-12, 0, 0] }).setFace('scream'); } });
  shot({ line: 'Und zum ersten Mal in der Geschichte dieser Stadt', set: cityNight, sfx: [['rise', 0, 0.8]], cam: drone([0, 2, -14], { h: 54, back: 52, drift: [10, 4, 6], fov: 52 }),
    act(lt, c) { cityNight.setLit(Math.round(lerp(0.1, 0.65, c.k) * 40) / 40); } });
  shot({ line: 'wachten alle mitten in der Nacht *auf.', set: cityNight, sfx: [['pop', 'auf', 0.8]], cam: { pos: [6, 6, 16], look: [0, 6, -14], fov: 58, blur: 0.05, push: 0.06 },
    act(lt, c) { cityNight.setLit(lt > c.w('auf') ? 1 : 0.7); } });
  shot({ line: 'Der *Postbote,', set: cityNight, cam: follow(lt => [-12 + lt * 10, 0, -3], [-3, 2.4, 9], { lookY: 3.6 }),
    act(lt, c) { cityNight.setLit(1); N.post.reset().place(-12 + lt * 10, -3, Math.PI / 2).run(c.t).setFace('angry'); } });
  shot({ line: 'der *Lehrer,', set: cityNight, cam: follow(lt => [-6 + lt * 10, 0, -2], [3, 2.4, 9], { lookY: 3.6 }),
    act(lt, c) { cityNight.setLit(1); N.teach.reset().place(-6 + lt * 10, -2, Math.PI / 2).run(c.t).setFace('angry'); } });
  shot({ line: 'sogar *Ronaldos *Vater.', set: cityNight, sfx: [['pop', 'vater', 0.7]], cam: follow(lt => [0 + lt * 10, 0, -3], [-2, 2.2, 8], { lookY: 3.6 }),
    act(lt, c) { cityNight.setLit(1); N.dad.reset().place(lt * 10, -3, Math.PI / 2).run(c.t, 0.8).setFace(lt > c.w('vater') ? 'angry' : 'shock'); } });
  shot({ line: 'Gemeinsam hielten sie den Chef *fest,', set: cityNight, sfx: [['thud', 'fest', 1]], cam: { pos: [CHX, 12, CHZ + 18], look: [CHX, 2.5, CHZ + 1], fov: 55, blur: 0.05, push: 0.06 },
    act(lt, c) { cityNight.setLit(1); crowd(N, c); N.chief.reset().place(CHX, CHZ, 0).pose('slump').setFace('sad'); N.me.reset().place(CHX, CHZ + 8.5, Math.PI).pose('hips').setFace('smug'); } });
  shot({ line: 'bis die *Sonne aufging.', set: cityNight, light: 'sunset', sfx: [['rise', 'sonne', 0.7]], cam: { pos: [CHX - 10, 5, CHZ + 16], look: [CHX, 4, CHZ], fov: 55, blur: 0.1, push: 0.05 },
    act(lt, c) { cityNight.skyA.visible = false; cityNight.skyB.visible = true; crowd(N, c, i => 'sleepy', i => 'reach'); N.chief.reset().place(CHX, CHZ, 0).pose('slump').setFace('sleepy'); } });
  // THE PARTY + ENDING
  shot({ line: 'Am nächsten Morgen standen alle um *sechs Uhr auf,', set: cityDay, sfx: [['whoosh', 0, 0.6], ['cheer', 'sechs', 0.8]], cam: drone([0, 2, -4], { h: 40, back: 42, drift: [0, -6, -8], fov: 55 }),
    act(lt, c) { const all = [D.post, D.teach, D.dad, ...D.folk]; all.forEach((a, i) => a.reset().place(-10 + (i % 5) * 5, -4 + Math.floor(i / 5) * 4, Math.PI).pose('cheer').setFace('joy').jump(Math.abs(Math.sin(c.t * 4 + i)), 0.6)); D.me.reset().place(0, -12, 0).pose('wave').setFace('grin'); confetti.at(c.t, 0, -6); } });
  shot({ line: 'um *Ronaldo zu feiern.', set: cityDay, sfx: [['cheer', 0, 1], ['sparkle', 'ronaldo', 0.8]], cam: frame(0, -6, { size: 'medium', low: 0.35, side: 8, push: 0.1 }),
    act(lt, c) { D.me.reset().place(0, -6, 0).pose('cheer').setFace('joy').jump(Math.abs(Math.sin(c.t * 4)), 0.5); spark.at(lt - c.w('ronaldo'), [0, 0, -6]); [D.post, D.dad, D.teach, D.folk[0], D.folk[4]].forEach((a, i) => a.reset().place(-5 + i * 2.5, -11 + (i % 2), 0).pose('cheer').setFace('joy').jump(Math.abs(Math.sin(c.t * 4 + i * 1.3)), 0.5)); confetti.at(c.t, 0, -6); } });
  shot({ line: 'Nur einer schlief bis *zwölf Uhr. //', set: bedDay, sfx: [['snore', 0, 0.9]], cam: { pos: [-1.6, 3.6, 3.2], look: [-2.5, 3.3, -3.4], fov: 55, blur: 0.6, push: 0.1 } });
  shot({ line: '*Ronaldo.', set: bedDay, cam: { pos: [-6.6, 6.6, -2.4], look: [-8, 2.6, -3.6], fov: 50, blur: 0.6, push: 0.08 },
    act(lt, c) { lie(meBedD, -8, 2.0 + Math.sin(c.t * 1.6) * 0.03, 1.4).setFace('happy'); zzzMe.at(lt % 1.4, meBedD); } });
  shot({ line: 'Er hatte es sich *verdient.', set: bedDay, cam: { pos: [2, 8, 10], look: [-6, 2.4, -1], fov: 55, blur: 0.15, push: 0.04 },
    act(lt, c) { lie(meBedD, -8, 2.0 + Math.sin(c.t * 1.6) * 0.03, 1.4).setFace('happy'); zzzMe.at(lt % 1.4, meBedD); } });
}
start(build);
