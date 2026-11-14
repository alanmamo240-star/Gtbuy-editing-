"""Outfit-transition edit: natural enhancement, depth headlines behind the head, Higgsfield light leaks on
key cuts, beat-aware settle-zooms, subtle grain/vignette, synthesized SFX mixed under the music."""
import subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, N = 1080, 1920, 30, 405
DUR = N / FPS
SRC, MASK = "input_cfr.mov", "mask.mkv"
OUT = sys.argv[1] if len(sys.argv) > 1 else "out.mp4"
ONLY = [float(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
ENH = open("enhance.txt").read().strip()
SERIF, SERIF_I = "fonts/InstrumentSerif.ttf", "fonts/InstrumentSerif-Italic.ttf"
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
INK, ACC = (24, 21, 19), (168, 64, 38)
CUTS = [0.0, 1.6, 4.133, 5.733, 6.667, 8.5, 9.9, 11.267, 12.0, DUR]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
FC = {}
def font(p, s):
    k = (p, int(s)); FC.setdefault(k, ImageFont.truetype(p, int(s))); return FC[k]

# ---------------------------------------------------------------- headlines
def make_hl(lines, label, size, x0=None):
    """lines: [(parts, baseline)]; centred when x0 is None"""
    chars = []; i = 0
    for parts, base in lines:
        lw = sum(font(SERIF_I if it else SERIF, size).getlength(tx) for tx, it in parts)
        x = x0 if x0 is not None else (W - lw) / 2
        for tx, it in parts:
            f = font(SERIF_I if it else SERIF, size)
            for ch in tx:
                chars.append((ch, x, i, f, ACC if it else INK, base)); x += f.getlength(ch); i += 1
    return dict(chars=chars, label=label, size=size, baseline=lines[-1][1], x0=x0 if x0 is not None else W / 2)

def render_hl(h, t, t0, t_land, t1, label_at=None):
    if t < t0 or t > t1: return None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    out_k = eio((t1 - t) / 0.3)
    n = len(h["chars"]); span = t_land - t0
    for ch, x, i, f, col, base in h["chars"]:
        st = t0 + i * (span * 0.45 / max(n - 1, 1)); k = eo((t - st) / (span * 0.55))
        a = k * out_k
        if a > 0: d.text((x, base + (1 - k) * 60), ch, font=f, fill=col + (int(255 * a),), anchor="ls")
    if h["label"] and label_at is not None:
        lk = eo((t - label_at) / 0.35); la = lk * out_k
        if la > 0:
            lf = font(INTER.format("SemiBold"), 32); sp = 8; txt = h["label"]
            tw = sum(lf.getlength(c) + sp for c in txt) - sp
            lx = (W - tw) / 2; ly = h["baseline"] - h["size"] * 0.95 - 34 + (1 - lk) * 10
            rw = 44 * lk
            d.line([(lx - 20 - rw, ly + 19), (lx - 20, ly + 19)], fill=ACC + (int(255 * la),), width=3)
            d.line([(lx + tw + 20, ly + 19), (lx + tw + 20 + rw, ly + 19)], fill=ACC + (int(255 * la),), width=3)
            for c in txt: d.text((lx, ly), c, font=lf, fill=INK + (int(235 * la),)); lx += lf.getlength(c) + sp
    blur = max(1 - eo((t - t0) / (span * 0.9)), 1 - out_k) * 8
    if blur > 0.3: img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img).astype(np.float32) / 255
    s = 1.0 + 0.025 * clamp((t - t0) / (t1 - t0)) + 0.04 * (1 - out_k)     # parallax drift vs. camera
    M = cv2.getRotationMatrix2D((W / 2, h["baseline"] - h["size"] * 0.35), 0, s)
    return cv2.warpAffine(arr, M, (W, H))

H1 = make_hl([([("Fit ", True), ("Check", False)], 720)], None, 280)
H2 = make_hl([([("Welcher ", False), ("Fit?", True)], 300)], "SCHREIB'S IN DIE KOMMENTARE", 178)
HEADLINES = [(H1, 1.72, 2.32, 3.98, None), (H2, 12.03, 12.47, DUR, 12.76)]

# ---------------------------------------------------------------- light leaks (Higgsfield)
def load_leak(p):
    im = np.asarray(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    im = np.clip((im - np.percentile(im, 30, axis=(0, 1))) / 0.9, 0, 1)        # remove black floor
    return cv2.GaussianBlur(im, (0, 0), 6)
LEAKS = [load_leak("img/leak_a.png"), load_leak("img/leak_b.png")]
LEAK_AT = [(1.6, 0, 0.75), (5.733, 1, 0.6), (6.667, 0, 0.55), (12.0, 1, 0.8)]   # time, which, strength
def leak_layer(t):
    for c, k, s in LEAK_AT:
        dt = t - c
        if -0.28 < dt < 0.4:
            a = (eo((dt + 0.28) / 0.28) if dt < 0 else 1 - eio(dt / 0.4)) * s
            shift = int(dt * 500 * (1 if k == 0 else -1))
            return np.roll(LEAKS[k], shift, axis=1) * a
    return None

# ---------------------------------------------------------------- camera: settle-zoom on every cut + slow push
def seg(t):
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        if a <= t < b: return a, b
    return CUTS[-2], CUTS[-1]
def zoom(t):
    a, b = seg(t)
    return 1.0 + 0.028 * eio((t - a) / (b - a)) + 0.035 * (1 - eo((t - a) / 0.38))

# ---------------------------------------------------------------- finishing: vignette + grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r2 = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.47) / (H * 0.62)) ** 2
VIG = (1 - 0.16 * np.clip(r2, 0, 1.6) ** 1.3)[..., None]
rng = np.random.default_rng(3)

def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=10, eps=2e-3):
    mI, mp = box(I, r), box(p, r)
    a = (box(I * p, r) - mI * mp) / (box(I * I, r) - mI * mI + eps); b = mp - a * mI
    return box(a, r) * I + box(b, r)

dv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", ENH, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", MASK, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
if ONLY is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", SRC, "-i", "sfx.wav", "-filter_complex",
                            f"[1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[m];[2:a]volume=1.0[s];"
                            f"[m][s]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89,afade=t=out:st={DUR-0.35}:d=0.35[a]",
                            "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-profile:v", "high",
                            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                            "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", OUT], stdin=subprocess.PIPE)
