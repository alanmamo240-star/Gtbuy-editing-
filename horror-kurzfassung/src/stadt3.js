// DIE STADT HINTER DER SPERRE · Folge 3 – "Eine Sekunde später" (30 s). A phone light in the cellar, Nina's double behind a grid door, the vent shaft.
import { story } from './core.js';
import { CAST } from './cast.js';
import { cellar } from './stadtsets.js';
import { towards, loadTimings, sequencer, mover, CRAWL } from './lib.js';
import { THREE, clamp, lerp, smooth, rad } from './util.js';

const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const C1 = [-2.6, 1.35, 0.9], C2 = [-0.2, 1.45, 0.9], C3 = [0.6, 1.4, 1.5], C4 = [-2.3, 1.5, 0.05], C5 = [0.4, 1.45, -0.05], C6 = [0.5, 1.3, -0.3], C7 = [2.4, 0.75, 0.55], C8 = [1.5, 0.8, 1.05];
const SH1 = [8.75, 0.5, 1.5], SH2 = [8.85, 0.52, 1.62], SH3 = [8.5, 0.5, 1.5], SH4 = [7.3, 0.7, 1.75];
const ben = CAST.ben(), nina = CAST.nina(), max = CAST.max(), dn = CAST.nina();
const HOME = { ben: [-0.6, 0.35, 90], max: [-1.2, 1.0, 100], nina: [-1.0, -0.45, 80] }, DN = [2.4, -0.55, -90];
const VENT = { ben: [2.35, 1.25], max: [1.9, 0.55], nina: [1.55, 1.85] };
const MV = mover();
for (const n of ['ben', 'max', 'nina']) MV.add({ ben, max, nina }[n], n, { from: HOME[n].slice(0, 2), to: VENT[n], T0: 15.6 + (n === 'max' ? 0.2 : n === 'nina' ? 0.4 : 0), T1: 17.6 + (n === 'nina' ? 0.3 : 0), mode: 'walk', endRy: n === 'ben' ? -100 : 80 });
MV.add(max, 'max', { from: [3.25, 1.5], to: [7.6, 1.5], T0: 19.95, T1: 23.1, mode: 'crawl', y0: 0.12, y1: 0.12, endRy: 90, keepRy: true })
  .add(ben, 'ben', { from: [3.0, 1.5], to: [6.2, 1.5], T0: 20.35, T1: 23.4, mode: 'crawl', y0: 0.12, y1: 0.12, endRy: 90, keepRy: true, ph: 0.3 })
  .add(nina, 'nina', { from: [2.8, 1.5], to: [4.9, 1.5], T0: 20.8, T1: 23.6, mode: 'crawl', y0: 0.12, y1: 0.12, endRy: 90, keepRy: true, ph: 0.55 });
