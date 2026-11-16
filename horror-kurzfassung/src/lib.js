// Shared helpers for the 30-second episodes: timing on fixed marks, moving figures (run / walk / crawl / jump),
// cold-breath puffs, billboards and small material tricks. Used by every src/<episode>.js.
import { THREE, canvasTex, noOutline, clamp, lerp, smooth, rad } from './util.js';

export const Q = new URLSearchParams(location.search);
export const towards = (a, b) => Math.atan2(b[0] - a[0], b[1] - a[1]) * 180 / Math.PI;     // rotation (deg) that faces from a to b
export const fogOff = o => { o.traverse(m => { if (m.material) m.material.fog = false; }); return o; };
export const texRep = (t, x, y) => { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(x, y); return t; };
export const blackOverlay = (ctx, w, h) => { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, w, h); };
export async function loadTimings() { if (Q.has('notimings')) return null; try { const r = await fetch('timings.json?' + Date.now()); if (r.ok) return await r.json(); } catch (e) {} return null; }

// Beats on absolute time marks. hold(until) fills to a mark; say() lasts as long as the real line. The engine restarts the slow
// push-in on every beat, so a beat that keeps the shot continues the zoom the previous one reached. cut: true marks a hard cut.
export function sequencer(S, TM) {
  const ZN = { tight: 44, medium: 60, close: 76, wide: 96 };
  let T = 0, N = 0, CAM = { look: null, zoom: 60, push: 0.012, at: 0 };
  const nWords = s => s.replace(/\|/g, ' ').split(/\s+/).filter(Boolean).length;
  const est = s => s.split('|').reduce((a, p) => a + 0.22 + 0.3 * nWords(p), 0) - 0.2;
  const lineDur = text => { const tm = TM?.lines?.[N]; return tm && tm.words && tm.words.length === nWords(text) ? tm.dur : est(text); };
  function camOpts(o, isSay) {
    const at = T + (o.camAt ?? (isSay ? -0.1 : 0));
    if (o.look === undefined && o.zoom === undefined && o.pov === undefined && !o.cut && CAM.look) o = { ...o, look: CAM.look, zoom: CAM.zoom * Math.max(0.72, 1 - CAM.push * Math.max(0, at - CAM.at)), push: o.push ?? CAM.push };
    if (o.cut) o = { ...o, sfx: [...(o.sfx || []), ['cut', 0]] };
    CAM = { look: o.look ?? CAM.look, zoom: typeof o.zoom === 'number' ? o.zoom : (ZN[o.zoom] ?? CAM.zoom), push: o.push ?? 0.012, at };
    return o;
  }
  const api = {
    get T() { return T; },
    abs: x => x - T,                                   // absolute time -> offset inside the beat being written
    hold(until, o = {}) { const d = Math.max(0.1, until - T); S.hold(d, { gap: 0, ...camOpts(o, false) }); T += d; return api; },
    say(who, text, o = {}) { const d = lineDur(text); N++; S.say(who, text, { gap: 0, autoLook: false, ...camOpts(o, true) }); T += d; return api; },
    // a phone beat (incoming texts / a typed reply) that lasts exactly as long as the engine will make it
    phone(o = {}) { let a = 0.45; for (const e of o.events || []) { if (e.type != null) a += 0.25 + e.type.length / 27 + 0.17 + (e.hold ?? 1.1); else a += e.hold ?? 1.5; } S.phone({ gap: 0, ...o }); T += a; return api; },
    black(from = 29.6, to = 30) { api.hold(from, {}); api.hold(to, { overlay: blackOverlay }); return api; },
  };
  return api;
}

