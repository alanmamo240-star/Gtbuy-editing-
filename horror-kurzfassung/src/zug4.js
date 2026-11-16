// DER ZUG OHNE MORGEN · Folge 4 – "Zusammen raus" (30 s). Emil wedges the lever, all three jump out and run into the sunrise.
import { story } from './core.js';
import { CAST } from './cast.js';
import { carriage, dawnPlatform, ticketTex, paperMesh } from './zugsets.js';
import { towards, loadTimings, sequencer, mover, pathAt, breathPuffs } from './lib.js';
import { THREE, toon, box, clamp, lerp, smooth, rad, noise } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

// ------------------------------------------------------------------ inside (same carriage as episode 3, morning light at the door)
const A = [1.0, 1.5, 0.15], Q = [5.6, 1.25, -1.0], P = [3.95, 1.5, 0.75], D = [5.45, 1.5, -0.45];
const LEVER = [4.65, -0.85], T_JUMP = 0.55, T_CRACK = 2.35, T_WEDGE = 4.25;
const pIn = CAST.paul(), eIn = CAST.emil(), lIn = CAST.lena();
const MVi = mover()
  .add(eIn, 'emil', { from: [4.9, 2.7], to: [4.85, 0.75], T0: T_JUMP, T1: T_JUMP + 0.55, mode: 'still', arc: 0.35, y0: -0.25, y1: 0, endRy: -120 })
  .add(eIn, 'emil', { from: [4.85, 0.75], to: [4.15, 0.5], T0: 1.35, T1: 1.85, mode: 'walk', endRy: -95 })
  .add(eIn, 'emil', { from: [4.15, 0.5], to: [5.05, -0.7], T0: 2.85, T1: 3.6, mode: 'walk', endRy: -95 })
  .add(pIn, 'paul', { from: LEVER, to: [5.15, 0.95], T0: 6.6, T1: 7.5, mode: 'walk', endRy: 10 })
  .add(eIn, 'emil', { from: [5.05, -0.7], to: [4.75, 0.8], T0: 6.8, T1: 7.6, mode: 'walk', endRy: 10 })
  .add(pIn, 'paul', { from: [5.15, 0.95], to: [5.2, 2.5], T0: 8.2, T1: 8.75, mode: 'still', arc: 0.35, y1: -0.25, endRy: 180 })
  .add(eIn, 'emil', { from: [4.75, 0.8], to: [4.85, 2.7], T0: 8.55, T1: 9.1, mode: 'still', arc: 0.4, y1: -0.25, endRy: 180 });
const stick = box(0.06, 0.5, 0.06, toon('#7a4e30')); const v1 = new THREE.Vector3(), q1 = new THREE.Quaternion();
const inside = carriage({
  pov: D, look: [5.0, 1.15, 1.4], platform: true, pulse: ['#ff2a1a', 2.4], spill: ['#ffb070', 3.0], spillAt: [5.0, 1.7, 4.4], shadowAt: [4.1, 1.2, -1.37],
  targets: { lever: [4.75, 1.3, -1.3], H_door: [5.0, 1.0, 2.0], H_paul: [4.65, 1.41, -0.85], H_emil: [5.05, 1.44, -0.7], bench: [3.9, 0.9, 0.55], two: [4.85, 1.3, -0.75], H_emilC: [5.0, 1.28, -0.68] },
  onUpdate(v, t, S) {
    MVi.update(t);
    const strain = clamp(1 - (t - T_WEDGE) / 0.3) * (t < T_WEDGE + 0.3 ? 1 : 0); S.parts.arm.rotation.z = rad(80) - strain * rad(9) * (0.6 + 0.4 * Math.sin(t * 3.1));
    stick.visible = t > T_CRACK;
    if (t > T_CRACK && t < T_WEDGE) { eIn.root.updateMatrixWorld(true); eIn.handR.getWorldPosition(v1); stick.position.copy(v1); eIn.handR.getWorldQuaternion(q1); stick.quaternion.copy(q1); stick.rotateX(Math.PI / 2); }
    else if (t >= T_WEDGE) { stick.position.set(4.82, 0.95, -1.2); stick.rotation.set(0.35, 0, -0.55); }
  },
});
inside.scene.add(stick);

