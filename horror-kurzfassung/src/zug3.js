// DER ZUG OHNE MORGEN · Folge 3 – "Die rote Lampe" (30 s). Emergency light, the brake, two jump, Paul holds the lever.
import { story } from './core.js';
import { CAST } from './cast.js';
import { carriage } from './zugsets.js';
import { towards, loadTimings, sequencer, mover } from './lib.js';
import { THREE, clamp, lerp, smooth, rad, noise } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const A = [1.0, 1.5, 0.15], B = [3.6, 1.55, 0.45], P = [3.95, 1.5, 0.75], Q = [5.6, 1.25, -1.0], R = [4.35, 1.5, 0.1], D = [5.45, 1.5, -0.45];
const camPt = t => t < 3.3 ? A : t < 7.0 ? B : t < 8.3 ? A : t < 9.1 ? B : t < 12.6 && t > 11.4 ? P : t < 16.2 ? A : t < 20 ? P : t < 23.2 ? B : P;
const paulAv = CAST.paul(), emilAv = CAST.emil(), lenaAv = CAST.lena();
const LEVER = [4.65, -0.85];
const HOME = { paul: [4.35, 0.35, -150], emil: [3.2, 0.75, 100], lena: [4.3, -0.3, 160] };
const T_PULL = 8.75, T_JOLT = 9.1;
const MV = mover()
  .add(lenaAv, 'lena', { from: [4.3, -0.3], to: [4.95, -0.75], T0: 0.6, T1: 1.4, mode: 'walk', endRy: 172 })
  .add(paulAv, 'paul', { from: [4.35, 0.35], to: LEVER, T0: 8.0, T1: 8.55, mode: 'walk', endRy: 180 })
  .add(emilAv, 'emil', { from: [3.2, 0.75], to: [3.45, 0.8], T0: T_JOLT, T1: T_JOLT + 0.3, mode: 'still', endRy: 95, keepRy: true })
  .add(lenaAv, 'lena', { from: [4.95, -0.75], to: [5.5, 0.25], T0: 6.6, T1: 7.3, mode: 'walk', endRy: -125 })
  .add(lenaAv, 'lena', { from: [5.5, 0.25], to: [3.8, 0.2], T0: 12.8, T1: 13.8, mode: 'walk', endRy: -40 })
  .add(emilAv, 'emil', { from: [3.45, 0.8], to: [3.3, 0.15], T0: 14.2, T1: 14.6, mode: 'walk', endRy: 100 })
  .add(emilAv, 'emil', { from: [3.3, 0.15], to: [4.15, 0.2], T0: 14.6, T1: 15.3, mode: 'walk', endRy: 60 })
  .add(lenaAv, 'lena', { from: [3.8, 0.2], to: [5.2, 0.95], T0: 14.9, T1: 15.9, mode: 'walk', endRy: 10 })
  .add(emilAv, 'emil', { from: [4.15, 0.2], to: [4.75, 0.8], T0: 15.3, T1: 15.9, mode: 'walk', endRy: 10 })
  .add(lenaAv, 'lena', { from: [5.2, 0.95], to: [5.25, 2.45], T0: 20.35, T1: 20.95, mode: 'still', arc: 0.35, y1: -0.25, endRy: 180 })
  .add(emilAv, 'emil', { from: [4.75, 0.8], to: [4.9, 2.7], T0: 20.95, T1: 21.55, mode: 'still', arc: 0.4, y1: -0.25, endRy: 185 });

const set = carriage({
  pov: A, look: [4.8, 1.3, -0.3], platform: true, pulse: ['#ff2a1a', 3.2], shadowAt: [4.1, 1.2, -1.37], shadowRy: 0,
  targets: { endArea: [4.6, 1.2, 0.0], paulLever: [4.5, 1.25, -1.0], wallShadow: [4.22, 1.42, -1.05], H_note: [5.08, 1.62, -1.4], H_door: [5.0, 1.0, 2.0], H_emil: [3.7, 1.0, 0.82], H_paul: [4.65, 1.41, -0.85], H_out: [5.0, 1.0, 2.6], H_lena: [4.9, 1.35, 1.0], H_emilOut: [4.8, 1.2, 2.7] },
  onUpdate(v, t, S) {
    MV.update(t);
    // the lever springs back against Paul's hands
    const strain = clamp((t - 15.5) / 2) * (1 - clamp((t - 29.5) / 0.3)); S.parts.arm.rotation.z = (v.lever ?? 0) * rad(80) - strain * rad(9) * (0.6 + 0.4 * Math.sin(t * 3.1) * noise(t * 2, 4));
    lanternGlow.intensity = 4.0 * (v.lantern ?? 0) * (0.85 + 0.15 * noise(t * 7, 2));
  },
});
const lanternGlow = new THREE.PointLight('#ffa860', 0, 4.5, 1.2); lanternGlow.position.set(4.0, 1.3, 0.45); set.scene.add(lanternGlow);