// ---- moving figures. Each move overrides a figure's position between T0 and T1 (+0.45 s turn into endRy).
// The figure's own state (cast home / do keys) must put it at `from` before and at `to` after: use mv.keys() in the first beat.
export function pathAt(from, to, T, t, DEC = 0.75) {
  const L = Math.max(1e-4, Math.hypot(to[0] - from[0], to[1] - from[1])), dec = Math.min(DEC, T * 0.8), v = L / (T - dec / 2); let s, sp;
  if (t <= T - dec) { s = v * Math.max(0, t); sp = t < 0 ? 0 : 1; } else if (t < T) { const u = t - (T - dec); s = v * (T - dec) + v * u - v * u * u / (2 * dec); sp = 1 - u / dec; } else { s = L; sp = 0; }
  const k = s / L; return { x: lerp(from[0], to[0], k), z: lerp(from[1], to[1], k), k, sp, v, ry: Math.atan2(to[0] - from[0], to[1] - from[1]) };
}
export function stride(av, t, amp, ph = 0, speed = 1.7) {
  av.walk(t + ph, speed); if (speed > 1.2) av.torso.rotation.x += rad(12) * amp;
  for (const [l, k] of av.legs) { l.rotation.x *= amp; k.rotation.x *= amp; }
  for (const [a, e] of av.arms) { a.rotation.x *= amp; if (speed > 1.2) e.rotation.x = lerp(-rad(8), -rad(80), amp); }
}
export function crawl(av, t, amp, ph = 0) {   // hands and knees: arms and legs swing in opposite pairs
  const w = (t + ph) * 7.5, s = Math.sin(w);
  av.arms[0][0].rotation.x += rad(22) * s * amp; av.arms[1][0].rotation.x -= rad(22) * s * amp;
  av.legs[0][0].rotation.x -= rad(18) * s * amp; av.legs[1][0].rotation.x += rad(18) * s * amp;
}
export const CRAWL = { hipY: 0.42, lean: 78, head: [-62, 0, 0], aL: [96, 6, 0], eL: 10, aR: [96, 6, 0], eR: 10, lL: [92, 8], kL: 92, lR: [92, 8], kR: 92 };
export function mover() {
  const L = [];
  const api = {
    // o: { from:[x,z], to:[x,z], T0, T1, endRy (deg, default = travel direction), ph, mode: 'run'|'walk'|'crawl'|'still', arc (jump height), y0, y1 }
    add(av, name, o) { L.push({ av, name, mode: 'run', ph: 0, ...o }); return api; },
    // state keys that keep the figure's own position in step with the move (a figure that keeps its facing turns at the start, so its head aims right)
    keys(name) { return L.filter(m => m.name === name).flatMap(m => [...(m.keepRy ? [{ at: [...m.from, m.endRy], t: m.T0, dur: 0.15 }] : []), { at: [...m.to, m.endRy ?? towards(m.from, m.to)], y: m.y1 ?? 0, t: m.T1 + 0.4, dur: 0 }]); },
    update(t) {
      for (const m of L) {
        if (t < m.T0 || t > m.T1 + 0.45) continue; const av = m.av, p = pathAt(m.from, m.to, m.T1 - m.T0, t - m.T0, m.mode === 'walk' ? 0.5 : m.mode === 'crawl' ? 0.4 : 0.75);
        const end = rad(m.endRy ?? towards(m.from, m.to)), dir = p.ry;
        av.root.position.x = p.x; av.root.position.z = p.z;
        const y0 = m.y0 ?? 0, y1 = m.y1 ?? 0, u = clamp((t - m.T0) / (m.T1 - m.T0)); av.root.position.y = lerp(y0, y1, u) + (m.arc ? 4 * m.arc * u * (1 - u) : 0);
        av.root.rotation.y = t < m.T1 ? (m.keepRy ? end : dir) : (m.keepRy ? end : dir + Math.atan2(Math.sin(end - dir), Math.cos(end - dir)) * smooth((t - m.T1) / 0.45));
        if (p.sp > 0.01 && !m.arc) { if (m.mode === 'crawl') crawl(av, t, clamp(p.sp * 1.2), m.ph); else if (m.mode !== 'still') stride(av, t, clamp(p.sp * 1.15), m.ph, m.mode === 'walk' ? 1.0 : 1.7); }
      }
    },
    // footstep sound events ['step', time, gain] from every run/walk, louder near the camera (camPt(t) -> [x,y,z])
    steps(camPt) {
      const ev = [];
      for (const m of L) { if (m.mode !== 'run' && m.mode !== 'walk' || m.arc) continue; const per = m.mode === 'run' ? 0.298 : 0.507;
        for (let t = m.T0 + ((m.ph * 0.37) % per); t < m.T1 - 0.05; t += per) { const p = pathAt(m.from, m.to, m.T1 - m.T0, t - m.T0); const c = camPt(t), d = Math.hypot(p.x - c[0], p.z - c[2]);
          ev.push([m.mode === 'run' ? 'step' : 'stepw', +t.toFixed(3), +(Math.max(0.3, p.sp) * Math.min(1.3, 3.0 / Math.max(2.2, d))).toFixed(2)]); } }
      return ev;
    },
  };
  return api;
}

// cold breath: a soft puff from each listed figure's mouth, period(name, t) seconds per breath, active(name, t) on/off
let puffTex;
export function breathPuffs(group, figures, period, active) {
  puffTex ||= canvasTex(128, 128, x => { const gr = x.createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 128, 128); });
  const P = {}; for (const n in figures) P[n] = [0, 1].map(() => { const m = noOutline(new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: puffTex, color: '#c6cde6', transparent: true, opacity: 0, depthWrite: false }))); group.add(m); return m; });
  const v3 = new THREE.Vector3(), v4 = new THREE.Vector3();
  return (t, cam) => {
    for (const n in figures) {
      const av = figures[n], Pp = period(n, t), ph = (t + n.length * 0.37) / Pp; av.torso.position.y = 0.006 * Math.sin(ph * Math.PI * 2);
      av.head.updateMatrixWorld(true); av.head.localToWorld(v3.set(0, -0.085, 0.22)); av.head.getWorldDirection(v4);
      P[n].forEach((m, k) => { const cyc = Math.floor(ph) - k, age = (ph - Math.floor(ph) + k) * Pp, live = av.root.visible && active(n, t) && cyc >= 0 && age < 1.15;
        if (!live) { m.visible = false; return; } m.visible = true; const u = age / 1.15; m.position.copy(v3).addScaledVector(v4, 0.05 + 0.32 * u); m.position.y += 0.06 * u; m.scale.setScalar(0.07 + 0.34 * u);
        m.material.opacity = 0.3 * Math.min(1, age / 0.08) * Math.pow(1 - u, 1.6); m.lookAt(cam[0], cam[1], cam[2]); });
    }
  };
}

// camera / figure path through points with constant speed per segment and a running bob. keys: [[t, x, y, z], ...]
export function runPath(keys, bob = 0.05, step = 0.3) {
  return t => {
    if (t < keys[0][0] || t > keys[keys.length - 1][0]) return null;
    for (let i = 1; i < keys.length; i++) { const a = keys[i - 1], b = keys[i]; if (t <= b[0]) { const u = (t - a[0]) / Math.max(1e-6, b[0] - a[0]), e = i === 1 ? u * u * (3 - 2 * u) * 0.5 + u * 0.5 : i === keys.length - 1 ? 1 - (1 - u) * (1 - u) * 0.5 - (1 - u) * 0.5 : u;
      const moving = Math.hypot(b[1] - a[1], b[3] - a[3]) > 0.05, ph = (t - keys[0][0]) / step * Math.PI;
      return [lerp(a[1], b[1], e), lerp(a[2], b[2], e) + (moving ? bob * Math.abs(Math.sin(ph)) - bob * 0.5 : 0), lerp(a[3], b[3], e)]; } }
    return null;
  };
}
