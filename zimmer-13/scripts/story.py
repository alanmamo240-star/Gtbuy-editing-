"""Episode 1 timeline: line start times, sfx cues, shots."""
import json, math, numpy as np
from engine import *
from sets import *
from lines import LINES

META = json.load(open("build/lines.json"))
START = dict(n1=0.5, m1=9.6, m2=12.0, m3=15.75, mia1=17.45, n2=19.3, n3=21.9, d1=28.1, n4=31.3, mia2=40.85, f1=43.3, f2=48.0, c1=57.9)
END_BLACK, CARD, DUR = 63.0, 63.9, 67.2
KNOCKS = (25.4, 26.1, 26.8)
BUZZ = (41.95, 47.55)
MSG = (42.9, 47.6)
LIGHT_ON = 53.7

def mouth(key, t):
    a = t - START[key]; e = META[key]["env"]; i = int(a * 30)
    return e[i] if 0 <= i < len(e) else 0.0
def talking(keys, t): return max(mouth(k, t) for k in keys)
def blink(t, seed=0.0):
    ph = (t + seed * 1.7) % 3.7; return clamp(1 - abs(ph - 0.08) / 0.08)
def cu(who, hx, hy, s):
    """feet position so that head centre lands at (hx,hy)"""
    return dict(who=who, x=hx, y=hy + 0.865 * s * CH[who]["h"], s=s)
def nz(t, f=7.0, seed=0): return 0.5 + 0.5 * math.sin(t * f + seed) * math.sin(t * f * 1.73 + 2 * seed)

AMB_N = (0.25, 0.28, 0.45)
def dark_hall_lights(under, extra=()):
    q = door_screen_rect(); bx = q[:, 0].mean(); by = q[:, 1].max(); w = abs(q[1, 0] - q[0, 0])
    L = [dict(x=bx, y=by, r=w * 1.4, I=0.9 * under, c=(0.75, 0.85, 1.0), sy=2.2), dict(x=bx, y=by - w * 0.5, r=w * 2.4, I=0.25 * under, c=(0.6, 0.7, 1.0))]
    return L + list(extra)

# ------------------------------------------------------------------ shots: each returns (img, opts)
def sh_hook(t):
    img = np.zeros((H, W, 3), np.uint8); z = kf(t, [(0, 1.15), (9.2, 2.0)]); setview(View(540, kf(t, [(0, 900), (9.2, 820)]), z))
    u = 0.75 + 0.25 * nz(t, 9)
    hallway(img, "night", "door", plate13=1.0, under=u)
    x, y, s = feet(0.0, 3.5); char(img, dict(who="mia", x=x, y=y, s=s, view="back", bob=0.004 * math.sin(t * 2)))
    img = light(img, AMB_N, dark_hall_lights(u))
    return img, dict(grain=8)

def sh_movein(t):
    img = np.zeros((H, W, 3), np.uint8)
    z = kf(t, [(9.2, 1.12), (12.2, 1.18), (14.6, 2.7), (15.5, 2.8)]); cy = kf(t, [(9.2, 980), (12.2, 980), (14.6, 800)]); setview(View(540, cy, z))
    hallway(img, "day", "door", plate13=0.0, boxes=True)
    x, y, s = feet(-0.62, 1.55); char(img, dict(who="mia", x=x, y=y, s=s, pose="box", turn=0.45, look=(0.7, 0), expr=kf(t, [(9.2, 0), (13, 1)]) > 0.5 and "worried" or "neutral", blink=blink(t, 1)))
    x, y, s = feet(0.62, 1.32); char(img, dict(who="mom", x=x, y=y, s=s, turn=-0.4, look=(-0.6, 0), expr="neutral", mouth=talking(("m1", "m2"), t), blink=blink(t, 2)))
    img = light(img, (0.78, 0.72, 0.68), [dict(x=150, y=700, r=900, I=0.35, c=(1.0, 0.8, 0.55))], vig=0.5)
    return img, dict(grain=6, grade=(1.0, 0.96, 0.92))

def bg_day_blur(z=2.6, cy=800, k=9):
    img = np.zeros((H, W, 3), np.uint8); setview(View(540, cy, z)); hallway(img, "day", "door", plate13=0.0, boxes=True); return blur(img, k)
_BG = {}
def cached(key, fn):
    if key not in _BG: _BG[key] = fn()
    return _BG[key].copy()

