// FLUCHT AUS ASCHENTAL · Folge 2 – "Der Hof" (80 s). Into a courtyard at dusk, up into an empty flat. Three knocks.
// The voice behind the door fails the question, then knows the answer the moment Elias texts it: it reads along.
// Soldiers floor by floor; out of the window onto the roofs. Across the courtyard, in the searchlight: Elias, waving.
import { story } from './core.js';
import { CAST } from './cast.js';
import { courtyard, hideout } from './fluchtsets.js';
import { towards, loadTimings, sequencer, mover, runPath, breathPuffs } from './lib.js';

const clock = (h, m, t) => { const mm = m + Math.floor(t / 60); return `${String(h + Math.floor(mm / 60)).padStart(2, '0')}:${String(mm % 60).padStart(2, '0')}`; };
const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

// courtyard: run in through the archway to the stairwell door
const RUNH = [[0.0, 0.0, 1.6, 15.5], [2.0, 0.4, 1.6, 7.5], [4.4, 2.2, 1.6, 0.0], [6.6, 2.8, 1.55, -4.6]];
// the flat: hallway by the door, then to the window and out onto the roof
const F0 = [-0.45, 1.5, -0.4], F1 = [-0.9, 1.45, 1.3];
const RUNW = [[55.2, ...F1], [56.6, -2.6, 1.45, 1.6], [58.0, -3.5, 1.35, 1.6], [59.4, -5.0, 1.45, 1.4], [61.0, -6.4, 1.45, 0.4]];
const ROOF = [-6.4, 1.45, 0.4], ROOFLOW = [-6.7, 0.95, -1.8];
const runH = runPath(RUNH, 0.06), runW = runPath(RUNW, 0.05, 0.34);
const camPt = t => runH(t) || runW(t) || (t < 7.6 ? RUNH[3].slice(1) : t < 55.2 ? (t < 50 ? F0 : F1) : t < 61 ? F1 : t < 62.5 ? ROOF : ROOFLOW);

const miraH = CAST.mira(), mira = CAST.mira(), elias = CAST.elias({ hood: true, hair: 'short' });
const MH = mover().add(miraH, 'miraH', { from: [-0.6, 13.5], to: [0.2, 6.0], T0: 0.0, T1: 1.9, ph: 0.1 })
  .add(miraH, 'miraH', { from: [0.2, 6.0], to: [2.6, -5.9], T0: 1.9, T1: 5.0, ph: 0.1, endRy: 180 });
const MV = mover()
  .add(mira, 'mira', { from: [0.25, -2.35], to: [0.55, -1.2], T0: 21.0, T1: 21.9, mode: 'walk', endRy: 200, keepRy: false })
  .add(mira, 'mira', { from: [0.55, -1.2], to: [-1.6, 1.0], T0: 53.6, T1: 55.0, ph: 0.2 })
  .add(mira, 'mira', { from: [-1.6, 1.0], to: [-2.9, 1.6], T0: 55.0, T1: 55.7, mode: 'walk' })
  .add(mira, 'mira', { from: [-2.9, 1.6], to: [-4.3, 1.6], T0: 55.8, T1: 56.6, mode: 'walk', arc: 0.75 })
  .add(mira, 'mira', { from: [-4.3, 1.6], to: [-7.1, -1.9], T0: 56.7, T1: 58.6, ph: 0.3 })
  .add(mira, 'mira', { from: [-7.1, -1.9], to: [-7.6, -2.4], T0: 61.2, T1: 61.8, mode: 'walk', endRy: -100 });
const MVE = mover().add(elias, 'elias', { from: [-20.4, -1.0], to: [-20.6, -1.0], T0: 79.0, T1: 79.4, mode: 'still', endRy: 90 });

const hof = courtyard({
  helis: [{ keys: [[0, 30, 26, -30], [4, 2, 18, -2], [8, -24, 22, 22]], light: 1, aim: 28 }],
  targets: { H_miraDoor: [2.6, 1.4, -5.9] },
  onUpdate(v, t) { MH.update(t); },
});
const flat = hideout({
  helis: [{ keys: [[0, -10, 24, -34], [16, -12, 20, -8], [30, -16, 21, 12], [46, -12, 19, 22], [60, -14, 18, 2], [66, -18, 16, -4], [72, -12, 17, 4], [80, -8, 20, 24]], light: t => t > 58 ? 1 : 0.7, aim: 26 }],
  targets: { H_mira: [0.55, 1.35, -1.2], H_miraW: [-1.6, 1.35, 1.0], H_elias: [-20.4, 2.85, -1.0], chimney: [-7.6, 0.7, -2.4] },
  onUpdate(v, t) { MV.update(t); MVE.update(t); elias.blink(1); puffs(t, camPt(t)); },
});
const puffs = breathPuffs(flat.group, { mira }, (n, t) => t > 53 ? 1.2 : 2.4, (n, t) => t > 58);

