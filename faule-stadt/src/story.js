// "In dieser Stadt ist jeder faul – außer mir."  Ich-Erzähler, deutsch, Cliffhanger-Ende "2?".
// Keywords marked with * show as yellow captions. // = 0.6 s silent hold, /// = 1.0 s.
import * as THREE from 'three';
import { start, shot, frame, W, H } from './core.js';
import { makeAvatar } from './avatar.js';
import { SETS, TEX, floor, building, lampPost, tree, bush, bench, sky, room, sofa, desk, chair, bookStack, windowPane, trashCan } from './sets.js';
import { makeEmote, makePuff } from './fx.js';
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
// dark windows at night (most of the town is asleep), a few warm ones
function nightWindows(group, litShare = 0.12, seed = 3) {
  const r = rng(seed), dark = mat('#1b2238'), warm = glow('#ffd98a', 1.5);
  group.traverse(o => { if (o.isMesh && o.material && o.material.isMeshBasicMaterial && o.geometry.type === 'PlaneGeometry' && o.material.color.b > 1.0 && o.material.color.r < 1.0) o.material = r() < litShare ? warm : dark; });
}

// ───────────── sets
const COLORS = ['#f2c7d0', '#bfe3ff', '#fff0b8', '#d6f2c4', '#e4d0ff', '#ffd2a8', '#c9f0ec', '#ffc2c2'];
function city(time) {
  const night = time === 'night', g = grp(night ? skyDome('night') : sky(), hills(night ? '#1d3320' : '#6fbf5a', -220));
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
  const bakery = building(20, 13, 12, '#f8c5c7', { sign: 'BÄCKEREI', signFg: '#c2264a', awning: '#e84b6a', windows: [3, 2], doorColor: '#e84b6a' }); g.add(at(bakery, 0, 0, -20));
  for (const x of [-30, -12, 12, 30]) g.add(at(lampPost(10), x, 0, 7.4));
  g.add(at(tree(9), -22, 0, 7.5), at(tree(9), 22, 0, 7.5), at(bench(), -8, 0, -8), at(bench(), 8, 0, -8), at(trashCan(), 12, 0, -7.5));
  if (night) { nightWindows(g); for (const x of [-30, 12]) { const L = new THREE.PointLight('#ffd9a0', 160, 24, 2); L.position.set(x, 10.2, 7.4); g.add(L); } }
  const fire = makeFire(g, 0, 0, -13.2, 18);
  const ash = grp(at(box(9, 0.25, 5, '#2a2626', 0.2), 0, 0.12, -9), at(box(2, 0.6, 1.4, '#1e1b1b', 0.2), -2, 0.3, -9.5), at(box(1.6, 0.5, 1.2, '#3a3433', 0.2), 2.5, 0.25, -8.2));
  const clockA = at(alarmClock('03:00'), 0.6, 0.1, -7.6); clockA.rotation.x = -0.25; clockA.scale.setScalar(0.55); ash.add(clockA); g.add(ash); PRE.push(() => { ash.visible = false; });
  return { group: g, light: night ? 'townNight' : 'outdoor', fire, ash, reset() { fire.set(0, 0, 0); } };
}
const cityDay = city('day'), cityNight = city('night');
const street = SETS.street({ shops: [['POST', '#fff0b8', '#e0a21a'], ['CAFÉ', '#f8c5c7', '#e84b6a'], ['KIOSK', '#bfe3ff', '#2f7de1'], ['BÜCHER', '#d6f2c4', '#2e9e59'], ['APOTHEKE', '#e4d0ff', '#7b3fc4']] });
const living = SETS.livingRoom();
const fridge = grp(at(box(3.2, 7.4, 2.6, '#f4f6f8', 0.2), 0, 3.7, 0), at(box(3.22, 0.08, 2.62, '#c9cdd3'), 0, 4.9, 0), at(box(0.2, 1.6, 0.2, '#9aa0a8'), 1.2, 6, 1.35), at(box(0.2, 1.6, 0.2, '#9aa0a8'), 1.2, 3.2, 1.35));
living.group.add(at(fridge, 4.5, 0, -4.2));
const letters = []; for (let i = 0; i < 3; i++) { const l = box(0.9, 0.06, 0.6, '#fbfbf8'); l.visible = false; living.group.add(l); letters.push(l); } PRE.push(() => letters.forEach(l => { l.visible = false; }));
const pizza = grp(at(box(2.4, 0.35, 2.4, '#e8d5b0', 0.05), 0, 0, 0), at(sign('PIZZA', 2, 0.7, { bg: '#e8d5b0', fg: '#c0392b' }), 0, 0.19, 0)); pizza.children[1].rotation.x = -Math.PI / 2; living.group.add(pizza); PRE.push(() => { pizza.visible = false; });
const classroom = SETS.classroom({ board: ['MATHE', '7 × 8 = ?'] });
const tDesk = desk('#b9783f'); classroom.group.add(at(tDesk, 9, 0, -1.5));
const bedroomDay = SETS.bedroom({ poster: 'NIE\nAUFGEBEN', bed: '#d8322a' });
const clock6 = at(alarmClock('06:00', '#2f7de1'), -2.5, 0, 0); bedroomDay.group.add(at(box(2.6, 2.2, 2, '#b9783f'), -2.5, 1.1, -3.6)); clock6.position.set(-2.5, 2.2, -3.4); bedroomDay.group.add(clock6);
bedroomDay.group.add(at(chair('#2b7de0'), 9, 0, 0.9), at(bookStack(4, 5), 6.6, 2.7, 3), at(sign('MATHE', 1.6, 0.5, { bg: '#fff', fg: '#2d5fd0' }), 10.2, 2.75, 3.2));
const bedroomNight = room({ floorTex: TEX.wood('#6a4428'), tile: 6, wallColor: '#2e3a66', trim: '#222b4a', trimY: 0.6, w: 30, d: 22, h: 12, lights: 0, ceiling: '#141a2c' });
bedroomNight.add(at(windowPane(5, 4, '#1a2340'), 5, 7, -5.85), at(box(4.6, 0.7, 8, '#4a3220'), -8, 0.35, -1.2), at(box(4.6, 1.2, 8, '#d9d4cc', 0.15), -8, 1.3, -1.2), at(box(4.7, 0.5, 5.4, '#d8322a', 0.2), -8, 2.05, 0.2), at(box(3.2, 0.6, 1.6, '#ffffff', 0.25), -8, 2.2, -3.9), at(box(2.6, 2.2, 2, '#4a3220'), -3.2, 1.1, -3.8));
const glowWin = new THREE.Mesh(new THREE.PlaneGeometry(5, 4), new THREE.MeshBasicMaterial({ color: new THREE.Color('#ff7a2a').multiplyScalar(1.6), transparent: true, opacity: 0, toneMapped: false })); glowWin.position.set(5, 7, -5.6); bedroomNight.add(glowWin);
const clock3 = at(alarmClock('03:00'), -3.2, 2.2, -3.6); bedroomNight.add(clock3);
const moonL = new THREE.PointLight('#9fb6ff', 120, 30, 2); moonL.position.set(4, 8, 2); bedroomNight.add(moonL);
const fireL = new THREE.PointLight('#ff7a2a', 0, 30, 2); fireL.position.set(4, 7, -3); bedroomNight.add(fireL);
const bedNight = { group: bedroomNight, light: 'roomNight', reset() { glowWin.material.opacity = 0; fireL.intensity = 0; } };
const station = room({ floorTex: TEX.concrete('#9a9a9a'), tile: 6, wallColor: '#b8342c', trim: '#f2c230', trimY: 4, w: 44, d: 28, h: 14, lights: 2 });
station.add(at(sign('FEUERWACHE', 14, 2.4, { bg: '#f4f4f4', fg: '#b8342c', border: '#b8342c', weight: 900 }), 0, 11, -5.85));
const truck = car('#d62828'); truck.scale.setScalar(1.6); station.add(at(truck, 15, 0, -1, -0.3));
const hammocks = [];
for (const [x, z] of [[-10, 0], [-2, 0], [6, 0]]) { const h = grp(at(box(0.4, 6, 0.4, '#4a3220'), 0, 3, -4.5), at(box(0.4, 6, 0.4, '#4a3220'), 0, 3, 4.5)); for (let i = 0; i < 9; i++) { const k = i / 8 - 0.5; h.add(at(box(2.2, 0.2, 1.05, i % 2 ? '#f2c230' : '#2f7de1'), 0, 3.2 - Math.cos(k * Math.PI) * 1.2, k * 8.4)); } station.add(at(h, x, 0, z)); hammocks.push([x, z]); }
const fstation = { group: station, light: 'indoor' };

