"""Talking-head creator edit (Christmas ordering tips): natural enhancement + front-light cast correction on the
person, depth headlines behind the head, Higgsfield cards behind the person, code motion graphics (price chart,
save badge), word-synced captions, settle-zooms on cuts, mixed voice / pad / SFX."""
import json, subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, N = 1080, 1920, 30, 826
DUR = N / FPS
SRC, MASK = "input_cfr.mov", "mask.mkv"
OUT = sys.argv[1] if len(sys.argv) > 1 else "out.mp4"
ONLY = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
ENH = "hqdn3d=1.2:1.0:3:3,cas=0.4:planes=1,eq=contrast=1.03:saturation=1.04"
SERIF, SERIF_I = "fonts/InstrumentSerif.ttf", "fonts/InstrumentSerif-Italic.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
INK, ACC, GOLD = (22, 20, 19), (172, 52, 40), (255, 203, 82)
CUTS = [0.0, 3.667, 6.133, 8.9, 11.367, 16.467, 25.933, DUR]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
FC = {}
def font(p, s):
    k = (p, int(s)); FC.setdefault(k, ImageFont.truetype(p, int(s))); return FC[k]

# ---------------------------------------------------------------- headlines behind the head
def make_hl(parts, label, size, baseline, max_w=980):
    wid = lambda sz: sum(font(SERIF_I if it else SERIF, sz).getlength(tx) for tx, it in parts)
    while wid(size) > max_w: size -= 6
    x = (W - wid(size)) / 2; chars = []; i = 0
    for tx, it in parts:
        f = font(SERIF_I if it else SERIF, size)
        for ch in tx: chars.append((ch, x, i, f, ACC if it else INK)); x += f.getlength(ch); i += 1
    return dict(chars=chars, label=label, size=size, baseline=baseline)

def render_hl(h, t, t0, tl, t1, label_at):
    if t < t0 or t > t1: return None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    out_k = eio((t1 - t) / 0.35); n = len(h["chars"]); span = tl - t0
    for ch, x, i, f, col in h["chars"]:
        st = t0 + i * (span * 0.45 / max(n - 1, 1)); k = eo((t - st) / (span * 0.55)); a = k * out_k
        if a > 0: d.text((x, h["baseline"] + (1 - k) * 50), ch, font=f, fill=col + (int(255 * a),), anchor="ls")
    lk = eo((t - label_at) / 0.4); la = lk * out_k
    if la > 0:
        lf = font(INTER.format("SemiBold"), 32); sp = 8; txt = h["label"]
        tw = sum(lf.getlength(c) + sp for c in txt) - sp
        lx = (W - tw) / 2; ly = h["baseline"] - h["size"] * 0.92 - 36 + (1 - lk) * 10; rw = 44 * lk
        d.line([(lx - 20 - rw, ly + 19), (lx - 20, ly + 19)], fill=ACC + (int(255 * la),), width=3)
        d.line([(lx + tw + 20, ly + 19), (lx + tw + 20 + rw, ly + 19)], fill=ACC + (int(255 * la),), width=3)
        for c in txt: d.text((lx, ly), c, font=lf, fill=ACC + (int(255 * la),)); lx += lf.getlength(c) + sp
    blur = max(1 - eo((t - t0) / (span * 0.9)), 1 - out_k) * 7
    if blur > 0.3: img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img).astype(np.float32) / 255
    s = 1.0 + 0.02 * clamp((t - t0) / (t1 - t0)) + 0.035 * (1 - out_k)
    return cv2.warpAffine(arr, cv2.getRotationMatrix2D((W / 2, h["baseline"] - h["size"] * 0.35), 0, s), (W, H))