const v1 = new THREE.Vector3();
const aimAt = t => t < 1.6 ? [1.2, 0.2, 0.3] : t < 2.6 ? [lerp(1.2, 2.4, smooth((t - 1.6) / 1.0)), lerp(0.2, 1.45, smooth((t - 1.6) / 1.0)), lerp(0.3, -0.55, smooth((t - 1.6) / 1.0))] : t < 13.4 ? [2.4, 1.35, -0.55] : t < 15.0 ? [3.0, 0.47, 1.5] : [3.0, 0.5, 1.5];
const set = cellar({
  pov: C1,
  phoneAt: t => { ben.root.updateMatrixWorld(true); ben.handR.getWorldPosition(v1); return [[v1.x + 0.05, v1.y + 0.08, v1.z], aimAt(t)]; },
  targets: { kids: [-0.9, 1.3, 0.3], H_dn: [2.4, 1.48, -0.55], H_nina: [-1.0, 1.4, -0.45], H_max: [-1.2, 1.43, 1.0], H_ben: [-0.6, 1.5, 0.35], mirror: [0.9, 1.35, -0.5], ventLow: [2.6, 0.6, 1.45], benVent: [2.35, 1.12, 1.25], H_cam: [1.5, 0.8, 1.05],
    maxFace: [8.28, 0.44, 1.5], benFace: [6.88, 0.42, 1.5], crawlers: [6.5, 0.45, 1.5], kidsLow: [1.4, 0.75, 1.2] },
  onUpdate(v, t, S) { MV.update(t); dn.blink(1); },
});
const S = story({
  set, lead: 0, tail: 0, shake: 0.7, vignette: 0.74, audioMood: 'tension',
  badge: { title: 'FOLGE 3', label: 'Die Stadt hinter der Sperre –', value: 'EINE SEKUNDE SPÄTER', until: 3.4 },
  speakers: { max: { color: '#9cf09c', voice: 'max' }, nina: { color: '#ffb0a8', voice: 'nina' }, ben: { color: '#7fb4ff', voice: 'ben', fx: 'whisper' }, draussen: { color: '#d0d4ee', voice: 'ben2', fx: 'far' } },
  pov: { phone: false }, vars: { phone: 0, cover: 0, arm: 0, day: 1, gdoor: 0 },
});
S.cast('ben', ben, { at: HOME.ben, pose: 'stand', face: 'scared', look: 'H_dn' });
S.cast('max', max, { at: HOME.max, pose: 'stand', face: 'scared', look: 'H_dn' });
S.cast('nina', nina, { at: HOME.nina, pose: 'stand', face: 'scared', look: 'H_dn' });
S.cast('dn', dn, { at: DN, pose: 'stand', face: 'creepy', look: 'H_nina' });

const Z = sequencer(S, TM), { hold, say, abs } = Z;
const PHONE = { hipY: 0.83, aR: [72, -4, 0], eR: 18 };
const RAISE = { hipY: 0.83, aR: [168, 6, 0], eR: 6 };
const TILT = { hipY: 0.83, aR: [168, 6, 0], eR: 6, head: [0, 0, 16] };
const POINTV = { hipY: 0.83, aL: [40, 40, 0], eL: 6, aR: [72, -4, 0], eR: 18 };
const DUCK = { hipY: 0.48, lean: 30, aL: [40, 8, 0], eL: 60, aR: [62, -4, 0], eR: 30, lL: [80, 8], kL: 110, lR: [80, 8], kR: 110, head: [-14, 0, 0] };
const keys = { ben: MV.keys('ben'), max: MV.keys('max'), nina: MV.keys('nina') };

// 00:00–00:08 · darkness. Ben switches on his phone light. Behind a grid door stands Nina's double. MAX: "Welche ist echt?"
hold(1.6, { look: 'kids', zoom: 50, vars: { phone: [1, 0.12, 1.0] }, sfx: [['drips', 0], ['click', 1.0]], do: { ...keys, ben: [...keys.ben, { pose: PHONE, t: 0.6, dur: 0.35 }] } });
hold(4.6, { look: 'H_dn', zoom: 32, pov: C2, povDur: 0.5, camDur: 0.4, push: 0.02, sfx: [['sting', 1.05, 0.7]], do: { dn: { pose: { head: [0, 0, -6] }, t: 1.8, dur: 1.5 } } });
say('max', 'Welche | ist echt?', { look: 'max', zoom: 30, pov: C3, povDur: 0.5, camDur: 0.35, headroom: 0.08, camAt: -0.2, do: { max: [{ look: 'H_nina', face: 'shock', t: -0.1 }, { look: 'H_dn', t: 'p1', dur: 0.3 }] } });
hold(8.0, { look: 'mirror', zoom: 42, pov: C4, povDur: 0.5, camDur: 0.35, do: { nina: { look: 'H_dn', face: 'worried', t: 0.3 } } });

