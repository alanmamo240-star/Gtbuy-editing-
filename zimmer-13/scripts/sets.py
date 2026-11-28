"""Sets: one-point-perspective hallway (both directions), bedroom, door close-up, phone close-up."""
from engine import *

VP = (540.0, 900.0)           # vanishing point (world)
NEAR = dict(x0=-300.0, x1=1380.0, y0=-160.0, y1=1960.0)   # corridor cross-section at depth 1
ZF = 5.2                       # far wall depth
PX_M = (NEAR["y1"] - NEAR["y0"]) / 2.6                     # px per metre at depth 1
def pz(x, y, z): return (VP[0] + (x - VP[0]) / z, VP[1] + (y - VP[1]) / z)
def quad(x0, y0, x1, y1, z0, z1, axis):
    if axis == "x": return [pz(x0, y0, z0), pz(x0, y0, z1), pz(x0, y1, z1), pz(x0, y1, z0)]
    if axis == "y": return [pz(x0, y0, z0), pz(x1, y0, z0), pz(x1, y0, z1), pz(x0, y0, z1)]
    return [pz(x0, y0, z0), pz(x1, y0, z0), pz(x1, y1, z0), pz(x0, y1, z0)]
def feet(xm, z):
    """character placement: xm metres from corridor centre at depth z -> (x, y, s for 1.6m)"""
    p = pz(VP[0] + xm * PX_M, NEAR["y1"], z); return p[0], p[1], 1.62 * PX_M / z

PAL = dict(
    day=dict(wall=(184, 168, 156), wall2=(168, 152, 142), floor=(132, 94, 70), ceil=(204, 198, 190), door=(104, 76, 62), frame=(214, 206, 196), base=(226, 220, 210)),
    night=dict(wall=(150, 150, 164), wall2=(136, 136, 152), floor=(110, 86, 72), ceil=(170, 170, 182), door=(92, 70, 62), frame=(196, 192, 196), base=(206, 204, 210)),
)

