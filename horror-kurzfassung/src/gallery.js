// Character, hair and pose gallery (not part of a video):  STORY=gallery NOTIMINGS=1 node tools/snap.mjs beats
import { story } from './core.js'; import { makeToon, POSES } from './toon.js'; import { SETS } from './sets.js';
const set = SETS.studio({ w: 80, d: 10 }); const S = story({ set, pov: { phone: false }, vignette: 0.15, shake: 0 });
const hairs = ['short', 'bun', 'curly', 'afro', 'long', 'bob', 'ponytail', 'pigtails', 'spiky', 'swoop', 'beanie', 'buzz', 'bald'], tops = ['sweater', 'hoodie', 'tee', 'jacket', 'stripe', 'dress'];
const cols = ['#d7a31f', '#e8742c', '#3fa98a', '#4a63e0', '#a86be0', '#d8423c', '#5fb8a6'], skins = ['pale', 'light', 'tan', 'brown', 'deep', 'fair'];
hairs.forEach((h, i) => S.cast('h' + i, makeToon({ hair: h, hairColor: ['#3a2a22', '#c0562c', '#e8c25a', '#15131c', '#5b4a8a'][i % 5], top: cols[i % 7], topStyle: tops[i % 6], skin: skins[i % 6], glasses: i % 3 === 0, seed: i + 1 }), { at: [-30 + i * 0.85, -1.5, i % 2 ? 28 : -22], pose: 'stand', look: i % 2 ? null : 'pov', face: ['neutral', 'scared', 'shock', 'worried', 'angry', 'sad', 'smile', 'grin', 'sus'][i % 9] }));
const names = Object.keys(POSES); names.forEach((p, i) => S.cast('p' + i, makeToon({ hair: 'short', top: cols[i % 7], seed: i + 3 }), { at: [10 + i * 1.1, -1.5, i % 2 ? 32 : -32], pose: ['shh', 'gasp', 'phone', 'wave'].includes(p) ? 'stand+' + p : p }));
for (let k = 0; k < 4; k++) S.hold(0.5, { look: [-28.8 + k * 3.0, 1.15, -1.5], zoom: 64, pov: [-28.8 + k * 3.0, 1.35, 1.0], cut: true });
for (let k = 0; k < 6; k++) S.hold(0.5, { look: [11.6 + k * 3.3, 0.75, -1.5], zoom: 64, pov: [11.6 + k * 3.3, 1.2, 1.3], cut: true });
S.start();
