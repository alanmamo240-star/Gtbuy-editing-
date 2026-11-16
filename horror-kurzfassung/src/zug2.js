// DER ZUG OHNE MORGEN · Folge 2 – "Die Fahrkarten" (30 s). Inside the empty carriage, moving through the night.
import { story } from './core.js';
import { POSES } from './toon.js';
import { CAST } from './cast.js';
import { carriage, ticketTex, paperMesh } from './zugsets.js';
import { towards, loadTimings, sequencer, mover } from './lib.js';
import { THREE, clamp, lerp, smooth, easeIO, rad, noise } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

// camera stations
const ZA = [1.2, 1.5, -0.45], ZB = [3.2, 1.45, -0.2], S2 = [0.5, 1.5, 0.1], S3 = [2.0, 1.4, -0.45];
const camPt = t => t < 4.3 ? ZA : t < 8.0 ? ZB : (t > 13.4 && t < 17.6) ? S3 : S2;

// people: Paul at the side door, Emil and Lena behind him in the open end of the carriage
const paulAv = CAST.paul(), emilAv = CAST.emil(), lenaAv = CAST.lena();
const HOME = { paul: [5.0, 0.95, 0], emil: [4.5, -0.1, 30], lena: [4.05, -0.25, 50] };
const LEG = [3.22, -0.86];                                            // Lena in the leg room of the last compartment, facing the bench
const ghosts = []; const GH = [[3.0, 1.38], [3.45, 1.47], [1.55, 1.42], [-0.05, 1.45], [0.25, 1.36], [-1.6, 1.44]];
const ghostAt = GH.map(([x, y]) => [x, -1.75, y]);

// three tickets on the seat; Lena picks them up
const SEAT = [2.72, 0.487], TZ = [-0.6, -0.86, -1.12], NAMES = ['PAUL', 'EMIL', 'LENA'];
const tickets = NAMES.map(n => paperMesh(ticketTex(n, 'ABFAHRT 23:59 · GLEIS 3', null, 'Ankunft: entfällt')));
const BEND = { hipY: 0.66, lean: 42, head: [36, 0, 0], aL: [72, 6, 0], eL: 12, aR: [72, 6, 0], eR: 12, lL: [42, 4], kL: 58, lR: [42, 4], kR: 58 };
const HOLD = { hipY: 0.83, aL: [40, -14, 0], eL: 100, aR: [40, -14, 0], eR: 100, head: [24, 0, 0] };
const T_PICK = 9.55, T_UP = 0.5;
function handsWorld(av, x, z, ry, pose) { av.reset().size(av.P.height).place(x, z, ry).pose(pose); av.root.updateMatrixWorld(true); const a = new THREE.Vector3(), b = new THREE.Vector3(); av.handL.getWorldPosition(a); av.handR.getWorldPosition(b); return a.add(b).multiplyScalar(0.5); }
const HELD = handsWorld(lenaAv, LEG[0], LEG[1], -90, HOLD); const TH = [HELD.x, HELD.y + 0.06, HELD.z];

const MV = mover();
MV.add(lenaAv, 'lena', { from: [4.05, -0.25], to: [3.3, -0.2], T0: 8.05, T1: 8.55, mode: 'walk', endRy: -150 });
MV.add(lenaAv, 'lena', { from: [3.3, -0.2], to: LEG, T0: 8.55, T1: 9.05, mode: 'walk', endRy: -90 });
MV.add(emilAv, 'emil', { from: [4.5, -0.1], to: [5.0, 0.35], T0: 26.0, T1: 26.7, mode: 'walk', endRy: -120, keepRy: true });

