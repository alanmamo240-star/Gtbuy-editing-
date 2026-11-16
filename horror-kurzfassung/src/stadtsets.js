// Sets and props for DIE STADT HINTER DER SPERRE (today, a fictional small town).
import { THREE, toon, lam, flat, box, rbox, sph, cyl, plane, torus, grp, at, noOutline, sameId, sign, glow, canvasTex, rng, clamp, lerp, smooth, noise, rad, FONT } from './util.js';
import { makeSet } from './sets.js';
import { fogOff, texRep } from './lib.js';

// ---------------------------------------------------------------------------------------------- small props
export function phoneMesh(screenTex) {
  const g = new THREE.Group(); g.add(rbox(0.075, 0.012, 0.155, 0.006, toon('#16161e')));
  const m = new THREE.MeshBasicMaterial({ map: screenTex, color: '#ffffff' }); const s = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(0.066, 0.142), m)); s.rotation.x = -Math.PI / 2; s.position.y = 0.0065; g.add(s); g.userData.screen = s; return g;
}
export function alertTex(title, lines, color = '#d8261c') {
  return canvasTex(300, 640, x => {
    x.fillStyle = '#0d0f18'; x.fillRect(0, 0, 300, 640); x.fillStyle = color; x.fillRect(0, 150, 300, 150);
    x.fillStyle = '#fff'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.font = `900 34px ${FONT}`; x.fillText('⚠', 150, 190); x.font = `900 30px ${FONT}`; x.fillText(title, 150, 250);
    x.fillStyle = '#f2f2f6'; x.font = `800 30px ${FONT}`; lines.forEach((l, i) => x.fillText(l, 150, 360 + i * 44));
    x.fillStyle = 'rgba(255,255,255,0.4)'; x.font = `700 22px ${FONT}`; x.fillText('jetzt', 150, 120);
  });
}
const darkTex = canvasTex(8, 8, x => { x.fillStyle = '#0d0f18'; x.fillRect(0, 0, 8, 8); });
export { darkTex };
// a front door seen from inside: lever handle that can turn, peephole; origin at the floor centre of the doorway, leaf facing +z
export function frontDoor({ color = '#e8e2d6', frame = '#c9c2b4' } = {}) {
  const g = new THREE.Group(); g.add(box(1.2, 2.3, 0.08, lam(frame), [0, 1.15, -0.03])); g.add(box(0.95, 2.12, 0.06, lam(color), [0, 1.06, 0.02]));
  for (const y of [0.55, 1.45]) g.add(box(0.72, 0.6, 0.012, lam('#d8d2c4'), [0, y, 0.056]));
  const handle = new THREE.Group(); handle.position.set(0.36, 1.02, 0.07); handle.add(cyl(0.035, 0.035, 0.03, toon('#b8b8c0'), [0, 0, 0], [Math.PI / 2, 0, 0])); handle.add(rbox(0.16, 0.03, 0.035, 0.012, toon('#c8c8d0'), [-0.075, 0, 0.025])); g.add(handle);
  g.add(box(0.05, 0.18, 0.02, toon('#a8a8b0'), [0.36, 0.88, 0.065]));
  g.add(cyl(0.018, 0.018, 0.02, toon('#8a8a90'), [0, 1.58, 0.06], [Math.PI / 2, 0, 0]));
  return { g, handle };
}

