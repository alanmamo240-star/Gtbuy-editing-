// Toon mannequin character: sphere head, huge round eyes, capsule limbs with elbows and knees, big sphere hands, block shoes.
// Faces +z at ry = 0. Left side is +x. One unit = one metre; height 1 = a 1.72 m adult, 0.8 = a child.
import { THREE, toon, flat, box, rbox, sph, cyl, limb, disc, torus, grp, at, noOutline, sameId, rad, lerp, clamp, noise, rng } from './util.js';

export const SKIN = { fair: '#f3cdb6', light: '#e9b999', tan: '#c98f68', brown: '#8a5a3c', deep: '#5e3a26', pale: '#f6dfd2' };
const R = 0.15; // head radius

// ---- poses (degrees). a = [forward, outward, twist], e = elbow bend, l = [forward, outward], k = knee bend, head = [nod(+down), turn(+left), tilt]
export const POSES = {
  stand:     { hipY: 0.83, lean: 0, twist: 0, head: [0, 0, 0], aL: [4, 7, 0], eL: 8, aR: [4, 7, 0], eR: 8, lL: [0, 2], kL: 0, lR: [0, 2], kR: 0 },
  open:      { hipY: 0.83, aL: [28, 22, 0], eL: 45, aR: [28, 22, 0], eR: 45 },
  stop:      { hipY: 0.83, lean: 4, aR: [84, 4, 0], eR: 6, aL: [8, 12, 0], eL: 14 },                // right palm pushed at the camera
  block:     { hipY: 0.83, aL: [10, 62, 0], eL: 12, aR: [10, 62, 0], eR: 12 },                       // both arms out, barring the way
  point:     { hipY: 0.83, aR: [80, 8, 0], eR: 4 },
  shh:       { aR: [52, -14, 0], eR: 138 },                                                          // finger to lips (layer on any pose)
  gasp:      { aL: [48, -16, 0], eL: 136, aR: [48, -16, 0], eR: 136 },                               // both hands to the mouth
  hipsHands: { hipY: 0.83, aL: [0, 34, 0], eL: 70, aR: [0, 34, 0], eR: 70 },
  cross:     { hipY: 0.83, aL: [38, -18, 0], eL: 100, aR: [34, -18, 0], eR: 104 },
  phone:     { aR: [42, -6, 0], eR: 96, head: [22, 0, 0] },
  wave:      { aR: [20, 150, 0], eR: 30 },
  shrug:     { hipY: 0.83, aL: [16, 30, 0], eL: 86, aR: [16, 30, 0], eR: 86, head: [0, 0, 8] },
  slump:     { hipY: 0.83, lean: 14, head: [26, 0, 0], aL: [6, 4, 0], eL: 4, aR: [6, 4, 0], eR: 4 },
  kneel:     { hipY: 0.30, lean: 6, aL: [16, 8, 0], eL: 40, aR: [16, 8, 0], eR: 40, lL: [38, 6], kL: 152, lR: [38, 6], kR: 152 },   // sitting on the heels
  kneelUp:   { hipY: 0.34, lean: 10, aL: [30, 6, 0], eL: 50, aR: [14, 10, 0], eR: 30, lL: [115, 8], kL: 115, lR: [18, 6], kR: 148 }, // one knee up, ready to move
  crouch:    { hipY: 0.33, lean: 30, head: [-12, 0, 0], aL: [52, 4, 0], eL: 96, aR: [52, 4, 0], eR: 96, lL: [112, 10], kL: 142, lR: [112, 10], kR: 142 }, // hiding squat
  sitHug:    { hipY: 0.16, lean: 14, aL: [66, -4, 0], eL: 40, aR: [66, -4, 0], eR: 40, lL: [138, 5], kL: 132, lR: [138, 5], kR: 132 },   // on the floor hugging the knees
  sitFloor:  { hipY: 0.12, lean: -6, aL: [-18, 14, 0], eL: 10, aR: [-18, 14, 0], eR: 10, lL: [88, 10], kL: 6, lR: [88, 10], kR: 6 },      // legs out
  sitChair:  { hipY: 0.50, aL: [22, 4, 0], eL: 60, aR: [22, 4, 0], eR: 60, lL: [90, 4], kL: 90, lR: [90, 4], kR: 90 },
  cower:     { hipY: 0.33, lean: 38, head: [20, 0, 0], aL: [118, -8, 0], eL: 128, aR: [118, -8, 0], eR: 128, lL: [112, 10], kL: 142, lR: [112, 10], kR: 142 }, // hands over head
  lean:      { hipY: 0.83, lean: 16, head: [-10, 0, 0], aL: [10, 10, 0], eL: 20, aR: [10, 10, 0], eR: 20 },
  reach:     { hipY: 0.83, lean: 8, aR: [70, 6, 0], eR: 20 },                                         // hand going for a handle
};
const BASE = POSES.stand;
function mixPose(a, b, t) { const o = {}; for (const k in BASE) { const x = a[k] ?? BASE[k], y = b[k] ?? x; o[k] = Array.isArray(x) ? x.map((v, i) => lerp(v, y[i] ?? v, t)) : lerp(x, y, t); } return o; }
// resolve 'kneelUp+shh' / object / array of layers into a full pose
export function getPose(p) {
  if (!p) return { ...BASE };
  if (typeof p === 'string') { let o = { ...BASE }; for (const n of p.split('+')) { if (!POSES[n]) throw new Error('unknown pose ' + n); o = { ...o, ...POSES[n] }; } return o; }
  return { ...BASE, ...p };
}

