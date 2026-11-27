"""Swap the 'BESTELLT ÜBER GTBUY' label in the finished v3 fit-check for 'BESTELLT ÜBER USFANS'.
The original label layer is re-drawn with render3's own maths to get its exact alpha, those pixels are inpainted, then the
new label is drawn with identical timing, spacing, fade, blur and parallax."""
import subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
SRC, OUT = sys.argv[1], sys.argv[2]
INK, ACC = (24, 21, 19), (168, 64, 38)
F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 32)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
BASE, SIZE, T0, TL, T1, LAB = 720, 280, 1.72, 2.32, 4.06, 2.35
def label(t, txt):
    if t < T0 or t > T1: return None
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    out_k = eio((T1 - t) / 0.35); span = TL - T0
    lk = eo((t - LAB) / 0.4); la = lk * out_k
    if la <= 0: return None
    sp = 8; tw = sum(F.getlength(c) + sp for c in txt) - sp
    lx = (W - tw) / 2; ly = BASE - SIZE * 0.95 - 34 + (1 - lk) * 10; rw = 44 * lk
    d.line([(lx - 20 - rw, ly + 19), (lx - 20, ly + 19)], fill=ACC + (int(255 * la),), width=3)
    d.line([(lx + tw + 20, ly + 19), (lx + tw + 20 + rw, ly + 19)], fill=ACC + (int(255 * la),), width=3)
    for c in txt: d.text((lx, ly), c, font=F, fill=INK + (int(235 * la),)); lx += F.getlength(c) + sp
    blur = max(1 - eo((t - T0) / (span * 0.9)), 1 - out_k) * 8
    if blur > 0.3: img = img.filter(ImageFilter.GaussianBlur(blur))
    arr = np.asarray(img).astype(np.float32) / 255
    s = 1.0 + 0.025 * clamp((t - T0) / (T1 - T0)) + 0.04 * (1 - out_k)
    return cv2.warpAffine(arr, cv2.getRotationMatrix2D((W / 2, BASE - SIZE * 0.35), 0, s), (W, H))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "copy", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
i = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = i / FPS; f = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    old = label(t, "BESTELLT ÜBER GTBUY")
    if old is not None:
        m = (cv2.dilate((old[..., 3] > 0.03).astype(np.uint8), np.ones((5, 5), np.uint8)) * 255)
        f = cv2.inpaint(f, m, 6, cv2.INPAINT_TELEA)
        new = label(t, "BESTELLT ÜBER USFANS")
        a = new[..., 3:4]; f = (f.astype(np.float32) * (1 - a) + new[..., :3] * 255 * a).clip(0, 255).astype(np.uint8)
    enc.stdin.write(f.tobytes()); i += 1
enc.stdin.close(); enc.wait(); print("frames", i)
