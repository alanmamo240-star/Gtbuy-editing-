s=open("../v8/render8.py").read()
def between(a,b): i=s.index(a); j=s.index(b,i); return i,j
def rep(a,b):
    global s
    assert s.count(a)==1,a[:70]; s=s.replace(a,b)
rep('"""v8 talking-head edit','"""v9 talking-head edit (PayPal news) — built from v8 by build9.py. Original v8 doc:\nv8 talking-head edit')
rep("NSRC = 1012\nDUR = 36.4\nFREEZE = 1001                       # 33.37 s, after the last word",
    "NSRC = 705\nDUR = 25.9\nFREEZE = 688                        # 22.93 s, after the last word")
rep("CUTS = [0, 399, 471, 660, NSRC]","CUTS = [0, 403, NSRC]")
i,j=between("CAM = [(0.00","# ------------------------------------------------------------------ typography")
s=s[:i]+'''CAM = [(0.00, 2.70, 1.08, 1.12), (2.70, 6.60, 1.10, 1.14), (6.60, 12.40, 1.04, 1.08), (12.40, 13.24, 1.10, 1.12),
       (13.24, 18.90, 1.06, 1.09), (18.90, 40.0, 1.10, 1.15)]
def tx_at(t):   # where the face sits horizontally on screen (fraction of W)
    k = max(win(t, 13.55, 16.25, 0.4, 0.4), win(t, 19.9, 22.9, 0.4, 0.3))
    return 0.5 - 0.10 * k
def camera(i, t):
    s = 1.1
    for k, (a, b, s0, s1) in enumerate(CAM):
        if a <= t < b:
            s = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0: prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.45)
            break
    if t < 0.5: s += 0.30 * (1 - ease_out(t / 0.5))
    if 22.10 <= t < 22.45: s *= 1 + 0.05 * math.exp(-(t - 22.10) / 0.08)
    x0 = clamp(FX[i] - tx_at(t) * W / s, 0, W - W / s)
    y0 = clamp(FY[i] - 0.47 * H / s, 0, H - H / s) * 0.6 + (H / 2 - H / (2 * s)) * 0.4
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])

'''+s[j:]
i,j=between("S = {}\nTHREE_M","def card(img, cw, ch")
s=s[:i]+'''S = {}
SKY = np.array([0, 156, 222], np.float32) / 255
NAVY = np.array([0, 48, 135], np.float32) / 255
NEWS_M = tmask("NEWS", font("Unbounded", 225, 900), 10)[0]
S["paypal_big"] = sprite_fill(tmask("PayPal", font("Archivo", 230, 900, 118), 2)[0], WHITE, shadow=0.0, stroke=(NAVY, 9))
S["users"] = sprite_fill(tmask("FÜR ALLE USER", font("SpaceGrotesk", 42, 700), 12)[0], SKY, shadow=0.0, stroke=(INK, 3))
GTB_M = tmask("GTBuy", font("Unbounded", 112, 900), 2)[0]
S["x"] = sprite_fill(tmask("×", font("Archivo", 130, 500, 100))[0], SKY, shadow=0.5, sblur=10)
S["pp2"] = sprite_fill(tmask("PayPal", font("InstrumentSerif-Italic", 150))[0], WHITE, shadow=0.6, sblur=12)
S["seit"] = chip("Schon seit Monaten", tick=True, size=46)
S["versand_l"] = chip("Versand  ·  PayPal", bg=BLUE, fg=WHITE, size=40)
S["produkt_l"] = chip("Produkte  ·  PayPal", bg=BLUE, fg=WHITE, size=40)
S["bezahlen"] = sprite_fill(tmask("BEZAHLEN", font("Archivo", 132, 900, 118), 4)[0], WHITE, shadow=0.0, stroke=(NAVY, 8))
S["c40"] = chip("2× 40 %", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("2× 30 %", bg=BLUE, fg=WHITE, size=60)
S["aufship"] = sprite_fill(tmask("AUF SHIPPING", font("SpaceGrotesk", 38, 700), 9)[0], SKY, shadow=0.0, stroke=(INK, 3))
S["three_w"] = sprite_fill(tmask("3", font("Archivo", 300, 900, 110))[0], WHITE, shadow=0.6, sblur=14)
FOUR_M = tmask("4", font("Unbounded", 380, 900))[0]
S["coupons_l"] = sprite_fill(tmask("COUPONS", font("SpaceGrotesk", 56, 700), 12)[0], BLUE, shadow=0.0, stroke=(INK, 3))
S["link"] = link_card(size=52)
S["cta1"] = sprite_fill(tmask("1. LINK", font("Archivo", 150, 900, 125), 2)[0], BLUE, shadow=0.0, stroke=(INK, 7))
S["cta2"] = sprite_fill(tmask("in meiner Bio", font("InstrumentSerif-Italic", 120))[0], WHITE, shadow=0.6, sblur=10)

'''+s[j:]
rep('IMG = {k: load_img(f"img/{k}.png") for k in ("coupons", "payment_clean", "warehouse", "delivery")}\nS["coupon_card"] = card(IMG["coupons"], 380, 470, None)\nS["pay_card"] = card(IMG["payment_clean"], 400, 500, None)',
    'IMG = {k: load_img(f"img/{k}.png") for k in ("coupons", "payment_clean", "warehouse", "haul")}\nS["coupon_card"] = card(IMG["coupons"], 360, 450, None)\nS["ship_card"] = card(IMG["warehouse"], 360, 470, None)\nS["prod_card"] = card(IMG["haul"], 360, 470, None)\nS["pay_card"] = card(IMG["payment_clean"], 330, 410, None)')
