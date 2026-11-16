// Engine: timeline of beats -> first-person camera (whip pans, zooms, handheld), character direction, ink outlines,
// fisheye + motion blur post, captions / phone / choice card. Every frame is a pure function of time: renderAt(t).
import { THREE, clamp, lerp, smooth, easeIO, easeOut, rad, noise, toon, flat, rbox, sph, limb, grp, at, noOutline } from './util.js';
import { makeToon, getPose } from './toon.js';
import * as U from './ui.js';

export const FPS = 30;
// vertical field of view per zoom name (degrees). The lens is a wide phone-style lens: wide shots bend straight lines.
export const ZOOM = { tight: 44, medium: 60, close: 76, wide: 96, phone: 58 };
const WHIP = 0.3, ZOOMT = 0.33, PUNCH = 0.13;   // 9-frame whip pan, 10-frame zoom, 4-frame punch-in (measured)
const q = new URLSearchParams(location.search);
const W = 1080, H = 1920, SCALE = parseFloat(q.get('scale') || '1'), SS = parseFloat(q.get('ss') || '1.25');

// ------------------------------------------------------------------ renderer + passes
const out = document.getElementById('c'); out.width = Math.round(W * SCALE); out.height = Math.round(H * SCALE); const ctx = out.getContext('2d');
const glc = document.createElement('canvas');
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: false, preserveDrawingBuffer: true }); renderer.setPixelRatio(1); renderer.setSize(out.width, out.height, false);
renderer.outputColorSpace = THREE.LinearSRGBColorSpace; renderer.setClearColor(0x05061a, 1);
const RW = Math.round(out.width * SS), RH = Math.round(out.height * SS);
const mkRT = () => new THREE.WebGLRenderTarget(RW, RH, { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: true });
const rtColor = mkRT(), rtInk = mkRT(), rtA = mkRT(), rtB = mkRT(); rtInk.texture.minFilter = rtInk.texture.magFilter = THREE.NearestFilter;
const camera = new THREE.PerspectiveCamera(60, W / H, 0.08, 80); camera.rotation.order = 'YXZ';
const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2)); const qscene = new THREE.Scene(); qscene.add(quad); const qcam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const VS = 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }';
const inkBase = new THREE.ShaderMaterial({
  uniforms: { uId: { value: 0 }, uFlat: { value: 0 } }, blending: THREE.NoBlending,
  vertexShader: 'varying vec3 vN; varying float vD; void main(){ vN = normalize(normalMatrix * normal); vec4 mv = modelViewMatrix * vec4(position, 1.); vD = -mv.z; gl_Position = projectionMatrix * mv; }',
  fragmentShader: 'uniform float uId, uFlat; varying vec3 vN; varying float vD; void main(){ vec3 n = normalize(vN); if(!gl_FrontFacing) n = -n; if(uFlat > .5) n = vec3(0., 0., 1.); gl_FragColor = vec4(n.xy * .5 + .5, clamp(vD / 24., 0., 1.), uId); }',
});
const edgeMat = new THREE.ShaderMaterial({
  uniforms: { tC: { value: null }, tI: { value: null }, px: { value: new THREE.Vector2(1 / RW, 1 / RH) }, uW: { value: 2.3 * SS * SCALE }, uInk: { value: new THREE.Color('#0a0c26') } }, vertexShader: VS, depthTest: false,
  fragmentShader: `uniform sampler2D tC, tI; uniform vec2 px; uniform float uW; uniform vec3 uInk; varying vec2 vUv;
    float edge(vec4 c, float r){ float e = 0.; for(int i = 0; i < 8; i++){ float a = float(i) * 0.7853982; vec4 s = texture2D(tI, vUv + vec2(cos(a), sin(a)) * r * px);
      e = max(e, max(step(0.0015, abs(s.a - c.a)), step(0.5, length(s.rg - c.rg)))); } return e; }
    void main(){ vec4 c = texture2D(tI, vUv); float d = c.b * 24.; float r = uW * clamp(2.4 / max(d, 0.3), 0.42, 1.25);
      float e = 0.62 * edge(c, r) + 0.38 * edge(c, r * 0.5); vec3 col = texture2D(tC, vUv).rgb; gl_FragColor = vec4(mix(col, uInk, e * 0.93), 1.); }`,
});
const finalMat = new THREE.ShaderMaterial({
  uniforms: { tA: { value: null }, tB: { value: null }, uMix: { value: 0 }, uK: { value: 0.2 }, uAsp: { value: W / H }, uVig: { value: 0.75 }, uBlack: { value: 0 }, uBlur: { value: new THREE.Vector2() }, uZoomBlur: { value: 0 } }, vertexShader: VS, depthTest: false,
  fragmentShader: `uniform sampler2D tA, tB; uniform float uMix, uK, uAsp, uVig, uBlack, uZoomBlur; uniform vec2 uBlur; varying vec2 vUv;
    vec2 lens(vec2 uv){ vec2 p = uv * 2. - 1.; vec2 w = vec2(p.x * uAsp, p.y); float r2 = dot(w, w) / (1. + uAsp * uAsp); return p * (1. + uK * r2) / (1. + uK) * .5 + .5; }
    vec3 samp(vec2 uv){ vec2 d = lens(uv); vec3 a = texture2D(tA, d).rgb; if(uMix > 0.) a = mix(a, texture2D(tB, d).rgb, uMix); return a; }
    void main(){ vec3 c = vec3(0.); float amt = length(uBlur) + abs(uZoomBlur);
      if(amt > 0.0008){ for(int i = 0; i < 16; i++){ float f = float(i) / 15. - .5; vec2 uv = vUv + uBlur * f; uv = (uv - .5) * (1. + uZoomBlur * f) + .5; c += samp(uv); } c /= 16.; } else c = samp(vUv);
      vec2 p = vUv * 2. - 1.; float v = smoothstep(1.42, 0.38, length(p * vec2(0.82, 1.))); c *= mix(1., v, uVig); gl_FragColor = vec4(c * (1. - uBlack), 1.); }`,
});
let inkId = 1; const inkGroups = new Map();
function inkOf(m) {
  if (m.userData.ink) return m.userData.ink; const im = inkBase.clone(); let id = m.userData.inkGroup ? (inkGroups.get(m.userData.inkGroup) ?? inkGroups.set(m.userData.inkGroup, inkId++).get(m.userData.inkGroup)) : inkId++;
  im.uniforms.uId.value = ((id * 37) % 251 + 3) / 255; im.uniforms.uFlat.value = m.userData.inkFlat ? 1 : 0; im.side = m.material.side; m.userData.ink = im; return im;
}
const swapped = [];
function renderSet(set, target) {
  renderer.setRenderTarget(rtColor); renderer.setClearColor(set.bg ?? 0x05061a, 1); renderer.clear(); renderer.render(set.scene, camera);
  swapped.length = 0;
  set.scene.traverseVisible(m => { if (!m.isMesh) return; if (m.userData.noOutline) { m.visible = false; swapped.push([m, null]); } else { swapped.push([m, m.material]); m.material = inkOf(m); } });
  renderer.setRenderTarget(rtInk); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(set.scene, camera);
  for (const [m, mat] of swapped) { if (mat) m.material = mat; else m.visible = true; }
  edgeMat.uniforms.tC.value = rtColor.texture; edgeMat.uniforms.tI.value = rtInk.texture; quad.material = edgeMat; renderer.setRenderTarget(target); renderer.render(qscene, qcam);
}

