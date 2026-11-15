"""POV hand + phone, phone screens (lock, chat, members, photo, camera, call), intercom texture, banners, captions, cards."""
import numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont
from eng import W, H, OUTL, clamp, ease, eout, lerp, shade

_f = {}
def F(wt, size):
    k = (wt, int(size))
    if k not in _f: _f[k] = ImageFont.truetype(f"fonts/Poppins-{wt}.ttf", int(size))
    return _f[k]
XB, B, M = "ExtraBold", "Bold", "Medium"
WHO = dict(Hame=(238, 96, 84), Shiar=(96, 204, 128), Zizo=(246, 204, 76), Alan=(150, 190, 255))
GREY = (146, 156, 172)

def wrap(text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

# ---------------------------------------------------------------- phone screens (600 x 1220)
SW_, SH_ = 600, 1220
_cache = {}
def _key(spec): return repr(sorted((k, v if not isinstance(v, np.ndarray) else id(v)) for k, v in spec.items() if k != "msgs")) + repr([(m["who"], m["text"], m.get("kind"), m.get("prog")) for m in spec.get("msgs", [])])

def screen(spec):
    k = _key(spec)
    if k in _cache: return _cache[k]
    im = Image.new("RGB", (SW_, SH_), (13, 17, 24)); d = ImageDraw.Draw(im); kind = spec["kind"]
    if kind == "lock":
        for y in range(0, SH_, 4): d.rectangle([0, y, SW_, y + 4], fill=(14 + y // 60, 20 + y // 50, 44 + y // 28))
        d.text((300, 250), spec.get("time", "23:41"), font=F(B, 128), fill=(240, 244, 255), anchor="mm")
        d.text((300, 350), "Freitag, 13. November", font=F(M, 28), fill=(190, 198, 220), anchor="mm")
        y = 470
        for m in spec.get("msgs", [])[-2:]:
            lines = wrap(m["text"], F(M, 26), 480)[:3]; hh = 62 + 34 * len(lines)
            d.rounded_rectangle([34, y, 566, y + hh], 26, fill=(40, 48, 70))
            d.text((58, y + 14), "Die 4", font=F(M, 20), fill=(170, 180, 200)); d.text((58, y + 40), m["who"] or "Unbekannt", font=F(B, 26), fill=WHO.get(m["who"], (200, 200, 205)))
            for i, l in enumerate(lines): d.text((58 + F(B, 26).getlength((m["who"] or "Unbekannt") + "  "), y + 42 + 34 * i) if i == 0 else (58, y + 42 + 34 * i), l, font=F(M, 26), fill=(236, 238, 244))
            y += hh + 16
    elif kind == "chat":
        d.rectangle([0, 0, SW_, 128], fill=(22, 28, 38)); d.ellipse([24, 30, 98, 104], fill=(72, 92, 156)); d.text((61, 68), "4", font=F(B, 38), fill=(255, 255, 255), anchor="mm")
        d.text((116, 30), spec.get("title", "Die 4"), font=F(B, 36), fill=(255, 255, 255))
        d.text((116, 80), spec.get("sub", "Alan, Hame, Shiar, Zizo"), font=F(M, 22), fill=spec.get("subc", GREY))
        typed = spec.get("typed", "")
        d.rounded_rectangle([20, 1128, 580, 1200], 36, fill=(26, 32, 44))
        d.text((48, 1164), typed if typed else "Nachricht", font=F(M, 27), fill=(240, 240, 244) if typed else (110, 118, 132), anchor="lm")
        y = 1108
        if spec.get("typing"): d.text((30, y - 8), f"{spec['typing']} schreibt …", font=F(M, 24), fill=(150, 160, 176), anchor="ls"); y -= 46
        for m in reversed(spec.get("msgs", [])):
            own = m["who"] == "Alan"; mk = m.get("kind", "text")
            if mk == "sys":
                tw = F(M, 22).getlength(m["text"]); d.rounded_rectangle([300 - tw / 2 - 20, y - 44, 300 + tw / 2 + 20, y], 22, fill=(30, 36, 48))
                d.text((300, y - 22), m["text"], font=F(M, 22), fill=(170, 178, 192), anchor="mm"); y -= 58; continue
            nm = 0 if own else 36; fnt = F(M, 29)
            if mk == "voice": lines = []; body = 74; bw = 380
            elif mk == "photo": lines = []; body = 392; bw = 320
            else:
                lines = wrap(m["text"], fnt, 400); body = 40 * len(lines)
                bw = max([fnt.getlength(l) for l in lines] + [F(B, 24).getlength(m["who"] or "Unbekannt") if not own else 0]) + 44
            bh = nm + body + 30; x0 = SW_ - 22 - bw if own else 22; y0 = y - bh
            if y0 < 136: break
            d.rounded_rectangle([x0, y0, x0 + bw, y], 24, fill=(40, 98, 162) if own else (30, 38, 54))
            if not own: d.text((x0 + 22, y0 + 12), m["who"] or "Unbekannt", font=F(B, 24), fill=WHO.get(m["who"], (170, 170, 178)))
            ty = y0 + 14 + nm
            if mk == "voice":
                pr = m.get("prog", 0.0); d.polygon([(x0 + 26, ty + 8), (x0 + 26, ty + 52), (x0 + 62, ty + 30)], fill=(230, 234, 242))
                rng = np.random.default_rng(5)
                for i in range(26):
                    hh = 8 + int(rng.random() * 34); xx = x0 + 84 + i * 9
                    d.rounded_rectangle([xx, ty + 30 - hh / 2, xx + 5, ty + 30 + hh / 2], 2, fill=(246, 204, 76) if i / 26 < pr else (120, 130, 150))
                d.text((x0 + bw - 20, ty + 30), m.get("dur", "0:04"), font=F(M, 22), fill=(190, 196, 210), anchor="rm")
            elif mk == "photo":
                ph = Image.fromarray(m["img"]).resize((280, 372), Image.LANCZOS); im.paste(ph, (int(x0 + 20), int(ty)))
                d.rounded_rectangle([x0 + 20, ty, x0 + 300, ty + 372], 10, outline=(60, 70, 90), width=2)
            else:
                for i, l in enumerate(lines): d.text((x0 + 22, ty + 40 * i), l, font=fnt, fill=(240, 242, 248))
            y = y0 - 14
    elif kind == "members":
        d.rectangle([0, 0, SW_, 110], fill=(22, 28, 38)); d.text((300, 56), "Gruppeninfo", font=F(B, 32), fill=(255, 255, 255), anchor="mm")
        d.ellipse([230, 140, 370, 280], fill=(72, 92, 156)); d.text((300, 208), "4", font=F(B, 72), fill=(255, 255, 255), anchor="mm")
        d.text((300, 326), "Die 4", font=F(B, 44), fill=(255, 255, 255), anchor="mm")
        n = spec.get("n", 5); hot = spec.get("hot", True)
        d.text((300, 384), f"Gruppe · {n} Mitglieder", font=F(B if hot else M, 28), fill=(255, 96, 84) if (hot and n != 4) else GREY, anchor="mm")
        rows = [("Du", WHO["Alan"], "online", "A"), ("Hame", WHO["Hame"], spec.get("hame", "online"), "H"), ("Shiar", WHO["Shiar"], spec.get("shiar", "online"), "S"), ("Zizo", WHO["Zizo"], "online", "Z")]
        if n == 5: rows.append(("", (96, 98, 108), spec.get("joined", "beigetreten: heute, 23:41"), "?"))
        for i, (nm, col, sub, ini) in enumerate(rows):
            y = 450 + i * 132
            if nm == "" and hot: d.rounded_rectangle([14, y - 6, 586, y + 116], 22, fill=(58, 24, 26))
            d.ellipse([34, y + 10, 124, y + 100], fill=col); d.text((79, y + 56), ini, font=F(B, 40), fill=(20, 22, 28), anchor="mm")
            if nm: d.text((150, y + 14), nm, font=F(B, 34), fill=(255, 255, 255))
            else: d.rounded_rectangle([150, y + 26, 330, y + 44], 9, fill=(70, 72, 82))
            d.text((150, y + 62), sub, font=F(M, 24), fill=GREY)
    elif kind in ("photo", "camera"):
        im.paste((0, 0, 0), (0, 0, SW_, SH_)); ph = Image.fromarray(spec["img"]).resize((600, 1000), Image.LANCZOS); im.paste(ph, (0, 100))
        if kind == "photo": d.text((300, 52), spec.get("label", "Foto"), font=F(B, 28), fill=(235, 238, 244), anchor="mm")
        else:
            d.text((300, 52), "FOTO", font=F(B, 26), fill=(246, 204, 76), anchor="mm"); d.ellipse([250, 1112, 350, 1212], outline=(255, 255, 255), width=8); d.ellipse([264, 1126, 336, 1198], fill=(255, 255, 255))
            if spec.get("flash", 0) > 0: im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), min(1.0, spec["flash"]))
    elif kind == "call":
        for y in range(0, SH_, 4): d.rectangle([0, y, SW_, y + 4], fill=(16, 22 + y // 60, 30 + y // 40))
        d.ellipse([190, 230, 410, 450], fill=WHO["Zizo"]); d.text((300, 334), "Z", font=F(B, 120), fill=(20, 22, 28), anchor="mm")
        d.text((300, 520), "Zizo", font=F(B, 56), fill=(255, 255, 255), anchor="mm"); d.text((300, 590), spec.get("timer", "00:07"), font=F(M, 30), fill=GREY, anchor="mm")
        rng = np.random.default_rng(int(spec.get("lvl", 0) * 7) + 3)
        for i in range(30):
            hh = 10 + rng.random() * 90 * spec.get("lvl", 0.0); d.rounded_rectangle([90 + i * 14, 740 - hh / 2, 98 + i * 14, 740 + hh / 2], 3, fill=(246, 204, 76))
        d.ellipse([240, 980, 360, 1100], fill=(222, 62, 56)); d.rounded_rectangle([268, 1030, 332, 1050], 8, fill=(255, 255, 255))
    out = np.asarray(im).copy(); _cache[k] = out
    if len(_cache) > 400: _cache.pop(next(iter(_cache)))
    return out

def icom_tex(t, face="hame", on=1.0, near=1.0):
    im = Image.new("RGB", (252, 204), (22, 30, 30)); d = ImageDraw.Draw(im)
    d.rectangle([0, 150, 252, 204], fill=(34, 44, 44)); d.rectangle([20, 20, 80, 150], fill=(16, 22, 22)); d.rectangle([176, 30, 232, 150], fill=(16, 22, 22))
    if face:
        s = 0.62 + 0.38 * near; cx, cy = 126, 104 + 26 * (1 - near); from eng import CH
        hood = tuple(int(v * 0.55 + 20) for v in CH[face]["hood"])
        d.polygon([(cx - 120 * s, 210), (cx - 86 * s, cy + 40 * s), (cx + 86 * s, cy + 40 * s), (cx + 120 * s, 210)], fill=hood)
        d.ellipse([cx - 62 * s, cy - 70 * s, cx + 62 * s, cy + 56 * s], fill=(150, 138, 126)); d.pieslice([cx - 66 * s, cy - 78 * s, cx + 66 * s, cy + 20 * s], 180, 360, fill=(20, 18, 18))
        for sx in (-1, 1): d.ellipse([cx + sx * 26 * s - 17 * s, cy - 14 * s, cx + sx * 26 * s + 17 * s, cy + 20 * s], fill=(236, 236, 224)); d.ellipse([cx + sx * 26 * s - 2, cy + 1, cx + sx * 26 * s + 2, cy + 5], fill=(10, 10, 10))
        d.arc([cx - 36 * s, cy + 8 * s, cx + 36 * s, cy + 44 * s], 20, 160, fill=(30, 20, 20), width=3)
    a = np.asarray(im).astype(np.float32); g = a.mean(2, keepdims=True); a = a * 0.35 + g * np.array([0.6, 0.78, 0.7]) * 0.9
    a[::3] *= 0.72; rng = np.random.default_rng(int(t * 30)); a += rng.normal(0, 13, a.shape[:2])[..., None]
    roll = int((t * 70) % 204); a[roll:roll + 10] *= 1.35
    a *= on; a = np.clip(a, 0, 255).astype(np.uint8); im = Image.fromarray(a); d = ImageDraw.Draw(im)
    if on > 0.5:
        d.text((10, 6), "EINGANG", font=F(B, 16), fill=(220, 230, 224))
        if int(t * 2) % 2 == 0: d.ellipse([228, 8, 242, 22], fill=(230, 60, 50))
    return np.asarray(im)

# ---------------------------------------------------------------- hand + phone
PW, PH = 210, 427
SLEEVE = (188, 190, 200); SKIN = (214, 166, 132)
def phone(img, k, ui, bob=(0, 0), tilt=0.0, hide=0.0):
    """k: 0 = held low, 1 = raised in front of the face. Returns (cx, cy, scale) of the phone."""
    e = ease(k); cx = lerp(742, 540, e) + bob[0]; cy = lerp(1600, 1196, e) + bob[1] + hide * 900; s = lerp(1.0, 3.4, e); ang = math.radians(lerp(-13, -1.5, e) + tilt)
    ca, sa = math.cos(ang), math.sin(ang)
    def T(x, y): return (cx + s * (x * ca - y * sa), cy + s * (x * sa + y * ca))
    def I(p): return (int(round(p[0] * 8)), int(round(p[1] * 8)))
    def seg(a, b, th, col, ol=5):
        cv2.line(img, I(T(*a)), I(T(*b)), OUTL, int(th * s + 2 * ol), cv2.LINE_AA, 3); cv2.line(img, I(T(*a)), I(T(*b)), col, int(th * s), cv2.LINE_AA, 3)
    seg((150, 340), (330, 1100), 170, SLEEVE); seg((128, 300), (160, 366), 178, shade(SLEEVE, 0.86))
    cv2.ellipse(img, I(T(58, 150)), (int(122 * s * 8), int(112 * s * 8)), math.degrees(ang), 0, 360, OUTL, -1, cv2.LINE_AA, 3)
    cv2.ellipse(img, I(T(58, 150)), (int((122 * s - 5) * 8), int((112 * s - 5) * 8)), math.degrees(ang), 0, 360, SKIN, -1, cv2.LINE_AA, 3)
    r = 26; pts = []
    for (qx, qy, a0) in [(PW / 2 - r, -PH / 2 + r, -90), (PW / 2 - r, PH / 2 - r, 0), (-PW / 2 + r, PH / 2 - r, 90), (-PW / 2 + r, -PH / 2 + r, 180)]:
        for a in np.linspace(a0, a0 + 90, 7): pts.append(T(qx + r * math.cos(math.radians(a)), qy + r * math.sin(math.radians(a))))
    q = np.array([I(p) for p in pts], np.int32).reshape(-1, 1, 2)
    cv2.fillPoly(img, [q], (20, 22, 30), cv2.LINE_AA, 3); cv2.polylines(img, [q], True, OUTL, 5, cv2.LINE_AA, 3)
    if ui is not None:
        sc = (PW - 18) / SW_ * s
        Mx = np.float32([[sc * ca, -sc * sa, 0], [sc * sa, sc * ca, 0]]); o = T(-(PW - 18) / 2, -(PH - 18) / 2); Mx[0, 2], Mx[1, 2] = o
        x0, y0 = max(int(min(p[0] for p in pts)) - 2, 0), max(int(min(p[1] for p in pts)) - 2, 0); x1, y1 = min(int(max(p[0] for p in pts)) + 2, W), min(int(max(p[1] for p in pts)) + 2, H)
        if x1 > x0 and y1 > y0:
            Ml = Mx.copy(); Ml[0, 2] -= x0; Ml[1, 2] -= y0
            warped = cv2.warpAffine(ui, Ml, (x1 - x0, y1 - y0), flags=cv2.INTER_AREA if sc < 0.6 else cv2.INTER_LINEAR)
            mask = cv2.warpAffine(np.full(ui.shape[:2], 255, np.uint8), Ml, (x1 - x0, y1 - y0))
            reg = img[y0:y1, x0:x1]; m = (mask.astype(np.float32) / 255)[..., None]; reg[:] = (reg * (1 - m) + warped * m).astype(np.uint8)
    seg((132, 176), (116, 70), 42, SKIN)
    for i in range(4): seg((-138, -30 + i * 60), (-116, -30 + i * 60), 40, SKIN)
    return cx, cy, s

def left_hand(img, x, y, k=1.0):
    """open left hand reaching up to (x, y) from the bottom-left."""
    x0, y0 = 150, H + 120; hx, hy = lerp(x0, x, k), lerp(y0, y, k)
    def seg(a, b, th, col): cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), OUTL, th + 12, cv2.LINE_AA); cv2.line(img, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), col, th, cv2.LINE_AA)
    seg((x0 - 40, y0 + 200), (hx, hy + 150), 150, SLEEVE)
    for i, (dx, ln) in enumerate([(-66, 96), (-24, 122), (20, 124), (62, 100)]): seg((hx + dx, hy + 20), (hx + dx * 1.15, hy - ln), 38, SKIN)
    seg((hx + 84, hy + 80), (hx + 132, hy + 16), 42, SKIN)
    cv2.ellipse(img, (int(hx), int(hy + 70)), (96, 90), 0, 0, 360, OUTL, -1, cv2.LINE_AA); cv2.ellipse(img, (int(hx), int(hy + 70)), (90, 84), 0, 0, 360, SKIN, -1, cv2.LINE_AA)