const S = story({
  set: hof, lead: 0, tail: 0, shake: 0.85, vignette: 0.7, audioMood: 'tension',
  badge: { title: 'FOLGE 2', label: 'Flucht aus Aschental –', value: 'DER HOF', until: 3.6 },
  speakers: { luca: { color: '#ffffff', voice: 'liam' }, mira: { color: '#ffd84a', voice: 'elli' }, elias: { color: '#ff9ad0', voice: 'harry', fx: 'door' }, offizier: { color: '#ff8a7a', voice: 'callum', fx: 'far' } },
  pov: { phone: true, name: 'Luca', skin: 'light', top: '#3d6a8a' },
  paint: 1,
  infobar: t => `ASCHENTAL · ${t < 7.6 ? 'HINTERHOF' : t < 55.2 ? 'WOHNUNG 4. OG' : 'DACH'} · MO ${clock(19, 12, t)}`,
  phone: { name: 'Elias', color: '#8a2a2e', clock: '19:12', history: [{ me: false, text: 'Bin raus. Alte Brücke.' }, { me: false, text: 'Komm allein.' }, { me: true, text: 'Mira kommt mit.' }, { me: false, text: 'Ich bin schon über der Brücke.' }, { me: false, text: 'Wer steht da bei dir?' }] },
  povPath: t => runH(t) || runW(t),
  vars: { phone: 1, hofDoor: 0, feet: 0, torch: 0, window: 0, sweep: 0, gapLight: 1 },
});
S.cast('miraH', miraH, { set: hof, at: [-0.6, 13.5, 180], pose: 'stand', face: 'scared', look: null });
S.cast('mira', mira, { set: flat, at: [0.25, -2.35, 200], pose: { hipY: 0.83, lean: -6, aL: [10, 20, 0], eL: 20, aR: [10, 20, 0], eR: 20 }, face: 'scared', look: 'pov' });
S.cast('elias', elias, { set: flat, at: [-20.4, -1.0, 90], y: 1.25, pose: 'stand', face: 'smile', look: 'pov', hide: true });

const Z = sequencer(S, TM), { hold, say, phone, abs } = Z;
const mySteps = []; for (const [a, b, p] of [[0.05, 6.5, 0.3], [55.3, 61.0, 0.34]]) for (let t = a; t < b - 0.1; t += p) mySteps.push(['step', +t.toFixed(3), 0.9]);
const LISTEN = { hipY: 0.83, lean: 10, head: [10, 0, 14], aL: [40, -10, 0], eL: 60 }, CROUCH = 'crouch';