HEADLINES = [  # (headline, start, land, end, label_at) — baselines from measured head tops (388 / 484 / 472)
    (make_hl([("Jetzt ", False), ("bestellen", True)], "BEVOR ES ZU SPÄT IST", 205, 438), 0.05, 0.46, 3.50, 0.75),
    (make_hl([("Delays", True)], "& OUT OF STOCK", 270, 575), 8.08, 8.50, 9.62, 8.75),
    (make_hl([("4 ", True), ("Coupons", False)], "NUR ÜBER MEINEN LINK", 230, 556), 24.02, 24.44, 25.88, 24.85),
]

# ---------------------------------------------------------------- Higgsfield image cards (behind the person)
def rounded(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return np.asarray(m).astype(np.float32) / 255
def load_card(path, label, cw=420, ch=540):
    im = Image.open(path).convert("RGB"); bw, bh = int(cw * 1.14), int(ch * 1.14)
    s = max(bw / im.width, bh / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    l, tp = (im.width - bw) // 2, (im.height - bh) // 2
    return dict(img=np.asarray(im.crop((l, tp, l + bw, tp + bh))).astype(np.float32) / 255, cw=cw, ch=ch, label=label, rm=rounded(cw, ch, 30))
CARDS = [(load_card("img/gifts.png", "Weihnachtszeit"), 4.30, 6.02),
         (load_card("img/warehouse.png", "Seller out of stock"), 9.75, 11.30),
         (load_card("img/coupons.png", "2× 40 %  ·  2× 30 %"), 19.60, 22.35)]

def card_layer(c, t, t0, t1, side):
    if t < t0 or t > t1: return None
    kin = eo((t - t0) / 0.55); kout = eio((t1 - t) / 0.4); a = min(kin, kout)
    cw, ch = c["cw"], c["ch"]; p = clamp((t - t0) / (t1 - t0)); z = 1.0 + 0.12 * (1 - eio(p))
    big = c["img"]; bh, bw = big.shape[:2]
    M = np.float32([[z, 0, (bw - cw * z) / 2], [0, z, (bh - ch * z) / 2]])
    tile = cv2.warpAffine(big, M, (cw, ch), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    s = 0.92 + 0.08 * kin; tw, th = int(cw * s), int(ch * s)
    tile = cv2.resize(tile, (tw, th), interpolation=cv2.INTER_AREA); rm = cv2.resize(c["rm"], (tw, th), interpolation=cv2.INTER_AREA)
    cx = 800 if side == "right" else 280; cy = 360 + (1 - kin) * 50
    X, Y = int(cx - tw / 2), int(cy - th / 2)
    g = (1 - np.linspace(0, 1, th)[:, None]) ** 2.4 * 0.55                     # top gradient for the label
    tile = tile * (1 - g[..., None])
    rgb = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
    rgb[Y:Y + th, X:X + tw] = tile; al[Y:Y + th, X:X + tw] = rm
    br = np.zeros((H, W), np.uint8); cv2.rectangle(br, (X, Y), (X + tw - 1, Y + th - 1), 255, 2)
    br = (cv2.bitwise_and(br, (al * 255).astype(np.uint8)).astype(np.float32) / 255 * 0.35)[..., None]
    rgb = rgb * (1 - br) + br
    sh = np.zeros((H, W), np.float32); cv2.rectangle(sh, (X + 14, Y + 30), (X + tw - 14, Y + th + 26), 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 28) * 0.38
    lab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lab).text((cx, Y + 40), c["label"], font=font(INTER.format("SemiBold"), 31), fill=(255, 255, 255, 245), anchor="mm")
    lab = np.asarray(lab).astype(np.float32) / 255; la = lab[..., 3:4]
    orgb = rgb * al[..., None]; oa = al + sh * (1 - al)
    orgb = orgb * (1 - la) + lab[..., :3] * la; oa = oa * (1 - la[..., 0]) + la[..., 0]
    return orgb * a, np.clip(oa, 0, 1) * a

# ---------------------------------------------------------------- motion graphic: rising shipping price chart
def chart_layer(t, t0=14.62, t1=16.42):
    if t < t0 or t > t1: return None
    kin = back((t - t0) / 0.45, 1.2); kout = eio((t1 - t) / 0.3); a = clamp(min(eo((t - t0) / 0.3), kout))
    cw, ch = 470, 270; cx, cy = 790, 350 + (1 - eo((t - t0) / 0.45)) * 40
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s = 0.9 + 0.1 * kin; w2, h2 = cw * s / 2, ch * s / 2
    d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], 28, fill=(16, 15, 17, int(225 * a)))
    lf = font(INTER.format("SemiBold"), 26)
    d.text((cx - w2 + 26, cy - h2 + 24), "SHIPPINGPREISE", font=lf, fill=(255, 255, 255, int(170 * a)))
    # line chart drawn progressively, peaking on the word "Shippingpreise" (~15.95 s)
    pts = [(0, .18), (.16, .22), (.3, .2), (.44, .34), (.58, .38), (.72, .6), (.86, .7), (1, .95)]
    pr = eio((t - t0 - 0.25) / (15.95 - t0 - 0.25))
    gx0, gx1, gy0, gy1 = cx - w2 + 28, cx + w2 - 28, cy + h2 - 30, cy - h2 + 80
    P = [(gx0 + (gx1 - gx0) * x, gy0 + (gy1 - gy0) * y) for x, y in pts]
    seglen = [np.hypot(P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]) for i in range(len(P) - 1)]
    L = sum(seglen) * pr; drawn = [P[0]]
    for i, sl in enumerate(seglen):
        if L <= 0: break
        f = min(1, L / sl); drawn.append((P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f)); L -= sl
    if len(drawn) > 1:
        poly = drawn + [(drawn[-1][0], gy0), (drawn[0][0], gy0)]
        d.polygon(poly, fill=ACC + (int(70 * a),))
        d.line(drawn, fill=(255, 120, 96, int(255 * a)), width=5, joint="curve")
        ex, ey = drawn[-1]; r = 9; d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(255, 255, 255, int(255 * a)))
    if t > 15.95:  # value pill pops at the peak
        k = back((t - 15.95) / 0.3, 1.6); vf = font(INTER.format("Bold"), 30); txt = "↑ steigt"
        tw = vf.getlength(txt); px, py = gx1 - tw - 8, gy1 - 58
        d.rounded_rectangle([px - 14, py - 6, px + tw + 14, py + 40], 20, fill=(255, 120, 96, int(255 * a * clamp(k))))
        d.text((px, py), txt, font=vf, fill=(20, 18, 17, int(255 * a * clamp(k))))
    return np.asarray(img).astype(np.float32) / 255

