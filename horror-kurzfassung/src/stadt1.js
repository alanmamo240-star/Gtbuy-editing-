// DIE STADT HINTER DER SPERRE · Folge 1 – "Nicht öffnen" (30 s). Kitchen at night, a warning on every phone, a voice at the door.
import { story } from './core.js';
import { CAST } from './cast.js';
import { kitchen, porch, phoneMesh, alertTex, darkTex, peepholeOverlay } from './stadtsets.js';
import { towards, loadTimings, sequencer, mover } from './lib.js';
import { THREE, clamp, lerp, smooth, rad } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const K1 = [2.6, 1.6, 2.0], K2 = [0.3, 1.2, -0.45], K3 = [1.2, 1.55, -0.5], K4 = [-0.45, 1.35, -1.45], K5 = [-1.4, 1.3, 0.0], K6 = [-2.35, 1.25, 0.15];
const LIFT = [0.02, 1.08, 0.36];
const benAv = CAST.ben(), ninaAv = CAST.nina(), maxAv = CAST.max(), dopAv = CAST.ben();
const SEAT = { ben: [1.05, 0, -90], nina: [0, -0.78, 0], max: [0, 0.78, 180] };
const T_ALERT = 0.9, T_BELL = 8.25;
const MV = mover()
  .add(benAv, 'ben', { from: [1.05, 0], to: [1.25, 1.3], T0: 16.8, T1: 17.45, mode: 'walk', endRy: -90 })
  .add(benAv, 'ben', { from: [1.25, 1.3], to: [-2.95, 1.25], T0: 17.45, T1: 19.8, mode: 'walk', endRy: -90 });
const alert = alertTex('NOTFALLWARNUNG', ['Bleiben Sie', 'drinnen.', 'Öffnen Sie', 'niemandem.']);
const phones = { ben: phoneMesh(darkTex), nina: phoneMesh(darkTex), max: phoneMesh(darkTex) };
const PH = { ben: [0.6, 0.8, 0.02, 0.4], nina: [0.08, 0.8, -0.32, 2.9], max: [-0.06, 0.8, 0.32, 0.2] };
const v1 = new THREE.Vector3();
const room = kitchen({
  pov: K1, look: [0, 0.85, 0],
  targets: { maxPhone: [0.02, 1.08, 0.36], H_door: [-3.5, 1.4, 1.25], H_ben: [1.05, 1.1, 0], H_benUp: [1.05, 1.5, 0], H_max: [0, 1.15, 0.78], H_nina: [0, 1.15, -0.78], two: [0.5, 1.15, -0.4], H_phone: [0, 0.8, 0], benDoor: [-3.0, 1.3, 1.2] },
  onUpdate(v, t, S) {
    MV.update(t);
    const on = t > T_ALERT; for (const n in phones) { const p = phones[n]; p.userData.screen.material.map = on ? alert : darkTex; }
    // Max lifts his phone to read it
    const lift = smooth((t - 1.6) / 0.5) * (1 - smooth((t - 7.6) / 0.5)), pm = phones.max;
    if (lift > 0) { pm.position.set(lerp(PH.max[0], LIFT[0], lift), lerp(PH.max[1], LIFT[1], lift), lerp(PH.max[2], LIFT[2], lift)); pm.rotation.set(0, PH.max[3], 0); const q0 = pm.quaternion.clone(); pm.lookAt(K2[0], K2[1], K2[2]); pm.rotateX(Math.PI / 2); pm.quaternion.slerpQuaternions(q0, pm.quaternion.clone(), lift); }
    else { pm.position.set(PH.max[0], PH.max[1], PH.max[2]); pm.rotation.set(0, PH.max[3], 0); }
    alertGlow.intensity = on ? 0.9 * (0.75 + 0.25 * Math.sin(t * 9)) * (1 - smooth((t - 7.5) / 1.5)) : 0;
  },
});
for (const n of ['ben', 'nina']) { phones[n].position.set(PH[n][0], PH[n][1], PH[n][2]); phones[n].rotation.y = PH[n][3]; }
for (const n in phones) room.scene.add(phones[n]);
const alertGlow = new THREE.PointLight('#ff5a4a', 0, 2.5, 1.5); alertGlow.position.set(0.2, 1.0, 0); room.scene.add(alertGlow);
const outside = porch({ targets: { H_dop: [1.3, 1.55, 0], dopFace: [1.3, 1.5, 0] } });

const S = story({
  set: room, lead: 0, tail: 0, shake: 0.6, vignette: 0.7, audioMood: 'tension',
  badge: { title: 'FOLGE 1', label: 'Die Stadt hinter der Sperre –', value: 'NICHT ÖFFNEN', until: 3.4 },
  speakers: { handy: { color: '#ff8a7a', voice: 'durchsage', fx: 'phone' }, aussen: { color: '#d0d4ee', voice: 'ben', fx: 'door' }, max: { color: '#9cf09c', voice: 'max' }, doppel: { color: '#ff9ad0', voice: 'ben2', fx: 'door' } },
  pov: { phone: false }, vars: { handle: 0 },
});
const SIT = 'sitChair';
S.cast('ben', benAv, { at: SEAT.ben, pose: SIT, face: 'neutral', look: 'H_phone' });
S.cast('nina', ninaAv, { at: SEAT.nina, pose: SIT, face: 'neutral', look: 'H_phone' });
S.cast('max', maxAv, { at: SEAT.max, pose: SIT, face: 'neutral', look: 'H_phone' });
S.cast('dop', dopAv, { set: outside, at: [1.3, 0, -90], pose: 'stand', face: 'creepy', look: [0.05, 1.58, 0] });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const READ = { hipY: 0.5, aR: [58, -16, 0], eR: 70, aL: [52, -16, 0], eL: 70, lL: [90, 4], kL: 90, lR: [90, 4], kR: 90, head: [18, 0, 0] };
const GRAB = { hipY: 0.5, lean: 6, aR: [70, -40, 0], eR: 20, aL: [22, 4, 0], eL: 60, lL: [90, 4], kL: 90, lR: [90, 4], kR: 90 };
const PEEP = { hipY: 0.83, lean: 14, head: [-4, 0, 0], aR: [30, 10, 0], eR: 60, aL: [40, 10, 0], eL: 70 };
const kB = MV.keys('ben');