// ------------------------------------------------------------------ first-person rig: the hand holding the phone
function makePhoneRig(pov = {}) {
  const skin = toon(pov.skin || '#e9b999'), g = new THREE.Group(), body = rbox(0.078, 0.162, 0.011, 0.01, toon('#11131d'));
  const sc = document.createElement('canvas'); sc.width = 400; sc.height = 846; const sx = sc.getContext('2d'); const tex = new THREE.CanvasTexture(sc); tex.colorSpace = THREE.NoColorSpace; tex.anisotropy = 8;
  const screen = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(0.0715, 0.1512), new THREE.MeshBasicMaterial({ map: tex }))); screen.position.z = 0.0062;
  g.add(body, screen);
  g.add(at(sph(0.04, skin), [0.008, -0.045, -0.03], null, [1.15, 1.4, 0.5]));                             // palm behind the phone
  for (let i = 0; i < 4; i++) g.add(at(sph(0.0135, skin), [0.0415, 0.03 - i * 0.026, 0.001], null, [1.2, 0.86, 1]));   // fingers wrapping the right edge
  g.add(at(sph(0.016, skin), [-0.041, -0.04, 0.003], null, [0.85, 2.0, 0.85]));                              // thumb on the left edge
  const arm = limb(0.045, 0.5, toon(pov.top || '#2b356f')); at(arm, [0.02, -0.085, -0.03], [0.25, 0, 0.1]); g.add(arm);
  return { g, sx, tex, sw: 400, sh: 846 };
}

