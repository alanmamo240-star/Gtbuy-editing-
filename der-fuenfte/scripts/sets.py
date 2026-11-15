"""Sets for the series: Alan's room, hallway (front door, intercom, mirror), stairwell (peephole view), street (window view)."""
import numpy as np, cv2, math
from eng import *

WALL, CEIL, FLOOR = (178, 150, 92), (150, 142, 122), (150, 62, 44)
CREAM, WOOD, DARK = (222, 214, 196), (140, 100, 62), (12, 12, 16)

def obj(objs, cam, anchor, fn): objs.append((cam.dist(anchor), fn))

def window(img, cam, emis, x0, x1, y0, y1, z, lit=((1, 1),)):
    poly(img, cam, rz(x0, x1, y0, y1, z - 0.01), (26, 30, 58), OUTL, 4)
    bw = (x1 - x0)
    poly(img, cam, rz(x0, x1, y0, y0 + (y1 - y0) * 0.78, z - 0.012), (58, 62, 90), None, 0)
    for i in range(4):
        for j in range(3):
            wx = x0 + bw * (0.1 + 0.225 * i); wy = y0 + (y1 - y0) * (0.08 + 0.24 * j)
            p = rz(wx, wx + bw * 0.12, wy, wy + (y1 - y0) * 0.14, z - 0.014)
            if (i, j) in lit: emis.append(lambda p=p: poly(img, cam, p, (244, 204, 112), OUTL, 2))
            else: poly(img, cam, p, (24, 26, 44), None, 0)
    t = 0.05
    for p in [rz(x0 - t, x0 + t, y0, y1, z - 0.03), rz(x1 - t, x1 + t, y0, y1, z - 0.03), rz(x0, x1, y1 - t, y1 + t, z - 0.03), rz(x0, x1, y0 - t, y0 + t, z - 0.03),
              rz((x0 + x1) / 2 - 0.03, (x0 + x1) / 2 + 0.03, y0, y1, z - 0.03), rz(x0, x1, y0 + (y1 - y0) * 0.62 - 0.03, y0 + (y1 - y0) * 0.62 + 0.03, z - 0.03)]:
        poly(img, cam, p, CREAM, OUTL, 3)

def set_zimmer(img, cam, st, objs, emis):
    room(img, cam, -2.0, 2.0, 0, 4.4, 2.5, WALL, FLOOR, CEIL, planks=0.34)
    poly(img, cam, ry(-0.9, 0.6, 1.2, 3.3, 0.004), (52, 62, 104), OUTL, 4)
    window(img, cam, emis, -1.3, 0.1, 0.95, 2.1, 4.4)
    poly(img, cam, rx(1.3, 2.0, 1.2, 2.1, -1.99), (70, 96, 120), OUTL, 4)              # poster
    poly(img, cam, rz(-1.7, -0.75, 0, 2.02, 0.01), shade(WOOD, 0.8), OUTL, 4)          # room door (back wall)
    poly(img, cam, rz(-1.62, -0.83, 0, 1.96, 0.02), CREAM, OUTL, 4)
    lamp = disc((0, 2.49, 2.2), 0.3)
    if st.get("lamp", 0) > 0.5: emis.append(lambda: poly(img, cam, lamp, (255, 236, 170), OUTL, 4))
    else: poly(img, cam, lamp, (196, 190, 172), OUTL, 4)
    obj(objs, cam, (-0.6, 0.3, 4.3), lambda: box(img, cam, (-1.25, 0.12, 4.22), (0.05, 0.8, 4.38), (206, 200, 190)))
    obj(objs, cam, (1.3, 0.3, 2.7), lambda: (box(img, cam, (0.7, 0, 1.6), (1.97, 0.42, 3.95), (56, 68, 112), top=(70, 86, 140)),
                                             box(img, cam, (0.9, 0.42, 3.35), (1.8, 0.58, 3.85), (226, 222, 210))))
    obj(objs, cam, (-1.5, 0.7, 2.8), lambda: (box(img, cam, (-1.97, 0, 2.0), (-1.15, 0.74, 3.6), shade(WOOD, 0.9), top=WOOD),
                                              box(img, cam, (-1.9, 0.74, 2.5), (-1.82, 1.3, 3.2), (26, 28, 36))))
    obj(objs, cam, (1.6, 1.0, 0.6), lambda: box(img, cam, (1.2, 0, 0.1), (1.97, 2.0, 1.1), (200, 190, 168)))