def hallway(img, mode="night", end="door", plate13=1.0, under=0.0, boxes=False, front_glow=0.0):
    c = PAL[mode]; x0, x1, y0, y1 = NEAR["x0"], NEAR["x1"], NEAR["y0"], NEAR["y1"]
    poly(img, quad(x0, y0, x1, y0, 1, ZF, "y"), c["ceil"])
    poly(img, quad(x0, y1, x1, y1, 1, ZF, "y"), c["floor"])
    # floor boards
    for k in range(1, 12):
        x = x0 + (x1 - x0) * k / 12; pline(img, [pz(x, y1, 1), pz(x, y1, ZF)], shade(c["floor"], 0.75), 2.5)
    for z in (1.3, 1.75, 2.4, 3.3, 4.4):
        pline(img, [pz(x0, y1, z), pz(x1, y1, z)], shade(c["floor"], 0.82), 1.5)
    # runner rug
    poly(img, quad(VP[0] - 300, y1, VP[0] + 300, y1, 1.15, 4.6, "y"), (96, 42, 46), shade((96, 42, 46), 0.6), 2)
    poly(img, quad(VP[0] - 250, y1, VP[0] + 250, y1, 1.25, 4.4, "y"), None, (150, 110, 70), 2)
    poly(img, quad(x0, y0, x0, y1, 1, ZF, "x"), c["wall2"])
    poly(img, quad(x1, y0, x1, y1, 1, ZF, "x"), c["wall2"])
    # baseboards
    for x in (x0, x1): poly(img, quad(x, y1 - 70, x, y1, 1, ZF, "x"), c["base"], OL, 2)
    # side doors
    for x, za, zb in ((x0, 1.6, 2.15), (x1, 2.5, 3.0), (x0, 3.6, 3.95)):
        poly(img, quad(x, y1 - 1650, x, y1, za - 0.05, zb + 0.05, "x"), c["frame"])
        poly(img, quad(x, y1 - 1600, x, y1, za, zb, "x"), c["door"])
        poly(img, quad(x, y1 - 1500, x, y1 - 1000, za + 0.06, zb - 0.06, "x"), None, shade(c["door"], 0.7), 2)
        hp = pz(x, y1 - 820, zb - 0.07); ell(img, hp[0], hp[1], 14 / zb, 10 / zb, (200, 170, 90), OL, 2)
    # picture frames
    for x, za, zb, hy in ((x1, 1.35, 1.9, 700), (x0, 2.6, 3.1, 640), (x1, 3.5, 3.9, 650)):
        poly(img, quad(x, y1 - hy - 560, x, y1 - hy, za, zb, "x"), (70, 56, 48))
        poly(img, quad(x, y1 - hy - 520, x, y1 - hy - 40, za + 0.03, zb - 0.03, "x"), (120, 130, 140) if mode == "day" else (66, 70, 88), OL, 1.5)
    # ceiling lamps
    for z in (1.9, 3.6):
        p = pz(VP[0], y0, z); ell(img, p[0], p[1] + 30 / z, 120 / z, 34 / z, (236, 226, 200) if mode == "day" else (120, 118, 120), OL, 2)
    # far wall
    poly(img, quad(x0, y0, x1, y1, ZF, ZF, "z"), c["wall"])
    pline(img, [pz(x0, y1 - 70, ZF), pz(x1, y1 - 70, ZF)], OL, 2)
    if end == "door":
        dx0, dx1, dy0 = VP[0] - 300, VP[0] + 300, y1 - 1720
        poly(img, quad(dx0 - 60, dy0 - 60, dx1 + 60, y1, ZF, ZF, "z"), c["frame"])
        poly(img, quad(dx0, dy0, dx1, y1, ZF, ZF, "z"), shade(c["door"], 0.92))
        poly(img, quad(dx0 + 70, dy0 + 120, dx1 - 70, dy0 + 760, ZF, ZF, "z"), None, shade(c["door"], 0.62), 2.5)
        poly(img, quad(dx0 + 70, dy0 + 880, dx1 - 70, y1 - 120, ZF, ZF, "z"), None, shade(c["door"], 0.62), 2.5)
        hp = pz(dx1 - 90, y1 - 820, ZF); ell(img, hp[0], hp[1], 18 / ZF, 14 / ZF, (200, 170, 90), OL, 2)
        kp = pz(dx1 - 90, y1 - 740, ZF); ell(img, kp[0], kp[1], 5 / ZF, 9 / ZF, (20, 16, 18), None, 0)
        # plate
        pp = quad(VP[0] - 90, dy0 + 40, VP[0] + 90, dy0 + 130, ZF, ZF, "z"); poly(img, pp, (176, 146, 80), OL, 2)
        if plate13 > 0:
            q = cur().P(pp); cx, cy = q[:, 0].mean(), q[:, 1].mean(); sz = int(abs(q[1, 0] - q[0, 0]) * 0.5)
            if sz > 6: text(img, "13", cx, cy, sz, (40, 26, 20), plate13)
        if under > 0:  # light strip under door
            poly(img, quad(dx0 + 10, y1 - 10, dx1 - 10, y1, ZF, ZF, "z"), mix(c["door"], (230, 240, 255), under), None, 0)
    else:  # entrance: front door with frosted window
        dx0, dx1, dy0 = VP[0] - 330, VP[0] + 330, y1 - 1760
        poly(img, quad(dx0 - 60, dy0 - 60, dx1 + 60, y1, ZF, ZF, "z"), c["frame"])
        poly(img, quad(dx0, dy0, dx1, y1, ZF, ZF, "z"), mix(shade(c["door"], 0.8), (230, 190, 130), front_glow * 0.55))
        poly(img, quad(dx0 + 120, dy0 + 120, dx1 - 120, dy0 + 900, ZF, ZF, "z"), mix((60, 66, 84), (255, 214, 150), front_glow), OL, 2.5)
        hp = pz(dx0 + 80, y1 - 820, ZF); ell(img, hp[0], hp[1], 18 / ZF, 14 / ZF, (200, 170, 90), OL, 2)
        # coat hook + coats
        for k, cc in enumerate(((70, 60, 72), (90, 50, 46))):
            p = pz(dx1 + 160 + k * 120, y1 - 1500, ZF); poly(img, [(p[0] - 14, p[1]), (p[0] + 14, p[1]), (p[0] + 22, p[1] + 150), (p[0] - 22, p[1] + 150)], shade(cc, 1.0), OL, 2)
    if boxes:
        for (bx, bz, bw, bh, cc) in ((-1.1, 2.0, 0.55, 0.45, (176, 138, 96)), (-1.05, 2.0, 0.45, 0.35, (160, 124, 86)), (0.95, 2.7, 0.6, 0.5, (170, 132, 92)), (-0.95, 3.4, 0.5, 0.42, (176, 138, 96))):
            fx, fy, _ = feet(bx, bz); w_, h_ = bw * PX_M / bz, bh * PX_M / bz
            stack = 0 if cc != (160, 124, 86) else 0.45 * PX_M / bz
            poly(img, rect(fx - w_ / 2, fy - h_ - stack, fx + w_ / 2, fy - stack), cc, OL, 2)
            pline(img, [(fx - w_ / 2, fy - h_ * 0.75 - stack), (fx + w_ / 2, fy - h_ * 0.75 - stack)], shade(cc, 0.7), 2)
            pline(img, [(fx - w_ * 0.2, fy - h_ * 0.5 - stack), (fx + w_ * 0.25, fy - h_ * 0.5 - stack)], (60, 50, 50), 1.5)

