"""Cut accents for v5: white flash + zoom punch + short camera shake on every cut (post pass over the rendered segments)."""
import subprocess, numpy as np, cv2, math
W, H, FPS = 1080, 1920, 30
CUTS = [(0.0, 0.9), (2.82, 0.8), (13.30, 0.6), (15.70, 0.8), (22.0, 0.8), (33.4, 0.35)]  # (time, strength)
rng = np.random.default_rng(3)
SHAKE = {c: rng.normal(0, 1, (8, 2)) for c, _ in CUTS}

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "seg_0.mkv", "-i", "seg_273.mkv", "-i", "seg_546.mkv", "-i", "seg_819.mkv",
                        "-filter_complex", "[0:v][1:v][2:v][3:v]concat=n=4:v=1:a=0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "ffv1", "-level", "3", "post.mkv"], stdin=subprocess.PIPE)
j = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = j / FPS
    act = [(c, k) for c, k in CUTS if 0 <= t - c < 0.30]
    if not act:
        enc.stdin.write(b); j += 1; continue
    img = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    c, k = act[0]; d = t - c; n = int(round(d * FPS))
    # zoom punch 1.06 -> 1.0 and decaying shake
    s = 1 + 0.06 * k * math.exp(-d / 0.08)
    sh = SHAKE[c][min(n, 7)] * 14 * k * math.exp(-d / 0.07)
    M = cv2.getRotationMatrix2D((W / 2, H * 0.45), 0, s); M[:, 2] += sh
    img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # flash: bright exposure bloom (not a flat white card) + white lift, decays over ~5 frames
    fl = 0.9 * k * math.exp(-d / 0.055)
    if fl > 0.01:
        bloom = cv2.GaussianBlur(img, (0, 0), 25)
        img = 1 - (1 - img) * (1 - bloom * fl * 0.8)          # screen-blend bloom
        img = img * (1 - fl * 0.75) + np.array([1.0, 0.98, 0.95], np.float32) * fl * 0.75
    enc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()); j += 1
enc.stdin.close(); enc.wait(); print("frames", j)