const v1 = new THREE.Vector3(), v2 = new THREE.Vector3();
const set = carriage({
  pov: ZA, look: [5, 1.1, 0.9],
  targets: {
    paulDoor: [5.0, 1.15, 1.0], groupZ: [3.9, 1.1, -0.2], winL: [3.2, 1.45, -1.4], winWide: [1.8, 1.4, -1.4],
    ticketsHeld: TH, H_door: [5.36, 1.0, 1.4], H_aisle: [-6, 1.2, 0], H_lena: [LEG[0], 1.38, LEG[1]], H_emil: [4.5, 1.44, -0.1], lenaCam: [LEG[0], 1.22, LEG[1]], H_paul: [5.0, 1.41, 0.95], H_win: [3.2, 1.4, -1.5], H_seat: [SEAT[0], 0.5, -0.86],
  },
  onUpdate(v, t, S) {
    MV.update(t);
    // tickets: on the seat, then fanned out in Lena's hands, facing the camera
    lenaAv.root.updateMatrixWorld(true); lenaAv.handL.getWorldPosition(v1); lenaAv.handR.getWorldPosition(v2); v1.add(v2).multiplyScalar(0.5);
    tickets.forEach((tk, i) => {
      const fl = [SEAT[0], SEAT[1], TZ[i]], u = smooth((t - T_PICK - i * 0.06) / 0.2), w = smooth((t - T_PICK) / T_UP);
      const hx = [v1.x, v1.y + 0.06 + (1 - i) * 0.012, v1.z];
      tk.position.set(lerp(fl[0], hx[0], u), lerp(fl[1], hx[1], u), lerp(fl[2], hx[2], u));
      if (u <= 0) { tk.rotation.set(-Math.PI / 2, 0, Math.PI / 2 + (i - 1) * 0.15); return; }
      const cp = camPt(t); tk.lookAt(cp[0], cp[1], cp[2]); tk.rotateZ((1 - i) * 0.06 * w); tk.translateY((1 - i) * 0.12 * w); tk.translateX((i - 1) * 0.02 * w);
    });
    // the faces outside: motionless, never blinking
    for (const gh of ghosts) { gh.blink(1); gh.head.rotation.z = 0; gh.torso.rotation.z = 0; }
    ghostLight.intensity = 0.9 * (v.ghostLight ?? 0);
  },
});
for (const tk of tickets) set.scene.add(tk);
const ghostLight = new THREE.PointLight('#9fb4ff', 0, 5, 1.2); ghostLight.position.set(2.0, 1.6, -0.6); set.scene.add(ghostLight);

const S = story({
  set, lead: 0, tail: 0, shake: 1.0, vignette: 0.72, audioMood: 'tension',
  badge: { title: 'FOLGE 2', label: 'Der Zug ohne Morgen –', value: 'DIE FAHRKARTEN', until: 3.6 },
  speakers: { paul: { color: '#ffffff', voice: 'paul' }, emil: { color: '#ffd84a', voice: 'emil' }, lena: { color: '#7fe3ff', voice: 'lena' }, schaffner: { color: '#ff9ad0', voice: 'schaffner', fx: 'radio' } },
  pov: { phone: false }, vars: { lights: 1, moving: 1, red: 0, door: 0 },
});
S.cast('paul', paulAv, { at: HOME.paul, pose: 'stand', face: 'scared' });
S.cast('emil', emilAv, { at: HOME.emil, pose: 'stand', face: 'worried', look: 'H_paul' });
S.cast('lena', lenaAv, { at: HOME.lena, pose: 'stand', face: 'worried', look: 'H_paul' });
ghostAt.forEach((p, i) => { const gh = CAST.paul({ skin: '#c9ced8', top: '#3a3c48', topStyle: 'coat', bottom: '#2a2c36', hair: ['short', 'bun', 'buzz', 'long', 'short', 'bob'][i], hairColor: '#5a5c66', cap: i === 2 ? '#3a3a44' : undefined, height: [0.98, 0.9, 1.02, 0.94, 0.86, 1.0][i], seed: 40 + i });
  ghosts.push(gh); S.cast('g' + i, gh, { at: [p[0], p[1], 0], y: p[2] - (0.83 + 0.77) * gh.P.height, pose: 'stand', face: 'dead', look: 'H_lena', hide: true }); });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const PULL1 = { hipY: 0.83, lean: -6, aR: [64, 26, 0], eR: 34, aL: [40, 20, 0], eL: 50 }, PULL2 = { hipY: 0.8, lean: -15, aR: [58, 20, 0], eR: 12, aL: [36, 16, 0], eL: 30 };
const pulls = []; for (let k = 0; k < 9; k++) pulls.push({ pose: k % 2 ? PULL2 : PULL1, t: 0.3 + k * 0.38, dur: 0.16 });
const knips = []; for (let t = 0.7; t < 28; t += 1.45) knips.push(['knips', +t.toFixed(2), t < 8 ? 1 : 0.6]);
const rattles = []; for (let k = 0; k < 9; k++) if (k % 2) rattles.push(['rattle', 0.3 + k * 0.38]);