def door_screen_rect():
    """screen rect of the far door (for lighting)"""
    q = cur().P(quad(VP[0] - 300, NEAR["y1"] - 1720, VP[0] + 300, NEAR["y1"], ZF, ZF, "z")); return q

def bedroom(img, moon=1.0):
    poly(img, rect(-200, -200, 1300, 1400), (96, 104, 140))          # back wall
    poly(img, rect(-200, 1400, 1300, 2200), (88, 70, 66))             # floor
    for k in range(-1, 12): pline(img, [(k * 110, 1400), (k * 160 - 300, 2200)], (70, 56, 54), 2)
    # window
    poly(img, rect(120, 160, 960, 900), (226, 224, 230))
    poly(img, rect(150, 190, 930, 870), (26, 34, 70))
    ell(img, 730, 360, 70, 70, (236, 236, 214), None, 0)
    ell(img, 755, 345, 60, 62, (26, 34, 70), None, 0)
    for sx, sy in ((260, 300), (420, 240), (560, 420), (880, 260), (330, 560)): ell(img, sx, sy, 4, 4, (220, 220, 230), None, 0)
    # tree silhouette branches
    pline(img, [(930, 600), (800, 520), (700, 540)], (14, 16, 30), 10); pline(img, [(930, 760), (840, 720), (780, 650)], (14, 16, 30), 8)
    pline(img, [(540, 190), (540, 870)], (226, 224, 230), 16); pline(img, [(150, 530), (930, 530)], (226, 224, 230), 16)
    poly(img, rect(120, 160, 960, 900), None, OL, 4)
    # curtains
    for sx in (-1, 1):
        x = 540 + sx * 470
        poly(img, smooth([(x - sx * 10, 100), (x + sx * 120, 100), (x + sx * 100, 1000), (x - sx * 60, 1010), (x - sx * 120 + sx * 40, 600)]), (70, 52, 84))
    pline(img, [(30, 100), (1050, 100)], (60, 50, 50), 10)
    # poster
    poly(img, rect(-120, 300, 60, 560), (150, 70, 70)); poly(img, rect(-100, 320, 40, 540), (200, 160, 100), OL, 2)

def bed(img, front=True):
    poly(img, smooth([(60, 1000), (60, 1500), (1080, 1500), (1080, 1000), (900, 960), (600, 950)], 6), (78, 56, 50))   # headboard
    poly(img, rect(40, 1380, 1120, 1720), (232, 228, 222))                                                        # mattress
    poly(img, rect(40, 1680, 1120, 1900), (70, 50, 46))

def blanket(img, pts):
    poly(img, smooth(pts, 6), (120, 132, 176));
    for k in range(3): pass

