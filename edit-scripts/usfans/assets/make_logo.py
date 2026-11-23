import numpy as np, cv2
from PIL import Image
im = np.asarray(Image.open("/root/.claude/uploads/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/07366bb3-image.jpg").convert("RGB")).astype(np.float32)
wh = (im.min(2) > 225).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(wh)
k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); x, y, w, h = st[k, :4]
print("icon box", x, y, w, h)
# wordmark region inside icon
sub = im[y:y + h, x:x + w]
F = 12
big = cv2.resize(sub, (w * F, h * F), interpolation=cv2.INTER_CUBIC)
r, g, b = big[..., 0], big[..., 1], big[..., 2]
lum = big.mean(2)
ink = np.clip((235 - lum) / 120, 0, 1)
sh, sw_ = sub.shape[:2]; inner = np.zeros((sh * F, sw_ * F), np.float32)
inner[int(sh * F * .3):int(sh * F * .7), int(sw_ * F * .06):int(sw_ * F * .94)] = 1
ink *= inner
orange = np.clip(((r - b) - 60) / 60, 0, 1) * (ink > 0.05)     # orange vs navy
def crisp(m):
    m = cv2.GaussianBlur(m.astype(np.float32), (0, 0), F * 0.6)
    return np.clip((m - 0.5) * 6 + 0.5, 0, 1)
inkc = crisp(ink); orc = crisp(orange) * inkc
nav = np.clip(inkc - orc, 0, 1)
ORANGE = np.array([255, 79, 18], np.float32); NAVY = np.array([24, 27, 44], np.float32)
ys, xs = np.where(inkc > 0.5); print("word bbox", xs.min(), xs.max(), ys.min(), ys.max())
wx0, wx1, wy0, wy1 = xs.min(), xs.max(), ys.min(), ys.max()
word_rgb = np.ones_like(big) * 255
word_rgb = word_rgb * (1 - orc[..., None]) + ORANGE * orc[..., None]
word_rgb = word_rgb * (1 - nav[..., None]) + NAVY * nav[..., None]
crop = word_rgb[wy0:wy1 + 1, wx0:wx1 + 1]; ca = inkc[wy0:wy1 + 1, wx0:wx1 + 1]
# compose 1024 icon: white rounded square, wordmark 72% width
N = 1024; out = np.zeros((N, N, 4), np.float32)
m = np.zeros((N * 4, N * 4), np.uint8); R = int(N * 4 * 0.225)
cv2.rectangle(m, (R, 0), (N * 4 - R, N * 4), 255, -1); cv2.rectangle(m, (0, R), (N * 4, N * 4 - R), 255, -1)
for cx, cy in ((R, R), (N * 4 - R, R), (R, N * 4 - R), (N * 4 - R, N * 4 - R)): cv2.circle(m, (cx, cy), R, 255, -1, cv2.LINE_AA)
al = cv2.resize(m, (N, N), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
out[..., :3] = 255; out[..., 3] = al * 255
tw = int(N * 0.74); th = int(crop.shape[0] * tw / crop.shape[1])
cr = cv2.resize(crop, (tw, th), interpolation=cv2.INTER_AREA); caa = cv2.resize(ca, (tw, th), interpolation=cv2.INTER_AREA)
ox, oy = (N - tw) // 2, (N - th) // 2
reg = out[oy:oy + th, ox:ox + tw, :3]; out[oy:oy + th, ox:ox + tw, :3] = reg * (1 - caa[..., None]) + cr * caa[..., None]
Image.fromarray(out.clip(0, 255).astype(np.uint8)).save("brand_logo.png")
# preview on dark bg
bg = np.zeros((N, N, 3), np.float32) + [40, 60, 90]; a = out[..., 3:] / 255
Image.fromarray((bg * (1 - a) + out[..., :3] * a).astype(np.uint8)).resize((512, 512)).save("preview.png")
