// DIE STADT HINTER DER SPERRE · Folge 4 – "Der andere Weg" (30 s). The side hatch, the drain pipe, the river, three figures on the other bank.
import { story } from './core.js';
import { CAST } from './cast.js';
import { cellar, riverbank, phoneMesh, alertTex } from './stadtsets.js';
import { towards, loadTimings, sequencer, mover, CRAWL } from './lib.js';
import { THREE, clamp, lerp, smooth, rad } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

// ---- inside the shaft (cellar set): Max at the grille, Ben behind him, Nina last next to the hatch
const W1 = [7.15, 0.72, 1.3], W2 = [5.35, 0.5, 2.45];
const ben = CAST.ben(), nina = CAST.nina(), max = CAST.max();
const MVs = mover()
  .add(max, 'max', { from: [7.6, 1.5], to: [7.2, 1.5], T0: 0.6, T1: 1.3, mode: 'still', y0: 0.12, y1: 0.12, endRy: 90, keepRy: true })
  .add(nina, 'nina', { from: [4.4, 1.5], to: [4.95, 1.6], T0: 6.0, T1: 7.4, mode: 'crawl', y0: 0.12, y1: 0.12, endRy: 30 });
const shaft = cellar({ pov: W1, targets: { grilleS: [9.0, 0.5, 1.5], maxBack: [8.0, 0.4, 1.5], ninaFace: [5.1, 0.45, 1.5], H_hatch: [5.5, 0.47, 2.3], H_max: [8.2, 0.45, 1.5] },
  onUpdate(v, t) { MVs.update(t); } });

// ---- outside: the drain pipe, the riverbank, the far bank
const P1 = [0, 0.62, 13.8], O1 = [2.2, 1.3, 2.6], R1 = [2.5, 1.35, -2.6], R2 = [0.45, 1.3, -6.2], PH = [-0.3, 1.2, -3.95], B1 = [0.6, 1.6, -1.2], T1 = [0.5, 1.5, -4.3];
const rb = { ben: CAST.ben(), nina: CAST.nina(), max: CAST.max() }, fb = { ben: CAST.ben(), nina: CAST.nina(), max: CAST.max() };
const BANK = { nina: [-0.4, -3.0], max: [0.5, -2.9], ben: [1.3, -3.2] }, FAR = { nina: [-0.4, -21.6], max: [0.5, -21.5], ben: [1.3, -21.8] };
const OUT = { nina: [-0.3, 4.6], max: [0.45, 4.4], ben: [0.9, 5.0] };
const MVo = mover()
  .add(rb.nina, 'nina_r', { from: [0, 12.6], to: [0, 6.2], T0: 8.0, T1: 10.7, mode: 'crawl', y0: 0.13, y1: 0.13, endRy: 180, keepRy: true })
  .add(rb.max, 'max_r', { from: [0, 13.6], to: [0, 6.3], T0: 8.0, T1: 11.4, mode: 'crawl', y0: 0.13, y1: 0.13, endRy: 180, keepRy: true, ph: 0.3 })
  .add(rb.ben, 'ben_r', { from: [0, 14.6], to: [0, 6.3], T0: 8.0, T1: 12.0, mode: 'crawl', y0: 0.13, y1: 0.13, endRy: 180, keepRy: true, ph: 0.6 })
  .add(rb.nina, 'nina_r', { from: [0, 6.2], to: OUT.nina, T0: 10.75, T1: 11.4, mode: 'walk', endRy: 170 })
  .add(rb.max, 'max_r', { from: [0, 6.3], to: OUT.max, T0: 11.45, T1: 12.1, mode: 'walk', endRy: 200 })
  .add(rb.ben, 'ben_r', { from: [0, 6.3], to: OUT.ben, T0: 12.05, T1: 12.6, mode: 'walk', endRy: 0 });
