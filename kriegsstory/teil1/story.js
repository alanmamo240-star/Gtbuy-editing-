// Kriegsstory "Flucht und Schulzeit" — Teil 1 von 4. Bei Luftalarm bleibt die Kellertür zu. Heute hört es nicht auf.
import { story } from './core.js';
import { makeToon } from './toon.js';
import { SETS } from './sets.js';

// 1. places -------------------------------------------------------------------------------------------------
// the school basement class: no windows, a loudspeaker on the front wall (left of the door)
const room = SETS.classroom({ board: 'LUFTALARM', boardLines: ['ALLE IN DEN', 'KELLER'], sign: 'AUSGANG', window: false,
  poster: ['SCHUTZRAUM', ['1 RUNTER', '2 TÜR ZU', '3 LEISE']], targets: { speaker: [-1.3, 2.3, -4.5] } });
// home: little sister Lina's room, seen low from behind the bed
const home = SETS.bedroom({ posterTitle: 'LINAS', posterLines: ['ZIMMER', 'KLOPFEN!'], mood: 'night', pov: [1.4, 0.55, 2.3], targets: { lina: [-0.2, 0.45, -1.2] } });

// 2. people ------------------------------------------------------------------------------------------------------
const S = story({
  set: room,
  badge: { title: 'TEIL 1', label: 'Die Regel:', value: 'TÜR BLEIBT ZU' },
  speakers: {
    you:     { color: '#ffffff', voice: 'Liam' },
    teacher: { color: '#ffd84a', voice: 'Sarah' },
    friend:  { color: '#7fe3ff', voice: 'Harry' },
    radio:   { color: '#ff9ad0', voice: 'Paul', fx: 'radio' },      // the school loudspeaker
    home:    { color: '#d0d4ee', voice: 'Paul', fx: 'far' },        // the same announcement, on the radio at home
  },
  pov: { name: 'Mika', top: '#2b356f', phone: true },
  phone: { name: 'Mama', color: '#ff5c8d', clock: '14:12', history: [{ text: 'mika alles ok??' }, { me: true, text: 'sind im keller. alles gut' }, { text: 'bleib unten. ich liebe dich' }] },
  vars: { feet: 0, pulse: 1, spill: 1 },
  target: 90,
});

S.cast('teacher', makeToon({ skin: 'fair', hair: 'bun', hairColor: '#6b4a3a', top: '#3fa98a', bottom: '#2a2f5e', collar: '#f1f1f6', glasses: true, seed: 2 }), { at: [1.62, 0.25, 176], pose: 'kneelUp', look: 'door', face: 'worried' });
S.cast('friend', makeToon({ skin: 'light', hair: 'swoop', hairColor: '#3a2a20', top: '#e8742c', topStyle: 'hoodie', bottom: '#2f3a78', eye: 0.07, height: 0.92, seed: 5 }), { at: [4.15, 3.0, -112], pose: 'sitHug', face: 'scared', tremble: 0.5, look: 'door' });
S.cast('kid1', makeToon({ skin: 'tan', hair: 'short', hairColor: '#d9b45a', top: '#5fb8a6', height: 0.84, seed: 7 }), { at: [-0.95, -2.9, 168], pose: 'crouch', look: 'door' });
S.cast('kid2', makeToon({ skin: 'brown', hair: 'buzz', hairColor: '#15131c', top: '#a86be0', height: 0.82, seed: 8 }), { at: [-0.5, -3.75, 150], pose: 'cower' });
S.cast('kid3', makeToon({ skin: 'light', hair: 'ponytail', hairColor: '#5a3424', top: '#4a63e0', height: 0.86, seed: 9 }), { at: [1.45, -3.5, 205], pose: 'kneel', look: 'door' });
S.cast('lina', makeToon({ skin: 'light', hair: 'pigtails', hairColor: '#3a2a20', top: '#ff7aa8', height: 0.78, eye: 0.075, seed: 11 }), { set: home, at: [-0.2, -1.2, 20], pose: 'kneel', face: 'scared', tremble: 0.6, look: 'door' });

// 3. beats ------------------------------------------------------------------------------------------------------
// an explosion somewhere outside: sub boom + a creak of the building, the light under the door jumps (flash), the next beat lets it settle (calm)
const boom = (t, g = 0.75) => [['boom', t, g], ['creak', t + 0.25, 0.4]];
const flash = at => ({ spill: [2.4, 0.06, at] });
const calm = (at = 0) => ({ spill: [1, 0.7, at] });