// ------------------------------------------------------------------ outside: the platform at dawn (door at x 0.35..1.2, z = -1.6; the sun is at -x)
const pX = CAST.paul(), eX = CAST.emil(), lX = CAST.lena();
const STOP = { paul: [-29.2, 0.5], emil: [-30.0, -0.35], lena: [-30.2, 1.45] }, STOPRY = { paul: -90, emil: 43, lena: 134 };
const RUNX = { paul: { from: [0.95, -0.5], T0: 9.7, T1: 20.1, ph: 0.1 }, emil: { from: [0.6, -0.3], T0: 9.95, T1: 20.3, ph: 0.33 }, lena: { from: [1.6, 0.4], T0: 9.55, T1: 19.95, ph: 0.52 } };
const MVx = mover(); for (const [n, av] of [['paul', pX], ['emil', eX], ['lena', lX]]) MVx.add(av, n + '_x', { from: RUNX[n].from, to: STOP[n], T0: RUNX[n].T0, T1: RUNX[n].T1, ph: RUNX[n].ph, endRy: STOPRY[n] });
const runAt = (n, t) => { const r = RUNX[n], p = pathAt(r.from, STOP[n], r.T1 - r.T0, t - r.T0); return [p.x, 1.25, p.z]; };
const C1 = [-5.0, 1.35, 1.6], C3 = [-6.5, 1.65, 0.7], C4 = [-33.0, 1.35, 0.75], C5 = [-30.45, 1.3, 0.38];
const camX = t => t < 11.2 ? C1 : t < 13.6 ? [lerp(-7.5, -15.5, smooth((t - 11.2) / 2.4)), 1.3, 2.7] : t < 17.4 ? C3 : t < 23.4 ? C4 : C5;
const newTex = ticketTex('PAUL', 'ABFAHRT 23:59 · GLEIS 3', null, 'Rückfahrt: heute Nacht');
const holeTex = ticketTex('PAUL', 'ABFAHRT 23:59 · GLEIS 3', null, 'Rückfahrt: heute Nacht'); { const x = holeTex.image.getContext('2d'); x.fillStyle = '#20140e'; x.beginPath(); x.arc(470, 250, 22, 0, 7); x.fill(); holeTex.needsUpdate = true; }
const ticket = paperMesh(newTex); const T_KNIPS = 26.1;
const HOLD = { hipY: 0.83, aL: [10, 10, 0], eL: 20, aR: [48, -10, 0], eR: 86, head: [26, 0, 0] };
pX.reset().size(pX.P.height).place(STOP.paul[0], STOP.paul[1], -90).pose(HOLD); pX.root.updateMatrixWorld(true); const TP = pX.handR.getWorldPosition(new THREE.Vector3()).toArray(); TP[1] += 0.12; TP[2] += 0.06;
const outside = dawnPlatform({
  pov: C1, look: [0.78, 1.1, -1.4],
  targets: { lenaRun: t => runAt('lena', t), backs: t => [lerp(-14, -26, smooth((t - 13.6) / 3.8)), 1.2, 0.5], three: [-29.4, 1.25, 0.5], H_sun: [-60, 2, 0.5],
    ticketP: TP, H_paulX: [-29.2, 1.41, 0.5], H_emilX: [-30.0, 1.44, -0.35], H_lenaX: [-30.2, 1.38, 1.45], H_ticket: [-29.6, 1.0, 0.45] },
  onUpdate(v, t, S) {
    MVx.update(t); puffs(t, camX(t));
    pX.root.updateMatrixWorld(true); pX.handR.getWorldPosition(v1); ticket.visible = t > 23.4; ticket.position.set(v1.x - 0.03, v1.y + 0.1, v1.z); ticket.lookAt(C5[0], C5[1], C5[2]); ticket.rotateZ(-0.08); ticket.translateX(0.075);
    ticket.material.map = t < T_KNIPS ? newTex : holeTex; ticket.material.emissiveMap = ticket.material.map;
  },
});
outside.scene.add(ticket);
const puffs = breathPuffs(outside.scene, { paul_x: pX, emil_x: eX, lena_x: lX }, (n, t) => t < 24 ? 0.5 : 0.75, (n, t) => t > 20.2);

