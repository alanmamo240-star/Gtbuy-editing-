// FLUCHT AUS ASCHENTAL · Folge 3 – "Die Brücke" (80 s). Night at the old bridge: a checkpoint, floodlights, a queue.
// A father comes back to his children - without breath. The man in the coat holds up a photo: Luca. Elias stands beside him.
// Down the embankment, along the river under the searchlight, to the old jetty. Someone is sitting in the boat.
import { story } from './core.js';
import { CAST } from './cast.js';
import { makeToon } from './toon.js';
import { river, suitcase, flashlight, photoCard, car } from './fluchtsets.js';
import { at } from './util.js';
import { towards, loadTimings, sequencer, mover, runPath, breathPuffs } from './lib.js';

const clock = (h, m, t) => { const mm = m + Math.floor(t / 60); return `${String(h + Math.floor(mm / 60)).padStart(2, '0')}:${String(mm % 60).padStart(2, '0')}`; };
const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const D = 0.6;   // bridge deck height
const C0 = [-4.6, 1.15, 6.4];
const RUN1 = [[44.0, ...C0], [45.0, -7.5, 1.3, 2.0], [46.0, -9.4, 0.4, -1.2], [47.2, -10.4, -1.5, -3.8], [48.2, -11.0, -2.7, -6.2]];
const RUN2 = [[52.0, -11.0, -2.7, -6.2], [55.4, -19.5, -2.65, -6.3], [58.4, -27.2, -2.7, -6.2], [59.4, -28.2, -3.25, -6.0], [62.6, -28.2, -3.25, -6.0], [64.4, -31.0, -2.7, -6.3], [65.4, -31.6, -2.7, -6.4]];
const run1 = runPath(RUN1, 0.04, 0.32), run2 = runPath(RUN2, 0.06, 0.3);
const P1 = [-11.0, -2.7, -6.2], PEND = [-31.6, -2.7, -6.4];
const camPt = t => run1(t) || run2(t) || (t < 44 ? C0 : t < 52 ? P1 : PEND);
const MIRA0 = [-6.4, 4.4];

const mira = CAST.mira(), off = CAST.offizier(), elias = CAST.elias({ hood: true, hair: 'short' }), bruder = CAST.elias({ hood: true, hair: 'short' });
const sol = [0, 1, 2].map(i => { const s = CAST.soldat({ seed: 40 + i, skin: ['tan', 'light', 'fair'][i] }); s.handR.add(flashlight()); return s; });
const civ = (o, i) => { const av = makeToon({ real: true, skin: ['light', 'tan', 'fair', 'brown', 'pale', 'light', 'tan'][i % 7], hair: ['short', 'bob', 'bun', 'buzz', 'long', 'curly', 'ponytail'][i % 7], hairColor: ['#3a2a20', '#6a4024', '#2a1a14', '#1a1210', '#8a5a2a', '#1a1210', '#5a3a22'][i % 7], top: ['#6a5a4a', '#4a5a7a', '#8a6a5a', '#5a6a5a', '#7a4a4a', '#5a5a6a', '#4a6a7a'][i % 7], topStyle: i % 2 ? 'coat' : 'jacket', bottom: '#2a2a32', shoe: '#2a2020', seed: 60 + i, ...o }); return av; };
const boy = civ({ hood: true, hoodColor: '#4a4a52', top: '#4a4a52', topStyle: 'hoodie', height: 0.9 }, 0), mom = civ({ height: 0.98 }, 1), kid1 = civ({ height: 0.7, hair: 'pigtails' }, 2), kid2 = civ({ height: 0.74 }, 3), papa = civ({ height: 1.02, top: '#5a5a62', topStyle: 'coat' }, 4);
const queue = [5, 6, 7, 8].map(i => civ({ height: 0.94 + (i % 3) * 0.04 }, i));
[mom, ...queue.slice(1)].forEach((q, i) => q.handR.add(suitcase(['#6a4a3a', '#3a4a6a', '#8a3a3a', '#5a6a3a'][i], i % 2 ? 'bag' : 'case')));
const card = photoCard(); card.position.set(0, 0.02, 0.06); card.rotation.set(0, 0, 0); card.visible = false; off.handR.add(card);

