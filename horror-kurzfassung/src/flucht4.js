// FLUCHT AUS ASCHENTAL · Folge 4 – "Der Steg" (80 s). Dawn fog at the old jetty. In the boat: Elias, and his breath shows in
// the cold. On the shore the other Elias shouts that this is not your brother. Out into the fog. Mira looks at you: everyone's
// breath shows except yours. Elias texts what he could not say: they sent you back two weeks ago. You are the copy.
import { story } from './core.js';
import { CAST } from './cast.js';
import { river, flashlight, keyed } from './fluchtsets.js';
import { loadTimings, sequencer, mover, runPath, breathPuffs } from './lib.js';
import { THREE, rbox, plane, flat, noOutline, sameId, grp, rad } from './util.js';

const clock = (h, m, t) => { const mm = m + Math.floor(t / 60); return `${String(h + Math.floor(mm / 60)).padStart(2, '0')}:${String(mm % 60).padStart(2, '0')}`; };
const TM = await loadTimings();
await Promise.all([700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));

const JX = -34, PLANK = -4.11, SEAT = -4.27, SIT_Y = SEAT - 0.49;
const BZ = [[0, -14.4], [25.6, -14.4], [32, -17.6], [60, -31.0], [80, -36.5]], BX = [[0, -32.0], [32, -31.8], [60, -30.6], [80, -30.2]];
const boatAt = t => [keyed(BX, t), keyed(BZ, t), 0];
const C0 = [JX, PLANK + 1.55, -8.0], CEND = [JX + 0.4, PLANK + 1.55, -13.5];
const WALK = [[11.0, ...C0], [15.0, ...CEND]], BOARD = [[24.4, ...CEND], [25.6, -32.0, SEAT + 0.98, -13.2]];
const walk = runPath(WALK, 0.025, 0.5), board = runPath(BOARD, 0.02, 0.4);
const CAMZ = 1.4, BRZ = 0.0, MIZ = -1.3, MIX = 0.32;   // stern seat (you), middle seat (Elias), bow (Mira, a little to the side)
const inBoat = t => { if (t < 25.6) return null; const [bx, bz] = boatAt(t); return [bx + 0.015 * Math.sin(t * 1.1), SEAT + 0.98 + 0.03 * Math.sin(t * 1.4), bz + CAMZ]; };
const camPt = t => walk(t) || board(t) || inBoat(t) || (t < 11 ? C0 : CEND);

const mira = CAST.mira(), bruder = CAST.elias(), elias = CAST.elias({ hood: true, hair: 'short' }), off = CAST.offizier();
const sol = [0, 1].map(i => { const s = CAST.soldat({ seed: 44 + i }); s.handR.add(flashlight()); return s; });
const phoneM = sameId(grp(rbox(0.075, 0.15, 0.012, 0.01, flat('#15161c')), noOutline(plane(0.064, 0.13, flat('#a8c8ff'), [0, 0, 0.007])))); phoneM.position.set(0, -0.04, 0.06); phoneM.rotation.set(-1.0, 0, 0); phoneM.visible = false; bruder.handR.add(phoneM);

const MV = mover().add(mira, 'mira', { from: [JX - 0.55, -10.2], to: [JX + 0.5, -13.9], T0: 11.2, T1: 14.8, mode: 'walk', endRy: 90 })
  .add(mira, 'mira', { from: [JX + 0.5, -13.9], to: [-32.0 + MIX, -14.4 + MIZ], T0: 15.2, T1: 15.8, mode: 'walk', arc: 0.35, y0: PLANK, y1: SIT_Y + 0.02, endRy: 0 });
const ROW = { hipY: 0.5, lean: -6, aL: [72, 14, 0], eL: 26, aR: [72, 14, 0], eR: 26, lL: [90, 4], kL: 90, lR: [90, 4], kR: 90 };
const SITM = { hipY: 0.5, lean: 4, aL: [30, 6, 0], eL: 70, aR: [30, 6, 0], eR: 70, lL: [90, 6], kL: 90, lR: [90, 6], kR: 90 };