// ---------------------------------------------------------------------------------------------- the kitchen at night (episode 1)
// x -3.5..3.5, z -2.5..2.5. Table at the origin. Front door in the hall wall x = -3.5 at z = 1.25 (facing +x). Window on z = -2.5.
export function kitchen(o = {}) {
  const g = new THREE.Group(), W = 7, D = 5, H = 2.6;
  const tiles = texRep(canvasTex(128, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); x.strokeStyle = 'rgba(40,40,70,0.22)'; x.lineWidth = 3; x.strokeRect(0, 0, 128, 128); }), W / 0.6, D / 0.6);
  g.add(plane(W, D, new THREE.MeshLambertMaterial({ color: '#b9a88e', map: tiles }), [0, 0, 0], [-Math.PI / 2, 0, 0])); g.add(plane(W, D, lam('#e6e2da'), [0, H, 0], [Math.PI / 2, 0, 0]));
  const wallM = lam('#d9cdb4');
  g.add(plane(W, H, wallM, [0, H / 2, -D / 2])); g.add(plane(W, H, wallM, [0, H / 2, D / 2], [0, Math.PI, 0])); g.add(plane(D, H, wallM, [-W / 2, H / 2, 0], [0, Math.PI / 2, 0])); g.add(plane(D, H, wallM, [W / 2, H / 2, 0], [0, -Math.PI / 2, 0]));
  for (const [x, z, ry, len] of [[0, -D / 2 + 0.02, 0, W], [0, D / 2 - 0.02, Math.PI, W], [-W / 2 + 0.02, 0, Math.PI / 2, D], [W / 2 - 0.02, 0, -Math.PI / 2, D]]) g.add(at(box(len, 0.1, 0.02, lam('#a89878')), [x, 0.05, z], [0, ry, 0]));
  // table, chairs
  const wood = toon('#9a6a44'); g.add(box(1.7, 0.06, 0.95, wood, [0, 0.76, 0])); for (const [x, z] of [[-0.75, -0.38], [0.75, -0.38], [-0.75, 0.38], [0.75, 0.38]]) g.add(box(0.06, 0.73, 0.06, wood, [x, 0.365, z]));
  const chair = (x, z, ry) => { const c = new THREE.Group(); c.add(box(0.44, 0.05, 0.42, toon('#6a4a34'), [0, 0.46, 0])); c.add(box(0.44, 0.5, 0.04, toon('#6a4a34'), [0, 0.72, -0.2])); for (const [a, b] of [[-0.19, -0.18], [0.19, -0.18], [-0.19, 0.18], [0.19, 0.18]]) c.add(box(0.04, 0.46, 0.04, toon('#5a3a26'), [a, 0.23, b])); g.add(at(c, [x, 0, z], [0, rad(ry), 0])); return c; };
  const chairs = { ben: chair(1.05, 0, -90), nina: chair(0, -0.78, 0), max: chair(0, 0.78, 180) };
  g.add(rbox(0.32, 0.1, 0.32, 0.05, toon('#e0d6c4'), [-0.35, 0.83, 0.05])); for (const [x, z, c] of [[-0.4, 0.02, '#d84a32'], [-0.3, 0.1, '#e8c23a'], [-0.32, -0.02, '#7ab83a']]) g.add(sph(0.045, toon(c), [x, 0.9, z]));
  g.add(cyl(0.04, 0.035, 0.1, toon('#f2f2f2'), [0.45, 0.84, -0.25]));
  // kitchen counter + fridge along z = +2.5, window on z = -2.5, clock
  g.add(box(3.2, 0.9, 0.62, toon('#e8e4dc'), [1.4, 0.45, D / 2 - 0.31])); g.add(box(3.24, 0.05, 0.66, toon('#5a5a66'), [1.4, 0.92, D / 2 - 0.33]));
  for (let i = 0; i < 4; i++) g.add(box(0.7, 0.75, 0.01, toon('#d8d2c6'), [0.2 + i * 0.8, 0.45, D / 2 - 0.62]));
  g.add(box(2.6, 0.7, 0.36, toon('#e8e4dc'), [1.4, 1.95, D / 2 - 0.18])); g.add(rbox(0.75, 1.9, 0.68, 0.04, toon('#eef0f2'), [3.0, 0.95, D / 2 - 0.36]));
  const win = grp(box(1.5, 1.2, 0.06, toon('#f0ece4')), noOutline(box(1.36, 1.06, 0.02, flat('#16203a'), [0, 0, 0.02])), box(0.04, 1.06, 0.03, toon('#f0ece4'), [0, 0, 0.03]), box(1.36, 0.04, 0.03, toon('#f0ece4'), [0, 0, 0.03]));
  g.add(at(win, [0.6, 1.5, -D / 2 + 0.03])); g.add(fogOff(glow(1.8, 1.4, '#3a5aa8', 0.25, [0.6, 1.5, -D / 2 + 0.08])));
  const clockTex = canvasTex(128, 128, x => { x.fillStyle = '#fafafa'; x.beginPath(); x.arc(64, 64, 60, 0, 7); x.fill(); x.strokeStyle = '#222'; x.lineWidth = 5; x.lineCap = 'round'; x.beginPath(); x.moveTo(64, 64); x.lineTo(64, 24); x.moveTo(64, 64); x.lineTo(88, 74); x.stroke(); });
  g.add(at(new THREE.Mesh(new THREE.CircleGeometry(0.17, 30), new THREE.MeshLambertMaterial({ map: clockTex })), [-1.2, 1.9, -D / 2 + 0.02]));
  // hall: the front door on the x = -3.5 wall, a coat rack
  const fd = frontDoor(); g.add(at(fd.g, [-W / 2 + 0.04, 0, 1.25], [0, Math.PI / 2, 0])); g.add(box(0.06, 1.7, 0.06, toon('#4a3a30'), [-W / 2 + 0.25, 0.85, -0.2])); g.add(rbox(0.3, 0.5, 0.18, 0.05, toon('#2f5fb8'), [-W / 2 + 0.25, 1.4, -0.2]));
  g.add(box(0.8, 0.02, 0.5, toon('#6a5a4a'), [-W / 2 + 0.5, 0.01, 1.25]));
  // pendant lamp over the table
  const lamp = grp(cyl(0.008, 0.008, 0.7, toon('#222'), [0, -0.35, 0]), cyl(0.12, 0.3, 0.22, toon('#2a2a30'), [0, -0.8, 0]), noOutline(sph(0.07, flat('#fff2d0'), [0, -0.9, 0])));
  g.add(at(lamp, [0, H, 0])); const pl = new THREE.PointLight('#ffd9a0', 3.2, 7, 1.5); pl.position.set(0, H - 1.0, 0); g.add(pl); g.add(fogOff(glow(1.4, 1.4, '#ffd9a0', 0.4, [0, H - 0.95, 0])));
  const hallLight = new THREE.PointLight('#ffe2b8', 0.8, 4, 1.6); hallLight.position.set(-2.8, 2.2, 1.0); g.add(hallLight);
  const set = makeSet(g, {
    mood: 'night', moodOverride: { bg: '#0a0c18', amb: ['#8a7a7a', 0.9], hemi: ['#ffe2c0', '#2a2430', 0.55], key: ['#9fb0ff', 0.35, [-2, 4, -4]] },
    pov: o.pov || [2.6, 1.6, 2.0], look: o.look || [0, 0.8, 0], targets: { door: [-W / 2, 1.2, 1.25], handle: [-W / 2 + 0.1, 1.02, 0.89], peephole: [-W / 2, 1.58, 1.25], table: [0, 0.85, 0], ...(o.targets || {}) },
    onUpdate(v, t, S) { fd.handle.rotation.z = (v.handle ?? 0) * rad(38); pl.intensity = 3.2 * (v.lamp ?? 1); o.onUpdate?.(v, t, S); },
  });
  set.parts = { door: fd, chairs };
  return set;
}