for (const n of ['nina', 'max', 'ben']) MVo.add(rb[n], n + '_r', { from: OUT[n], to: BANK[n], T0: 18.2 + (n === 'max' ? 0.1 : n === 'ben' ? 0.25 : 0), T1: 20.3 + (n === 'ben' ? 0.15 : 0), endRy: 180, ph: n.length * 0.13 });
const msg = alertTex('NACHRICHT', ['Austausch', 'außerhalb der', 'Stadt', 'fortsetzen.'], '#3a5ad8'), dark = alertTex('', [], '#0d0f18');
const phone = phoneMesh(dark), T_BEEP = 20.9, LIFT = [-0.38, 1.12, -3.42];
const river = riverbank({
  pov: P1,
  targets: { pipeOut: [0, 0.6, 6.0], outside: [0.3, 1.0, 5.2], H_max: [0.45, 1.43, 4.4], H_ben: [0.9, 1.5, 5.0], runners: [0.4, 1.0, -1.5], group: [0.5, 1.1, -3.0], phone: LIFT, far: [0.45, 1.25, -21.6], farW: [0.0, 1.35, -21.6], H_far: [0.5, 1.4, -21.6], H_kids: [0.5, 1.4, -3.0], H_grille: [0, 0.8, 6.0] },
  onUpdate(v, t, S) {
    MVo.update(t);
    for (const n in fb) fb[n].blink(1);
    const l = smooth((t - 21.3) / 0.5); phone.visible = t > 20.5; phone.userData.screen.material.map = t > T_BEEP ? msg : dark;
    phone.position.set(lerp(-0.25, LIFT[0], l), lerp(0.95, LIFT[1], l), lerp(-3.05, LIFT[2], l)); phone.lookAt(PH[0], PH[1], PH[2]); phone.rotateX(Math.PI / 2);
  },
});
river.scene.add(phone);

const S = story({
  set: shaft, lead: 0, tail: 0, shake: 0.7, vignette: 0.7, audioMood: 'tension',
  badge: { title: 'FOLGE 4', label: 'Die Stadt hinter der Sperre –', value: 'DER ANDERE WEG', until: 3.2 },
  speakers: { nina: { color: '#ffb0a8', voice: 'nina' }, max_r: { color: '#9cf09c', voice: 'max' }, ben_r: { color: '#7fb4ff', voice: 'ben' } },
  pov: { phone: false }, vars: { arm: 1, hatch: 0, grille: 1, hands: 0, phone: 0 },
});
S.cast('max', max, { at: [7.6, 1.5, 90], y: 0.12, pose: CRAWL, face: 'scared' });
S.cast('ben', ben, { at: [6.0, 1.5, 90], y: 0.12, pose: CRAWL, face: 'scared' });
S.cast('nina', nina, { at: [4.4, 1.5, 90], y: 0.12, pose: CRAWL, face: 'scared' });
for (const n of ['nina', 'max', 'ben']) S.cast(n + '_r', rb[n], { set: river, at: [0, { nina: 12.6, max: 13.6, ben: 14.6 }[n], 180], y: 0.13, pose: CRAWL, face: 'scared' });
for (const n of ['nina', 'max', 'ben']) S.cast('f_' + n, fb[n], { set: river, at: [...FAR[n], 0], y: 0.2, pose: 'stand', face: 'smile', look: 'H_kids' });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const REACHF = { ...CRAWL, aR: [150, 4, 0], eR: 6, aL: [150, 4, 0], eL: 6 };
const HATCH = { ...CRAWL, aL: [120, 50, 0], eL: 20 };
const SHUT = { hipY: 0.83, lean: 10, aR: [80, -10, 0], eR: 14, aL: [70, 10, 0], eL: 30 };
const HOLDP = { hipY: 0.83, aR: [52, -16, 0], eR: 70, aL: [48, -16, 0], eL: 70, head: [14, 0, 0] };
const WAVE1 = { hipY: 0.83, aR: [24, 150, 0], eR: 26 }, WAVE2 = { hipY: 0.83, aR: [24, 150, 0], eR: 60 };
const kS = { max: MVs.keys('max'), nina: MVs.keys('nina') }, kO = { nina_r: MVo.keys('nina_r'), max_r: MVo.keys('max_r'), ben_r: MVo.keys('ben_r') };
const waves = []; for (let k = 0; k < 6; k++) waves.push({ pose: k % 2 ? WAVE2 : WAVE1, t: 0, dur: 0.22 });

// 00:00–00:08 · Ben pulls Max back from the grille. Nina opens a side hatch. NINA: "Nicht zu ihm. Hier lang!"
hold(2.2, { look: 'maxBack', zoom: 60, push: 0.02, sfx: [['shuffle', 0.6], ['grate', 0.2, 0.6], ['drips', 0]], do: { ...kS, ben: { pose: REACHF, t: 0.4, dur: 0.3 }, max: [...kS.max, { face: 'shock', t: 0.6 }] } });
hold(4.0, { look: 'ninaFace', zoom: 56, pov: W2, povDur: 0.4, camDur: 0.3, vars: { hatch: [1, 0.5, 0.6] }, sfx: [['ventoff', 0.65, 0.7]], do: { nina: [{ pose: HATCH, look: 'H_hatch', t: 0.2, dur: 0.3 }, { pose: CRAWL, t: 1.2, dur: 0.3 }] } });
say('nina', 'Nicht zu ihm. | Hier lang!', { do: { nina: { look: [5.35, 0.5, 2.45], face: 'worried', t: -0.2 } } });
hold(8.0, { sfx: [['crawl', abs(6.0)]] });