const S = story({
  set: inside, lead: 0, tail: 0, shake: 1.0, vignette: 0.68, audioMood: 'tension',
  badge: { title: 'FOLGE 4', label: 'Der Zug ohne Morgen –', value: 'ZUSAMMEN RAUS', until: 3.2 },
  speakers: { emil: { color: '#ffd84a', voice: 'emil' }, lena_x: { color: '#7fe3ff', voice: 'lena' }, paul_x: { color: '#ffffff', voice: 'paul' } },
  pov: { phone: false }, vars: { lights: 0, red: 1, pulse: 1, pulsePeriod: 1.6, moving: 0, door: 1, platform: 1, lever: 1, platLight: 0.5, dawn: 1, spill: 1, shadow: 1 },
});
S.cast('paul', pIn, { at: [...LEVER, 90], pose: { hipY: 0.76, lean: -12, aL: [12, 76, 0], eL: 18, aR: [30, 30, 0], eR: 60 }, face: 'shock', look: 'H_door', tremble: 0.8 });
S.cast('emil', eIn, { at: [4.9, 2.7, 185], y: -0.25, pose: 'stand', face: 'angry', look: 'H_paul' });
S.cast('lena', lIn, { at: [5.25, 2.45, 180], y: -0.25, pose: 'stand', face: 'scared', look: 'H_paul' });
S.cast('paul_x', pX, { set: outside, at: [...RUNX.paul.from, -90], pose: 'stand', face: 'scared' });
S.cast('emil_x', eX, { set: outside, at: [...RUNX.emil.from, -90], pose: 'stand', face: 'scared' });
S.cast('lena_x', lX, { set: outside, at: [...RUNX.lena.from, -90], pose: 'stand', face: 'worried', look: 'H_sun' });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const CROUCH = { hipY: 0.5, lean: 34, aR: [70, 4, 0], eR: 20, aL: [60, 8, 0], eL: 30, lL: [70, 8], kL: 100, lR: [70, 8], kR: 100, head: [24, 0, 0] };
const WEDGE = { hipY: 0.7, lean: 24, aR: [84, -20, 0], eR: 12, aL: [40, 10, 0], eL: 40, lL: [30, 6], kL: 40, lR: [30, 6], kR: 40 };
const RELAX = { hipY: 0.83, lean: 4, aL: [30, 40, 0], eL: 30, aR: [14, 12, 0], eR: 30 };
const kIn = { emil: MVi.keys('emil'), paul: MVi.keys('paul') }, kX = { paul_x: MVx.keys('paul_x'), emil_x: MVx.keys('emil_x'), lena_x: MVx.keys('lena_x') };
const steps = MVx.steps(camX);

// 00:00–00:08 · Emil jumps back in and wedges the lever with a broken-off seat leg. EMIL: "Keiner bleibt hier!"
hold(1.4, { look: 'sideDoor', zoom: 56, push: 0.02, vars: { shadow: [0, 1.0, 0.2] }, sfx: [['alarmhum', 0], ['windout', 0], ['birds', 0, 0.5], ['land', T_JUMP + 0.55], ['spring', 0.2]],
  do: { ...kIn, emil: [...kIn.emil, { face: 'angry', look: 'bench', t: 1.2 }] } });
hold(2.85, { look: 'bench', zoom: 30, pov: A, povDur: 0.5, camDur: 0.35, sfx: [['crack', T_CRACK - 1.4]],
  do: { emil: [{ pose: CROUCH, t: abs(1.95), dur: 0.3 }, { pose: 'stand', look: 'lever', t: abs(T_CRACK + 0.1), dur: 0.35 }] } });
hold(4.8, { look: 'lever', zoom: 56, pov: Q, povDur: 0.5, camDur: 0.35, sfx: [['wood', abs(T_WEDGE)], ['spring', abs(3.2), 0.9]],
  do: { emil: [{ pose: WEDGE, t: abs(3.75), dur: 0.35 }, { pose: 'stand', look: 'H_paul', t: abs(T_WEDGE + 0.25), dur: 0.3 }], paul: [{ pose: RELAX, look: 'lever', tremble: 0, face: 'worried', t: abs(T_WEDGE + 0.35), dur: 0.5 }] } });