// 00:00–00:07 · the courtyard at dusk, a helicopter's searchlight crossing it; Mira holds the stairwell door
hold(1.9, { look: 'miraH', zoom: 80, sfx: [['cityamb', 0], ['heli_far', 0, 0.8], ['heli', 0.0, 1.0], ['pant', 0.3, 0.8], ...mySteps, ...MH.steps(camPt)], do: { miraH: MH.keys('miraH'), mira: MV.keys('mira'), elias: MVE.keys('elias') } });
say('mira', 'Hier rein! | Schnell!', { look: 'H_miraDoor', zoom: 64, camAt: -0.1, vars: { hofDoor: [1, 0.4, 0.6] } });
hold(7.6, { look: 'door', zoom: 70, camDur: 0.45, sfx: [['creak', 1.2, 0.6]] });
// 00:07–00:55 · inside the flat, by the front door. Light under it. Steps on the stairs.
hold(9.4, { set: flat, look: 'door', zoom: 62, pov: F0, sfx: [['slam', 0.05, 0.35], ['pant_soft', 0.3, 0.9], ['stop_cityamb', 0], ['cityamb', 0.05, 0.6]], vars: { sweep: [1, 0.5, 0.6] } });
hold(11.0, { look: 'mira', zoom: 48, camDur: 0.4, vars: { sweep: [0, 0.6, 0.1] } });
say('mira', 'Psst. | Hörst du das?', { look: 'mira', zoom: 50, do: { mira: [{ pose: LISTEN, t: 0.1, dur: 0.4 }, { look: 'door', t: 0.6 }] } });
hold(14.2, { look: 'gap', zoom: 50, push: 0.02, sfx: [['stepw', 0.2, 0.5], ['stepw', 0.75, 0.55], ['stepw', 1.3, 0.6], ['stepw', 1.85, 0.6]], vars: { feet: [1, 0.6, 1.5] } });
phone({ low: true, look: 'door', zoom: 54, events: [{ in: 'Versteckt euch.', hold: 1.3 }, { in: 'Die gehen von Haus zu Haus.', hold: 1.5 }, { in: 'Er klopft dreimal.', hold: 1.3 }, { in: 'Mach nicht auf.', alert: true, hold: 1.6 }] });
hold(22.0, { look: 'door', zoom: 52, camDur: 0.4, sfx: [['knock3', 0.25, 1.0]], do: { mira: [{ pose: 'stand', look: 'door', face: 'scared', t: 0.4, dur: 0.4 }] } });
say('elias', 'Luca? | Ich bin es. | Mach auf.', { look: 'peep', zoom: 40, push: 0.02, tag: 'VOR DER TÜR' });
hold(24.4, {});
say('luca', 'Wie hat Mama | mich immer | genannt?', { look: 'door', zoom: 46, camAt: 0 });
hold(28.0, { look: 'peep', zoom: 30, push: 0.025, sfx: [['heart', 0.4, 0.7], ['heart', 1.3, 0.75], ['heart', 2.2, 0.8]] });
say('elias', '…Luca.', { tag: 'VOR DER TÜR', look: 'peep', zoom: 26 });
hold(28.8, {});
say('mira', 'Falsch.', { look: 'mira', zoom: 48, camAt: -0.15, do: { mira: { look: 'pov', face: 'worried', t: 0, dur: 0.3 } } });
hold(30.0, {});
phone({ low: true, look: 'door', zoom: 56, events: [{ in: 'Spatz. Sie hat dich Spatz genannt.', hold: 2.2 }] });
hold(34.6, { look: 'door', zoom: 40, push: 0.03, sfx: [['heart', 0.3, 0.8], ['heart', 1.1, 0.85]] });
say('elias', 'Spatz. | Mach auf, | Spatz.', { tag: 'VOR DER TÜR', look: 'peep', zoom: 30, sfx: [['sting', 0, 0.75]] });
hold(36.4, {});
say('mira', 'Woher | weiß er das?', { look: 'mira', zoom: 48, camAt: -0.15, do: { mira: { face: 'shock', look: 'pov', t: 0 } } });
hold(37.6, {});
say('luca', 'Er liest mit. | Er liest | alles mit.', { look: 'mira', zoom: 50 });
hold(40.2, {});
phone({ events: [{ type: 'Er liest mit.', hold: 0.9 }, { in: 'Dann schreib ich nicht, wo.', hold: 1.8 }, { in: 'Da, wo Papa uns Schwimmen beigebracht hat.', hold: 2.4 }] });
hold(49.0, { look: 'gap', zoom: 46, camDur: 0.4, push: 0.015, sfx: [['stepw', 0.1, 0.8], ['stepw', 0.5, 0.85], ['stepw', 0.9, 0.9], ['stepw', 1.3, 0.85], ['slam_far', 1.0, 0.7]], vars: { feet: [0, 0.3, 0.1], torch: [1, 0.4, 0.3] } });
say('offizier', 'Jedes Stockwerk. | Jede Tür.', { tag: 'TREPPENHAUS', look: 'door', zoom: 50, sfx: [['slam_far', 1.6, 0.8]] });
hold(52.8, { look: 'window', zoom: 56, camDur: 0.4, pov: F1, povDur: 1.2, do: { mira: { look: 'window', t: 0.2 } } });
say('mira', 'Das Fenster! | Über das Dach!', { look: 'mira', zoom: 56, camAt: 0, vars: { window: [1, 0.8, 1.6] }, sfx: [['creak', 1.7, 0.5]] });
hold(55.2, {});
// 00:55–01:20 · out over the sill onto the roof, down behind a chimney. Across the courtyard, in the searchlight: Elias.
hold(61.0, { look: 'mira', zoom: 82, pov: ROOF, povDur: 5.8, camDur: 0.5, sfx: [['pant', 0.3, 0.8], ['heli', 0.6, 1.0], ['stop_cityamb', 0], ['cityamb', 0.05, 1.0]] });
hold(64.6, { look: 'chimney', zoom: 60, pov: ROOFLOW, povDur: 1.2, camDur: 0.4, do: { mira: { pose: CROUCH, look: 'pov', t: abs(61.8), dur: 0.4 } } });
say('luca', 'Der alte Steg. | Am Fluss.', { look: 'mira', zoom: 46, camAt: -0.1 });
hold(68.4, { look: 'across', zoom: 52, camDur: 0.45, do: { mira: { look: 'H_elias', t: 0.2 } } });
hold(71.2, { look: 'H_elias', zoom: 15, camDur: 0.35, push: 0.02, sfx: [['sting', 0.05, 0.7]], do: { elias: { hide: false, t: abs(67.6) } } });
say('elias', 'Bis gleich, | Spatz.', { look: 'H_elias', zoom: 14, tag: 'GEGENÜBER', fx: 'far' });
hold(76.6, { look: 'H_elias', zoom: 11, push: 0.025, sfx: [['heart', 0.6, 0.8], ['heart', 1.4, 0.85]], do: { elias: [{ pose: { hipY: 0.83, aR: [20, 150, 0], eR: 30 }, t: 0.4, dur: 0.6 }, { pose: { hipY: 0.83, aR: [20, 120, 0], eR: 30 }, t: 1.2, dur: 0.6 }, { pose: { hipY: 0.83, aR: [20, 150, 0], eR: 30 }, t: 2.0, dur: 0.6 }, { pose: 'stand', t: 3.6, dur: 0.8 }, { face: 'creepy', t: 1.0 }] } });
hold(79.6, { look: 'across', zoom: 30, camDur: 0.5, do: { elias: { hide: true, t: abs(78.4) } } });
Z.black(79.6, 80.0);
S.start();
