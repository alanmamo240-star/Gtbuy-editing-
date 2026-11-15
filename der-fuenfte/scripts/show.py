"""Episode framework + renderer.  usage: show.py N preview t1,t2 | show.py N chunk K NC"""
import json, os, sys, subprocess, math, numpy as np
from sets import *
import ui
FPS = 30

class Ep:
    def __init__(s, n, title, clock=(23, 41)):
        s.n, s.title, s.clock = n, title, clock
        s.msgs, s.typing, s.typed, s.lines, s.sfx, s.shots, s.ups, s.screens, s.dips, s.imgs = [], [], [], [], [], [], [], [(-99, "lock", {})], [], {}
        s.t_black, s.dur, s._lt = 118.0, 121.6, None
    def msg(s, t, who, text, banner=True, kind="text", **kw):
        s.msgs.append(dict(t=t, who=who, text=text, banner=banner, kind=kind, **kw))
        if t >= 0 and kind != "sys": s.fx(t, "buzz" if banner else ("send" if who == "Alan" else "ping"), -4 if banner else -9)
    def say(s, t, sp, text, fx="near", key=None, cap=None, **kw): s.lines.append(dict(t=t, sp=sp, text=text, fx=fx, key=key, cap=cap, **kw))
    def fx(s, t, name, db=0.0, **kw): s.sfx.append(dict(t=t, name=name, db=db, **kw))
    def shot(s, t0, t1, fn): s.shots.append((t0, t1, fn))
    def up(s, t0, t1): s.ups.append((t0, t1))
    def scr(s, t, kind, **kw): s.screens.append((t, kind, kw))
    def dip(s, t, half=0.2): s.dips.append((t, half))
    def typ(s, t0, t1, who): s.typing.append((t0, t1, who))
    def typd(s, t0, t1, text): s.typed.append((t0, t1, text))
    def end(s, t): s.t_black = t; s.dur = t + 3.6
    def k(s, t): return max([min(ease((t - a) / 0.45), ease((b - t) / 0.4)) for a, b in s.ups if a <= t <= b] + [0.0])
    def ltimes(s):
        if s._lt is None:
            p = f"ep{s.n}_lines.json"
            s._lt = json.load(open(p)) if os.path.exists(p) else [(l["t"], l["t"] + 0.085 * len(l["text"]) + 0.4) for l in s.lines]
        return s._lt
    def spec(s, t):
        _, kind, kw = [x for x in s.screens if x[0] <= t][-1]
        mm = int(s.clock[0] * 60 + s.clock[1] + t / 60); tm = f"{(mm // 60) % 24:02d}:{mm % 60:02d}"
        if kind == "lock": return dict(kind="lock", time=tm, msgs=[dict(who=m["who"], text=m["text"]) for m in s.msgs if m["banner"] and m["kind"] == "text" and 0 <= t - m["t"] < 9][-1:])
        if kind == "chat":
            ms = []
            for m in s.msgs:
                if m["t"] > t: continue
                d = dict(who=m["who"], text=m["text"], kind=m["kind"])
                if m["kind"] == "photo": d["img"] = s.img(m["img"]); d["text"] = m["img"]
                if m["kind"] == "voice": d["prog"] = round(clamp((t - m.get("p0", 1e9)) / max(m.get("p1", 1e9) - m.get("p0", 0), 0.1)), 1)
                ms.append(d)
            ty = next((w for a, b, w in s.typing if a <= t < b), None)
            tx = next((x[:max(1, int(len(x) * clamp((t - a) / max(b - a, 0.1))) + 1)] for a, b, x in s.typed if a <= t < b), "")
            return dict(kind="chat", msgs=ms[-9:], typing=("Unbekannt" if ty == "" else ty), typed=tx, **kw)
        d = dict(kind=kind, **{a: b for a, b in kw.items() if a != "img"})
        if "img" in kw: d["img"] = s.img(kw["img"])
        if kind == "camera": d["flash"] = round(clamp(1 - abs(t - kw.get("ft", -9)) / 0.22), 1) if "ft" in kw else 0
        if kind == "call": d["timer"] = f"00:{int(max(0, t - kw.get('t0', 0))):02d}"; d["lvl"] = round(0.5 + 0.5 * math.sin(t * 9), 1) if any(l["fx"] == "phone" and a <= t <= b for l, (a, b) in zip(s.lines, s.ltimes())) else 0.0
        d.pop("ft", None); d.pop("t0", None)
        return d
    def img(s, name):
        if name not in s.imgs: s.imgs[name] = PHOTOS[name]()
        return s.imgs[name]

PHOTOS = {}
def photo_from(st, crop=(90, 130, 990, 1630)):
    im, _ = draw_scene(st); x0, y0, x1, y1 = crop; return np.ascontiguousarray(im[y0:y1, x0:x1])

def chunks(text):
    out, cur = [], ""
    for w in text.split():
        if cur and (len(cur) + len(w) > 13 or cur.count(" ") >= 2 or cur[-1] in ".?!,…"): out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out

