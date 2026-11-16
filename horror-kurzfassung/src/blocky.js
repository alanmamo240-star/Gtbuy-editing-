// Blocky game-style character (block head with a face on its front, block torso, block limbs with elbows and knees).
// Same interface as makeToon() in toon.js, so core.js can direct it: reset size place pose face lookAt idle talk walk run hide.
// Proportions match the kit's toon (hip 0.83, head centre ~0.77 above the hip) so all POSES work unchanged.
// height 1 = 1.72 m adult, 0.85-0.92 = teenager.
import { THREE, toon, flat, box, rbox, sph, cyl, disc, torus, grp, at, noOutline, sameId, rad, lerp, clamp, noise, rng } from './util.js';
import { POSES, getPose, SKIN } from './toon.js';

const BASE = POSES.stand;
const HW = 0.36, HH = 0.34, HD = 0.33;           // head block
function mixPose(a, b, t) { const o = {}; for (const k in BASE) { const x = a[k] ?? BASE[k], y = b[k] ?? x; o[k] = Array.isArray(x) ? x.map((v, i) => lerp(v, y[i] ?? v, t)) : lerp(x, y, t); } return o; }

function hairMesh(style, color, seed) {
  const m = toon(color), g = new THREE.Group(), r = rng(seed);
  const top = (h = 0.1, back = 0.05) => g.add(rbox(HW + 0.03, h, HD + 0.03 + back, 0.03, m, [0, HH / 2 - h / 2 + 0.03, -back / 2]));
  if (style === 'bald') return g;
  if (style === 'buzz') { top(0.06, 0.0); return sameId(g); }
  top(0.1, 0.03);
  g.add(rbox(HW + 0.03, HH * 0.62, 0.06, 0.025, m, [0, HH * 0.12, -HD / 2 - 0.015]));                     // back of the head
  if (style === 'short' || style === 'spiky' || style === 'swoop' || style === 'curly') for (const s of [-1, 1]) g.add(rbox(0.045, 0.13, HD * 0.55, 0.015, m, [s * (HW / 2 + 0.012), HH * 0.2, -0.06]));
  if (style === 'swoop') g.add(at(rbox(HW * 0.72, 0.07, 0.07, 0.02, m), [-0.04, HH / 2 - 0.01, HD / 2 + 0.01], [0.3, 0, 0.18]));
  if (style === 'spiky') for (let i = 0; i < 6; i++) g.add(at(rbox(0.07, 0.11, 0.07, 0.01, m), [-0.13 + i * 0.052, HH / 2 + 0.06, -0.02 + (i % 2) * 0.05], [0.2 * (r() - 0.5), 0, 0.3 * (r() - 0.5)]));
  if (style === 'curly') for (let i = 0; i < 7; i++) g.add(rbox(0.09, 0.07, 0.09, 0.03, m, [-0.15 + i * 0.05, HH / 2 + 0.04, -0.06 + (i % 3) * 0.05]));
  if (style === 'long' || style === 'pigtails' || style === 'bob') { for (const s of [-1, 1]) g.add(rbox(0.05, style === 'bob' ? 0.26 : 0.22, HD * 0.8, 0.02, m, [s * (HW / 2 + 0.015), HH * 0.05, -0.03])); g.add(at(rbox(HW * 0.95, 0.06, 0.05, 0.02, m), [0, HH / 2 - 0.02, HD / 2 + 0.005])); }
  if (style === 'long') g.add(rbox(HW + 0.02, 0.36, 0.07, 0.03, m, [0, -0.08, -HD / 2 - 0.03]));
  if (style === 'pigtails') for (const s of [-1, 1]) { g.add(rbox(0.09, 0.09, 0.09, 0.03, m, [s * (HW / 2 + 0.07), -0.02, -0.06])); g.add(rbox(0.07, 0.2, 0.07, 0.03, m, [s * (HW / 2 + 0.075), -0.16, -0.06])); }
  if (style === 'bun') g.add(rbox(0.13, 0.11, 0.12, 0.04, m, [0, HH / 2 + 0.06, -0.11]));
  g.traverse(o => { o.userData.inkFlat = true; }); return sameId(g);
}