for i in range(N):
    fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
    if len(fb) < W * H * 3 or len(mb) < W * H: break
    t = i / FPS
    if ONLY is not None and not any(abs(t - o) < 0.5 / FPS for o in ONLY): continue
    frame = np.frombuffer(fb, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    m = np.frombuffer(mb, np.uint8).reshape(H, W).astype(np.float32) / 255
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    m = np.clip(cv2.resize(guided(gs, cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    s = zoom(t)
    M = cv2.getRotationMatrix2D((540, 760), 0, s)
    frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    m = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    bgk = (1 - m)[..., None]
    comp = frame
    for h, t0, tl, t1, lab in HEADLINES:
        L = render_hl(h, t, t0, tl, t1, lab)
        if L is not None:
            a = L[..., 3:4] * bgk; comp = comp * (1 - a) + L[..., :3] * a
    lk = leak_layer(t)
    if lk is not None: comp = 1 - (1 - comp) * (1 - lk)                       # screen blend
    comp = comp * VIG
    comp = comp + rng.normal(0, 0.011, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.35: comp = comp * clamp((DUR - t) / 0.35)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if ONLY is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=92)
    else:
        enc.stdin.write(out.tobytes())
        if i % 90 == 0: print("frame", i, flush=True)
if ONLY is None: enc.stdin.close(); enc.wait()
print("done")