rep('d.text((c, c), "EXKLUSIV"','d.text((c, c), "NUR HIER"')
i,j=between("def phone_state(t):","# ------------------------------------------------------------------ captions")
s=s[:i]+'''def phone_state(t):
    if t < 15.0:
        z = 1 + 1.4 * ease_io((t - 14.05) / 0.45); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 14.05) / 0.45)
        return "profile", z, cy, ease_io((t - 14.25) / 0.3), (clamp((t - 14.55) / 0.35) if t >= 14.55 else -1), 0.0
    if t < 20.0:
        z = 1 + 0.9 * ease_io((t - 15.05) / 0.45); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 15.05) / 0.45)
        return "beacons", z, cy, ease_io((t - 15.3) / 0.3), (clamp((t - 15.65) / 0.35) if t >= 15.65 else -1), ease_out((t - 15.45) / 0.3)
    k = clamp((t - 23.7) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 24.0) / 0.3), (clamp((t - 24.4) / 0.4) if t >= 24.4 else -1), ease_out((t - 24.2) / 0.3)

'''+s[j:]
i,j=between("    rep = {\"Paypal,\"","KEY = {")
s=s[:i]+'''    if t_ == "Paypal" and raw[i + 1]["w"] == "-User,": words.append(dict(w="PayPal-User,", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    rep = {"Paypal": "PayPal", "GTbuy": "GTBuy", "Büro": "Bio", "erhält": "erhaltet"}
    words.append(dict(w=rep.get(t_, t_), s=w["s"], e=w["e"])); i += 1
'''+s[j:]
i,j=between("KEY = {","def clean(s)")
s=s[:i]+'''KEY = {"neuigkeiten", "paypal-user", "gtbuy", "paypal", "monaten", "versand", "produktbestellung", "bezahlen", "link", "bio",
       "coupons", "2× 40 %", "2× 30 %", "shipping", "3", "4"}
'''+s[j:]
rep('nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 33.9','nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 23.2')
i,j=between("def progress(t, L):","# ------------------------------------------------------------------ main")
s=s[:i]+open("scene9.py").read()+s[j:]
rep("    if 2.70 <= t < 2.82: dx = -ease_in((t - 2.70) / 0.12) * W * 0.55\n    if 2.82 <= t < 2.96: dx = (1 - ease_out((t - 2.82) / 0.14)) * W * 0.55",
    "    if 13.12 <= t < 13.24: dx = -ease_in((t - 13.12) / 0.12) * W * 0.55\n    if 13.24 <= t < 13.38: dx = (1 - ease_out((t - 13.24) / 0.14)) * W * 0.55")
rep("    if t >= 33.4:\n        k = ease_io((t - 33.4) / 0.5)","    if t >= 22.95:\n        k = ease_io((t - 22.95) / 0.5)")
rep("P_ = new_layer(); progress(t, P_); caption_layer(t, P_)","P_ = new_layer(); ticker(t, P_); caption_layer(t, P_)")
open("render9.py","w").write(s)
print("built")