def sh_mom_cu(t):
    img = cached("daycu", lambda: bg_day_blur(2.0, 900, 10)); setview(View())
    s = kf(t, [(15.5, 2500), (17.2, 2620)])
    tt = kf(t, [(18.8, -0.15), (20.3, -0.15), (20.9, 0.75)]) if t > 18 else -0.15
    lk = (0.5, 0.35) if t > 19.4 else (-0.15, 0)
    ex = "cold" if t > 18 else "neutral"
    char(img, dict(cu("mom", 560, 760, s), turn=tt, look=lk, expr=ex, mouth=talking(("m3",), t), blink=blink(t, 0.4)))
    img = light(img, (0.74, 0.68, 0.66), [dict(x=200, y=600, r=900, I=0.32, c=(1.0, 0.8, 0.55))], vig=0.6)
    return img, dict(grain=6, grade=(1.0, 0.95, 0.9))

def sh_mia_cu_day(t):
    img = cached("daycu2", lambda: bg_day_blur(1.6, 1000, 10)); setview(View())
    s = kf(t, [(17.2, 2500), (18.8, 2580)])
    char(img, dict(cu("mia", 520, 760, s), turn=-0.25, look=(-0.55, 0), expr="worried", mouth=talking(("mia1",), t), blink=blink(t, 0.9)))
    img = light(img, (0.74, 0.68, 0.66), [dict(x=900, y=600, r=900, I=0.3, c=(1.0, 0.8, 0.55))], vig=0.6)
    return img, dict(grain=6, grade=(1.0, 0.95, 0.9))

def moon_lights(): return [dict(x=540, y=520, r=900, I=0.55, c=(0.55, 0.65, 1.0)), dict(x=540, y=1350, r=700, I=0.25, c=(0.5, 0.6, 1.0))]
def sh_bed_lying(t):
    img = np.zeros((H, W, 3), np.uint8); z = kf(t, [(21.6, 1.35), (KNOCKS[0], 1.6), (26.6, 1.75)]); sx = 0.0
    if t > KNOCKS[0]: sx += 7 * math.sin(t * 90) * clamp(1 - (t - KNOCKS[0]) / 0.22)
    if t > KNOCKS[1]: sx += 9 * math.sin(t * 90) * clamp(1 - (t - KNOCKS[1]) / 0.22)
    setview(View(470 + sx, 1260, z))
    bedroom(img); bed(img)
    ell(img, 330, 1330, 230, 90, (240, 238, 234))   # pillow
    awake = t > KNOCKS[0] + 0.12; s = 1500; hx, hy = 360, 1290
    char(img, dict(who="mia", x=hx + 0.865 * s, y=hy + 0.0, s=s, scale_h=False, rot=-90, headonly=True, expr="scared" if awake else "sleep", look=(0.0, -0.7) if awake else (0, 0), blink=0.0))
    poly(img, smooth([(470, 1235), (700, 1170), (1100, 1190), (1130, 1720), (420, 1730), (440, 1420)], 6), (98, 110, 160))
    for k in range(3): pline(img, smooth([(560 + k * 190, 1220), (540 + k * 200, 1450), (580 + k * 190, 1700)], closed=False), (76, 86, 130), 3)
    img = light(img, (0.2, 0.23, 0.38), moon_lights() + [dict(x=540, y=1100, r=700, I=0.35, c=(0.55, 0.65, 1.0))])
    return img, dict(grain=8)

def bed_sit(img, t, s, hx, hy, **kw):
    bedroom(img); bed(img); char(img, dict(cu("mia", hx, hy, s), **kw))
    by = hy + 0.43 * s; poly(img, smooth([(-100, by), (300, by - 40), (800, by - 20), (1200, by + 10), (1200, 2400), (-100, 2400)], 6), (98, 110, 160))
def sh_bed_sit(t):
    img = np.zeros((H, W, 3), np.uint8); setview(View(540, 960, 1.0))
    if t > KNOCKS[2]: setview(View(540 + 8 * math.sin(t * 90) * clamp(1 - (t - KNOCKS[2]) / 0.25), 960, 1.0))
    look = (0.8, -0.1) if t > KNOCKS[2] + 0.1 else (0.2, 0)
    bed_sit(img, t, 1250, 540, 900, expr="scared", turn=0.35 if t > KNOCKS[2] + 0.1 else 0.0, look=look, pose="clutch")
    img = light(img, (0.16, 0.19, 0.33), moon_lights())
    return img, dict(grain=8)

def sh_door(t):
    img = np.zeros((H, W, 3), np.uint8); z = kf(t, [(27.8, 1.0), (31.0, 1.22)]); setview(View(540, 1150, z))
    u = 0.65 + 0.35 * nz(t, 13)
    if START["d1"] < t < START["d1"] + 2.3: u = 0.8 + 0.2 * mouth("d1", t)
    door_cu(img, under=u)
    S = cur().P([(540, 1840)])[0]
    img = light(img, (0.26, 0.28, 0.42), [dict(x=S[0], y=S[1], r=800 * z, I=1.3 * u, c=(0.7, 0.8, 1.0), sy=2.5), dict(x=540, y=500, r=1000, I=0.25, c=(0.6, 0.7, 1.0))])
    [glow(img, S[0] + dx * z, S[1], 26 * z, (210, 225, 255), 0.22 * u) for dx in (-240, -120, 0, 120, 240)]
    return img, dict(grain=9)

