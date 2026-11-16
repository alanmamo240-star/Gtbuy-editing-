// FLUCHT AUS ASCHENTAL · Folge 1 – "Die Kolonne" (80 s). The main street on the morning the convoys come. Mira pulls you
// along, Elias texts from the bridge, you run into the side street, and Elias is standing behind you. He has no breath.
import { story } from './core.js';
import { CAST } from './cast.js';
import { makeToon } from './toon.js';
import { street, suitcase } from './fluchtsets.js';
import { towards, loadTimings, sequencer, mover, runPath, breathPuffs } from './lib.js';
import { THREE, rad } from './util.js';

const clock = (h, m, t) => { const mm = m + Math.floor(t / 60); return `${String(h + Math.floor(mm / 60)).padStart(2, '0')}:${String(mm % 60).padStart(2, '0')}`; };
const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const C0 = [-4.6, 1.55, 2.0], C1 = [22.0, 1.55, -18.6], C2 = [38.0, 1.55, -18.4];
const RUN1 = [[33.0, ...C0], [34.8, -1.5, 1.6, -6.0], [36.8, 5.0, 1.6, -12.6], [38.6, 11.0, 1.6, -17.8], [40.2, 18.0, 1.6, -18.6], [41.0, ...C1]];
const RUN2 = [[63.1, ...C1], [64.0, 25.0, 1.6, -18.5], [66.2, 33.0, 1.6, -18.5], [67.8, ...C2]];
const run1 = runPath(RUN1, 0.06), run2 = runPath(RUN2, 0.07, 0.27);
const camPt = t => run1(t) || run2(t) || (t < 33 ? C0 : t < 63 ? C1 : C2);

// people
const mira = CAST.mira(), elias = CAST.elias({ hood: true, hair: 'short' }), soldiers = [0, 1, 2].map(i => CAST.soldat({ seed: 37 + i, skin: ['light', 'tan', 'fair'][i], height: [1.0, 1.04, 0.97][i] }));
const CIVC = [['#6a5a4a', '#3a3a44'], ['#4a5a7a', '#2a2a30'], ['#8a6a5a', '#3a3030'], ['#5a6a5a', '#2a2a2a'], ['#7a4a4a', '#30303a'], ['#5a5a6a', '#2a2a34'], ['#8a7a5a', '#3a3a3a'], ['#4a6a7a', '#2a3030']];
const civs = CIVC.map(([top, bot], i) => { const av = makeToon({ real: true, skin: ['light', 'tan', 'fair', 'brown', 'light', 'deep', 'pale', 'tan'][i], height: i === 1 ? 0.72 : i === 5 ? 0.78 : 0.95 + (i % 3) * 0.04, hair: ['short', 'bob', 'bun', 'buzz', 'long', 'curly', 'beanie', 'ponytail'][i], hairColor: ['#3a2a20', '#6a4024', '#2a1a14', '#1a1210', '#8a5a2a', '#1a1210', '#4a4a50', '#5a3a22'][i], top, topStyle: i % 3 === 0 ? 'coat' : 'jacket', bottom: bot, shoe: '#2a2020', seed: 50 + i }); av.handR.add(at3(suitcase(['#6a4a3a', '#3a4a6a', '#8a3a3a', '#4a4a4a', '#5a6a3a', '#7a5a2a', '#3a3a5a', '#6a3a5a'][i], i % 2 ? 'bag' : 'case'), [0, -0.05, 0])); return av; });
function at3(o, p) { o.position.set(...p); return o; }
const CIVP = [[[-5.3, -30], [-5.5, 12], 0, 14, 'walk'], [[-5.9, -28.6], [-6.0, 12], 0.4, 14.4, 'walk'], [[5.4, -40], [5.2, 13], 0, 16, 'walk'], [[6.0, -36], [6.0, 14], 2.5, 17.5, 'walk'],
  [[-6.1, -52], [-6.0, 10], 7.5, 26, 'walk'], [[4.8, -48], [5.0, 14], 11.5, 24.5, 'run'], [[-0.8, -46], [-1.2, 12], 17.5, 31, 'run'], [[1.2, -54], [0.8, 14], 19.0, 34, 'run']];