say('emil', 'Keiner | bleibt hier!', { look: 'H_emilC', zoom: 38, pov: P, povDur: 0.5, camDur: 0.35, camAt: -0.2, do: { emil: { look: 'H_paul', face: 'angry', t: -0.1 }, paul: { look: 'H_emil', face: 'scared', t: 0.2 } } });
hold(8.0, { look: 'sideDoor', zoom: 54, pov: D, povDur: 0.5, camDur: 0.35, do: { paul: { pose: 'stand', look: 'H_door', t: abs(6.5), dur: 0.3 }, emil: { look: 'H_door', t: abs(6.7) } } });
hold(9.2, { sfx: [['land', 8.75 - 8.0], ['land', 9.1 - 8.0]] });

// 00:08–00:20 · all three run along the platform into the sunrise. Behind them the door slams. Long whistle. LENA: "Nicht umdrehen!"
hold(11.2, { set: outside, look: 'door', zoom: 54, pov: C1, push: 0.015, vars: { door: [0, 0.12, 10.6 - 9.2] }, sfx: [...steps.map(e => [e[0], abs(e[1]), e[2]]), ['slam', 10.6 - 9.2 + 0.1], ['whistle_long', 10.85 - 9.2], ['birds', 0, 0.8]],
  do: { paul_x: kX.paul_x.map(k => ({ ...k, t: abs(k.t) })), emil_x: kX.emil_x.map(k => ({ ...k, t: abs(k.t) })), lena_x: [...kX.lena_x.map(k => ({ ...k, t: abs(k.t) })), { look: null, t: 0.3 }] } });
say('lena_x', 'Nicht | umdrehen!', { look: 'lenaRun', zoom: 40, pov: [-15.5, 1.3, 2.7], povDur: 2.4, camDur: 0.3, camAt: -0.6, do: { lena_x: { face: 'scared', t: -0.3 } } });
hold(13.6, {});
hold(17.4, { look: 'backs', zoom: 44, pov: C3, povDur: 0.4, camDur: 0.3 });
hold(20.0, { look: 'three', zoom: 40, pov: C4, povDur: 0.4, camDur: 0.3, push: 0.015 });

// 00:20–00:30 · they stop, out of breath. PAUL: "Alle da?" Emil and Lena nod. Paul's hand: a new ticket, "Rückfahrt: heute Nacht". A soft punch. Black.
hold(20.6, { sfx: [['pant', 0.1, 1.1]], do: { paul_x: { face: 'worried', look: 'H_lenaX', t: 0.3 }, emil_x: { face: 'scared', look: 'H_paulX', t: 0.2 }, lena_x: { face: 'worried', look: 'H_paulX', t: 0.4 } } });
say('paul_x', 'Alle da?', { look: 'paul_x', zoom: 32, headroom: 0.05, camAt: -0.15, do: { paul_x: { look: 'H_emilX', t: 0 } } });
hold(23.4, { look: 'three', zoom: 62, sfx: [['pant_soft', 0.2]],
  do: { emil_x: [{ pose: { head: [22, 0, 0] }, t: abs(22.3), dur: 0.18 }, { pose: 'stand', t: abs(22.55), dur: 0.18 }, { pose: { head: [22, 0, 0] }, t: abs(22.8), dur: 0.18 }, { pose: 'stand', t: abs(23.05), dur: 0.2 }],
        lena_x: [{ pose: { head: [20, 0, 0] }, t: abs(22.55), dur: 0.2 }, { pose: 'stand', t: abs(22.85), dur: 0.2 }], paul_x: { look: 'H_ticket', face: 'worried', t: abs(23.0) } } });
hold(29.6, { look: 'ticketP', zoom: 30, pov: C5, povDur: 0.7, camDur: 0.45, push: 0.02, sfx: [['paper', 0.1], ['knips', T_KNIPS - 23.4, 0.7], ['heart', 4.0, 0.7], ['heart', 4.9, 0.8]],
  do: { paul_x: [{ pose: HOLD, t: 0.0, dur: 0.5 }, { face: 'shock', t: T_KNIPS - 23.4 + 0.2 }] } });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
