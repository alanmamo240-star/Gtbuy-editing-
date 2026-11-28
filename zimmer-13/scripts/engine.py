"""2D cartoon engine for 'Das Mädchen aus Zimmer 13': view transform, outlined vector shapes,
expressive characters, screen-space lighting, film post. All colors RGB."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
OL = (20, 16, 24)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_F = {}
def font(sz, bold=True):
    k = (sz, bold)
    if k not in _F: _F[k] = ImageFont.truetype(FONT if bold else FONT_R, sz)
    return _F[k]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def ein(x): x = clamp(x); return x ** 3
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
def mix(a, b, t): return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))

# ------------------------------------------------------------------ view
class View:
    """world point (cx,cy) -> screen centre, scaled by z, rotated by r degrees."""
    def __init__(s, cx=540.0, cy=960.0, z=1.0, r=0.0, ox=0.0, oy=0.0):
        s.cx, s.cy, s.z, s.r, s.ox, s.oy = cx, cy, z, math.radians(r), ox, oy
    def P(s, pts):
        p = np.asarray(pts, float).reshape(-1, 2); x = (p[:, 0] - s.cx) * s.z; y = (p[:, 1] - s.cy) * s.z
        c, n = math.cos(s.r), math.sin(s.r)
        return np.stack([540 + s.ox + x * c - y * n, 960 + s.oy + x * n + y * c], 1)
V = View()
def cur(): return V
def setview(v):
    global V; V = v

def _q(S): return np.round(np.clip(S, -30000, 30000) * 8).astype(np.int32).reshape(-1, 1, 2)
def poly(img, pts, fill=None, ol=OL, lw=3.0, world=True):
    S = V.P(pts) if world else np.asarray(pts, float)
    if S[:, 0].max() < -50 or S[:, 0].min() > W + 50 or S[:, 1].max() < -50 or S[:, 1].min() > H + 50: return
    q = _q(S)
    if fill is not None: cv2.fillPoly(img, [q], fill, cv2.LINE_AA, 3)
    if ol is not None and lw > 0: cv2.polylines(img, [q], True, ol, max(1, int(round(lw * (V.z if world else 1)))), cv2.LINE_AA, 3)
def pline(img, pts, color=OL, lw=3.0, closed=False):
    cv2.polylines(img, [_q(V.P(pts))], closed, color, max(1, int(round(lw * V.z))), cv2.LINE_AA, 3)
def ellpts(cx, cy, rx, ry, rot=0.0, n=56, a0=0.0, a1=2 * math.pi):
    a = np.linspace(a0, a1, n, endpoint=(a1 - a0) < 2 * math.pi - 1e-6); c, s = math.cos(rot), math.sin(rot)
    x, y = rx * np.cos(a), ry * np.sin(a)
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], 1)
def ell(img, cx, cy, rx, ry, fill, ol=OL, lw=3.0, rot=0.0): poly(img, ellpts(cx, cy, rx, ry, rot), fill, ol, lw)
def seg(img, a, b, w, color, ol=OL, olw=3.0):
    S = V.P([a, b]); z = V.z; i = lambda p: (int(round(p[0] * 8)), int(round(p[1] * 8)))
    if ol is not None: cv2.line(img, i(S[0]), i(S[1]), ol, max(1, int(round((w + 2 * olw) * z))), cv2.LINE_AA, 3)
    cv2.line(img, i(S[0]), i(S[1]), color, max(1, int(round(w * z))), cv2.LINE_AA, 3)
def smooth(pts, k=8, closed=True):
    """Catmull-Rom spline through control points"""
    p = np.asarray(pts, float); n = len(p); out = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0, p1, p2, p3 = p[(i - 1) % n] if closed or i > 0 else p[0], p[i], p[(i + 1) % n], p[(i + 2) % n] if closed or i + 2 < n else p[-1]
        for u in np.linspace(0, 1, k, endpoint=False):
            u2, u3 = u * u, u * u * u
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3))
    if not closed: out.append(p[-1])
    return np.array(out)
def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

# ------------------------------------------------------------------ characters
CH = {
    "mia": dict(skin=(238, 198, 172), hair=(52, 36, 34), top=(46, 84, 98), top2=(36, 66, 78), legs=(44, 48, 66), shoe=(226, 222, 216), iris=(98, 128, 84), lips=(196, 112, 108), h=1.0),
    "mom": dict(skin=(230, 190, 164), hair=(112, 52, 40), top=(104, 90, 104), top2=(150, 140, 132), legs=(46, 42, 50), shoe=(40, 32, 30), iris=(90, 70, 50), lips=(170, 84, 84), h=1.08),
}
def _dk(c, d): return shade(c, d) if d != 1.0 else c

def char(img, c, emis=None):
    """c: who,x,y(feet),s(px height),view(front|back),turn(-1..1),expr,mouth,blink,look,pose,walk,rot,tilt,dark"""
    P0 = CH[c["who"]]; d = c.get("dark", 1.0); col = {k: (_dk(v, d) if isinstance(v, tuple) else v) for k, v in P0.items()}
    s = c["s"] * P0["h"] if c.get("scale_h", True) else c["s"]; X, Y = c["x"], c["y"]; rot = math.radians(c.get("rot", 0.0))
    cr, sr = math.cos(rot), math.sin(rot); ol = _dk(OL, min(1, d + 0.4)); lw = max(1.4, s * 0.0055) / max(V.z, 1e-3)
    tilt = math.radians(c.get("tilt", 0.0)); neck = (0.0, -0.735); bob = c.get("bob", 0.0)
    def L(u, v, head=False):
        if head:
            du, dv = u - neck[0], v - neck[1]; ct, st = math.cos(tilt), math.sin(tilt); u, v = neck[0] + du * ct - dv * st, neck[1] + du * st + dv * ct
        v += bob; return (X + (u * cr - v * sr) * s, Y + (u * sr + v * cr) * s)
    def LP(pts, head=False): return [L(u, v, head) for u, v in pts]
    def E(cu, cv, ru, rv, fill, head=True, o=True, n=40, lm=1.0):
        pts = [(cu + ru * math.cos(a), cv + rv * math.sin(a)) for a in np.linspace(0, 2 * math.pi, n, endpoint=False)]
        poly(img, LP(pts, head), fill, ol if o else None, lw * lm)
    def SP(pts, fill, head=True, lm=1.0): poly(img, smooth(LP(pts, head)), fill, ol, lw * lm)
    def SG(a, b, w, color, head=False, o=True): seg(img, L(*a, head=head), L(*b, head=head), w * s, color, ol if o else None, lw)
    view = c.get("view", "front"); pose = c.get("pose", "down"); ex = c.get("expr", "neutral"); t = c.get("turn", 0.0) if view == "front" else 0.0
    who = c["who"]; ph = c.get("walk", None)
    # ---- back hair (behind everything above shoulders)
    hc = (0.0 + t * 0.006, -0.865); hr = (0.098, 0.108)
    if who == "mia":
        g = -t * 0.02; SP([(-0.112 + g, -0.9), (-0.126 + g, -0.78), (-0.132 + g, -0.67), (-0.104, -0.605), (0.104, -0.605), (0.132 + g, -0.67), (0.126 + g, -0.78), (0.112 + g, -0.9), (0.0, -0.978)], col["hair"])
    ho = c.get("headonly", False)
    # ---- legs
    for sx in ((-1, 1) if not ho else ()):
        fx = sx * 0.045; lift = 0.0
        if ph is not None: fx += sx * 0.055 * math.sin(ph); lift = 0.02 * max(0, math.sin(ph * sx))
        if pose == "sit": continue
        SG((sx * 0.04, -0.45), (fx, -0.045 - lift), 0.056, col["legs"])
        E(fx + sx * 0.012, -0.022 - lift, 0.04, 0.022, col["shoe"], head=False)
    # ---- arms behind torso for back view
    shy = -0.705
    arm = {"down": ((0.128, -0.575), (0.132, -0.455)), "phone": ((0.125, -0.57), (0.035, -0.615)), "box": ((0.13, -0.585), (0.085, -0.56)),
           "clutch": ((0.125, -0.6), (0.035, -0.67)), "phone2": ((0.125, -0.57), (0.035, -0.615))}
    def arms():
        for sx in (-1, 1):
            p = pose
            if p == "phone" and sx == -1: p = "down"
            (eu, ev), (hu, hv) = arm.get(p, arm["down"])
            if ph is not None and p == "down": hu += 0.0; hv += 0.0; eu -= sx * 0.0; swing = 0.03 * math.sin(ph) * -sx
            else: swing = 0.0
            sh = (sx * 0.092, shy); el = (sx * eu + swing * 0.5, ev); hd = (sx * hu + swing, hv)
            SG(sh, el, 0.044, col["top"]); SG(el, hd, 0.04, col["top"])
            E(hd[0], hd[1] + 0.014, 0.019, 0.022, col["skin"], head=False)
    if view == "back" and not ho: arms()
    # ---- torso
    if ho: pass
    elif who == "mia":
        SP([(-0.06, -0.748), (0.06, -0.748), (0.1, -0.725), (0.113, -0.66), (0.11, -0.5), (0.106, -0.436), (0.0, -0.43), (-0.106, -0.436), (-0.11, -0.5), (-0.113, -0.66), (-0.1, -0.725)], col["top"], head=False)
        if view == "front":
            poly(img, LP([(-0.06, -0.53), (0.06, -0.53), (0.07, -0.455), (-0.07, -0.455)]), col["top2"], ol, lw * 0.7)
            SG((-0.022, -0.71), (-0.026, -0.62), 0.006, (220, 220, 214), o=False); SG((0.022, -0.71), (0.026, -0.62), 0.006, (220, 220, 214), o=False)
        else:
            poly(img, LP([(-0.07, -0.745), (0.07, -0.745), (0.06, -0.64), (0.0, -0.615), (-0.06, -0.64)]), col["top2"], ol, lw)
    else:
        SP([(-0.06, -0.752), (0.06, -0.752), (0.102, -0.728), (0.114, -0.66), (0.114, -0.48), (0.112, -0.405), (0.0, -0.4), (-0.112, -0.405), (-0.114, -0.48), (-0.114, -0.66), (-0.102, -0.728)], col["top"], head=False)
        if view == "front":
            poly(img, LP([(-0.03, -0.74), (0.03, -0.74), (0.02, -0.44), (-0.02, -0.44)]), col["top2"], ol, lw * 0.7)
            for k in range(3): E(0.036, -0.66 + k * 0.07, 0.006, 0.006, shade(col["top"], 0.6), head=False, o=False)
    # neck
    if view == "front": poly(img, LP([(-0.026, -0.775, ), (0.026, -0.775), (0.028, -0.725), (-0.028, -0.725)]), shade(col["skin"], 0.86), ol, lw)
    # ---- head
    if view == "back":
        E(hc[0], hc[1], hr[0] * 1.06, hr[1] * 1.04, col["hair"])
        if who == "mom": E(0.0, -0.975, 0.048, 0.042, col["hair"])
        else:
            for k in (-1, 1): pline(img, LP([(k * 0.03, -0.95), (k * 0.05, -0.82), (k * 0.06, -0.68)], True), shade(col["hair"], 0.7), lw * 0.8)
        return
    if who == "mom": E(0.0 - t * 0.02, -0.975, 0.05, 0.044, col["hair"])
    E(hc[0], hc[1], hr[0], hr[1], col["skin"])
    # ---- face
    fo = t * 0.042; cu = hc[0] + fo
    ey = -0.872; sclera = (248, 244, 238) if ex != "creepy" else (250, 250, 236)
    BR = {"neutral": (0.0, 0.0), "worried": (0.012, -0.004), "scared": (0.02, 0.006), "whisper": (0.014, -0.002), "sleep": (0.0, 0.0),
          "smile": (0.004, 0.004), "creepy": (-0.012, 0.004), "cold": (-0.004, -0.004), "sad": (0.014, -0.006)}
    OPEN = {"neutral": 1.0, "worried": 1.05, "scared": 1.3, "whisper": 0.95, "sleep": 0.0, "smile": 0.85, "creepy": 0.9, "cold": 0.62, "sad": 0.8}
    op = OPEN.get(ex, 1.0) * (1 - c.get("blink", 0.0)); lk = c.get("look", (0.0, 0.0)); irs = 0.0148 if ex != "scared" else 0.0118
    brows = []
    for sx in (-1, 1):
        far = (sx * t) < 0; sc = 1 - 0.38 * abs(t) if far else 1.0
        ex0 = cu + sx * 0.041 * (1 - 0.25 * abs(t)) * (0.7 if far else 1.0); rx, ry = 0.022 * sc, 0.026
        if op < 0.12:
            pline(img, LP([(ex0 - rx, ey + 0.002), (ex0, ey + 0.008), (ex0 + rx, ey + 0.002)], True), ol, lw * 1.3)
        else:
            E(ex0, ey, rx, ry * op, sclera, lm=0.55)
            if ex == "creepy":
                E(ex0 + lk[0] * 0.004, ey, 0.0048, 0.0048, (16, 10, 10), o=False)
                if emis is not None: emis.append(("glow", L(ex0, ey, True), rx * s * 1.9))
            else:
                ix, iy = ex0 + lk[0] * 0.008 * sc, ey + lk[1] * 0.007
                E(ix, iy, irs * sc, min(irs, ry * op * 0.95), col["iris"], o=False)
                E(ix, iy, irs * 0.5 * sc, min(irs * 0.5, ry * op * 0.6), (14, 10, 12), o=False)
                E(ix + 0.005 * sc, iy - 0.006 * op, 0.0045 * sc, 0.0045 * op, (255, 255, 255), o=False)
            # upper lid
            pts = [(ex0 + rx * math.cos(a), ey + ry * op * math.sin(a)) for a in np.linspace(math.pi * 1.02, math.pi * 1.98, 10)]
            pline(img, LP(pts, True), ol, lw * (1.9 if who == "mia" else 1.4))
            if who == "mia": pline(img, LP([pts[-1], (pts[-1][0] + sx * 0.008, pts[-1][1] - 0.006)], True), ol, lw * 1.2)
            if ex == "creepy": pline(img, LP([(ex0 - rx, ey + 0.012), (ex0, ey + 0.004), (ex0 + rx, ey + 0.012)], True), ol, lw)
        # brows
        bi, bo = BR.get(ex, (0, 0)); by = ey - 0.038
        brows.append(((cu + sx * 0.014 * sc, by - bi), (ex0 + sx * 0.026 * sc, by - bo + 0.004)))
    # nose
    pline(img, LP([(cu + t * 0.018, -0.855), (cu + t * 0.022 + 0.004, -0.835), (cu + t * 0.012 - 0.003, -0.83)], True), shade(col["skin"], 0.62), lw * 0.9)
    # cheeks
    if ex in ("smile", "neutral", "worried", "whisper", "sad") and d > 0.6:
        for sx in (-1, 1):
            if (sx * t) < -0.3: continue
            E(cu + sx * 0.055, -0.832, 0.016, 0.008, mix(col["skin"], (230, 140, 140), 0.35), o=False)
    # mouth
    m = c.get("mouth", 0.0); my = -0.808; mw = 0.024 * (1 - 0.3 * abs(t))
    if ex == "creepy":
        gw = 0.05; op2 = 0.006 + 0.016 * m
        top = [(cu + gw * x, my - 0.004 - 0.012 * (1 - x * x)) for x in np.linspace(-1, 1, 14)]
        bot = [(cu + gw * x, my - 0.004 + op2 + 0.012 * (1 - x * x) * 0.4) for x in np.linspace(1, -1, 14)]
        poly(img, LP(top + bot, True), (70, 14, 18), ol, lw)
        poly(img, LP([(cu - gw * 0.85, my - 0.012), (cu + gw * 0.85, my - 0.012), (cu + gw * 0.8, my - 0.004 + op2 * 0.3), (cu - gw * 0.8, my - 0.004 + op2 * 0.3)], True), (236, 230, 212), None, 0)
        for k in np.linspace(-0.7, 0.7, 7): pline(img, LP([(cu + gw * k, my - 0.016), (cu + gw * k, my - 0.004 + op2 * 0.3)], True), (150, 130, 120), lw * 0.5)
        pline(img, LP(top, True), ol, lw * 1.2)
    elif m > 0.08 or ex == "scared":
        oh = 0.004 + 0.016 * max(m, 0.35 if ex == "scared" else 0.0)
        E(cu + t * 0.01, my + oh * 0.3, mw * (0.75 if ex == "whisper" else 1.12), oh, (92, 26, 34))
        if oh > 0.012: E(cu + t * 0.01, my + oh * 0.85, mw * 0.55, oh * 0.35, (200, 96, 100), o=False)
    else:
        curve = {"smile": 0.008, "neutral": 0.002, "sad": -0.005, "worried": -0.003, "cold": 0.0, "sleep": 0.002, "whisper": -0.002}.get(ex, 0)
        pline(img, LP([(cu - mw + t * 0.01, my), (cu + t * 0.01, my + curve), (cu + mw + t * 0.01, my)], True), shade(col["lips"], 0.7), lw * 1.3)
    # front hair
    h = col["hair"]; g = t * 0.03
    if who == "mia":
        for sx in (-1, 1):
            SP([(sx * 0.088 + g * 0.3, -0.9), (sx * 0.112 + g * 0.3, -0.82), (sx * 0.118, -0.72), (sx * 0.112, -0.635), (sx * 0.097, -0.69), (sx * 0.09 + g * 0.3, -0.8)], h)
        SP([(-0.1 + g * 0.2, -0.83), (-0.108 + g * 0.2, -0.9), (-0.08, -0.955), (-0.03, -0.984), (0.03, -0.986), (0.08, -0.96), (0.107 + g * 0.2, -0.905), (0.103 + g * 0.2, -0.83),
            (0.088 + g, -0.872), (0.058 + g, -0.902), (0.03 + g, -0.896), (-0.005 + g, -0.918), (-0.045 + g, -0.905), (-0.078 + g, -0.88), (-0.092 + g * 0.5, -0.85)], h)
        pline(img, smooth(LP([(-0.04, -0.965), (-0.01 + g, -0.95), (0.02 + g, -0.93)], True), closed=False), shade(h, 1.8), lw * 0.9)
    else:
        SP([(-0.1, -0.83), (-0.104, -0.91), (-0.06, -0.97), (0.02, -0.984), (0.08, -0.96), (0.106, -0.9), (0.104, -0.82), (0.09 + g, -0.875), (0.04 + g, -0.92), (-0.03 + g, -0.925), (-0.08 + g * 0.5, -0.89)], h)
        SP([(0.094, -0.88), (0.112, -0.8), (0.104, -0.76), (0.09, -0.82)], h)
    for a_, b_ in brows: SG(a_, b_, 0.0085 if who == "mia" else 0.007, shade(h, 0.75), head=True, o=False)
    if view == "front" and not ho: arms()
    if pose in ("phone", "phone2"):
        poly(img, LP([(0.008, -0.66), (0.062, -0.66), (0.062, -0.57), (0.008, -0.57)]), (28, 28, 34), ol, lw)
        poly(img, LP([(0.014, -0.654), (0.056, -0.654), (0.056, -0.578), (0.014, -0.578)]), (190, 214, 255) if c.get("screen", True) else (30, 30, 40), None, 0)
        E(0.035, -0.6, 0.02, 0.022, col["skin"], head=False)
    if pose == "box":
        poly(img, LP([(-0.13, -0.64), (0.13, -0.64), (0.13, -0.46), (-0.13, -0.46)]), _dk((178, 140, 98), d), ol, lw)
        pline(img, LP([(-0.13, -0.6), (0.13, -0.6)]), _dk((140, 106, 70), d), lw * 0.8)
        for sx in (-1, 1): E(sx * 0.1, -0.56, 0.022, 0.024, col["skin"], head=False)

# ------------------------------------------------------------------ lighting
_LS = 4
_yy, _xx = np.mgrid[0:H // _LS, 0:W // _LS].astype(np.float32) * _LS + _LS / 2
_rr = np.sqrt((_xx - 540) ** 2 + (_yy - 960) ** 2)
def light(img, amb, lights, vig=0.6):
    """lights: dict(x,y,r,I,c, soft) in screen px"""
    L = np.ones((H // _LS, W // _LS, 3), np.float32) * np.array(amb, np.float32)
    for l in lights:
        d = np.sqrt((_xx - l["x"]) ** 2 + ((_yy - l["y"]) * l.get("sy", 1.0)) ** 2) / max(l["r"], 1)
        f = np.clip(1 - d, 0, 1) ** l.get("p", 1.6)
        L += f[..., None] * (np.array(l.get("c", (1.0, 0.9, 0.75)), np.float32) * l["I"])
    if vig > 0: L *= (1 - vig * np.clip((_rr - 520) / 700, 0, 1) ** 1.5)[..., None]
    L = cv2.resize(cv2.GaussianBlur(L, (0, 0), 2.0), (W, H), interpolation=cv2.INTER_LINEAR)
    return np.clip(img.astype(np.float32) * L, 0, 255).astype(np.uint8)

def glow(img, x, y, r, color=(230, 240, 255), I=1.0):
    r = max(2, int(r)); x0, y0 = int(x) - 3 * r, int(y) - 3 * r
    yy, xx = np.mgrid[0:6 * r, 0:6 * r].astype(np.float32); d = np.sqrt((xx - 3 * r) ** 2 + (yy - 3 * r) ** 2) / r
    a = (np.clip(1.15 - d, 0, 1) ** 0.6 + 0.35 * np.exp(-d * 1.2)) * I
    ys, xs = slice(max(0, y0), min(H, y0 + 6 * r)), slice(max(0, x0), min(W, x0 + 6 * r))
    if ys.start >= ys.stop or xs.start >= xs.stop: return
    a = a[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0, None]
    reg = img[ys, xs].astype(np.float32); img[ys, xs] = np.clip(reg + (np.array(color, np.float32) - reg * 0.3) * a, 0, 255).astype(np.uint8)

def emissive(img, emis, I=1.0):
    for e in emis:
        if e[0] == "glow":
            p = V.P([e[1]])[0]; glow(img, p[0], p[1], e[2] * V.z * 0.5, (240, 246, 255), I)

# ------------------------------------------------------------------ post
_rng = np.random.default_rng(7)
_GR = [(_rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)) for _ in range(6)]
_vg = (1 - 0.5 * np.clip((np.sqrt((np.mgrid[0:H, 0:W][1] - 540.0) ** 2 + ((np.mgrid[0:H, 0:W][0] - 960.0) * 0.62) ** 2) - 380) / 640, 0, 1) ** 1.8).astype(np.float32)
def post(img, fi, grain=7.0, ca=0.0, grade=(1.0, 1.0, 1.0), lift=(6, 8, 14)):
    f = img.astype(np.float32) * _vg[..., None]
    f = f * np.array(grade, np.float32) + np.array(lift, np.float32) * (1 - f / 255)
    g = cv2.resize(_GR[(fi // 2) % 6], (W, H), interpolation=cv2.INTER_LINEAR) * grain * 0.55
    f += g[..., None]
    out = np.clip(f, 0, 255).astype(np.uint8)
    if ca > 0:
        k = int(ca); out[:, k:, 0] = out[:, :-k, 0].copy(); out[:, :-k, 2] = out[:, k:, 2].copy()
    return out

def blur(img, k):
    if k < 0.5: return img
    return cv2.GaussianBlur(img, (0, 0), k)

# ------------------------------------------------------------------ text
def text(img, s, x, y, sz, color=(255, 255, 255), a=1.0, stroke=0, sc=(0, 0, 0), anchor="mm", bold=True, spacing=6, align="center"):
    if a <= 0.01: return img
    pil = Image.fromarray(img); lay = Image.new("RGBA", pil.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    dr.multiline_text((x, y), s, font=font(sz, bold), fill=color + (int(255 * a),), anchor=anchor, align=align, stroke_width=stroke, stroke_fill=sc + (int(255 * a),), spacing=spacing)
    pil = Image.alpha_composite(pil.convert("RGBA"), lay).convert("RGB"); img[:] = np.asarray(pil)
    return img
def wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out