export function makeBlocky(o = {}) {
  const P = { skin: 'light', height: 1, hair: 'short', hairColor: '#3a2a22', top: '#d7a31f', topStyle: 'sweater', bottom: '#27306b', shoe: '#1c1f3d', inner: '#e8e4d8', seed: 1, eye: 1, ...o };
  const skinHex = SKIN[P.skin] || P.skin, sk = toon(skinHex), topM = toon(P.top), botM = toon(P.bottom), shoeM = toon(P.shoe), dark = flat('#14111c');
  const root = new THREE.Group(), body = new THREE.Group(), torsoG = new THREE.Group(); root.add(body); body.add(torsoG);
  // pelvis + torso
  body.add(rbox(0.42, 0.16, 0.22, 0.03, botM, [0, 0.02, 0]));
  torsoG.add(rbox(0.44, 0.5, 0.23, 0.035, topM, [0, 0.33, 0]));
  const lighter = c => toon(new THREE.Color(c).multiplyScalar(0.82).getHex());
  if (P.topStyle === 'jacket') { torsoG.add(noOutline(box(0.1, 0.44, 0.012, toon(P.inner), [0, 0.32, 0.12]))); torsoG.add(rbox(0.3, 0.07, 0.25, 0.02, topM, [0, 0.57, 0])); }
  if (P.topStyle === 'hoodie') { torsoG.add(rbox(0.3, 0.14, 0.12, 0.04, topM, [0, 0.52, -0.14])); torsoG.add(noOutline(box(0.24, 0.11, 0.012, lighter(P.top), [0, 0.17, 0.12]))); for (const s of [-1, 1]) torsoG.add(noOutline(box(0.012, 0.12, 0.012, toon('#e8e8ee'), [s * 0.05, 0.45, 0.122]))); }
  if (P.topStyle === 'coat') { torsoG.add(noOutline(box(0.012, 0.44, 0.012, lighter(P.top), [0, 0.32, 0.121]))); body.add(rbox(0.46, 0.34, 0.25, 0.03, topM, [0, -0.12, 0])); for (const y of [0.42, 0.3, 0.18]) torsoG.add(noOutline(box(0.025, 0.025, 0.01, dark, [0.04, y, 0.121]))); }
  if (P.topStyle === 'uniform') { torsoG.add(noOutline(box(0.09, 0.44, 0.012, toon(P.inner), [0, 0.32, 0.12]))); for (const y of [0.42, 0.3, 0.18]) torsoG.add(noOutline(box(0.026, 0.026, 0.012, flat('#d9b65a'), [0.065, y, 0.125]))); body.add(rbox(0.46, 0.22, 0.25, 0.03, topM, [0, -0.06, 0])); }
  if (P.scarf) torsoG.add(rbox(0.3, 0.07, 0.27, 0.03, toon(P.scarf), [0, 0.585, 0]));
  if (P.backpack) torsoG.add(rbox(0.34, 0.38, 0.14, 0.04, toon(P.backpack), [0, 0.32, -0.19]));
  const short = P.topStyle === 'tee';
  const mkArm = s => {
    const a = new THREE.Group(); a.position.set(0.29 * s, 0.53, 0);
    a.add(rbox(0.14, 0.3, 0.15, 0.03, topM, [0, -0.13, 0]));
    const e = new THREE.Group(); e.position.y = -0.26; a.add(e);
    e.add(rbox(0.13, 0.25, 0.14, 0.03, short ? sk : topM, [0, -0.11, 0]));
    const h = rbox(0.12, 0.11, 0.13, 0.035, sk, [0, -0.28, 0]); e.add(h);
    torsoG.add(a); return { a, e, h };
  };
  const armL = mkArm(1), armR = mkArm(-1);
  const mkLeg = s => {
    const l = new THREE.Group(); l.position.set(0.11 * s, 0, 0); l.add(rbox(0.2, 0.42, 0.21, 0.03, botM, [0, -0.19, 0]));
    const k = new THREE.Group(); k.position.y = -0.4; l.add(k); k.add(rbox(0.19, 0.38, 0.2, 0.03, botM, [0, -0.17, 0]));
    k.add(rbox(0.2, 0.08, 0.28, 0.03, shoeM, [0, -0.385, 0.04]));
    body.add(l); return { l, k };
  };
  const legL = mkLeg(1), legR = mkLeg(-1);
  // head: a rounded block with the face on its front
  const neck = new THREE.Group(); neck.position.set(0, 0.58, 0); torsoG.add(neck); neck.add(cyl(0.07, 0.07, 0.08, sk, [0, 0.02, 0]));
  const head = new THREE.Group(); head.position.set(0, 0.04 + HH / 2, 0); head.rotation.order = 'YXZ'; neck.add(head);
  head.add(rbox(HW, HH, HD, 0.06, sk));
  head.add(hairMesh(P.hair, P.hairColor, P.seed));
  if (P.cap) { const c = toon(P.cap); head.add(sameId(grp(rbox(HW + 0.05, 0.1, HD + 0.05, 0.03, c, [0, HH / 2 + 0.02, 0]), rbox(HW * 0.85, 0.025, 0.13, 0.01, c, [0, HH / 2 - 0.02, HD / 2 + 0.06], [0.12, 0, 0])))); }
  if (P.hat) { const c = toon(P.hat); head.add(sameId(grp(rbox(HW + 0.06, 0.16, HD + 0.06, 0.03, c, [0, HH / 2 + 0.06, 0]), rbox(HW * 0.9, 0.025, 0.14, 0.01, flat('#101018'), [0, HH / 2 - 0.02, HD / 2 + 0.06], [0.08, 0, 0])))); head.add(noOutline(rbox(0.06, 0.04, 0.012, 0.006, flat('#d9b65a'), [0, HH / 2 + 0.07, HD / 2 + 0.035]))); }
  if (P.glasses) { const gl = new THREE.Group(); for (const s of [-1, 1]) gl.add(torus(0.042, 0.008, dark, [s * 0.075, 0.03, HD / 2 + 0.012])); gl.add(box(0.07, 0.01, 0.01, dark, [0, 0.035, HD / 2 + 0.012])); head.add(noOutline(gl)); }
  // face features (flat decals, no ink): white eyes with black pupils, brows, a mouth that changes shape
  const FZ = HD / 2 + 0.004, eyes = [], pupils = [], brows = [];
  for (const s of [1, -1]) {
    const eg = new THREE.Group(); eg.position.set(0.075 * s, 0.03, FZ);
    const w = noOutline(sph(0.045, flat('#f6f4ee'), null, [0.85 * P.eye, 1.1 * P.eye, 0.12])); eg.add(w);
    const p = noOutline(sph(0.03, dark, [0, 0, 0.004], [0.85, 1.1, 0.12])); eg.add(p);
    const hl = noOutline(sph(0.007, flat('#ffffff'), [-0.008, 0.012, 0.009], [1, 1, 0.3])); p.add(hl);
    head.add(eg); eyes.push(eg); pupils.push(p);
    const b = noOutline(box(0.07, 0.014, 0.01, dark)); b.position.set(0.075 * s, 0.11, FZ + 0.004); head.add(b); brows.push(b);
  }
  const mouthG = new THREE.Group(); mouthG.position.set(0, -0.085, FZ + 0.004); head.add(mouthG);
  const mOpen = noOutline(sph(0.03, flat('#3a1018'), null, [1.3, 1, 0.1])); mouthG.add(mOpen);
  const mTongue = noOutline(sph(0.014, flat('#b84a5a'), [0, -0.012, 0.002], [1.4, 0.7, 0.1])); mOpen.add(mTongue);
  const mLine = noOutline(box(0.07, 0.012, 0.008, dark)); mouthG.add(mLine);
  const arc = (r, flip) => { const q = noOutline(new THREE.Mesh(new THREE.TorusGeometry(r, 0.007, 6, 18, Math.PI), dark)); q.rotation.z = flip ? 0 : Math.PI; q.position.y = flip ? -0.022 : 0.02; mouthG.add(q); return q; };
  const mSmile = arc(0.04, false), mFrown = arc(0.035, true), mGrin = arc(0.07, false);
  const teeth = noOutline(box(0.1, 0.018, 0.006, flat('#f2efe4'), [0, -0.035, 0.002])); mouthG.add(teeth);
  // contact shadow
  const shadow = noOutline(new THREE.Mesh(new THREE.CircleGeometry(0.34, 24), new THREE.MeshBasicMaterial({ color: '#05061a', transparent: true, opacity: 0.32, depthWrite: false }))); shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.012; root.add(shadow);

  const A = { root, head, handL: armL.h, handR: armR.h, torso: torsoG, P, height: P.height, legs: [[legL.l, legL.k], [legR.l, legR.k]], arms: [[armL.a, armL.e], [armR.a, armR.e]], blocky: true };
  let cur = { ...BASE }, faceName = 'neutral', mouthOpen = 0, gaze = [0, 0], lid = 1;
  A.reset = () => { root.visible = true; root.position.set(0, 0, 0); root.rotation.set(0, 0, 0); root.scale.setScalar(P.height); torsoG.position.set(0, 0, 0); cur = { ...BASE }; faceName = 'neutral'; mouthOpen = 0; gaze = [0, 0]; lid = 1; A._apply(); A._face(); return A; };
  A.hide = () => { root.visible = false; return A; };
  A.place = (x, z, ry = 0, y = 0) => { root.position.set(x, y, z); root.rotation.y = rad(ry); return A; };
  A.size = s => { root.scale.setScalar(s); return A; };
  A.pose = (a, b, t) => { cur = b == null ? getPose(a) : mixPose(getPose(a), getPose(b), clamp(t)); A._apply(); return A; };
  A._apply = () => {
    const p = cur; body.position.y = p.hipY; torsoG.rotation.set(rad(p.lean), rad(p.twist), 0);
    head.rotation.set(rad(p.head[0]), rad(p.head[1]), rad(p.head[2]));
    armL.a.rotation.set(-rad(p.aL[0]), rad(p.aL[2]), rad(p.aL[1])); armL.e.rotation.x = -rad(p.eL);
    armR.a.rotation.set(-rad(p.aR[0]), -rad(p.aR[2]), -rad(p.aR[1])); armR.e.rotation.x = -rad(p.eR);
    legL.l.rotation.set(-rad(p.lL[0]), 0, rad(p.lL[1])); legL.k.rotation.x = rad(p.kL);
    legR.l.rotation.set(-rad(p.lR[0]), 0, -rad(p.lR[1])); legR.k.rotation.x = rad(p.kR);
    shadow.scale.setScalar(p.hipY < 0.5 ? 1.25 : 1);
  };
  const v = new THREE.Vector3();
  A.lookAt = (pt, amount = 1) => {
    root.updateMatrixWorld(true); v.set(pt[0], pt[1], pt[2]); neck.worldToLocal(v);
    let yaw = Math.atan2(v.x, v.z), pitch = -Math.atan2(v.y - 0.2, Math.hypot(v.x, v.z));
    const hy = clamp(yaw, -1.4, 1.4) * amount, hp = clamp(pitch, -0.6, 0.7) * amount;
    head.rotation.y += hy; head.rotation.x += hp * 0.8; gaze = [clamp((yaw - hy) * 0.6 + hy * 0.12, -1, 1), clamp(-pitch * 0.25, -1, 1)]; A._eyes(); return A;
  };
  A.gaze = (x, y = 0) => { gaze = [x, y]; A._eyes(); return A; };
  // faces: neutral scared shock worried angry sad smile grin sus dead creepy
  const F = { //   eye  pupil lidY  browY  browTilt mouth   open
    neutral: [1.0, 0.72, 1.0, 0.11, 0, 'line', 0], scared: [1.1, 0.5, 1.0, 0.13, -0.35, 'open', 0.35], shock: [1.22, 0.36, 1.0, 0.145, -0.15, 'open', 0.95],
    worried: [1.04, 0.62, 1.0, 0.125, -0.4, 'frown', 0], angry: [0.95, 0.66, 0.8, 0.1, 0.45, 'frown', 0], sad: [0.98, 0.7, 0.85, 0.115, -0.3, 'frown', 0],
    smile: [1.0, 0.72, 1.0, 0.115, 0, 'smile', 0], grin: [1.0, 0.7, 0.9, 0.115, 0, 'grin', 0], sus: [0.95, 0.62, 0.5, 0.1, 0.25, 'line', 0],
    dead: [0.9, 0.2, 1.0, 0.11, 0, 'line', 0], creepy: [1.08, 0.3, 1.0, 0.125, 0.15, 'grin', 0],
  };
  A.face = name => { faceName = name; A._face(); return A; };
  A.mouth = k => { mouthOpen = clamp(k); A._face(); return A; };
  A.blink = k => { lid = clamp(k); A._face(); return A; };
  A._eyes = () => { const f = F[faceName] || F.neutral; pupils.forEach(p => { p.position.x = gaze[0] * 0.016 * f[0]; p.position.y = gaze[1] * 0.012; }); };
  A._face = () => {
    const f = F[faceName] || F.neutral, ls = Math.max(0.08, lid) * f[2];
    eyes.forEach((e, i) => { e.scale.set(f[0], f[0] * ls, 1); pupils[i].scale.set(0.85 * f[1] / 0.72, 1.1 * f[1] / 0.72, 0.12); });
    brows.forEach((b, i) => { const s = i === 0 ? 1 : -1; b.position.y = f[3]; b.rotation.z = -s * f[4]; });
    const talk = mouthOpen > 0.05, kind = talk ? 'open' : f[5], o = talk ? Math.max(mouthOpen, 0.25) : f[6];
    mOpen.visible = kind === 'open'; mOpen.scale.set(1.3 * (0.75 + 0.3 * o), 0.35 + 1.1 * o, 0.1);
    mLine.visible = kind === 'line'; mSmile.visible = kind === 'smile'; mFrown.visible = kind === 'frown'; mGrin.visible = kind === 'grin'; teeth.visible = kind === 'grin' && faceName === 'creepy';
    A._eyes();
  };
  A.idle = (t, tremble = 0) => {
    const s = P.seed * 1.7;
    torsoG.rotation.z = rad(1.0) * noise(t * 0.35, s + 7); head.rotation.z += rad(1.2) * noise(t * 0.3, s + 3);
    if (tremble) { root.position.x += 0.004 * tremble * Math.sin(t * 43 + s); head.rotation.y += rad(1.2) * tremble * Math.sin(t * 37 + s); }
    const bp = 3.1 + (P.seed % 5) * 0.37, ph = (t + s) % bp; if (ph < 0.14) A.blink(Math.abs(ph - 0.07) / 0.07);
    return A;
  };
  A.talk = (t, env) => { const ph = Math.floor(t * 9.5 + P.seed), pat = [0.75, 0.2, 0.55, 0.9, 0.15, 0.6, 0.35, 0.8][ph % 8]; A.mouth(env == null ? pat : (env > 0.12 ? 0.25 + 0.7 * Math.min(1, env * 1.4) * (0.6 + 0.4 * pat) : 0)); head.rotation.x += rad(1.5) * Math.sin(t * 7); return A; };
  A.walk = (t, speed = 1) => { const w = t * 6.2 * speed, s = Math.sin(w); legL.l.rotation.x = -rad(26) * s; legR.l.rotation.x = rad(26) * s; legL.k.rotation.x = rad(28) * Math.max(0, -Math.cos(w)); legR.k.rotation.x = rad(28) * Math.max(0, Math.cos(w)); armL.a.rotation.x = rad(20) * s; armR.a.rotation.x = -rad(20) * s; body.position.y = cur.hipY - 0.012 + 0.014 * Math.abs(Math.cos(w)); return A; };
  A.run = t => { A.walk(t, 1.7); torsoG.rotation.x = rad(12); armL.e.rotation.x = armR.e.rotation.x = -rad(80); return A; };
  A.reset(); return A;
}