// ---------------------------------------------------------------------------------------------- outside the front door at night (seen through the peephole)
// The door is at x = 0 facing +x; the peephole camera sits at (0.05, 1.58, 0). The visitor stands on the porch at +x.
export function porch(o = {}) {
  const g = new THREE.Group();
  g.add(plane(30, 30, lam('#3a3e4a'), [8, 0, 0], [-Math.PI / 2, 0, 0])); g.add(box(2.4, 0.16, 2.6, lam('#8a8478'), [1.0, 0.08, 0]));
  g.add(at(plane(10, 3.2, lam('#b8a890'), [0, 1.6, 0], [0, Math.PI / 2, 0]))); g.add(box(0.12, 2.4, 1.3, lam('#e8e2d6'), [-0.02, 1.2, 0]));
  g.add(at(box(0.5, 0.02, 0.8, toon('#6a4a3a')), [0.5, 0.17, 0])); g.add(at(sign('WILLKOMMEN', 0.46, 0.12, { bg: '#6a4a3a', fg: '#e8d8b8', weight: 800, size: 0.7 }), [0.5, 0.185, 0], [-Math.PI / 2, 0, Math.PI / 2]));
  const lampG = grp(box(0.16, 0.24, 0.12, toon('#2a2a30')), noOutline(box(0.12, 0.18, 0.02, flat('#ffe2a8'), [0, 0, 0.065]))); g.add(at(lampG, [0.02, 2.35, 0.75], [0, Math.PI / 2, 0]));
  g.add(fogOff(glow(1.4, 1.4, '#ffd9a0', 0.55, [0.12, 2.35, 0.75], [0, Math.PI / 2, 0])));
  const pl = new THREE.PointLight('#ffd49a', 3.4, 6, 1.4); pl.position.set(0.4, 2.3, 0.7); g.add(pl);
  // front garden, fence, a street lamp and dark houses across the road
  for (let z = -4; z <= 4; z += 0.5) if (Math.abs(z) > 0.8) g.add(box(0.08, 0.9, 0.08, toon('#d8d2c4'), [4.2, 0.45, z])); g.add(box(0.06, 0.06, 8.2, toon('#d8d2c4'), [4.2, 0.82, 0]));
  for (const [x, z, w] of [[12, -5, 6], [12, 3, 7], [13, 11, 6]]) { g.add(box(4, 4, w, lam('#2a2e3e'), [x, 2, z])); g.add(noOutline(box(0.02, 0.8, 0.7, flat(z > 2 ? '#e8c27a' : '#1a1e2c'), [x - 2.02, 2.2, z]))); }
  const sl = grp(cyl(0.05, 0.07, 4, toon('#2a2d3a'), [0, 2, 0]), noOutline(box(0.3, 0.08, 0.16, flat('#ffe4b0'), [-0.25, 3.95, 0]))); g.add(at(sl, [7.5, 0, -2.5])); g.add(fogOff(glow(2.4, 2.4, '#ffd8a0', 0.4, [7.2, 3.9, -2.5], [0, -Math.PI / 2, 0])));
  const set = makeSet(g, {
    mood: 'night', moodOverride: { bg: '#0a0e1c', amb: ['#5a608a', 1.0], hemi: ['#8a90c8', '#1a1a2a', 0.6], key: ['#9fb0ff', 0.3, [5, 5, 2]] },
    pov: o.pov || [0.05, 1.58, 0], look: o.look || [3, 1.4, 0], targets: o.targets || {}, onUpdate: o.onUpdate,
  });
  set.scene.fog = new THREE.Fog('#0a0e1c', 4, 22);
  return set;
}
// peephole: black ring with a soft edge around a circle in the frame centre
export function peepholeOverlay(ctx, w, h) {
  const cx = w * 0.5, cy = h * 0.47, r = w * 0.62; ctx.save();
  const gr = ctx.createRadialGradient(cx, cy, r * 0.74, cx, cy, r); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,0.85)');
  ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.rect(0, 0, w, h); ctx.arc(cx, cy, r, 0, Math.PI * 2, true); ctx.fillStyle = '#000'; ctx.fill('evenodd');
  ctx.restore();
}

