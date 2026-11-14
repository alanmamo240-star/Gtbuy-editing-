"""v2 creator edit: depth headlines behind the head (mixed serif/italic), Higgsfield B-roll cards behind
the person, word-synced captions, tip progress bar, eased camera moves. Person pixels are never altered."""
import json, subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SRC, MASK = "input.mov", "mask.mkv"
OUT = sys.argv[1] if len(sys.argv) > 1 else "out.mp4"
ONLY = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
DUR = 27.08
N = 813
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
SERIF, SERIF_I = "fonts/InstrumentSerif.ttf", "fonts/InstrumentSerif-Italic.ttf"
INK = (20, 18, 17)
ACCENT_HL = (176, 58, 36)     # deep terracotta for headline accents / labels
GOLD = (255, 203, 82)         # caption highlight

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
FONTS = {}
def font(p, s):
    k = (p, int(s))
    if k not in FONTS: FONTS[k] = ImageFont.truetype(p, int(s))
    return FONTS[k]

# ---------------------------------------------------------------- headlines
def make_headline(label, parts, size=290, max_w=960, baseline=640):
    """parts: list of (text, italic_accent: bool)"""
    def width(sz): return sum(font(SERIF_I if it else SERIF, sz).getlength(tx) for tx, it in parts)
    while width(size) > max_w: size -= 6
    x = (W - width(size)) / 2; chars = []; i = 0
    for tx, it in parts:
        f = font(SERIF_I if it else SERIF, size)
        for ch in tx:
            chars.append((ch, x, i, f, ACCENT_HL if it else INK)); x += f.getlength(ch); i += 1
    return dict(label=label, chars=chars, size=size, baseline=baseline)

def render_headline(hl, t, t0, t1):
    if t < t0 or t > t1: return None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    out_k = ease_io((t1 - t) / 0.4)
    lk = ease_out((t - t0) / 0.5); la = lk * out_k
    lf = font(INTER.format("SemiBold"), 33); sp = 9; txt = hl["label"]
    tw = sum(lf.getlength(c) + sp for c in txt) - sp
    lx = (W - tw) / 2; ly = hl["baseline"] - hl["size"] * 0.98 - 22 + (1 - lk) * 14
    rw = 46 * lk
    col = ACCENT_HL + (int(255 * la),)
    d.line([(lx - 22 - rw, ly + 21), (lx - 22, ly + 21)], fill=col, width=3)
    d.line([(lx + tw + 22, ly + 21), (lx + tw + 22 + rw, ly + 21)], fill=col, width=3)
    for c in txt: d.text((lx, ly), c, font=lf, fill=col); lx += lf.getlength(c) + sp
    for ch, x, i, f, colr in hl["chars"]:
        k = ease_out((t - t0 - 0.1 - i * 0.035) / 0.6)
        a = k * out_k
        if a <= 0: continue
        d.text((x, hl["baseline"] + (1 - k) * 46), ch, font=f, fill=colr + (int(255 * a),), anchor="ls")
    # soft focus-pull on entry and exit (blur -> sharp)
    blur = max(1 - ease_out((t - t0) / 0.55), 1 - out_k) * 7
    if blur > 0.3: img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img).astype(np.float32) / 255
    s = 1 + 0.035 * (1 - out_k) + 0.02 * clamp((t - t0) / (t1 - t0))   # slow drift + exit push
    M = cv2.getRotationMatrix2D((W / 2, hl["baseline"] - hl["size"] / 3), 0, s)
    return cv2.warpAffine(arr, M, (W, H))

HEADLINES = [
    (make_headline("FÜR JEDEN HAUL", [("3 ", True), ("Tipps", False)]), 0.02, 2.05),
    (make_headline("TIPP 01  ·  GTBUY", [("4 ", True), ("Coupons", False)]), 10.30, 12.95),
    (make_headline("TIPP 02  ·  VERSAND", [("3–10 ", True), ("kg", False)], baseline=585), 13.05, 17.70),
    (make_headline("TIPP 03", [("Verpackung", False)]), 23.25, 25.40),
]