# ---------------------------------------------------------------- motion graphic: save badge
def save_layer(t, t0=25.98, t_fill=26.62):
    if t < t0: return None
    k = back((t - t0) / 0.42, 1.8); a = clamp(eo((t - t0) / 0.25)) * clamp((DUR - 0.05 - t) / 0.3)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cx, cy = W / 2, 330; R = 78 * clamp(k, 0, 1.2)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, int(240 * a)))
    fill = eo((t - t_fill) / 0.25)
    bw, bh = 40 * k, 54 * k
    bm = [(cx - bw / 2, cy - bh / 2), (cx + bw / 2, cy - bh / 2), (cx + bw / 2, cy + bh / 2), (cx, cy + bh / 2 - 15 * k), (cx - bw / 2, cy + bh / 2)]
    if R > 10:
        d.polygon(bm, fill=(ACC + (int(255 * a * fill),)) if fill > 0 else None, outline=INK + (int(255 * a),))
        d.line(bm + [bm[0]], fill=INK + (int(255 * a),), width=5, joint="curve")
    lf = font(INTER.format("Bold"), 34); txt = "Video speichern"
    lk = eo((t - t0 - 0.2) / 0.35)
    d.text((cx, cy + 118 + (1 - lk) * 10), txt, font=lf, fill=INK + (int(255 * a * lk),), anchor="mm")
    return np.asarray(img).astype(np.float32) / 255

