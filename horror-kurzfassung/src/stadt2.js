// DIE STADT HINTER DER SPERRE · Folge 2 – "Der Austausch" (30 s). Out the back door, the van at the end of the street, down into a cellar.
import { story } from './core.js';
import { CAST } from './cast.js';
import { alley } from './stadtsets.js';
import { towards, loadTimings, sequencer, mover } from './lib.js';
import { THREE, clamp, lerp, smooth, rad } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const A1 = [-3.2, 1.45, 1.2], A2 = [-0.6, 1.5, 1.6], A3 = [-1.2, 1.4, 0.9], A4 = [-6.8, 1.4, 1.0], R1 = [-8.0, 1.75, 0.35], M1 = [-13.0, 1.35, 0.6], L1 = [-10.5, 1.5, -1.2], N1 = [-11.8, 1.4, 0.9], D1 = [-9.5, -1.0, 7.4];
const ben = CAST.ben(), nina = CAST.nina(), max = CAST.max(), dBen = CAST.ben(), dNina = CAST.nina(), dMax = CAST.max(), nina2 = CAST.nina();
const STOP = { max: [-11.3, -0.3], nina: [-11.0, 1.15], ben: [-10.7, -1.15] }, BACK = { max: [-10.75, -0.25], nina: [-10.45, 1.2], ben: [-10.15, -1.1] };
const DUP = { ben: [-17.5, -0.8], nina: [-17.8, 0.4], max: [-17.4, 1.4] };
const MV = mover()
  .add(max, 'max', { from: [0, -1.6], to: [-1.6, -0.2], T0: 0.3, T1: 1.0, endRy: -60 })
  .add(nina, 'nina', { from: [0, -1.6], to: [-1.9, 0.6], T0: 0.6, T1: 1.35, endRy: -70 })
  .add(ben, 'ben', { from: [0, -1.6], to: [2.35, -1.3], T0: 0.95, T1: 1.9, endRy: -90 })
  .add(ben, 'ben', { from: [2.35, -1.3], to: [0.95, -1.3], T0: 2.5, T1: 4.4, mode: 'walk', endRy: -90, keepRy: true })
  .add(ben, 'ben', { from: [0.95, -1.3], to: STOP.ben, T0: 6.35, T1: 10.5, endRy: -90, ph: 0.2 })
  .add(max, 'max', { from: [-1.6, -0.2], to: STOP.max, T0: 6.45, T1: 10.25, endRy: -90, ph: 0.45 })
  .add(nina, 'nina', { from: [-1.9, 0.6], to: STOP.nina, T0: 6.55, T1: 10.4, endRy: -90, ph: 0.7 });
for (const n of ['max', 'nina', 'ben']) MV.add({ max, nina, ben }[n], n, { from: STOP[n], to: BACK[n], T0: 16.3 + (n === 'nina' ? 0.1 : 0), T1: 17.0, mode: 'walk', endRy: -90, keepRy: true });
for (const [n, av] of [['ben', dBen], ['nina', dNina], ['max', dMax]]) MV.add(av, 'd' + n, { from: DUP[n], to: [DUP[n][0] + 2.6, DUP[n][1]], T0: 17.3, T1: 20.6, mode: 'walk', endRy: 90 });
MV.add(nina, 'nina', { from: BACK.nina, to: [-9.5, 1.85], T0: 19.95, T1: 20.45, endRy: -135 })
  .add(max, 'max', { from: BACK.max, to: [-9.5, 2.0], T0: 21.15, T1: 21.75, endRy: 0 })
  .add(max, 'max', { from: [-9.5, 2.0], to: [-9.5, 5.6], T0: 21.75, T1: 23.1, mode: 'walk', y0: 0, y1: -1.9, endRy: 0 })
  .add(ben, 'ben', { from: BACK.ben, to: [-9.5, 2.0], T0: 21.6, T1: 22.3, endRy: 0 })
  .add(ben, 'ben', { from: [-9.5, 2.0], to: [-9.4, 4.7], T0: 22.3, T1: 23.5, mode: 'walk', y0: 0, y1: -1.35, endRy: 0 })
  .add(nina, 'nina', { from: [-9.5, 1.85], to: [-9.6, 3.35], T0: 22.9, T1: 23.6, mode: 'walk', y0: 0, y1: -0.35, endRy: 180 });