// 00:08–00:20 · Nina raises her hand; her double does it a second later. NINA: "Sie machen uns nur nach." Ben points at a low vent; all duck. BEN: "Da rein."
hold(11.6, { push: 0.025, sfx: [['sting', 1.6, 0.5]],
  do: { nina: [{ pose: RAISE, t: 0.55, dur: 0.45 }, { pose: TILT, t: 2.4, dur: 0.4 }], dn: [{ pose: RAISE, t: 1.55, dur: 0.45 }, { pose: TILT, t: 3.4, dur: 0.4 }] } });
say('nina', 'Sie machen | uns nur nach.', { look: 'nina', zoom: 32, pov: C5, povDur: 0.45, camDur: 0.35, headroom: 0.08, camAt: -0.2, do: { nina: { pose: 'stand', look: 'H_max', face: 'scared', t: -0.2, dur: 0.4 }, dn: { pose: 'stand', look: 'H_max', t: 0.8, dur: 0.4 } } });
hold(15.6, { look: 'vent', zoom: 32, pov: C6, povDur: 0.5, camDur: 0.4, do: { ben: [{ pose: POINTV, look: 'vent', t: abs(13.8), dur: 0.3 }], max: { look: 'vent', t: abs(14.2) }, nina: { look: 'vent', t: abs(14.4) } } });
hold(18.1, { look: 'kidsLow', zoom: 56, pov: C7, povDur: 0.5, camDur: 0.4, vars: { cover: [1, 0.4, abs(17.6)] }, sfx: [['ventoff', abs(17.6)], ['shuffle', abs(15.7)]],
  do: { ben: [{ pose: DUCK, look: 'vent', t: abs(15.5), dur: 0.35 }], max: { pose: DUCK, look: 'vent', t: abs(15.7), dur: 0.35 }, nina: { pose: DUCK, look: 'vent', t: abs(15.9), dur: 0.35 } } });
say('ben', 'Da rein.', { look: 'benVent', zoom: 52, pov: C8, povDur: 0.4, camDur: 0.3, camAt: -0.15, vars: { phone: [0, 0.2, -0.5] }, do: { ben: { look: 'H_cam', face: 'scared', t: -0.1 } } });
hold(20.0, {});

// 00:20–00:30 · crawling through the shaft. Max reaches the outer grille. MAX: "Tageslicht!" A hand grabs the grille. BEN'S VOICE: "Ich helfe euch raus." The real Ben, in the shaft. Black.
hold(23.0, { cut: true, look: 'crawlers', zoom: 58, pov: SH1, sfx: [['crawl', 0.0], ['birds', 0.0, 0.6]], vars: { phone: [0, 0, 0] },
  do: { max: { pose: CRAWL, look: null, t: 0, dur: 0 }, ben: { pose: CRAWL, look: null, t: 0, dur: 0 }, nina: { pose: CRAWL, look: null, t: 0, dur: 0 } } });
say('max', 'Tageslicht!', { look: 'maxFace', zoom: 66, pov: SH2, povDur: 0.4, camDur: 0.3, camAt: -0.1, do: { max: { face: 'smile', t: -0.2 } } });
hold(24.6, {});
hold(26.4, { look: 'grille', zoom: 72, pov: SH3, povDur: 0.4, camDur: 0.3, vars: { arm: [1, 0.25, abs(25.0)] }, sfx: [['grate', abs(25.1)], ['sting', abs(25.1), 0.6]], do: { max: { face: 'shock', t: abs(25.2) } } });
say('draussen', 'Ich helfe | euch raus.', { tag: 'DRAUSSEN' });
hold(29.6, { look: 'benFace', zoom: 86, pov: SH4, povDur: 0.35, camDur: 0.25, push: 0.03, sfx: [['heart', 0.3, 0.9], ['heart', 1.1, 1.0]], do: { ben: { face: 'shock', tremble: 1, t: 0 } } });
hold(30.0, { overlay: (c, w, h) => { c.fillStyle = '#000'; c.fillRect(0, 0, w, h); } });
S.start();
