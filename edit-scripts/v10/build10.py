s=open("../v8/render8.py").read()
def between(a,b): i=s.index(a); j=s.index(b,i); return i,j
def rep(a,b):
    global s
    assert s.count(a)==1,a[:70]; s=s.replace(a,b)
rep('"""v8 talking-head edit','"""v10 talking-head edit (Winter-Haul vakuumieren, GTBuy orange) — built from v8 by build10.py. Original v8 doc:\nv8 talking-head edit')
rep("from lib8 import *","from lib10 import *")
rep("BLUE = np.array([70, 125, 255], np.float32) / 255","BLUE = np.array([255, 140, 0], np.float32) / 255   # GTBuy orange (name kept from v8)")
rep("NSRC = 1012\nDUR = 36.4\nFREEZE = 1001                       # 33.37 s, after the last word",
    "NSRC = 1088\nDUR = 38.9\nFREEZE = 1074                       # 35.80 s")
rep("CUTS = [0, 399, 471, 660, NSRC]","CUTS = [0, 323, NSRC]")
i,j=between("CAM = [(0.00","# ------------------------------------------------------------------ typography")
s=s[:i]+'''CAM = [(0.00, 3.85, 1.08, 1.12), (3.85, 7.25, 1.12, 1.16), (7.25, 10.80, 1.05, 1.08), (10.80, 13.35, 1.08, 1.12),
       (13.35, 17.50, 1.06, 1.10), (17.50, 19.55, 1.12, 1.16), (19.55, 28.50, 1.06, 1.09), (28.50, 40.0, 1.08, 1.13)]
def tx_at(t):
    k = max(win(t, 11.0, 13.1, 0.35, 0.35), win(t, 14.2, 17.4, 0.35, 0.35), win(t, 19.5, 22.6, 0.4, 0.4),
            win(t, 24.4, 28.5, 0.4, 0.3), win(t, 30.4, 35.8, 0.4, 0.3))
    return 0.5 - 0.10 * k
def camera(i, t):
    s = 1.1
    for k, (a, b, s0, s1) in enumerate(CAM):
        if a <= t < b:
            s = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0: prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.45)
            break
    if t < 0.5: s += 0.30 * (1 - ease_out(t / 0.5))
    if 27.80 <= t < 28.15: s *= 1 + 0.05 * math.exp(-(t - 27.80) / 0.08)
    x0 = clamp(FX[i] - tx_at(t) * W / s, 0, W - W / s)
    y0 = clamp(FY[i] - 0.47 * H / s, 0, H - H / s) * 0.6 + (H / 2 - H / (2 * s)) * 0.4
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])

'''+s[j:]
i,j=between("S = {}\nTHREE_M","def card(img, cw, ch")
s=s[:i]+'''S = {}
S["winter"] = sprite_fill(tmask("WINTER", font("Unbounded", 120, 900), 14)[0], WHITE, shadow=0.0, stroke=(np.array([0.45, 0.7, 1.0], np.float32), 5))
HAUL_M = tmask("HAUL", font("Archivo", 250, 900, 125), 6)[0]
S["guenstiger"] = chip("Günstiger als zuvor", bg=BLUE, fg=WHITE, size=54)
S["sparst"] = sprite_fill(tmask("GESPART", font("SpaceGrotesk", 48, 700), 14)[0], BLUE, shadow=0.0, stroke=(INK, 3))
S["teurer"] = chip("Größer = teurer", size=42)
S["winterhauls"] = chip("Für Winter-Hauls", tick=True, size=42)
VAK_M = tmask("VAKUUMIEREN", font("Archivo", 98, 900, 108), 2)[0]
S["agent"] = sprite_fill(tmask("Als Agent:", font("InstrumentSerif-Italic", 120))[0], WHITE, shadow=0.6, sblur=12)
S["c40"] = chip("2× 40 %", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("2× 30 %", bg=BLUE, fg=WHITE, size=60)
S["aufship"] = chip("Auf Shipping", tick=True, size=42)
S["three_w"] = sprite_fill(tmask("3", font("Archivo", 300, 900, 110))[0], WHITE, shadow=0.6, sblur=14)
FOUR_M = tmask("4", font("Unbounded", 380, 900))[0]
S["coupons_l"] = sprite_fill(tmask("COUPONS", font("SpaceGrotesk", 56, 700), 12)[0], BLUE, shadow=0.0, stroke=(INK, 3))
S["link"] = link_card(size=52)
S["cta1"] = sprite_fill(tmask("1. LINK", font("Archivo", 150, 900, 125), 2)[0], BLUE, shadow=0.0, stroke=(INK, 7))
S["cta2"] = sprite_fill(tmask("in meiner Bio", font("InstrumentSerif-Italic", 120))[0], WHITE, shadow=0.6, sblur=10)

'''+s[j:]
rep('IMG = {k: load_img(f"img/{k}.png") for k in ("coupons", "payment_clean", "warehouse", "delivery")}\nS["coupon_card"] = card(IMG["coupons"], 380, 470, None)\nS["pay_card"] = card(IMG["payment_clean"], 400, 500, None)',
    'IMG_FS = {k: load_img(f"img/{k}.png") for k in ("winterhaul", "vacuum")}\nS["coupon_card"] = card(load_img("img/coupons.png"), 340, 420, None)')