// ---------------------------------------------------------------------------------------------- back alley at night (episode 2)
// House back wall at z = -2 with the back door at x = 0. The alley runs to -x; the street crosses at x = -16 where a white van
// is parked. A building on the other side (z = +2.6) has an open cellar entrance at x -10..-9 with stairs going down (+z, -y).
export function alley(o = {}) {
  const g = new THREE.Group(), ZH = -2, ZB = 2.6;
  const asph = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); const r = rng(3); for (let i = 0; i < 700; i++) { x.fillStyle = `rgba(20,20,40,${0.05 + r() * 0.12})`; x.fillRect(r() * 256, r() * 256, 2, 2); } }), 20, 10);
  g.add(plane(70, 22.6, new THREE.MeshLambertMaterial({ color: '#3e4254', map: asph }), [-12, 0, -8.7], [-Math.PI / 2, 0, 0]));
  const brick = texRep(canvasTex(256, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 128); x.strokeStyle = 'rgba(40,20,20,0.25)'; x.lineWidth = 3; for (let r = 0; r < 4; r++) { x.beginPath(); x.moveTo(0, r * 32); x.lineTo(256, r * 32); x.stroke(); for (let c = 0; c < 4; c++) { const xx = c * 64 + (r % 2) * 32; x.beginPath(); x.moveTo(xx, r * 32); x.lineTo(xx, r * 32 + 32); x.stroke(); } } }), 8, 3);
  const houseM = new THREE.MeshLambertMaterial({ color: '#8a6a5a', map: brick }), oppM = new THREE.MeshLambertMaterial({ color: '#6a6a7a', map: brick.clone() });
  g.add(box(22, 6, 0.4, houseM, [-5, 3, ZH - 0.2])); g.add(box(13, 6, 0.4, oppM, [-2.5, 3, ZB + 0.2])); g.add(box(6, 6, 0.4, oppM, [-13, 3, ZB + 0.2]));
  g.add(box(1.0, 6 - 2.3, 0.4, oppM, [-9.5, 2.3 + (6 - 2.3) / 2, ZB + 0.2]));
  for (const [x, y] of [[-3, 3.6], [-7, 3.6], [3, 3.6], [-11, 3.6]]) { g.add(box(1.0, 1.1, 0.05, toon('#2a2a3a'), [x, y, ZH + 0.03])); g.add(noOutline(box(0.9, 1.0, 0.02, flat(x === -7 ? '#e8c27a' : '#1a1e2c'), [x, y, ZH + 0.05]))); }
  // back door (opens outward toward +z, hinge on the -x side)
  g.add(box(1.25, 2.35, 0.1, toon('#3a3a44'), [0, 1.175, ZH + 0.02])); g.add(noOutline(box(1.0, 2.1, 0.02, flat('#ffd9a0'), [0, 1.05, ZH + 0.04])));
  const bd = new THREE.Group(); bd.position.set(-0.5, 0, ZH + 0.08); bd.add(box(1.0, 2.1, 0.05, toon('#5a6a7a'), [0.5, 1.05, 0])); bd.add(box(0.05, 0.16, 0.05, toon('#c8c8d0'), [0.88, 1.0, 0.04])); g.add(bd);
  const doorLight = new THREE.PointLight('#ffd9a0', 0, 5, 1.5); doorLight.position.set(0, 1.4, ZH + 0.6); g.add(doorLight); g.add(at(box(0.3, 0.2, 0.2, toon('#2a2a30')), [0.9, 2.6, ZH + 0.1])); const wallLamp = new THREE.PointLight('#ffe0b0', 1.8, 7, 1.5); wallLamp.position.set(0.9, 2.5, ZH + 0.5); g.add(wallLamp); g.add(fogOff(glow(1.2, 1.2, '#ffe0b0', 0.5, [0.9, 2.5, ZH + 0.25])));
  // the dumpster
  const dump = new THREE.Group(); dump.add(rbox(1.7, 1.15, 1.05, 0.04, toon('#3f6a4a'), [0, 0.68, 0])); dump.add(rbox(1.76, 0.08, 1.12, 0.03, toon('#2f4a38'), [0, 1.28, 0])); for (const dx of [-0.65, 0.65]) for (const dz of [-0.35, 0.35]) dump.add(cyl(0.08, 0.08, 0.06, toon('#1a1a20'), [dx, 0.08, dz], [Math.PI / 2, 0, 0]));
  g.add(dump);
  // bins, crates, a fence at the end of the house
  g.add(cyl(0.28, 0.25, 0.9, toon('#5a5a6a'), [3.2, 0.45, ZH + 0.5])); g.add(cyl(0.28, 0.25, 0.9, toon('#4a5a8a'), [3.8, 0.45, ZH + 0.5])); g.add(box(0.6, 0.45, 0.45, toon('#8a6a44'), [-5.5, 0.22, ZB - 0.4]));
  // the cellar entrance: an open door at x -10..-9 and stairs going down behind it
  const cd = new THREE.Group(); cd.position.set(-9.0, 0, ZB - 0.02); cd.add(box(1.0, 2.25, 0.06, toon('#4a3a32'), [-0.5, 1.125, 0])); cd.add(box(0.05, 0.14, 0.05, toon('#a8a8b0'), [-0.88, 1.05, -0.04])); g.add(cd);
  g.add(box(1.2, 0.2, 0.42, toon('#2a2a30'), [-9.5, 2.35, ZB + 0.2])); const gap = noOutline(box(0.95, 0.025, 0.02, flat('#c8d0ff'), [-9.5, 0.012, ZB + 0.06])); g.add(gap);
  const stairM = lam('#4a4a56');
  for (let i = 0; i < 12; i++) g.add(box(1.0, 0.2, 0.3, stairM, [-9.5, -0.1 - i * 0.2, ZB + 0.55 + i * 0.3]));
  g.add(box(0.2, 6, 4.5, stairM, [-10.1, -0.5, ZB + 2.3])); g.add(box(0.2, 6, 4.5, stairM, [-8.9, -0.5, ZB + 2.3])); g.add(box(1.4, 0.2, 2.0, stairM, [-9.5, -2.5, ZB + 4.6])); g.add(box(1.4, 4, 0.2, stairM, [-9.5, -0.6, ZB + 5.6]));
  g.add(box(1.4, 0.2, 4.6, stairM, [-9.5, 2.5, ZB + 2.3]));
  const lowDoor = grp(box(0.9, 2.0, 0.06, toon('#3a3430')), box(0.05, 0.12, 0.05, toon('#9a9aa0'), [0.33, 0, 0.04])); g.add(at(lowDoor, [-9.5, -1.4, ZB + 5.48]));
  // the street at the end: a lamp, the white van with a loudspeaker horn on its roof
  g.add(box(0.3, 0.15, 30, lam('#7a7a8a'), [-16.2, 0.07, 0])); const sl = grp(cyl(0.06, 0.08, 5, toon('#2a2d3a'), [0, 2.5, 0]), noOutline(box(0.4, 0.1, 0.2, flat('#ffe4b0'), [0.3, 4.95, 0]))); g.add(at(sl, [-17.2, 0, 2.6])); const slL = new THREE.PointLight('#ffe0b0', 3.0, 11, 1.4); slL.position.set(-17.0, 4.6, 2.2); g.add(slL); g.add(fogOff(glow(2.8, 2.8, '#ffe0b0', 0.45, [-16.9, 4.85, 2.6], [0, Math.PI / 2, 0])));
  const van = new THREE.Group(); const wM = toon('#e8eaee');
  van.add(rbox(4.2, 2.1, 2.0, 0.08, wM, [0, 1.35, 0])); van.add(rbox(1.4, 1.5, 1.95, 0.1, wM, [2.7, 1.05, 0])); van.add(noOutline(box(0.05, 0.6, 1.7, flat('#1a1e2c'), [3.38, 1.45, 0])));
  for (const s of [-1, 1]) van.add(noOutline(box(0.8, 0.55, 0.03, flat('#1a1e2c'), [2.7, 1.45, s * 0.99])));
  for (const x of [-1.3, 2.4]) for (const s of [-1, 1]) van.add(cyl(0.38, 0.38, 0.25, toon('#1a1a20'), [x, 0.38, s * 0.9], [Math.PI / 2, 0, 0]));
  van.add(noOutline(box(3.0, 0.4, 0.02, flat('#c8cad0'), [-0.3, 1.0, 1.005]))); const horn = grp(cyl(0.05, 0.05, 0.4, toon('#3a3a44'), [0, 0.2, 0]), at(cyl(0.12, 0.32, 0.5, toon('#d8d8de')), [0.2, 0.42, 0], [0, 0, -Math.PI / 2])); van.add(at(horn, [0.6, 2.4, 0]));
  g.add(at(van, [-20.0, 0, 0.4], [0, Math.PI, 0]));
  const set = makeSet(g, {
    mood: 'night', moodOverride: { bg: '#090b16', amb: ['#5a608a', 1.1], hemi: ['#8a90c8', '#1a1a2a', 0.7], key: ['#9fb0ff', 0.45, [-6, 6, 4]], spill: ['#ffd9a0', 0] },
    pov: o.pov || [-3, 1.4, 0.8], look: o.look || [0, 1.1, -2], targets: { backDoor: [0, 1.1, ZH], dumpster: [0.6, 0.9, -1.3], van: [-20, 1.3, 0.4], horn: [-20.6, 2.6, 0.4], cellar: [-9.5, 1.1, ZB], stairUp: [-9.5, 0.8, ZB + 0.2], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      bd.rotation.y = -(v.backDoor ?? 0) * rad(105); doorLight.intensity = 2.5 * (v.backDoor ?? 0);
      dump.position.set(lerp(1.45, 0.05, v.dump ?? 0), 0, -1.38); cd.rotation.y = -(v.cellarDoor ?? 1) * rad(95); gap.visible = (v.cellarDoor ?? 1) < 0.05;
      const dk = 1 - (v.dark ?? 0); slL.intensity = 3.0 * dk; wallLamp.intensity = 1.8 * dk; S.parts.amb ||= S.scene.children.find(c => c.isAmbientLight); S.parts.hemi ||= S.scene.children.find(c => c.isHemisphereLight); S.parts.key ||= S.scene.children.find(c => c.isDirectionalLight);
      S.parts.amb.intensity = 1.1 * dk + 0.02; S.parts.hemi.intensity = 0.7 * dk; S.parts.key.intensity = 0.45 * dk;
      o.onUpdate?.(v, t, S);
    },
  });
  set.scene.fog = new THREE.Fog('#090b16', 6, 32); set.parts = { dump, van, cd };
  return set;
}

