"""v9 "Winter-Hauls jetzt bestellen" (v7/v8 engine, 720p source upscaled): jump cuts + punch-in framing, 3D title behind the head, animated smartphone walkthrough
(TikTok bio -> Beacons -> USFans app), section chips + motion graphics per point, word-synced captions, end card.
usage: render7.py chunk K N | preview t_out1,t_out2,..."""
import json, subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import typo as T
from tl import FRAMES, N_MAIN, N_OUT, SEGS, FPS, DUR_MAIN

W, H = 1080, 1920
import os; OUTDIR = os.environ.get("OUTDIR", "frames")
ENH = "hqdn3d=1.4:1.1:3:3,cas=0.5,eq=contrast=1.06:saturation=1.08:gamma=1.02,colorbalance=rm=0.015:bm=-0.015:rh=0.01"
OR, ORD, NAVY, WHITE, INK = (240, 98, 40), (150, 48, 14), (38, 44, 62), (255, 255, 255), (16, 16, 20)
GREEN = (102, 214, 72)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def ei(x): x = clamp(x); return x ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def win(t, t0, t1, fi=0.3, fo=0.25): return min(eo((t - t0) / fi), eio((t1 - t) / fo)) if t0 <= t <= t1 else 0.0
def over(base, L, m=None):
    a = L[..., 3:4] if m is None else L[..., 3:4] * m
    return base * (1 - a) + L[..., :3] * a
def pil2np(im): return np.asarray(im).astype(np.float32) / 255
def place(layer, cx, cy, s=1.0, a=1.0, ry=0.0, rx=0.0, rz=0.0, blur=0.0):
    return T.place_canvas(layer, W, H, cx, cy, s, rot_y=ry, rot_x=rx, rot_z=rz, alpha=a, blur=blur)