// ------------------------------------------------------------------ story
export function story(cfg = {}) {
  const S = { cfg, beats: [], chars: {}, targets: {}, vars: {}, sets: [], speakers: cfg.speakers || {} };
  const phone = makePhoneRig(cfg.pov); camera.add(phone.g);
  const povBody = makeToon({ top: cfg.pov?.top || '#2b356f', bottom: cfg.pov?.bottom || '#232a5c', skin: cfg.pov?.skin || 'light', shoe: cfg.pov?.shoe || '#14162c' }); povBody.head.visible = false; povBody.handL.parent.parent.visible = false; povBody.handR.parent.parent.visible = false;
  let startSet = cfg.set;

  // a character and its "home" state
  S.cast = (name, av, home = {}) => { const set = home.set || startSet; set.scene.add(av.root); S.chars[name] = { name, av, set, home: { at: [0, 0, 0], y: 0, pose: 'stand', look: null, face: 'neutral', tremble: 0, hide: false, scale: av.P.height, ...home }, keys: [] }; if (S.speakers[name] && !S.speakers[name].av) S.speakers[name].av = name; return av; };
  S.target = (name, p) => { S.targets[name] = p; };
  const add = b => { b.i = S.beats.length; S.beats.push(b); return b; };
  // spoken line. '|' splits the caption into phrases of 1-5 words.
  S.say = (who, text, o = {}) => add({ type: 'say', who, text, ...o });
  S.hold = (dur, o = {}) => add({ type: 'hold', dur, ...o });                    // silence: let the picture and the sound do the work
  S.phone = (o = {}) => add({ type: 'phone', ...o });                             // raise the phone: incoming texts, typing a reply
  S.choice = (o = {}) => add({ type: 'choice', ...o });                           // "WHAT WOULD YOU DO?" end card
  S.start = () => boot(S, phone, povBody);
  return S;
}

const words = s => s.replace(/\|/g, ' ').split(/\s+/).filter(Boolean);
const estPhrase = p => 0.22 + 0.3 * words(p).length;   // calibrated on real Nixly voices at the kit's tempo
const wrapPi = a => { a = (a + Math.PI) % (2 * Math.PI); if (a < 0) a += 2 * Math.PI; return a - Math.PI; };