// ---------------------------------------------------------------------------------------------- cellar + ventilation shaft (episodes 3 and 4)
// Cellar x -3.5..3, z -2.5..2.5, dark concrete. A wire-mesh storage cage in the corner (x 1.8..3, z -2.5..0) with a grid door
// at z -1.0..-0.1. A low vent opening in the x = 3 wall at z 1.5, y 0.12..0.82, leading into a square shaft that runs along +x to an outer
// grille at x = 9 with daylight behind it. A maintenance hatch on the shaft's +z wall at x 6.4..7.1 opens into a flat drain pipe.
export function cellar(o = {}) {
  const g = new THREE.Group(), conc = lam('#6a6a72'), concD = lam('#4a4a54');
  const ct = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); const r = rng(6); for (let i = 0; i < 400; i++) { x.fillStyle = `rgba(30,30,40,${0.04 + r() * 0.1})`; x.beginPath(); x.arc(r() * 256, r() * 256, 1 + r() * 5, 0, 7); x.fill(); } }), 4, 4);
  const floorM = new THREE.MeshLambertMaterial({ color: '#5a5a62', map: ct });
  g.add(plane(6.5, 5, floorM, [-0.25, 0, 0], [-Math.PI / 2, 0, 0])); g.add(plane(6.5, 5, concD, [-0.25, 2.4, 0], [Math.PI / 2, 0, 0]));
  g.add(plane(6.5, 2.4, conc, [-0.25, 1.2, -2.5])); g.add(plane(6.5, 2.4, conc, [-0.25, 1.2, 2.5], [0, Math.PI, 0])); g.add(plane(5, 2.4, conc, [-3.5, 1.2, 0], [0, Math.PI / 2, 0]));
  // the x = 3 wall with the vent opening (z 1.1..1.9, y 0.12..0.82)
  for (const [z0, z1] of [[-2.5, 1.1], [1.9, 2.5]]) g.add(at(plane(z1 - z0, 2.4, conc), [3, 1.2, (z0 + z1) / 2], [0, -Math.PI / 2, 0]));
  g.add(at(plane(0.8, 2.4 - 0.82, conc), [3, 0.82 + (2.4 - 0.82) / 2, 1.5], [0, -Math.PI / 2, 0])); g.add(at(plane(0.8, 0.12, conc), [3, 0.06, 1.5], [0, -Math.PI / 2, 0]));
  // pipes, boxes, shelves, a furnace
  g.add(cyl(0.06, 0.06, 6.4, toon('#8a6a4a'), [-0.25, 2.2, -2.3], [0, 0, Math.PI / 2])); g.add(cyl(0.04, 0.04, 6.4, toon('#6a7a8a'), [-0.25, 2.05, -2.35], [0, 0, Math.PI / 2]));
  for (const [x, z, s, c, y0 = 0] of [[-2.9, -2.0, 0.6, '#8a6a44'], [-2.9, -1.3, 0.5, '#7a5a3a'], [-2.6, 2.0, 0.55, '#8a6a44'], [0.9, 1.9, 0.5, '#7a5a3a'], [0.3, 2.05, 0.4, '#8a6a44'], [0.9, 1.9, 0.45, '#9a7a54', 0.5]]) g.add(box(s, s, s, toon(c), [x, y0 + s / 2, z]));
  g.add(box(0.9, 1.6, 0.8, toon('#5a5a66'), [-3.0, 0.8, 0.4])); g.add(cyl(0.12, 0.12, 0.8, toon('#4a4a54'), [-3.0, 2.0, 0.4]));
  // wire-mesh cage with a grid door
  const mesh = canvasTex(128, 128, x => { x.clearRect(0, 0, 128, 128); x.strokeStyle = '#c8c8d0'; x.lineWidth = 5; for (let i = 0; i <= 128; i += 16) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i, 128); x.stroke(); x.beginPath(); x.moveTo(0, i); x.lineTo(128, i); x.stroke(); } });
  const meshM = new THREE.MeshLambertMaterial({ map: texRep(mesh, 6, 6), transparent: true, alphaTest: 0.4, side: THREE.DoubleSide });
  const frameM = toon('#7a7a86');
  g.add(noOutline(at(plane(1.5, 2.2, meshM), [1.8, 1.1, -1.75], [0, Math.PI / 2, 0]))); g.add(noOutline(at(plane(1.2, 2.2, meshM), [2.4, 1.1, 0.0])));
  for (const [x, z] of [[1.8, -2.5], [1.8, -1.0], [1.8, 0], [3.0, 0], [1.8, -0.1]]) g.add(box(0.06, 2.2, 0.06, frameM, [x, 1.1, z]));
  g.add(box(0.06, 0.06, 2.5, frameM, [1.8, 2.2, -1.25])); g.add(box(1.2, 0.06, 0.06, frameM, [2.4, 2.2, 0]));
  const gdoor = new THREE.Group(); gdoor.position.set(1.8, 0, -1.0); gdoor.add(noOutline(at(plane(0.9, 2.1, new THREE.MeshLambertMaterial({ map: texRep(mesh.clone(), 4, 9), transparent: true, alphaTest: 0.4, side: THREE.DoubleSide })), [0, 1.08, 0.45], [0, Math.PI / 2, 0])));
  gdoor.add(box(0.05, 2.1, 0.05, frameM, [0, 1.08, 0.9])); gdoor.add(box(0.05, 0.05, 0.9, frameM, [0, 2.12, 0.45])); gdoor.add(box(0.05, 0.05, 0.9, frameM, [0, 0.05, 0.45])); gdoor.add(box(0.08, 0.12, 0.04, toon('#3a3a40'), [-0.03, 1.0, 0.8])); g.add(gdoor);
  // vent cover (comes off), the shaft, the outer grille, daylight
  const cover = grp(box(0.06, 0.74, 0.84, toon('#9a9aa4')), ...[0, 1, 2, 3, 4, 5].map(i => box(0.07, 0.04, 0.78, toon('#6a6a74'), [0.01, -0.28 + i * 0.11, 0]))); cover.position.set(2.96, 0.47, 1.5); g.add(cover);
  const shaftM = new THREE.MeshLambertMaterial({ color: '#8a8e9a', side: THREE.DoubleSide }), seamM = toon('#6a6e78');
  const SX0 = 3.0, SX1 = 9.0, SL = SX1 - SX0, SC = (SX0 + SX1) / 2;
  g.add(plane(SL, 0.8, shaftM, [SC, 0.12, 1.5], [-Math.PI / 2, 0, 0])); g.add(plane(SL, 0.8, shaftM, [SC, 0.82, 1.5], [Math.PI / 2, 0, 0])); g.add(plane(SL, 0.7, shaftM, [SC, 0.47, 1.1]));
  for (const [x0, x1] of [[SX0, 5.15], [5.85, SX1]]) g.add(plane(x1 - x0, 0.7, shaftM, [(x0 + x1) / 2, 0.47, 1.9], [0, Math.PI, 0]));
  g.add(plane(0.7, 0.7, lam('#2a2e38'), [5.5, 0.47, 2.6], [0, Math.PI, 0])); for (const s2 of [-1, 1]) g.add(plane(0.7, 0.7, lam('#3a3e48'), [5.5 + s2 * 0.35, 0.47, 2.25], [0, -s2 * Math.PI / 2, 0])); g.add(plane(0.7, 0.7, lam('#3a3e48'), [5.5, 0.12, 2.25], [-Math.PI / 2, 0, 0]));
  for (let x = 3.6; x < 9; x += 0.6) { g.add(box(0.03, 0.02, 0.8, seamM, [x, 0.13, 1.5])); g.add(box(0.03, 0.7, 0.02, seamM, [x, 0.47, 1.11])); g.add(box(0.03, 0.02, 0.8, seamM, [x, 0.81, 1.5])); }
  const hatch = new THREE.Group(); hatch.position.set(5.15, 0.12, 1.89); hatch.add(box(0.7, 0.7, 0.03, toon('#7a7e8a'), [0.35, 0.35, 0])); hatch.add(box(0.12, 0.04, 0.04, toon('#3a3a40'), [0.6, 0.35, -0.03])); g.add(hatch);
  const grille = new THREE.Group(); for (let i = 0; i < 7; i++) grille.add(box(0.03, 0.7, 0.03, toon('#5a5e68'), [SX1, 0.47, 1.17 + i * 0.11])); for (const y of [0.15, 0.47, 0.79]) grille.add(box(0.03, 0.03, 0.8, toon('#5a5e68'), [SX1, y, 1.5])); g.add(grille);
  const day = noOutline(plane(1.4, 1.2, flat('#f4f6ff'), [SX1 + 0.6, 0.5, 1.5], [0, -Math.PI / 2, 0])); g.add(day); g.add(fogOff(glow(2.4, 2.0, '#fff6e0', 0.85, [SX1 + 0.1, 0.5, 1.5], [0, -Math.PI / 2, 0])));
  const dayLight = new THREE.PointLight('#fff2dc', 2.2, 7, 1.1); dayLight.position.set(SX1 + 0.6, 0.6, 1.5); g.add(dayLight);
  // the hand outside that grabs the grille: a blue sleeve and a block hand
  const arm = grp(rbox(0.6, 0.14, 0.14, 0.03, toon('#2f5fb8'), [0.35, 0, 0]), rbox(0.12, 0.13, 0.12, 0.035, toon('#e9b999'), [0.0, 0, 0]), ...[0, 1, 2].map(i => box(0.04, 0.12, 0.03, toon('#e9b999'), [-0.05, -0.02, -0.035 + i * 0.035])));
  arm.position.set(SX1 + 0.12, 0.66, 1.42); arm.rotation.z = -0.55; g.add(arm); const armFill = new THREE.PointLight('#cfd8ff', 0.9, 2.5, 1.2); armFill.position.set(SX1 - 0.9, 0.7, 1.4); g.add(armFill);
  // the phone light: a spot with a visible beam
  const spot = new THREE.SpotLight('#eef2ff', 0, 9, rad(24), 0.5, 1.2); g.add(spot); g.add(spot.target);
  const beamTex = canvasTex(8, 128, x => { const gr = x.createLinearGradient(0, 0, 0, 128); gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(1, 'rgba(255,255,255,1)'); x.fillStyle = gr; x.fillRect(0, 0, 8, 128); });
  const beam = noOutline(new THREE.Mesh(new THREE.CylinderGeometry(0.02, 1.4, 4.5, 24, 1, true), new THREE.MeshBasicMaterial({ map: beamTex, color: '#dfe6ff', transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false })));
  beam.geometry.translate(0, -2.25, 0); beam.geometry.rotateX(-Math.PI / 2); g.add(beam);
  const flare = fogOff(glow(0.5, 0.5, '#ffffff', 0, [0, 0, 0])); g.add(flare);
  const set = makeSet(g, {
    mood: 'dark', moodOverride: { bg: '#030308', amb: ['#3a3e5a', 0.8], hemi: ['#4a5078', '#0a0a12', 0.45], key: ['#7f8cff', 0.12, [1, 5, 3]], spill: ['#fff', 0] },
    pov: o.pov || [-2.5, 1.4, 0.5], look: o.look || [2, 1.2, -0.6], targets: { gridDoor: [1.8, 1.2, -0.55], vent: [3.0, 0.47, 1.5], grille: [SX1, 0.5, 1.5], hatch: [5.5, 0.47, 1.9], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      const L = v.phone ?? 0; spot.intensity = 9 * L; beam.material.opacity = 0.09 * L; flare.material.opacity = 0.9 * L;
      if (o.phoneAt) { const [p, q] = o.phoneAt(t); spot.position.set(...p); spot.target.position.set(...q); beam.position.set(...p); beam.lookAt(...q); flare.position.set(...p); }
      cover.position.set(lerp(2.96, 2.2, v.cover ?? 0), lerp(0.47, 0.37, v.cover ?? 0), lerp(1.5, 0.9, v.cover ?? 0)); cover.rotation.y = (v.cover ?? 0) * 0.9; cover.rotation.z = (v.cover ?? 0) * 1.45;
      const a = v.arm ?? 0; arm.visible = a > 0.01; arm.position.x = lerp(SX1 + 0.9, SX1 + 0.12, a); hatch.rotation.y = -(v.hatch ?? 0) * rad(100);
      dayLight.intensity = 2.2 * (v.day ?? 1); gdoor.rotation.y = (v.gdoor ?? 0) * rad(70);
      o.onUpdate?.(v, t, S);
    },
  });
  set.scene.fog = new THREE.Fog('#030308', 5, 14); set.parts = { cover, hatch, grille, arm, spot };
  return set;
}