// ───────────── cast (one copy per set, same options)
const ME = { seed: 3, skin: 'light', hair: 'spiky', hairColor: '#1d1410', top: 'hoodie', topColor: '#d8322a', sleeves: 'long', bottom: 'jeans', bottomColor: '#2c3550', shoe: '#f2f2f2', face: 'smile' };
const me = s => { const a = makeAvatar(ME); s.group.add(a.root); return a; };
const meNight = me(cityNight), meStreet = me(street), meBedDay = me(bedroomDay), meBedNight = me(bedNight);
const hose = grp(at(box(0.5, 0.5, 2.4, '#c0392b', 0.15), 0, 0, 0.9), at(box(0.35, 0.35, 0.8, '#d9d9de'), 0, 0, 2.4)); hose.rotation.x = Math.PI / 2; meNight.handR.add(hose); PRE.push(() => { hose.visible = false; });
const postman = makeAvatar({ seed: 21, skin: 'tan', hair: 'short', top: 'shirt', topColor: '#f6c915', sleeves: 'short', bottom: 'slacks', bottomColor: '#24305e', cap: '#f6c915', face: 'sleepy' }); living.group.add(postman.root);
const dad = makeAvatar({ seed: 31, skin: 'light', hair: 'messy', hairColor: '#4a2f1d', top: 'tee', topColor: '#f2f2f2', sleeves: 'short', bottom: 'joggers', bottomColor: '#6b6f78', face: 'sleepy' }); living.group.add(dad.root);
const phone = at(box(0.5, 0.9, 0.12, '#141418', 0.05), 0, -0.2, 0.6); dad.handR.add(phone);
const teacher = makeAvatar({ seed: 41, skin: 'fair', hair: 'short', hairColor: '#9a9aa0', glasses: true, top: 'suit', topColor: '#7a5a3a', tie: '#2f7de1', sleeves: 'long', bottom: 'slacks', bottomColor: '#4a3a2a', face: 'sleepy' }); classroom.group.add(teacher.root);
const KIDS = [{ hair: 'curly', hairColor: '#2b1b14', topColor: '#2e9e59', skin: 'brown' }, { hair: 'ponytail', hairColor: '#c98a3a', topColor: '#e84b6a', skin: 'fair' }, { hair: 'short', hairColor: '#111', topColor: '#7b3fc4', skin: 'tan', glasses: true }, { hair: 'buns', hairColor: '#5a2a1a', topColor: '#f2b01e', skin: 'light' }];
const kids = KIDS.map((o, i) => { const a = makeAvatar({ seed: 50 + i, top: 'tee', sleeves: 'short', bottom: 'jeans', ...o }); classroom.group.add(a.root); return a; });
const NB = [{ hair: 'bob', hairColor: '#c9c9c9', top: 'cardigan', topColor: '#9b6fd0', skin: 'fair' }, { hair: 'bald', top: 'vest', topColor: '#3f9b3f', skin: 'deep' }, { hair: 'long', hairColor: '#6a3a1a', top: 'sweater', topColor: '#e8632b', skin: 'light' }];
const neighbors = NB.map((o, i) => { const a = makeAvatar({ seed: 60 + i, sleeves: 'long', bottom: 'slacks', bottomColor: '#3a3d48', face: 'sus', ...o }); street.group.add(a.root); return a; });
const FF = { skin: 'light', hair: 'short', top: 'stripes', topColor: '#2a2f45', stripe: '#f2c230', sleeves: 'long', bottom: 'slacks', bottomColor: '#2a2f45', cap: '#d62828', face: 'sleepy' };
const firemen = [0, 1, 2].map(i => { const a = makeAvatar({ ...FF, seed: 70 + i, skin: ['light', 'tan', 'brown'][i] }); station.add(a.root); return a; });
const shadow = makeAvatar({ seed: 99, skin: '#121216', hair: 'short', hairColor: '#0b0b0d', top: 'hoodie', topColor: '#121216', sleeves: 'long', bottom: 'plain', bottomColor: '#121216', shoe: '#121216', sole: '#121216', face: 'blank' });
for (const s of [-1, 1]) shadow.head.add(at(box(0.2, 0.09, 0.05, glow('#ff2a2a', 3)), s * 0.24, 0.68, 0.64)); cityNight.group.add(shadow.root);
const zzzT = makeEmote(classroom.group, 'zzz', '#2f7de1'), zzzP = makeEmote(living.group, 'zzz', '#2f7de1'), zzzF = makeEmote(station, 'zzz', '#2f7de1'), qNB = makeEmote(street.group, '?', '#ff3b30'), exMe = makeEmote(bedNight.group, '!', '#ff3b30');
const puff = makePuff(street.group), spray = makeSpray(cityNight.group);