# ---------------------------------------------------------------- captions
raw = json.load(open("words.json")); words = []; i = 0
while i < len(raw):
    w = raw[i]; nx = raw[i + 1] if i + 1 < len(raw) else None
    if w["w"] == "100" and nx and nx["w"].startswith("%"): words.append(dict(w="100 %", s=w["s"], e=nx["e"])); i += 2; continue
    if w["w"] == "240": words.append(dict(w="2× 40 %", s=w["s"], e=nx["e"])); i += 2; continue
    if w["w"] == "230": words.append(dict(w="2× 30 %", s=w["s"], e=nx["e"])); i += 2; continue
    rep = {"cook,": "cooked,", "erhält": "erhaltet"}
    words.append(dict(w=rep.get(w["w"], w["w"]), s=w["s"], e=w["e"])); i += 1
KEY = {"bestellt", "cooked", "weihnachtszeit", "delays", "out", "of", "stock", "shippingpreise", "sparen", "account",
       "bio", "2× 40 %", "2× 30 %", "4", "coupons", "link", "speichert", "100 %"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nx = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if nx is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 15 or nx["s"] - w["e"] > 0.35:
        chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    nx0 = chunks[j + 1][0]["s"] - 0.06 if j + 1 < len(chunks) else DUR
    adj = nx0 - c[-1]["e"] < 0.5
    CH.append(dict(words=c, t0=c[0]["s"] - 0.06, t1=nx0 if adj else min(c[-1]["e"] + 0.3, nx0), adj=adj))
for j in range(len(CH)): CH[j]["prev_adj"] = j > 0 and CH[j - 1]["adj"]
CF = font(INTER.format("ExtraBold"), 64)
def caption_layer(t):
    ch = next((c for c in CH if c["t0"] <= t < c["t1"]), None)
    if ch is None: return None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    toks = [clean(w["w"]) for w in ch["words"]]; sp = CF.getlength(" ") * 1.3; wd = [CF.getlength(x) for x in toks]
    total = sum(wd) + sp * (len(toks) - 1)
    a = (1.0 if ch["prev_adj"] else eo((t - ch["t0"]) / 0.18)) * (1.0 if ch["adj"] else eio((ch["t1"] - t) / 0.14))
    cy = 1515 + (1 - eo((t - ch["t0"]) / 0.16)) * 12
    ImageDraw.Draw(img).rounded_rectangle([W / 2 - total / 2 - 34, cy - 62, W / 2 + total / 2 + 34, cy + 62], 38, fill=(14, 14, 16, int(150 * a)))
    x = W / 2 - total / 2
    for w, tok, wdt in zip(ch["words"], toks, wd):
        active = w["s"] - 0.03 <= t <= w["e"] + 0.02; spoken = t > w["e"] + 0.02
        if active: col, al = GOLD, 1.0
        elif spoken: col, al = (GOLD if tok.lower() in KEY else (255, 255, 255)), 1.0
        else: col, al = (255, 255, 255), 0.5
        lay = Image.new("RGBA", (int(wdt) + 40, 140), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((20, 70), tok, font=CF, fill=col + (int(255 * al * a),), anchor="lm")
        if active:
            pk = eo((t - w["s"] + 0.03) / 0.14); sc = 1.0 + 0.07 * (1 - abs(2 * pk - 1))
            if sc > 1.002: lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.LANCZOS)
        img.alpha_composite(lay, (int(x + wdt / 2 - lay.width / 2), int(cy - lay.height / 2))); x += wdt + sp
    return np.asarray(img).astype(np.float32) / 255

# ---------------------------------------------------------------- camera, matte, colour
def zoom(t):
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        if a <= t < b: return 1.0 + 0.03 * eio((t - a) / (b - a)) + 0.025 * (1 - eo((t - a) / 0.4))
    return 1.03
def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=10, eps=2e-3):
    mI, mp = box(I, r), box(p, r); a = (box(I * p, r) - mI * mp) / (box(I * I, r) - mI * mI + eps); b = mp - a * mI
    return box(a, r) * I + box(b, r)
