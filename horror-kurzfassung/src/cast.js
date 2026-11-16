// The recurring characters of both stories as toon figures in the kit's hand-inked cartoon look (round heads, big eyes,
// thick outlines). Each call builds a new figure (a doppelganger is just a second call).
import { makeToon } from './toon.js';
export const CAST = {
  // DER ZUG OHNE MORGEN (1944)
  paul:      o => makeToon({ skin: 'light', height: 0.9, hair: 'swoop', hairColor: '#6a4024', top: '#4f8f3e', topStyle: 'jacket', inner: '#d9d2bf', bottom: '#3a3550', shoe: '#2a1f1c', brows: true, seed: 3, ...o }),
  emil:      o => makeToon({ skin: 'tan', height: 0.92, hair: 'beanie', hairColor: '#7a5030', top: '#3d4a7a', topStyle: 'sweater', bottom: '#2b2a3c', shoe: '#1e1a1a', seed: 5, ...o }),
  lena:      o => makeToon({ skin: 'fair', height: 0.88, hair: 'pigtails', hairColor: '#9a4f2a', top: '#8a8c98', topStyle: 'coat', bottom: '#3a3446', shoe: '#2a2020', scarf: '#b0443c', seed: 8, ...o }),
  schaffner: o => makeToon({ skin: '#ddd3cb', height: 1.06, hair: 'short', hairColor: '#8a8a96', top: '#232a46', topStyle: 'uniform', inner: '#b8b4a4', bottom: '#1c2036', shoe: '#101220', hat: '#1d2238', eye: 0.056, seed: 21, ...o }),
  // DIE STADT HINTER DER SPERRE (today)
  ben:       o => makeToon({ skin: 'light', height: 0.95, hair: 'spiky', hairColor: '#3a2618', top: '#2f5fb8', topStyle: 'jacket', inner: '#e8e8ee', bottom: '#2a2f45', shoe: '#e6e6ea', seed: 11, ...o }),
  nina:      o => makeToon({ skin: 'tan', height: 0.9, hair: 'long', hairColor: '#2a1a14', top: '#c23a3a', topStyle: 'sweater', bottom: '#2c3550', shoe: '#f0f0f2', seed: 13, ...o }),
  max:       o => makeToon({ skin: 'brown', height: 0.9, hair: 'curly', hairColor: '#1a1210', top: '#3f8f4f', topStyle: 'hoodie', bottom: '#33333f', shoe: '#2a2a33', seed: 17, ...o }),
};
