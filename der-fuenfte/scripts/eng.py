"""Mini cartoon engine: fisheye POV camera, flat-shaded rooms with outlines, billboard characters, stepped lighting."""
import numpy as np, cv2, math

W, H = 1080, 1920
OUTL = (36, 24, 20)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, t): return a + (b - a) * t
def kf(t, keys, e=ease):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t0 <= t < t1:
            u = e((t - t0) / (t1 - t0))
            if isinstance(v0, (tuple, list)): return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]
def shade(c, f): return tuple(int(clamp(v * f, 0, 255)) for v in c)

class Cam:
    def __init__(s, pos, yaw=0.0, pitch=0.0, roll=0.0, f=620.0, cx=540.0, cy=940.0):
        s.pos = np.array(pos, float); s.f, s.cx, s.cy = f, cx, cy
        y, p, r = math.radians(yaw), math.radians(pitch), math.radians(roll)
        fw = np.array([math.sin(y), 0, math.cos(y)]); rt = np.array([math.cos(y), 0, -math.sin(y)]); up = np.array([0, 1.0, 0])
        f2 = fw * math.cos(p) + up * math.sin(p); u2 = -fw * math.sin(p) + up * math.cos(p)
        r3 = rt * math.cos(r) + u2 * math.sin(r); u3 = -rt * math.sin(r) + u2 * math.cos(r)
        s.R = np.stack([r3, u3, f2])
    def to_cam(s, P): return (np.asarray(P, float) - s.pos) @ s.R.T
    def proj(s, Pc):
        x, y, z = Pc[:, 0], Pc[:, 1], Pc[:, 2]; rho = np.hypot(x, y) + 1e-9; r = s.f * np.arctan2(rho, z)
        return np.stack([s.cx + r * x / rho, s.cy - r * y / rho], 1)
    def world(s, P): return s.proj(s.to_cam(np.atleast_2d(np.asarray(P, float))))
    def dist(s, p): return float(np.linalg.norm(np.asarray(p, float) - s.pos))

ZN = 0.04
def _clip(Pc):
    out = []; n = len(Pc)
    for i in range(n):
        a, b = Pc[i], Pc[(i + 1) % n]; ia, ib = a[2] >= ZN, b[2] >= ZN
        if ia: out.append(a)
        if ia != ib: out.append(a + (b - a) * ((ZN - a[2]) / (b[2] - a[2])))
    return np.array(out) if len(out) >= 3 else None
def _subdiv(Pc, closed=True):
    pts = []; n = len(Pc)
    for i in range(n if closed else n - 1):
        a, b = Pc[i], Pc[(i + 1) % n]
        ang = math.acos(clamp(float(np.dot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9), -1, 1))
        k = int(min(64, max(1, math.ceil(ang / 0.045))))
        for j in range(k): pts.append(a + (b - a) * (j / k))
    if not closed: pts.append(Pc[-1])
    return np.array(pts)
def _q(S): return np.round(np.clip(S, -20000, 20000) * 8).astype(np.int32).reshape(-1, 1, 2)

def poly(img, cam, pts, fill=None, line=OUTL, lw=4):
    Pc = _clip(cam.to_cam(pts))
    if Pc is None: return
    S = cam.proj(_subdiv(Pc))
    if S[:, 0].max() < -40 or S[:, 0].min() > W + 40 or S[:, 1].max() < -40 or S[:, 1].min() > H + 40: return
    q = _q(S)
    if fill is not None: cv2.fillPoly(img, [q], fill, cv2.LINE_AA, 3)
    if line is not None and lw > 0: cv2.polylines(img, [q], True, line, int(lw), cv2.LINE_AA, 3)

def line3(img, cam, a, b, color=OUTL, lw=3):
    Pc = cam.to_cam(np.array([a, b], float))
    if Pc[0, 2] < ZN and Pc[1, 2] < ZN: return
    if Pc[0, 2] < ZN: Pc[0] = Pc[0] + (Pc[1] - Pc[0]) * ((ZN - Pc[0, 2]) / (Pc[1, 2] - Pc[0, 2]))
    elif Pc[1, 2] < ZN: Pc[1] = Pc[1] + (Pc[0] - Pc[1]) * ((ZN - Pc[1, 2]) / (Pc[0, 2] - Pc[1, 2]))
    cv2.polylines(img, [_q(cam.proj(_subdiv(Pc, False)))], False, color, int(lw), cv2.LINE_AA, 3)