def sh_bed_cu(t):
    img = np.zeros((H, W, 3), np.uint8); setview(View(540, 760, kf(t, [(31.0, 1.0), (33.6, 1.25)])))
    bed_sit(img, t, 2300, 540, 760, expr="scared", turn=0.2, look=(0.7, 0), pose="clutch", blink=0.0)
    img = light(img, (0.14, 0.17, 0.3), [dict(x=540, y=300, r=1100, I=0.6, c=(0.55, 0.65, 1.0))])
    return img, dict(grain=9)

def sh_walk(t):
    img = np.zeros((H, W, 3), np.uint8); a = (t - 33.6) / 4.2; setview(View(540, 900, lerp(1.0, 1.3, ease(a))))
    u = 0.7 + 0.3 * nz(t, 9)
    hallway(img, "night", "door", plate13=0.0, under=u)
    z = lerp(1.55, 3.7, ease(a) * 0.5 + a * 0.5); x, y, s = feet(0.05, z)
    char(img, dict(who="mia", x=x, y=y, s=s, view="back", walk=t * 2 * math.pi * 0.55, bob=-0.004 * abs(math.sin(t * math.pi * 1.1))))
    img = light(img, AMB_N, dark_hall_lights(u))
    return img, dict(grain=8)

def sh_sign(t):
    img = np.zeros((H, W, 3), np.uint8); z = kf(t, [(37.8, 2.6), (39.6, 3.3), (40.6, 3.0)]); setview(View(540, 140, z))
    door_cu(img, under=0.7)
    r = clamp((t - 38.2) / 1.1)
    if r > 0:
        q = cur().P([(540, 70)])[0]; jit = (np.random.default_rng(int(t * 30)).normal(0, 3, 2) if r < 1 else (0, 0))
        text(img, "13", q[0] + jit[0], q[1] + jit[1], int(96 * cur().z), (24, 10, 8), r if r < 1 else 1.0)
    img = light(img, (0.34, 0.34, 0.46), [dict(x=540, y=600, r=1300, I=0.5, c=(0.75, 0.82, 1.0))])
    return img, dict(grain=9, ca=3 if 38.3 < t < 39.4 and int(t * 12) % 3 == 0 else 0)

def bg_night_door_blur():
    img = np.zeros((H, W, 3), np.uint8); setview(View(540, 900, 1.6)); hallway(img, "night", "door", plate13=1.0, under=0.9); return blur(img, 9)
def sh_mia_whisper(t):
    img = cached("ndoor", bg_night_door_blur); setview(View(540, 960, kf(t, [(40.6, 1.0), (42.6, 1.12)])))
    flinch = t > BUZZ[0]
    char(img, dict(cu("mia", 540, 820, 2400), expr="whisper" if not flinch else "scared", look=(0, 0.8) if flinch else (0.1, -0.2), mouth=talking(("mia2",), t), pose="phone", screen=flinch, blink=blink(t, 1.3) if not flinch else 0))
    L = [dict(x=540, y=2000, r=1200, I=0.55, c=(0.6, 0.7, 1.0))]
    if flinch: L.append(dict(x=600, y=1500, r=900, I=0.9, c=(0.7, 0.82, 1.0)))
    img = light(img, (0.14, 0.16, 0.28), L)
    return img, dict(grain=9)

def sh_phone(t):
    img = cached("ndoor2", lambda: blur(bg_night_door_blur(), 12)); setview(View(540 + 8 * math.sin(t * 0.7), 900 + 10 * math.sin(t * 0.5), 1.0 + 0.015 * (t - 42.6)))
    phone_cu(img, t, [])
    img = light(img, (0.16, 0.18, 0.3), [dict(x=540, y=900, r=900, I=0.9, c=(0.7, 0.8, 1.0))], vig=0.4)
    msgs = [("Geh nicht rein. Ich bin du. Aus der Zukunft.", t - MSG[0])] if t > MSG[0] else []
    if t > MSG[1]: msgs.append(("Deine Mutter ist nicht die, für die du sie hältst.", t - MSG[1]))
    phone_ui(img, t, msgs)
    return img, dict(grain=7)