// helpers
const lie = (a, x, y, z) => { a.reset().place(x, z, 0, y); a.root.rotation.x = -Math.PI / 2 + 0.22; a.pose({ aL: [10, 20], aR: [10, 20] }); return a; };
const fireOn = (c, lv = 1, sm) => cityNight.fire.set(lv, c.t, sm === undefined ? lv : sm);

// ───────────── shots
async function build() {
  // HOOK: the burning town from above
  shot({ line: 'In dieser Stadt ist jeder so *faul,', set: cityNight, sfx: [['whoosh', 0, 0.9], ['fire', 0, 0.8]],
    cam: drone([0, 4, -14], { h: 46, back: 62, drift: [-6, -6, -10], fov: 52 }), act(lt, c) { fireOn(c); } });
  shot({ line: 'dass letzte Nacht beinahe alles *abgebrannt wäre.', set: cityNight, sfx: [['boom', 'abgebrannt', 0.9]],
    cam: { pos: [6, 5, 14], look: [0, 8, -16], fov: 55, blur: 0.15, push: 0.1 }, act(lt, c) { fireOn(c); } });
  shot({ line: 'Und das Schlimmste:', set: cityNight, cam: frame(5, -3, { size: 'close', side: 12 }),
    act(lt, c) { fireOn(c); meNight.reset().place(5, -3, 0.15).setFace('uneasy').idle(c.t); } });
  shot({ line: 'Es war *kein *Unfall. //', set: cityNight, sfx: [['hit', 'unfall', 1]], cam: frame(5, -3, { size: 'face', side: -8, push: 0.12 }),
    act(lt, c) { fireOn(c); meNight.reset().place(5, -3, 0.1).setFace(lt < c.w('unfall') ? 'worried' : 'shock').idle(c.t, 0.4); } });
  // THE LAZY TOWN
  shot({ line: 'Hier steht niemand vor *zwölf Uhr auf.', set: cityDay, sfx: [['whoosh', 0, 0.6]], cam: drone([0, 0, -6], { h: 52, back: 58, drift: [10, 0, -4], fov: 50 }) });
  shot({ line: 'Der *Postbote wirft die Briefe', set: living, cam: frame(-4, -3.4, { size: 'medium', side: 18, low: 0.05 }),
    act(lt, c) { postman.reset().place(-4, -3.4, 0.2).sit(1.6).setFace('sleepy').idle(c.t, 0.5); zzzP.at(lt, postman); } });
  shot({ line: 'vom Sofa aus durchs Fenster.', set: living, sfx: [['whoosh', 'fenster', 0.6]], cam: { pos: [-5, 6.5, 10], look: [0, 4.2, -4], fov: 64, blur: 0.1 },
    act(lt, c) {
      postman.reset().place(-4, -3.4, 0.5).sit(1.6).setFace('sleepy');
      const t0 = c.w('durchs') - 0.2, k = clamp((lt - t0) / 0.7); postman.pose({ aR: [150 - 110 * E.out(k), 20] });
      const l = letters[0]; l.visible = k > 0 && k < 1; l.position.set(lerp(-3.2, 6, k), lerp(5, 7.4, k) + Math.sin(k * Math.PI) * 2, lerp(-2.6, -5.7, k)); l.rotation.y = lt * 9;
    } });
  shot({ line: 'Der *Lehrer schläft im Unterricht', set: classroom, sfx: [['snore', 'schläft', 0.8]], cam: frame(9, -3.6, { size: 'medium', side: -15, low: 0.2 }),
    act(lt, c) { teacher.reset().place(9, -3.6, 0).sit(1.4).pose({ head: [38, 0, 10], aL: [80, -10], aR: [80, -10] }).setFace('sleepy'); teacher.hip.position.y += Math.sin(c.t * 2) * 0.05; zzzT.at(lt, teacher); classroom.desks.visible = true; } });
  shot({ line: 'schneller ein als seine Schüler.', set: classroom, cam: { pos: [0, 7, 2.5], look: [0, 4.6, 11], fov: 70, blur: 0.15 },
    act(lt, c) { classroom.desks.visible = true; kids.forEach((a, i) => { const [x, z] = classroom.seats[i]; const sl = lt > c.w('schüler') - 0.3 + i * 0.12; a.reset().place(x, z, Math.PI).sit(1.5).setFace(sl ? 'sleepy' : (i % 2 ? 'neutral' : 'sus')).pose({ head: [sl ? 28 : 0, 0, sl ? 12 : 0] }).idle(c.t, 0.4); }); } });
  shot({ line: 'Und mein *Vater bestellt Pizza,', set: living, cam: frame(-4, -3.4, { size: 'close', side: -14, low: 0.05 }),
    act(lt, c) { dad.reset().place(-4, -3.4, 0).sit(1.6).pose({ aR: [70, -10], head: [12, 0, 0] }).setFace(lt > c.w('pizza') ? 'smug' : 'sleepy').idle(c.t, 0.4); } });
  shot({ line: 'weil ihm der Kühlschrank zu weit weg ist.', set: living, sfx: [['pop', 'weit', 0.7]], cam: { pos: [0, 7, 15], look: [0, 3.5, -3], fov: 64, blur: 0.1, push: 0.05 },
    act(lt, c) { dad.reset().place(-4, -3.4, 0.4).sit(1.6).pose({ aL: [80, 30], aR: [70, -10] }).setFace(lt > c.w('weit') ? 'sad' : 'sleepy').idle(c.t, 0.4); pizza.visible = true; pizza.position.set(-4, 2.6, -1.6); } });
  // THE EXCEPTION: ME
  shot({ line: 'Nur *ich bin anders.', set: street, sfx: [['whoosh', 0, 0.5], ['pop', 'ich', 0.6]], cam: frame(0, 3, { size: 'full', low: 0.45, side: 10, push: 0.09 }),
    act(lt, c) { meStreet.reset().place(0, 3, 0).pose(lt > c.w('anders') ? 'hips' : 'open').setFace(lt > c.w('ich') ? 'grin' : 'smile').idle(c.t); } });
  shot({ line: 'Ich stehe jeden Morgen um *sechs Uhr auf,', set: bedroomDay, sfx: [['alarm', 'sechs', 0.9]], cam: { pos: [-1.6, 3.6, 3.2], look: [-2.5, 3.3, -3.4], fov: 55, blur: 0.6, push: 0.1 },
    act(lt, c) { const ring = lt > c.w('sechs'); clock6.rotation.z = ring ? Math.sin(c.t * 70) * 0.09 : 0; } });
  shot({ line: 'gehe *joggen', set: street, light: 'sunset', sfx: [['steps', 0, 0.7]],
    cam: follow(lt => [-14 + lt * 9, 0, 5], [4, 2.2, 11], { lookY: 3.4 }), act(lt, c) { meStreet.reset().place(-14 + lt * 9, 5, Math.PI / 2).run(c.t).setFace('grin'); } });
  shot({ line: 'und mache sogar meine *Hausaufgaben.', set: bedroomDay, sfx: [['tick', 'hausaufgaben', 0.8]], cam: { pos: [9, 5.6, 9.5], look: [9, 3.8, 1.4], fov: 55, blur: 0.4 },
    act(lt, c) { meBedDay.reset().place(9, 1.2, 0).sit(1.5).pose({ aL: [70, -5], aR: [60 + Math.sin(c.t * 9) * 8, -8], head: [16, 0, 0] }).setFace(lt > c.w('hausaufgaben') ? 'grin' : 'serious'); } });
  shot({ line: 'Deshalb halten mich alle', set: street, cam: { pos: [0, 4.6, 16], look: [0, 3.8, 4], fov: 60, blur: 0.2 },
    act(lt, c) { neighbors.forEach((a, i) => a.reset().place(-5 + i * 5, 4.2 - (i % 2) * 0.6, 0.15 - i * 0.15).pose(i === 1 ? 'hips' : 'idle').setFace('sus').idle(c.t, 0.5)); meStreet.reset().place(-10 + lt * 8, 8.5, Math.PI / 2).run(c.t); } });
  shot({ line: 'für *verrückt.', set: street, sfx: [['pop', 'verrückt', 0.7]], cam: frame(5, 3.6, { size: 'close', side: -12, push: 0.12 }),
    act(lt, c) { const a = neighbors[2]; a.reset().place(5, 3.6, -0.15).pose('point').setFace('sus').idle(c.t, 0.4); qNB.at(lt - c.w('verrückt'), a); } });
  // THE NIGHT
  shot({ line: 'Doch letzte Nacht, um *drei Uhr,', set: bedNight, sfx: [['tick', 'drei', 0.9]], cam: { pos: [-2.4, 4.2, 2.4], look: [-3.2, 3.3, -3.6], fov: 52, blur: 0.7, push: 0.12 } });
  shot({ line: 'roch ich plötzlich *Rauch.', set: bedNight, sfx: [['hit', 'rauch', 0.8]], cam: frame(-8, -0.6, { size: 'close', y: 0.0, side: 14 }),
    act(lt, c) { const k = remap(lt, c.w('rauch') - 0.3, c.w('rauch') + 0.4); glowWin.material.opacity = 0.9 * k; fireL.intensity = 180 * k; meBedNight.reset().place(-8, -0.6, 0.2).sit(2.3).pose({ head: [-8, 25 * k, 0] }).setFace(lt > c.w('rauch') ? 'shock' : 'uneasy').idle(c.t, 0.3); exMe.at(lt - c.w('rauch'), meBedNight); } });
  shot({ line: 'Die *Bäckerei am Marktplatz', set: cityNight, sfx: [['fire', 0, 0.9]], cam: { pos: [0, 7, 22], look: [0, 8, -16], fov: 55, blur: 0.05, push: 0.08 }, act(lt, c) { fireOn(c); } });
  shot({ line: 'stand in *Flammen. //', set: cityNight, sfx: [['boom', 'flammen', 1]], cam: handheld({ pos: [-4, 9.5, -3], look: [0, 9, -15], fov: 50, blur: 0.1, push: 0.1 }, 1.2, 4), act(lt, c) { fireOn(c, 1.15); } });
  shot({ line: 'Ich rannte zur *Feuerwache.', set: cityNight, sfx: [['steps', 0, 0.9]],
    cam: follow(lt => [10 + lt * 12, 0, 1], [-5, 2.6, 10], { lookY: 3.6 }), act(lt, c) { fireOn(c, 0.9); meNight.reset().place(10 + lt * 12, 1, Math.PI / 2).run(c.t, 1.2).setFace('worried'); } });
  shot({ line: 'Aber die Feuerwehrmänner lagen in ihren *Hängematten', set: fstation, sfx: [['snore', 'hängematten', 0.9]], cam: { pos: [14, 10, 8], look: [-3, 2.8, 0], fov: 58, blur: 0.1, push: 0.05 },
    act(lt, c) { firemen.forEach((a, i) => { const [x, z] = hammocks[i]; lie(a, x, 2.3 + Math.sin(c.t * 2 + i) * 0.04, z + 2.6).setFace('sleepy'); }); zzzF.at(lt % 1.4, firemen[1]); } });
  shot({ line: 'und sagten nur: „Morgen *vielleicht.“ //', set: fstation, cam: { pos: [-1.4, 8.6, 1.4], look: [-2, 3.2, -1.9], fov: 50, blur: 0.6, push: 0.08 },
    act(lt, c) { const a = firemen[1]; lie(a, -2, 2.3, 2.6); a.head.rotation.y = 0.35; a.setFace(lt > c.w('morgen') && lt < c.w('vielleicht') + 0.5 ? 'talk' : 'sleepy'); } });
  // I DO IT MYSELF
  shot({ line: 'Also schnappte ich mir selbst den *Schlauch', set: cityNight, sfx: [['whoosh', 'schlauch', 0.7]], cam: frame(7, -2, { size: 'close', side: -16, low: 0.3 }),
    act(lt, c) { fireOn(c); meNight.reset().place(7, -2, -0.4).pose(lt > c.w('schlauch') ? 'carry' : 'idle').setFace(lt > c.w('schnappte') ? 'angry' : 'serious').idle(c.t); hose.visible = lt > c.w('schlauch'); } });
  shot({ line: 'und kämpfte ganz *allein gegen das Feuer.', set: cityNight, sfx: [['water', 0, 1], ['fire', 0, 0.6]], cam: handheld({ pos: [18, 5.5, 6], look: [4, 6, -10], fov: 58, blur: 0.08, push: 0.05 }, 1.4, 7),
    act(lt, c) { fireOn(c, 1 - 0.35 * c.k); meNight.reset().place(8, -6, -2.3).pose('carry').setFace('angry'); hose.visible = true; spray.at(c.t, [6.4, 3.4, -7], [1, 9, -14], 3); } });
  shot({ line: 'Nach zwanzig Minuten war es endlich *aus.', set: cityNight, sfx: [['water', 0, 0.6], ['hiss', 'aus', 1]], cam: { pos: [0, 12, 26], look: [0, 6, -12], fov: 55, blur: 0, push: 0.05 },
    act(lt, c) { const k = remap(lt, 0, c.w('aus') + 0.2); fireOn(c, 0.65 * (1 - k), 0.7); meNight.reset().place(6, -6, -2.3).pose('carry').setFace('serious'); hose.visible = true; if (k < 1) spray.at(c.t, [4.4, 3.4, -7], [1, 7, -14], 3); } });
  // THE CLUE
  shot({ line: 'Aber dann fand ich in der Asche etwas,', set: cityNight, cam: frame(3, -6, { size: 'medium', side: 25, low: -0.2 }),
    act(lt, c) { fireOn(c, 0, 0.5); cityNight.ash.visible = true; meNight.reset().place(3, -6, -0.6).pose({ head: [30, 0, 0], aL: [20, 10], aR: [20, 10] }).setFace('uneasy').idle(c.t, 0.3); } });
  shot({ line: 'das dort nicht sein durfte.', set: cityNight, sfx: [['hit', 'durfte', 0.6]], cam: { pos: [2.4, 4, -3.4], look: [0.6, 0.6, -7.6], fov: 50, blur: 0.5, push: 0.1 }, act(lt, c) { fireOn(c, 0, 0.4); cityNight.ash.visible = true; } });
  shot({ line: 'Einen *Wecker.', set: cityNight, sfx: [['tick', 'wecker', 1]], cam: { pos: [1.0, 1.9, -5.6], look: [0.6, 0.8, -7.6], fov: 45, blur: 0.8, push: 0.12 }, act(lt, c) { cityNight.ash.visible = true; } });
  shot({ line: 'Gestellt auf *drei Uhr nachts. //', set: cityNight, sfx: [['alarm', 'drei', 0.6]], cam: { pos: [0.7, 1.3, -5.4], look: [0.6, 0.72, -7.6], fov: 40, blur: 0.9, push: 0.15 }, act(lt, c) { cityNight.ash.visible = true; } });
  shot({ line: 'In einer Stadt, in der *niemand jemals', set: cityNight, sfx: [['whoosh', 0, 0.5]], cam: drone([0, 0, 0], { h: 60, back: 50, drift: [-12, 4, 0], fov: 50 }), act(lt, c) { fireOn(c, 0, 0.3); } });
  shot({ line: 'einen Wecker stellt. ///', set: cityNight, sfx: [['hit', 'stellt', 0.9]], cam: frame(4, 2, { size: 'face', side: 6, push: 0.1 }),
    act(lt, c) { meNight.reset().place(4, 2, 0).setFace(lt > c.w('stellt') ? 'shock' : 'worried').idle(c.t, 0.3); } });
  // CLIFFHANGER
  shot({ line: 'Jemand hier ist gar *nicht faul.', set: cityNight, sfx: [['drone', 0, 1]], cam: { pos: [-30, 4.5, 17], look: [-40, 4.2, 3], fov: 50, blur: 0.15, push: 0.1 },
    act(lt, c) { shadow.reset().place(-40, 3, 0.7).setFace('blank').idle(c.t, 0.2); } });
  shot({ line: 'Und er *weiß,', set: cityNight, cam: frame(4, 2, { size: 'close', side: -14 }),
    act(lt, c) { meNight.reset().place(4, 2, -0.5).pose({ head: [0, -30, 0] }).setFace('worried').idle(c.t, 0.3); } });
  shot({ line: 'dass ich es *weiß.', set: cityNight, sfx: [['hit', 'weiß', 1]], cam: frame(-40, 3, { size: 'face', side: 18, push: 0.12, blur: 0.9 }),
    act(lt, c) { shadow.reset().place(-40, 3, 0.7).setFace('blank'); } });
}
start(build);