S.say('you', 'Bei Luftalarm | bleibt die Kellertür zu.', { look: 'door', zoom: 'tight', push: 0.02 });
S.say('you', 'Heute | hört es nicht auf.', { zoom: 'medium', sfx: boom(-0.45), vars: flash(-0.4) });
S.say('teacher', 'Alle runter. | Köpfe unten.', { look: 'teacher', zoom: 'wide', vars: calm(), do: { teacher: { face: 'angry' } } });
S.say('radio', 'Achtung. | Luftalarm. | Bleiben Sie | im Schutzraum.', { look: 'speaker', zoom: 34, punch: { at: 'p1', zoom: 26 }, do: { teacher: { face: 'worried' } } });
S.say('teacher', 'Kein Wort.', { look: 'teacher', zoom: 'wide', do: { teacher: { pose: 'kneelUp+shh' } } });
S.hold(1.0, { look: 'door', zoom: 'medium', sfx: boom(0.3, 0.6), vars: flash(0.3), do: { teacher: { pose: 'kneelUp' } } });
S.say('radio', 'Der letzte Zug | fährt um fünfzehn Uhr.', { look: 'speaker', zoom: 34, vars: calm() });
S.say('you', 'Mama wollte | heute mit uns | weg.', { look: 'door', zoom: 'medium' });
S.say('friend', 'Warte... | die Sirene | ist aus.', { look: 'friend', zoom: 'auto', do: { friend: [{ look: 'door', face: 'scared' }, { t: 'p1', face: 'shock' }] } });
S.say('friend', 'Aber es knallt | immer noch.', { punch: { at: 0, zoom: 30 } });
S.say('you', 'Unter der Tür...', { look: 'doorGap', zoom: 30, push: 0.03 });
S.say('you', 'Ein Blitz.', { gap: 0.3, sfx: boom(-0.35, 0.6), vars: flash(-0.3) });
S.hold(1.1, { sfx: [['heartbeat', 0.1, 0.6], ...boom(0.55, 0.85)], vars: { spill: [3, 0.06, 0.55] }, punch: { at: 0.55, zoom: 24 } });
S.say('you', 'Noch einer. | Näher.', { vars: calm(0.2) });
S.say('friend', 'Das ist | beim Bahnhof.', { look: 'friend', zoom: 'auto', do: { friend: { face: 'shock', tremble: 1 } } });
S.hold(1.7, { look: 'door', zoom: 'tight', vars: { spill: [0.5, 1.2, 0.2] }, sfx: [['boom', 0.2, 0.3]] });
S.say('friend', 'Es wird leiser.', { look: 'friend', zoom: 'auto', do: { friend: { face: 'scared', tremble: 0.4 } } });
S.say('you', 'Mama und Lina | sind noch zuhause.', { look: 'door', zoom: 'medium', push: 0.03 });
S.say('teacher', 'Unten bleiben. | Das ist nicht vorbei.', { look: 'teacher', zoom: 'wide', vars: calm() });
// cutaway: the same announcement, on the radio at home
S.hold(0.9, { set: home, look: 'door', zoom: 'wide', aim: [-6, 4] });
S.say('home', 'Achtung. | Luftalarm.', { tag: 'ZUHAUSE' });
S.say('home', 'Der letzte Zug | fährt um fünfzehn Uhr.', { tag: 'ZUHAUSE', look: 'lina', zoom: 'medium', camAt: 0.1 });
// back in the basement: the phone
S.phone({ set: room, look: 'friend', turn: -30, events: [
  { in: 'mika wir müssen weg', hold: 1.4 },
  { in: 'letzter zug um drei. lina packt schon', hold: 1.6 },
  { in: 'bleib wo du bist.', hot: 'ich hol dich jetzt ab', hold: 1.6 },
  { type: 'MAMA NEIN!! BLEIB BEI LINA', hold: 1.0 } ] });
S.say('you', 'Sie läuft | mitten durch die Stadt.', { look: 'teacher', zoom: 'close', camAt: 0.45, do: { teacher: { at: [1.62, 0.25, 30], look: 'pov', face: 'worried', dur: 0.4 } } });
S.say('friend', 'Mika... | der Bahnhof | liegt auf ihrem Weg.', { look: 'friend', zoom: 'auto', do: { friend: { look: 'pov', face: 'shock' } } });
S.say('teacher', 'Setz dich. | Sie schafft das.', { look: 'teacher', zoom: 'close', do: { teacher: { face: 'worried' } } });
S.say('you', 'Fünfzehn Uhr... | das ist in | vierzig Minuten.', { look: 'door', zoom: 'medium', push: 0.03 });
S.hold(1.2, { set: home, look: 'lina', zoom: 'medium', sfx: boom(0.2, 0.7) });
S.say('home', 'Bleiben Sie | im Schutzraum!', { tag: 'ZUHAUSE' });
S.say('you', 'Ich muss zu ihr!', { set: room, look: 'teacher', pov: [1.5, 1.5, 2.0], povDur: 0.9, zoom: 'wide', do: { teacher: { pose: 'stop', at: [1.55, 0.75, 8], face: 'angry', dur: 0.8 } } });
S.say('teacher', 'Mika, stopp! | Wer die Tür aufmacht, | bringt uns alle | in Gefahr.', { zoom: 'close', sfx: boom(1.2, 0.5) });
S.say('friend', 'Und wenn nicht... | ist deine Mama | allein da draußen.', { look: 'friend', zoom: 'wide', aim: [0, -6] });
S.hold(0.9, { look: 'teacher', zoom: 'close', push: 0.09, camAt: -0.25 });
S.choice({ question: 'WAS WÜRDEST\nDU TUN?', a: { text: 'ZU MAMA RENNEN', color: 'green', icon: 'run' }, b: { text: 'IM KELLER BLEIBEN', color: 'red', icon: 'lock' }, footer: ['Kommentiere für', 'Teil 2'] });
S.start();