def door(img, cam, x0, x1, z, opn=0.0, handle=0.0, color=CREAM, peep=True, hinge=1):
    poly(img, cam, rz(x0 - 0.08, x1 + 0.08, 0, 2.13, z - 0.005), shade(WOOD, 0.75), OUTL, 4)
    w = x1 - x0
    if opn > 0.01:
        poly(img, cam, rz(x0, x1, 0, 2.05, z - 0.008), (10, 12, 16), OUTL, 3)
        a = math.radians(84 * opn); hx = x1 if hinge == 1 else x0; sx = -1 if hinge == 1 else 1
        ex, ez = hx + sx * w * math.cos(a), z - 0.02 - w * math.sin(a)
        poly(img, cam, [(hx, 0, z - 0.02), (ex, 0, ez), (ex, 2.05, ez), (hx, 2.05, z - 0.02)], shade(color, 0.8), OUTL, 4); return
    zz = z - 0.012
    poly(img, cam, rz(x0, x1, 0, 2.05, zz), color, OUTL, 4)
    for (a, b) in [(1.15, 1.92), (0.12, 0.98)]: poly(img, cam, rz(x0 + 0.13, x1 - 0.13, a, b, zz - 0.004), None, shade(color, 0.7), 3)
    hx = x0 + 0.09
    poly(img, cam, rz(hx - 0.035, hx + 0.035, 0.9, 1.14, zz - 0.006), (150, 140, 110), OUTL, 2)
    ha = math.radians(-38 * handle)
    line3(img, cam, (hx, 1.06, zz - 0.05), (hx + 0.15 * math.cos(ha), 1.06 + 0.15 * math.sin(ha), zz - 0.05), (60, 56, 50), 7)
    if peep:
        poly(img, cam, disc(((x0 + x1) / 2, 1.52, zz - 0.006), 0.036, "z", 12), (170, 150, 90), OUTL, 2)
        poly(img, cam, disc(((x0 + x1) / 2, 1.52, zz - 0.008), 0.018, "z", 10), (14, 14, 18), None, 0)

def intercom_quad(): return rz(0.635, 0.845, 1.43, 1.60, 6.2 - 0.055)