const MV = mover();
CIVP.forEach(([a, b, T0, T1, mode], i) => MV.add(civs[i], 'c' + i, { from: a, to: b, T0, T1, mode, ph: i * 0.31 }));
MV.add(mira, 'mira', { from: [-5.4, 7.0], to: [-5.6, 0.5], T0: 4.6, T1: 5.9, endRy: towards([-5.6, 0.5], [C0[0], C0[2]]) })
  .add(mira, 'mira', { from: [-5.6, 0.5], to: [-2.6, -5.4], T0: 33.0, T1: 34.9, ph: 0.2 })
  .add(mira, 'mira', { from: [-2.6, -5.4], to: [4.4, -11.6], T0: 34.9, T1: 36.9, ph: 0.2 })
  .add(mira, 'mira', { from: [4.4, -11.6], to: [11.6, -17.2], T0: 36.9, T1: 38.6, ph: 0.2 })
  .add(mira, 'mira', { from: [11.6, -17.2], to: [19.8, -19.9], T0: 38.6, T1: 40.6, ph: 0.2, endRy: -90 })
  .add(mira, 'mira', { from: [19.8, -19.9], to: [31.0, -17.9], T0: 63.0, T1: 65.6, ph: 0.4 })
  .add(mira, 'mira', { from: [31.0, -17.9], to: [40.2, -16.6], T0: 65.6, T1: 67.9, ph: 0.4, endRy: 100 });
const SOLP = [[[1.0, -28.6], [-5.8, -26.2]], [[2.2, -28.4], [-5.8, -31.0]], [[1.6, -28.9], [5.8, -27.0]]];
SOLP.forEach(([a, b], i) => MV.add(soldiers[i], 's' + i, { from: a, to: b, T0: 17.6 + i * 0.4, T1: 20.6 + i * 0.5, mode: 'walk', ph: i * 0.4 }));
MV.add(elias, 'elias', { from: [12.6, -18.2], to: [15.2, -18.5], T0: 47.0, T1: 49.6, mode: 'walk', endRy: 90 })
  .add(elias, 'elias', { from: [15.2, -18.5], to: [16.8, -18.6], T0: 61.2, T1: 62.4, mode: 'walk', endRy: 90 });

const H_E = [12.6, 1.6, -18.2], H_E2 = [15.2, 1.6, -18.5], H_EEND = [43.2, 1.6, -18.5];
const set = street({
  helis: [
    { keys: [[0, -8, 24, -72], [4.3, 0, 16, -22], [7.5, 3, 15, 8], [11, 8, 19, 48]] },
    { keys: [[0, -18, 34, -96], [20, 2, 30, -76], [40, 16, 33, -88], [60, -6, 28, -66], [80, 12, 31, -82]] },
    { keys: [[66, -30, 19, -46], [72, 22, 15, -20], [78, 70, 19, 4]] },
  ],
  convoy: [
    { kind: 'tank', x: 1.7, keys: [[0, 3], [9.0, -40], [15, -76]], ry: 180 },
    { kind: 'apc', x: 1.7, keys: [[0, 14], [11.0, -36], [17, -66]], ry: 180 },
    { kind: 'truck', x: 1.7, keys: [[0, 30], [16.5, -32]], ry: 180 },
    { kind: 'truck', x: 1.7, keys: [[0, 46], [4.0, 46], [19, -20], [26, -62], [30, -90]], ry: 180 },
  ],
  targets: { H_mira0: [-5.6, 1.45, 0.5], soldiers: [0, 1.4, -28], truck: [1.7, 1.8, -30], cross: [5, 1.4, -14], H_elias: H_E, H_elias2: H_E2, H_end: H_EEND, sideEnd: [44, 1.5, -18.5] },
  onUpdate(v, t) { MV.update(t); elias.blink(1); puffs(t, camPt(t)); },
});
const AVS = { mira, ...Object.fromEntries(civs.map((c, i) => ['c' + i, c])), ...Object.fromEntries(soldiers.map((s, i) => ['s' + i, s])) };
const puffs = breathPuffs(set.group, AVS, (n, t) => n === 'mira' ? (t > 33 && t < 42 || t > 63 && t < 70 ? 1.1 : 2.2) : 2.8, (n, t) => true);

const S = story({
  set, lead: 0, tail: 0, shake: 0.9, vignette: 0.6, audioMood: 'tension',
  badge: { title: 'FOLGE 1', label: 'Flucht aus Aschental –', value: 'DIE KOLONNE', until: 3.6 },
  speakers: { luca: { color: '#ffffff', voice: 'liam' }, mira: { color: '#ffd84a', voice: 'elli' }, elias: { color: '#ff9ad0', voice: 'harry' }, soldat: { color: '#ff8a7a', voice: 'callum', fx: 'radio' } },
  pov: { phone: true, name: 'Luca', skin: 'light', top: '#3d6a8a' },
  paint: 1,
  infobar: t => `ASCHENTAL · ${t < 33 ? 'HAUPTSTRASSE' : 'LINDENGASSE'} · MO ${clock(7, 42, t)}`,
  phone: { name: 'Elias', color: '#8a2a2e', clock: '07:42', history: [{ me: false, text: 'Pass auf Mama auf.' }, { me: true, text: 'Wo bist du??' }, { me: true, text: 'Elias???' }] },
  povPath: t => run1(t) || run2(t),
  vars: { phone: 1 },
});
S.cast('mira', mira, { at: [-5.4, 7.0, 180], pose: 'stand', face: 'scared', look: 'pov' });
civs.forEach((c, i) => S.cast('c' + i, c, { at: [...CIVP[i][0], 0], pose: 'stand', face: i % 2 ? 'scared' : 'worried', look: null }));
soldiers.forEach((s, i) => S.cast('s' + i, s, { at: [...SOLP[i][0], 0], pose: 'stand', face: 'angry', hide: true }));
S.cast('elias', elias, { at: [12.6, -18.2, 90], pose: 'stand', face: 'smile', look: 'pov', hide: true });
S.target('H_mira', [19.8, 1.45, -19.9]);