const S = story({
  set, lead: 0, tail: 0, shake: 1.0, vignette: 0.75, audioMood: 'tension',
  badge: { title: 'FOLGE 3', label: 'Der Zug ohne Morgen –', value: 'DIE ROTE LAMPE', until: 3.2 },
  speakers: { paul: { color: '#ffffff', voice: 'paul' }, emil: { color: '#ffd84a', voice: 'emil' }, lena: { color: '#7fe3ff', voice: 'lena' } },
  pov: { phone: false }, vars: { lights: 0, red: 1, pulse: 1, pulsePeriod: 1.6, moving: 1, door: 0, platform: 0, lever: 0, platLight: 1.3 },
});
S.cast('paul', paulAv, { at: HOME.paul, pose: 'stand', face: 'worried', look: 'H_note' });
S.cast('emil', emilAv, { at: HOME.emil, pose: 'stand', face: 'scared', look: 'H_note' });
S.cast('lena', lenaAv, { at: HOME.lena, pose: 'stand', face: 'worried', look: 'H_note' });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const POINT = { hipY: 0.83, aR: [118, 6, 0], eR: 6, head: [-8, 0, 0] };
const GRAB = { hipY: 0.83, lean: 6, aR: [100, 0, 0], eR: 22, aL: [92, 12, 0], eL: 30, head: [-6, 0, 0] };
const PULLED = { hipY: 0.78, lean: -4, aR: [62, 0, 0], eR: 18, aL: [56, 12, 0], eL: 26 };
const STRAIN = { hipY: 0.76, lean: -14, aR: [66, 2, 0], eR: 34, aL: [60, 12, 0], eL: 40, lL: [14, 6], kL: 20, lR: [-10, 6], kR: 8 };
const HOLDL = { hipY: 0.8, lean: -6, aL: [12, 76, 0], eL: 18, aR: [12, 14, 0], eR: 34, lL: [8, 8], kL: 10, lR: [-6, 8], kR: 6 };
const HOLDS = { ...HOLDL, hipY: 0.76, lean: -12, aR: [30, 30, 0], eR: 60, lL: [18, 10], kL: 24 };
const knips = []; for (let t = 0.5; t < T_JOLT + 0.4; t += 1.25) knips.push(['knips', +t.toFixed(2), 1.2]);
const keys = { lena: MV.keys('lena'), emil: MV.keys('emil'), paul: MV.keys('paul') };

// 00:00–00:08 · emergency light. Lena points at a note beside a red lever. LENA: "Bei rotem Signal bleibt er stehen."
hold(3.3, { look: 'endArea', zoom: 46, push: 0.02, sfx: [['train', 0], ['alarmhum', 0], ...knips], do: { ...keys, lena: [...keys.lena, { look: 'H_note', t: 1.0 }, { pose: POINT, t: 1.6, dur: 0.35 }] } });
say('lena', '„Bei rotem Signal | bleibt er stehen.“', { look: 'note', zoom: 22, pov: B, povDur: 0.7, camDur: 0.45, camAt: -0.6, push: 0.03 });
hold(7.0, {});
hold(8.3, { look: 'paul', zoom: 26, pov: A, povDur: 0.6, camDur: 0.4, headroom: 0.1, do: { paul: { look: 'lever', face: 'scared', t: 0.3 }, lena: { pose: 'stand', look: 'H_paul', t: 0.4 }, emil: { look: 'H_paul', t: 0.5 } } });