rep('d.text((c, c), "EXKLUSIV"','d.text((c, c), "NUR HIER"')
i,j=between("def phone_state(t):","# ------------------------------------------------------------------ captions")
s=s[:i]+'''def phone_state(t):
    if t < 20.95:
        z = 1 + 1.4 * ease_io((t - 20.0) / 0.45); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 20.0) / 0.45)
        return "profile", z, cy, ease_io((t - 20.2) / 0.3), (clamp((t - 20.5) / 0.35) if t >= 20.5 else -1), 0.0
    if t < 30.0:
        z = 1 + 0.9 * ease_io((t - 21.0) / 0.45); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 21.0) / 0.45)
        return "beacons", z, cy, ease_io((t - 21.25) / 0.3), (clamp((t - 21.6) / 0.35) if t >= 21.6 else -1), ease_out((t - 21.4) / 0.3)
    k = clamp((t - 36.8) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 37.1) / 0.3), (clamp((t - 37.4) / 0.4) if t >= 37.4 else -1), ease_out((t - 37.3) / 0.3)

'''+s[j:]
i,j=between("    rep = {\"Paypal,\"","KEY = {")
s=s[:i]+'''    if t_ == "Das" and raw[i + 1]["w"] == "Agent": words.append(dict(w="Als", s=w["s"], e=w["e"])); i += 1; continue
    if t_ == "die" and raw[i + 1]["w"] == "T" and raw[i + 2]["w"] == "-Buy":
        words.append(dict(w="GTBuy", s=raw[i + 1]["s"], e=raw[i + 2]["e"])); i += 3; continue
    if t_ == "2x" and raw[i + 1]["w"] in ("40", "30"): words.append(dict(w=f"2× {raw[i + 1]['w']} %", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    rep = {"erhält": "erhaltet", "Vakuminium": "Vakuumieren", "Haul": "Haul"}
    words.append(dict(w=rep.get(t_, t_), s=w["s"], e=w["e"])); i += 1
'''+s[j:]
i,j=between("KEY = {","def clean(s)")
s=s[:i]+'''KEY = {"winter", "haul", "günstiger", "50", "100", "euro", "gewicht", "volumen", "paket", "teurer", "vakuumieren", "gtbuy",
       "link", "bio", "2× 40 %", "2× 30 %", "coupons", "3", "4", "shipping", "kleiner", "kompakter", "hauls"}
'''+s[j:]
rep('nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 33.9','nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 34.6')
rep("col = (120, 165, 255) if (active or (spoken and k)) else (255, 255, 255)","col = (255, 170, 60) if (active or (spoken and k)) else (255, 255, 255)")
i,j=between("def progress(t, L):","# ------------------------------------------------------------------ main")
s=s[:i]+open("scene10.py").read()+s[j:]
rep("    if 2.70 <= t < 2.82: dx = -ease_in((t - 2.70) / 0.12) * W * 0.55\n    if 2.82 <= t < 2.96: dx = (1 - ease_out((t - 2.82) / 0.14)) * W * 0.55",
    "    if 10.66 <= t < 10.78: dx = -ease_in((t - 10.66) / 0.12) * W * 0.55\n    if 10.78 <= t < 10.92: dx = (1 - ease_out((t - 10.78) / 0.14)) * W * 0.55")
rep("    if t >= 33.4:\n        k = ease_io((t - 33.4) / 0.5)","    if t >= 35.82:\n        k = ease_io((t - 35.82) / 0.5)")
rep("P_ = new_layer(); progress(t, P_); caption_layer(t, P_)","P_ = new_layer(); caption_layer(t, P_)")
open("render10.py","w").write(s)
print("built")