def set_flur(img, cam, st, objs, emis):
    X, Z = 0.95, 6.2
    room(img, cam, -X, X, 0, Z, 2.5, WALL, FLOOR, CEIL, planks=0.27)
    poly(img, cam, ry(-0.46, 0.46, 0.9, 5.4, 0.004), (118, 40, 36), OUTL, 4)
    poly(img, cam, ry(-0.38, 0.38, 0.98, 5.32, 0.006), None, (150, 70, 56), 3)
    door(img, cam, -0.5, 0.5, Z, st.get("door", 0.0), st.get("handle", 0.0))
    # intercom
    poly(img, cam, rz(0.60, 0.88, 1.24, 1.66, Z - 0.02), (214, 212, 206), OUTL, 3)
    for k in range(3): poly(img, cam, disc((0.67 + 0.07 * k, 1.33, Z - 0.03), 0.02, "z", 10), (120, 120, 124) if k else (90, 150, 110), OUTL, 2)
    if st.get("icom") is not None: emis.append(lambda: tex_quad(img, cam, intercom_quad(), st["icom"]))
    else: poly(img, cam, rz(0.635, 0.845, 1.43, 1.60, Z - 0.03), (20, 22, 28), OUTL, 2)
    poly(img, cam, rz(-0.86, -0.76, 1.2, 1.32, Z - 0.02), (220, 216, 206), OUTL, 2)                  # light switch
    # back wall: dark doorway to living room
    poly(img, cam, rz(-0.5, 0.5, 0, 2.08, 0.012), shade(WOOD, 0.75), OUTL, 4); poly(img, cam, rz(-0.43, 0.43, 0, 2.02, 0.02), DARK, OUTL, 3)
    # right wall: doorway to Alan's room, shoe cabinet
    poly(img, cam, rx(0.9, 1.9, 0, 2.08, X - 0.012), shade(WOOD, 0.75), OUTL, 4); poly(img, cam, rx(0.97, 1.83, 0, 2.02, X - 0.02), DARK, OUTL, 3)
    obj(objs, cam, (0.78, 0.4, 4.9), lambda: box(img, cam, (0.6, 0, 4.3), (0.945, 0.82, 5.5), (196, 186, 164)))
    # left wall: mirror, coat rack
    mz0, mz1, my0, my1 = 2.55, 3.35, 0.45, 1.95
    poly(img, cam, rx(mz0 - 0.05, mz1 + 0.05, my0 - 0.05, my1 + 0.05, -X + 0.012), shade(WOOD, 0.9), OUTL, 4)
    poly(img, cam, rx(mz0, mz1, my0, my1, -X + 0.02), (74, 86, 104), OUTL, 3)
    for r in st.get("mirror", []):
        zc = lerp(mz0, mz1, r["u"]); s = r["s"]; yh = my0 + 0.98 * (my1 - my0) * r.get("v", 0.62); xx = -X + 0.026
        hood = shade(CH[r["ch"]]["hood"], r.get("dark", 0.75))
        poly(img, cam, [(xx, max(my0, yh - 0.62 * s), zc - 0.26 * s), (xx, yh - 0.17 * s, zc - 0.2 * s), (xx, yh - 0.12 * s, zc + 0.2 * s) if False else (xx, yh - 0.17 * s, zc + 0.2 * s), (xx, max(my0, yh - 0.62 * s), zc + 0.26 * s)], hood, OUTL, 3)
        poly(img, cam, disc((xx - 0.002 + 0.004, yh, zc), 0.15 * s, "x", 16), shade(CH[r["ch"]]["skin"], r.get("dark", 0.75)), OUTL, 3)
        if r["ch"] != "shadow":
            hr = [(xx + 0.006, yh + 0.15 * s * math.sin(q), zc + 0.155 * s * math.cos(q)) for q in np.linspace(0.12, math.pi - 0.12, 10)] + [(xx + 0.006, yh + 0.055 * s, zc - 0.06 * s), (xx + 0.006, yh + 0.07 * s, zc + 0.05 * s)]
            poly(img, cam, hr, shade(CH[r["ch"]]["hair"], r.get("dark", 0.75) + 0.2), OUTL, 2)
            for sg in (-1, 1):
                poly(img, cam, disc((xx + 0.008, yh - 0.01 * s, zc + sg * 0.062 * s), 0.034 * s, "x", 10), shade((235, 235, 230), r.get("dark", 0.75)), OUTL, 2)
                poly(img, cam, disc((xx + 0.010, yh - 0.01 * s, zc + sg * 0.062 * s), 0.014 * s, "x", 8), (20, 16, 16), None, 0)
        if r.get("eyes"):
            for sg in (-1, 1):
                e = disc((xx + 0.006, yh + 0.01 * s, zc + sg * 0.06 * s), 0.036 * s, "x", 10)
                emis.append(lambda e=e: poly(img, cam, e, (236, 232, 214), None, 0))
    line3(img, cam, (-X + 0.05, 1.8, 4.2), (-X + 0.05, 1.8, 5.5), (70, 60, 50), 6)
    for k, c in enumerate([(70, 92, 144), (150, 62, 52), (64, 112, 84)]):
        poly(img, cam, rx(4.3 + 0.4 * k, 4.62 + 0.4 * k, 0.85, 1.76, -X + 0.03 + 0.01 * k), c, OUTL, 3)
    lamp = disc((0, 2.49, 3.1), 0.26)
    if st.get("lamp", 0) > 0.5: emis.append(lambda: poly(img, cam, lamp, (255, 236, 170), OUTL, 4))
    else: poly(img, cam, lamp, (196, 190, 172), OUTL, 4)

def tex_quad(img, cam, quad, tex):
    S = cam.world(quad).astype(np.float32); h, w = tex.shape[:2]
    if cam.to_cam(quad)[:, 2].min() < 0.1: return
    src = np.float32([[0, h], [w, h], [w, 0], [0, 0]]); M = cv2.getPerspectiveTransform(src, S)
    warped = cv2.warpPerspective(tex, M, (W, H), flags=cv2.INTER_LINEAR)
    mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), M, (W, H))
    img[mask > 127] = warped[mask > 127]
    cv2.polylines(img, [np.round(S * 8).astype(np.int32).reshape(-1, 1, 2)], True, OUTL, 3, cv2.LINE_AA, 3)