// 00:00–00:08 · Ben, Nina and Max at the kitchen table. Every phone beeps. PHONE: "Bleiben Sie drinnen. Öffnen Sie niemandem."
hold(2.6, { look: 'table', zoom: 54, push: 0.02, sfx: [['alert', T_ALERT], ['roomtone', 0]],
  do: { ben: [...kB, { face: 'worried', t: T_ALERT + 0.3 }], nina: { face: 'worried', t: T_ALERT + 0.4 }, max: [{ face: 'scared', t: T_ALERT + 0.2 }, { pose: READ, look: 'maxPhone', t: 1.5, dur: 0.5 }] } });
say('handy', 'Bleiben Sie drinnen. | Öffnen Sie niemandem.', { look: 'maxPhone', zoom: 24, pov: K2, povDur: 0.6, camDur: 0.4, tag: 'HANDY', camAt: -0.35, push: 0.02 });
hold(8.0, { look: 'table', zoom: 50, pov: K1, povDur: 0.6, camDur: 0.4, do: { max: { pose: SIT, look: 'H_nina', t: abs(7.4), dur: 0.5 }, nina: { look: 'H_max', t: abs(6.9) }, ben: { look: 'H_door', t: abs(7.2) } } });

// 00:08–00:20 · doorbell. VOICE OUTSIDE: "Ben? Ich habe den Schlüssel vergessen." MAX: "Das ist deine Stimme." Ben stands up slowly; Nina grabs his sleeve.
hold(9.5, { look: 'door', zoom: 34, pov: K3, povDur: 0.5, camDur: 0.35, push: 0.02, sfx: [['doorbell', T_BELL - 8.0]],
  do: { ben: { look: 'H_door', face: 'scared', t: T_BELL - 8.0 + 0.2 }, nina: { look: 'H_door', face: 'scared', t: T_BELL - 8.0 + 0.3 }, max: { look: 'H_door', face: 'scared', t: T_BELL - 8.0 + 0.25 } } });
say('aussen', 'Ben? | Ich habe den Schlüssel | vergessen.', { tag: 'DRAUSSEN' });
hold(12.4, {});
say('max', 'Das ist | deine Stimme.', { look: 'max', zoom: 30, pov: K4, povDur: 0.5, camDur: 0.35, headroom: 0.08, camAt: -0.2, do: { max: { look: 'H_ben', face: 'shock', t: -0.1 } } });
hold(20.0, { look: 'two', zoom: 70, pov: K5, povDur: 0.6, camDur: 0.4,
  do: { ben: [{ look: 'H_door', face: 'worried', t: 0 }, { pose: 'stand', t: abs(14.0), dur: 1.2 }, { look: 'H_door', t: abs(16.6) }, { pose: PEEP, t: abs(19.6), dur: 0.4 }],
        nina: [{ look: 'H_benUp', face: 'scared', t: abs(14.6) }, { pose: GRAB, t: abs(15.6), dur: 0.45 }, { pose: SIT, t: abs(17.2), dur: 0.5 }, { look: 'benDoor', t: abs(18.0) }],
        max: { look: 'benDoor', t: abs(17.8) } }, sfx: [['chairscrape', abs(14.1)], ['heart', abs(16.0), 0.7], ['heart', abs(17.0), 0.8]] });

// 00:20–00:30 · through the peephole: a second Ben outside. He smiles. DOUBLE: "Ich weiß, dass du mich siehst." The handle moves. Black.
hold(22.3, { set: outside, cut: true, look: 'H_dop', zoom: 92, pov: [0.05, 1.58, 0], push: 0.012, overlay: peepholeOverlay, sfx: [['sting', 0.1, 0.6]] });
say('doppel', 'Ich weiß, | dass du mich siehst.', { overlay: peepholeOverlay, do: { dop: { pose: { head: [0, 0, -12] }, t: 0.9, dur: 1.2 } } });
hold(27.0, { overlay: peepholeOverlay, do: { dop: { at: [0.85, 0, -90], dur: 1.4, t: 0.5, walk: false } } });
hold(29.6, { set: room, cut: true, look: 'handle', zoom: 34, pov: K6, push: 0.03, vars: { handle: [1, 1.2, 0.5] }, sfx: [['handle', 0.5], ['heart', 0.3, 0.9], ['heart', 1.2, 1.0]], do: { ben: { pose: 'stand', look: 'handle', face: 'shock', tremble: 1, t: 0 } } });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