const QP = { boy: [2.2, -0.6], mom: [1.3, 3.9], kid1: [0.7, 3.6], kid2: [0.6, 4.4], q0: [1.5, 2.8], q1: [1.5, 5.0], q2: [1.0, 6.1], q3: [1.3, 7.3] };
const MV = mover()
  .add(boy, 'boy', { from: QP.boy, to: [3.6, -5.0], T0: 15.0, T1: 17.6, mode: 'walk', endRy: 180 })
  .add(papa, 'papa', { from: [0.9, -13.0], to: [0.8, -4.0], T0: 7.0, T1: 10.6, mode: 'walk', endRy: 0 })
  .add(kid1, 'kid1', { from: QP.kid1, to: [0.45, -2.4], T0: 10.4, T1: 12.0, endRy: 180 })
  .add(kid2, 'kid2', { from: QP.kid2, to: [1.05, -2.35], T0: 10.7, T1: 12.4, endRy: 180 })
  .add(mom, 'mom', { from: QP.mom, to: [-0.2, -1.7], T0: 11.2, T1: 13.6, mode: 'walk', endRy: 160 })
  .add(elias, 'elias', { from: [0.4, -13.0], to: [3.4, -2.8], T0: 21.0, T1: 24.6, mode: 'walk', endRy: -60 })
  .add(mira, 'mira', { from: MIRA0, to: [-8.6, 0.6], T0: 44.0, T1: 45.2 })
  .add(mira, 'mira', { from: [-8.6, 0.6], to: [-11.8, -6.0], T0: 45.2, T1: 47.6, y0: 0, y1: -4.2, endRy: -90 })
  .add(mira, 'mira', { from: [-11.8, -6.0], to: [-20.3, -6.1], T0: 52.0, T1: 55.4, ph: 0.2 })
  .add(mira, 'mira', { from: [-20.3, -6.1], to: [-29.2, -6.0], T0: 55.4, T1: 58.6, ph: 0.2, endRy: -90 })
  .add(mira, 'mira', { from: [-29.2, -6.0], to: [-32.5, -6.3], T0: 62.4, T1: 64.6, ph: 0.3, endRy: -120 });
const SOLS = [[-2.4, -3.8, 0], [3.6, -0.3, -30], [-3.4, 1.0, 120]];
MV.add(sol[0], 's0', { from: [-2.4, -3.8], to: [-5.6, -1.4], T0: 40.0, T1: 42.6, mode: 'walk', endRy: -110 });
MV.add(sol[2], 's2', { from: [-3.4, 1.0], to: [-6.2, 0.6], T0: 40.6, T1: 43.4, mode: 'walk', endRy: -100 });

const set = river({
  mood: 'night',
  helis: [{ keys: [[0, 22, 16, -24], [20, 8, 15, -20], [40, -4, 16, -22], [52, -14, 14, -14], [58, -24, 13, -9], [62, -30, 14, -11], [70, -36, 16, -18], [80, -48, 17, -24]], light: 1, aim: 20 }],
  targets: { H_off: [2.2, D + 1.7, -2.5], H_boy: [2.2, D + 1.4, -0.6], H_papa: [0.8, D + 1.6, -4.0], H_kids: [0.8, D + 1.0, -2.5], H_elias: [3.4, D + 1.62, -2.8], H_mira: [-6.4, 0.65, 4.4], photo: [2.15, D + 2.2, -2.3], H_rail: [-3.6, D + 1.62, -6.0], slope: [-6, -0.5, -1.5], H_boat: [-32.0, -3.3, -14.4] },
  onUpdate(v, t) { MV.update(t); elias.blink(1); papa.blink(1); puffs(t, camPt(t)); card.visible = t > 26.4 && t < 33.5; },
});
const AV = { mira, off, bruder, boy, mom, kid1, kid2, s0: sol[0], s1: sol[1], s2: sol[2], ...Object.fromEntries(queue.map((q, i) => ['q' + i, q])) };
const puffs = breathPuffs(set.group, AV, (n, t) => n === 'mira' && t > 44 && t < 66 ? 1.1 : 2.6, (n, t) => true);

