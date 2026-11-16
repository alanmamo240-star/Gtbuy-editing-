// Sets and props shared by DER ZUG OHNE MORGEN episodes 2-4: the carriage from inside, the platform at dawn, tickets, the note.
import { THREE, toon, lam, flat, box, rbox, sph, cyl, plane, torus, grp, at, noOutline, sameId, sign, glow, canvasTex, rng, clamp, lerp, smooth, noise, rad, FONT } from './util.js';
import { makeSet } from './sets.js';
import { fogOff, texRep } from './lib.js';

// ---------------------------------------------------------------------------------------------- paper props
export function ticketTex(name, line = 'EINFACHE FAHRT · GLEIS 3', stamp = '23:59', foot = null) {
  return canvasTex(560, 330, x => {
    x.fillStyle = '#ece2c2'; x.fillRect(0, 0, 560, 330); x.strokeStyle = '#5a3a2a'; x.lineWidth = 8; x.strokeRect(14, 14, 532, 302); x.lineWidth = 2; x.strokeRect(26, 26, 508, 278);
    x.fillStyle = '#5a3a2a'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.font = `800 40px ${FONT}`; x.fillText('FAHRKARTE', 280, 62);
    x.font = `900 ${name.length > 6 ? 96 : 118}px ${FONT}`; x.fillStyle = '#1b1f3a'; x.fillText(name, 280, foot ? 150 : 168);
    if (foot) { x.font = `900 44px ${FONT}`; x.fillStyle = '#b02a2a'; x.fillText(foot, 280, 232); }
    x.font = `700 28px ${FONT}`; x.fillStyle = '#5a3a2a'; x.fillText(line, 280, foot ? 282 : 266);
    x.strokeStyle = '#5a3a2a'; x.beginPath(); x.arc(500, 62, 14, 0, 7); x.stroke();
    if (stamp) { x.save(); x.translate(470, 250); x.rotate(-0.25); x.strokeStyle = 'rgba(190,40,40,0.75)'; x.lineWidth = 5; x.beginPath(); x.arc(0, 0, 44, 0, 7); x.stroke(); x.fillStyle = 'rgba(190,40,40,0.8)'; x.font = `800 26px ${FONT}`; x.fillText(stamp, 0, 2); x.restore(); }
  });
}
export function paperMesh(tex, w = 0.19, h = 0.112, glowK = 0.32) {
  return new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshLambertMaterial({ map: tex, emissive: '#ffffff', emissiveMap: tex, emissiveIntensity: glowK, side: THREE.DoubleSide }));
}
export function noteTex(lines) {
  return canvasTex(360, 300, x => {
    x.fillStyle = '#e9e0c4'; x.fillRect(0, 0, 360, 300); x.fillStyle = 'rgba(120,90,50,0.18)'; x.fillRect(0, 0, 360, 14);
    x.fillStyle = '#2a2030'; x.textAlign = 'center'; x.textBaseline = 'middle';
    lines.forEach((l, i) => { x.font = `${i === 0 ? 900 : 800} ${i === 0 ? 50 : 44}px ${FONT}`; x.fillText(l, 180, 70 + i * 62); });
  });
}
// conductor's lantern (hangs from a hand) and whistle
export function lantern(intensity = 2.4) {
  const L = new THREE.Group(); L.position.set(0, -0.13, 0.02); const m = toon('#2a2c3a');
  L.add(torus(0.035, 0.008, m, [0, 0.02, 0])); L.add(box(0.1, 0.02, 0.1, m, [0, -0.03, 0])); L.add(box(0.11, 0.02, 0.11, m, [0, -0.19, 0]));
  for (const [dx, dz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) L.add(box(0.012, 0.15, 0.012, m, [dx * 0.045, -0.11, dz * 0.045]));
  L.add(noOutline(box(0.07, 0.12, 0.07, flat('#ffd58a'), [0, -0.11, 0]))); const gl = fogOff(glow(0.9, 0.9, '#ffb060', 0.7, [0, -0.11, 0])); L.add(gl);
  const light = new THREE.PointLight('#ffb062', intensity, 4.5, 1.4); light.position.set(0, -0.11, 0.05); L.add(light); L.userData = { glow: gl, light }; return L;
}

// ---------------------------------------------------------------------------------------------- the carriage from inside
// x along the carriage (-6 .. 6), z across (-1.4 .. 1.4), floor y = 0. Benches in pairs up to x = 3.8, then an open end:
// side door to the platform on the +z wall (x 4.6..5.45), end door on the x = 6 wall, emergency lever + note on the -z wall,
// loudspeaker and a red emergency lamp above the end door. Outside: night fog sliding past, or a platform (o.platform).
export function carriage(o = {}) {
  const g = new THREE.Group(), W = 2.8, H = 2.5, X0 = -6, X1 = 6, ZW = W / 2;
  const wood = lam('#6b4630'), woodDark = lam('#4a2c1c'), upper = lam('#a58a62'), ceilM = lam('#c9b892'), brass = toon('#c9a55a');
  const planks = texRep(canvasTex(128, 512, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 128, 512); x.strokeStyle = 'rgba(40,20,10,0.35)'; x.lineWidth = 3; for (let i = 0; i <= 4; i++) { x.beginPath(); x.moveTo(i * 32, 0); x.lineTo(i * 32, 512); x.stroke(); } }), 1, 14);
  g.add(plane(W, X1 - X0, new THREE.MeshLambertMaterial({ color: '#6a4a34', map: planks }), [0, 0, 0], [-Math.PI / 2, 0, Math.PI / 2]));
  g.add(noOutline(plane(X1 - X0 - 2.2, 0.62, lam('#5a2224'), [-1.1, 0.004, 0], [-Math.PI / 2, 0, 0])));
  // ceiling (flat with a slight arch look), walls with windows cut into them
  g.add(plane(X1 - X0, W, ceilM, [0, H, 0], [Math.PI / 2, 0, 0]));
  for (const s of [-1, 1]) g.add(at(cyl(ZW, ZW, X1 - X0, ceilM), [0, H - 0.05, 0], [0, 0, Math.PI / 2], [0.12, 1, 1]));
  const winX = [], comp = []; for (let k = 0; k < 6; k++) { const x0 = X0 + 0.4 + k * 1.6; comp.push(x0); winX.push(x0 + 0.8); }
  const glassM = new THREE.MeshBasicMaterial({ color: '#0d1226', transparent: true, opacity: 0.35, depthWrite: false });
  for (const s of [-1, 1]) {
    const z = s * ZW, ry = s > 0 ? Math.PI : 0;
    // lower panel, upper wall in strips around the windows
    g.add(at(plane(X1 - X0, 0.95, woodDark), [0, 0.475, z], [0, ry, 0]));
    g.add(at(plane(X1 - X0, H - 1.85, upper), [0, 1.85 + (H - 1.85) / 2, z], [0, ry, 0]));
    let xs = X0; const cuts = winX.map(x => [x - 0.55, x + 0.55]); if (s > 0) cuts.push([4.6, 5.45]);
    cuts.sort((a, b) => a[0] - b[0]);
    for (const [a, b] of cuts) { if (a > xs) g.add(at(plane(a - xs, 0.9, upper), [(xs + a) / 2, 1.4, z], [0, ry, 0])); xs = b; }
    if (X1 > xs) g.add(at(plane(X1 - xs, 0.9, upper), [(xs + X1) / 2, 1.4, z], [0, ry, 0]));
    for (const x of winX) { g.add(box(1.16, 0.06, 0.08, wood, [x, 0.95, z - s * 0.04])); g.add(box(1.16, 0.06, 0.06, wood, [x, 1.86, z - s * 0.03])); for (const d of [-1, 1]) g.add(box(0.06, 0.92, 0.06, wood, [x + d * 0.56, 1.4, z - s * 0.03]));
      const gl = noOutline(plane(1.1, 0.9, glassM, [x, 1.4, z + s * 0.01], [0, ry, 0])); g.add(gl); }
    // luggage rack
    g.add(cyl(0.015, 0.015, X1 - X0 - 2.4, brass, [-1.2, 2.02, z - s * 0.32], [0, 0, Math.PI / 2])); g.add(cyl(0.015, 0.015, X1 - X0 - 2.4, brass, [-1.2, 2.02, z - s * 0.08], [0, 0, Math.PI / 2]));
  }
  // end walls
  g.add(at(plane(W, H, wood), [X0, H / 2, 0], [0, Math.PI / 2, 0]));
  g.add(at(plane(W, H, wood), [X1, H / 2, 0], [0, -Math.PI / 2, 0]));
  const endDoor = grp(box(0.05, 2.0, 0.8, lam('#5e3a26'), [0, 1.0, 0]), box(0.02, 0.5, 0.42, toon('#2a1a12'), [-0.03, 1.45, 0]), noOutline(box(0.01, 0.42, 0.34, flat('#141a2e'), [-0.04, 1.45, 0])), box(0.06, 0.04, 0.18, brass, [-0.05, 1.0, 0.25]));
  g.add(at(endDoor, [X1 - 0.03, 0, 0]));
  // benches: wooden slats, back to back between compartments
  const bench = (facing) => { const b = new THREE.Group(); b.add(box(0.46, 0.06, 1.0, wood, [0, 0.45, 0])); for (let i = 0; i < 4; i++) b.add(box(0.05, 0.1, 0.98, wood, [-0.2 + 0.0, 0.62 + i * 0.13, 0])); b.add(box(0.06, 0.62, 1.0, woodDark, [-0.24, 0.8, 0])); for (const dz of [-0.45, 0.45]) b.add(box(0.05, 0.45, 0.05, woodDark, [0.15, 0.22, dz])); b.rotation.y = facing > 0 ? 0 : Math.PI; return b; };
  const seats = [];
  for (const x0 of comp) for (const s of [-1, 1]) { const zc = s * 0.86; g.add(at(bench(1), [x0 + 0.27, 0, zc])); g.add(at(bench(-1), [x0 + 1.33, 0, zc])); seats.push([x0 + 0.27, zc, 1], [x0 + 1.33, zc, -1]); }
  // ceiling lamps
  const lamps = []; for (const x of [-4.4, -1.2, 2.0, 4.9]) { const l = grp(cyl(0.02, 0.02, 0.12, brass, [0, -0.06, 0]), noOutline(sph(0.11, flat('#ffe6b0'), [0, -0.17, 0]))); const gl = fogOff(glow(1.1, 1.1, '#ffcf8a', 0.5, [0, -0.17, 0])); l.add(gl); const pl = new THREE.PointLight('#ffc884', 2.2, 7.5, 1.5); pl.position.set(0, -0.3, 0); l.add(pl); g.add(at(l, [x, H, 0])); lamps.push({ g: l, gl, pl, bulb: l.children[1] }); }
  // loudspeaker and red emergency lamp above the end door; emergency lever + note on the -z wall
  const speaker = grp(rbox(0.36, 0.36, 0.1, 0.03, toon('#3a3a44')), noOutline(sph(0.13, flat('#151520'), [0, 0, 0.04], [1, 1, 0.2])));
  for (let i = -2; i <= 2; i++) speaker.add(noOutline(box(0.22, 0.012, 0.01, toon('#6a6a78'), [0, i * 0.04, 0.07])));
  g.add(at(speaker, [X1 - 0.07, 2.22, -0.7], [0, -Math.PI / 2, 0]));
  const redLamp = grp(box(0.2, 0.12, 0.1, toon('#2a2a30')), noOutline(box(0.16, 0.08, 0.02, flat('#ff2a1a'), [0, 0, 0.06]))); const redGl = fogOff(glow(1.4, 1.0, '#ff2a1a', 0, [0, 0, 0.1])); redLamp.add(redGl);
  g.add(at(redLamp, [X1 - 0.07, 2.22, 0.45], [0, -Math.PI / 2, 0]));
  const lever = new THREE.Group(); lever.position.set(4.7, 1.65, -ZW + 0.06);
  lever.add(box(0.12, 0.22, 0.06, toon('#2a2a30'), [0, 0, -0.02])); const arm = new THREE.Group(); lever.add(arm);
  arm.add(box(0.05, 0.36, 0.05, toon('#c8261c'), [0, -0.16, 0.04])); arm.add(rbox(0.16, 0.06, 0.07, 0.02, toon('#d8301e'), [0, -0.34, 0.04])); g.add(lever);
  g.add(at(sign('NOTBREMSE', 0.34, 0.09, { bg: '#c8261c', fg: '#fff', weight: 900, size: 0.75 }), [4.7, 1.9, -ZW + 0.012]));
  const note = paperMesh(noteTex(['Bei rotem', 'Signal bleibt', 'er stehen.']), 0.24, 0.2, 0.25); at(note, [5.08, 1.62, -ZW + 0.012], [0, 0, 0.06]); g.add(note);
  // side door to the platform (+z wall): opens outward on a hinge at x = 4.6
  const hinge = new THREE.Group(); hinge.position.set(4.6, 0, ZW);
  hinge.add(box(0.85, 2.15, 0.05, lam('#5e3a26'), [0.425, 1.075, 0])); hinge.add(box(0.46, 0.5, 0.012, toon('#2a1a12'), [0.425, 1.5, -0.03])); hinge.add(noOutline(plane(0.4, 0.44, flat('#141a2e'), [0.425, 1.5, -0.037], [0, Math.PI, 0])));
  hinge.add(box(0.05, 0.2, 0.06, brass, [0.76, 1.0, -0.05])); g.add(hinge);
  g.add(box(0.06, 2.2, 0.08, wood, [4.57, 1.1, ZW - 0.02])); g.add(box(0.06, 2.2, 0.08, wood, [5.48, 1.1, ZW - 0.02])); g.add(box(0.95, 0.35, 0.08, wood, [5.03, 2.33, ZW - 0.02]));
  // outside: fog streaks sliding past (moving train) or a still platform
  const outside = new THREE.Group(); g.add(outside);
  const fogTex = canvasTex(512, 128, x => { const r = rng(7); for (let i = 0; i < 60; i++) { const cx = r() * 512, cy = 20 + r() * 88, rr = 18 + r() * 50, al = 0.12 + r() * 0.16; for (const ox of [0, 512, -512]) { const gr = x.createRadialGradient(cx + ox, cy, 0, cx + ox, cy, rr); gr.addColorStop(0, `rgba(255,255,255,${al})`); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(cx + ox - rr, cy - rr, rr * 2, rr * 2); } } });
  const streaks = [];
  for (const s of [-1, 1]) for (const [d, op, sp] of [[2.3, 0.5, 1], [4.5, 0.35, 0.55]]) { const t = fogTex.clone(); t.needsUpdate = true; texRep(t, 3, 1); const m = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(40, 5), new THREE.MeshBasicMaterial({ map: t, color: '#8b94bc', transparent: true, opacity: op, depthWrite: false })));
    at(m, [0, 1.4, s * (ZW + d)], [0, s > 0 ? Math.PI : 0, 0]); outside.add(m); streaks.push([t, sp]); }
  const passing = []; for (let i = 0; i < 4; i++) { const gl = fogOff(glow(1.6, 1.6, '#ffd08a', 0.0, [0, 1.6, (i % 2 ? 1 : -1) * (ZW + 3)])); outside.add(gl); passing.push(gl); }
  const platform = new THREE.Group(); g.add(platform); platform.visible = !!o.platform;
  platform.add(plane(30, 8, lam('#4a4e68'), [4, -0.25, ZW + 4.4], [-Math.PI / 2, 0, 0])); platform.add(box(30, 0.08, 0.3, lam('#7d80a0'), [4, -0.21, ZW + 0.55]));
  const pl2 = new THREE.PointLight('#ffbe73', 0, 8, 1.6); pl2.position.set(5.0, 2.6, ZW + 2.6); platform.add(pl2);
  const plg = fogOff(glow(1.6, 1.6, '#ffc27a', 0.6, [5.0, 3.0, ZW + 2.6])); platform.add(plg); platform.add(cyl(0.06, 0.08, 3.4, toon('#22263c'), [5.5, 1.45, ZW + 2.9]));
  const dawnGlow = fogOff(glow(14, 6, '#ffb070', 0, [5.0, 1.6, ZW + 7.5], [0, Math.PI, 0])); platform.add(dawnGlow);
  const coldFog = fogOff(glow(7, 4, '#7f90c8', 0.45, [5.0, 1.2, ZW + 3.2], [0, Math.PI, 0])); platform.add(coldFog);
  const shadow = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(1.0, 2.3), new THREE.MeshBasicMaterial({ map: canvasTex(128, 256, x => { x.fillStyle = 'rgba(0,0,0,0)'; x.fillRect(0, 0, 128, 256); x.fillStyle = 'rgba(4,2,8,0.85)';
    x.beginPath(); x.ellipse(64, 40, 22, 26, 0, 0, 7); x.fill(); x.fillRect(24, 22, 80, 10); x.fillRect(36, 62, 56, 110); x.fillRect(22, 70, 18, 80); x.fillRect(88, 70, 18, 80); x.fillRect(40, 168, 20, 88); x.fillRect(68, 168, 20, 88); }), transparent: true, opacity: 0, depthWrite: false })));
  g.add(shadow);

  const set = makeSet(g, {
    mood: 'warm', moodOverride: { bg: '#0b0a14', amb: ['#8a6a58', 0.9], hemi: ['#ffd9a8', '#3a2620', 0.6], key: ['#ffd9a0', 0.35, [2, 5, 3]], pulse: o.pulse || ['#ff2a1a', 0], spill: o.spill || ['#9fb0ff', 0] },
    pov: o.pov || [0, 1.5, 0], look: o.look || [5, 1.1, 0], pulseAt: [5.6, 2.1, 0.2], spillAt: o.spillAt || [5.0, 1.4, ZW + 0.4],
    targets: { sideDoor: [5.03, 1.15, ZW], endDoor: [X1, 1.2, 0], lever: [4.7, 1.5, -ZW], note: [5.08, 1.62, -ZW], speaker: [X1, 2.22, -0.7], aisleFar: [X0, 1.0, 0], ...(o.targets || {}) },
    onUpdate(v, t, S) {
      const L = v.lights ?? 1, flick = v.flicker ? (Math.sin(t * 37) + Math.sin(t * 91.3) > 1.15 * (2 - v.flicker) ? 0.25 : 1) : 1, k = clamp(L * flick);
      for (const l of lamps) { l.pl.intensity = 2.2 * k; l.gl.material.opacity = 0.5 * k; l.bulb.material = k > 0.4 ? flat('#ffe6b0') : flat('#3a3226'); }
      S.parts.amb ||= S.scene.children.find(c => c.isAmbientLight); S.parts.hemi ||= S.scene.children.find(c => c.isHemisphereLight);
      const red = v.red ?? 0; S.parts.amb.intensity = (0.25 + 0.65 * k) * (1 - 0.3 * red) + 1.0 * red * (1 - k); S.parts.hemi.intensity = 0.15 + 0.45 * k + 0.35 * red * (1 - k);
      redGl.material.opacity = 0.75 * red * (0.75 + 0.25 * Math.sin(t * 5)); S.parts.amb.color.set('#8a6a58').lerp(new THREE.Color('#7a1a18'), red * (1 - k));
      const mv = v.moving ?? 1; for (const [tx, sp] of streaks) tx.offset.x = (tx.offset.x * 0) + t * 0.35 * sp * mv + (v.jolt ?? 0) * 0.0;
      passing.forEach((gl, i) => { const ph = ((t * 0.55 * mv + i * 0.37) % 1.4) / 1.4; gl.position.x = lerp(12, -12, ph); gl.material.opacity = mv * 0.55 * Math.sin(Math.PI * ph); });
      hinge.rotation.y = -(v.door ?? 0) * rad(100);
      const lv = v.lever ?? 0; arm.rotation.z = lv * rad(80);
      platform.visible = (v.platform ?? (o.platform ? 1 : 0)) > 0.5; outside.visible = !platform.visible || mv > 0.05;
      pl2.intensity = 2.0 * (v.platLight ?? 1); const dawn = v.dawn ?? 0; dawnGlow.material.opacity = 0.7 * dawn;
      shadow.material.opacity = 0.85 * (v.shadow ?? 0); if (o.shadowAt) { shadow.position.set(...o.shadowAt); shadow.rotation.y = o.shadowRy ?? 0; shadow.scale.setScalar(0.8 + 0.15 * (v.shadow ?? 0)); }
      o.onUpdate?.(v, t, S);
    },
  });
  set.parts = { hinge, lever, arm, note, speaker, lamps, seats, comp, winX };
  set.scene.fog = new THREE.Fog('#0b0a14', 4, 16);
  return set;
}

