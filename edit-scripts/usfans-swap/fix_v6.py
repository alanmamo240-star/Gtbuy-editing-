"""Swap 'via GTBuy' (gold pill on the tracked Gallery Dept tag) and 'VIA GTBUY' (recap card row) in the finished v6
outfit video for USFans. The tag is tracked, so both elements are found per frame by their gold colour, then the old
glyphs are inpainted and the new text is drawn in the same fonts at the same place and opacity."""
import subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
SRC, OUT = sys.argv[1], sys.argv[2]
GOLD, INK = np.array([255, 200, 80], np.float32), (16, 16, 18)
def gfont(sz):
    f = ImageFont.truetype("/home/user/Gtbuy-editing-/../../tmp/_nofont", sz) if False else ImageFont.truetype(FONT, sz)
    f.set_variation_by_axes([700]); return f
FONT = sys.argv[3]
def gold_mask(f):
    r, g, b = [f[..., k].astype(np.int16) for k in range(3)]
    return ((r > 140) & (r - b > 85) & (g > 90) & (g < r - 15) & (b < 140)).astype(np.uint8)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", SRC,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "copy", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
i = 0; log = []
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = i / FPS; f = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    if 3.6 <= t <= 7.6 or 13.85 <= t <= 14.75:
        gm = gold_mask(f)
        n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(gm, np.ones((7, 21), np.uint8)))
        for k in range(1, n):
            x, y, w, h, _ = st[k]
            core = gm[y:y + h, x:x + w]; fill = core.mean() if core.size else 0
            strip = f[y + 6:y + h - 6, max(0, x - 8):x + 6]
            dark_above = strip.size > 0 and float(np.median(strip)) < 80                       # dark tag body right left of the pill
            if 4.0 <= t <= 7.0 and 145 <= w <= 200 and 26 <= h <= 46 and fill > 0.45 and dark_above:  # gold pill "via GTBuy"
                px0, py0, px1, py1 = x + 10, y + 3, x + w - 10, y + h - 3                         # undo dilation
                pts = f[py0:py1, px0:px1].astype(np.float32); gpx = pts[core[3:h - 3, 10:w - 10] > 0]
                a = float(np.clip(np.median(gpx[:, 0] - gpx[:, 2]) / 175.0, 0, 1)) if len(gpx) else 0
                if a < 0.08: continue
                ph = py1 - py0; reg = f[py0 - 2:py1 + 2, px0 - 2:px1 + 2].astype(np.float32)
                under = np.full_like(reg, 14.0)                                                    # dark tag body under the pill
                pill = Image.new("RGBA", (px1 - px0 + 4, ph + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(pill)
                d.rounded_rectangle([2, 2, px1 - px0 + 1, ph + 1], ph // 2, fill=(255, 200, 80, 255))
                fz = 24; fnt = gfont(fz)
                while fnt.getlength("via USFans") > (px1 - px0) - 14 and fz > 12: fz -= 1; fnt = gfont(fz)
                d.text(((px1 - px0 + 4) / 2, (ph + 4) / 2), "via USFans", font=fnt, fill=INK + (255,), anchor="mm")
                P = np.asarray(pill).astype(np.float32); pa = P[..., 3:4] / 255 * a
                base = reg * (1 - (P[..., 3:4] / 255)) + under * (P[..., 3:4] / 255) * 0 + reg * 0   # keep outside-rounded corners
                inside = (P[..., 3:4] / 255)
                bg = reg * (1 - inside) + (reg * (1 - a) + 0) * 0 + under * inside * 0
                # remove old pill: where old gold was, reconstruct as dark tag (blend by measured alpha)
                oldm = cv2.dilate(core[3 - 2:h - 1, 10 - 2:w - 8] if False else gold_mask(f[py0 - 2:py1 + 2, px0 - 2:px1 + 2]), np.ones((3, 3), np.uint8))[..., None].astype(np.float32)
                clean = reg * (1 - oldm) + (reg - GOLD * a) / max(1 - a, 0.25) * oldm * 0 + under * oldm
                clean = clean * (1 - inside) + under * inside
                newreg = clean * (1 - pa) + P[..., :3] * pa + clean * 0
                f[py0 - 2:py1 + 2, px0 - 2:px1 + 2] = np.clip(newreg, 0, 255).astype(np.uint8)
                log.append(("pill", round(t, 2), w, h, round(a, 2)))
            elif 13.85 <= t <= 14.75 and 40 <= w <= 160 and 14 <= h <= 34 and fill < 0.6 and x > 500:  # "VIA GTBUY" row text
                x0, y0, x1, y1 = x + 10, y + 3, x + w - 10, y + h - 3
                sub = f[y0 - 3:y1 + 3, x0 - 3:x1 + 3]; sm = cv2.dilate(gold_mask(sub), np.ones((3, 3), np.uint8))
                gpx = sub[sm > 0].astype(np.float32)
                a = float(np.clip(np.median(gpx[:, 0] - gpx[:, 2]) / 175.0, 0, 1)) if len(gpx) else 0
                f[y0 - 3:y1 + 3, x0 - 3:x1 + 3] = cv2.inpaint(np.ascontiguousarray(sub), sm * 255, 4, cv2.INPAINT_TELEA)
                if a < 0.08: continue
                fnt = gfont(18); txt = "VIA USFANS"
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x1, (y0 + y1) / 2), txt, font=fnt, fill=(255, 200, 80, 255), anchor="rm")
                L = np.asarray(lay).astype(np.float32); la = L[..., 3:4] / 255 * a
                yy0, yy1 = max(0, y0 - 30), y1 + 30
                f[yy0:yy1] = np.clip(f[yy0:yy1] * (1 - la[yy0:yy1]) + L[yy0:yy1, :, :3] * la[yy0:yy1], 0, 255).astype(np.uint8)
                log.append(("row", round(t, 2), w, h, round(a, 2)))
    enc.stdin.write(f.tobytes()); i += 1
enc.stdin.close(); enc.wait(); print("frames", i)
import collections
c = collections.Counter(l[0] for l in log); print(c)
for l in log[:3] + log[-3:]: print(l)