def door_cu(img, under=0.6, plate=0.0, scratch=0.0, handle_shake=0.0):
    """big door close-up. door fills frame (world coords ~ screen)"""
    poly(img, rect(-300, -300, 1400, 2300), (130, 128, 146))
    poly(img, rect(120, -300, 960, 2300), (190, 186, 194))
    poly(img, rect(170, -300, 910, 1840), (96, 72, 64))
    poly(img, rect(250, 140, 830, 880), None, (62, 46, 42), 5); poly(img, rect(250, 1000, 830, 1760), None, (62, 46, 42), 5)
    for k in range(8): pline(img, [(190 + k * 95, -300), (200 + k * 95, 1840)], (88, 66, 58), 2)
    poly(img, rect(-300, 1840, 1400, 2300), (92, 70, 60))
    hx = 820 + handle_shake * 4
    ell(img, hx, 1040, 34, 34, (196, 166, 92)); poly(img, rect(hx - 10, 1030, hx + 70, 1052), (196, 166, 92))
    ell(img, 820, 1130, 9, 18, (16, 12, 14), None, 0)
    # plate
    poly(img, rect(400, 10, 680, 130), (176, 146, 80), OL, 3)
    for px in (418, 662): ell(img, px, 70, 6, 6, (110, 90, 50), None, 0)
    if under > 0: poly(img, rect(170, 1834, 910, 1846), mix((96, 72, 64), (235, 244, 255), under), None, 0)

def phone_cu(img, t, msgs, now_label="03:19", typing=False, banner=None):
    """phone held in hand, screen faces camera. msgs: list of (text, age_seconds)"""
    poly(img, smooth([(220, 2100), (190, 1500), (260, 1230), (420, 1180), (500, 1400), (460, 2100)], 6), (230, 190, 164))   # palm/thumb base
    poly(img, rect(250, 300, 830, 1500), (18, 18, 22), OL, 6)
    poly(img, rect(272, 322, 808, 1478), (14, 16, 24), None, 0)
    # thumb over edge
    poly(img, smooth([(220, 1500), (280, 1380), (330, 1330), (360, 1360), (310, 1470), (280, 1600)], 6), (238, 196, 170))
    for k, y in enumerate((900, 1060, 1220)):
        poly(img, smooth([(830, y), (900, y + 10), (920, y + 80), (880, y + 130), (820, y + 120)], 5), (232, 192, 166))

def phone_ui(img, t, msgs, banner=None):
    """drawn in screen space over the phone rect (needs V = identity at draw time)"""
    x0, y0, x1, y1 = 272, 322, 808, 1478
    S = cur().P(rect(x0, y0, x1, y1)); sx0, sy0 = S[:, 0].min(), S[:, 1].min(); sx1, sy1 = S[:, 0].max(), S[:, 1].max(); k = (sx1 - sx0) / (x1 - x0)
    cv2.rectangle(img, (int(sx0), int(sy0)), (int(sx1), int(sy1)), (22, 24, 34), -1)
    cv2.rectangle(img, (int(sx0), int(sy0)), (int(sx1), int(sy0 + 150 * k)), (34, 36, 48), -1)
    text(img, "03:19", sx0 + 60 * k, sy0 + 30 * k, int(24 * k), (220, 220, 230), anchor="lm")
    ell_s = lambda cx, cy, r, col: cv2.circle(img, (int(cx), int(cy)), int(r), col, -1, cv2.LINE_AA)
    ell_s(sx0 + 80 * k, sy0 + 100 * k, 30 * k, (90, 90, 104)); text(img, "?", sx0 + 80 * k, sy0 + 100 * k, int(34 * k), (230, 230, 240))
    text(img, "Unbekannte Nummer", sx0 + 125 * k, sy0 + 88 * k, int(28 * k), (240, 240, 245), anchor="lm")
    text(img, "+49 ••• ••• 13 13", sx0 + 125 * k, sy0 + 120 * k, int(21 * k), (150, 150, 165), anchor="lm", bold=False)
    y = sy0 + 200 * k
    for m, age in msgs:
        a = clamp(age / 0.25); lines = wrap(m, 19); bh = (len(lines) * 46 + 36) * k; bw = min(470, max(len(l) for l in lines) * 20.5 + 60) * k
        bx = sx0 + 30 * k; by = y + (1 - eout(a)) * 40 * k
        ov = img.copy(); cv2.rectangle(ov, (int(bx), int(by)), (int(bx + bw), int(by + bh)), (58, 60, 78), -1); img[:] = (img * (1 - a) + ov * a).astype(np.uint8)
        text(img, "\n".join(lines), bx + 28 * k, by + 20 * k, int(34 * k), (245, 245, 250), a, anchor="la", spacing=int(12 * k), align="left")
        y += bh + 26 * k