const Z = sequencer(S, TM), { hold, say, phone, abs } = Z;
const keys = n => MV.keys(n);
const SIGN = { hipY: 0.83, aR: [70, 20, 0], eR: 30 }, GRAB = { hipY: 0.83, lean: 8, aR: [70, -6, 0], eR: 20, aL: [20, 10, 0], eL: 30 }, REACH = { hipY: 0.83, lean: 6, aR: [62, 4, 0], eR: 10 };
const steps = MV.steps(camPt), mySteps = [];
for (const [a, b, p] of [[33.15, 41.0, 0.3], [63.2, 67.8, 0.27]]) for (let t = a; t < b - 0.1; t += p) mySteps.push(['step', +t.toFixed(3), 1.0]);

// 00:00–00:15 · the convoy rolls past, a helicopter low over the roofs, people with suitcases. Mira pulls you along.
hold(2.6, { look: [1.0, 1.6, -8], zoom: 74, push: 0.012, sfx: [['cityamb', 0], ['heli_far', 0], ['convoy', 0], ['heli', 1.3, 0.9], ...steps, ...mySteps],
  do: { ...Object.fromEntries(civs.map((c, i) => ['c' + i, keys('c' + i)])), mira: keys('mira'), elias: keys('elias'), ...Object.fromEntries(soldiers.map((s, i) => ['s' + i, [...keys('s' + i), { hide: false, t: 17.4 + i * 0.3 }]])) } });