const set = river({
  mood: 'dawn', fogFar: 30, boatAt,
  helis: [{ keys: [[0, 30, 24, -60], [24, 12, 20, -40], [29, -10, 13, -22], [33, -40, 14, -18], [40, -70, 20, -30], [80, -90, 26, -60]], light: 0.6, aim: 18 }],
  targets: { H_bruder: [-32.0, SEAT + 0.95, -14.1], H_fake: [JX - 0.8, -4.2 + 1.6, -6.6], H_off: [JX - 2.5, -4.2 + 1.75, -6.4], shore: [JX, -3.0, -7], H_fakeEnd: [JX, PLANK + 1.6, -14.9], down: [0, 0, 0] },
  onUpdate(v, t) {
    MV.update(t); elias.blink(1);
    const [bx, bz] = boatAt(t), row = v.row ?? 0;
    if (t > 15.8) { mira.root.position.set(bx + MIX, SIT_Y + 0.02, bz + MIZ); mira.root.rotation.y = 0; }
    bruder.root.position.set(bx - 0.08, SIT_Y, bz + BRZ); bruder.root.rotation.y = 0;
    if (row > 0) { bruder.torso.rotation.x += rad(10) * row * Math.sin(t * 2.4); }
    phoneM.visible = t > 51.3 && t < 58.4;
    puffs(t, camPt(t));
  },
});
const puffs = breathPuffs(set.group, { mira, bruder, off, s0: sol[0], s1: sol[1] }, (n, t) => n === 'bruder' && t > 26 && t < 40 ? 1.4 : 2.3, (n, t) => true);

const S = story({
  set, lead: 0, tail: 0, shake: 0.6, vignette: 0.6, audioMood: 'tension',
  badge: { title: 'FOLGE 4', label: 'Flucht aus Aschental –', value: 'DER STEG', until: 3.6 },
  speakers: { luca: { color: '#ffffff', voice: 'liam' }, mira: { color: '#ffd84a', voice: 'elli' }, bruder: { color: '#ff9a6a', voice: 'harry' }, elias: { color: '#ff9ad0', voice: 'harry', fx: 'far' }, off: { color: '#ff8a7a', voice: 'callum', fx: 'radio' } },
  pov: { phone: true, name: 'Luca', skin: 'light', top: '#3d6a8a' },
  paint: 1,
  infobar: t => `ASCHENTAL · ${t < 25.6 ? 'ALTER STEG' : 'AUF DEM FLUSS'} · DI ${clock(5, 58, t)}`,
  phone: { name: 'Elias', color: '#8a2a2e', clock: '05:58', history: [{ me: false, text: 'Da, wo Papa uns Schwimmen beigebracht hat.' }, { me: false, text: 'Weil du vor zwei Wochen weg warst.' }, { me: false, text: 'Weißt du das nicht mehr?' }] },
  povPath: t => { const [bx, bz] = boatAt(t); S.targets.down = [bx, SEAT - 0.05, bz + CAMZ - 0.62]; S.targets.H_bruderB = [bx - 0.08, SEAT + 0.95, bz + BRZ]; S.targets.H_miraB = [bx + MIX, SEAT + 0.92, bz + MIZ]; return walk(t) || board(t) || inBoat(t); },
  vars: { phone: 1, row: 0 },
});
S.target('H_bruderB', [-32, SEAT + 0.95, -14.1]); S.target('H_miraB', [-32, SEAT + 0.92, -15.35]); S.target('down', [-32, SEAT, -12.8]);
// heads in the boat aim from where the engine thinks the figure stands, so these points sit where the camera is relative to it
S.target('Pb', [-32.0 + 0.08, SEAT + 0.98, -14.1 + CAMZ - BRZ]); S.target('Pm', [-32.0 + MIX - MIX, SEAT + 0.98, -14.4 + MIZ + CAMZ - MIZ]);
S.cast('mira', mira, { at: [JX - 0.55, -10.2, 180], y: PLANK, pose: 'stand', face: 'worried', look: 'H_bruder' });
S.cast('bruder', bruder, { at: [-32.0, -14.1, 0], y: SIT_Y, pose: 'sitChair', face: 'worried', look: 'Pb' });
S.cast('elias', elias, { at: [JX - 0.8, -6.6, 180], y: -4.2, pose: 'stand', face: 'angry', look: 'pov', hide: true });
S.cast('off', off, { at: [JX - 2.5, -6.4, 160], y: -4.2, pose: 'stand', face: 'sus', look: 'pov', hide: true });
sol.forEach((s, i) => S.cast('s' + i, s, { at: [[JX - 3.8, -6.0, 170], [JX + 2.4, -6.1, 200]][i], y: -4.2, pose: { hipY: 0.83, aR: [40, 6, 0], eR: 30 }, face: 'angry', look: null, hide: true }));