const S = story({
  set, lead: 0, tail: 0, shake: 0.8, vignette: 0.72, audioMood: 'tension',
  badge: { title: 'FOLGE 3', label: 'Flucht aus Aschental –', value: 'DIE BRÜCKE', until: 3.6 },
  speakers: { luca: { color: '#ffffff', voice: 'liam' }, mira: { color: '#ffd84a', voice: 'elli' }, elias: { color: '#ff9ad0', voice: 'harry', fx: 'far' }, off: { color: '#ff8a7a', voice: 'callum' } },
  pov: { phone: true, name: 'Luca', skin: 'light', top: '#3d6a8a' },
  paint: 1,
  infobar: t => `ASCHENTAL · ${t < 44 ? 'ALTE BRÜCKE' : 'FLUSSUFER'} · MO ${clock(23, 51, t)}`,
  phone: { name: 'Elias', color: '#8a2a2e', clock: '23:51', history: [{ me: false, text: 'Spatz. Sie hat dich Spatz genannt.' }, { me: true, text: 'Er liest mit.' }, { me: false, text: 'Dann schreib ich nicht, wo.' }, { me: false, text: 'Da, wo Papa uns Schwimmen beigebracht hat.' }] },
  povPath: t => run1(t) || run2(t),
  vars: { phone: 1 },
});
S.cast('mira', mira, { at: [...MIRA0, 45], pose: 'crouch', face: 'scared', look: 'H_off' });
set.group.add(at(car('#4a5a6a'), [-6.9, 0, 7.4], [0, 0.1, 0]), at(car('#7a3a3a', true), [-12.0, 0, 6.6], [0, Math.PI / 2 + 0.2, 0]));
S.cast('off', off, { at: [2.2, -2.5, 0], y: D, pose: 'stand', face: 'sus', look: 'H_boy' });
S.cast('boy', boy, { at: [...QP.boy, 180], y: D, pose: 'stand', face: 'scared', look: 'H_off' });
for (const [n, av] of [['mom', mom], ['kid1', kid1], ['kid2', kid2]]) S.cast(n, av, { at: [...QP[n], 180], pose: 'stand', face: 'worried', look: null });
queue.forEach((q, i) => S.cast('q' + i, q, { at: [...QP['q' + i], 180], pose: 'stand', face: 'worried', look: null }));
S.cast('papa', papa, { at: [0.9, -13.0, 0], y: D, pose: 'stand', face: 'smile', look: 'H_kids' });
sol.forEach((s, i) => S.cast('s' + i, s, { at: SOLS[i], y: i === 2 ? 0 : D, pose: { hipY: 0.83, aR: [40, 6, 0], eR: 30 }, face: 'angry', look: null }));
S.cast('elias', elias, { at: [0.4, -13.0, 0], y: D, pose: 'stand', face: 'smile', look: 'H_off', hide: true });
S.cast('bruder', bruder, { at: [-32.0, -14.2, 180], y: -4.85, pose: 'sitChair', face: 'neutral', look: [-32, -3.3, -30] });

const Z = sequencer(S, TM), { hold, say, phone, abs } = Z;
const mySteps = []; for (const [a, b, p] of [[44.1, 46.8, 0.32], [52.1, 58.4, 0.3], [62.7, 65.3, 0.3]]) for (let t = a; t < b - 0.1; t += p) mySteps.push(['step', +t.toFixed(3), 0.85]);
const HOLDUP = { hipY: 0.83, aR: [110, 10, 0], eR: 20 }, POINT = { hipY: 0.83, aR: [80, 30, 0], eR: 4 }, HUG = { hipY: 0.7, lean: 24, aL: [70, -20, 0], eL: 60, aR: [70, -20, 0], eR: 60 };

