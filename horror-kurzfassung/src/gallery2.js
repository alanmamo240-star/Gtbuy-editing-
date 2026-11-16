// Lineup of the blocky cast (not part of a video):  STORY=gallery2 NOTIMINGS=1 node tools/snap.mjs 0.2 0.7 1.2
import { story } from './core.js'; import { SETS } from './sets.js'; import { CAST } from './cast.js';
const set = SETS.studio({ w: 30, d: 10 }); const S = story({ set, pov: { phone: false }, vignette: 0.1, shake: 0 });
const names = Object.keys(CAST), faces = ['neutral', 'scared', 'shock', 'worried', 'sus', 'creepy', 'smile'];
names.forEach((n, i) => S.cast(n, CAST[n](), { at: [-3 + i * 1.0, -1.0, 0], pose: i % 2 ? 'stand' : 'open', face: faces[i % faces.length] }));
S.cast('pick', CAST.paul(), { at: [5, -1.0, 30], pose: { ...{ hipY: 0.27, lean: 46, aR: [52, 4, 0], eR: 8 }, lL: [112, 10], kL: 142, lR: [112, 10], kR: 142 }, face: 'worried' });
S.hold(0.5, { look: [0, 1.0, -1.0], zoom: 62, pov: [0, 1.3, 5.2], cut: true });
for (let i = 0; i < names.length + 1; i++) { const x = i < names.length ? -3 + i : 5; S.hold(0.5, { look: [x, i === names.length ? 0.6 : 1.42, -1.0], zoom: i === names.length ? 50 : 26, pov: [x + 0.25, 1.45, 0.4], cut: true }); }
S.start();