# ================================================================ head tracking + framing
HD = np.load("head.npy")
def _sm(x, k=15):
    p = np.pad(x, k // 2, mode="edge"); med = np.median(np.lib.stride_tricks.sliding_window_view(p, k), 1)
    p2 = np.pad(med, k // 2, mode="edge"); return np.convolve(p2, np.ones(k) / k, "valid")
HTOP, HCX = _sm(HD[:, 0]), _sm(HD[:, 1])
# shots: (source start, zoom, screen x of head or None=natural centre)
SHOTS = [(0.0, 1.15, None), (1.62, 1.0, None), (5.46, 1.3, None), (SEGS[1][0], 1.05, None), (11.68, 1.32, None),
         (SEGS[2][0], 1.0, None), (16.6, 1.22, None), (18.12, 1.05, None), (SEGS[3][0], 1.3, None)]
SHOT_END = [s[0] for s in SHOTS[1:]] + [99.0]
ANCH = []
for (a, z, hx), b in zip(SHOTS, SHOT_END):
    i0, i1 = int(a * FPS), min(int(b * FPS), len(HTOP)); ANCH.append((float(np.median(HTOP[i0:i1])), float(np.median(HCX[i0:i1]))))
def shot_of(ts):
    k = max(i for i, s in enumerate(SHOTS) if s[0] <= ts + 1e-6); return k
def camera(ts, extra=1.0):
    k = shot_of(ts); a, z, hx = SHOTS[k]; b = min(SHOT_END[k], SEGS[-1][1]); top, cx = ANCH[k]
    s = z * (1 + 0.028 * eio((ts - a) / max(b - a, 0.1))) * (1 + 0.045 * (1 - eo((ts - a) / 0.4))) * extra
    X = hx if hx is not None else 540 + (cx - 540) * 0.35
    Y = 1000 - (z - 1) * 700
    tx, ty = X - s * cx, Y - s * top
    tx = min(max(tx, W - s * W), 0); ty = min(max(ty, H - s * H), 0)
    return np.float32([[s, 0, tx], [0, s, ty]]), s, (cx * s + tx, top * s + ty)

# ================================================================ title / headline sprites
def title_sprite(big, small=None, big_font="unb", size=150, face=(255, 255, 255), face2=(232, 232, 238), side=ORD, small_col=OR):
    m = T.text_mask(big, big_font, size, 0.0)
    if m.shape[1] > 1000: m = cv2.resize(m, (1000, int(m.shape[0] * 1000 / m.shape[1])), interpolation=cv2.INTER_AREA)
    face_l = T.gradient(m, face, face2, pad=6)
    L = T.shadow(T.extrude(face_l, 16, 0.0, 1.0, side, 0.45), 26, 0, 22, 0.5)
    S = None
    if small:
        sm = T.text_mask(small, "montbi", 74, 0.04); S = T.shadow(T.solid(sm, small_col, pad=4), 16, 0, 10, 0.45)
    return L, S
TITLE_P, TITLE_S = title_sprite("WINTER HAUL", "JETZT BESTELLEN", size=170)
T1_P, T1_S = title_sprite("DELAYS", "GANZ VIELE", size=210)
T2_P, T2_S = title_sprite("ZEIT", "SO SPART IHR", size=230)
HEADS = [(TITLE_P, TITLE_S, 0.1, 1.55), (T1_P, T1_S, 11.68, 12.62), (T2_P, T2_S, 18.68, 20.08)]
def headline(comp, ts, bgk, head_y):
    for P, S, t0, t1 in HEADS:
        if not (t0 <= ts <= t1): continue
        cy = head_y - 25
        k = back((ts - t0) / 0.45, 1.3); out = eio((t1 - ts) / 0.22); a = clamp(eo((ts - t0) / 0.16)) * out
        sc = (1.55 - 0.55 * clamp(k)) * (1 + 0.03 * clamp((ts - t0) / (t1 - t0))) * (1 + 0.08 * (1 - out))
        sc *= 0.92 if P.shape[1] > 1060 else 1.0
        comp = over(comp, place(P, 540, cy, sc, a, ry=-8 + 12 * eio((ts - t0) / max(t1 - t0, 0.1)), rx=8 * (1 - clamp(k)),
                                blur=(1 - clamp(k)) * 9 + (1 - out) * 6), bgk)
        if S is not None:
            ks = eo((ts - t0 - 0.18) / 0.35)
            comp = over(comp, place(S, 540, cy - P.shape[0] * 0.5 * sc - 8 + (1 - ks) * 30, 1.0, ks * out), bgk)
    return comp

# ================================================================ brand pieces
LOGO = Image.open("img/logo.png").convert("RGB")
def logo_pill(w=560):
    lw = w - 90; lh = int(LOGO.height * lw / LOGO.width); h = lh + 64
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=(250, 250, 250, 255))
    im.paste(LOGO.resize((lw, lh), Image.LANCZOS), (45, 32)); return T.shadow(pil2np(im), 24, 0, 18, 0.5)
LOGO_P = logo_pill(); LOGO_S = logo_pill(420)

def gtbuy_card(strike):
    im = Image.new("RGBA", (300, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 299, 100], 50, fill=(14, 14, 18, 215), outline=(255, 255, 255, 70), width=2)
    d.text((150, 50), "GTBuy", font=T.font("interx", 50), fill=(255, 255, 255, 235), anchor="mm")
    if strike > 0:
        x0, x1 = 50, 50 + 200 * strike; d.line([(x0, 56), (x1, 46)], fill=OR + (255,), width=8)
        ka = clamp(strike * 2 - 1); d.rounded_rectangle([80, 110, 220, 148], 19, fill=OR + (int(255 * ka),))
        d.text((150, 129), "BEENDET", font=T.font("interx", 24), fill=(255, 255, 255, int(255 * ka)), anchor="mm")
    return pil2np(im)

# ================================================================ captions
raw = json.load(open("words.json"))
REP = {"G": None, "-T": None, "-Buy": None, "US": None, "Büro": "Bio", "erhält": "erhaltet", "KC": None, "-Bilder.": None,
       "Qualitätskontrollenbilder.": "Qualitätskontroll­bilder.", "outen,": "orten,", "Holz": "Hauls", "vakuuminiert": "vakuumiert",
       "Vergiss": "Vergesst", "Vierten": "Vierter"}
words = []; i = 0
while i < len(raw):
    w = raw[i]; tok = w["w"]
    if tok == "G": words.append(dict(w="GTBuy", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    if tok == "US": nx = raw[i + 1]["w"]; words.append(dict(w="USFans" + nx[len("-Fans"):], s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Winterhals": words.append(dict(w="Winter-Hauls", s=w["s"], e=w["e"])); i += 1; continue
    if tok == "3" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-5"):
        words.append(dict(w="3–5 kg", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Shipping" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-Coupons"):
        words.append(dict(w="Shipping-Coupons", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "KC": words.append(dict(w="QC-Bilder.", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok in ("40", "30") and i + 1 < len(raw) and raw[i + 1]["w"].startswith("%"):
        words.append(dict(w=tok + " %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "All": words.append(dict(w="All-in-One-Plattform.", s=w["s"], e=raw[i + 3]["e"])); i += 4; continue
    if tok == "Echtzeit": words.append(dict(w="Echtzeit-Sendungsverfolgung", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    r = REP.get(tok, tok); words.append(dict(w=r if r else tok, s=w["s"], e=w["e"])); i += 1
for w in words: w["w"] = w["w"].replace("­", "")
KEY = {"winter-hauls", "jetzt", "feiertage", "china", "deutschland", "weihnachtens", "delays", "später", "schnell", "möglich",
       "bestellen", "zeit", "früher", "pakete", "paket"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nx = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if nx is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 14 or nx["s"] - w["e"] > 0.3 or len(clean(w["w"])) > 14:
        chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    nx0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 70
    adj = nx0 - c[-1]["e"] < 0.75
    CH.append(dict(words=c, t0=c[0]["s"] - 0.05, t1=nx0 if adj else min(c[-1]["e"] + 0.3, nx0), adj=adj))
for j in range(len(CH)): CH[j]["prev_adj"] = j > 0 and CH[j - 1]["adj"]
CF = T.font("interb", 66)
def caption(ts, canvas):
    ch = next((c for c in CH if c["t0"] <= ts < c["t1"]), None)
    if ch is None: return
    toks = [clean(w["w"]) for w in ch["words"]]; sp = CF.getlength(" ") * 1.2; wd = [CF.getlength(x) for x in toks]
    total = sum(wd) + sp * (len(toks) - 1); sc0 = min(1.0, 940 / total)
    a = (1.0 if ch["prev_adj"] else eo((ts - ch["t0"]) / 0.16)) * (1.0 if ch["adj"] else eio((ch["t1"] - ts) / 0.14))
    cy = 1590 + (1 - eo((ts - ch["t0"]) / 0.14)) * 14
    lay = Image.new("RGBA", (int(total) + 120, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x = 60
    for w, tok, wdt in zip(ch["words"], toks, wd):
        active = w["s"] - 0.03 <= ts <= w["e"] + 0.02; spoken = ts > w["e"] + 0.02
        col = OR if (active or (spoken and tok.lower() in KEY)) else WHITE
        al = 1.0 if (active or spoken) else 0.55
        yo = -6 * (1 - abs(2 * eo((ts - w["s"] + 0.03) / 0.16) - 1)) if active else 0
        for dx, dy in [(0, 6), (0, 4)]: d.text((x + dx, 85 + dy + yo), tok, font=CF, fill=(0, 0, 0, int(140 * al * a)), anchor="lm")
        d.text((x, 85 + yo), tok, font=CF, fill=col + (int(255 * al * a),), anchor="lm", stroke_width=5, stroke_fill=(10, 10, 12, int(235 * al * a)))
        x += wdt + sp
    if sc0 < 1: lay = lay.resize((int(lay.width * sc0), int(lay.height * sc0)), Image.LANCZOS)
    canvas.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(cy - lay.height / 2)))

# ================================================================ section chips
SECTIONS = []
def chips(ts, canvas):
    for k, (num, lab, t0, t1) in enumerate(SECTIONS):
        if not (t0 <= ts <= t1): continue
        a = win(ts, t0, t1, 0.3, 0.2); kk = back((ts - t0) / 0.4, 1.5)
        f1, f2 = T.font("unb", 34), T.font("interx", 32)
        w = int(f1.getlength(num) + f2.getlength(lab) + 120); h = 74
        im = Image.new("RGBA", (w + 4, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w, h], 37, fill=(14, 14, 18, int(205 * a)), outline=(255, 255, 255, int(60 * a)), width=2)
        nw = f1.getlength(num) + 36; d.rounded_rectangle([7, 7, 7 + nw, h - 7], 30, fill=OR + (int(255 * a),))
        d.text((7 + nw / 2, h / 2 + 1), num, font=f1, fill=(255, 255, 255, int(255 * a)), anchor="mm")
        d.text((nw + 28, h / 2 + 1), lab, font=f2, fill=(255, 255, 255, int(255 * a)), anchor="lm")
        for j in range(5):                                         # progress dots
            cx = w / 2 - 48 + j * 24; r = 6 if j == k else 4
            d.ellipse([cx - r, h + 20 - r, cx + r, h + 20 + r], fill=(OR if j <= k else (255, 255, 255)) + (int((255 if j <= k else 110) * a),))
        sc = 0.85 + 0.15 * clamp(kk)
        if sc < 0.999: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        canvas.alpha_composite(im, (int(W / 2 - im.width / 2), int(118 - (1 - eo((ts - t0) / 0.3)) * 30)))

# ================================================================ smartphone walkthrough (6.0 - 12.5)
SHOT_P = Image.open("img/shot_profile.png").convert("RGB"); SHOT_B = Image.open("img/shot_beacons.png").convert("RGB")
SHOT_U = Image.open("img/shot_usfans.png").convert("RGB")
SW, SH_ = 400, round(2556 * 400 / 1179); SCL = 400 / 1179; BZ = 15
SCR = {k: v.resize((SW, SH_), Image.LANCZOS) for k, v in (("p", SHOT_P), ("b", SHOT_B), ("u", SHOT_U))}
def S(v): return v * SCL
LINK_BOX = (S(40), S(918), S(612), S(985)); BTN_BOX = (S(60), S(1352), S(1119), S(1848)); GS_BOX = (S(291), S(2018), S(889), S(2146))
COUPON_C = (S(700), S(1640))
def rr_mask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255); return m
SCR_MASK = rr_mask(SW, SH_, 52)
def tap(d, x, y, q, dark=True):
    r = 16 + 58 * eo(q); c = (25, 25, 25) if dark else (255, 255, 255)
    d.ellipse([x - r, y - r, x + r, y + r], outline=c + (int(230 * (1 - q)),), width=4)
    r2 = 20 * (1 - 0.5 * q); d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(255, 255, 255, int(190 * (1 - q))), outline=(30, 30, 30, int(140 * (1 - q))), width=2)
def screen(ts):
    p = SCR["p"]; b = SCR["b"]; u = SCR["u"]
    if ts < 7.22: base = p.copy(); cur = "p"
    elif ts < 7.5:                                                    # push transition profile -> beacons
        k = eio((ts - 7.22) / 0.28); base = Image.new("RGB", (SW, SH_)); base.paste(p, (int(-SW * k * 0.35), 0))
        sh = b.copy(); base.paste(sh, (int(SW * (1 - k)), 0)); cur = "pb"
    elif ts < 8.2: base = b.copy(); cur = "b"
    else:
        base = b.copy(); cur = "u"
        k = eo((ts - 8.2) / 0.35)                                   # app-launch zoom from the tapped button
        if k < 1:
            bx = (BTN_BOX[0] + BTN_BOX[2]) / 2; by = (BTN_BOX[1] + BTN_BOX[3]) / 2
            w = int(60 + (SW - 60) * k); h = int(60 + (SH_ - 60) * k); x = int(bx + (0 - bx) * k); y = int(by + (0 - by) * k)
            base.paste(u.resize((max(w, 1), max(h, 1)), Image.LANCZOS), (x, y), rr_mask(max(w, 1), max(h, 1), int(30 + 22 * k)))
        else: base = u.copy()
    ov = Image.new("RGBA", (SW, SH_), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if cur == "p" and ts > 6.5:                                       # bio link highlight
        pr = eo((ts - 6.5) / 0.3); x0, y0, x1, y1 = LINK_BOX
        d.rounded_rectangle([x0, y0, x0 + (x1 - x0) * pr, y1], 8, fill=OR + (int(60 * pr),), outline=OR + (255,), width=3)
        if ts > 6.98: tap(d, (x0 + x1) / 2, (y0 + y1) / 2, clamp((ts - 6.98) / 0.4))
    if cur == "b" and ts > 7.62:
        x0, y0, x1, y1 = BTN_BOX; pr = eo((ts - 7.62) / 0.25)
        d.rounded_rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], 14, outline=OR + (int(255 * pr),), width=4)
        if ts > 7.9: d.rounded_rectangle([x0, y0, x1, y1], 12, fill=(0, 0, 0, int(50 * np.sin(np.pi * clamp((ts - 7.9) / 0.3))))); tap(d, (x0 + x1) / 2, (y0 + y1) / 2, clamp((ts - 7.9) / 0.4))
    if cur == "u" and ts > 8.6:
        cx, cy = COUPON_C; q = clamp((ts - 8.76) / 0.6)                # glow ring on the coupon
        if ts > 8.76: r = 40 + 90 * eo(q); d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], outline=OR + (int(220 * (1 - q)),), width=5)
        if ts > 11.3:
            x0, y0, x1, y1 = GS_BOX; pr = eo((ts - 11.3) / 0.25)
            d.rounded_rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], 30, outline=(255, 255, 255, int(255 * pr)), width=4)
            if ts > 11.6: d.rounded_rectangle([x0, y0, x1, y1], 26, fill=(0, 0, 0, int(60 * np.sin(np.pi * clamp((ts - 11.6) / 0.3))))); tap(d, (x0 + x1) / 2, (y0 + y1) / 2, clamp((ts - 11.6) / 0.4))
    scr = Image.alpha_composite(base.convert("RGBA"), ov)
    ph = Image.new("RGBA", (SW + 2 * BZ, SH_ + 2 * BZ), (0, 0, 0, 0)); dp = ImageDraw.Draw(ph)
    dp.rounded_rectangle([0, 0, SW + 2 * BZ - 1, SH_ + 2 * BZ - 1], 66, fill=(18, 18, 20, 255), outline=(92, 94, 100, 255), width=3)
    dp.rounded_rectangle([3, 3, SW + 2 * BZ - 4, SH_ + 2 * BZ - 4], 63, outline=(40, 40, 44, 255), width=2)
    ph.paste(scr, (BZ, BZ), SCR_MASK)
    dp.rounded_rectangle([SW / 2 + BZ - 62, BZ + 14, SW / 2 + BZ + 62, BZ + 48], 17, fill=(0, 0, 0, 255))   # dynamic island
    g = Image.new("L", ph.size, 0); ImageDraw.Draw(g).polygon([(0, 0), (ph.width * 0.55, 0), (0, ph.height * 0.4)], fill=26)   # glass glint
    ph.alpha_composite(Image.merge("RGBA", (g.point(lambda v: 255), g.point(lambda v: 255), g.point(lambda v: 255), g)).filter(ImageFilter.GaussianBlur(30)))
    return T.shadow(pil2np(ph), 30, 0, 26, 0.55)
def ticket(pct, w=300):
    h = 150; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 22, fill=(253, 236, 214, 255))
    for cy in (h / 2,):
        d.ellipse([w * 0.7 - 14, -14, w * 0.7 + 14, 14], fill=(0, 0, 0, 0)); d.ellipse([w * 0.7 - 14, h - 14, w * 0.7 + 14, h + 14], fill=(0, 0, 0, 0))
    for y in range(18, h - 18, 14): d.line([(w * 0.7, y), (w * 0.7, y + 7)], fill=(220, 150, 110, 255), width=3)
    d.text((22, 62), pct, font=T.font("unb", 64), fill=OR + (255,), anchor="lm")
    d.text((24, 118), "SHIPPING", font=T.font("interx", 24), fill=ORD + (255,), anchor="lm")
    d.text((w * 0.85, h / 2), "OFF", font=T.font("interx", 26), fill=ORD + (255,), anchor="mm")
    return T.shadow(pil2np(im), 18, 0, 14, 0.45)
TIX40, TIX30 = ticket("40%"), ticket("30%")
def chip(text, col=OR, fcol=WHITE, size=34):
    f = T.font("interx", size); w = int(f.getlength(text) + 60); h = int(size * 2.0)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=col + (255,)); d.text((w / 2, h / 2 + 1), text, font=f, fill=fcol + (255,), anchor="mm")
    return T.shadow(pil2np(im), 14, 0, 10, 0.45)
CHIP_BIO = chip("1. LINK IN MEINER BIO ↓")
PH_MAP = ([21.4, 22.0, 22.46, 22.7, 23.0, 23.2, 23.55, 24.48, 25.40, 26.55, 26.85, 27.2, 27.55],
          [6.0, 6.5, 6.98, 7.22, 7.62, 7.9, 8.2, 8.76, 9.66, 11.3, 11.6, 12.2, 12.55])
def phone_layer(comp, ts):
    if True: return comp
    ts = float(np.interp(ts, *PH_MAP))
    kin = back((ts - 6.0) / 0.5, 1.2); kout = ei((ts - 12.2) / 0.32) if ts > 12.2 else 0
    cx = 800 + kout * 500; cy = 930 + (1 - clamp(kin)) * 700
    a = clamp(eo((ts - 6.0) / 0.2))
    ph = screen(ts)
    comp = over(comp, place(ph, cx, cy, 1.0, a, ry=-14 * (1 - clamp(kin)) - 5 + 3 * np.sin(ts * 0.9), rx=3, rz=-2 * (1 - clamp(kin)) + 10 * kout))
    if 6.15 <= ts <= 8.5:
        k = back((ts - 6.15) / 0.4, 1.5); comp = over(comp, place(CHIP_BIO, 790, 395, 0.8 + 0.2 * clamp(k), win(ts, 6.15, 8.5, 0.2, 0.25)))
    for tx, t0, x, rz in ((TIX40, 8.76, 660, -7), (TIX30, 9.66, 935, 6)):
        if t0 <= ts <= 12.3:
            k = back((ts - t0) / 0.5, 1.8); fl = 4 * np.sin((ts - t0) * 2.2)
            y = 330 + (1 - clamp(k)) * 520 + fl
            comp = over(comp, place(tx, x + (cx - 800), y, 0.4 + 0.5 * clamp(k, 0, 1.3), clamp(eo((ts - t0) / 0.15)) * (1 - kout), rz=rz * clamp(k)))
    return comp

# ================================================================ motion graphic cards (behind the person, upper frame)
def card_base(w, h, r=34, fill=(14, 14, 18, 215)):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=fill, outline=(255, 255, 255, 55), width=2); return im, d
def flag(d, cx, cy, r, kind):
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    f = Image.new("RGB", (2 * r, 2 * r)); fd = ImageDraw.Draw(f)
    if kind == "de":
        for k, c in enumerate([(20, 20, 20), (221, 0, 0), (255, 206, 0)]): fd.rectangle([0, k * 2 * r / 3, 2 * r, (k + 1) * 2 * r / 3], fill=c)
    else:
        fd.rectangle([0, 0, 2 * r, 2 * r], fill=(222, 41, 16))
        def star(x, y, R):
            pts = [(x + R * (1 if j % 2 == 0 else 0.42) * np.sin(j * np.pi / 5), y - R * (1 if j % 2 == 0 else 0.42) * np.cos(j * np.pi / 5)) for j in range(10)]
            fd.polygon(pts, fill=(255, 222, 0))
        star(r * 0.72, r * 0.72, r * 0.36)
        for (x, y) in [(1.2, .38), (1.42, .62), (1.42, .95), (1.2, 1.18)]: star(r * x, r * y, r * 0.11)
    return f, m
def route_card(ts):
    w, h = 900, 330; im, d = card_base(w, h)
    p0, p1 = (150, 205), (750, 205)
    for (x, y), kind, lab, t_on in ((p0, "cn", "CHINA", 20.38), (p1, "de", "DEUTSCHLAND", 18.8)):
        on = eo((ts - t_on) / 0.3); r = 62
        if on > 0:
            rr = r + 12 + 26 * eo(((ts - t_on) % 1.2) / 1.2); d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=OR + (int(160 * (1 - ((ts - t_on) % 1.2) / 1.2) * on),), width=4)
        f, m = flag(d, x, y, r, kind); im.paste(f, (x - r, y - r), m)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 230), width=4)
        d.text((x, y + r + 28), lab, font=T.font("interx", 28), fill=(OR if on > 0.5 else WHITE) + (255,), anchor="mm")
    pr = eio((ts - 17.6) / 1.0)                                         # dashed arc draws in
    pts = [(p0[0] + 70 + (p1[0] - p0[0] - 140) * u, p0[1] - 150 * np.sin(np.pi * u)) for u in np.linspace(0, 1, 60)]
    for j in range(0, int(59 * pr), 2): d.line([pts[j], pts[j + 1]], fill=(255, 255, 255, 200), width=5)
    d.text((w / 2, 40), "BESTELLEN AUS CHINA", font=T.font("grotesk", 26), fill=(255, 255, 255, 150), anchor="mm")
    if ts > 20.45:                                                       # plane flies CN -> DE
        u = eio((ts - 20.45) / 0.55); j = min(int(u * 59), 58); x, y = pts[j]; x2, y2 = pts[min(j + 1, 59)]
        ang = np.degrees(np.arctan2(y2 - y, x2 - x))
        pl = Image.new("RGBA", (90, 90), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        pd.polygon([(78, 45), (20, 37), (12, 45), (20, 53)], fill=(255, 255, 255, 255)); pd.polygon([(50, 41), (34, 12), (26, 12), (34, 41)], fill=(255, 255, 255, 255))
        pd.polygon([(50, 49), (34, 78), (26, 78), (34, 49)], fill=(255, 255, 255, 255)); pd.polygon([(22, 41), (12, 26), (8, 26), (14, 45)], fill=(255, 255, 255, 255))
        pl = pl.rotate(-ang, resample=Image.BICUBIC); im.alpha_composite(pl, (int(x - 45), int(y - 45)))
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
QC = Image.open("img/qc.jpg").convert("RGB")
def qc_card(ts):
    pw = 540; ph = int(QC.height * pw / QC.width); w, h = pw + 40, ph + 100; im, d = card_base(w, h)
    im.paste(QC.resize((pw, ph), Image.LANCZOS), (20, 80), rr_mask(pw, ph, 20))
    d.text((32, 42), "QC-BILDER", font=T.font("unb", 32), fill=OR + (255,), anchor="lm")
    d.text((w - 30, 42), "WAREHOUSE", font=T.font("grotesk", 24), fill=(255, 255, 255, 150), anchor="rm")
    if 24.1 <= ts <= 25.3:                                               # scan line
        y = 80 + ph * eio((ts - 24.1) / 1.1)
        for k in range(18): d.line([(20, y - k * 2), (20 + pw, y - k * 2)], fill=OR + (int(110 * (1 - k / 18)),), width=2)
        d.line([(20, y), (20 + pw, y)], fill=(255, 190, 140, 255), width=4)
    L = pil2np(im)
    if ts > 25.3:                                                         # stamp
        k = back((ts - 25.3) / 0.35, 2.0); st = Image.new("RGBA", (330, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 325, 125], 24, outline=GREEN + (255,), width=8, fill=(14, 14, 18, 150))
        sd.text((165, 66), "✓ GEPRÜFT", font=T.font("interb", 50), fill=GREEN + (255,), anchor="mm")
        Lc = np.zeros((h, w, 4), np.float32); Lc[...] = L
        Sx = T.place_canvas(pil2np(st), w, h, w - 200, h - 100, 1.6 - 0.6 * clamp(k), rot_z=-10, alpha=clamp(eo((ts - 25.3) / 0.1)))
        a = Sx[..., 3:4]; Lc[..., :3] = Lc[..., :3] * (1 - a) + Sx[..., :3] * a; Lc[..., 3] = Lc[..., 3] + Sx[..., 3] * (1 - Lc[..., 3]); L = Lc
    return T.shadow(L, 24, 0, 18, 0.45)
def choice(ts, canvas):
    if not (31.25 <= ts <= 33.35): return
    for lab, t0, x, good in (("↩  ZURÜCKSCHICKEN", 31.42, 290, False), ("✓  NACH HAUSE", 32.8, 790, True)):
        if ts < t0: continue
        k = back((ts - t0) / 0.4, 1.6); a = win(ts, t0, 33.35, 0.15, 0.2)
        f = T.font("interx", 34); w = int(f.getlength(lab) + 70); h = 84
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w - 1, h - 1], 42, fill=(GREEN if good else (14, 14, 18)) + (int(235 * a),), outline=(255, 255, 255, int(90 * a)), width=2)
        d.text((w / 2, h / 2 + 1), lab, font=f, fill=((10, 30, 10) if good else WHITE) + (int(255 * a),), anchor="mm")
        s = 0.7 + 0.3 * clamp(k, 0, 1.2); im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
        canvas.alpha_composite(im, (int(min(max(x - im.width / 2, 20), W - im.width - 20)), int(420 - im.height / 2)))
STEPS = ["Bestellt", "Warehouse", "Unterwegs", "Zuhause"]
def track_card(ts):
    w, h = 920, 330; im, d = card_base(w, h)
    d.text((36, 52), "SENDUNGSVERFOLGUNG", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="lm")
    lv = 0.5 + 0.5 * np.sin(ts * 7); d.ellipse([w - 140, 42, w - 120, 62], fill=(255, 70, 60, int(140 + 115 * lv)))
    d.text((w - 110, 52), "LIVE", font=T.font("interx", 28), fill=(255, 255, 255, 255), anchor="lm")
    xs = [110 + j * 233 for j in range(4)]; y = 175
    prog = 0.0
    for j, tj in enumerate([35.9, 36.5, 37.1]): prog += eio((ts - tj) / 0.45)
    prog = min(prog, 2.0) + 0.45 * eio((ts - 37.6) / 2.4)
    d.line([(xs[0], y), (xs[-1], y)], fill=(255, 255, 255, 60), width=8)
    xe = xs[0] + (xs[-1] - xs[0]) * prog / 3; d.line([(xs[0], y), (xe, y)], fill=OR + (255,), width=8)
    for j, x in enumerate(xs):
        done = prog >= j - 0.02; r = 24
        d.ellipse([x - r, y - r, x + r, y + r], fill=(OR if done else (40, 40, 46)) + (255,), outline=(255, 255, 255, 200), width=3)
        if done and j < 3: d.line([(x - 10, y), (x - 3, y + 8), (x + 11, y - 9)], fill=(255, 255, 255, 255), width=5)
        d.text((x, y + 62), STEPS[j], font=T.font("interx", 28), fill=(255, 255, 255, 255 if done else 130), anchor="mm")
    # package marker riding the line
    bx = xe; by = y - 62 + 4 * np.sin(ts * 5)
    d.rounded_rectangle([bx - 26, by - 22, bx + 26, by + 22], 8, fill=(205, 150, 95, 255), outline=(120, 80, 45, 255), width=3)
    d.line([(bx - 26, by - 4), (bx + 26, by - 4)], fill=(120, 80, 45, 255), width=3); d.polygon([(bx - 8, by + 22), (bx + 8, by + 22), (bx, by + 34)], fill=(205, 150, 95, 255))
    if ts > 39.6:
        k = eo((ts - 39.6) / 0.3); d.rounded_rectangle([w / 2 - 180, h - 58, w / 2 + 180, h - 14], 22, fill=GREEN + (int(235 * k),))
        d.text((w / 2, h - 36), "✓  Paket geortet", font=T.font("interx", 26), fill=(10, 30, 10, int(255 * k)), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def box_icon(d, cx, cy, s, col=(205, 150, 95), edge=(120, 80, 45)):
    w, h = 150 * s, 110 * s; top = 40 * s
    d.polygon([(cx - w / 2, cy - h / 2 + top), (cx + w / 2, cy - h / 2 + top), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=col + (255,), outline=edge + (255,))
    d.polygon([(cx - w / 2, cy - h / 2 + top), (cx - w / 2 + 30 * s, cy - h / 2), (cx + w / 2 + 30 * s, cy - h / 2), (cx + w / 2, cy - h / 2 + top)], fill=tuple(min(255, c + 25) for c in col) + (255,), outline=edge + (255,))
    d.polygon([(cx + w / 2, cy - h / 2 + top), (cx + w / 2 + 30 * s, cy - h / 2), (cx + w / 2 + 30 * s, cy + h / 2 - top), (cx + w / 2, cy + h / 2)], fill=tuple(max(0, c - 35) for c in col) + (255,), outline=edge + (255,))
    d.line([(cx - 12 * s, cy - h / 2 + top), (cx - 12 * s, cy - h / 2 + top + 40 * s)], fill=(235, 225, 200, 255), width=max(2, int(10 * s)))
def pack_card(ts):
    w, h = 900, 380; im, d = card_base(w, h)
    if ts < 48.4:
        d.text((w / 2, 44), "UNNÖTIGE KARTONS  →  VAKUUMIERT", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
        box_icon(d, 230, 200, 1.25)
        if ts > 44.15:
            k = eo((ts - 44.15) / 0.25); L = 90
            d.line([(230 - L, 200 - L * 0.8), (230 - L + 2 * L * k, 200 - L * 0.8 + 1.6 * L * k)], fill=(255, 70, 60, 255), width=12)
            if k >= 1: d.line([(230 + L, 200 - L * 0.8), (230 + L - 2 * L * eo((ts - 44.4) / 0.25), 200 - L * 0.8 + 1.6 * L * eo((ts - 44.4) / 0.25))], fill=(255, 70, 60, 255), width=12)
        if ts > 46.4:                                                   # vacuum bag squeezes flat
            k = eio((ts - 46.5) / 0.9); bw, bh = 260 - 40 * k, 200 - 120 * k; cx, cy = 650, 200
            d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], int(40 - 20 * k), fill=(200, 215, 230, int(150 + 60 * k)), outline=(255, 255, 255, 230), width=4)
            for j in range(5): d.line([(cx - bw / 2 + 20, cy - bh / 2 + 18 + j * (bh - 36) / 4), (cx + bw / 2 - 20, cy - bh / 2 + 18 + j * (bh - 36) / 4 + 6)], fill=(255, 255, 255, int(90 * k)), width=2)
            for sgn in (-1, 1):
                ax = cx + sgn * (bw / 2 + 40 - 20 * np.sin(ts * 8) * (1 - k)); d.line([(ax + sgn * 40, cy), (ax, cy)], fill=OR + (255,), width=7)
                d.polygon([(ax, cy), (ax + sgn * 18, cy - 14), (ax + sgn * 18, cy + 14)], fill=OR + (255,))
                vy = cy + sgn * (bh / 2 + 34); d.line([(cx, vy + sgn * 30), (cx, vy)], fill=OR + (255,), width=7)
                d.polygon([(cx, vy), (cx - 14, vy + sgn * 18), (cx + 14, vy + sgn * 18)], fill=OR + (255,))
            d.text((cx, cy + 150), "VAKUUMIERT", font=T.font("interx", 30), fill=(255, 255, 255, int(255 * eo((ts - 46.6) / 0.3))), anchor="mm")
        d.text((230, 315), "KARTON", font=T.font("interx", 30), fill=(255, 255, 255, 255), anchor="mm")
    else:                                                               # savings
        d.text((w / 2, 44), "DU SPARST", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
        for j, (lab, t0) in enumerate((("GELD", 50.64), ("VERSANDKOSTEN", 51.34))):
            k = back((ts - t0) / 0.4, 1.6)
            if ts < t0 - 0.02: continue
            x = 250 + j * 400; y = 190
            r = 70 * clamp(k, 0, 1.2); d.ellipse([x - r, y - r - 10, x + r, y + r - 10], fill=(255, 196, 60, 255), outline=(190, 130, 20, 255), width=6)
            if r > 30: d.text((x, y - 10), "€", font=T.font("unb", int(80 * clamp(k, 0, 1.2))), fill=(150, 95, 10, 255), anchor="mm")
            ax = x + 95; d.line([(ax, y - 40), (ax, y + 30)], fill=GREEN + (255,), width=10); d.polygon([(ax - 22, y + 20), (ax + 22, y + 20), (ax, y + 50)], fill=GREEN + (255,))
            d.text((x + 20, 300), lab, font=T.font("interx", 32), fill=(255, 255, 255, int(255 * clamp(k))), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
LANGS = [("DE", "Deutsch"), ("EN", "English"), ("FR", "Français"), ("ES", "Español"), ("IT", "Italiano"), ("PL", "Polski"), ("TR", "Türkçe"), ("NL", "Nederlands")]
CURS = [("$", "USD"), ("£", "GBP"), ("CHF", "CHF"), ("€", "EUR")]
def lang_card(ts):
    w, h = 820, 360; im, d = card_base(w, h)
    if ts < 58.35:
        d.text((w / 2, 44), "SPRACHE WÄHLEN", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
        u = (ts - 54.6) / 0.55; base = int(np.floor(u)); fr = eio((u - base) / 0.35) if u > 0 else 0
        for off in (-1, 0, 1, 2):
            j = (base + off) % len(LANGS); yy = 205 + (off - fr) * 105
            if not (95 < yy < 320): continue
            act = 1 - min(abs(off - fr), 1); al = int(255 * (1 - 0.6 * min(abs(yy - 205) / 105, 1)) * clamp((min(yy, 330 - yy) - 95) / 40 + 1))
            code, name = LANGS[j]
            d.rounded_rectangle([140, yy - 42, w - 140, yy + 42], 42, fill=(OR if act > 0.5 else (40, 40, 46)) + (int(al * (0.6 + 0.4 * act)),))
            d.text((200, yy), code, font=T.font("unb", 34), fill=(255, 255, 255, al), anchor="lm")
            d.text((300, yy), name, font=T.font("interx", 40), fill=(255, 255, 255, al), anchor="lm")
    else:
        d.text((w / 2, 44), "EINSTELLUNGEN", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
        rows = [("Sprache", "Deutsch", 59.68), ("Währung", None, 61.52)]
        for j, (lab, val, t0) in enumerate(rows):
            y = 135 + j * 120; on = eo((ts - t0) / 0.3)
            d.rounded_rectangle([50, y - 48, w - 50, y + 48], 26, fill=(40, 40, 46, 255), outline=(OR if on > 0.5 else (255, 255, 255)) + (int(60 + 195 * on),), width=3)
            d.text((86, y), lab, font=T.font("interx", 34), fill=(255, 255, 255, 190), anchor="lm")
            if val is None:
                q = clamp((ts - 60.9) / 0.85); c = CURS[min(int(q * len(CURS)), len(CURS) - 1)]; val = f"{c[0]}  {c[1]}"
            d.text((w - 120, y), val, font=T.font("interx", 36), fill=(OR if on > 0.5 else WHITE) + (255,), anchor="rm")
            d.polygon([(w - 92, y - 6), (w - 68, y - 6), (w - 80, y + 8)], fill=(255, 255, 255, 200))
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def holiday_card(ts):
    w, h = 900, 400; im, d = card_base(w, h)
    d.text((w / 2, 46), "BALD: FEIERTAGE", font=T.font("unb", 34), fill=OR + (255,), anchor="mm")
    for (x, kind, lab, t0) in ((180, "cn", "CHINA", 4.34), (720, "de", "DEUTSCHLAND", 5.08)):
        if ts < t0 - 0.02: continue
        k = back((ts - t0) / 0.4, 1.8); r = int(70 * clamp(k, 0, 1.15))
        if r > 4:
            f, m = flag(d, x, 200, r, kind); im.paste(f, (x - r, 200 - r), m); d.ellipse([x - r, 200 - r, x + r, 200 + r], outline=(255, 255, 255, 230), width=4)
        d.text((x, 315), lab, font=T.font("interx", 30), fill=(255, 255, 255, int(255 * clamp(k))), anchor="mm")
    if ts > 5.7:                                                        # calendar page: Weihnachten
        k = back((ts - 5.7) / 0.45, 1.6); s_ = clamp(k, 0, 1.15); cx, cy = 450, 205
        cw, ch = 190 * s_, 200 * s_
        if cw > 10:
            d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2], int(22 * s_), fill=(250, 250, 250, 255))
            d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy - ch / 2 + 56 * s_], int(22 * s_), fill=(220, 40, 40, 255))
            d.rectangle([cx - cw / 2, cy - ch / 2 + 30 * s_, cx + cw / 2, cy - ch / 2 + 56 * s_], fill=(220, 40, 40, 255))
            d.text((cx, cy - ch / 2 + 28 * s_), "DEZ", font=T.font("interx", int(32 * s_) + 1), fill=(255, 255, 255, 255), anchor="mm")
            d.text((cx, cy + 30 * s_), "24", font=T.font("unb", int(84 * s_) + 1), fill=(30, 30, 34, 255), anchor="mm")
        lk = eo((ts - 7.58) / 0.3)
        d.text((cx, 340), "WEIHNACHTEN", font=T.font("interx", 32), fill=(255, 90, 80, int(255 * lk)), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def delay_card(ts):
    w, h = 900, 360; im, d = card_base(w, h)
    d.text((40, 52), "DEIN PAKET", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="lm")
    blink = 0.5 + 0.5 * np.sin(ts * 9)
    d.rounded_rectangle([w - 300, 28, w - 40, 78], 25, fill=(230, 50, 45, int(160 + 95 * blink)))
    d.text((w - 170, 53), "VERSPÄTET", font=T.font("interb", 30), fill=(255, 255, 255, 255), anchor="mm")
    xs = [120, 340, 560, 780]; y = 170; labs = ["Bestellt", "Warehouse", "Zoll", "Zuhause"]
    d.line([(xs[0], y), (xs[-1], y)], fill=(255, 255, 255, 60), width=8); d.line([(xs[0], y), (xs[1] + 60, y)], fill=OR + (255,), width=8)
    for j, x in enumerate(xs):
        done = j <= 1; d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(OR if done else (40, 40, 46)) + (255,), outline=(255, 255, 255, 200), width=3)
        d.text((x, y + 55), labs[j], font=T.font("interx", 26), fill=(255, 255, 255, 255 if done else 120), anchor="mm")
    # stalled package with clock
    bx, by = xs[1] + 60, y - 58
    d.rounded_rectangle([bx - 26, by - 22, bx + 26, by + 22], 8, fill=(205, 150, 95, 255), outline=(120, 80, 45, 255), width=3)
    ang = (ts - 12.6) * 4; cx, cy = w - 120, 270
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=(255, 255, 255, 230), width=5)
    d.line([(cx, cy), (cx + 26 * np.sin(ang), cy - 26 * np.cos(ang))], fill=(255, 90, 80, 255), width=5); d.line([(cx, cy), (cx, cy - 18)], fill=(255, 255, 255, 255), width=5)
    k = eo((ts - 13.18) / 0.3)
    d.text((60, 300), "ANKUNFT:", font=T.font("interx", 30), fill=(255, 255, 255, 200), anchor="lm")
    d.text((230, 300), "SPÄTER", font=T.font("interb", 34), fill=(255, 90, 80, int(255 * k)), anchor="lm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def order_card(ts):
    w, h = 760, 380; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 36, fill=(250, 250, 250, 245))
    lw = 260; lh = int(LOGO.height * lw / LOGO.width); im.paste(LOGO.resize((lw, lh), Image.LANCZOS), (40, 34))
    d.text((w - 40, 34 + lh / 2), "WINTER HAUL", font=T.font("interx", 28), fill=NAVY + (255,), anchor="rm")
    for j, (lab, col) in enumerate((("Jacke", (70, 110, 200)), ("Hoodie", (90, 90, 100)), ("Boots", (150, 100, 60)))):
        x = 40 + j * 230; d.rounded_rectangle([x, 120, x + 210, 220], 20, fill=(236, 236, 240, 255))
        d.rounded_rectangle([x + 18, 138, x + 82, 202], 14, fill=col + (255,)); d.text((x + 100, 170), lab, font=T.font("interx", 28), fill=NAVY + (255,), anchor="lm")
    bx0, by0, bx1, by1 = 40, 250, w - 40, 340; done = ts > 17.7
    press = np.sin(np.pi * clamp((ts - 17.56) / 0.25)) if ts > 17.56 else 0
    d.rounded_rectangle([bx0 + 6 * press, by0 + 4 * press, bx1 - 6 * press, by1 - 4 * press], 45, fill=(GREEN if done else OR) + (255,))
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "✓  BESTELLT" if done else "JETZT BESTELLEN", font=T.font("interb", 38), fill=((10, 30, 10) if done else WHITE) + (255,), anchor="mm")
    if 17.56 < ts < 18.1: tap(d, (bx0 + bx1) / 2, (by0 + by1) / 2, clamp((ts - 17.56) / 0.45))
    if ts > 16.78 and not done:                                          # urgency pulse on "schnell"
        q = ((ts - 16.78) % 0.6) / 0.6; d.rounded_rectangle([bx0 - 8 * q, by0 - 8 * q, bx1 + 8 * q, by1 + 8 * q], 50, outline=OR + (int(200 * (1 - q)),), width=4)
    return T.shadow(pil2np(im), 26, 0, 20, 0.5)
