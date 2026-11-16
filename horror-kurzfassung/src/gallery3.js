// Close-ups of the Flucht cast (not part of a video):  STORY=gallery3 NOTIMINGS=1 tools/ep.sh gallery snap 0.25 0.75 ...
import { story } from './core.js'; import { SETS } from './sets.js'; import { CAST } from './cast.js';
const set = SETS.studio({ w: 30, d: 10 }); const S = story({ set, pov: { phone: false }, vignette: 0.1, shake: 0 });
const L = [['mira', CAST.mira()], ['elias', CAST.elias({ hood: true, hair: 'short' })], ['elias2', CAST.elias()], ['offizier', CAST.offizier()], ['soldat', CAST.soldat()]];
L.forEach(([n, f], i) => S.cast(n, f, { at: [-2 + i, -1.0, 0], pose: 'stand', face: 'neutral' }));
S.hold(0.5, { look: [0, 1.0, -1.0], zoom: 62, pov: [0, 1.3, 4.2], cut: true });
L.forEach(([n, f], i) => S.hold(0.5, { look: [-2 + i, 1.5 * f.P.height, -1.0], zoom: 30, pov: [-2 + i + 0.5, 1.55 * f.P.height, 0.4], cut: true }));
S.start();