def sh_reveal(t):
    rf = clamp((t - 54.6) / 1.0); push = ease((t - 56.2) / 1.4)
    img = np.zeros((H, W, 3), np.uint8); setview(View(540, lerp(900, 840, push), lerp(1.0, 1.9, push)))
    on = clamp((t - LIGHT_ON) / 0.12) * (1 if t < LIGHT_ON + 0.1 or t > LIGHT_ON + 0.35 or int(t * 30) % 2 else 0.3)
    hallway(img, "night", "entrance", front_glow=on)
    emis = []
    if on > 0:
        x, y, s = feet(0.0, 4.7); char(img, dict(who="mom", x=x, y=y, s=s, expr="creepy", dark=0.12, tilt=-6), emis)
    img = blur(img, lerp(7, 0, ease(rf)))
    q = cur().P([(540, 900)])[0]
    L = [dict(x=q[0], y=q[1] + 50 * cur().z, r=450 * cur().z, I=1.2 * on, c=(1.0, 0.72, 0.42))]
    # foreground Mia (screen space)
    setview(View()); tr = kf(t, [(55.1, 0.0), (56.3, -0.95)])
    fg = dict(cu("mia", lerp(300, 120, push), lerp(980, 1200, push), lerp(2600, 3200, push)), pose="phone", look=(0, 0.8) if t < 55.0 else (-0.9, 0), expr="scared" if t > 54.8 else "worried", screen=True)
    if t < 56.35: char(img, dict(fg, turn=tr))
    else: char(img, dict(fg, view="back"))
    L.append(dict(x=lerp(330, 150, push), y=lerp(1650, 1900, push), r=800, I=0.7 if t < 56.35 else 0.3, c=(0.7, 0.82, 1.0)))
    img = light(img, (0.14, 0.15, 0.27), L)
    if on > 0:
        setview(View(540, lerp(900, 840, push), lerp(1.0, 1.9, push))); emissive(img, emis, on)
    return img, dict(grain=9)

def sh_mom_creepy(t):
    img = np.zeros((H, W, 3), np.uint8); setview(View(540, 900, 1.0)); hallway(img, "night", "entrance", front_glow=1.0); img = blur(img, 6)
    setview(View(540, 960, kf(t, [(57.6, 1.0), (62.0, 1.35)])))
    emis = []
    char(img, dict(cu("mom", 540, 840, 2500), expr="creepy", dark=0.5, tilt=kf(t, [(57.6, -3), (62, -14)]), mouth=talking(("c1",), t)), emis)
    img = light(img, (0.2, 0.18, 0.26), [dict(x=540, y=200, r=900, I=0.7, c=(1.0, 0.7, 0.45)), dict(x=540, y=1900, r=900, I=0.3, c=(0.6, 0.7, 1.0))])
    emissive(img, emis, 1.0)
    return img, dict(grain=10, ca=2 + 3 * mouth("c1", t))

def sh_end(t):
    img = cached("ndoor", bg_night_door_blur); setview(View(540, 960, kf(t, [(62.0, 1.0), (63.0, 1.15)])))
    char(img, dict(cu("mia", 540, 820, 2400), expr="scared", look=(0.0, -0.2), pose="clutch"))
    fl = 1.0 if t < 62.5 else (0.25 if int(t * 24) % 2 else 1.0)
    img = light(img, (0.14 * fl, 0.16 * fl, 0.28 * fl), [dict(x=540, y=1500, r=900, I=0.8 * fl, c=(0.7, 0.82, 1.0))])
    return img, dict(grain=10)

SHOTS = [(0, 9.2, sh_hook), (9.2, 15.5, sh_movein), (15.5, 17.2, sh_mom_cu), (17.2, 18.8, sh_mia_cu_day), (18.8, 21.6, sh_mom_cu),
         (21.6, 26.6, sh_bed_lying), (26.6, 27.8, sh_bed_sit), (27.8, 31.0, sh_door), (31.0, 33.6, sh_bed_cu), (33.6, 37.8, sh_walk),
         (37.8, 40.6, sh_sign), (40.6, 42.6, sh_mia_whisper), (42.6, 52.2, sh_phone), (52.2, 57.6, sh_reveal), (57.6, 62.0, sh_mom_creepy), (62.0, END_BLACK, sh_end)]
CUTS = [a for a, b, f in SHOTS[1:]]

CAPCOL = dict(narr=(255, 238, 205), mom=(255, 255, 255), mia=(255, 255, 255), whisper=(220, 230, 255), door=(190, 215, 255), future=(170, 225, 255), creepy=(255, 96, 96))
def chunks(text):
    out, cur = [], ""
    for w in text.split():
        if cur and (len(cur) + len(w) > 15 or cur.count(" ") >= 2 or cur[-1] in ".?!,…"): out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out
def caption(t):
    for k, st in START.items():
        sp, tx, cap = LINES[k]; d = META[k]["dur"]
        if st <= t <= st + d + 0.2:
            ch = chunks(cap or tx); tot = sum(len(x) + 3 for x in ch); u = (t - st) / d; acc = 0.0
            for x in ch:
                w = (len(x) + 3) / tot
                if acc <= u < acc + w or (x is ch[-1] and u >= acc): return x, CAPCOL[sp], clamp((u - acc) * d / 0.1)
                acc += w
    return None