// 00:08–00:20 · through a flat drain pipe into the open. Ben locks the grille behind them; hands reach through too late. MAX: "Sind wir jetzt draußen?" BEN: "Lauf weiter!"
hold(10.9, { set: river, cut: true, look: 'pipeOut', zoom: 50, pov: P1, push: 0.02, sfx: [['crawl', 0.1], ['river', 0, 0.8], ['birds', 0.5, 0.7]], do: { max_r: kO.max_r.map(k => ({ ...k, t: abs(k.t) })), ben_r: kO.ben_r.map(k => ({ ...k, t: abs(k.t) })), nina_r: [...kO.nina_r.map(k => ({ ...k, t: abs(k.t) })), { pose: 'stand', look: 'H_kids', t: abs(10.8), dur: 0.4 }] } });
hold(14.5, { look: 'outside', zoom: 50, pov: O1, povDur: 0.4, camDur: 0.3, vars: { grille: [0, 0.3, abs(13.05)], hands: [1, 0.8, abs(13.55)] }, sfx: [['grate', abs(13.2)], ['click', abs(13.5)], ['rattle', abs(13.8)], ['rattle', abs(14.2)]],
  do: { max_r: [{ pose: 'stand', t: abs(11.5), dur: 0.4 }, { look: 'H_grille', t: abs(12.4) }], ben_r: [{ pose: 'stand', t: abs(12.1), dur: 0.4 }, { pose: SHUT, look: 'H_grille', t: abs(12.7), dur: 0.3 }, { pose: 'stand', face: 'shock', t: abs(13.7), dur: 0.3 }], nina_r: { look: 'H_grille', face: 'scared', t: abs(13.3) } } });
say('max_r', 'Sind wir | jetzt draußen?', { look: 'max_r', zoom: 34, headroom: 0.08, camAt: -0.15, do: { max_r: { look: 'H_ben', face: 'scared', t: -0.2 } } });
hold(16.55, {});
say('ben_r', 'Lauf weiter!', { look: 'ben_r', zoom: 34, headroom: 0.08, camAt: -0.15, do: { ben_r: { at: [...OUT.ben, 205], look: 'H_max', face: 'angry', t: -0.35, dur: 0.3 } } });
hold(20.0, { look: 'runners', zoom: 56, pov: R1, povDur: 0.4, camDur: 0.3, sfx: MVo.steps(t => R1).filter(e => e[1] > 18).map(e => [e[0], abs(e[1]), e[2]]) });

// 00:20–00:30 · on the riverbank. Nina's phone: "Austausch außerhalb der Stadt fortsetzen." Three figures on the far bank; one waves. Three seconds of silence. Black.
hold(21.3, { look: 'group', zoom: 58, pov: R2, povDur: 0.4, camDur: 0.3, sfx: [['pant', 0.1, 1.0], ['notify', T_BEEP - 20.0]], do: { nina_r: { look: 'phone', t: 1.0 }, max_r: { look: 'H_far', t: 0.0 }, ben_r: { look: 'H_far', t: 0.1 } } });
hold(24.4, { look: 'phone', zoom: 26, pov: PH, povDur: 0.4, camDur: 0.3, push: 0.02, do: { nina_r: { pose: HOLDP, look: 'phone', face: 'worried', t: 0.0, dur: 0.45 } } });
hold(26.0, { look: 'far', zoom: 30, pov: B1, povDur: 0.5, camDur: 0.35, do: { nina_r: { pose: 'stand', look: 'H_far', face: 'shock', t: 0.2, dur: 0.4 }, max_r: { look: 'H_far', face: 'shock', t: 0.3 }, ben_r: { look: 'H_far', face: 'shock', t: 0.45 } } });
hold(29.6, { look: 'farW', zoom: 17, pov: T1, povDur: 0.4, camDur: 0.3, push: 0.01, sfx: [['silence', abs(26.6)]],
  do: { f_nina: waves.map((w, k) => ({ ...w, t: abs(26.3 + k * 0.32) })).concat([{ pose: 'stand', t: abs(28.3), dur: 0.4 }]) } });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