SW, SF = (136, 146, 132), (124, 124, 120)
def set_treppe(img, cam, st, objs, emis):
    lv = st.get("lamp", 1.0)
    room(img, cam, -1.7, 1.7, -0.4, 3.4, 2.6, SW, SF, (150, 150, 140), tiles=0.5)
    poly(img, cam, rz(0.45, 1.7, 0.0, 2.3, 3.39), (16, 18, 22), OUTL, 4)                         # stair shaft opening
    for sa in st.get("stair_actors", []): actor(img, cam, sa, emis)
    poly(img, cam, ry(0.40, 1.70, 0.12, 3.395, 0.001), SF, None, 0)
    for xl in (0.8, 1.3): line3(img, cam, (xl, 0.003, 0.12), (xl, 0.003, 3.39), shade(SF, 0.78), 2)
    for zl in (0.6, 1.1, 1.6, 2.1, 2.6, 3.1): line3(img, cam, (0.40, 0.003, zl), (1.70, 0.003, zl), shade(SF, 0.78), 2)
    line3(img, cam, (0.45, 0.002, 3.395), (1.7, 0.002, 3.395), OUTL, 4)
    door(img, cam, -1.35, -0.45, 3.4, 0, 0, color=(70, 96, 84), peep=True)
    poly(img, cam, ry(-1.3, -0.5, 2.75, 3.25, 0.004), (88, 64, 50), OUTL, 3)
    for k in range(7): line3(img, cam, (0.5 + 0.2 * k, 0, 3.36), (0.5 + 0.2 * k, 0.95, 3.36), (40, 40, 44), 3)
    line3(img, cam, (0.45, 0.95, 3.36), (1.7, 0.95, 3.36), (40, 40, 44), 6)
    poly(img, cam, rx(1.0, 2.0, 1.0, 2.0, -1.69), (30, 36, 62), OUTL, 4)                           # small window left wall
    line3(img, cam, (-1.69, 1.0, 1.5), (-1.69, 2.0, 1.5), CREAM, 4)
    lamp = disc((0, 2.59, 1.5), 0.24)
    if lv > 0.15: emis.append(lambda: poly(img, cam, lamp, shade((255, 240, 190), 0.5 + 0.5 * lv), OUTL, 4))
    else: poly(img, cam, lamp, (170, 168, 156), OUTL, 4)