const set = alley({
  pov: A1,
  targets: { H_ben: [0.95, 1.5, -1.3], H_others: [-1.7, 1.4, 0.2], H_van: [-17.6, 1.5, 0.3], H_kids: [-11, 1.45, 0.1], alleyEnd: [-17.5, 1.2, 0.3], H_nina2: [-9.15, 0.9, 3.5], H_ninaStair: [-9.6, 1.0, 3.35], H_cellar: [-9.5, 1.2, 2.6], H_up: [-9.5, 1.5, 2.6], H_down: [-9.5, -1.0, 7.4], stair: [-9.5, -0.1, 4.0], ninaDoor: [-9.5, 1.2, 1.85] },
  onUpdate(v, t, S) { MV.update(t); for (const d of [dBen, dNina, dMax]) d.blink(1); },
});
const S = story({
  set, lead: 0, tail: 0, shake: 0.8, vignette: 0.72, audioMood: 'tension',
  badge: { title: 'FOLGE 2', label: 'Die Stadt hinter der Sperre –', value: 'DER AUSTAUSCH', until: 3.4 },
  speakers: { ben: { color: '#7fb4ff', voice: 'ben' }, max: { color: '#9cf09c', voice: 'max' }, lautsprecher: { color: '#ff8a7a', voice: 'durchsage', fx: 'radio' }, nina: { color: '#ffb0a8', voice: 'nina' }, nina2: { color: '#ff9ad0', voice: 'nina2' } },
  pov: { phone: false }, vars: { backDoor: 0, dump: 0, cellarDoor: 1, dark: 0 },
});
S.cast('ben', ben, { at: [0, -1.6, 0], pose: 'stand', face: 'scared', hide: true });
S.cast('nina', nina, { at: [0, -1.6, 0], pose: 'stand', face: 'scared', hide: true });
S.cast('max', max, { at: [0, -1.6, 0], pose: 'stand', face: 'scared', hide: true });
for (const [n, av] of [['ben', dBen], ['nina', dNina], ['max', dMax]]) S.cast('d' + n, av, { at: [...DUP[n], 90], pose: 'stand', face: 'creepy', look: 'H_kids' });
S.cast('nina2', nina2, { at: [-9.18, 3.6, 0], y: -0.45, pose: 'stand', face: 'creepy', hide: true, look: 'H_down' });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const PUSH = { hipY: 0.78, lean: 26, aL: [84, 10, 0], eL: 20, aR: [84, 10, 0], eR: 20, lL: [24, 4], kL: 20, lR: [-14, 4], kR: 10 };
const PULLIN = { hipY: 0.83, aR: [80, 30, 0], eR: 10, aL: [30, 10, 0], eL: 40 };
const keys = { ben: MV.keys('ben'), nina: MV.keys('nina'), max: MV.keys('max'), dben: MV.keys('dben'), dnina: MV.keys('dnina'), dmax: MV.keys('dmax') };
const camS = t => t < 2.4 ? A1 : t < 4.6 ? A2 : t < 6.2 ? A3 : t < 8 ? A4 : t < 10.6 ? R1 : t < 12.6 ? M1 : t < 16 ? L1 : t < 20 ? R1 : t < 21.6 ? N1 : D1;

// 00:00–00:08 · out through the back door. Ben pushes a dumpster in front of it. BEN: "Zur Brücke! Schnell!"
hold(2.4, { look: 'backDoor', zoom: 50, push: 0.02, vars: { backDoor: [1, 0.18, 0.12] }, sfx: [['doorbang', 0.12], ['nightamb', 0], ...MV.steps(camS).filter(e => e[1] < 10.6)],
  do: { ...keys, ben: [...keys.ben, { hide: false, t: 0.95 }, { look: 'dumpster', t: 1.5 }, { pose: PUSH, t: 2.3, dur: 0.25 }], nina: [...keys.nina, { hide: false, t: 0.6 }, { look: 'H_ben', t: 1.5 }], max: [...keys.max, { hide: false, t: 0.3 }, { look: 'H_ben', t: 1.2 }] } });
hold(4.6, { look: 'dumpster', zoom: 46, pov: A2, povDur: 0.5, camDur: 0.35, vars: { dump: [1, 1.9, 0.1] }, sfx: [['scrape', 0.1]] });
say('ben', 'Zur Brücke! | Schnell!', { look: 'ben', zoom: 34, pov: A3, povDur: 0.5, camDur: 0.35, headroom: 0.08, camAt: -0.2, do: { ben: { pose: 'stand', look: 'H_others', face: 'angry', t: -0.3, dur: 0.3 } } });
hold(8.0, { look: [-1.0, 1.2, -0.3], zoom: 56, pov: A4, povDur: 0.5, camDur: 0.35 });