// ---------------------------------------------------------------------------------------------- riverbank with a drain outlet (episode 4)
// River along x at z -20..-4; this bank z > -4 (ground y 0). A concrete embankment wall at z = 6 with a round drain outlet at x 0
// (centre y 0.55, radius 0.45) and a grille door. The pipe runs into the embankment (+z). Far bank z < -20.
export function riverbank(o = {}) {
  const g = new THREE.Group();
  const grass = texRep(canvasTex(128, 128, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 128); const r = rng(12); for (let i = 0; i < 500; i++) { x.fillStyle = `rgba(30,50,30,${0.06 + r() * 0.14})`; x.fillRect(r() * 128, r() * 128, 1.5, 4); } }), 20, 8);
  g.add(plane(80, 10, new THREE.MeshLambertMaterial({ color: '#7a8a6a', map: grass }), [0, 0, 1.0], [-Math.PI / 2, 0, 0]));
  g.add(at(plane(80, 2.2, lam('#8a8270')), [0, -0.5, -4.6], [-1.1, 0, 0]));
  const waterTex = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); const r = rng(21); for (let i = 0; i < 120; i++) { x.strokeStyle = `rgba(255,255,255,${0.2 + r() * 0.5})`; x.lineWidth = 2; const y = r() * 256, x0 = r() * 256; x.beginPath(); x.moveTo(x0, y); x.lineTo(x0 + 20 + r() * 40, y); x.stroke(); } x.globalCompositeOperation = 'multiply'; x.fillStyle = '#9aa8b8'; x.fillRect(0, 0, 256, 256); }), 12, 4);
  g.add(noOutline(plane(120, 18, new THREE.MeshLambertMaterial({ color: '#5a6a80', map: waterTex }), [0, -0.9, -12], [-Math.PI / 2, 0, 0])));
  g.add(plane(120, 30, new THREE.MeshLambertMaterial({ color: '#6a7a5a', map: grass.clone() }), [0, 0.2, -36], [-Math.PI / 2, 0, 0])); g.add(at(plane(120, 2.0, lam('#7a7464')), [0, -0.35, -20.4], [-1.9, 0, 0]));
  for (const [x, z, h] of [[-9, -26, 5], [-4, -29, 6.5], [6, -27, 5.5], [12, -30, 6], [-15, -31, 7]]) { g.add(cyl(0.18, 0.24, h * 0.45, toon('#4a3a2a'), [x, 0.2 + h * 0.22, z])); g.add(sameId(grp(sph(h * 0.25, toon('#4a5a40'), [x, h * 0.6, z]), sph(h * 0.2, toon('#4a5a40'), [x + h * 0.15, h * 0.52, z + 0.2])))); }
  // embankment wall with the outlet, the pipe going in
  const concM = lam('#9a9a96');
  g.add(box(30, 3, 0.6, concM, [-15.0 - 0.6, 1.5, 6.3])); g.add(box(30, 3, 0.6, concM, [15.0 + 0.6, 1.5, 6.3])); g.add(box(1.2, 3 - 1.15, 0.6, concM, [0, 1.15 + (3 - 1.15) / 2, 6.3]));
  g.add(box(1.2, 0.05, 0.6, concM, [0, 0.025, 6.3]));
  g.add(at(new THREE.Mesh(new THREE.CylinderGeometry(0.47, 0.47, 10, 24, 1, true), new THREE.MeshLambertMaterial({ color: '#6a6a70', side: THREE.BackSide })), [0, 0.6, 11.0], [Math.PI / 2, 0, 0]));
  g.add(at(torus(0.5, 0.06, toon('#7a7a78')), [0, 0.6, 6.0]));
  g.add(noOutline(at(plane(1.0, 1.0, flat('#05060a')), [0, 0.6, 15.9], [0, Math.PI, 0])));
  g.add(box(30, 3, 4, lam('#7a8270'), [0, 1.5, 8.6])); g.add(box(80, 4, 6, lam('#8a8c80'), [0, 2.0, 13.0]));
  for (const [x, w, h, c] of [[-12, 5, 7, '#9a8a7a'], [-5, 6, 9, '#8a8a96'], [4, 5, 6, '#a08a78'], [11, 7, 8, '#8a9098']]) g.add(box(w, h, 4, lam(c), [x, 4 + h / 2, 14]));
  const gdoor = new THREE.Group(); gdoor.position.set(-0.55, 0.05, 5.92); for (let i = 0; i < 7; i++) gdoor.add(box(0.035, 1.1, 0.035, toon('#4a4e58'), [0.1 + i * 0.15, 0.55, 0])); for (const y of [0.1, 0.55, 1.0]) gdoor.add(box(1.1, 0.035, 0.035, toon('#4a4e58'), [0.55, y, 0])); g.add(gdoor);
  const latch = box(0.08, 0.12, 0.08, toon('#2a2a30'), [0.6, 0.55, 5.9]); g.add(latch);
  const hands = []; for (const [i, c] of [[0, '#2f5fb8'], [1, '#3f8f4f'], [2, '#c23a3a']]) { const a = grp(rbox(0.12, 0.12, 0.6, 0.03, toon(c), [0, 0, 0.3]), rbox(0.12, 0.11, 0.12, 0.035, toon(['#e9b999', '#8a5a3c', '#c98f68'][i]), [0, 0, -0.02])); a.position.set(-0.25 + i * 0.25, 0.45 + (i % 2) * 0.25, 6.6); g.add(a); hands.push(a); }
  const set = makeSet(g, {
    mood: 'day', moodOverride: { bg: '#a8b0c0', amb: ['#c8ccd8', 1.25], hemi: ['#dfe6f2', '#6a6a60', 0.8], key: ['#fff0dc', 0.7, [-3, 6, -4]] },
    pov: o.pov || [2.5, 1.4, 2.0], look: o.look || [0, 0.6, 6], targets: { outlet: [0, 0.6, 6.0], river: [0, 0.2, -12], farBank: [0, 1.4, -21.5], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      waterTex.offset.x = t * 0.05; gdoor.rotation.y = -(v.grille ?? 1) * rad(100);
      hands.forEach((h, i) => { const a = clamp((v.hands ?? 0) * 1.2 - i * 0.12); h.position.z = lerp(6.9, 5.75, a); h.position.x = -0.25 + i * 0.25 + Math.sin(t * 9 + i) * 0.02 * a; });
      S.parts.amb ||= S.scene.children.find(c => c.isAmbientLight); S.parts.amb.intensity = 1.25 * (1 - 0.4 * (v.dim ?? 0));
      o.onUpdate?.(v, t, S);
    },
  });
  set.scene.fog = new THREE.Fog('#a8b0c0', 12, 60); set.parts = { gdoor, hands };
  return set;
}
