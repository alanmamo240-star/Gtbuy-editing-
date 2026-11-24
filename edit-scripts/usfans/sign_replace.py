"""Replace the physical orange GTBUY sign(s) in v13 footage with a USFANS sign.
Per frame: orange segmentation -> minAreaRect quad per blob (EMA-smoothed) -> inpaint old lettering on the orange
surface (keeps lighting) -> perspective-warped 'USFANS' lettering; hands/fingers stay in front (only orange + white
lettering pixels are replaced). usage: python sign_replace.py in.mov out.mov [test_png ...]"""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
W, H = 1080, 1920
FONT = ImageFont.truetype("fonts/Archivo.ttf", 200); FONT.set_variation_by_axes([900, 112])
def text_tex(tw=1000, th=1000):
    im = Image.new("L", (tw, th), 0); d = ImageDraw.Draw(im)
    s = "USFANS"; L = FONT.getlength(s); bb = d.textbbox((0, 0), s, font=FONT)
    sc = 0.80 * tw / L; f = FONT.font_variant(size=int(200 * sc)); f.set_variation_by_axes([900, 112])
    bb = d.textbbox((0, 0), s, font=f)
    d.text(((tw - (bb[2] - bb[0])) / 2 - bb[0], th * 0.47 - (bb[3] - bb[1]) / 2 - bb[1]), s, font=f, fill=255)
    return np.asarray(im).astype(np.float32) / 255
TEX = text_tex()
def order(box):
    box = np.array(box, np.float32); s = box.sum(1); d = box[:, 0] - box[:, 1]
    return np.array([box[np.argmin(s)], box[np.argmax(d)], box[np.argmax(s)], box[np.argmin(d)]], np.float32)  # TL TR BR BL
tracks = []   # [centroid, quad]
def process(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    org = ((h <= 9) | (h >= 172)) & (s > 118) & (v > 80)
    org = cv2.morphologyEx(org.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(cv2.morphologyEx(org, cv2.MORPH_CLOSE, np.ones((35, 35), np.uint8)))
    lab = np.where(org > 0, lab, 0)
    out = img.copy(); new_tracks = []
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] < 2500: continue
        ys, xs = np.where(lab == k)
        if len(xs) < 2500: continue
        if cen[k][1] > 760 and np.median(s[ys, xs]) < 150: continue   # warm skin in close-ups, not a sign
        rect = cv2.minAreaRect(np.stack([xs, ys], 1).astype(np.float32))
        if min(rect[1]) < 40: continue
        q = order(cv2.boxPoints(rect)); c = cen[k]
        for tc, tq in tracks:   # temporal smoothing
            if np.linalg.norm(tc - c) < 40: q = 0.55 * tq + 0.45 * q; break
        new_tracks.append((c, q))
        x0, y0 = np.maximum(q.min(0).astype(int) - 12, 0); x1, y1 = np.minimum(q.max(0).astype(int) + 12, [W - 1, H - 1])
        crop = img[y0:y1, x0:x1]; ql = (q - [x0, y0]).astype(np.float32)
        hull = np.zeros(crop.shape[:2], np.uint8); cv2.fillConvexPoly(hull, ql.astype(np.int32), 1)
        hh = hsv[y0:y1, x0:x1].astype(int)
        o = (lab[y0:y1, x0:x1] == k)
        inside = np.zeros_like(hull); oy, ox = np.where(o)
        cv2.fillConvexPoly(inside, cv2.convexHull(np.stack([ox, oy], 1).astype(np.int32)), 1)
        inside = cv2.erode(inside, np.ones((9, 9), np.uint8))   # lettering lies inside the orange's hull
        wt = (hh[..., 1] < 110) & (hh[..., 2] > 150) & (hull > 0) & (inside > 0)
        wt = cv2.dilate(wt.astype(np.uint8), np.ones((5, 5), np.uint8)) & hull & inside
        sign = ((o | (wt > 0)) & (hull > 0)).astype(np.uint8)
        # orange surface without lettering (lighting kept)
        sm = 0.5
        small = cv2.resize(crop, None, fx=sm, fy=sm, interpolation=cv2.INTER_AREA)
        msk = cv2.resize(wt * 255, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
        surf = cv2.resize(cv2.inpaint(small, msk, 5, cv2.INPAINT_TELEA), (crop.shape[1], crop.shape[0]), interpolation=cv2.INTER_LINEAR)
        surf = np.where(o[..., None], crop, surf).astype(np.float32)
        # new lettering, colour = old lettering brightness
        wpix = crop[wt > 0]; tc = np.median(wpix, 0) if len(wpix) > 50 else np.array([235, 235, 235])
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [999, 0], [999, 999], [0, 999]]), ql)
        ta = cv2.warpPerspective(TEX, M, (crop.shape[1], crop.shape[0]), flags=cv2.INTER_LINEAR)
        comp = surf * (1 - ta[..., None]) + tc * ta[..., None]
        a = cv2.GaussianBlur(sign.astype(np.float32), (0, 0), 1.0)[..., None]
        out[y0:y1, x0:x1] = (crop * (1 - a) + comp * a).clip(0, 255).astype(np.uint8)
    tracks[:] = new_tracks
    return out
if __name__ == "__main__":
    if len(sys.argv) > 3:
        for p in sys.argv[3:]:
            im = np.asarray(Image.open(p).convert("RGB")); tracks.clear()
            Image.fromarray(process(im)).save(p.replace(".png", "_us.jpg"), quality=90)
        sys.exit()
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-c:v", "libx264", "-crf", "8", "-preset", "medium", "-pix_fmt", "yuv420p", sys.argv[2]], stdin=subprocess.PIPE)
    i = 0
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        enc.stdin.write(process(np.frombuffer(b, np.uint8).reshape(H, W, 3)).tobytes()); i += 1
    enc.stdin.close(); enc.wait(); print("done", i)