def rz(x0, x1, y0, y1, z): return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
def rx(z0, z1, y0, y1, x): return [(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0)]
def ry(x0, x1, z0, z1, y): return [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
def disc(c, r, axis="y", n=20):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False); cx, cy, cz = c
    if axis == "y": return [(cx + r * math.cos(t), cy, cz + r * math.sin(t)) for t in a]
    if axis == "z": return [(cx + r * math.cos(t), cy + r * math.sin(t), cz) for t in a]
    return [(cx, cy + r * math.sin(t), cz + r * math.cos(t)) for t in a]

def box(img, cam, lo, hi, color, lw=4, top=None):
    x0, y0, z0 = lo; x1, y1, z1 = hi
    faces = [((0, 1, 0), ry(x0, x1, z0, z1, y1), 1.0), ((0, -1, 0), ry(x0, x1, z0, z1, y0), 0.5),
             ((-1, 0, 0), rx(z0, z1, y0, y1, x0), 0.72), ((1, 0, 0), rx(z0, z1, y0, y1, x1), 0.72),
             ((0, 0, -1), rz(x0, x1, y0, y1, z0), 0.86), ((0, 0, 1), rz(x0, x1, y0, y1, z1), 0.86)]
    vis = []
    for n, p, s in faces:
        c = np.mean(p, 0)
        if np.dot(n, cam.pos - c) > 0: vis.append((-np.linalg.norm(cam.pos - c), p, s, n))
    for _, p, s, n in sorted(vis, key=lambda v: v[0]):
        poly(img, cam, p, shade(top if (top and n[1] == 1) else color, s), OUTL, lw)

def room(img, cam, x0, x1, z0, z1, h, wall, floor, ceil, planks=None, tiles=None):
    poly(img, cam, ry(x0, x1, z0, z1, h), ceil, OUTL, 4)
    poly(img, cam, ry(x0, x1, z0, z1, 0), floor, OUTL, 4)
    if planks:
        x = x0 + planks
        while x < x1 - 0.01: line3(img, cam, (x, 0.002, z0), (x, 0.002, z1), shade(floor, 0.72), 2); x += planks
    if tiles:
        x = x0 + tiles
        while x < x1 - 0.01: line3(img, cam, (x, 0.002, z0), (x, 0.002, z1), shade(floor, 0.78), 2); x += tiles
        z = z0 + tiles
        while z < z1 - 0.01: line3(img, cam, (x0, 0.002, z), (x1, 0.002, z), shade(floor, 0.78), 2); z += tiles
    poly(img, cam, rz(x0, x1, 0, h, z1), wall, OUTL, 4)
    poly(img, cam, rz(x0, x1, 0, h, z0), shade(wall, 0.92), OUTL, 4)
    poly(img, cam, rx(z0, z1, 0, h, x0), shade(wall, 0.84), OUTL, 4)
    poly(img, cam, rx(z0, z1, 0, h, x1), shade(wall, 0.84), OUTL, 4)
    for (a, b) in [((x0, 0.09, z1), (x1, 0.09, z1)), ((x0, 0.09, z0), (x0, 0.09, z1)), ((x1, 0.09, z0), (x1, 0.09, z1)), ((x0, 0.09, z0), (x1, 0.09, z0))]:
        line3(img, cam, a, b, shade(wall, 0.6), 3)

# ---------------------------------------------------------------- characters (billboards)
SKIN = (226, 176, 140)
CH = dict(
    hame=dict(hood=(198, 54, 46), pants=(44, 48, 66), skin=(222, 170, 132), hair=(30, 24, 22), acc=None),
    shiar=dict(hood=(54, 132, 88), pants=(62, 62, 70), skin=(212, 158, 120), hair=(26, 22, 20), acc="cap"),
    zizo=dict(hood=(234, 190, 62), pants=(54, 72, 114), skin=(228, 178, 140), hair=(34, 26, 22), acc="beanie"),
    alan=dict(hood=(196, 198, 206), pants=(50, 56, 78), skin=SKIN, hair=(60, 44, 32), acc=None),
    shadow=dict(hood=(16, 15, 20), pants=(12, 12, 16), skin=(20, 19, 24), hair=(8, 8, 10), acc=None))