hold(6.0, { look: [0, 12, -24], zoom: 84, camDur: 0.6 });
say('mira', 'Luca! | Nicht stehen bleiben!', { look: 'mira', zoom: 40, camAt: -0.3, do: { mira: [{ pose: GRAB, t: 0.1, dur: 0.3 }, { face: 'scared', t: 0 }] } });
hold(8.4, {});
say('mira', 'Die holen | alle Jungs | aus den Häusern.', { do: { mira: [{ pose: 'stand', t: 0.2, dur: 0.4 }, { look: 'soldiers', t: 0.9, dur: 0.4 }, { look: 'pov', t: 1.5 }] } });
hold(10.6, { look: [2, 1.6, -22], zoom: 52, camDur: 0.4 });
say('luca', 'Ohne Elias | geh ich nicht.', { look: 'mira', zoom: 44, camAt: -0.2 });
hold(12.3, {});
say('mira', 'Elias ist weg, | Luca. | Seit gestern.', { do: { mira: [{ face: 'sad', t: 0 }, { pose: SIGN, t: 0.4, dur: 0.3 }, { pose: 'stand', t: 2.2, dur: 0.4 }] } });
hold(15.4, {});
phone({ events: [{ in: 'Bin raus. Alte Brücke.', hold: 1.6 }, { in: 'Komm allein.', hold: 1.4 }, { type: 'Mira kommt mit.', hold: 1.0 }], do: { mira: { look: [C0[0], 1.0, C0[2] - 0.3], t: 0.3 } } });
say('luca', 'Er lebt. | Er ist | an der Brücke.', { look: 'mira', zoom: 46, camAt: -0.15, do: { mira: [{ look: 'pov', t: 0, dur: 0.3 }, { face: 'worried', t: 0.4 }] } });
hold(25.4, { look: 'truck', zoom: 36, camDur: 0.45, push: 0.018 });
say('soldat', 'Alle Jungen | ab vierzehn | zum Wagen!', { tag: 'MEGAFON', look: 'soldiers', zoom: 24, camAt: -0.2 });
hold(30.6, { look: [-3, 1.4, -24], zoom: 56, camDur: 0.4, do: { mira: [{ look: 'soldiers', t: 0, dur: 0.3 }, { face: 'scared', t: 0.2 }] } });
say('luca', 'Weg hier. | Durch die Seitenstraße.', { look: 'cross', zoom: 60, camAt: -0.15, do: { mira: { look: 'cross', t: 0.3, dur: 0.3 } } });
hold(33.0, {});
// 00:33–00:41 · across the street and into the side street, running behind Mira
hold(41.0, { look: 'mira', zoom: 82, pov: C1, povDur: 8.0, camDur: 0.5, sfx: [['pant', 0.4, 0.9]], do: { mira: { face: 'scared', t: 0 }, elias: { hide: false, t: abs(40.0) } } });
// 00:41–00:63 · "Luca!" from behind. Elias at the burnt car, hood up, smiling. He has no breath.
say('elias', 'Luca!', { look: 'H_elias', zoom: 46, camAt: 0.05, camDur: 0.32, do: { mira: [{ look: 'H_elias', t: 0.15, dur: 0.25 }, { face: 'shock', t: 0.2 }] } });
hold(43.0, { look: 'elias', zoom: 30, push: 0.02, sfx: [['sting', 0.05, 0.6]] });
say('luca', 'Elias?! | Du bist doch | an der Brücke.', { look: 'elias', zoom: 34, camAt: -0.1 });
hold(45.3, {});
say('elias', 'Die Brücke | ist zu. | Komm mit mir.', { look: 'elias', zoom: 30, do: { elias: [{ face: 'smile', t: 0 }] } });
hold(47.1, {});
say('luca', 'Wo warst du | die ganze Nacht?', { look: 'H_elias2', zoom: 36, camAt: 0, push: 0.01 });
hold(48.5, {});
say('elias', 'Hier. | Ich hab | auf dich gewartet.', { look: 'elias', zoom: 26, do: { elias: [{ face: 'grin', t: 0.6 }] } });
hold(51.8, { look: 'mira', zoom: 26, camDur: 0.4, push: 0.012, do: { mira: [{ look: 'pov', face: 'worried', t: 0, dur: 0.35 }] } });
hold(53.5, { look: 'elias', zoom: 20, camDur: 0.4, push: 0.018, sfx: [['heart', 0.1, 0.7], ['heart', 0.95, 0.75]], do: { elias: { face: 'smile', t: 0 } } });
say('mira', 'Luca. | Sein Atem. | Er hat keinen.', { look: 'mira', zoom: 36, camAt: -0.15, do: { mira: { look: 'pov', t: 0.2, dur: 0.4 } } });
hold(56.8, {});
phone({ low: true, look: 'elias', zoom: 56, events: [{ in: 'Ich bin schon über der Brücke.', hold: 1.6 }, { in: 'Wer steht da bei dir?', hold: 1.3 }, { in: 'Das bin nicht ich.', alert: true, hold: 1.7 }], do: { elias: [{ face: 'neutral', t: 1.0 }] } });
say('elias', 'Gib mir | dein Handy, | Luca.', { look: 'elias', zoom: 28, camAt: -0.2, do: { elias: [{ pose: REACH, t: -0.2, dur: 0.6 }, { face: 'creepy', t: 0.3 }] } });
hold(62.6, {});
say('luca', 'Lauf!', { look: 'mira', zoom: 50, camAt: 0, do: { mira: [{ look: 'sideEnd', t: 0.1 }] } });
// 00:63–00:80 · down the side street. At its end, already waiting: Elias.
hold(67.8, { look: [44, 1.4, -18.5], zoom: 84, pov: C2, povDur: 4.7, camDur: 0.45, sfx: [['pant_fast', 0.2, 0.9]], do: { elias: [{ hide: true, t: abs(63.4) }, { at: [43.2, -18.5, -90], pose: 'stand', face: 'smile', t: abs(66.8), dur: 0 }, { hide: false, t: abs(68.9) }] } });
hold(70.4, { look: 'H_end', zoom: 46, camDur: 0.35, sfx: [['heli', 0.1, 1.1]], do: { mira: [{ look: 'H_end', face: 'scared', t: abs(68.0) }] } });
say('elias', 'Du kannst | nicht weglaufen, | Luca.', { look: 'H_end', zoom: 30, camAt: -0.35, camDur: 0.3, push: 0.02, sfx: [['sting', -0.3, 0.8]] });
hold(76.0, { look: 'H_end', zoom: 20, push: 0.03, sfx: [['heart', 1.0, 0.8], ['heart', 1.8, 0.85], ['heart', 2.5, 0.9]], do: { elias: [{ face: 'creepy', t: 0.6 }, { pose: { hipY: 0.83, head: [0, 0, 14] }, t: 1.2, dur: 1.6 }] } });
Z.black(79.6, 80.0);
S.start();