def frame(ep, t):
    if t >= ep.t_black:
        img = np.zeros((H, W, 3), np.uint8); a = clamp((t - ep.t_black - 0.5) / 0.5)
        ui.card(img, [("FORTSETZUNG FOLGT …", "ExtraBold", 74, (240, 232, 214)), (f"DER FÜNFTE · EP {ep.n + 1}", "Bold", 40, (200, 60, 50))], a)
        return img
    st = dict(next(fn for a, b, fn in ep.shots if a <= t < b)(t)); c = dict(st["cam"]); st["cam"] = c
    zf = 620.0 / c.get("f", 620); sw = st.get("sway", 1.0) * zf
    c["yaw"] = c.get("yaw", 0) + sw * (0.55 * math.sin(0.7 * t) + 0.3 * math.sin(1.9 * t + 1)); c["pitch"] = c.get("pitch", 0) + sw * 0.4 * math.sin(0.9 * t + 2); c["roll"] = c.get("roll", 0) + sw * 0.35 * math.sin(0.6 * t)
    bob = (0.0, 0.0)
    if st.get("walk", 0) > 0:
        w = st["walk"]; ph = t * 2 * math.pi * 0.95; p = list(c["pos"]); p[1] += 0.028 * w * abs(math.sin(ph)); c["pos"] = tuple(p); c["roll"] += 0.9 * w * math.sin(ph); bob = (10 * w * math.sin(ph), 16 * w * abs(math.sin(ph)))
    if st.get("shake", 0) > 0:
        rs = np.random.default_rng(int(t * FPS)); c["yaw"] += st["shake"] * rs.normal(0, 1.2); c["pitch"] += st["shake"] * rs.normal(0, 1.0)
    k = ep.k(t); lights = list(st.get("lights", [])); nophone = st.get("nophone", False); hide = st.get("hide", 0.0)
    if not nophone and hide < 0.8:
        pl = st.get("plight", 1.0)
        if k < 0.5: lights.append(dict(x=742 + bob[0], y=1560 + bob[1], r=450, I=0.72 * pl * (1 - 2 * k) * (1 - hide)))
        lights.append(dict(x=540, y=1150, r=860, I=0.42 * ease(k) * pl, c=(0.8, 0.87, 1.0)))
    st["lights"] = lights
    img, cam = draw_scene(st)
    if st.get("flash", 0) > 0: img[:] = (img * (1 - st["flash"]) + 255 * st["flash"]).astype(np.uint8)
    if st.get("lhand", 0) > 0:
        p = cam.world([st.get("lhand_at", (-0.36, 1.02, 6.15))])[0]; ui.left_hand(img, p[0], p[1] + 30, ease(st["lhand"]))
    if not nophone: ui.phone(img, k, ui.screen(ep.spec(t)), bob, hide=hide)
    if k < 0.5:
        for m in ep.msgs:
            if not m["banner"]: continue
            du = clamp(2.4 + 0.055 * len(m["text"]), 3.2, 6.0); dt = t - m["t"]
            if 0 <= dt <= du: ui.banner(img, m["who"], m["text"], min(dt / 0.25, (du - dt) / 0.2, 1.0), m.get("head"))
    cy = st.get("capy") or (1560 if st.get("peep") is not None else lerp(1130, 330, ease(k)))
    for l, (a, b) in zip(ep.lines, ep.ltimes()):
        if l.get("cap") is False or not (a <= t <= b + 0.25): continue
        ch = chunks(l["cap"] or l["text"]); tot = sum(len(x) + 2 for x in ch); u = (t - a) / max(b - a, 0.1); acc = 0.0
        for x in ch:
            w = (len(x) + 2) / tot
            if acc <= u < acc + w or (x is ch[-1] and u >= acc): ui.caption(img, x, cy, clamp((u - acc) * (b - a) / 0.12)); break
            acc += w
    if 0.6 <= t < 4.2: ui.tag(img, f"DER FÜNFTE · EP {ep.n}", min((t - 0.6) / 0.4, (4.2 - t) / 0.4, 1.0))
    f = min([clamp(abs(t - tc) / h) for tc, h in ep.dips] + [clamp(t / 0.6), 1.0])
    if f < 1: img[:] = (img * f).astype(np.uint8)
    return img

if __name__ == "__main__":
    import story
    ep = story.EPS[int(sys.argv[1])]; mode = sys.argv[2]
    if mode == "preview":
        from PIL import Image
        for t in [float(x) for x in sys.argv[3].split(",")]: Image.fromarray(frame(ep, t)).save(f"test/e{ep.n}_{t:06.2f}.jpg", quality=90)
        print("preview done")
    else:
        K, NC = int(sys.argv[3]), int(sys.argv[4]); N = int(round(ep.dur * FPS)); a, b = K * N // NC, (K + 1) * N // NC
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", f"ep{ep.n}_chunk_{K}.mp4"], stdin=subprocess.PIPE)
        for i in range(a, b):
            enc.stdin.write(frame(ep, i / FPS).tobytes())
            if (i - a) % 150 == 0: print(f"ep{ep.n} chunk {K}: {i - a}/{b - a}", flush=True)
        enc.stdin.close(); enc.wait(); print(f"ep{ep.n} chunk {K} done")
