"""v13 haul edit (5 kg GTBuy haul, orange) — built from v8 by build13.py. Original v8 doc:
v8 talking-head edit: '3 Gründe, warum du zu GTBuy wechseln solltest'.
Cobalt-blue / white / chrome. Creator's own TikTok + Beacons screenshots in an animated phone mock-up (zoom + tap on the link),
head-masked headlines, face-tracked camera, Higgsfield B-roll (coupons, payment, delivery, warehouse), timeline infographic,
word-synced captions, freeze end card. Usage: python render8.py <start> <end> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib13 import *

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
NSRC = 705
DUR = 26.8
FREEZE = 704
BLUE = np.array([255, 140, 0], np.float32) / 255   # GTBuy orange (name kept from v8)
WHITE = np.array([250, 250, 248], np.float32) / 255

# ------------------------------------------------------------------ camera (face tracked, no source re-timing)
faces = json.load(open("faces.json"))
CUTS = [0, 63, 240, 285, 330, 375, 420, 465, 510, 555, 600, 660, 690, NSRC]
fx = np.array([np.nan if f[1] is None else f[1] + f[3] / 2 for f in faces[:NSRC]], np.float32)
fy = np.array([np.nan if f[1] is None else f[2] + f[4] * 0.45 for f in faces[:NSRC]], np.float32)
def smooth(v, sig):
    out = v.copy()
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        seg = v[a:b].copy(); idx = np.arange(len(seg)); ok = ~np.isnan(seg)
        seg = np.interp(idx, idx[ok], seg[ok]) if ok.any() else np.full(len(seg), 540.0, np.float32)
        k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2); k /= k.sum()
        out[a:b] = np.convolve(np.pad(seg, 3 * sig, mode="edge"), k, "valid")
    return out
FX, FY = smooth(fx, 14), smooth(fy, 14)
CLIPS_T = [8.0, 9.5, 11.0, 12.5, 14.0, 15.5, 17.0, 18.5, 20.0, 22.0, 23.0]
def camera(i, t):
    if t < 2.10:
        s = 1.20 + 0.30 * (1 - ease_out(t / 0.5)) + 0.04 * t / 2.1
        x0 = clamp(FX[i] - 0.5 * W / s, 0, W - W / s); y0 = clamp(FY[i] - 0.40 * H / s, 0, H - H / s)
    elif t < 8.0:
        s = 1.10 + 0.07 * ease_io((t - 2.1) / 5.9) + 0.10 * (1 - ease_out((t - 2.1) / 0.4))
        x0 = clamp(FX[i] - 0.36 * W / s, 0, W - W / s); y0 = clamp(FY[i] - 0.44 * H / s, 0, H - H / s)
    else:
        t0 = max(c for c in CLIPS_T if c <= t)
        s = 1.04 + 0.10 * (1 - ease_out((t - t0) / 0.45)) + 0.02 * (t - t0)
        x0 = (W - W / s) / 2; y0 = (H - H / s) * 0.42
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])

# ------------------------------------------------------------------ typography
_cache = {}
def chrome_cached(key, M_, depth, sw):
    k = (key, None if sw is None else round(round(sw / 0.05) * 0.05, 2))
    if k not in _cache: _cache[k] = sprite_chrome(M_, depth=depth, sweep=k[1])
    return _cache[k]
S = {}
KG_M = tmask("5 KG", font("Unbounded", 250, 900), 6)[0]
S["haulw"] = sprite_fill(tmask("GTBUY HAUL", font("Archivo", 86, 900, 118), 6)[0], WHITE, shadow=0.0, stroke=(BLUE * 0.85, 7))
S["yalla"] = chip("YALLA!", bg=BLUE, fg=WHITE, size=64)
S["c40"] = chip("2× 40 %", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("2× 30 %", bg=BLUE, fg=WHITE, size=60)
S["aufship"] = chip("Auf Shipping", tick=True, size=42)
S["jetzt"] = sprite_fill(tmask("JETZT", font("Archivo", 130, 900, 125), 10)[0], BLUE, shadow=0.0, stroke=(INK, 6))
ANM_M = tmask("ANMELDEN", font("Unbounded", 94, 900), 2)[0]
S["detail"] = chip("Detail-Check", tick=True, size=52)
KGH_M = tmask("5 KG HAUL", font("Archivo", 140, 900, 118), 2)[0]
S["e1"] = chip("9 Teile  ·  über GTBuy", tick=True, size=42)
S["e2"] = chip("Coupons: 2× 40 %  +  2× 30 %", bg=BLUE, fg=WHITE, size=40)
S["link"] = link_card(size=52)
_lg = Image.open("img/gtbuy_logo.png").convert("RGBA")
def _logo(sz):
    arr = np.asarray(_lg.resize((sz, sz), Image.LANCZOS)).astype(np.float32) / 255; return arr[..., :3], arr[..., 3], (0, 0)
S["logo_s"] = _logo(150); S["logo_m"] = _logo(210)

def card(img, cw, ch, label=None, z=1.04):
    return card_sprite(img, cw, ch, z, label)
S["haul_card"] = card(load_img("img/haulbox.png"), 400, 560, None)

# ------------------------------------------------------------------ phone mock-up with the creator's screenshots
SHOT = {k: load_img(f"img/shot_{k}.png") for k in ("profile", "beacons")}
SW_, SH_ = 1179, 2556
HL = {"profile": (40, 912, 625, 1000), "beacons": (58, 1545, 1121, 2145)}   # highlight rects in screenshot pixels
PW, PH, BZ = 452, 980, 14
def phone(name, zoom, cy_frac, hl=0.0, tap=-1.0, badge=0.0):
    """renders the phone: screenshot viewed at `zoom` centred at cy_frac, highlight box + tap ripple"""
    img = SHOT[name]
    vh, vw = SH_ / zoom, SW_ / zoom
    cy = clamp(cy_frac * SH_, vh / 2, SH_ - vh / 2); cx = SW_ / 2 if zoom <= 1.001 else clamp((HL[name][0] + HL[name][2]) / 2, vw / 2, SW_ - vw / 2)
    x0, y0 = cx - vw / 2, cy - vh / 2
    sw, sh = PW - 2 * BZ, PH - 2 * BZ
    M = np.float32([[sw / vw, 0, -x0 * sw / vw], [0, sh / vh, -y0 * sh / vh]])
    scr = cv2.warpAffine(img, M, (sw, sh), flags=cv2.INTER_AREA if zoom < 1.5 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    L = Image.new("RGBA", (sw, sh), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    bx = HL[name]; p0 = (bx[0] - x0) * sw / vw, (bx[1] - y0) * sh / vh; p1 = (bx[2] - x0) * sw / vw, (bx[3] - y0) * sh / vh
    bl = tuple(int(v * 255) for v in BLUE)
    if hl > 0:
        d.rounded_rectangle([p0[0] - 8, p0[1] - 8, p0[0] + (p1[0] - p0[0] + 16) * hl - 8, p1[1] + 8], 16, outline=bl + (255,), width=6)
    if tap >= 0:
        tx, ty = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        r = 18 + 70 * tap; d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 255, 255, int(230 * (1 - tap))), width=5)
        d.ellipse([tx - 22, ty - 22, tx + 22, ty + 22], fill=(255, 255, 255, int(200 * (1 - tap * 0.6))))
    if badge > 0:
        f = font("Archivo", 40, 900, 112); txt = "1. LINK"
        bw = f.getlength(txt) + 36; bx_ = min(max(p0[0] + 10, 12), sw - bw - 12); by_ = max(p0[1] - 74, 12)
        d.rounded_rectangle([bx_, by_, bx_ + bw, by_ + 58], 12, fill=bl + (int(255 * badge),))
        d.text((bx_ + bw / 2, by_ + 29), txt, font=f, fill=(255, 255, 255, int(255 * badge)), anchor="mm")
    ov = np.asarray(L).astype(np.float32) / 255
    scr = scr * (1 - ov[..., 3:4]) + ov[..., :3] * ov[..., 3:4]
    rgb = np.zeros((PH, PW, 3), np.float32) + 0.05
    rgb[BZ:BZ + sh, BZ:BZ + sw] = scr * rounded(sw, sh, 46)[..., None] + 0.05 * (1 - rounded(sw, sh, 46)[..., None])
    a = rounded(PW, PH, 60)
    # glass reflection
    X, Y = np.meshgrid(np.arange(PW), np.arange(PH)); refl = np.clip(1 - np.abs((X + Y * 0.6) / (PW + PH * 0.6) - 0.3) / 0.08, 0, 1) * 0.08
    rgb = np.clip(rgb + refl[..., None], 0, 1)
    pad = 70
    R = np.zeros((PH + 2 * pad, PW + 2 * pad, 3), np.float32); Al = np.zeros((PH + 2 * pad, PW + 2 * pad), np.float32)
    sh_ = np.zeros_like(Al); sh_[pad + 30:pad + PH + 26, pad + 16:pad + PW - 16] = 1; sh_ = cv2.GaussianBlur(sh_, (0, 0), 28) * 0.55
    Al[:] = sh_; R[pad:pad + PH, pad:pad + PW] = rgb * a[..., None]
    Al[pad:pad + PH, pad:pad + PW] = np.maximum(sh_[pad:pad + PH, pad:pad + PW] * (1 - a), a)
    R = R / np.maximum(Al[..., None], 1e-4) * (Al[..., None] > 0)
    return R, Al, (pad, pad)

def phone_state(t):
    if t < 3.55:
        z = 1 + 1.4 * ease_io((t - 2.75) / 0.35); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 2.75) / 0.35)
        return "profile", z, cy, ease_io((t - 2.9) / 0.25), (clamp((t - 3.15) / 0.3) if t >= 3.15 else -1), 0.0
    if t < 10.0:
        z = 1 + 0.9 * ease_io((t - 3.6) / 0.35); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 3.6) / 0.35)
        return "beacons", z, cy, ease_io((t - 3.8) / 0.25), (clamp((t - 4.1) / 0.3) if t >= 4.1 else -1), ease_out((t - 3.9) / 0.25)
    k = clamp((t - 24.8) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 25.1) / 0.3), (clamp((t - 25.4) / 0.4) if t >= 25.4 else -1), ease_out((t - 25.3) / 0.3)

# ------------------------------------------------------------------ captions
raw = json.load(open("words.json"))
words = []; i = 0
while i < len(raw):
    w = raw[i]; t_ = w["w"]
    if t_ == "2x40": words.append(dict(w="2× 40 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "2x30": words.append(dict(w="2× 30 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "6" and raw[i + 1]["w"] == "-7": words.append(dict(w="6–7", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "1" and raw[i + 1]["w"] == "-3": words.append(dict(w="1–3", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "Express" and raw[i + 1]["w"] == "-Versand": words.append(dict(w="Express-Versand", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "GT": words.append(dict(w="GTBuy-Haul!", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    rep = {"Video": "Bio", "erhält": "erhaltet", "Fünf": "5"}
    words.append(dict(w=rep.get(t_, t_), s=w["s"], e=w["e"])); i += 1
KEY = {"5", "kilo", "gtbuy-haul", "yalla", "link", "bio", "coupons", "2× 40 %", "2× 30 %", "shipping", "jetzt"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nxt = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if nxt is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 15 or (nxt["s"] - w["e"] > 0.35):
        chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    t0 = c[0]["s"] - 0.05
    nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 8.0
    adj = nxt0 - c[-1]["e"] < 0.45
    t1 = nxt0 if adj else min(c[-1]["e"] + 0.3, nxt0)
    CH.append(dict(words=c, t0=t0, t1=t1, adj=adj))
for j in range(len(CH)): CH[j]["prev_adj"] = j > 0 and CH[j - 1]["adj"]
F_CAP = font("Archivo", 72, 850, 108); F_KEY = font("InstrumentSerif-Italic", 100)
CAP_Y = 1430
def caption_layer(t, L):
    ch = next((c for c in CH if c["t0"] <= t < c["t1"]), None)
    if ch is None: return
    toks = [clean(w["w"]) for w in ch["words"]]; keys = [tk.lower() in KEY for tk in toks]
    fs = [F_KEY if k else F_CAP for k in keys]; sp = 30
    wd = [f.getlength(tk) for f, tk in zip(fs, toks)]; total = sum(wd) + sp * (len(toks) - 1)
    scale = min(1.0, 960 / total)
    kin = 1.0 if ch["prev_adj"] else ease_out((t - ch["t0"]) / 0.16); kout = 1.0 if ch["adj"] else ease_io((ch["t1"] - t) / 0.12)
    a = kin * kout
    if a <= 0: return
    cw, chh = int(total + 120), 230
    img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([20, 58, cw - 20, 190], 40, fill=(10, 12, 20, 150))   # legibility over the white sweater
    x = 60; base = 150
    for w, tk, wdt, f, k in zip(ch["words"], toks, wd, fs, keys):
        active = w["s"] - 0.03 <= t <= w["e"] + 0.03; spoken = t > w["e"] + 0.03
        col = (255, 170, 60) if (active or (spoken and k)) else (255, 255, 255)
        al = 1.0 if (active or spoken) else 0.55
        lay = Image.new("RGBA", (int(wdt) + 60, chh), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((30, base), tk, font=f, fill=col + (int(255 * al),), anchor="ls", stroke_width=2, stroke_fill=(10, 10, 12, int(200 * al)))
        if active:
            pk = clamp((t - w["s"] + 0.03) / 0.16); sc = 1.0 + 0.07 * math.sin(math.pi * pk)
            if sc > 1.003:
                nw, nh = int(lay.width * sc), int(lay.height * sc); lay = lay.resize((nw, nh), Image.BICUBIC)
                img.alpha_composite(lay, (int(x - 30 - (nw - wdt - 60) / 2), int(-(nh - chh) * base / chh))); x += wdt + sp; continue
        img.alpha_composite(lay, (int(x - 30), 0)); x += wdt + sp
    arr = np.asarray(img).astype(np.float32) / 255; ca = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(ca, 6, 0), (0, 0), 10) * 0.4; A_ = ca + sh * (1 - ca)
    rgb = arr[..., :3] * ca[..., None] / np.maximum(A_[..., None], 1e-4)
    rise = (1 - ease_out((t - ch["t0"]) / 0.18)) * 22 if not ch["prev_adj"] else 0
    place(L, (rgb, A_, (0, 0)), W / 2, CAP_Y + rise, s=scale, alpha=a)

# ------------------------------------------------------------------ graphics
ITEMS = [("Puffer-Weste", 8.0), ("Hose", 9.5), ("Jogger", 11.0), ("Half-Zip Schwarz", 12.5), ("Half-Zip Beige", 14.0),
         ("Half-Zip Weiß", 15.5), ("Trainingshose", 17.0), ("Polo", 18.5), ("Pufferjacke", 20.0)]
BOUNDS = [2.10] + [t0 for _, t0 in ITEMS] + [22.0, 23.0]
NUM = [sprite_chrome(tmask(f"{k + 1:02d}", font("Unbounded", 150, 900))[0], depth=12) for k in range(len(ITEMS))]
NAME = [sprite_fill(tmask(nm.upper(), font("Archivo", 96 if len(nm) < 14 else 78, 900, 118), 2)[0], WHITE, shadow=0.0, stroke=(INK, 7)) for nm, _ in ITEMS]

def whip(t):
    for n, b in enumerate(BOUNDS):
        sg = -1 if n % 2 == 0 else 1
        if b - 0.10 <= t < b: return sg * ease_in((t - (b - 0.10)) / 0.10) * W * 0.5
        if b <= t < b + 0.12: return -sg * (1 - ease_out((t - b) / 0.12)) * W * 0.5
    return 0.0

def progress(t, L):
    if t < 8.0 or t >= 23.0: return
    cur = max(k for k, (_, t0) in enumerate(ITEMS) if t >= t0) if t < 22.0 else len(ITEMS) - 1
    n = len(ITEMS); sw, gap = 86, 12; x0 = W / 2 - (n * sw + (n - 1) * gap) / 2
    im = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(n):
        x = x0 + k * (sw + gap)
        d.rounded_rectangle([x, 20, x + sw, 34], 7, fill=(10, 10, 14, 170))
        if k < cur: d.rounded_rectangle([x, 20, x + sw, 34], 7, fill=(250, 250, 248, 255))
        elif k == cur:
            t0 = ITEMS[k][1]; t1 = ITEMS[k + 1][1] if k + 1 < n else 23.0
            d.rounded_rectangle([x, 20, x + max(14, sw * clamp((t - t0) / (t1 - t0))), 34], 7, fill=(255, 140, 0, 255))
    arr = np.asarray(im).astype(np.float32) / 255
    place(L, (arr[..., :3], arr[..., 3], (0, 0)), W / 2, 70, alpha=ease_out((t - 8.0) / 0.3))

def scene(t, back, front):
    # HOOK
    a = win(t, 0.05, 2.05, 0.15, 0.12)
    if a:
        k = back_out((t - 0.05) / 0.45, 1.8)
        place(back, chrome_cached("5kg", KG_M, 22, (t - 0.4) / 0.9 if 0.4 <= t <= 1.3 else None), W / 2, 240, s=1.5 - 0.5 * k, alpha=a * clamp(t / .06), blur=max(0, 1 - t / .2) * 8)
        k2 = ease_out((t - 0.85) / 0.4)
        place(back, S["haulw"], W / 2, 440, s=1.25 - 0.25 * k2, alpha=a * k2)
    a = win(t, 1.72, 2.05, 0.1, 0.1)
    if a: place(front, S["yalla"], 820, 640, s=back_out((t - 1.72) / 0.3, 2.2), rot=-8, alpha=a)
    # COUPONS + link screenshots
    a = win(t, 2.45, 4.75, 0.3, 0.25)
    if a:
        k = ease_out((t - 2.45) / 0.45); ko = ease_in((t - 4.5) / 0.25) if t > 4.5 else 0
        nm, z, cy, hl, tap, badge = phone_state(t)
        px = 840 + (1 - k) * 500 + ko * 600
        place(front, phone(nm, z, cy, hl, tap, badge), px, 540, rot=-4 * (1 - k) + 3, alpha=a, s=0.74)
        place(front, S["logo_s"], px - 150, 150, s=back_out((t - 2.8) / 0.35, 2.0), alpha=a * clamp((t - 2.8) / .1), rot=-8)
    for key_, t0, y in (("c40", 4.48, 250), ("c30", 5.46, 390)):
        a = win(t, t0, 6.85, 0.2, 0.2)
        if a: place(front, S[key_], 1030, y, anchor=(1.0, 0.5), s=back_out((t - t0) / 0.35, 2.2), alpha=a)
    a = win(t, 6.36, 6.85, 0.15, 0.2)
    if a: place(front, S["aufship"], 1030, 520, anchor=(1.0, 0.5), alpha=a)
    a = win(t, 6.90, 7.98, 0.12, 0.12)
    if a:
        k = back_out((t - 6.90) / 0.4, 1.8)
        place(front, S["jetzt"], W / 2, 170, alpha=a, s=k)
        place(front, chrome_cached("anm", ANM_M, 16, (t - 7.1) / 0.7 if 7.1 <= t <= 7.8 else None), W / 2, 330, s=back_out((t - 7.02) / 0.4, 1.8), alpha=a * clamp((t - 7.02) / .05))
    # ITEM MONTAGE
    for k, (nm, t0) in enumerate(ITEMS):
        t1 = ITEMS[k + 1][1] if k + 1 < len(ITEMS) else 22.0
        if not (t0 <= t < t1): continue
        u = t - t0; a = min(ease_out(u / 0.15), ease_io((t1 - t) / 0.1))
        place(front, NUM[k], 215, 250, s=1.35 - 0.35 * back_out(u / 0.35, 1.8), alpha=a, rot=-6)
        ks = ease_out((u - 0.08) / 0.35)
        ns = min(1.0, 960 / (NAME[k][1].shape[1] - 100))
        place(front, NAME[k], W / 2, 1560 + (1 - ks) * 60, s=ns, alpha=a * ks)
        m = np.zeros((H, W), np.float32); wl = (NAME[k][1].shape[1] - 100) * ns
        cv2.line(m, (int(W / 2 - wl / 2), 1632), (int(W / 2 - wl / 2 + wl * ease_io((u - 0.2) / 0.35)), 1632), 1.0, 12, cv2.LINE_AA)
        m *= a * (u > 0.2); front[0] *= (1 - m[..., None]); front[0] += BLUE * m[..., None]; front[1] *= (1 - m); front[1] += m
    a = win(t, 22.05, 22.98, 0.15, 0.1)
    if a: place(front, S["detail"], W / 2, 1560, s=back_out((t - 22.05) / 0.35, 2.0), alpha=a)
    progress(t, front)

def fullscreen(t, comp): return comp

def endcard(t, comp):
    if t < 23.45: return comp
    L = new_layer()
    k0 = ease_out((t - 23.5) / 0.5)
    place(L, S["logo_m"], W / 2, 160, s=0.7 + 0.3 * back_out((t - 23.5) / 0.5, 1.8), rx=-70 * (1 - k0), alpha=k0)
    k = ease_out((t - 23.65) / 0.45)
    place(L, chrome_cached("5kgh", KGH_M, 16, (t - 24.0) / 0.9 if 24.0 <= t <= 24.9 else None), W / 2, 385, s=0.9 + 0.1 * k, rx=-60 * (1 - k), alpha=clamp((t - 23.65) / .1))
    for n, key in enumerate(("e1", "e2")):
        t0 = 23.95 + n * 0.18
        if t >= t0: place(L, S[key], W / 2, 545 + n * 96, s=back_out((t - t0) / 0.35, 2.0), alpha=ease_out((t - t0) / .2))
    k3 = ease_out((t - 24.2) / 0.55)
    place(L, S["haul_card"], 300, 1180 + (1 - k3) * 300, rot=-4, alpha=k3)
    nm, z, cy, hl, tap, badge = phone_state(t)
    place(L, phone(nm, z, cy, hl, tap, badge), 790, 1180 + (1 - k3) * 380, rot=3 * (1 - k3) + 2, alpha=k3, s=0.66)
    k4 = ease_out((t - 25.6) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1690, s=back_out((t - 25.6) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

# ------------------------------------------------------------------ main
def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=8, eps=2e-3):
    mI, mp_ = box(I, r), box(p, r); a = (box(I * p, r) - mI * mp_) / (box(I * I, r) - mI * mI + eps); b = mp_ - a * mI
    return box(a, r) * I + box(b, r)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.22 * np.clip(np.sqrt(((XX - W / 2) / (W * .75)) ** 2 + ((YY - H * .45) / (H * .72)) ** 2) - .45, 0, 1) ** 1.5)[..., None]
rng = np.random.default_rng(A + 31)
sA, sB = min(A, FREEZE), min(B, NSRC)
sel = f"select='between(n\\,{sA}\\,{max(sB, sA + 1) - 1})'"
dv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "enh.mov", "-vf", sel, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "mask.mkv", "-vf", sel, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
if PREVIEW is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "ffv1", "-level", "3", OUT], stdin=subprocess.PIPE)
frozen = None; frame = m = None
for i in range(A, B):
    t = i / FPS
    if i <= FREEZE or frozen is None:
        fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
        if len(fb) == W * H * 3:
            frame = np.frombuffer(fb, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
            m = np.frombuffer(mb, np.uint8).reshape(H, W).astype(np.float32) / 255
        if i == FREEZE or (i > FREEZE and frozen is None): frozen = (frame, m)
    if PREVIEW is not None and not any(abs(t - o) < 0.5 / FPS for o in PREVIEW): continue
    fr, mm = (frozen if i >= FREEZE else (frame, m))
    gs = cv2.resize(cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    mm = np.clip(cv2.resize(guided(gs, cv2.resize(mm, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    fi = min(i, FREEZE)
    M = camera(fi, t)
    dx = whip(t)
    M[0, 2] += dx
    zb = (1 - t / 0.3) if t < 0.3 else 0
    if zb > 0.02:
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(6):
            sk = 1 + zb * 0.07 * k / 5; Mk = M.copy(); Mk[:, :2] *= sk; Mk[0, 2] = M[0, 2] * sk + W / 2 * (1 - sk); Mk[1, 2] = M[1, 2] * sk + H * .45 * (1 - sk)
            acc += cv2.warpAffine(fr, Mk, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cf = acc / 6
    else:
        cf = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    cm = cv2.warpAffine(mm, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if abs(dx) > 1:
        k = int(abs(dx) / 6) | 1; cf = cv2.blur(cf, (k, 1)); cm = cv2.blur(cm, (k, 1))
    back, front = new_layer(), new_layer()
    scene(t, back, front)
    comp = cf * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])
    comp = fullscreen(t, comp)
    comp = comp * (1 - front[1][..., None]) + front[0]
    if t >= 23.45:
        k = ease_io((t - 23.45) / 0.5); comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.55 * k)
    comp = endcard(t, comp)
    P_ = new_layer(); caption_layer(t, P_)
    comp = comp * (1 - P_[1][..., None]) + P_[0]
    comp = comp * VIGN
    comp += rng.normal(0, 0.011, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.3: comp *= ease_io((DUR - t) / 0.3)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if PREVIEW is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=88)
    else:
        enc.stdin.write(out.tobytes())
        if (i - A) % 60 == 0: print(A, "frame", i, flush=True)
if PREVIEW is None: enc.stdin.close(); enc.wait()
print("done", A, B)