# ---------------------------------------------------------------- B-roll cards
def rounded(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return np.asarray(m).astype(np.float32) / 255

def load_card(path, label, cw=420, ch=560):
    im = Image.open(path).convert("RGB")
    bw, bh = int(cw * 1.14), int(ch * 1.14)
    s = max(bw / im.width, bh / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    l, tp = (im.width - bw) // 2, (im.height - bh) // 2
    return dict(img=np.asarray(im.crop((l, tp, l + bw, tp + bh))).astype(np.float32) / 255,
                cw=cw, ch=ch, label=label, rm=rounded(cw, ch, 34))

CARDS = [
    (load_card("img/coupons.png", "2× 40 %  ·  2× 30 %"), 8.25, 10.25),
    (load_card("img/scale_clean.png", "3 – 10 kg pro Paket"), 17.80, 22.85),
    (load_card("img/sneakers.png", "Ohne Originalkarton"), 25.45, 27.08),
]

def card_layer(c, t, t0, t1, side):
    if t < t0 or t > t1 + 1e-6: return None
    kin = ease_out((t - t0) / 0.6)
    kout = 1.0 if t1 >= DUR - 0.05 else ease_io((t1 - t) / 0.45)
    a = min(kin, kout)
    cw, ch = c["cw"], c["ch"]
    p = clamp((t - t0) / max(t1 - t0, 0.1))
    z = 1.0 + 0.12 * (1 - ease_io(p))
    big = c["img"]; bh, bw = big.shape[:2]
    x0 = (bw - cw * z) / 2; y0 = (bh - ch * z) / 2
    M = np.float32([[z, 0, x0], [0, z, y0]])
    tile = cv2.warpAffine(big, M, (cw, ch), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    s = 0.92 + 0.08 * kin
    cx = 800 if side == "right" else 280
    cy = 430 + (1 - kin) * 60
    tw, th = int(cw * s), int(ch * s)
    tile = cv2.resize(tile, (tw, th), interpolation=cv2.INTER_AREA)
    rm = cv2.resize(c["rm"], (tw, th), interpolation=cv2.INTER_AREA)
    X, Y = int(cx - tw / 2), int(cy - th / 2)
    rgb = np.zeros((H, W, 3), np.float32); al = np.zeros((H, W), np.float32)
    rgb[Y:Y + th, X:X + tw] = tile; al[Y:Y + th, X:X + tw] = rm
    # bottom gradient for label legibility inside the card
    g = np.linspace(0, 1, th)[:, None] ** 2.2 * 0.55
    rgb[Y:Y + th, X:X + tw] *= (1 - g[..., None])
    # hairline border
    br = np.zeros((H, W), np.uint8); cv2.rectangle(br, (X, Y), (X + tw - 1, Y + th - 1), 255, 2)
    br = (cv2.bitwise_and(br, (al * 255).astype(np.uint8)).astype(np.float32) / 255 * 0.35)[..., None]
    rgb = rgb * (1 - br) + br
    # shadow
    sh = np.zeros((H, W), np.float32)
    cv2.rectangle(sh, (X + 14, Y + 34), (X + tw - 14, Y + th + 30), 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 30) * 0.42
    # label inside card bottom
    lab = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lab)
    lf = font(INTER.format("SemiBold"), 31)
    d.text((cx, Y + th - 44), c["label"], font=lf, fill=(255, 255, 255, 245), anchor="mm")
    lab = np.asarray(lab).astype(np.float32) / 255
    out_rgb = rgb * al[..., None]; out_a = al + sh * (1 - al)
    la = lab[..., 3:4]
    out_rgb = out_rgb * (1 - la) + lab[..., :3] * la
    out_a = out_a * (1 - la[..., 0]) + la[..., 0]
    return out_rgb * a, np.clip(out_a, 0, 1) * a

# ---------------------------------------------------------------- captions (text fixes)
raw = json.load(open("words.json"))
def W_(w, s, e): return dict(w=w, s=s, e=e)
words = []
i = 0
while i < len(raw):
    w = raw[i]
    if w["w"] == "GT" and i + 2 < len(raw):
        words.append(W_("GTBuy-Account,", w["s"], raw[i + 2]["e"])); i += 3; continue
    if w["w"] == "240": words.append(W_("2× 40 %", w["s"], raw[i + 1]["e"])); i += 2; continue
    if w["w"] == "2x30": words.append(W_("2× 30 %", w["s"], raw[i + 1]["e"])); i += 2; continue
    if w["w"] in ("wird", "Ihnen", "verhalten,"): i += 1; continue  # unintelligible, left out
    rep = {"erhält": "erhaltet", "3kg": "3 kg", "10kg": "10 kg", "Haul": "Haul"}
    words.append(W_(rep.get(w["w"], w["w"]), w["s"], w["e"])); i += 1
KEY = {"tipps", "haul", "gtbuy-account", "coupons", "shipping", "niemals", "teuer", "teurer",
       "originalverpackung", "3 kg", "10 kg", "2× 40 %", "2× 30 %", "4", "bio"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nxt = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if (nxt is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 15 or (nxt["s"] - w["e"] > 0.35)):
        chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    t0 = c[0]["s"] - 0.06
    nxt0 = chunks[j + 1][0]["s"] - 0.06 if j + 1 < len(chunks) else DUR
    adj = nxt0 - c[-1]["e"] < 0.5
    t1 = nxt0 if adj else min(c[-1]["e"] + 0.3, nxt0)
    CH.append(dict(words=c, t0=t0, t1=t1, adj=adj))
for j in range(len(CH)): CH[j]["prev_adj"] = j > 0 and CH[j - 1]["adj"]

CF = font(INTER.format("ExtraBold"), 64)
def caption_layer(t):
    ch = next((c for c in CH if c["t0"] <= t < c["t1"]), None)
    if ch is None: return None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    toks = [clean(w["w"]) for w in ch["words"]]
    sp = CF.getlength(" "); wd = [CF.getlength(x) for x in toks]; total = sum(wd) + sp * (len(toks) - 1)
    kin = 1.0 if ch["prev_adj"] else ease_out((t - ch["t0"]) / 0.18)
    kout = 1.0 if ch["adj"] else ease_io((ch["t1"] - t) / 0.14)
    a = kin * kout
    rise = ease_out((t - ch["t0"]) / 0.16)
    cy = 1500 + (1 - rise) * 12
    px, py = 34, 22
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([W / 2 - total / 2 - px, cy - 40 - py, W / 2 + total / 2 + px, cy + 40 + py],
                                           38, fill=(14, 14, 16, int(140 * a)))
    img.alpha_composite(pill)
    x = W / 2 - total / 2
    for w, tok, wdt in zip(ch["words"], toks, wd):
        active = w["s"] - 0.03 <= t <= w["e"] + 0.02
        spoken = t > w["e"] + 0.02
        if active: col, al = GOLD, 1.0
        elif spoken: col, al = (GOLD if tok.lower() in KEY else (255, 255, 255)), 1.0
        else: col, al = (255, 255, 255), 0.5
        lay = Image.new("RGBA", (int(wdt) + 40, 140), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((20, 70), tok, font=CF, fill=col + (int(255 * al * a),), anchor="lm")
        if active:
            pk = ease_out((t - w["s"] + 0.03) / 0.14)
            sc = 1.0 + 0.07 * (1 - abs(2 * pk - 1))
            if sc > 1.002: lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.LANCZOS)
        img.alpha_composite(lay, (int(x + wdt / 2 - lay.width / 2), int(cy - lay.height / 2)))
        x += wdt + sp
    return np.asarray(img).astype(np.float32) / 255

# ---------------------------------------------------------------- tip progress bar (top)
TIPS = [(2.30, 13.0), (13.0, 23.2), (23.2, DUR)]
def progress_layer(t):
    if t < 2.2: return None
    a = ease_out((t - 2.2) / 0.5)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    segw, gap, y = 92, 12, 112
    x0 = (W - (3 * segw + 2 * gap)) / 2
    for k, (s, e) in enumerate(TIPS):
        x = x0 + k * (segw + gap)
        d.rounded_rectangle([x, y, x + segw, y + 7], 4, fill=(20, 18, 17, int(55 * a)))
        f = clamp((t - s) / (e - s))
        if f > 0:
            d.rounded_rectangle([x, y, x + max(7, segw * f), y + 7], 4, fill=(20, 18, 17, int(200 * a)))
    return np.asarray(img).astype(np.float32) / 255

# ---------------------------------------------------------------- camera
SECTIONS = [(0.0, 2.25, 1.00, 1.04), (2.25, 13.0, 1.07, 1.02), (13.0, 23.2, 1.075, 1.03), (23.2, 30.0, 1.08, 1.045)]
def zoom(t):
    for k, (a, b, s0, s1) in enumerate(SECTIONS):
        if a <= t < b:
            v = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0:
                prev = SECTIONS[k - 1][3]; v = prev + (v - prev) * ease_out((t - a) / 0.55)
            return v
    return SECTIONS[-1][3]
def flash(t): return max([0.0] + [0.08 * max(0, 1 - abs(t - b) / 0.2) for b in (2.25, 13.0, 23.2)])

def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=10, eps=2e-3):
    mI, mp_ = box(I, r), box(p, r)
    a = (box(I * p, r) - mI * mp_) / (box(I * I, r) - mI * mI + eps); b = mp_ - a * mI
    return box(a, r) * I + box(b, r)

# card side from head position in matte
def head_x():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", MASK, "-vf", "scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    xs = []
    while True:
        b = p.stdout.read(270 * 480)
        if len(b) < 270 * 480: break
        m = np.frombuffer(b, np.uint8).reshape(480, 270)[100:190].astype(np.float32); cs = m.sum(0)
        xs.append((cs * np.arange(270)).sum() / max(cs.sum(), 1) * 4)
    return np.array(xs)
HX = head_x()
SIDES = ["left" if HX[int(t0 * FPS):int(t1 * FPS)].mean() > 560 else "right" for _, t0, t1 in CARDS]
print("sides", SIDES, flush=True)

dv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", MASK, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
if ONLY is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a",
                            "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={DUR-0.3}:d=0.3",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
for i in range(N):
    fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
    if len(fb) < W * H * 3 or len(mb) < W * H: break
    t = i / FPS
    if ONLY is not None and not any(abs(t - o) < 0.5 / FPS for o in ONLY): continue
    frame = np.frombuffer(fb, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    m = np.frombuffer(mb, np.uint8).reshape(H, W).astype(np.float32) / 255
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)
    m = np.clip(cv2.resize(guided(gs, ms), (W, H)), 0, 1)
    s = zoom(t)
    if s != 1.0:
        M = cv2.getRotationMatrix2D((540, 800), 0, s)
        frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        m = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    bgk = (1 - m)[..., None]
    comp = frame.copy()
    for hl, t0, t1 in HEADLINES:
        L = render_headline(hl, t, t0, t1)
        if L is not None:
            a = L[..., 3:4] * bgk; comp = comp * (1 - a) + L[..., :3] * a
    for (c, t0, t1), side in zip(CARDS, SIDES):
        r = card_layer(c, t, t0, t1, side)
        if r is not None:
            rgb, al = r; comp = comp * (1 - al[..., None] * bgk) + rgb * bgk
    fl = flash(t)
    if fl > 0: comp = comp * (1 - fl) + fl
    for layer in (progress_layer(t), caption_layer(t)):
        if layer is not None:
            a = layer[..., 3:4]; comp = comp * (1 - a) + layer[..., :3] * a
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if ONLY is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=90)
    else:
        enc.stdin.write(out.tobytes())
        if i % 90 == 0: print("frame", i, flush=True)
if ONLY is None: enc.stdin.close(); enc.wait()
print("done")