const Z = sequencer(S, TM), { hold, say, phone, abs } = Z;
const mySteps = []; for (let t = 11.1; t < 14.9; t += 0.5) mySteps.push(['stepw', +t.toFixed(3), 0.7]);
const REACH = { ...SITM, lean: 14, aR: [74, 4, 0], eR: 10 }, PHONE = { ...SITM, aR: [42, -6, 0], eR: 100, head: [24, 0, 0] }, BACK = { ...SITM, lean: -16, aL: [20, 20, 0], eL: 40, aR: [20, 20, 0], eR: 40 };

// 00:00–00:11 · dawn fog, the jetty, the boat. "Spatz? Bist du das?" His breath shows in the cold.
hold(1.8, { look: 'H_bruder', zoom: 34, pov: C0, sfx: [['water', 0, 1.0], ['cityamb', 0, 0.45], ['heli_far', 0, 0.6], ...mySteps, ...MV.steps(camPt)], do: { mira: MV.keys('mira') } });
say('bruder', 'Spatz? | Bist du das?', { look: 'H_bruder', zoom: 28, do: { bruder: { face: 'worried', t: 0 } } });
hold(3.4, {});
say('luca', 'Elias! | Bist du es | wirklich?', { look: 'H_bruder', zoom: 30 });
hold(5.2, {});
say('bruder', 'Schnell. | Bevor der Nebel | weg ist.', { look: 'H_bruder', zoom: 26, do: { bruder: { pose: REACH, t: 0.5, dur: 0.5 } } });
hold(9.2, { look: 'H_bruder', zoom: 16, push: 0.02, sfx: [['heart', 0.5, 0.5]], do: { bruder: { pose: SITM, t: 0.2, dur: 0.5 } } });
say('mira', 'Er atmet. | Das ist er.', { look: 'mira', zoom: 40, camAt: -0.2, do: { mira: [{ look: 'pov', face: 'smile', t: 0, dur: 0.3 }, { look: 'H_bruder', t: 1.4 }] } });
// 00:11–00:25 · along the jetty. Voices on the shore: the other Elias, the man in the coat, flashlights in the fog.
hold(15.0, { look: 'H_bruder', zoom: 58, pov: CEND, povDur: 4.0, camDur: 0.5, do: { mira: { face: 'worried', t: 0 } } });
hold(17.2, { look: 'H_miraB', zoom: 54, camDur: 0.4, sfx: [['stepw', 0.4, 0.5], ['creak', 0.6, 0.4], ['stepw', 1.1, 0.4]], do: { mira: [{ pose: SITM, look: 'Pm', t: 0.6, dur: 0.6 }], elias: { hide: false, t: abs(16.5) }, off: { hide: false, t: abs(16.4) }, s0: { hide: false, t: abs(16.2) }, s1: { hide: false, t: abs(16.3) } } });
say('elias', 'Luca! | Steig nicht | in das Boot!', { look: 'H_fake', zoom: 30, camAt: -0.3, camDur: 0.32, tag: 'UFER', sfx: [['sting', -0.25, 0.7]] });
hold(19.3, {});
say('elias', 'Er ist nicht | dein Bruder.', { look: 'H_fake', zoom: 22, tag: 'UFER', push: 0.02 });
hold(22.2, { look: 'H_bruder', zoom: 50, camDur: 0.4, sfx: [['heart', 0.3, 0.7], ['heart', 1.1, 0.75]], do: { bruder: { pose: REACH, face: 'scared', t: 0.2, dur: 0.4 } } });
hold(24.0, { look: 'H_fake', zoom: 26, camDur: 0.35 });
say('bruder', 'Mama ist | schon drüben.', { look: 'H_bruder', zoom: 52, camAt: -0.2 });
// 00:25–00:40 · into the boat, out into the fog. A searchlight crosses above. Then only the oars.
hold(29.0, { look: 'H_bruderB', zoom: 74, pov: [-32.0, SEAT + 0.98, -13.2], povDur: 1.2, camDur: 0.5, vars: { row: [1, 0.6, 1.4] }, sfx: [['creak', 0.2, 0.5], ['oars', 1.6, 1.0], ['heli', 0.2, 1.1]], do: { bruder: { pose: ROW, look: 'Pb', face: 'worried', t: 1.2, dur: 0.5 }, elias: { look: 'pov', t: 0 } } });
hold(33.4, { look: [-28, 2, -26], zoom: 70, camDur: 0.6, vars: { row: [0, 0.4, 0.4] }, do: { bruder: { pose: SITM, look: [-28, 3, -24], t: 0.3, dur: 0.5 }, mira: { look: [-28, 3, -24], t: 0.2 } } });
hold(40.5, { look: 'H_bruderB', zoom: 66, camDur: 0.5, vars: { row: [1, 0.6, 0.2] }, sfx: [['stop_oars', 0.0], ['oars', 0.4, 1.0]], do: { bruder: { pose: ROW, look: 'Pb', t: 0.2, dur: 0.5 }, mira: { look: 'Pm', t: 0.4 }, elias: { hide: true, t: abs(36) }, off: { hide: true, t: abs(36) }, s0: { hide: true, t: abs(36) }, s1: { hide: true, t: abs(36) } } });
// 00:40–00:61 · "Sag mal was." Mira looks at your mouth. Everyone's breath shows in the cold. Yours does not.
say('bruder', 'Luca… | sag mal was.', { look: 'H_bruderB', zoom: 58, vars: { row: [0, 0.5, 0.0] }, sfx: [['stop_oars', 0.0]], do: { bruder: { pose: SITM, face: 'worried', t: 0, dur: 0.5 } } });
hold(42.3, {});
say('luca', 'Was denn?', { look: 'H_bruderB', zoom: 62 });
hold(44.8, { look: 'H_miraB', zoom: 40, camDur: 0.45, push: 0.02, sfx: [['heart', 0.3, 0.75], ['heart', 1.1, 0.8]], do: { mira: { look: 'Pm', face: 'scared', t: 0 } } });
hold(46.6, { look: 'H_bruderB', zoom: 44, camDur: 0.4, push: 0.02, do: { bruder: { face: 'scared', t: 0 } } });
say('mira', 'Luca. | Wo ist | dein Atem?', { look: 'H_miraB', zoom: 42, camAt: -0.2 });
hold(49.1, {});
say('luca', 'Ich atme doch. | Ich… | atme doch.', { look: 'down', zoom: 70, camAt: -0.2, camDur: 0.5 });
hold(51.8, { look: 'H_bruderB', zoom: 56, camDur: 0.45, do: { bruder: { pose: PHONE, face: 'sad', t: 0, dur: 0.5 } } });
phone({ low: true, look: 'H_bruderB', zoom: 52, events: [{ in: 'Ich wollte es dir nicht sagen.', hold: 1.8 }, { in: 'Sie haben dich vor zwei Wochen zurückgeschickt.', hold: 2.2 }, { in: 'Du bist die Kopie.', alert: true, hold: 2.0 }] });
hold(59.2, { look: 'H_bruderB', zoom: 38, camDur: 0.4, push: 0.02, sfx: [['sting', 0.1, 0.8]], do: { bruder: { pose: SITM, face: 'sad', t: 0.4, dur: 0.6 } } });
say('luca', 'Nein. | Ich bin | Luca.', { look: 'H_bruderB', zoom: 44 });
// 00:61–01:20 · from the fog behind: the man in the coat. The other Elias at the end of the jetty. Your hands.
hold(64.2, { look: [-34, -2.6, -14.9], zoom: 46, camDur: 0.6, sfx: [['heart', 1.0, 0.6]], do: { elias: [{ at: [JX, -14.9, 180], y: PLANK, pose: 'stand', face: 'smile', look: 'pov', t: abs(61.0), dur: 0 }, { hide: false, t: abs(62.2) }], off: [{ at: [JX - 0.9, -13.2, 180], y: PLANK, t: abs(61.0), dur: 0 }, { hide: false, t: abs(61.2) }] } });
say('off', 'Lasst ihn gehen. | Er findet immer | nach Hause.', { look: [-34, -2.6, -14.9], zoom: 40, tag: 'UFER' });
hold(70.2, { look: 'H_fakeEnd', zoom: 20, camDur: 0.4, push: 0.02 });
say('elias', 'Bis gleich, | Spatz.', { look: 'H_fakeEnd', zoom: 16, tag: 'STEG', do: { elias: { face: 'creepy', t: 0.2 } } });
hold(75.6, { look: 'down', zoom: 66, camDur: 0.6, push: 0.03, sfx: [['heart', 0.5, 0.8], ['heart', 1.5, 0.7], ['heart', 2.8, 0.6]] });
hold(79.6, { look: 'H_bruderB', zoom: 70, camDur: 0.5, push: 0.02, do: { bruder: { pose: BACK, face: 'scared', t: 0.4, dur: 1.6 }, mira: { pose: { ...SITM, lean: -20 }, face: 'scared', t: 0.2, dur: 1.6 } } });
Z.black(79.6, 80.0);
S.start();