// 00:00–00:22 · from the bushes on the embankment: the checkpoint, the queue, a father coming back
hold(0.6, { look: 'H_off', zoom: 34, pov: C0, sfx: [['cityamb', 0, 0.8], ['heli_far', 0, 0.9], ['crowd', 0, 1.0], ['water', 0, 0.6], ...mySteps, ...MV.steps(camPt)], do: { mira: MV.keys('mira'), boy: MV.keys('boy'), papa: MV.keys('papa'), kid1: MV.keys('kid1'), kid2: MV.keys('kid2'), mom: MV.keys('mom'), elias: [...MV.keys('elias'), { hide: false, t: 20.8 }], s0: MV.keys('s0'), s2: MV.keys('s2') } });
say('off', 'Nächster.', { look: 'H_off', zoom: 26, camAt: -0.2 });
hold(5.0, { look: 'queue', zoom: 40, camDur: 0.5, push: 0.012 });
say('mira', 'Da vorne | lassen sie | Leute durch.', { look: 'mira', zoom: 44, camAt: -0.2, do: { mira: { look: 'pov', t: 0, dur: 0.3 } } });
hold(7.0, {});
say('luca', 'Nicht über die Brücke. | Zum Steg | darunter.', { look: 'water', zoom: 60, camAt: -0.1, do: { mira: { look: 'H_off', t: 1.4 } } });
hold(12.2, { look: 'H_papa', zoom: 30, camDur: 0.5, push: 0.015, do: { papa: [{ pose: { hipY: 0.83, aL: [20, 150, 0], eL: 30 }, t: abs(10.8), dur: 0.5 }] } });
say('off', 'Kapuze runter. | Name?', { look: 'H_boy', zoom: 26, camAt: -0.15, do: { off: { pose: POINT, t: 0.1, dur: 0.3 }, boy: { look: 'H_off', t: 0 } } });
hold(17.2, { look: 'H_kids', zoom: 22, camDur: 0.5, push: 0.02, sfx: [['heart', 1.2, 0.6], ['heart', 2.0, 0.65]], do: { off: { pose: 'stand', t: 0.6, dur: 0.4 }, papa: [{ pose: HUG, face: 'grin', t: 0, dur: 0.6 }], kid1: { look: 'H_papa', face: 'smile', t: 0 }, kid2: { look: 'H_papa', face: 'smile', t: 0 } } });
say('mira', 'Der Mann da. | Auch kein Atem.', { look: 'mira', zoom: 44, camAt: -0.2, do: { mira: { look: 'pov', face: 'scared', t: 0 } } });
hold(19.4, {});
say('luca', 'Die schicken | Kopien zurück. | Zu den Familien.', { look: 'H_papa', zoom: 26, camAt: -0.1 });
// 00:22–00:44 · Elias walks up to the man in the coat. A photo. "Er heißt Luca."
hold(26.2, { look: 'H_elias', zoom: 26, camDur: 0.5, push: 0.015, do: { elias: [{ look: 'H_off', t: abs(24.8) }, { pose: POINT, look: 'slope', t: abs(25.3), dur: 0.5 }], off: { look: 'H_elias', t: abs(24.6) } } });
say('off', 'Wir suchen | nur einen Jungen. | Er heißt Luca.', { look: 'H_off', zoom: 26, camAt: -0.2, do: { off: [{ look: 'queue', t: 0 }, { pose: HOLDUP, t: 0.2, dur: 0.5 }], elias: { pose: 'stand', look: 'slope', t: 0.4, dur: 0.5 } } });
hold(31.2, { look: 'photo', zoom: 17, camDur: 0.45, push: 0.01, sfx: [['sting', 0.1, 0.7]] });
say('mira', 'Luca, | die haben | dein Foto.', { look: 'mira', zoom: 42, camAt: -0.2, do: { off: { pose: 'stand', t: 1.8, dur: 0.6 } } });
hold(33.4, {});
say('mira', 'Warum | ausgerechnet dich?', { look: 'mira', zoom: 40 });
hold(35.3, {});
phone({ low: true, look: 'mira', zoom: 50, events: [{ in: 'Weil du vor zwei Wochen weg warst.', hold: 1.6 }, { in: 'Weißt du das nicht mehr?', alert: true, hold: 1.6 }] });
say('luca', 'Ich war | nie weg.', { look: 'mira', zoom: 40, camAt: -0.1 });
hold(42.0, { look: 'mira', zoom: 34, push: 0.02, sfx: [['heart', 0.4, 0.7], ['heart', 1.2, 0.75]], do: { mira: { face: 'worried', t: 0.2 } } });
hold(44.0, { look: 'slope', zoom: 52, camDur: 0.4, sfx: [['stop_crowd', 0.2]], do: { s0: { look: 'pov', t: 0 }, s2: { look: 'pov', t: 0.3 } } });
// 00:44–00:66 · down the embankment, along the river. Elias at the railing. The searchlight on the water.
hold(50.0, { look: 'mira', zoom: 80, pov: P1, povDur: 2.8, camDur: 0.4, sfx: [['pant', 0.2, 0.8]], do: { elias: [{ hide: true, t: abs(46.0) }, { at: [-3.5, -6.0, -90], y: D, pose: 'stand', face: 'creepy', look: 'pov', t: abs(46.2), dur: 0 }, { hide: false, t: abs(48.0) }] } });
say('elias', 'Spatz! | Du kommst | sowieso zurück.', { look: 'H_rail', zoom: 30, camAt: -0.3, camDur: 0.35, tag: 'BRÜCKE' });
hold(52.0, { look: 'H_rail', zoom: 24, push: 0.02 });
hold(59.4, { look: 'mira', zoom: 82, pov: PEND, povDur: 13.4, camDur: 0.45, sfx: [['pant_fast', 0.2, 0.9], ['heli', 4.2, 1.1]], do: { mira: [{ face: 'scared', t: 0 }, { pose: 'crouch', t: abs(58.8), dur: 0.3 }, { pose: 'stand', t: abs(62.3), dur: 0.3 }] } });
hold(62.6, { look: [-26, -1.5, -14], zoom: 70, camDur: 0.4, push: 0 });
hold(66.0, { look: 'mira', zoom: 74, camDur: 0.4 });
// 00:66–01:20 · the jetty in the dark. In the boat at its end: someone with a hood. A breath.
hold(68.0, { look: 'jetty', zoom: 48, camDur: 0.45, do: { mira: { look: 'jetty', t: 0 } } });
say('mira', 'Da! | Der Steg!', { look: 'jetty', zoom: 40, camAt: 0 });
hold(74.0, { look: 'H_boat', zoom: 26, camDur: 0.5, push: 0.025, sfx: [['heart', 1.0, 0.7], ['heart', 1.8, 0.75], ['heart', 2.6, 0.8]] });
hold(79.6, { look: 'H_boat', zoom: 16, camDur: 0.5, push: 0.02, sfx: [['sting', 3.4, 0.8]], do: { bruder: [{ look: 'pov', t: 3.0, dur: 1.4 }] } });
Z.black(79.6, 80.0);
S.start();
