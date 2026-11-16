// Lineup of the cast (not part of a video):  STORY=gallery2 NOTIMINGS=1 tools/ep.sh gallery snap 0.25 0.75 ...
import { story } from './core.js'; import { SETS } from './sets.js'; import { CAST } from './cast.js';
const set = SETS.studio({ w: 30, d: 10 }); const S = story({ set, pov: { phone: false }, vignette: 0.1, shake: 0 });
const names = Object.keys(CAST), faces = ['neutral', 'scared', 'shock', 'worried', 'sus', 'creepy', 'smile'], H = {};
names.forEach((n, i) => { const f = CAST[n](); H[n] = f.P.height; S.cast(n, f, { at: [-3 + i * 1.0, -1.0, 0], pose: i % 2 ? 'stand' : 'open', face: faces[i % faces.length] }); });
S.hold(0.5, { look: [0, 1.0, -1.0], zoom: 62, pov: [0, 1.3, 5.2], cut: true });
names.forEach((n, i) => { const x = -3 + i; S.hold(0.5, { look: [x, 1.5 * H[n], -1.0], zoom: 30, pov: [x + 0.35, 1.55 * H[n], 0.6], cut: true }); });
S.hold(0.5, { look: [0, 0.9, -1.0], zoom: 50, pov: [0, 1.0, 3.2], cut: true });
S.start();
