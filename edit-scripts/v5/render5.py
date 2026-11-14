"""v5 'cinematic creator' edit of the GTBuy haul explainer.
usage: python3 render5.py chunk K N      -> renders output frames of chunk K of N to chunk_K.mp4
       python3 render5.py preview t1,t2   -> saves preview frames (output times) to frames/p_*.jpg"""
import json, subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import typo as T
from tl import FRAMES, SEG_OF, N_MAIN, N_OUT, DUR, DUR_MAIN, CUTS_OUT, s2o, FPS

W, H = 1080, 1920
ENH = "hqdn3d=1.2:1.0:3:3,cas=0.38:planes=1,eq=contrast=1.04:saturation=1.05:gamma=0.99"
INK, RED, GOLD, GREEN, WHITE = (18, 17, 20), (214, 48, 40), (255, 196, 64), (46, 204, 113), (255, 255, 255)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def ei(x): x = clamp(x); return x ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def env(t, t0, t1, fin=0.35, fout=0.3): return 0.0 if (t < t0 or t > t1) else min(eo((t - t0) / fin), eio((t1 - t) / fout))
def over_full(base, L, m=None):
    a = L[..., 3:4] if m is None else L[..., 3:4] * m
    return base * (1 - a) + L[..., :3] * a

# ---------------------------------------------------------------- head track (smoothed) in source frames
HD = np.load("head.npy")
def _med(x, k):
    p = np.pad(x, k // 2, mode="edge"); return np.median(np.lib.stride_tricks.sliding_window_view(p, k), 1)
def _avg(x, k):
    p = np.pad(x, k // 2, mode="edge"); return np.convolve(p, np.ones(k) / k, "valid")
for j in range(3): HD[:, j] = _avg(_med(HD[:, j], 15), 9)
def head(fsrc):
    top, cx, wd = HD[min(fsrc, len(HD) - 1)]; return float(top), float(cx), float(wd)

# ---------------------------------------------------------------- camera: zoom keyframes (source time) + face-follow
ZK = [(0.92, 1.06), (5.24, 1.06), (7.13, 1.00), (12.44, 1.08), (16.47, 1.08), (17.2, 1.00), (21.3, 1.10), (26.5, 1.10),
      (28.7, 1.0), (36.5, 1.09), (40.3, 1.02), (44.1, 1.06), (46.9, 1.15), (49.66, 1.05), (55.44, 1.11), (59.76, 1.0),
      (65.74, 1.07), (69.18, 1.0), (72.9, 1.0), (73.2, 1.06), (76.8, 1.0), (80.42, 1.09), (86.6, 1.02), (90.2, 1.14), (92.1, 1.17)]
def zoom_src(ts):
    for (a, za), (b, zb) in zip(ZK[:-1], ZK[1:]):
        if a <= ts < b:
            k = eio((ts - a) / 0.45) if zb != za else 0       # quick, smooth push between keyframes
            return za + (zb - za) * k if (b - a) > 0.45 else zb
    return ZK[-1][1]
def zoom_eff(ts):  # smooth step: value of current keyframe blended from previous keyframe
    prev = ZK[0][1]
    for (a, za) in ZK:
        if ts < a: break
        prev_a, prev = a, za
    # find previous value before prev_a
    i = [a for a, _ in ZK].index(prev_a); z0 = ZK[i - 1][1] if i > 0 else prev
    return z0 + (prev - z0) * eio((ts - prev_a) / 0.5) + 0.012 * eio((ts - prev_a) / 6.0)

def camera_matrix(fsrc, s, extra_dx=0.0, extra_dy=0.0):
    top, cx, wd = head(fsrc); fy = top + 170
    tx = cx + (540 - cx) * clamp((s - 1) / 0.15) * 0.35   # gentle reframe toward centre when punched in
    M = cv2.getRotationMatrix2D((cx, fy), 0, s); M[0, 2] += tx - cx;
    # keep frame covered
    lo_x, hi_x = (W - cx) * (1 - s) , cx * (s - 1)
    M[0, 2] = np.clip(M[0, 2], -(s - 1) * W, 0) if s >= 1 else M[0, 2]
    M[1, 2] = np.clip(M[1, 2], -(s - 1) * H, 0) if s >= 1 else M[1, 2]
    M[0, 2] += extra_dx; M[1, 2] += extra_dy
    return M

# ---------------------------------------------------------------- sprites (built once)
def spr_chrome3d(text, fname, size, depth=20, tracking=0.02):
    m = T.text_mask(text, fname, size, tracking); return T.shadow(T.extrude(T.chrome(m), depth, 0.5, 1.0, (28, 28, 34)), 20, 0, 22, 0.42)
SP = {}
SP["gtbuy"] = spr_chrome3d("GTBUY", "unb", 205)
SP["haul"] = T.outline(T.text_mask("HAUL", "anton", 190, 0.10), 5, INK)
SP["hook_label"] = T.solid(T.text_mask("WAS PASSIERT WIRKLICH?", "grotesk", 40, 0.16), INK)
SP["c3"] = T.solid(T.text_mask("3 COUPONS", "anton", 150, 0.02), (95, 95, 102))
SP["c4"] = T.shadow(T.glow(T.gradient(T.text_mask("4 COUPONS", "anton", 190, 0.0), (255, 222, 110), (255, 132, 40), pad=10), (255, 170, 60), 26, 0.75), 16, 0, 16, 0.35)
m = T.text_mask("AGENT", "unb", 200, 0.04); SP["agent_out"] = T.outline(m, 5, INK); SP["agent_fill"] = T.gradient(m, (30, 30, 36), (8, 8, 10), pad=8)
SP["agent_eyebrow"] = T.solid(T.text_mask("DEIN AGENT BESTELLT", "grotesk", 40, 0.18), INK)
SP["tage35"] = spr_chrome3d("3–5 TAGE", "unb", 128, 16)
m = T.text_mask("VOLUMEN", "arx", 98, 0.0); SP["vol"] = T.shadow(T.solid(m, INK), 10, 0, 10, 0.25)
m = T.text_mask("GEWICHT", "arx", 98, 0.0); SP["gew"] = T.shadow(T.outline(m, 4, INK), 1, 0, 0, 0.0)
SP["geschaetzt"] = T.solid(T.text_mask("geschätzt", "serifi", 130, 0.0), RED)
SP["hohe"] = T.shadow(T.gradient(T.text_mask("HOHE PREISE", "arxi", 100, 0.0), (255, 90, 70), (168, 18, 30), pad=8), 12, 0, 12, 0.4)
m = T.text_mask("REHEARSAL", "arx", 112, 0.0); SP["reh"] = T.solid(m, INK); SP["reh_o"] = T.outline(m, 3, INK)
SP["paketsim"] = T.solid(T.text_mask("Paketsimulation", "serifi", 128, 0.0), RED)
SP["n812"] = T.shadow(T.gradient(T.text_mask("8–12", "orb", 250, 0.04), (52, 52, 62), (8, 8, 12), pad=8), 16, 0, 18, 0.35)
SP["tage"] = T.solid(T.text_mask("TAGE", "grotesk", 54, 0.5), INK)
SP["final8"] = spr_chrome3d("≈ 8 TAGE", "unb", 160, 20)
SP["warehouse_t"] = T.shadow(T.solid(T.text_mask("WAREHOUSE", "unb", 112, 0.06), WHITE), 18, 0, 10, 0.55)
SP["warehouse_s"] = T.shadow(T.solid(T.text_mask("ANKUNFT NACH 3–5 TAGEN", "grotesk", 38, 0.2), WHITE), 10, 0, 6, 0.6)
SP["plane_t"] = T.shadow(T.solid(T.text_mask("ABGESCHICKT", "arxi", 92, 0.0), WHITE), 18, 0, 10, 0.6)
SP["plane_s"] = T.shadow(T.solid(T.text_mask("AUF DEM WEG ZU DIR", "grotesk", 38, 0.24), WHITE), 10, 0, 6, 0.6)
SP["qc_t"] = T.shadow(T.solid(T.text_mask("QC-BILDER", "unb", 84, 0.04), WHITE), 14, 0, 8, 0.6)
SP["qc_s"] = T.shadow(T.solid(T.text_mask("QUALITÄTSKONTROLLE", "grotesk", 32, 0.22), WHITE), 8, 0, 5, 0.6)

def img_cover(path, w, h, over=1.14):
    im = Image.open(path).convert("RGB"); bw, bh = int(w * over), int(h * over)
    s = max(bw / im.width, bh / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    l, t = (im.width - bw) // 2, (im.height - bh) // 2
    return np.asarray(im.crop((l, t, l + bw, t + bh))).astype(np.float32) / 255
IM = dict(warehouse=img_cover("img/warehouse.png", W, H, 1.12), plane=img_cover("img/plane.png", W, H, 1.12),
          qc=img_cover("img/qc.png", W, 960, 1.12), packing=img_cover("img/packing.png", 420, 540),
          scale=img_cover("img/scale_clean.png", 420, 540), door=img_cover("img/door.png", 420, 540),
          warehouse_card=img_cover("img/warehouse.png", 420, 540))

def kenburns(big, w, h, p, z0=1.12, z1=1.0, dy=0.0):
    z = z0 + (z1 - z0) * eio(p); bh, bw = big.shape[:2]
    M = np.float32([[z, 0, (bw - w * z) / 2], [0, z, (bh - h * z) / 2 + dy * p]])
    return cv2.warpAffine(big, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)

def rrect_mask(w, h, r):
    m = Image.new("L", (max(w, 1), max(h, 1)), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return np.asarray(m).astype(np.float32) / 255

def card_rgba(tile, label, r=30, label_pos="top"):
    h, w = tile.shape[:2]; g = np.linspace(1, 0, h)[:, None] if label_pos == "top" else np.linspace(0, 1, h)[:, None]
    tile = tile * (1 - (g ** 2.4 * 0.55))[..., None]
    rgba = np.dstack([tile, rrect_mask(w, h, r)])
    im = Image.fromarray((rgba * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, outline=(255, 255, 255, 80), width=2)
    if label: d.text((w / 2, 42 if label_pos == "top" else h - 42), label, font=T.font("grotesk", 30), fill=(255, 255, 255, 245), anchor="mm")
    return np.asarray(im).astype(np.float32) / 255

def panel(w, h, r=30, alpha=0.82):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=(14, 14, 18, int(255 * alpha)), outline=(255, 255, 255, 40), width=2)
    return im

# ---------------------------------------------------------------- screenshot UI cards
def prep_shot(path, box, w):
    im = Image.open(path).convert("RGB").crop(box); sc = w / im.width
    return dict(im=im.resize((w, round(im.height * sc)), Image.LANCZOS).convert("RGBA"), sc=sc)
PROF = prep_shot("img/shot_profile.png", (0, 300, 1179, 1003), 640)
BEAC = prep_shot("img/shot_beacons.png", (50, 1262, 1130, 1875), 600)
LINK_BOX = [v * PROF["sc"] for v in (34, 620, 616, 696)]
UI = [(PROF, 7.55, 8.95, 70, 7.86, 8.30, ((LINK_BOX[0] + LINK_BOX[2]) / 2, (LINK_BOX[1] + LINK_BOX[3]) / 2), True),
      (BEAC, 17.65, 19.45, 250, None, 18.60, (540 * BEAC["sc"], 300 * BEAC["sc"]), False)]
def ui_layer(ts, canvas):
    for card, t0, t1, top, hl_at, tap_at, tp, light in UI:
        if not (t0 <= ts <= t1): continue
        kin = back((ts - t0) / 0.42, 1.3); kout = eio((t1 - ts) / 0.28); a = clamp(eo((ts - t0) / 0.25)) * kout
        c = card["im"].copy(); ov = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        if hl_at is not None and ts > hl_at:
            p = eo((ts - hl_at) / 0.32); x0, y0, x1, y1 = LINK_BOX
            d.rounded_rectangle([x0, y0, x1, y1], 10, fill=RED + (int(34 * p),))
            per = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
            seg = [np.hypot(per[i + 1][0] - per[i][0], per[i + 1][1] - per[i][1]) for i in range(4)]; L = sum(seg) * p; pts = [per[0]]
            for i, sl in enumerate(seg):
                if L <= 0: break
                f = min(1, L / sl); pts.append((per[i][0] + (per[i + 1][0] - per[i][0]) * f, per[i][1] + (per[i + 1][1] - per[i][1]) * f)); L -= sl
            if len(pts) > 1: d.line(pts, fill=RED + (255,), width=4, joint="curve")
        press = 1.0
        if ts > tap_at - 0.05:
            q = clamp((ts - tap_at) / 0.45); r = 14 + 60 * eo(q); rc = (30, 30, 30) if light else (255, 255, 255)
            d.ellipse([tp[0] - r, tp[1] - r, tp[0] + r, tp[1] + r], outline=rc + (int(230 * (1 - q)),), width=4)
            r2 = 18 * (1 - q * 0.6); d.ellipse([tp[0] - r2, tp[1] - r2, tp[0] + r2, tp[1] + r2], fill=rc + (int(120 * (1 - q)),))
            press = 1 - 0.025 * np.sin(np.pi * clamp((ts - tap_at) / 0.22))
        c = Image.alpha_composite(c, ov)
        s = (0.9 + 0.1 * kin) * press * (1 - 0.04 * (1 - kout)); cw, ch = c.size; tw, th = int(cw * s), int(ch * s)
        c = c.resize((tw, th), Image.LANCZOS); mk = rrect_mask(tw, th, 28)
        c.putalpha(Image.fromarray((mk * 255 * a).astype(np.uint8)))
        X = int(W / 2 - tw / 2); Y = int(top + ch / 2 - th / 2 + (1 - clamp(kin)) * 36 - (1 - kout) * 30)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([X + 10, Y + 22, X + tw - 10, Y + th + 22], 28, fill=(0, 0, 0, int(110 * a)))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22))); canvas.alpha_composite(c, (X, Y))

# ---------------------------------------------------------------- tracking bar (stepper)
STEPS = [("ACCOUNT", 17.25), ("WAREHOUSE", 21.3), ("QC", 28.7), ("PACKEN", 36.5), ("SIMULATION", 44.1), ("VERSAND", 59.76)]
def stepper(ts, canvas):
    t0, t1 = 17.25, 65.75
    if not (t0 <= ts <= t1): return
    a = env(ts, t0, t1, 0.4, 0.4); slide = (1 - eo((ts - t0) / 0.45)) * -60
    x0, y0, w, h = 50, 64 + slide, 980, 128
    p = panel(w, h, 34, 0.80 * a); canvas.alpha_composite(p, (x0, int(y0)))
    d = ImageDraw.Draw(canvas)
    active = max(i for i, (_, st) in enumerate(STEPS) if ts >= st or i == 0)
    done_all = ts >= 65.0
    xs = [x0 + 85 + i * (w - 170) / 5 for i in range(6)]; yc = y0 + 48
    d.line([(xs[0], yc), (xs[-1], yc)], fill=(255, 255, 255, int(60 * a)), width=4)
    # progress line animates to the active node
    st_a = STEPS[active][1]; prog = xs[max(active - 1, 0)] + (xs[active] - xs[max(active - 1, 0)]) * eo((ts - st_a) / 0.5)
    if done_all: prog = xs[-1]
    d.line([(xs[0], yc), (prog, yc)], fill=GOLD + (int(255 * a),), width=5)
    for i, (lab, st) in enumerate(STEPS):
        done = i < active or done_all; act = i == active and not done_all
        r = 15 if not act else 15 + 5 * back((ts - st) / 0.4)
        if done:
            d.ellipse([xs[i] - r, yc - r, xs[i] + r, yc + r], fill=GOLD + (int(255 * a),))
            d.text((xs[i], yc + 1), "✓", font=T.font("inter", 20), fill=INK + (int(255 * a),), anchor="mm")
        elif act:
            pulse = 0.5 + 0.5 * np.sin((ts - st) * 6)
            rr = r + 8 + 4 * pulse; d.ellipse([xs[i] - rr, yc - rr, xs[i] + rr, yc + rr], fill=GOLD + (int(60 * a),))
            d.ellipse([xs[i] - r, yc - r, xs[i] + r, yc + r], fill=GOLD + (int(255 * a),))
        else:
            d.ellipse([xs[i] - 11, yc - 11, xs[i] + 11, yc + 11], outline=(255, 255, 255, int(110 * a)), width=3)
        col = (255, 255, 255, int((255 if act else 150 if done else 90) * a))
        d.text((xs[i], y0 + 98), lab, font=T.font("grotesk", 24 if not act else 27), fill=col, anchor="mm")

# ---------------------------------------------------------------- behind-the-person graphics (source time)
def behind_layers(ts, canvas_list):
    """append float RGBA full-frame layers that must sit BEHIND the person"""
    add = canvas_list.append
    # HOOK: 3D chrome GTBUY slam + label + HAUL
    if 1.0 <= ts <= 5.2:
        k = eo((ts - 1.0) / 0.35); out = eio((5.2 - ts) / 0.22)
        add(T.place_canvas(SP["gtbuy"], W, H, 540, 470, (1.7 - 0.7 * k) * (1 + 0.06 * (1 - out)), rot_y=-16 + 8 * eio((ts - 1) / 4),
                           rot_x=6, alpha=k * out, blur=(1 - k) * 10))
    if 2.0 <= ts <= 4.15:
        k = eo((ts - 2.0) / 0.35); add(T.place_canvas(SP["hook_label"], W, H, 540, 300 + (1 - k) * 18, 1.0, alpha=k * eio((4.15 - ts) / 0.2)))
    if 4.15 <= ts <= 5.2:
        k = back((ts - 4.18) / 0.35, 1.4); add(T.place_canvas(SP["haul"], W, H, 540, 290, 0.8 + 0.2 * k, rot_x=(1 - clamp(k)) * 70, alpha=clamp(k) * eio((5.2 - ts) / 0.2)))
    # 2x40 / 2x30 tiles
    for (t0, x, num, lab) in [(9.06, 285, "2× 40 %", "COUPONS"), (10.46, 795, "2× 30 %", "SHIPPING")]:
        if t0 <= ts <= 12.35:
            if (num, lab) not in SP:
                p = panel(460, 290, 34, 0.82); d = ImageDraw.Draw(p)
                nm = T.text_mask(num, "unb", 74, 0.0); g = (T.gradient(nm, (255, 226, 120), (255, 140, 40)) * 255).astype(np.uint8)
                gi = Image.fromarray(g); p.alpha_composite(gi, (int(230 - gi.width / 2), 60))
                d.text((230, 222), lab, font=T.font("grotesk", 32), fill=(255, 255, 255, 190), anchor="mm")
                SP[(num, lab)] = np.asarray(p).astype(np.float32) / 255
            k = back((ts - t0) / 0.45, 1.3); out = eio((12.35 - ts) / 0.3)
            add(T.place_canvas(SP[(num, lab)], W, H, x, 330 - (1 - out) * 40, 0.9 + 0.1 * clamp(k), rot_x=(1 - clamp(k)) * -75, alpha=clamp(eo((ts - t0) / 0.25)) * out))
    # 3 -> 4 COUPONS
    if 14.44 <= ts <= 15.4:
        k = eo((ts - 14.44) / 0.3); gone = eo((ts - 15.22) / 0.18)
        L = T.place_canvas(SP["c3"], W, H, 540, 380 - gone * 60, 1.0 - 0.2 * gone, alpha=k * (1 - gone))
        add(L)
        if ts > 14.9:  # red strike draws across
            p = eo((ts - 14.9) / 0.2); im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            w2 = SP["c3"].shape[1] / 2 * 0.95; d.line([(540 - w2, 400 - gone * 60), (540 - w2 + 2 * w2 * p, 360 - gone * 60)], fill=RED + (int(255 * (1 - gone)),), width=12)
            add(np.asarray(im).astype(np.float32) / 255)
    if 15.3 <= ts <= 16.45:
        k = back((ts - 15.36) / 0.4, 1.5); out = eio((16.45 - ts) / 0.22)
        add(T.place_canvas(SP["c4"], W, H, 540, 600, (1.45 - 0.45 * clamp(k)) * (1 + 0.05 * (1 - out)), rot_x=(1 - clamp(k)) * 30, alpha=clamp(eo((ts - 15.3) / 0.15)) * out, blur=(1 - clamp(k)) * 6))
    # AGENT outline -> fill wipe
    if 22.4 <= ts <= 24.6:
        k = eo((ts - 22.4) / 0.35); out = eio((24.6 - ts) / 0.25); wipe = eio((ts - 22.6) / 0.6)
        o = SP["agent_out"]; f = SP["agent_fill"].copy()
        hf, wf = f.shape[:2]; f[:, int(wf * wipe):, 3] = 0
        add(T.place_canvas(o, W, H, 600, 600, 0.92 + 0.08 * k, alpha=k * out))
        add(T.place_canvas(f, W, H, 600, 600, 0.92 + 0.08 * k, alpha=k * out))
        if ts > 22.78:
            k2 = eo((ts - 22.78) / 0.35); add(T.place_canvas(SP["agent_eyebrow"], W, H, 600, 455 + (1 - k2) * 14, 1.0, alpha=k2 * out))
    # 3-5 TAGE spinning chrome
    if 24.72 <= ts <= 26.55:
        k = eo((ts - 24.72) / 0.45); out = eio((26.55 - ts) / 0.3)
        ry = 85 * (1 - k) - 8 - 50 * (1 - out)
        add(T.place_canvas(SP["tage35"], W, H, 560, 590, 1.0, rot_y=ry, rot_x=5, alpha=clamp(k * 1.4) * out))
    # Volumen / Gewicht / geschätzt kinetic
    if 38.3 <= ts <= 40.25:
        out = eio((40.25 - ts) / 0.25)
        k1 = eo((ts - 38.3) / 0.35); add(T.place_canvas(SP["vol"], W, H, 620 - (1 - k1) * 700, 390, 1.0, alpha=out))
        if ts > 38.9: k2 = eo((ts - 38.9) / 0.35); add(T.place_canvas(SP["gew"], W, H, 620 + (1 - k2) * 700, 510, 1.0, alpha=out))
        if ts > 39.42: k3 = eo((ts - 39.42) / 0.4); add(T.place_canvas(SP["geschaetzt"], W, H, 640, 640 + (1 - k3) * 20, 0.94 + 0.06 * k3, alpha=k3 * out, blur=(1 - k3) * 5))
    # HOHE PREISE slam
    if 42.82 <= ts <= 44.05:
        k = back((ts - 42.86) / 0.35, 1.6); out = eio((44.05 - ts) / 0.22)
        add(T.place_canvas(SP["hohe"], W, H, 540, 560, 1.4 - 0.4 * clamp(k), rot_z=-4 * clamp(k), alpha=clamp(eo((ts - 42.82) / 0.12)) * out, blur=(1 - clamp(k)) * 6))
    # REHEARSAL echo stack + Paketsimulation
    if 46.9 <= ts <= 49.55:
        out = eio((49.55 - ts) / 0.25); k = eo((ts - 46.94) / 0.3)
        for e in range(3, 0, -1):
            ke = eo((ts - 47.0 - 0.07 * e) / 0.35)
            add(T.place_canvas(SP["reh_o"], W, H, 600, 470 - e * 52 * ke, 1.0, alpha=ke * out * (0.55 - 0.13 * e)))
        add(T.place_canvas(SP["reh"], W, H, 600, 470, 1.25 - 0.25 * k, alpha=k * out, blur=(1 - k) * 6))
        if ts > 48.3:
            k2 = eo((ts - 48.36) / 0.4); add(T.place_canvas(SP["paketsim"], W, H, 620, 612 + (1 - k2) * 18, 1.0, alpha=k2 * out))
            if ts > 48.6:
                p = eo((ts - 48.6) / 0.4); im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                w2 = SP["paketsim"].shape[1] / 2; d.line([(620 - w2 + 20, 668), (620 - w2 + 20 + (2 * w2 - 40) * p, 662)], fill=RED + (int(255 * out),), width=6)
                add(np.asarray(im).astype(np.float32) / 255)
    # 8-12 TAGE tilted
    if 74.5 <= ts <= 77.35:
        k = eo((ts - 74.58) / 0.45); out = eio((77.35 - ts) / 0.25)
        add(T.place_canvas(SP["n812"], W, H, 600, 540, 1.3 - 0.3 * k, rot_x=22, rot_y=-10 + 4 * eio((ts - 74.5) / 2.8), alpha=k * out, blur=(1 - k) * 8))
        if ts > 75.8: k2 = eo((ts - 75.8) / 0.35); add(T.place_canvas(SP["tage"], W, H, 600, 700, 1.0, alpha=k2 * out))
    # final ≈ 8 TAGE (persists into freeze)
    if ts >= 90.5:
        k = eo((ts - 90.64) / 0.4)
        add(T.place_canvas(SP["final8"], W, H, 600, 520, (1.6 - 0.6 * k), rot_y=-12 + 4 * eio((ts - 90.6) / 3), rot_x=6, alpha=clamp(eo((ts - 90.5) / 0.15)), blur=(1 - k) * 9))

def cards_behind(ts, canvas):
    """image cards / infographic panels on the free right side (PIL canvas, composited behind the person)"""
    def card(key, t0, t1, label, x=790, y=430, label_pos="top"):
        if not (t0 <= ts <= t1): return None
        kin = back((ts - t0) / 0.5, 1.2); a = clamp(eo((ts - t0) / 0.3)) * eio((t1 - ts) / 0.3)
        tile = kenburns(IM[key], 420, 540, clamp((ts - t0) / (t1 - t0)))
        c = card_rgba(tile, label, 30, label_pos); s = 0.9 + 0.1 * clamp(kin)
        L = T.place_canvas(T.shadow(c, 24, 0, 26, 0.4), W, H, x, y + (1 - clamp(kin)) * 50, s, rot_y=-8 * (1 - clamp(kin)), alpha=a)
        return L
    out = []
    for args in [("warehouse_card", 26.55, 27.12, "IM WAREHOUSE"), ("packing", 36.62, 38.25, "HAUL WIRD GEPACKT"),
                 ("scale", 49.95, 53.05, "WIRKLICH GEWOGEN"), ("door", 64.2, 65.68, "ZU DIR NACH HAUSE")]:
        L = card(*args)
        if L is not None: out.append(L)
    # chips after QC
    if 33.05 <= ts <= 36.45:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a_out = eio((36.45 - ts) / 0.3)
        for i, (t0, txt, col) in enumerate([(33.1, "↩  ZURÜCKSCHICKEN MÖGLICH", (255, 255, 255)), (35.25, "→  NÄCHSTER SCHRITT", GOLD)]):
            if ts < t0: continue
            k = back((ts - t0) / 0.4, 1.3); a = clamp(eo((ts - t0) / 0.2)) * a_out
            f = T.font("grotesk", 32); tw = f.getlength(txt); x1 = 1040; x0 = x1 - tw - 64; y = 300 + i * 100 + (1 - clamp(k)) * 24
            ImageDraw.Draw(im).rounded_rectangle([x0, y, x1, y + 74], 37, fill=(14, 14, 18, int(215 * a)), outline=col + (int(120 * a),), width=2)
            ImageDraw.Draw(im).text((x0 + 32, y + 37), txt, font=f, fill=col + (int(255 * a),), anchor="lm")
        out.append(np.asarray(im).astype(np.float32) / 255)
    # price comparison bars
    if 53.1 <= ts <= 59.62:
        a = env(ts, 53.1, 59.62, 0.35, 0.3); pw, ph = 470, 520
        p = panel(pw, ph, 34, 0.84 * a); d = ImageDraw.Draw(p)
        d.text((36, 40), "VERSANDPREIS", font=T.font("grotesk", 28), fill=(255, 255, 255, int(170 * a)))
        base = 430
        for i, (t0, hh, col, lab) in enumerate([(53.15, 300, (232, 72, 60), "GESCHÄTZT"), (56.9, 160, GREEN, "SIMULATION")]):
            if ts < t0: continue
            g = eo((ts - t0) / 0.6); x = 70 + i * 200
            d.rounded_rectangle([x, base - hh * g, x + 130, base], 14, fill=col + (int(255 * a),))
            d.text((x + 65, base + 40), lab, font=T.font("grotesk", 24), fill=(255, 255, 255, int(200 * a)), anchor="mm")
            d.text((x + 65, base - hh * g - 30), "€€€" if i == 0 else "€", font=T.font("unb", 34), fill=col + (int(255 * a * g),), anchor="mm")
        if ts > 57.84:
            k = back((ts - 57.84) / 0.4, 1.8); f = T.font("unb", 30); txt = "WENIGER ZAHLEN ↓"
            tw = f.getlength(txt) * clamp(k); bx = pw / 2 - tw / 2 - 20
            d.rounded_rectangle([bx, 88, bx + tw + 40, 146], 29, fill=GREEN + (int(255 * a * clamp(k)),))
            if k > 0.6: d.text((pw / 2, 117), txt, font=f, fill=INK + (int(255 * a),), anchor="mm")
        out.append(T.place_canvas(T.shadow(np.asarray(p).astype(np.float32) / 255, 24, 0, 24, 0.35), W, H, 790, 440 + (1 - eo((ts - 53.1) / 0.4)) * 40, 1.0, alpha=1.0))
    # ZUGESTELLT stamp over door card
    if 64.95 <= ts <= 65.68:
        k = back((ts - 64.95) / 0.3, 2.0); a = clamp(eo((ts - 64.95) / 0.1)) * eio((65.68 - ts) / 0.25)
        im = Image.new("RGBA", (520, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 8, 512, 162], 26, outline=(220, 40, 40, 255), width=10)
        d.text((260, 85), "ZUGESTELLT", font=T.font("arx", 54), fill=(220, 40, 40, 255), anchor="mm")
        st = np.asarray(im).astype(np.float32) / 255
        out.append(T.place_canvas(st, W, H, 790, 520, 1.6 - 0.6 * clamp(k), rot_z=-11, alpha=a))
    # DHL / DPD tiles
    if 66.0 <= ts <= 72.75:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); a_out = eio((72.75 - ts) / 0.3)
        ka = eo((ts - 66.1) / 0.35)
        d.text((790, 168 + (1 - ka) * 12), "DIE BESTEN VERSANDLINIEN", font=T.font("grotesk", 30), fill=INK + (int(230 * ka * a_out),), anchor="mm")
        out.append(np.asarray(im).astype(np.float32) / 255)
        for (t0, name, y, fav) in [(67.48, "DHL", 380, True), (68.5, "DPD", 620, False)]:
            if ts < t0: continue
            k = back((ts - t0) / 0.45, 1.3); a = clamp(eo((ts - t0) / 0.25)) * a_out
            hi = eo((ts - 70.02) / 0.4) if ts > 70.02 else 0.0
            p = panel(440, 210, 34, 0.86); d = ImageDraw.Draw(p)
            if fav and hi > 0:
                d.rounded_rectangle([0, 0, 439, 209], 34, outline=GOLD + (int(255 * hi),), width=5)
            m = T.text_mask(name, "arx", 104, 0.02)
            g = T.gradient(m, (255, 226, 120), (255, 150, 40)) if (fav and hi > 0) else T.solid(m, (245, 245, 250))
            if fav and hi > 0: g = g * hi + T.solid(m, (245, 245, 250)) * (1 - hi)
            gi = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8)); p.alpha_composite(gi, (int(220 - gi.width / 2), int(105 - gi.height / 2)))
            L = np.asarray(p).astype(np.float32) / 255
            if fav and hi > 0:
                b = Image.new("RGBA", (440, 270), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
                bd.rounded_rectangle([250, 0, 432, 52], 26, fill=GOLD + (int(255 * hi),))
                cx_, cy_, R, r = 280, 26, 15, 6.5
                star = [(cx_ + (R if j % 2 == 0 else r) * np.sin(j * np.pi / 5), cy_ - (R if j % 2 == 0 else r) * np.cos(j * np.pi / 5)) for j in range(10)]
                bd.polygon(star, fill=INK + (int(255 * hi),)); bd.text((360, 26), "FAVORIT", font=T.font("grotesk", 24), fill=INK + (int(255 * hi),), anchor="mm")
                Lb = np.zeros((270, 440, 4), np.float32); Lb[60:270] = L; L = T.over(np.asarray(b).astype(np.float32) / 255, Lb)
            dim = 1 - 0.55 * (eo((ts - 70.02) / 0.4) if (not fav and ts > 70.02) else 0)
            s = (0.9 + 0.1 * clamp(k)) * (1 + 0.1 * hi)
            out.append(T.place_canvas(T.shadow(L, 20, 0, 20, 0.35), W, H, 790, y - (30 if fav and hi > 0 else 0), s, rot_x=(1 - clamp(k)) * -60, alpha=a * dim))
    # calendar + delay chips
    if 77.4 <= ts <= 88.45:
        a = env(ts, 77.4, 88.45, 0.4, 0.3); pw, ph = 470, 640
        p = panel(pw, ph, 34, 0.84 * a); d = ImageDraw.Draw(p)
        d.text((36, 40), "LIEFERZEIT", font=T.font("grotesk", 28), fill=(255, 255, 255, int(170 * a)))
        bs, gap = 86, 16; gx0, gy0 = 36, 100
        for i in range(12):
            r_, c_ = divmod(i, 4); x = gx0 + c_ * (bs + gap); y = gy0 + r_ * (bs + gap); day = i + 1
            filled = ts > 77.5 + i * 0.2 and day <= 8
            mine = ts > 79.1 and day in (7, 8); window = ts > 79.1 and day >= 8
            if mine: d.rounded_rectangle([x, y, x + bs, y + bs], 18, fill=GOLD + (int(255 * a),))
            elif filled: d.rounded_rectangle([x, y, x + bs, y + bs], 18, fill=(255, 255, 255, int(46 * a)))
            else: d.rounded_rectangle([x, y, x + bs, y + bs], 18, outline=(255, 255, 255, int((110 if window else 50) * a)), width=3)
            d.text((x + bs / 2, y + bs / 2), str(day), font=T.font("unb", 30), fill=(INK if mine else (255, 255, 255)) + (int((255 if (mine or filled) else 120) * a),), anchor="mm")
        if ts > 79.1:
            k = eo((ts - 79.1) / 0.35); d.text((36, 425), "BEI MIR: 7–8 TAGE", font=T.font("unb", 30), fill=GOLD + (int(255 * a * k),))
            d.text((36, 470), "NORMAL: 8–12 TAGE", font=T.font("grotesk", 26), fill=(255, 255, 255, int(150 * a * k)))
        for j, (t0, txt, col) in enumerate([(81.92, "⚠ STREIKS", (255, 255, 255)), (83.04, "FEIERTAGE IN CHINA", (255, 255, 255)), (87.46, "VERZÖGERUNG", (255, 110, 96))]):
            if ts < t0: continue
            k = back((ts - t0) / 0.35, 1.4); f = T.font("grotesk", 24); tw = f.getlength(txt)
            x = [36, 36 + 185, 36][j] if j < 2 else 36; y = 530 if j < 2 else 585
            if j == 1: x = 36 + T.font("grotesk", 24).getlength("⚠ STREIKS") + 44 + 16
            d.rounded_rectangle([x, y, x + tw + 36, y + 44], 22, fill=col + (int(40 * a * clamp(k)),), outline=col + (int(200 * a * clamp(k)),), width=2)
            d.text((x + 18, y + 22), txt, font=f, fill=col + (int(255 * a * clamp(k)),), anchor="lm")
        out.append(T.place_canvas(T.shadow(np.asarray(p).astype(np.float32) / 255, 24, 0, 24, 0.35), W, H, 800, 520 + (1 - eo((ts - 77.4) / 0.4)) * 40, 1.0))
    return out

# ---------------------------------------------------------------- full-screen cutaways & split screen
def fullscreen(ts, frame_comp, fsrc):
    """returns modified comp for cutaway moments (warehouse card->fullscreen->iris, plane whip)"""
    # warehouse: grows from the card position to fullscreen, iris back to the speaker
    if 27.1 <= ts <= 28.75:
        p_all = clamp((ts - 27.1) / (28.75 - 27.1)); img = kenburns(IM["warehouse"], W, H, p_all, 1.12, 1.0)
        g = eo((ts - 27.1) / 0.35)
        x0 = 790 - 210 + (0 - (790 - 210)) * g; y0 = 430 - 270 + (0 - (430 - 270)) * g
        x1 = 790 + 210 + (W - (790 + 210)) * g; y1 = 430 + 270 + (H - (430 + 270)) * g
        m = np.zeros((H, W), np.float32)
        r = int(30 * (1 - g)); mm = rrect_mask(int(x1 - x0), int(y1 - y0), r); m[int(y0):int(y0) + mm.shape[0], int(x0):int(x0) + mm.shape[1]] = mm[:H - int(y0), :W - int(x0)]
        if ts > 28.45:   # iris reveal from the face
            top, cx, _ = head(fsrc); q = eio((ts - 28.45) / 0.3)
            yy, xx = np.ogrid[:H, :W]; rad = q * 1500
            hole = np.clip((rad - np.sqrt((xx - cx) ** 2 + (yy - (top + 170)) ** 2)) / 6, 0, 1)
            m = m * (1 - hole)
        comp = frame_comp * (1 - m[..., None]) + img * m[..., None]
        if ts > 27.3:
            k = eo((ts - 27.3) / 0.5); a = k * (1 - eio((ts - 28.3) / 0.15))
            comp = over_full(comp, T.place_canvas(SP["warehouse_t"], W, H, 540, 860, 1.0, alpha=a))
            comp = over_full(comp, T.place_canvas(SP["warehouse_s"], W, H, 540, 960 + (1 - k) * 12, 1.0, alpha=a))
        return comp
    # plane: vertical whip in / out
    if 62.35 <= ts <= 63.8:
        tin = eio((ts - 62.35) / 0.22); tout = eio((ts - 63.55) / 0.25)
        img = kenburns(IM["plane"], W, H, clamp((ts - 62.35) / 1.45), 1.0, 1.1)
        off = int((1 - tin) * H - tout * H)
        sh = np.roll(img, off, axis=0); m = np.zeros((H, W), np.float32)
        if off >= 0: m[off:] = 1
        else: m[:H + off] = 1
        comp = frame_comp * (1 - m[..., None]) + sh * m[..., None]
        speed = max(1 - tin, tout) if (tin < 1 or tout > 0) else 0
        if speed > 0.05:
            k = int(9 + 70 * speed) | 1; ker = np.zeros((k, 1), np.float32); ker[:, 0] = 1 / k
            comp = cv2.filter2D(comp, -1, ker)
        k2 = eo((ts - 62.6) / 0.4); a = k2 * (1 - tout)
        comp = over_full(comp, T.place_canvas(SP["plane_t"], W, H, 540, 640, 1.0 + 0.04 * eio((ts - 62.6) / 1.2), alpha=a))
        comp = over_full(comp, T.place_canvas(SP["plane_s"], W, H, 540, 730, 1.0, alpha=a))
        return comp
    return None

def split_offset(ts):
    if not (29.25 <= ts <= 32.1): return 0.0
    return 330 * min(eio((ts - 29.25) / 0.35), eio((32.1 - ts) / 0.3))
def split_panel(ts):
    if not (29.25 <= ts <= 32.1): return None
    k = min(eio((ts - 29.25) / 0.35), eio((32.1 - ts) / 0.3)); y_off = int((k - 1) * 960)
    img = kenburns(IM["qc"], W, 960, clamp((ts - 29.25) / 2.85), 1.1, 1.0)
    for fl in (30.0, 31.0):  # camera shutter flashes
        if fl <= ts <= fl + 0.18: img = img + (1 - img) * 0.65 * (1 - (ts - fl) / 0.18)
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    L, M_ = 70, 60
    for (x, y, sx, sy) in [(M_, M_ + 150, 1, 1), (W - M_, M_ + 150, -1, 1), (M_, 960 - M_, 1, -1), (W - M_, 960 - M_, -1, -1)]:
        d.line([(x, y), (x + sx * L, y)], fill=(255, 255, 255, 230), width=5); d.line([(x, y), (x, y + sy * L)], fill=(255, 255, 255, 230), width=5)
    if int(ts * 2) % 2 == 0: d.ellipse([M_ + 10, M_ + 182, M_ + 34, M_ + 206], fill=(235, 50, 45, 255))
    d.text((M_ + 46, M_ + 194), "REC", font=T.font("grotesk", 28), fill=(255, 255, 255, 235), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255
    if ts > 29.6:
        kk = eo((ts - 29.6) / 0.4); arr = T.over(T.place_canvas(SP["qc_t"], W, 960, 360, 800, 1.0, alpha=kk), arr)
    if ts > 30.98:
        kk = eo((ts - 30.98) / 0.35); arr = T.over(T.place_canvas(SP["qc_s"], W, 960, 300, 870, 1.0, alpha=kk), arr)
    full = np.zeros((H, W, 4), np.float32)
    ys, ye = max(y_off, 0), y_off + 960
    full[ys:ye] = arr[960 - (ye - ys):]
    full[ye - 3:ye + 3, :, :3] = 1; full[ye - 3:ye + 3, :, 3] = 1 if ye > 3 else 0
    return full

# ---------------------------------------------------------------- captions
raw = json.load(open("words.json"))
words, i = [], 0
while i < len(raw):
    w = raw[i]; nx = raw[i + 1] if i + 1 < len(raw) else None
    if w["s"] < 0.92 or w["s"] >= 91.95: i += 1; continue
    if w["w"] in ("2x40", "2x30") and nx and nx["w"].startswith("%"): words.append(dict(w="2× " + w["w"][2:] + " %", s=w["s"], e=nx["e"])); i += 2; continue
    if w["w"] == "KC" and nx and nx["w"].startswith("-"): words.append(dict(w="QC-Bilder", s=w["s"], e=nx["e"])); i += 2; continue
    if w["w"] in ("3", "8") and nx and nx["w"] in ("-5", "-12"): words.append(dict(w=w["w"] + "–" + nx["w"][1:], s=w["s"], e=nx["e"])); i += 2; continue
    rep = {"erhält": "erhaltet", "müsst": "müsste"}
    words.append(dict(w=rep.get(w["w"], w["w"]), s=w["s"], e=w["e"])); i += 1
KEY = {"gtbuy", "haul", "link", "bio", "2× 40 %", "2× 30 %", "coupons", "4", "account", "agent", "3–5", "warehouse",
       "qc-bilder", "qualitätskontrolle", "gepackt", "volumen", "gewicht", "geschätzt", "hohe", "preise", "rehearsal", "paketsimulation",
       "gewogen", "weniger", "zugestellt", "dhl", "dpd", "8–12", "7", "8", "streiks", "feiertage", "china", "verzögerungen", "simulation", "shipping"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nx = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if nx is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 16 or nx["s"] - w["e"] > 0.35: chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    o0 = s2o(c[0]["s"]); o1e = s2o(min(c[-1]["e"], 91.95))
    if o0 is None or o1e is None: continue
    CH.append(dict(words=[dict(w=x["w"], s=s2o(x["s"]) or o0, e=s2o(min(x["e"], 91.95)) or o1e) for x in c], t0=o0 - 0.05, t1=o1e + 0.25))
for j in range(len(CH) - 1): CH[j]["t1"] = min(CH[j]["t1"], CH[j + 1]["t0"])
WC = {}
def word_sprite(tok, key, col):
    k = (tok, key, col)
    if k not in WC:
        if key: m = T.text_mask(tok, "serifi", 104, 0.0, pad=30)
        else: m = T.text_mask(tok.upper(), "montb", 70, 0.01, pad=30)
        L = T.solid(m, col, pad=12); dark = T.outline(m, 3, (10, 10, 12), pad=12)
        L = T.over(L, dark); WC[k] = (T.shadow(L, 8, 0, 5, 0.55), m.shape[1] - 30)
    return WC[k]
def captions(to, comp):
    ch = next((c for c in CH if c["t0"] <= to < c["t1"]), None)
    if ch is None: return comp
    toks = [clean(w["w"]) for w in ch["words"]]; keys = [t.lower() in KEY for t in toks]
    sprites = [word_sprite(t, k, GOLD if k else WHITE) for t, k in zip(toks, keys)]
    gap = 48; total = sum(vw for _, vw in sprites) + gap * (len(sprites) - 1)
    fit = min(1.0, 960 / total); total *= fit; gap *= fit
    x = W / 2 - total / 2; base_y = 1490
    for n_, (w, (sp, wd), k) in enumerate(zip(ch["words"], sprites, keys)):
        wd = wd * fit; cx = x + wd / 2
        appear = eo((to - ch["t0"] - n_ * 0.045) / 0.22); active = w["s"] - 0.02 <= to <= w["e"] + 0.03
        pop = back((to - w["s"]) / 0.18, 2.2) if active else 1.0
        s = (0.9 + 0.1 * clamp(appear)) * (1 + (0.1 if active else 0) * clamp(pop)) * fit
        if active and not k:
            sp = word_sprite(toks[n_], False, GOLD)[0]
        L = T.place_canvas(sp, W, H, cx, base_y - (8 if k else 0), s, rot_x=(1 - clamp(appear)) * 70, alpha=clamp(appear * 1.5))
        comp = over_full(comp, L); x += wd + gap
    return comp

# ---------------------------------------------------------------- per-frame compositing
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.13 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1.6) ** 1.3)[..., None]
rng = np.random.default_rng(9)
def box_(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=10, eps=2e-3):
    mI, mp = box_(I, r), box_(p, r); a = (box_(I * p, r) - mI * mp) / (box_(I * I, r) - mI * mI + eps); b = mp - a * mI
    return box_(a, r) * I + box_(b, r)

def zoom_blur(img, cx, cy, amount, n=6):
    acc = np.zeros_like(img)
    for k in range(n):
        s = 1 + amount * k / (n - 1); M = cv2.getRotationMatrix2D((cx, cy), 0, s)
        acc += cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return acc / n

def transition_params(to):
    """extra zoom factor, zoom-blur amount, horizontal whip offset, flash for the edit points"""
    zf, zb, dx, fl = 1.0, 0.0, 0.0, 0.0
    if to < 0.55: k = eo(to / 0.55); zf *= 1 + 0.42 * (1 - k); zb = 0.12 * (1 - k) if to < 0.35 else 0.0          # hook whip-zoom
    c1, c2, c3 = CUTS_OUT
    if c1 - 0.2 <= to < c1: p = ei((to - (c1 - 0.2)) / 0.2); zf *= 1 + 0.28 * p; zb = 0.10 * p                     # zoom-through
    if c1 <= to < c1 + 0.25: p = 1 - eo((to - c1) / 0.25); zf *= 1 + 0.28 * p; zb = 0.10 * p
    if c2 - 0.16 <= to < c2: p = ei((to - (c2 - 0.16)) / 0.16); dx = -W * 0.11 * p; zf *= 1 + 0.24 * p           # whip pan
    if c2 <= to < c2 + 0.22: p = 1 - eo((to - c2) / 0.22); dx = W * 0.11 * p; zf *= 1 + 0.24 * p
    if c3 - 0.18 <= to < c3: p = ei((to - (c3 - 0.18)) / 0.18); zf *= 1 - 0.1 * p; fl = 0.35 * p                 # pull-out + flash
    if c3 <= to < c3 + 0.25: p = 1 - eo((to - c3) / 0.25); zf *= 1 + 0.12 * p; fl = max(fl, 0.35 * p)
    return zf, zb, dx, fl

def render_frame(o, frame8, mask8, fsrc, freeze_t=None):
    to = o / FPS; ts = fsrc / FPS if freeze_t is None else 92.0 + freeze_t
    frame = frame8.astype(np.float32) / 255; m = mask8.astype(np.float32) / 255
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    m = np.clip(cv2.resize(guided(gs, cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    zf, zb, dx, fl = transition_params(to) if freeze_t is None else (1.0, 0.0, 0.0, 0.0)
    s = zoom_eff(min(ts, 92.0)) * zf
    if freeze_t is not None: s *= 1 + 0.04 * eo(freeze_t / 0.4)
    M = camera_matrix(fsrc, s, dx, split_offset(ts))
    frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    m = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if dx != 0:
        k = int(9 + abs(dx) * 1.1) | 1; ker = np.zeros((1, k), np.float32); ker[0] = 1 / k
        frame = cv2.filter2D(frame, -1, ker); m = cv2.filter2D(m, -1, ker)
    if zb > 0.005:
        top, cx, _ = head(fsrc); frame = zoom_blur(frame, cx, top + 170, zb); m = zoom_blur(m[..., None].repeat(3, 2), cx, top + 170, zb)[..., 0]
    bgk = (1 - m)[..., None]
    comp = frame
    if freeze_t is not None:   # freeze frame: desaturated, darker background, sticker outline on the person
        k = eo(freeze_t / 0.35); gray = comp.mean(2, keepdims=True)
        bg = (comp * (1 - 0.75 * k) + gray * 0.75 * k) * (1 - 0.28 * k)
        comp = comp * (1 - bgk) + bg * bgk
    layers = []; behind_layers(ts, layers)
    for L in layers: comp = over_full(comp, L, bgk)
    for L in cards_behind(ts, None) if True else []: comp = over_full(comp, L, bgk)
    if freeze_t is not None:
        k = eo(freeze_t / 0.3); mb = (m > 0.5).astype(np.uint8)
        ring = cv2.dilate(mb, np.ones((23, 23), np.uint8)).astype(np.float32) - mb
        ring = cv2.GaussianBlur(ring, (0, 0), 1.2)[..., None] * k
        comp = comp * (1 - ring) + ring
    fs = fullscreen(ts, comp, fsrc) if freeze_t is None else None
    if fs is not None: comp = fs
    sp = split_panel(ts)
    if sp is not None: comp = over_full(comp, sp)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0)); stepper(ts, canvas); ui_layer(ts, canvas)
    U = np.asarray(canvas).astype(np.float32) / 255
    if U[..., 3].max() > 0: comp = over_full(comp, U)
    comp = comp * VIG
    if fl > 0: comp = comp + (1 - comp) * fl
    if freeze_t is None: comp = captions(to, comp)
    comp = comp + rng.normal(0, 0.008, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if freeze_t is not None and freeze_t > FREEZE_LEN - 0.45: comp *= clamp((FREEZE_LEN - freeze_t) / 0.45)
    return (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)

from tl import FREEZE as FREEZE_LEN

def read_exact(cmd, size):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE); return p

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "preview":
        outs = [float(x) for x in sys.argv[2].split(",")]
        for to in outs:
            o = min(int(round(to * FPS)), N_OUT - 1); fsrc = FRAMES[min(o, N_MAIN - 1)]
            fz = (o - N_MAIN) / FPS if o >= N_MAIN else None
            f8 = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{fsrc / FPS:.4f}", "-i", "input_cfr.mov", "-vf", ENH, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout, np.uint8).reshape(H, W, 3)
            m8 = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{fsrc / FPS:.4f}", "-i", "mask.mkv", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout, np.uint8).reshape(H, W)
            Image.fromarray(render_frame(o, f8, m8, fsrc, fz)).save(f"frames/p_{to:06.2f}.jpg", quality=92)
        print("preview done")
    else:
        K, NCH = int(sys.argv[2]), int(sys.argv[3])
        a, b = K * N_OUT // NCH, (K + 1) * N_OUT // NCH
        first_src = FRAMES[min(a, N_MAIN - 1)]
        dv = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{first_src / FPS:.4f}", "-i", "input_cfr.mov", "-vf", ENH, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        dm = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{first_src / FPS:.4f}", "-i", "mask.mkv", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-pix_fmt", "yuv420p", f"chunk_{K}.mp4"], stdin=subprocess.PIPE)
        cur = first_src - 1; f8 = m8 = None
        for o in range(a, b):
            if o < N_MAIN:
                need = FRAMES[o]
                while cur < need:
                    fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
                    if len(fb) < W * H * 3: break
                    f8 = np.frombuffer(fb, np.uint8).reshape(H, W, 3); m8 = np.frombuffer(mb, np.uint8).reshape(H, W); cur += 1
                out = render_frame(o, f8, m8, need)
            else:
                if f8 is None or cur < FRAMES[N_MAIN - 1]:
                    last = FRAMES[N_MAIN - 1]
                    while cur < last:
                        fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
                        if len(fb) < W * H * 3: break
                        f8 = np.frombuffer(fb, np.uint8).reshape(H, W, 3); m8 = np.frombuffer(mb, np.uint8).reshape(H, W); cur += 1
                out = render_frame(o, f8, m8, FRAMES[N_MAIN - 1], (o - N_MAIN) / FPS)
            enc.stdin.write(out.tobytes())
            if (o - a) % 60 == 0: print(f"chunk {K}: {o - a}/{b - a}", flush=True)
        enc.stdin.close(); enc.wait(); dv.kill(); dm.kill(); print(f"chunk {K} done")