def compare_card(ts):
    w, h = 900, 380; im, d = card_base(w, h)
    d.text((w / 2, 46), "WANN KOMMT DEIN PAKET?", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    rows = [("JETZT BESTELLT", 0.42, GREEN, "✓ FRÜHER DA", 20.9), ("SPÄTER BESTELLT", 0.95, (230, 60, 50), "DELAYS", 21.2)]
    for j, (lab, L, col, tag, t0) in enumerate(rows):
        y = 125 + j * 125; k = eio((ts - t0) / 0.7)
        d.text((40, y), lab, font=T.font("interx", 30), fill=(255, 255, 255, 230), anchor="lm")
        d.rounded_rectangle([40, y + 28, w - 40, y + 72], 22, fill=(40, 40, 46, 255))
        x1 = 40 + (w - 80) * L * k
        if x1 > 60: d.rounded_rectangle([40, y + 28, x1, y + 72], 22, fill=col + (255,))
        if k > 0.98:
            f = T.font("interb", 28); tw = f.getlength(tag)
            hi = j == 0 and ts > 22.1
            tx = min(x1 + 20, w - 50 - tw)
            d.text((tx if j == 0 else x1 - tw - 20, y + 50), tag, font=f, fill=(255, 255, 255, 255) if not hi else (255, 255, 255, 255), anchor="lm")
            if hi:
                q = clamp((ts - 22.1) / 0.5); d.rounded_rectangle([36 - 6 * q, y + 24 - 6 * q, x1 + 4 + 6 * q, y + 76 + 6 * q], 26, outline=GREEN + (int(255 * (1 - q)),), width=4)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(holiday_card, 3.0, 8.47, 480), (delay_card, 12.62, 14.13, 480), (order_card, 14.55, 18.05, 480), (compare_card, 20.85, 22.88, 480)]