// ---------------------------------------------------------------------------------------------- the platform at dawn (exterior)
// Same layout as episode 1: track along x at z = -3, carriage side at z = -1.6 (x -12 .. 3), its open side door at x 0.35 .. 1.2,
// platform from z = -1.25 to +5.75 at y = 0. Sunrise toward -x.
export function dawnPlatform(o = {}) {
  const g = new THREE.Group(), FOG = new THREE.Color(o.fog || '#7a6a82');
  const pave = texRep(canvasTex(256, 256, x => { x.fillStyle = '#fff'; x.fillRect(0, 0, 256, 256); x.strokeStyle = 'rgba(20,24,60,0.3)'; x.lineWidth = 5; x.strokeRect(2, 2, 252, 252); }), 60 / 1.3, 7 / 1.3);
  g.add(plane(80, 7, new THREE.MeshLambertMaterial({ color: '#8a8aa0', map: pave }), [-16, 0, 2.25], [-Math.PI / 2, 0, 0])); g.add(box(80, 1.0, 7.0, lam('#555a72'), [-16, -0.502, 2.25])); g.add(box(80, 0.07, 0.34, lam('#b8b8c8'), [-16, 0.035, -1.08]));
  g.add(plane(100, 14, lam('#55586e'), [-10, -1.0, -8.25], [-Math.PI / 2, 0, 0]));
  for (const cz of [-3.0, -7.5]) { const T = new THREE.Group(); for (const dz of [-0.72, 0.72]) T.add(box(90, 0.13, 0.07, toon('#a8acc0'), [-10, -0.87, cz + dz])); for (let x = -50; x < 30; x += 0.62) T.add(box(0.25, 0.1, 2.5, toon('#5a4a40'), [x, -0.955, cz])); g.add(sameId(T)); }
  // the carriage (exterior), door hinge on the left edge, opening over the platform
  const CZ = -3.0, ZS = -1.6, bodyM = lam('#7a3a34'), frameM = toon('#3a1816'), trimM = toon('#c4a56c'), winGlass = flat('#3a3040');
  for (const [a, b] of [[-12, 0.35], [1.2, 3.0]]) { g.add(box(b - a, 2.75, 2.8, bodyM, [(a + b) / 2, 1.125, CZ])); g.add(noOutline(box(b - a, 0.05, 0.02, trimM, [(a + b) / 2, 0.98, ZS + 0.012]))); }
  g.add(box(0.85, 0.3, 2.8, bodyM, [0.775, 2.35, CZ])); g.add(box(0.85, 0.45, 2.8, bodyM, [0.775, -0.025, CZ]));
  for (const x of [-10.4, -9.15, -7.9, -6.65, -4.15, -2.9, -1.65, -0.45, 2.15]) { g.add(box(1.03, 0.8, 0.03, frameM, [x, 1.55, ZS + 0.015])); g.add(plane(0.93, 0.7, winGlass, [x, 1.55, ZS + 0.033])); }
  g.add(box(15, 0.14, 2.9, lam('#3c3e52'), [-4.5, 2.57, CZ])); g.add(at(cyl(1.45, 1.45, 15, lam('#3c3e52')), [-4.5, 2.6, CZ], [0, 0, Math.PI / 2], [0.24, 1, 1]));
  g.add(box(14.4, 0.28, 2.3, lam('#151726'), [-4.5, -0.39, CZ]));
  const hinge = new THREE.Group(); hinge.position.set(0.35, 0.2, ZS + 0.02); hinge.add(box(0.85, 2.0, 0.04, lam('#6a302c'), [0.425, 1.0, 0])); hinge.add(box(0.5, 0.55, 0.012, frameM, [0.425, 1.35, 0.026])); hinge.add(plane(0.42, 0.47, winGlass, [0.425, 1.35, 0.034])); g.add(hinge);
  g.add(plane(0.85, 2.0, flat('#2a1410'), [0.775, 1.2, -1.75]));
  // canopy, columns, sign and the stopped clock
  g.add(box(42, 0.12, 4.6, lam('#3a3e58'), [-6, 4.12, 3.5])); for (const x of [-18, -12, -6, 0, 6]) g.add(cyl(0.085, 0.11, 4.06, toon('#2a2e48'), [x, 2.03, 4.6]));
  g.add(box(80, 4.2, 0.3, lam('#4a4a64'), [-16, 2.1, 5.9]));
  // sky with the sun coming up at -x
  const skyTex = canvasTex(64, 512, x => { const gr = x.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, '#3a3a6a'); gr.addColorStop(0.55, '#b27a8a'); gr.addColorStop(0.8, '#ffb27a'); gr.addColorStop(1, '#ffd6a0'); x.fillStyle = gr; x.fillRect(0, 0, 64, 512); });
  g.add(noOutline(fogOff(new THREE.Mesh(new THREE.SphereGeometry(70, 24, 16), new THREE.MeshBasicMaterial({ map: skyTex, side: THREE.BackSide })))));
  const sun = fogOff(glow(40, 26, '#ffc27a', 0.9, [-62, 4, 1], [0, Math.PI / 2, 0])); g.add(sun); g.add(noOutline(fogOff(sph(2.4, flat('#fff0c8'), [-66, 3.2, 1]))));
  const sunLight = new THREE.DirectionalLight('#ffb27a', 1.6); sunLight.position.set(-10, 2.5, 1); g.add(sunLight);
  const set = makeSet(g, {
    mood: 'dusk', moodOverride: { bg: FOG.getHex(), amb: ['#a88a9a', 1.3], hemi: ['#ffcfa8', '#4a3a50', 1.0], key: ['#ffd0a0', 0.6, [-4, 4, 3]] },
    pov: o.pov || [4, 1.4, 1], look: o.look || [-8, 1.1, 0.5], targets: { door: [0.78, 1.15, -1.6], sun: [-40, 3, 1], ...(o.targets || {}) },
    onUpdate(v, t, S) { hinge.rotation.y = -(v.door ?? 0) * rad(98); o.onUpdate?.(v, t, S); },
  });
  set.scene.fog = new THREE.Fog(FOG, 4, 38); set.parts = { hinge };
  return set;
}