function hairMesh(style, color, seed) {
  const m = toon(color), g = new THREE.Group(), r = rng(seed * 97 + 5);
  const cap = (len = 0.56, tilt = -0.42, s = 1.07) => { const q = new THREE.Mesh(new THREE.SphereGeometry(R * s, 28, 18, 0, Math.PI * 2, 0, Math.PI * len), m); q.rotation.x = tilt; q.scale.set(1, 1.06, 1.02); return q; };
  if (style === 'bald') return g;
  if (style === 'buzz') { g.add(cap(0.46, -0.3, 1.03)); return g; }
  g.add(cap());
  if (style === 'bun') g.add(sph(0.078, m, [0, R * 1.16, -0.035]));
  else if (style === 'curly' || style === 'afro') { const n = style === 'afro' ? 26 : 16, rr = style === 'afro' ? 0.07 : 0.058, k = style === 'afro' ? 1.2 : 1.05;
    for (let i = 0; i < n; i++) { const th = r() * Math.PI * 2, ph = r() * 1.25; const y = Math.cos(ph), q = Math.sin(ph); let z = Math.sin(th) * q, x = Math.cos(th) * q; if (z > 0.55 && y < 0.55) { z = 0.5; } g.add(sph(rr, m, [x * R * k, y * R * k + 0.01, z * R * k - 0.02])); } }
  else if (style === 'long') { g.add(at(rbox(0.3, 0.36, 0.13, 0.06, m), [0, -0.1, -0.1])); g.add(sph(0.07, m, [0.13, -0.02, -0.02], [0.6, 1.5, 1])); g.add(sph(0.07, m, [-0.13, -0.02, -0.02], [0.6, 1.5, 1])); }
  else if (style === 'bob') { g.add(at(rbox(0.33, 0.2, 0.2, 0.08, m), [0, -0.03, -0.06])); }
  else if (style === 'ponytail') { g.add(sph(0.05, m, [0, 0.06, -R * 1.05])); const t = limb(0.045, 0.24, m); at(t, [0, 0.06, -R * 1.1], [-0.5, 0, 0]); g.add(t); }
  else if (style === 'pigtails') { g.add(sph(0.065, m, [R * 1.1, 0.02, -0.03])); g.add(sph(0.065, m, [-R * 1.1, 0.02, -0.03])); }
  else if (style === 'spiky') { for (let i = 0; i < 9; i++) { const a = i / 9 * Math.PI * 2; const c = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.13, 8), m); c.position.set(Math.cos(a) * 0.08, R * 0.98, Math.sin(a) * 0.08 - 0.02); c.rotation.set(Math.sin(a) * 0.6, 0, -Math.cos(a) * 0.6); g.add(c); } g.add(new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.14, 8), m).translateY(R * 1.08)); }
  else if (style === 'swoop') { g.add(at(rbox(0.26, 0.07, 0.12, 0.035, m), [0.02, R * 0.74, R * 0.6], [0.5, 0, 0.12])); }
  else if (style === 'beanie') { g.children[0].scale.set(1.03, 1.16, 1.05); g.add(torus(R * 1.03, 0.026, m, [0, R * 0.34, 0.012], [Math.PI / 2 - 0.42, 0, 0])); g.add(sph(0.04, m, [0, R * 1.3, -0.05])); }
  // 'short' = cap only
  g.traverse(o => { o.userData.inkFlat = true; }); return sameId(g);
}