DELTA = np.load("ab_delta.npy") / 0.68 * 0.5          # Lab a*/b* front-light cast, 50 % correction
HT = np.load("headtop.npy")
SIDES = ["left" if np.median((HT[int(t0 * FPS):int(t1 * FPS), 1] + HT[int(t0 * FPS):int(t1 * FPS), 2]) / 2) > 600 else "right" for _, t0, t1 in CARDS]
print("sides", SIDES, flush=True)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.12 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1.6) ** 1.3)[..., None]
rng = np.random.default_rng(5)

dv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", ENH, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", MASK, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
if ONLY is None:
    af = ("[1:a]aresample=48000,highpass=f=75,afftdn=nr=8:nf=-40:tn=1,acompressor=threshold=-20dB:ratio=2.5:attack=12:release=180:makeup=2,"
          "loudnorm=I=-15:TP=-2:LRA=8,aresample=48000,asplit=2[v][vsc];"
          "[2:a]volume=-21dB[pd];[pd][vsc]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=450[pdd];"
          "[3:a]volume=0dB[sx];[v][pdd][sx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.89,"
          f"afade=t=out:st={DUR - 0.4}:d=0.4[a]")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", SRC, "-i", "pad.wav", "-i", "sfx.wav", "-filter_complex", af, "-map", "0:v", "-map", "[a]",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
for i in range(N):
    fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
    if len(fb) < W * H * 3 or len(mb) < W * H: break
    t = i / FPS
    if ONLY is not None and not any(abs(t - o) < 0.5 / FPS for o in ONLY): continue
    f8 = np.frombuffer(fb, np.uint8).reshape(H, W, 3)
    m = np.frombuffer(mb, np.uint8).reshape(H, W).astype(np.float32) / 255
    # front-light colour cast correction, person only, weighted by luminance
    msoft = cv2.GaussianBlur(m, (0, 0), 6)
    lab = cv2.cvtColor(f8, cv2.COLOR_RGB2LAB).astype(np.float32)
    wl = np.clip(lab[..., 0:1] / 255 / 0.82, 0, 1) ** 1.6
    lab[..., 1:] -= DELTA[min(i, len(DELTA) - 1)] * (msoft[..., None] * wl)
    frame = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32) / 255
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    m = np.clip(cv2.resize(guided(gs, cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    s = zoom(t); M = cv2.getRotationMatrix2D((540, 700), 0, s)
    frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    m = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    bgk = (1 - m)[..., None]; comp = frame
    for h, t0, tl, t1, la in HEADLINES:
        L = render_hl(h, t, t0, tl, t1, la)
        if L is not None: a = L[..., 3:4] * bgk; comp = comp * (1 - a) + L[..., :3] * a
    for (c, t0, t1), side in zip(CARDS, SIDES):
        r = card_layer(c, t, t0, t1, side)
        if r is not None: rgb, al = r; comp = comp * (1 - al[..., None] * bgk) + rgb * bgk
    G = chart_layer(t)
    if G is not None: a = G[..., 3:4] * bgk; comp = comp * (1 - a) + G[..., :3] * a
    comp = comp * VIG
    for layer in (save_layer(t), caption_layer(t)):
        if layer is not None: a = layer[..., 3:4]; comp = comp * (1 - a) + layer[..., :3] * a
    comp = comp + rng.normal(0, 0.008, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.4: comp = comp * clamp((DUR - t) / 0.4)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if ONLY is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=92)
    else:
        enc.stdin.write(out.tobytes())
        if i % 120 == 0: print("frame", i, flush=True)
if ONLY is None: enc.stdin.close(); enc.wait()
print("done")