def set_strasse(img, cam, st, objs, emis):
    poly(img, cam, rz(-40, 40, 0, 30, 26), (20, 22, 44), None, 0)                                  # sky
    poly(img, cam, ry(-40, 40, 1.2, 26, 0), (60, 62, 72), None, 0)
    poly(img, cam, ry(-40, 40, 1.2, 4.6, 0.01), (112, 110, 106), OUTL, 3)
    poly(img, cam, ry(-40, 40, 11.4, 13.0, 0.01), (104, 102, 98), OUTL, 3)
    for k in range(-6, 7): poly(img, cam, ry(k * 3.0 - 0.7, k * 3.0 + 0.7, 7.9, 8.1, 0.012), (200, 198, 186), None, 0)
    if st.get("slamp", 1.0) > 0.3: poly(img, cam, disc((1.3, 0.014, 4.9), 2.3, "y", 28), (150, 140, 104), None, 0)
    box(img, cam, (-16, 0, 13.0), (16, 11, 15), (66, 70, 96), 3)
    for i in range(9):
        for j in range(4):
            p = rz(-13.5 + 3.2 * i, -12.1 + 3.2 * i, 1.3 + 2.4 * j, 2.6 + 2.4 * j, 12.98)
            if (i, j) in ((6, 2), (2, 1)): emis.append(lambda p=p: poly(img, cam, p, (240, 200, 110), OUTL, 2))
            else: poly(img, cam, p, (26, 28, 46), OUTL, 2)
    obj(objs, cam, (-4.5, 0.6, 6.0), lambda: (box(img, cam, (-6.4, 0.25, 5.2), (-2.4, 0.95, 6.9), (86, 34, 34)), box(img, cam, (-5.6, 0.95, 5.35), (-3.3, 1.5, 6.75), (70, 28, 30))))
    obj(objs, cam, (6.5, 0.6, 6.0), lambda: (box(img, cam, (4.8, 0.25, 5.2), (8.6, 0.95, 6.9), (50, 60, 84)), box(img, cam, (5.5, 0.95, 5.35), (7.8, 1.5, 6.75), (42, 50, 70))))
    def lampf():
        line3(img, cam, (1.3, 0, 3.6), (1.3, 4.7, 3.6), (40, 42, 48), 7); line3(img, cam, (1.3, 4.7, 3.6), (1.3, 4.7, 4.6), (40, 42, 48), 6)
        if st.get("slamp", 1.0) > 0.3: emis.append(lambda: box(img, cam, (1.1, 4.55, 4.4), (1.5, 4.7, 4.9), (255, 236, 170), 2))
        else: box(img, cam, (1.1, 4.55, 4.4), (1.5, 4.7, 4.9), (90, 90, 90), 2)
    obj(objs, cam, (1.3, 2.3, 3.6), lampf)
    obj(objs, cam, (-7.5, 1.5, 3.2), lambda: (line3(img, cam, (-7.5, 0, 3.2), (-7.5, 2.2, 3.2), (60, 44, 34), 8), poly(img, cam, disc((-7.5, 3.2, 3.2), 1.5, "z", 14), (34, 66, 46), OUTL, 3)))
    # interior window frame close to the camera (drawn last, after actors)
    def frame():
        cy = cam.pos[1]; z = 0.62; wl = shade(WALL, 0.9)
        for p in [rz(-6, -0.78, cy - 4, cy + 4, z), rz(0.78, 6, cy - 4, cy + 4, z), rz(-0.78, 0.78, cy + 0.72, cy + 4, z), rz(-0.78, 0.78, cy - 4, cy - 1.0, z)]: poly(img, cam, p, wl, OUTL, 4)
        t = 0.045
        for p in [rz(-0.78, -0.78 + 2 * t, cy - 1.0, cy + 0.72, z - 0.01), rz(0.78 - 2 * t, 0.78, cy - 1.0, cy + 0.72, z - 0.01), rz(-0.78, 0.78, cy + 0.72 - 2 * t, cy + 0.72, z - 0.01)
]: poly(img, cam, p, CREAM, OUTL, 4)
        box(img, cam, (-0.95, cy - 1.08, 0.32), (0.95, cy - 1.0, 0.66), CREAM)
    objs.append((-1.0, frame))

SETS = dict(zimmer=set_zimmer, flur=set_flur, treppe=set_treppe, strasse=set_strasse)

def draw_scene(st):
    img = np.zeros((H, W, 3), np.uint8)
    c = st["cam"]; cam = Cam(c["pos"], c.get("yaw", 0), c.get("pitch", 0), c.get("roll", 0), c.get("f", 620), c.get("cx", 540), c.get("cy", 940))
    objs, emis = [], []
    SETS[st["set"]](img, cam, st, objs, emis)
    for a in st.get("actors", []):
        x, z = a["pos"]; objs.append((cam.dist((x, 0.9, z)), lambda a=a: actor(img, cam, a, emis)))
    for _, fn in sorted(objs, key=lambda o: -o[0]): fn()
    spots = []
    for s in st.get("lights", []):
        if "w" in s:
            pc = cam.to_cam(np.array([s["w"]]))
            if pc[0, 2] < 0.1: continue
            p = cam.proj(pc)[0]; spots.append(dict(x=p[0], y=p[1], r=s["rw"] * cam.f / max(np.linalg.norm(pc[0]), 0.3), I=s["I"], c=s.get("c", (1.0, 0.92, 0.78)), soft=s.get("soft")))
        else: spots.append(s)
    img[:] = light(img, st.get("amb", (0.3, 0.3, 0.36)), spots, vig=st.get("peep") is None)
    for e in emis: e()
    if st.get("peep") is not None: img[:] = peephole(img, st["peep"])
    return img, cam