export function makeToon(o = {}) {
  const P = { skin: 'light', height: 1, head: 1, hair: 'short', hairColor: '#3a2a22', top: '#d7a31f', topStyle: 'sweater', bottom: '#27306b', shoe: '#1c1f3d', collar: null, glasses: false, eye: 0.064, brows: false, seed: 1, ...(o.real ? { head: 0.88, eye: 0.046, brows: true } : {}), ...o };
  const L = P.real ? { tw: 0.37, sh: 0.074, ua: 0.06, fa: 0.052, hd: 0.058, th: 0.075, sn: 0.062 } : { tw: 0.41, sh: 0.098, ua: 0.078, fa: 0.07, hd: 0.084, th: 0.09, sn: 0.08 };   // real: slimmer, closer to drawn people
  const skinHex = SKIN[P.skin] || P.skin, sk = toon(skinHex), topM = toon(P.top), botM = toon(P.bottom), dark = flat('#15101c');
  const skinDark = toon(new THREE.Color(skinHex).multiplyScalar(0.8).getHex());
  const root = new THREE.Group(), body = new THREE.Group(), torsoG = new THREE.Group(); root.add(body); body.add(torsoG);
  body.add(at(rbox(0.36, 0.2, 0.24, 0.09, botM), [0, 0.03, 0]));
  const torso = at(rbox(L.tw, 0.52, 0.25, P.real ? 0.08 : 0.115, topM), [0, 0.285, 0]); torsoG.add(torso);
  if (P.topStyle === 'hoodie') { torsoG.add(sph(0.11, topM, [0, 0.5, -0.1], [1.25, 0.8, 0.9])); torsoG.add(noOutline(at(rbox(0.2, 0.1, 0.02, 0.02, toon(new THREE.Color(P.top).multiplyScalar(0.82).getHex())), [0, 0.16, 0.131]))); }
  if (P.topStyle === 'jacket') torsoG.add(noOutline(box(0.09, 0.46, 0.012, toon(P.inner || '#f1f1f6'), [0, 0.29, 0.128])));
  if (P.topStyle === 'stripe') torsoG.add(noOutline(box(0.415, 0.09, 0.265, toon(P.inner || '#f1f1f6'), [0, 0.33, 0])));
  if (P.topStyle === 'dress') body.add(at(cyl(0.2, 0.3, 0.34, topM), [0, -0.1, 0]));
  if (P.topStyle === 'coat') { body.add(at(cyl(0.215, 0.255, 0.36, topM), [0, -0.1, 0])); torsoG.add(noOutline(box(0.012, 0.46, 0.012, toon(new THREE.Color(P.top).multiplyScalar(1.18).getHex()), [0, 0.29, 0.13]))); for (const y of [0.44, 0.32, 0.2]) torsoG.add(noOutline(sph(0.017, dark, [0.045, y, 0.128], [1, 1, 0.4]))); }
  if (P.topStyle === 'uniform') { torsoG.add(noOutline(box(0.09, 0.46, 0.012, toon(P.inner || '#b8b4a4'), [0, 0.29, 0.128]))); for (const y of [0.44, 0.32, 0.2]) torsoG.add(noOutline(sph(0.018, flat('#d9b65a'), [0.07, y, 0.129], [1, 1, 0.4]))); body.add(at(cyl(0.2, 0.22, 0.2, topM), [0, -0.04, 0])); }
  if (P.scarf) { torsoG.add(at(torus(0.085, 0.034, toon(P.scarf)), [0, 0.535, 0.01], [Math.PI / 2, 0, 0])); torsoG.add(at(rbox(0.07, 0.2, 0.03, 0.015, toon(P.scarf)), [0.06, 0.43, 0.12], [0.1, 0, 0.12])); }
  if (P.collar) torsoG.add(at(rbox(0.13, 0.05, 0.1, 0.02, toon(P.collar)), [0, 0.545, 0.03]));
  if (P.backpack) torsoG.add(at(rbox(0.32, 0.38, 0.14, 0.06, toon(P.backpack)), [0, 0.3, -0.19]));
  const short = P.topStyle === 'tee' || P.sleeves === 'short';
  const mkArm = s => {
    const a = new THREE.Group(); a.position.set(0.225 * s, 0.455, 0);
    a.add(sph(L.sh, topM)); a.add(limb(L.ua, 0.29, topM));
    const e = new THREE.Group(); e.position.y = -0.25; a.add(e);
    e.add(limb(L.fa, 0.27, short ? sk : topM)); const h = sph(L.hd, sk, [0, -0.27, 0], P.real ? [0.8, 1.15, 0.6] : null); e.add(h);
    torsoG.add(a); return { a, e, h };
  };
  const armL = mkArm(1), armR = mkArm(-1);
  const mkLeg = s => {
    const l = new THREE.Group(); l.position.set(0.1 * s, 0, 0); l.add(limb(L.th, 0.42, P.topStyle === 'dress' && P.bare ? sk : botM));
    const k = new THREE.Group(); k.position.y = -0.38; l.add(k); k.add(limb(L.sn, 0.42, botM));
    k.add(at(rbox(0.14, 0.11, 0.27, 0.035, toon(P.shoe)), [0, -0.395, 0.05]));
    body.add(l); return { l, k };
  };
  const legL = mkLeg(1), legR = mkLeg(-1);
  // head
  const neck = new THREE.Group(); neck.position.set(0, 0.54, 0); torsoG.add(neck); neck.add(cyl(0.05, 0.055, 0.1, sk, [0, 0.03, 0]));
  const head = new THREE.Group(); head.position.set(0, 0.07 + R * P.head, 0); head.rotation.order = 'YXZ'; head.scale.setScalar(P.head); neck.add(head);
  head.add(sph(R, sk, null, [1, 1.05, 1]));
  head.add(sph(0.036, sk, [R * 0.98, -0.01, -0.01], [0.6, 1, 1])); head.add(sph(0.036, sk, [-R * 0.98, -0.01, -0.01], [0.6, 1, 1]));
  head.add(hairMesh(P.hair, P.hairColor, P.seed));
  if (P.cap) { const cp = new THREE.Mesh(new THREE.SphereGeometry(R * 1.1, 24, 12, 0, Math.PI * 2, 0, Math.PI * 0.34), toon(P.cap)); cp.rotation.x = -0.12; head.add(sameId(grp(cp, at(rbox(0.2, 0.02, 0.12, 0.01, toon(P.cap)), [0, R * 0.74, R * 1.0], [0.18, 0, 0])))); }
  if (P.hat) { const c = toon(P.hat); head.add(sameId(grp(at(cyl(R * 1.1, R * 1.04, 0.13, c), [0, R * 1.0, -0.01]), at(cyl(R * 1.14, R * 1.14, 0.016, c), [0, R * 1.0 + 0.07, -0.01]), at(rbox(0.21, 0.016, 0.1, 0.008, flat('#101018')), [0, R * 0.66, R * 0.97], [0.3, 0, 0]))));
    head.add(noOutline(rbox(0.05, 0.035, 0.012, 0.006, flat('#d9b65a'), [0, R * 0.98, R * 1.08]))); }
  if (P.helmet) { const c = toon(P.helmet); const dome = new THREE.Mesh(new THREE.SphereGeometry(R * 1.24, 24, 14, 0, Math.PI * 2, 0, Math.PI * 0.5), c); dome.position.set(0, R * 0.12, -0.01); dome.rotation.x = -0.1;
    head.add(sameId(grp(dome, at(cyl(R * 1.34, R * 1.34, 0.025, c), [0, R * 0.14, -0.01], [-0.1, 0, 0]))));
    if (P.strap !== false) head.add(noOutline(at(torus(R * 0.98, 0.008, flat('#2a2a22')), [0, -0.02, 0], [0, Math.PI / 2, 0]))); }
  if (P.hood) { const hm = toon(P.hoodColor || P.top, { side: THREE.DoubleSide }), hg = new THREE.Group();
    hg.add(new THREE.Mesh(new THREE.SphereGeometry(R * 1.2, 26, 10, 0, Math.PI * 2, 0, Math.PI * 0.3), hm));                                  // closed crown over the hair
    hg.add(new THREE.Mesh(new THREE.SphereGeometry(R * 1.2, 26, 14, Math.PI * 0.84, Math.PI * 1.32, Math.PI * 0.3, Math.PI * 0.44), hm));      // sides and back, open at the face
    hg.position.set(0, 0.012, -0.012); hg.scale.set(1, 1.06, 1.05); head.add(sameId(hg)); }
  const ex = P.glasses ? 0.07 : P.eye * 0.97, ey = 0.022, ez = Math.sqrt(R * R - ex * ex - ey * ey) * 0.9;
  const eyes = [], pupils = [], white = toon('#ffffff');
  for (const s of [1, -1]) {
    const eg = new THREE.Group(); eg.position.set(ex * s, ey, ez); eg.rotation.y = 0.2 * s;
    const w = sph(P.eye, white, null, [1, 1, 0.42]); eg.add(w);
    const p = noOutline(sph(P.eye * 0.34, dark, [0, 0, P.eye * 0.44], [1, 1, 0.3])); eg.add(p);
    if (P.glasses) { eg.add(noOutline(torus(P.eye * 1.2, 0.011, dark, [0, 0, P.eye * 0.3]))); }
    head.add(eg); eyes.push(eg); pupils.push(p);
  }
  if (P.glasses) { head.add(noOutline(box(0.04, 0.014, 0.014, dark, [0, ey + 0.012, ez + 0.03]))); for (const s of [1, -1]) head.add(noOutline(box(0.012, 0.012, 0.13, dark, [R * 0.99 * s, ey, 0.045]))); }
  const brows = [1, -1].map(s => { const b = noOutline(rbox(0.07, 0.014, 0.012, 0.006, dark)); b.position.set(ex * s, ey + P.eye * 1.18, ez + 0.02); b.visible = !!P.brows; head.add(b); return b; });
  head.add(noOutline(sph(0.017, skinDark, [0, -0.035, R * 0.99], [1.1, 0.8, 0.7])));
  const my = -0.082, mz = Math.sqrt(R * R * 1.05 - my * my) + 0.002;
  const mouth = noOutline(disc(0.03, dark, [0, my, mz], [0.52, 0, 0])); head.add(mouth);
  const tongue = noOutline(disc(0.013, flat('#9c4456'), [0, my - 0.012, mz + 0.0015], [0.52, 0, 0])); head.add(tongue);
  const arc = (flip) => { const q = noOutline(new THREE.Mesh(new THREE.TorusGeometry(0.036, 0.007, 6, 16, Math.PI), dark)); q.position.set(0, my + (flip ? -0.02 : 0.022), mz + 0.001); q.rotation.set(0.5, 0, flip ? 0 : Math.PI); q.visible = false; head.add(q); return q; };
  const smileArc = arc(false), frownArc = arc(true);
  // contact shadow
  const shadow = noOutline(new THREE.Mesh(new THREE.CircleGeometry(0.34, 24), new THREE.MeshBasicMaterial({ color: '#05061a', transparent: true, opacity: 0.32, depthWrite: false }))); shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.012; root.add(shadow);

  const A = { root, head, handL: armL.h, handR: armR.h, torso: torsoG, P, height: P.height, legs: [[legL.l, legL.k], [legR.l, legR.k]], arms: [[armL.a, armL.e], [armR.a, armR.e]] };
  let cur = { ...BASE }, faceName = 'neutral', mouthOpen = 0, gaze = [0, 0], lid = 1;
  A.reset = () => { root.visible = true; root.position.set(0, 0, 0); root.rotation.set(0, 0, 0); root.scale.setScalar(P.height); cur = { ...BASE }; faceName = 'neutral'; mouthOpen = 0; gaze = [0, 0]; lid = 1; A._apply(); return A; };
  A.hide = () => { root.visible = false; return A; };
  A.place = (x, z, ry = 0, y = 0) => { root.position.set(x, y, z); root.rotation.y = rad(ry); return A; };
  A.size = s => { root.scale.setScalar(s); return A; };
  // pose(a) or pose(a, b, blend 0..1)
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
  // turn head (and a little torso, and the pupils) toward a world point. amount 0..1
  const v = new THREE.Vector3();
  A.lookAt = (pt, amount = 1) => {
    root.updateMatrixWorld(true); v.set(pt[0], pt[1], pt[2]); neck.worldToLocal(v); // neck space (includes torso lean/twist)
    let yaw = Math.atan2(v.x, v.z), pitch = -Math.atan2(v.y - 0.2, Math.hypot(v.x, v.z));
    const hy = clamp(yaw, -1.45, 1.45) * amount, hp = clamp(pitch, -0.6, 0.7) * amount;
    head.rotation.y += hy; head.rotation.x += hp * 0.8; gaze = [clamp((yaw - hy) * 0.6 + hy * 0.12, -1, 1), clamp(-pitch * 0.25, -1, 1)]; A._eyes(); return A;
  };
  A.gaze = (x, y = 0) => { gaze = [x, y]; A._eyes(); return A; };   // -1..1, +x = character's left
  A._eyes = () => { pupils.forEach((p, i) => { p.position.x = gaze[0] * P.eye * 0.42; p.position.y = gaze[1] * P.eye * 0.4; }); };
  // faces: neutral scared shock worried angry sad smile grin sus dead creepy
  A.face = name => { faceName = name; A._face(); return A; };
  A.mouth = k => { mouthOpen = clamp(k); A._face(); return A; };   // 0 closed .. 1 wide (speech)
  A.blink = k => { lid = clamp(k); A._face(); return A; };          // 1 open .. 0 shut
  A._face = () => {
    const F = { neutral: [1, 0.34, 0.12, 0.85], scared: [1.1, 0.26, 0.2, 0.7], shock: [1.16, 0.22, 0.9, 0.62], worried: [1.04, 0.32, 0.14, 0.8], angry: [0.92, 0.32, 0.12, 0.9], sad: [0.95, 0.36, 0.1, 0.8], smile: [1, 0.36, 0, 1], grin: [1.02, 0.36, 0.5, 1.15], sus: [0.62, 0.34, 0.1, 0.8], dead: [1.1, 0.14, 0.12, 0.8], creepy: [1.18, 0.15, 0, 1.6] }[faceName] || [1, 0.34, 0.12, 0.85];
    const [eyeS, pupS, mH, mW] = F;
    eyes.forEach(e => e.children[0].scale.set(eyeS, eyeS * Math.max(0.07, lid) * (faceName === 'sus' ? 0.6 : 1), 0.42));
    pupils.forEach(p => { p.scale.set(pupS / 0.34, pupS / 0.34 / Math.max(0.3, lid), 0.3); p.visible = lid > 0.3; });
    const open = Math.max(mH, mouthOpen * 0.95);
    smileArc.visible = (faceName === 'smile' || faceName === 'creepy') && mouthOpen < 0.08; smileArc.scale.set(faceName === 'creepy' ? 1.7 : 1, faceName === 'creepy' ? 0.75 : 1, 1); frownArc.visible = (faceName === 'sad') && mouthOpen < 0.08;
    mouth.visible = !smileArc.visible && !frownArc.visible; mouth.scale.set(mW * (1 - 0.25 * mouthOpen), Math.max(0.1, open), 1);
    tongue.visible = mouth.visible && open > 0.55;
    const tilt = { angry: -0.42, worried: 0.34, sad: 0.4, scared: 0.3, shock: 0.2, creepy: -0.18 }[faceName];
    brows.forEach((b, i) => { b.visible = !!P.brows || tilt != null && !P.glasses; b.rotation.z = (tilt || 0) * (i ? -1 : 1); b.position.y = ey + P.eye * (faceName === 'angry' ? 1.02 : 1.22); });
  };
  // idle life: breathing, sway, automatic blinks. tremble 0..1 adds a scared shiver.
  A.idle = (t, tremble = 0) => {
    const s = P.seed * 13.7; torso.scale.y = 1 + 0.012 * Math.sin(t * 1.9 + s); head.rotation.z += rad(1.6) * noise(t * 0.5, s); head.rotation.x += rad(1.4) * noise(t * 0.4, s + 3);
    torsoG.rotation.z = rad(1.0) * noise(t * 0.35, s + 7);
    if (tremble) { root.position.x += 0.004 * tremble * Math.sin(t * 43 + s); head.rotation.y += rad(1.2) * tremble * Math.sin(t * 37 + s); }
    const bp = 3.1 + (P.seed % 5) * 0.37, ph = (t + s) % bp; if (ph < 0.14) A.blink(Math.abs(ph - 0.07) / 0.07);
    return A;
  };
  // speech: hard-switching mouth shapes at syllable rate. env = loudness 0..1 if known, else a seeded pattern.
  A.talk = (t, env) => { const ph = Math.floor(t * 9.5 + P.seed), pat = [0.75, 0.2, 0.55, 0.9, 0.15, 0.6, 0.35, 0.8][ph % 8]; A.mouth(env == null ? pat : (env > 0.12 ? 0.25 + 0.7 * Math.min(1, env * 1.4) * (0.6 + 0.4 * pat) : 0)); head.rotation.x += rad(1.5) * Math.sin(t * 7); return A; };
  // locomotion layers
  A.walk = (t, speed = 1) => { const w = t * 6.2 * speed, s = Math.sin(w); legL.l.rotation.x = -rad(26) * s; legR.l.rotation.x = rad(26) * s; legL.k.rotation.x = rad(28) * Math.max(0, -Math.cos(w)); legR.k.rotation.x = rad(28) * Math.max(0, Math.cos(w)); armL.a.rotation.x = rad(20) * s; armR.a.rotation.x = -rad(20) * s; body.position.y = cur.hipY - 0.012 + 0.014 * Math.abs(Math.cos(w)); return A; };
  A.run = t => { A.walk(t, 1.7); torsoG.rotation.x = rad(12); armL.e.rotation.x = armR.e.rotation.x = -rad(80); return A; };
  A.reset(); A._face(); return A;
}