def actor(img, cam, a, emis):
    c = dict(CH[a["ch"]]); d = a.get("dark", 1.0); x, z = a["pos"]; y0 = a.get("y", 0.0); h = a.get("h", 1.72)
    Pc = cam.to_cam(np.array([(x, y0, z), (x, y0 + h, z)]))
    if Pc[:, 2].min() < 0.25: return
    S = cam.proj(Pc); U = (S[1] - S[0]) / h; ppm = float(np.linalg.norm(U)); R = np.array([-U[1], U[0]])
    if ppm < 6: return
    lean = a.get("lean", 0.0)
    def P(u, v): return S[0] + (u + lean * v) * R + v * U
    ow = max(1.5, ppm * 0.014); col = lambda k: shade(c[k], d); ol = shade(OUTL, min(1.0, d + 0.3))
    def I(p): return (int(round(p[0] * 8)), int(round(p[1] * 8)))
    def seg(p, q, th, color):
        cv2.line(img, I(p), I(q), ol, max(1, int(th * ppm + 2 * ow)), cv2.LINE_AA, 3); cv2.line(img, I(p), I(q), color, max(1, int(th * ppm)), cv2.LINE_AA, 3)
    def circ(p, r, color, o=True):
        if o: cv2.circle(img, I(p), max(1, int((r * ppm + ow) * 8)), ol, -1, cv2.LINE_AA, 3)
        cv2.circle(img, I(p), max(1, int(r * ppm * 8)), color, -1, cv2.LINE_AA, 3)
    def pg(pts, color, o=True):
        q = np.array([I(P(u, v)) for u, v in pts], np.int32).reshape(-1, 1, 2); cv2.fillPoly(img, [q], color, cv2.LINE_AA, 3)
        if o: cv2.polylines(img, [q], True, ol, max(1, int(ow * 1.6)), cv2.LINE_AA, 3)
    face = a.get("face", "front"); pose = a.get("pose", "stand"); ex = a.get("expr", "normal"); sit = pose == "sit"
    hip = 0.36 if sit else 0.86; sh = hip + 0.52; hd = sh + 0.2; bob = a.get("bob", 0.0); hip += bob; sh += bob; hd += bob
    if sit:
        seg(P(-0.10, hip), P(-0.34, 0.10), 0.14, col("pants")); seg(P(0.10, hip), P(0.34, 0.10), 0.14, col("pants"))
        seg(P(-0.34, 0.10), P(-0.05, 0.06), 0.13, col("pants")); seg(P(0.34, 0.10), P(0.05, 0.06), 0.13, col("pants"))
    elif not a.get("nolegs"):
        for sx in (-1, 1):
            seg(P(sx * 0.095, hip), P(sx * 0.1, 0.07), 0.135, col("pants")); seg(P(sx * 0.1, 0.035), P(sx * 0.16, 0.035), 0.075, shade((230, 230, 230), d))
    arms = {"stand": ((-0.30, hip - 0.02), (0.30, hip - 0.02)), "sit": ((-0.26, hip + 0.02), (0.26, hip + 0.02)),
            "wave": ((-0.30, hip - 0.02), (0.44, sh + 0.34)), "knock": ((-0.30, hip - 0.02), (0.20, sh + 0.05)),
            "phone": ((-0.30, hip - 0.02), (0.14, sh - 0.12)), "scared": ((-0.2, sh - 0.2), (0.2, sh - 0.2))}[pose if pose in ("stand", "sit", "wave", "knock", "phone", "scared") else "stand"]
    wv = a.get("wave", 0.0)
    for sx, hand in zip((-1, 1), arms):
        hx, hy = hand
        if pose == "wave" and sx == 1: hx += 0.12 * math.sin(wv)
        seg(P(sx * 0.25, sh - 0.04), P(hx, hy), 0.105, col("hood")); circ(P(hx, hy), 0.058, col("skin"))
        if pose == "phone" and sx == 1: pg([(hx - 0.04, hy + 0.01), (hx + 0.05, hy + 0.01), (hx + 0.05, hy + 0.17), (hx - 0.04, hy + 0.17)], shade((200, 220, 255), max(d, 0.9)))
    pg([(-0.23, hip - 0.04), (0.23, hip - 0.04), (0.27, sh - 0.02), (0.17, sh + 0.05), (-0.17, sh + 0.05), (-0.27, sh - 0.02)], col("hood"))
    if face == "front": pg([(-0.11, sh + 0.03), (0.11, sh + 0.03), (0.06, sh - 0.09), (-0.06, sh - 0.09)], shade(c["hood"], d * 0.8), False)
    hc = P(0, hd); circ(hc, 0.155, col("skin") if face != "back" else col("hair"))
    hair = col("hair")
    if face != "back":
        pg([(-0.16, hd + 0.03), (-0.13, hd + 0.13), (-0.04, hd + 0.17), (0.06, hd + 0.17), (0.14, hd + 0.12), (0.16, hd + 0.03), (0.08, hd + 0.075), (-0.02, hd + 0.06), (-0.10, hd + 0.075)], hair)
    if c["acc"] == "cap":
        pg([(-0.165, hd + 0.04), (-0.13, hd + 0.15), (0, hd + 0.185), (0.13, hd + 0.15), (0.165, hd + 0.04)], shade((30, 30, 34), d))
        if face == "front": pg([(-0.17, hd + 0.04), (0.17, hd + 0.04), (0.19, hd + 0.005), (-0.19, hd + 0.005)], shade((22, 22, 26), d))
    if c["acc"] == "beanie":
        pg([(-0.165, hd + 0.03), (-0.14, hd + 0.15), (0, hd + 0.2), (0.14, hd + 0.15), (0.165, hd + 0.03)], shade((60, 74, 150), d))
        pg([(-0.17, hd + 0.03), (0.17, hd + 0.03), (0.17, hd + 0.075), (-0.17, hd + 0.075)], shade((84, 100, 180), d))
    if face == "front":
        er = {"normal": 0.036, "scared": 0.047, "creepy": 0.05, "closed": 0.0}[ex]; ey = hd - 0.005
        blink = a.get("blink", 0.0)
        for sx in (-1, 1):
            e = P(sx * 0.064, ey)
            if ex == "closed" or blink > 0.5: seg(P(sx * 0.064 - 0.03, ey), P(sx * 0.064 + 0.03, ey), 0.008, ol); continue
            wc = (245, 242, 232) if ex == "creepy" else shade((245, 245, 245), max(d, 0.75))
            circ(e, er, wc)
            if ex == "creepy":
                circ(P(sx * 0.064, ey), 0.007, (20, 16, 16), False)
                if a.get("glow", True): emis.append(lambda e=e, r=er * ppm: (cv2.circle(img, I(e), max(1, int(r * 8)), (236, 232, 214), -1, cv2.LINE_AA, 3), cv2.circle(img, I(e), max(1, int(r * 1.2)), (30, 20, 20), -1, cv2.LINE_AA, 3)))
            else:
                lk = a.get("look", (0, 0)); circ(P(sx * 0.064 + lk[0] * 0.014, ey + lk[1] * 0.014), 0.017 if ex == "normal" else 0.012, (24, 18, 18), False)
        if ex == "creepy":
            pts = [P(-0.085 + 0.17 * k / 8, hd - 0.085 - 0.022 * math.sin(math.pi * k / 8)) for k in range(9)]
            cv2.polylines(img, [np.array([I(p) for p in pts], np.int32).reshape(-1, 1, 2)], False, ol, max(1, int(ppm * 0.014)), cv2.LINE_AA, 3)
        elif ex == "scared": circ(P(0, hd - 0.085), 0.026, (60, 24, 24))
        else: seg(P(-0.03, hd - 0.085), P(0.03, hd - 0.085), 0.008, ol)