def cards(comp, ts, bgk):
    for fn, t0, t1, cy in CARDS:
        if not (t0 <= ts <= t1): continue
        k = back((ts - t0) / 0.5, 1.3); a = win(ts, t0, t1, 0.25, 0.25)
        comp = over(comp, place(fn(ts), 540, cy + (1 - clamp(k)) * 60, 0.88 + 0.12 * clamp(k), a, rx=(1 - clamp(k)) * 18, ry=-4 + 2 * np.sin(ts * 0.8)), bgk)
    return comp

# ================================================================ opening + CTA + end card
def opening(comp, ts, bgk):
    return comp
def cta(comp, ts):
    return comp
MASCOT = Image.open("img/mascot.png").convert("RGB")
def end_card_sprite():
    mw = 380; mh = int(MASCOT.height * mw / MASCOT.width); im = Image.new("RGBA", (mw + 20, mh + 20), (0, 0, 0, 0))
    im.paste(MASCOT.resize((mw, mh), Image.LANCZOS), (10, 10), rr_mask(mw, mh, 40)); return T.shadow(pil2np(im), 24, 0, 18, 0.5)
MASC = end_card_sprite()
FUN = T.shadow(T.solid(T.text_mask("VIEL SPASS!", "unb", 84, 0.02), WHITE, pad=4), 18, 0, 12, 0.6)
CHIP_END = chip("1. LINK IN BIO  ·  40% + 30% SHIPPING", OR, WHITE, 30)