// 00:00–00:08 · in the empty carriage. Paul pulls at the locked door. PAUL: "Die geht nicht mehr auf!" · slow ticket punching
hold(4.3, { look: 'paulDoor', zoom: 50, push: 0.015, sfx: [['train', 0], ...knips, ...rattles], do: { paul: [{ look: 'H_door', face: 'scared' }, ...pulls], lena: MV.keys('lena'), emil: MV.keys('emil') } });
say('paul', 'Die geht | nicht mehr auf!', { look: 'paul', zoom: 34, pov: ZB, povDur: 0.7, camDur: 0.4, headroom: 0.1, camAt: -0.2,
  do: { paul: { pose: 'stand', at: [...HOME.paul.slice(0, 2), towards(HOME.paul, HOME.emil)], look: 'H_emil', face: 'shock', t: -0.15, dur: 0.35 } } });
hold(8.0, { look: 'H_aisle', zoom: 42, push: 0.025, camAt: 0.15,
  do: { paul: { look: 'H_aisle', face: 'scared', t: 0.4 }, emil: { look: 'H_aisle', t: 0.25 }, lena: { look: 'H_aisle', t: 0.55 } } });

// 00:08–00:20 · Lena finds three tickets on the seats. LENA: "Hier stehen unsere Namen." EMIL: "Und wann kommen wir an?" Insert: "Ankunft: entfällt".
hold(10.15, { look: 'lenaCam', zoom: 30, pov: S2, povDur: 0.8, camDur: 0.45,
  do: { lena: [{ look: 'H_seat', face: 'worried', t: 0.1 }, { pose: BEND, t: abs(T_PICK - 0.45), dur: 0.4 }, { pose: HOLD, look: 'ticketsHeld', t: abs(T_PICK + 0.05), dur: T_UP }], paul: { look: 'H_lena', t: 0.9 }, emil: { look: 'H_lena', t: 0.7 } },
  sfx: [['paper', T_PICK - 8.0]] });
say('lena', 'Hier stehen | unsere Namen.', { do: { lena: { face: 'scared', t: 0 } } });
say('emil', 'Und wann | kommen wir an?', { look: 'emil', zoom: 28, camAt: -0.2, headroom: 0.1, do: { emil: { look: 'H_lena', face: 'worried', t: 0 } } });
hold(17.6, { look: 'ticketsHeld', zoom: 27, pov: S3, povDur: 0.6, camDur: 0.45, push: 0.018, sfx: [['heart', 0.9, 0.7], ['heart', 1.8, 0.8], ['heart', 2.7, 0.9]] });
hold(20.0, { look: 'groupZ', zoom: 40, pov: S2, povDur: 0.6, camDur: 0.4, vars: { flicker: [1, 0.05, 0.9] }, sfx: [['buzz', 0.9, 0.6], ['pant_soft', 0.3]],
  do: { lena: { pose: 'stand', look: 'H_emil', t: 0.3 }, emil: { at: [4.5, -0.1, towards([4.5, -0.1], LEG)], look: 'H_paul', t: 0.2, dur: 0.4 }, paul: { at: [5.0, 0.95, towards([5.0, 0.95], LEG)], look: 'H_lena', t: 0.5, dur: 0.4 } } });

// 00:20–00:30 · motionless faces behind the glass. LOUDSPEAKER: "Bitte sitzen bleiben. Die Toten steigen zuerst aus." Emil recoils. Lights out.
const showG = ghosts.map((_, i) => ['g' + i, { hide: false, t: 0.32 + (i % 3) * 0.04 }]);
hold(22.3, { look: 'winL', zoom: 30, vars: { flicker: [2, 0.02, 0.0], ghostLight: [1, 0.3, 0.3] }, sfx: [['sting', 0.34, 0.7], ['buzz', 0.0, 0.8]],
  do: { ...Object.fromEntries(showG), lena: { look: 'H_win', face: 'shock', pose: 'gasp', t: 0.5, dur: 0.2 } } });
say('schaffner', 'Bitte sitzen bleiben. | Die Toten | steigen zuerst aus.', { look: 'speaker', zoom: 18, tag: 'LAUTSPRECHER', camAt: -0.25, vars: { flicker: [0, 0.05, 0] }, sfx: [['chime', -0.55]],
  do: { paul: { look: 'speaker', t: 0.3 }, emil: { look: 'speaker', t: 0.2 } } });
hold(28.0, { look: 'emil', zoom: 30, headroom: 0.1, camAt: 0.05, do: { emil: [{ face: 'shock', look: 'H_win', pose: 'block', t: abs(26.0), dur: 0.25, tremble: 1 }] }, sfx: [['stumble', abs(26.2)]] });
hold(29.6, { look: 'winWide', zoom: 40, vars: { flicker: [1.6, 0.02, 0], lights: [0, 0.08, 0.35] }, sfx: [['buzz', 0.0, 0.8], ['lightsout', 0.35]] });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