// 00:08–00:20 · Paul pulls the lever. A jolt. Emil falls against a bench. The door opens to the dark platform. PAUL: "Raus! Sofort!" The punching stops.
hold(T_JOLT, { look: 'lever', zoom: 52, pov: Q, povDur: 0.5, camDur: 0.35, vars: { lever: [1, 0.3, T_PULL - 8.3] }, sfx: [['lever', T_PULL - 8.3 + 0.15]],
  do: { paul: [{ pose: GRAB, look: 'lever', t: 0.2, dur: 0.25 }, { pose: PULLED, t: T_PULL - 8.3, dur: 0.3 }] } });
hold(T_JOLT + 0.18, { look: 'lever', zoom: 58, aim: [4, -6], roll: 6, camDur: 0.05, vars: { moving: [0, 1.0, 0] }, sfx: [['jolt', 0], ['brake', 0.05], ['trainstop', 0]],
  do: { emil: { pose: 'slump', face: 'shock', t: 0, dur: 0.18 }, lena: { pose: 'cower', face: 'shock', t: 0.02, dur: 0.18 }, paul: { pose: STRAIN, face: 'shock', t: 0, dur: 0.15 } } });
hold(10.4, { look: 'H_emil', zoom: 36, pov: R, povDur: 0.35, camDur: 0.25, do: { emil: { pose: 'kneel', look: 'H_paul', t: 0.4, dur: 0.4 }, lena: { pose: 'stand', look: 'H_emil', t: 0.6, dur: 0.4 } } });
hold(11.4, { look: 'sideDoor', zoom: 52, vars: { door: [1, 0.7, 0.05], platform: [1, 0, 0] }, sfx: [['creak', 0.0, 0.9], ['windout', 0.3]], do: { emil: { look: 'H_door', t: 0.2 }, lena: { look: 'H_door', t: 0.3 } } });
say('paul', 'Raus! | Sofort!', { look: 'paul', zoom: 32, pov: P, povDur: 0.45, camDur: 0.3, headroom: 0.1, camAt: -0.2, do: { paul: { at: [...LEVER, 90], pose: HOLDL, look: 'H_door', face: 'shock', t: -0.35, dur: 0.3 } } });
hold(16.2, { look: 'endArea', zoom: 50, pov: A, povDur: 0.6, camDur: 0.4,
  do: { emil: [{ pose: 'stand', t: abs(13.9), dur: 0.35 }, { look: 'H_door', t: abs(15.9) }], lena: { look: 'H_out', t: abs(15.7) }, paul: { look: 'lever', face: 'worried', t: abs(13.2) } } });
hold(20.0, { look: 'paul', zoom: 34, pov: P, povDur: 0.6, camDur: 0.4, headroom: 0.1, push: 0.02, sfx: [['spring', 0.4], ['spring', 2.0, 0.8]], do: { paul: { pose: HOLDS, tremble: 0.7, face: 'angry', look: 'H_lena', t: 0.3, dur: 0.6 } } });

// 00:20–00:30 · Lena and Emil jump out. Paul holds the lever as it springs back. EMIL: "Paul! Komm!" PAUL: "Einer muss ihn halten." The conductor's shadow behind Paul.
hold(21.75, { look: 'sideDoor', zoom: 60, pov: D, povDur: 0.5, camDur: 0.35, sfx: [['land', 20.95 - 20.0], ['land', 21.6 - 20.0]], do: { lena: { look: 'H_paul', t: abs(21.1) }, emil: { look: 'H_paul', face: 'shock', t: abs(21.7) } } });
say('emil', 'Paul! | Komm!', { look: 'H_emilOut', zoom: 30, camAt: -0.15, do: { emil: { look: 'H_paul', face: 'shock', t: -0.2 } } });
hold(23.25, {});
say('paul', 'Einer muss | ihn halten.', { look: 'paul', zoom: 30, pov: P, povDur: 0.5, camDur: 0.35, headroom: 0.1, camAt: -0.2, do: { paul: { look: 'H_door', face: 'worried', t: -0.1, dur: 0.3 } } });
hold(29.6, { look: 'wallShadow', zoom: 48, push: 0.03, vars: { shadow: [1, 1.4, abs(26.9)], lantern: [1, 1.2, abs(26.7)] }, sfx: [['stepw', abs(26.6), 0.6], ['stepw', abs(27.1), 0.7], ['sting', abs(27.3), 0.8], ['knips', abs(28.6), 1.4]],
  do: { paul: { look: 'H_door', face: 'shock', tremble: 1, t: abs(28.7), dur: 0.2 } } });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