// 00:08–00:20 · at the end of the street: a white van and their three doubles. MAX: "Warum sehen die aus wie wir?" LOUDSPEAKER: "Bitte begrüßen Sie Ihre Nachfolger."
hold(10.6, { look: 'alleyEnd', zoom: 46, pov: R1, povDur: 0.5, camDur: 0.35, sfx: [['sting', 1.9, 0.6]], do: { max: { face: 'shock', look: 'H_van', t: abs(10.3) }, nina: { face: 'shock', look: 'H_van', t: abs(10.4) }, ben: { face: 'shock', look: 'H_van', t: abs(10.5) } } });
say('max', 'Warum sehen die | aus wie wir?', { look: 'max', zoom: 32, pov: M1, povDur: 0.5, camDur: 0.35, headroom: 0.08, camAt: -0.2 });
hold(12.7, {});
say('lautsprecher', 'Bitte begrüßen Sie | Ihre Nachfolger.', { look: 'horn', zoom: 26, pov: L1, povDur: 0.5, camDur: 0.35, tag: 'LAUTSPRECHER', camAt: -0.3, sfx: [['megaphone', -0.25]] });
hold(20.0, { look: 'alleyEnd', zoom: 44, pov: R1, povDur: 0.5, camDur: 0.35, push: 0.02, sfx: [['stepw', abs(17.4), 0.5], ['stepw', abs(17.9), 0.5], ['stepw', abs(18.4), 0.55], ['stepw', abs(18.9), 0.55], ['stepw', abs(19.4), 0.6]],
  do: { dben: { pose: { head: [0, 0, 10] }, t: abs(16.8), dur: 0.6 }, dnina: { pose: { head: [0, 0, 10] }, t: abs(17.0), dur: 0.6 }, dmax: { pose: { head: [0, 0, 10] }, t: abs(17.2), dur: 0.6 } } });

// 00:20–00:30 · Nina pulls the others into an open cellar entrance. NINA: "Hier runter!" She shuts the door. In the dark, her own voice: "Hier seid ihr also."
hold(20.75, { look: 'ninaDoor', zoom: 40, pov: N1, povDur: 0.45, camDur: 0.3, do: { nina: { look: 'H_kids', face: 'scared', pose: PULLIN, t: 0.6, dur: 0.2 } } });
say('nina', 'Hier runter!', { do: { max: { look: 'H_cellar', t: 0.2 }, ben: { look: 'H_cellar', t: 0.3 } } });
hold(24.6, { look: 'H_up', zoom: 52, pov: D1, povDur: 0.4, camDur: 0.3, vars: { cellarDoor: [0, 0.35, abs(23.9)], dark: [1, 0.25, abs(24.15)] }, sfx: [['doorshut', abs(24.15)], ['stepw', abs(22.1), 0.5], ['stepw', abs(22.5), 0.5], ['stepw', abs(22.9), 0.5]],
  do: { nina: [{ pose: 'stand', t: abs(22.6) }, { pose: PULLIN, t: abs(23.7), dur: 0.25 }, { pose: 'stand', at: [-9.6, 3.35, 0], look: 'H_down', face: 'scared', t: abs(24.35), dur: 0.35 }], max: [{ face: 'scared', look: 'H_up', t: abs(23.2) }, { look: 'H_down', t: abs(24.5), dur: 0.4 }], ben: [{ look: 'H_up', t: abs(23.6) }, { look: 'H_down', face: 'scared', t: abs(24.6), dur: 0.4 }] } });
hold(26.2, { look: 'H_ninaStair', zoom: 44, push: 0.02, sfx: [['pant_soft', 0.0, 0.9], ['heart', 0.7, 0.8]], do: { nina2: { hide: false, look: 'H_ninaStair', t: abs(25.9) } } });
say('nina2', 'Hier seid | ihr also.', { do: { nina: { look: [-9.3, 0.6, 4.4], face: 'shock', t: 0.6, dur: 0.25 }, max: { face: 'shock', t: 0.8 }, ben: { face: 'shock', t: 0.9 } } });
hold(29.6, { sfx: [['sting', 0.4, 0.7]] });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
