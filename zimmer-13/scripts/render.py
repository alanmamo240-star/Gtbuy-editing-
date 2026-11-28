"""usage: render.py preview t1,t2,...  |  render.py chunk K NC"""
import sys, subprocess, numpy as np
from story import *
FPS = 30

def frame(t):
    fi = int(round(t * FPS))
    if t >= END_BLACK:
        img = np.zeros((H, W, 3), np.uint8)
        if t >= CARD:
            a = clamp((t - CARD) / 0.6); pulse = 1.0 + 0.04 * math.sin((t - CARD) * 2 * math.pi * 1.1) ** 8
            text(img, "Teil 2?", 540, 900, int(140 * pulse), (236, 228, 214), a)
            text(img, "DAS MÄDCHEN AUS ZIMMER 13", 540, 1060, 40, (190, 50, 50), a * 0.9)
            text(img, "Folge Mia, wenn du wissen willst, was hinter der Tür ist.", 540, 1150, 28, (160, 160, 170), clamp((t - CARD - 1.0) / 0.6), bold=False)
        return post(img, fi, grain=6, lift=(0, 0, 0))
    a, b, fn = next(s for s in SHOTS if s[0] <= t < s[1])
    img, o = fn(t)
    img = post(img, fi, grain=o.get("grain", 7), ca=o.get("ca", 0), grade=o.get("grade", (0.96, 0.98, 1.06)))
    # hook overlays
    if t < 3.2:
        al = min(clamp(t / 0.25), clamp((3.2 - t) / 0.5)); glitch = int(t * 20) % 7 == 0
        text(img, "03:17", 540 + (6 if glitch else 0), 360, 150, (235, 50, 50), al, stroke=4, sc=(30, 0, 0))
    if 0.3 < t < 9.0:
        al = min(clamp((t - 0.3) / 0.5), clamp((9.0 - t) / 0.5))
        text(img, "DAS MÄDCHEN AUS ZIMMER 13", 540, 150, 40, (240, 234, 220), al, stroke=3)
        text(img, "FOLGE 1 · ÖFFNE NIEMALS ZIMMER 13", 540, 205, 28, (220, 70, 64), al, stroke=3)
    c = caption(t)
    if c:
        y = 1700 if a == 42.6 else 1520
        text(img, c[0], 540, y + (1 - eout(c[2])) * 14, 74, c[1], clamp(c[2] * 1.5), stroke=7, sc=(10, 8, 12))
    # cut fades / dips
    if t < 0.4: img = (img * clamp(t / 0.4)).astype(np.uint8)
    if END_BLACK - 0.08 < t < END_BLACK: img[:] = 0
    return img

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        for t in [float(x) for x in sys.argv[2].split(",")]: Image.fromarray(frame(t)).save(f"test/f_{t:06.2f}.jpg", quality=88)
    else:
        K, NC = int(sys.argv[2]), int(sys.argv[3]); N = int(round(DUR * FPS)); a, b = K * N // NC, (K + 1) * N // NC
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", f"build/chunk_{K}.mp4"], stdin=subprocess.PIPE)
        for i in range(a, b):
            enc.stdin.write(frame(i / FPS).tobytes())
            if (i - a) % 150 == 0: print(f"chunk {K}: {i - a}/{b - a}", flush=True)
        enc.stdin.close(); enc.wait(); print(f"chunk {K} done")