async function boot(S, phone, povBody) {
  let timings = null; try { const r = await fetch('timings.json?' + Date.now()); if (r.ok) timings = await r.json(); } catch (e) {}
  if (q.has('notimings')) timings = null;
  await Promise.all([500, 600, 700, 800, 900].map(w => document.fonts.load(`${w} 40px Rubik`)));
  const B = S.beats, cfg = S.cfg; let t = cfg.lead ?? 0.1, prev = null, sayN = 0;
  let cur = { set: cfg.set, look: cfg.look || [0, 1.2, -10], zoom: 'medium' };
  for (const b of B) {
    b.set ||= cur.set; b.setChanged = prev && b.set !== cur.set; if (b.setChanged || !prev) b.povPos = b.pov || b.set.pov || [0, 1.5, 3]; else b.povPos = b.pov || prev.povPos;
    if (b.type === 'phone') { b.look = b.look ?? cur.look; if (!b.low) { b.zoom = b.zoom ?? 'phone'; b.isPhone = true; } }   // low: the phone stays in your hand at the bottom, the scene goes on
    if (b.type === 'choice') { b.look = cur.look; b.zoom = cur.zoom; }
    b.look = b.look ?? (b.setChanged ? (b.set.look || [0, 1.2, -10]) : cur.look); b.zoom = b.zoom ?? cur.zoom;
    b.camChanged = !prev || b.setChanged || b.look !== cur.look || b.zoom !== cur.zoom || b.isPhone !== !!prev.isPhone || (b.pov && b.pov !== prev.povPos);
    const speakerChange = prev && prev.type === 'say' && b.type === 'say' && prev.who !== b.who;
    b.gap = b.gap ?? (!prev ? 0.05 : b.type === 'choice' ? 0.25 : b.type === 'hold' ? 0.1 : b.type === 'phone' ? 0.2 : (speakerChange || b.camChanged) ? 0.28 : 0.14);
    t += b.gap; b.t0 = t;
    if (b.type === 'say') {
      b.phrases = b.text.split('|').map(s => s.trim()).filter(Boolean); b.n = sayN++; const tm = timings?.lines?.[b.n]; let k = 0;
      if (tm && tm.words && tm.words.length === words(b.text).length) { b.ps = b.phrases.map(p => { const s = tm.words[k][0]; k += words(p).length; return k === words(p).length ? 0 : s; }); b.dur = tm.dur; b.env = tm.env; b.voiced = true; }
      else { let a = 0; b.ps = b.phrases.map(p => { const s = a; a += estPhrase(p); return s; }); b.dur = a - 0.2; }
    } else if (b.type === 'phone') {
      // sub-events: raise (0.4 s) then each incoming / typed message
      let a = 0.45; b.ev = (b.events || []).map(e => { const o = { ...e, t: a }; if (e.type != null) { o.typeDur = e.type.length / 27; o.sent = a + 0.25 + o.typeDur + 0.17; a = o.sent + (e.hold ?? 1.1); } else a += (e.hold ?? 1.5); return o; }); b.dur = a;
    } else if (b.type === 'choice') b.dur = b.dur ?? 3.6;
    b.t1 = b.t0 + b.dur; t = b.t1; b.camAtT = b.t0 + (b.camAt ?? (b.type === 'say' ? -0.1 : 0)); if (!prev) b.camAtT = -1;
    cur = { set: b.set, look: b.look, zoom: b.zoom }; prev = b;
  }
  // target length: stretch or squeeze the silences between lines (never the lines themselves) to land on cfg.target seconds
  let pace = 1; if (cfg.target) { const flex = B.slice(1).reduce((a, b) => a + b.gap, 0), fixed = t - flex; pace = clamp((cfg.target - (cfg.tail ?? 0.05) - fixed) / Math.max(0.01, flex), 0.55, 3);
    t = cfg.lead ?? 0.1; B.forEach((b, i) => { if (i) b.gap *= pace; t += b.gap; b.t0 = t; b.t1 = t + b.dur; t = b.t1; b.camAtT = i ? b.t0 + (b.camAt ?? (b.type === 'say' ? -0.1 : 0)) : -1; }); }
  const DUR = t + (cfg.tail ?? 0.05); S.duration = DUR;
  const sayBeats = B.filter(b => b.type === 'say'), camBeats = B.filter(b => b.camChanged);
  // caption intervals
  const caps = []; for (const b of sayBeats) b.phrases.forEach((p, k) => caps.push({ b, k, text: p, s: b.t0 + b.ps[k], e: k + 1 < b.phrases.length ? b.t0 + b.ps[k + 1] : b.t1 + 0.16 }));
  caps.forEach((c, i) => { if (caps[i + 1]) c.e = Math.min(c.e, caps[i + 1].s); });
  // character keys from beat.do; vars from beat.vars
  const when = (b, v) => v == null ? b.camAtT + 0.02 : typeof v === 'string' ? b.t0 + b.ps[parseInt(v.slice(1))] : b.t0 + v;
  for (const b of B) {
    for (const [n, d] of Object.entries(b.do || {})) { const c = S.chars[n]; if (!c) throw new Error('do: unknown character ' + n); for (const k of [].concat(d)) c.keys.push({ t: Math.max(0, when(b, k.t)), dur: k.dur ?? 0.35, st: k }); }
    for (const [n, v] of Object.entries(b.vars || {})) { const [val, dur, off] = [].concat(v); (S.vars[n] ||= []).push({ t: Math.max(0, when(b, off)), dur: dur ?? 0.4, val }); }
  }
  Object.values(S.chars).forEach(c => c.keys.sort((a, b) => a.t - b.t));
  const varAt = (n, t, def) => { let v = (S.cfg.vars || {})[n] ?? def; for (const k of S.vars[n] || []) { if (k.t > t) break; v = lerp(v, k.val, k.dur > 0 ? smooth((t - k.t) / k.dur) : 1); } return v; };
  const allVars = t => { const o = { ...(S.cfg.vars || {}) }; for (const n in S.vars) o[n] = varAt(n, t, 0); return o; };

  // ---- characters
  const charState = (c, t) => {
    const h = c.home; let st = { x: h.at[0], z: h.at[1], ry: h.at[2] || 0, y: h.y, pose: getPose(h.pose), look: h.look, lookAmt: h.look ? 1 : 0, lookPt: null, face: h.face, tremble: h.tremble, hide: h.hide, scale: h.scale, walk: 0 };
    st.lookPt = st.look ? resolvePt(st.look, t, c) : [0, 0, 0];
    for (const k of c.keys) { if (k.t > t) break; const w = k.dur > 0 ? easeIO((t - k.t) / k.dur) : 1, s = k.st;
      if (s.at) { const moving = w < 1 && (Math.hypot(s.at[0] - st.x, s.at[1] - st.z) > 0.3); st.x = lerp(st.x, s.at[0], w); st.z = lerp(st.z, s.at[1], w); if (s.at[2] != null) st.ry = st.ry + wrapPi(rad(s.at[2] - st.ry)) * 180 / Math.PI * w; if (moving && s.walk !== false) st.walk = 1; }
      if (s.y != null) st.y = lerp(st.y, s.y, w); if (s.scale != null) st.scale = lerp(st.scale, s.scale, w);
      if (s.pose) { const p = getPose(s.pose), o = {}; for (const kk in p) { const a = st.pose[kk], bb = p[kk]; o[kk] = Array.isArray(a) ? a.map((v, i) => lerp(v, bb[i], w)) : lerp(a, bb, w); } st.pose = o; }
      if (s.look !== undefined) { const amt = s.look ? 1 : 0; if (s.look) { const p = resolvePt(s.look, t, c); st.lookPt = st.lookAmt > 0 ? st.lookPt.map((v, i) => lerp(v, p[i], w)) : p; } st.lookAmt = lerp(st.lookAmt, amt, w); }
      if (s.face && w > 0.4) st.face = s.face; if (s.tremble != null) st.tremble = lerp(st.tremble, s.tremble, w); if (s.hide != null && w > 0.5) st.hide = s.hide;
    }
    return st;
  };
  const headPt = (c, t) => { const s = charState(c, t); return [s.x, s.y + (s.pose.hipY + 0.74) * s.scale, s.z]; };
  function resolvePt(v, t, self, set) { if (Array.isArray(v)) return v; if (v === 'pov') return povAt(t); if (S.chars[v] && S.chars[v] !== self) return headPt(S.chars[v], t); const p = S.targets[v] ?? set?.targets?.[v] ?? self?.set.targets?.[v] ?? S.cfg.set.targets?.[v]; if (!p) throw new Error('unknown target ' + v); return typeof p === 'function' ? p(t) : p; }
  const speaking = (name, t) => { let best = null; for (const b of sayBeats) { if (S.speakers[b.who]?.av !== name || b.autoLook === false) continue; const a = smooth((t - (b.t0 - 0.28)) / 0.3) * (1 - smooth((t - (b.t1 + 0.1)) / 0.35)); if (a > 0 && (!best || a > best.a)) best = { a, b }; } return best; };
  function poseChar(c, t, visibleSet) {
    const av = c.av; if (c.set !== visibleSet) return; const s = charState(c, t); if (s.hide) { av.hide(); return; }
    av.reset().size(s.scale); let ry = s.ry; const sp = speaking(c.name, t), pov = povAt(t);
    let lookPt = s.lookPt, lookAmt = s.lookAmt;
    if (sp) { const rel = wrapPi(Math.atan2(pov[0] - s.x, pov[2] - s.z) - rad(ry)); if (Math.abs(rel) > rad(60)) ry += Math.sign(rel) * (Math.abs(rel) - rad(42)) * 180 / Math.PI * sp.a; lookPt = lookAmt > 0 ? lookPt.map((v, i) => lerp(v, pov[i], sp.a)) : pov; lookAmt = Math.max(lookAmt, sp.a); }
    av.place(s.x, s.z, ry, s.y).pose(s.pose).face(s.face); if (s.walk) av.walk(t);
    if (lookAmt > 0.01) av.lookAt(lookPt, lookAmt);
    av.idle(t, s.tremble);
    const line = sayBeats.find(b => S.speakers[b.who]?.av === c.name && t >= b.t0 && t <= b.t1 + 0.03);
    if (line) { const e = line.env ? line.env[Math.min(line.env.length - 1, Math.floor((t - line.t0) * FPS))] : null; av.talk(t, e); }
  }

  // ---- camera
  function povAt(t) { const ov = cfg.povPath?.(t); if (ov) return ov; let i = 0; for (let k = 0; k < B.length; k++) if (B[k].camAtT <= t) i = k; else break; const b = B[i]; let j = i; while (j > 0 && B[j].povPos === B[j - 1].povPos && !B[j].setChanged) j--;
    if (j === 0 || B[j].setChanged) return b.povPos; const u = B[j].cut ? 1 : easeIO((t - B[j].camAtT) / (B[j].povDur ?? 0.9)); return B[j - 1].povPos.map((v, k) => lerp(v, b.povPos[k], u)); }
  S.povAt = povAt;   // cfg.povPath(t) -> [x, y, z] or null overrides the camera position (running along a path)
  const zoomDeg = z => typeof z === 'number' ? z : ZOOM[z] ?? 60;
  function aimOf(b, t, fixedPos) {   // yaw, pitch, fov of a beat's own framing at time t
    const pos = fixedPos || povAt(t); let pt = resolvePt(b.look, t, null, b.set), isChar = typeof b.look === 'string' && S.chars[b.look];
    let fov = zoomDeg(b.zoom); if (b.zoom === 'auto') { const c = isChar ? charState(isChar, t) : null, span = c ? (c.pose.hipY + 0.92) * c.scale : 1.2; fov = clamp(2 * Math.atan(span / (1.04 * Math.hypot(pt[0] - pos[0], pt[2] - pos[2]))) * 180 / Math.PI, 30, 98); }
    for (const p of [].concat(b.punch || [])) { const tp = when(b, p.at ?? 0); if (t >= tp) fov = lerp(fov, zoomDeg(p.zoom), easeIO((t - tp) / (p.dur ?? PUNCH))); }
    const push = b.push ?? 0.012; fov *= Math.max(0.72, 1 - push * Math.max(0, t - b.camAtT));
    let yaw = Math.atan2(-(pt[0] - pos[0]), -(pt[2] - pos[2])), pitch = Math.atan2(pt[1] - pos[1], Math.hypot(pt[0] - pos[0], pt[2] - pos[2]));
    if (isChar) pitch -= rad(fov) * (b.headroom ?? 0.17);            // aim below the face: head in the upper third, caption on the chest
    if (b.isPhone) { pitch = rad(-50); yaw += rad(b.turn ?? 18); }
    if (b.aim) { yaw -= rad(b.aim[0]); pitch += rad(b.aim[1]); }
    return { yaw, pitch, fov, roll: rad(b.roll || 0), phone: b.isPhone ? 1 : 0 };
  }
  function camAt(t) {
    let i = 0; for (let k = 0; k < camBeats.length; k++) if (camBeats[k].camAtT <= t) i = k; else break;
    const b = camBeats[i], p = i > 0 ? camBeats[i - 1] : null, a = aimOf(b, t, b.setChanged ? b.povPos : null); let st = { ...a, set: b.set, setB: null, mix: 0, pos: povAt(t) };
    if (p && !b.cut) {
      const pa = aimOf(p, t, b.setChanged ? p.povPos : null), dy = wrapPi(a.yaw - pa.yaw), ang = Math.hypot(dy, a.pitch - pa.pitch);
      const dur = b.camDur ?? (b.setChanged ? 0.34 : (b.isPhone || p.isPhone) ? 0.4 : ang > rad(10) ? WHIP : ZOOMT), u = (t - b.camAtT) / dur;
      if (u < 1) { const e = easeIO(u);
        if (b.setChanged) { const dir = b.whipDir ?? -1, sw = rad(34); st = { ...a, yaw: a.yaw - dir * sw * (1 - e), set: p.set, setB: b.set, mix: smooth(u), pos: null, posA: p.povPos, posB: b.povPos, a: { ...pa, yaw: pa.yaw + dir * sw * e } }; }
        else st = { yaw: pa.yaw + dy * e, pitch: lerp(pa.pitch, a.pitch, e), fov: lerp(pa.fov, a.fov, e), roll: lerp(pa.roll, a.roll, e), phone: lerp(pa.phone, a.phone, e), set: b.set, setB: null, mix: 0, pos: povAt(t) }; }
    }
    return st;
  }
  const hand = (t, k = 1) => [rad(0.55) * k * (noise(t * 0.42, 1) + 0.35 * noise(t * 1.6, 2)), rad(0.45) * k * (noise(t * 0.37, 3) + 0.35 * noise(t * 1.9, 4)), rad(0.5) * k * noise(t * 0.3, 5)];
  function setCamera(pos, yaw, pitch, fov, roll, t, shake) {
    const [hy, hp, hr] = hand(t, shake); camera.position.set(pos[0] + 0.006 * noise(t * 0.5, 8), pos[1] + 0.008 * Math.sin(t * 1.7), pos[2]); camera.rotation.set(pitch + hp, yaw + hy, roll + hr);
    const k = clamp((fov - 40) / 60) * 0.3; camera.fov = 2 * Math.atan(Math.tan(rad(fov) / 2) * (1 + k * 0.55)) * 180 / Math.PI; camera.updateProjectionMatrix(); return k;
  }

  // ---- phone content + banner at time t
  const phoneBeats = B.filter(b => b.type === 'phone');
  function phoneAt(t) {
    const cfgP = cfg.phone || {}; let msgs = [...(cfgP.history || [])].map(m => ({ ...m, k: 1 })), banner = null, bk = 0, draft = '', delivered = 0;
    for (const b of phoneBeats) for (const e of b.ev) { const te = b.t0 + e.t; if (t < te) continue;
      if (e.type != null) { const n = Math.floor(clamp((t - te - 0.2) / e.typeDur) * e.type.length), ts = b.t0 + e.sent, sent = t >= ts; if (!sent) draft = e.type.slice(0, n);
        if (t < b.t1 + 0.35) { banner = { name: 'Du', letter: (cfg.pov?.name || 'Du')[0].toUpperCase(), color: '#7d9bff', text: sent ? e.type : e.type.slice(0, Math.max(1, n)), status: sent ? 'gesendet ✓' : 'schreibt …', statusColor: '#2f7bf6' }; bk = clamp((t - te) / 0.13); }
        if (sent) { msgs.push({ me: true, text: e.type, style: e.style, k: (t - ts) / 0.17 }); delivered = clamp((t - ts - 0.2) / 0.15); } else delivered = 0; }
      else { if (e.stamp) msgs.push({ stamp: e.stamp, k: 1 }); msgs.push({ me: false, text: e.in + (e.hot ? ' ' + e.hot : ''), style: e.style, k: (t - te - 0.03) / 0.17 }); delivered = 0;
        if (t < b.t1 + 0.35) { banner = { name: cfgP.name || 'Zoe', color: cfgP.color, text: e.in, hot: e.hot, alert: e.alert, status: cfgP.clock || '10:55', statusColor: '#e23b3b' }; bk = clamp((t - te) / 0.13); } }
    }
    const last = phoneBeats.filter(b => b.t0 <= t).pop(); if (last && t > last.t1) { const nb = camBeats.find(c => c.camAtT >= last.t1 - 0.01); const tOut = nb ? nb.camAtT : last.t1; bk *= 1 - clamp((t - tOut) / 0.12); }
    return { msgs, banner, bk, draft, delivered };
  }

  // ---- frame
  const P_LOW = { p: [0.185, -0.41, -0.36], r: [-0.62, -0.25, 0.5] }, P_UP = { p: [-0.011, -0.012, -0.212], r: [0.02, 0.13, -0.035] }, P_MID = { p: [0.07, -0.168, -0.33], r: [-0.42, -0.12, 0.1] };
  const lowBeats = B.filter(b => b.type === 'phone' && b.low), lowK = t => Math.max(0, ...lowBeats.map(b => easeIO(clamp((t - b.t0) / 0.35)) * easeIO(clamp((b.t1 + 0.35 - t) / 0.35))));
  const qa = new THREE.Quaternion(), qb = new THREE.Quaternion(), ea = new THREE.Euler();
  function drawSet(set, t, pos, st, target, vars) {
    for (const c of Object.values(S.chars)) poseChar(c, t, set);
    set.update?.(vars, t); set.scene.add(camera);
    const k = setCamera(pos, st.yaw, st.pitch, st.fov, st.roll, t, cfg.shake ?? 1);
    // phone in the hand
    const r = easeIO(st.phone); phone.g.visible = cfg.pov?.phone !== false && (varAt('phone', t, 1) > 0.5);
    const lk = lowK(t), PL = { p: P_LOW.p.map((v, i) => lerp(v, P_MID.p[i], lk)), r: P_LOW.r.map((v, i) => lerp(v, P_MID.r[i], lk)) };
    phone.g.position.set(lerp(PL.p[0], P_UP.p[0], r), lerp(PL.p[1], P_UP.p[1], r) + 0.004 * Math.sin(t * 1.3), lerp(PL.p[2], P_UP.p[2], r));
    qa.setFromEuler(ea.set(...PL.r)); qb.setFromEuler(ea.set(...P_UP.r)); phone.g.quaternion.slerpQuaternions(qa, qb, r);
    povBody.root.visible = st.phone > 0.02 || lk > 0.02 || st.pitch < rad(-28); if (povBody.root.visible) { set.scene.add(povBody.root); const sit = pos[1] < 1.1; povBody.reset().pose(sit ? { hipY: 0.12, lean: -4, lL: [100, 9], kL: 62, lR: [96, 9], kR: 50 } : 'stand');
      const fx = -Math.sin(st.yaw), fz = -Math.cos(st.yaw); povBody.place(pos[0] - fx * 0.1, pos[2] - fz * 0.1, st.yaw * 180 / Math.PI + 180, sit ? 0 : pos[1] - 1.58); }
    renderSet(set, target); return k;
  }
  let frozen = null, frozenT = -1;
  function render3D(t) {
    const st = camAt(t), prevSt = camAt(Math.max(0, t - 0.5 / FPS)), vars = allVars(t);
    const ph = phoneAt(t); U.drawPhone(phone.sx, phone.sw, phone.sh, { ...(cfg.phone || {}), msgs: ph.msgs, draft: ph.draft, delivered: ph.delivered }); phone.tex.needsUpdate = true;
    let k;
    if (st.setB) { drawSet(st.set, t, st.posA, st.a, rtA, vars); k = drawSet(st.setB, t, st.posB, st, rtB, vars); }
    else k = drawSet(st.set, t, st.pos, st, rtA, vars);
    const u = finalMat.uniforms; u.tA.value = rtA.texture; u.tB.value = rtB.texture; u.uMix.value = st.setB ? st.mix : 0; u.uK.value = k; u.uVig.value = varAt('vignette', t, cfg.vignette ?? 0.78);
    const hf = 2 * Math.atan(Math.tan(rad(st.fov) / 2) * W / H); let bx = 0, by = 0, zb = 0;
    if (!prevSt.setB === !st.setB) { bx = wrapPi(st.yaw - prevSt.yaw) / hf; by = -(st.pitch - prevSt.pitch) / rad(st.fov); zb = (prevSt.fov - st.fov) / st.fov; }
    const sh = 1.15; u.uBlur.value.set(clamp(bx * sh, -0.4, 0.4), clamp(by * sh, -0.3, 0.3)); u.uZoomBlur.value = clamp(zb * 1.2, -0.2, 0.2); u.uBlack.value = 0;
    quad.material = finalMat; renderer.setRenderTarget(null); renderer.render(qscene, qcam); return ph;
  }
  const choice = B.find(b => b.type === 'choice');
  window.renderAt = t => {
    t = clamp(t, 0, DUR - 1e-4); ctx.filter = 'none'; ctx.globalAlpha = 1;
    if (choice && t >= choice.t0) {
      const f = Math.floor((t - choice.t0) * FPS + 1e-6);
      if (f < 1) { ctx.fillStyle = '#04050c'; ctx.fillRect(0, 0, out.width, out.height); return; }       // one black frame, then the frozen picture
      if (!frozen) { frozen = document.createElement('canvas'); frozen.width = out.width; frozen.height = out.height; render3D(choice.t0 - 1 / FPS); const fx = frozen.getContext('2d'); fx.filter = `blur(${11 * SCALE}px)`; fx.drawImage(glc, -24, -24, out.width + 48, out.height + 48); fx.filter = 'none'; fx.fillStyle = 'rgba(8,8,20,0.64)'; fx.fillRect(0, 0, out.width, out.height); }
      ctx.drawImage(frozen, 0, 0); U.drawChoice(ctx, out.width, out.height, { question: 'WHAT WOULD\nYOU DO?', ...choice }, f); return;
    }
    const ph = render3D(t); ctx.drawImage(glc, 0, 0);
    // overlay
    if (cfg.infobar) U.drawInfo(ctx, out.width, out.height, typeof cfg.infobar === 'function' ? cfg.infobar(t) : cfg.infobar);
    const bd = cfg.badge; if (bd) U.drawBadge(ctx, out.width, out.height, bd, Math.min(clamp((t - 0.07) / 0.23), 1 - clamp((t - (bd.until ?? 3.5)) / 0.17)));
    U.drawBanner(ctx, out.width, out.height, ph.banner, ph.bk);
    const c = caps.find(c => t >= c.s && t < c.e);
    if (c) { const sp = S.speakers[c.b.who] || {}, u = (t - c.s) / Math.max(0.01, c.e - c.s), st = c.b.stretch && c.k === c.b.phrases.length - 1 ? u : 0;
      if (c.b.tag) U.drawTag(ctx, out.width, out.height, c.b.tag); U.drawCaption(ctx, out.width, out.height, c.text, c.b.color || sp.color || '#ffffff', { stretch: st, alpha: 1 - 0.65 * st }); }
    const b = B.find(b => t >= b.t0 && t < b.t1); b?.overlay?.(ctx, out.width, out.height, t - b.t0);
  };
  // ---- info for the tools: script per speaker, sound events
  window.FRAMES = Math.ceil(DUR * FPS); window.DURATION = DUR;
  window.INFO = () => {
    const ev = []; camBeats.forEach((b, i) => { if (i === 0) return; const p = camBeats[i - 1]; if (b.type === 'choice') return; const a = aimOf(b, b.camAtT + 1), pa = aimOf(p, b.camAtT); const ang = Math.hypot(wrapPi(a.yaw - pa.yaw), a.pitch - pa.pitch);
      ev.push([b.setChanged ? 'whoosh_long' : b.isPhone ? 'rustle' : ang > rad(10) ? 'whoosh' : 'zoom', +(b.camAtT).toFixed(3)]); });
    for (const b of B) { for (const p of [].concat(b.punch || [])) ev.push(['punch', +when(b, p.at ?? 0).toFixed(3)]); for (const s of b.sfx || []) ev.push([s[0], +(typeof s[1] === 'string' ? b.t0 + b.ps[parseInt(s[1].slice(1))] : b.t0 + (s[1] || 0)).toFixed(3), s[2] ?? 1]);
      if (b.type === 'phone') for (const e of b.ev) { if (e.type != null) { for (let i = 0; i < e.type.length; i++) if (e.type[i] !== ' ') ev.push(['key', +(b.t0 + e.t + 0.2 + e.typeDur * i / e.type.length).toFixed(3)]); ev.push(['send', +(b.t0 + e.sent).toFixed(3)]); } else ev.push(['notify', +(b.t0 + e.t).toFixed(3)]); }
      if (b.type === 'choice') { ev.push(['riser', +(b.t0 - 1.6).toFixed(3)]); ev.push(['boom', +b.t0.toFixed(3)]); ev.push(['pop', +(b.t0 + 18 / FPS).toFixed(3)], ['pop', +(b.t0 + 27 / FPS).toFixed(3)]); } }
    return { duration: DUR, frames: window.FRAMES, target: cfg.target || null, pace: +pace.toFixed(2), voiced: !!timings, unvoiced: timings ? sayBeats.filter(b => !b.voiced).map(b => b.n) : [], mood: cfg.audioMood || 'tension',
      beats: B.map(b => ({ i: b.i, type: b.type, who: b.who, text: b.text, t0: +b.t0.toFixed(3), t1: +b.t1.toFixed(3), cam: +b.camAtT.toFixed(3), look: typeof b.look === 'string' ? b.look : 'point', zoom: b.zoom, moved: !!b.camChanged })),
      lines: sayBeats.map(b => ({ n: b.n, who: b.who, voice: S.speakers[b.who]?.voice || 'Puck', fx: b.fx ?? S.speakers[b.who]?.fx ?? null, text: words(b.text).join(' '), t0: +b.t0.toFixed(3), dur: +b.dur.toFixed(3), stretch: !!b.stretch })),
      speakers: Object.fromEntries(Object.entries(S.speakers).map(([k, v]) => [k, { voice: v.voice || 'Puck', fx: v.fx || null, color: v.color }])), events: ev.sort((a, b) => a[1] - b[1]) };
  };
  if (q.has('t')) window.renderAt(parseFloat(q.get('t')));
  if (q.has('play')) { const a = new Audio('audio/final_audio.wav'); let t0 = performance.now(); a.play().catch(() => {}); const loop = () => { const tt = a.currentTime > 0 ? a.currentTime : (performance.now() - t0) / 1000; window.renderAt(tt % DUR); requestAnimationFrame(loop); }; loop(); }
  window.READY = true;
}