# ---------------------------------------------------------------- lighting
_yy, _xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32) * 4 + 2
def light(img, amb, spots, vig=True):
    L = np.ones((H // 4, W // 4, 3), np.float32) * np.array(amb, np.float32)
    for s in spots:
        d = np.sqrt((_xx - s["x"]) ** 2 + (_yy - s["y"]) ** 2) / max(s["r"], 1)
        f = np.clip((1.0 - d) / 0.06, 0, 1) * 0.55 + np.clip((0.6 - d) / 0.06, 0, 1) * 0.45
        if s.get("soft"): f = np.clip(1 - d, 0, 1) ** 1.5
        L += f[..., None] * (np.array(s.get("c", (1.0, 0.92, 0.78)), np.float32) * s["I"])
    if vig:
        rr = np.sqrt((_xx - 540) ** 2 + (_yy - 940) ** 2); L *= (1 - 0.55 * np.clip((rr - 700) / 330, 0, 1) ** 1.6)[..., None]
        L *= (1 - np.clip((rr - 1040) / 90, 0, 1))[..., None]
    L = cv2.resize(cv2.GaussianBlur(L, (0, 0), 1.6), (W, H), interpolation=cv2.INTER_LINEAR)
    return np.clip(img.astype(np.float32) * L, 0, 255).astype(np.uint8)

_pr = np.sqrt((np.mgrid[0:H, 0:W][1] - 540.0) ** 2 + (np.mgrid[0:H, 0:W][0] - 930.0) ** 2).astype(np.float32)
def peephole(img, k):
    R = lerp(70, 470, eout(k)); m = np.clip((R - _pr) / 16, 0, 1)
    ring = np.clip(1 - np.abs(_pr - (R - 26)) / 26, 0, 1) * 0.5
    out = img.astype(np.float32) * (m * (1 - 0.55 * np.clip((_pr / R) - 0.55, 0, 1)) * (1 - ring))[..., None]
    return out.astype(np.uint8)