# ---------------------------------------------------------------- overlays
_spr = {}
def _paste(img, spr, x, y, a=1.0):
    h, w = spr.shape[:2]; x, y = int(x), int(y); x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0: return
    s = spr[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32); al = s[..., 3:4] / 255 * a
    img[y0:y1, x0:x1] = (img[y0:y1, x0:x1] * (1 - al) + s[..., :3] * al).astype(np.uint8)

def banner(img, who, text, k, head=None):
    key = ("b", who, text)
    if key not in _spr:
        fb = F(XB, 40); lines = wrap(text, fb, 900); hh = 74 + 52 * len(lines) + 26
        im = Image.new("RGBA", (1016, hh + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([8, 12, 1008, hh + 12], 26, fill=(24, 16, 14, 150)); d.rounded_rectangle([4, 4, 1004, hh], 26, fill=(248, 242, 224, 255), outline=OUTL + (255,), width=5)
        d.text((34, 22), head or f"{who or 'Unbekannt'} · jetzt", font=F(B, 27), fill=(70, 62, 56, 255))
        for i, l in enumerate(lines): d.text((34, 62 + 52 * i), l, font=fb, fill=(22, 18, 16, 255))
        _spr[key] = np.asarray(im)
    s = _spr[key]; _paste(img, s, 32, lerp(-s.shape[0] - 10, 150, eout(k)))

def caption(img, text, y, pop=1.0, col=(255, 255, 255)):
    key = ("c", text, col)
    if key not in _spr:
        f = F(XB, 76); tw = int(f.getlength(text)) + 60
        if tw > 1030: f = F(XB, int(76 * 1030 / tw)); tw = int(f.getlength(text)) + 60
        im = Image.new("RGBA", (tw, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((tw / 2 + 3, 81), text, font=f, fill=(20, 12, 10, 150), anchor="mm", stroke_width=9, stroke_fill=(20, 12, 10, 150))
        d.text((tw / 2, 75), text, font=f, fill=col + (255,), anchor="mm", stroke_width=8, stroke_fill=OUTL + (255,))
        _spr[key] = np.asarray(im)
    s = _spr[key]
    if pop < 0.999:
        sc = 0.82 + 0.18 * eout(pop); s = cv2.resize(s, (max(2, int(s.shape[1] * sc)), max(2, int(s.shape[0] * sc))), interpolation=cv2.INTER_LINEAR)
    _paste(img, s, 540 - s.shape[1] / 2, y - s.shape[0] / 2)

def card(img, lines, a=1.0):
    """centered text card on black: lines = [(text, weight, size, color)]"""
    key = ("card", repr(lines))
    if key not in _spr:
        im = Image.new("RGBA", (W, 600), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = 60
        for text, wt, size, col in lines:
            d.text((540, y + size / 2), text, font=F(wt, size), fill=col + (255,), anchor="mm"); y += size + 34
        _spr[key] = np.asarray(im)
    _paste(img, _spr[key], 0, 720, a)

def tag(img, text, a=1.0):
    key = ("tag", text)
    if key not in _spr:
        f = F(B, 30); tw = int(f.getlength(text)) + 44; im = Image.new("RGBA", (tw, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, tw - 1, 59], 30, fill=(16, 12, 12, 190)); d.text((tw / 2, 30), text, font=f, fill=(240, 232, 214, 255), anchor="mm")
        _spr[key] = np.asarray(im)
    _paste(img, _spr[key], 540 - _spr[key].shape[1] / 2, 64, a)