# ================================================================ frame
def box_(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=10, eps=2e-3):
    mI, mp = box_(I, r), box_(p, r); a = (box_(I * p, r) - mI * mp) / (box_(I * I, r) - mI * mI + eps); b = mp - a * mI
    return box_(a, r) * I + box_(b, r)
def zoom_blur(img, cx, cy, amount, n=6):
    acc = np.zeros_like(img)
    for k in range(n): acc += cv2.warpAffine(img, cv2.getRotationMatrix2D((cx, cy), 0, 1 + amount * k / (n - 1)), (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
    return acc / n
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.18 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1.6) ** 1.3)[..., None]
rng = np.random.default_rng(7)

def render(o, get):
    freeze = o >= N_MAIN; fz = (o - N_MAIN) / FPS if freeze else 0.0
    sidx = FRAMES[min(o, N_MAIN - 1)]; ts = sidx / FPS; to = o / FPS
    f8, m8 = get(sidx)
    frame = f8.astype(np.float32) / 255; m = m8.astype(np.float32) / 255
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    m = np.clip(cv2.resize(guided(gs, cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    extra = 1.0; zb = 0.0
    if to < 0.4: k = eo(to / 0.4); extra = 1 + 0.3 * (1 - k); zb = 0.08 * (1 - k)
    if freeze: extra = 1.0
    M, s, (hx, hy) = camera(ts, extra)
    frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    m = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if s > 1.08: frame = np.clip(frame + (0.25 + 0.35 * clamp((s - 1.08) / 0.3)) * (frame - cv2.GaussianBlur(frame, (0, 0), 1.3)), 0, 1)
    if zb > 0.004: frame = zoom_blur(frame, hx, hy + 200, zb); m = zoom_blur(np.dstack([m] * 3), hx, hy + 200, zb)[..., 0]
    bgk = (1 - m)[..., None]; comp = frame
    if freeze:
        k = eo(fz / 0.35); comp = cv2.GaussianBlur(comp, (0, 0), 3 + 30 * k) * (1 - 0.45 * k); bgk = np.ones_like(bgk)
    comp = headline(comp, ts, bgk, hy)
    comp = cards(comp, ts, bgk)
    if not freeze: comp = opening(comp, ts, bgk)
    comp = comp * VIG
    if freeze:
        k = back(fz / 0.5, 1.5); a = clamp(eo(fz / 0.25))
        comp = over(comp, place(LOGO_P, 540, 560, 0.6 + 0.4 * clamp(k, 0, 1.2), a, rx=(1 - clamp(k)) * 30), bgk)
        k2 = back((fz - 0.2) / 0.5, 1.5); comp = over(comp, place(FUN, 540, 740, 0.7 + 0.3 * clamp(k2, 0, 1.2), clamp(eo((fz - 0.2) / 0.2))), bgk)
        k3 = back((fz - 0.35) / 0.5, 1.6)
        comp = over(comp, place(MASC, 540, 1180 + (1 - clamp(k3)) * 300, 0.85, clamp(eo((fz - 0.35) / 0.2)), rz=6))
        k4 = eo((fz - 0.5) / 0.3); comp = over(comp, place(CHIP_END, 540, 1600 + (1 - k4) * 20, 1.0, k4))
    else:
        comp = phone_layer(comp, ts); comp = cta(comp, ts)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        chips(ts, canvas); caption(ts, canvas)
        U = pil2np(canvas)
        if U[..., 3].max() > 0: comp = over(comp, U)
    comp = comp + rng.normal(0, 0.009, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if freeze and fz > (N_OUT - N_MAIN) / FPS - 0.3: comp *= clamp(((N_OUT - N_MAIN) / FPS - fz) / 0.3)
    return (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)

def loader(srcs):
    i0, i1 = min(srcs), max(srcs) + 1; n = i1 - i0
    dv = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{i0 / FPS:.4f}", "-i", "input_cfr.mov", "-vf", ENH, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    dm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{i0 / FPS:.4f}", "-i", "mask.mkv", "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    F = np.frombuffer(dv, np.uint8).reshape(-1, H, W, 3); Mk = np.frombuffer(dm, np.uint8).reshape(-1, H, W)
    return lambda i: (F[min(i - i0, len(F) - 1)], Mk[min(i - i0, len(Mk) - 1)])
def single(i):
    dv = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{i / FPS:.4f}", "-i", "input_cfr.mov", "-vf", ENH, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    dm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{i / FPS:.4f}", "-i", "mask.mkv", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(dv, np.uint8).reshape(H, W, 3), np.frombuffer(dm, np.uint8).reshape(H, W)

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        for to in [float(x) for x in sys.argv[2].split(",")]:
            o = min(int(round(to * FPS)), N_OUT - 1)
            Image.fromarray(render(o, lambda i: single(i))).save(f"{OUTDIR}/p_{to:05.2f}.jpg", quality=90)
        print("preview done")
    else:
        K, NC = int(sys.argv[2]), int(sys.argv[3]); a, b = K * N_OUT // NC, (K + 1) * N_OUT // NC
        get = loader([FRAMES[min(o, N_MAIN - 1)] for o in range(a, b)])
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-pix_fmt", "yuv420p", f"chunk_{K}.mp4"], stdin=subprocess.PIPE)
        for o in range(a, b):
            enc.stdin.write(render(o, get).tobytes())
            if (o - a) % 30 == 0: print(f"chunk {K}: {o - a}/{b - a}", flush=True)
        enc.stdin.close(); enc.wait(); print(f"chunk {K} done")
