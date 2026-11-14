s=open("../v8/render8.py").read()
def between(a,b): i=s.index(a); j=s.index(b,i); return i,j
def rep(a,b):
    global s
    assert s.count(a)==1,a[:70]; s=s.replace(a,b)
rep('"""v8 talking-head edit','"""v12 talking-head edit (Haul in 7 Tagen, violet) — built from v8 by build12.py. Original v8 doc:\nv8 talking-head edit')
rep("from lib8 import *","from lib12 import *")
rep("BLUE = np.array([70, 125, 255], np.float32) / 255","BLUE = np.array([140, 92, 255], np.float32) / 255   # violet accent (name kept from v8)")
rep("NSRC = 1012\nDUR = 36.4\nFREEZE = 1001                       # 33.37 s, after the last word",
    "NSRC = 784\nDUR = 29.0\nFREEZE = 778                        # 25.93 s")
rep("CUTS = [0, 399, 471, 660, NSRC]","CUTS = [0, 130, 333, 478, 648, NSRC]")
i,j=between("CAM = [(0.00","# ------------------------------------------------------------------ typography")
s=s[:i]+'''CAM = [(0.00, 4.33, 1.08, 1.13), (4.33, 11.10, 1.06, 1.10), (11.10, 15.93, 1.08, 1.12), (15.93, 21.60, 1.05, 1.09),
       (21.60, 40.0, 1.17, 1.21)]
def tx_at(t):
    k = max(win(t, 5.45, 11.0, 0.4, 0.3), win(t, 11.85, 14.35, 0.35, 0.35), win(t, 16.15, 21.55, 0.4, 0.2))
    return 0.5 - 0.10 * k
def camera(i, t):
    s = 1.1
    for k, (a, b, s0, s1) in enumerate(CAM):
        if a <= t < b:
            s = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0 and a != 21.60: prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.45)
            break
    if t < 0.5: s += 0.30 * (1 - ease_out(t / 0.5))
    x0 = clamp(FX[i] - tx_at(t) * W / s, 0, W - W / s)
    y0 = clamp(FY[i] - 0.47 * H / s, 0, H - H / s) * 0.6 + (H / 2 - H / (2 * s)) * 0.4
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])

'''+s[j:]
i,j=between("S = {}\nTHREE_M","def card(img, cw, ch")
s=s[:i]+'''S = {}
S["hooklab"] = chip("HAUL  ·  NACH HAUSE IN", size=38)
SEVEN_M = tmask("7", font("Unbounded", 600, 900))[0]
S["tage"] = sprite_fill(tmask("TAGEN", font("Archivo", 118, 900, 118), 4)[0], WHITE, shadow=0.0, stroke=(BLUE * 0.8, 7))
for n in ("01", "02"): S["n" + n] = sprite_outline(tmask(n, font("Unbounded", 170, 900))[0], WHITE, 4)
ACC_M = tmask("ACCOUNT", font("Archivo", 150, 900, 118), 2)[0]
S["c40"] = chip("2× 40 %", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("2× 30 %", bg=BLUE, fg=WHITE, size=60)
S["aufship"] = chip("Auf Shipping", tick=True, size=42)
S["nurkl"] = chip("Nur Klamotten?", size=44)
S["keine"] = sprite_fill(tmask("KEINE", font("Archivo", 130, 900, 125), 8)[0], WHITE, shadow=0.0, stroke=(INK, 6))
EXTRAS_M = tmask("EXTRAS", font("Unbounded", 150, 900), 4)[0]
S["nicht"] = sprite_fill(tmask("NICHT", font("Archivo", 120, 900, 125), 10)[0], CORAL, shadow=0.0, stroke=(INK, 6))
KOMB_M = tmask("KOMBINIEREN", font("Archivo", 108, 900, 108), 2)[0]
S["pluszeit"] = chip("+ Zeit", bg=CORAL, fg=WHITE, size=46)
S["mehrzeit"] = sprite_outline(tmask("MEHR ZEIT", font("Unbounded", 110, 900), 4)[0], WHITE, 4)
XS_M = tmask("EXTRA", font("Unbounded", 170, 900), 6)[0]
S["services"] = sprite_fill(tmask("Services", font("InstrumentSerif-Italic", 170))[0], WHITE, shadow=0.6, sblur=12)
IN7_M = tmask("IN 7 TAGEN", font("Archivo", 130, 900, 118), 2)[0]
S["link"] = link_card(size=52)
_lg = Image.open("img/gtbuy_logo.png").convert("RGBA")
def _logo(sz):
    arr = np.asarray(_lg.resize((sz, sz), Image.LANCZOS)).astype(np.float32) / 255; return arr[..., :3], arr[..., 3], (0, 0)
S["logo_s"] = _logo(170); S["logo_m"] = _logo(210)

'''+s[j:]
rep('IMG = {k: load_img(f"img/{k}.png") for k in ("coupons", "payment_clean", "warehouse", "delivery")}\nS["coupon_card"] = card(IMG["coupons"], 380, 470, None)\nS["pay_card"] = card(IMG["payment_clean"], 400, 500, None)',
    'S["haul_card"] = card(load_img("img/haul.png"), 360, 460, None)')
i,j=between("def stamp_sprite():","# ------------------------------------------------------------------ phone mock-up")
s=s[:i]+s[j:]
i,j=between("def phone_state(t):","# ------------------------------------------------------------------ captions")
s=s[:i]+'''def phone_state(t):
    if t < 6.80:
        z = 1 + 1.4 * ease_io((t - 5.90) / 0.4); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 5.90) / 0.4)
        return "profile", z, cy, ease_io((t - 6.05) / 0.3), (clamp((t - 6.35) / 0.35) if t >= 6.35 else -1), 0.0
    if t < 20.0:
        z = 1 + 0.9 * ease_io((t - 6.85) / 0.4); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 6.85) / 0.4)
        return "beacons", z, cy, ease_io((t - 7.05) / 0.3), (clamp((t - 7.40) / 0.35) if t >= 7.40 else -1), ease_out((t - 7.15) / 0.3)
    k = clamp((t - 27.2) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 27.5) / 0.3), (clamp((t - 27.8) / 0.4) if t >= 27.8 else -1), ease_out((t - 27.7) / 0.3)

'''+s[j:]
i,j=between("    rep = {\"Paypal,\"","KEY = {")
s=s[:i]+'''    if t_ == "BioingTiBa":
        words += [dict(w="Bio", s=6.44, e=6.72), dict(w="einen", s=6.72, e=6.90), dict(w="GTBuy", s=6.90, e=7.34)]; i += 1; continue
    if t_ == "240": words.append(dict(w="2× 40 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "230": words.append(dict(w="2× 30 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    rep = {"erhält": "erhaltet", "Extraservices": "Extra-Services"}
    words.append(dict(w=rep.get(t_, t_), s=w["s"], e=w["e"])); i += 1
'''+s[j:]
i,j=between("KEY = {","def clean(s)")
s=s[:i]+'''KEY = {"hauls", "7", "tagen", "hause", "1", "link", "bio", "gtbuy", "2× 40 %", "2× 30 %", "shipping", "2", "klamotten",
       "extras", "paket", "zeit", "extra-services", "paketen"}
'''+s[j:]
rep('nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 33.9','nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 26.2')
i,j=between("def progress(t, L):","# ------------------------------------------------------------------ main")
s=s[:i]+open("scene12.py").read()+s[j:]
rep("    if 2.70 <= t < 2.82: dx = -ease_in((t - 2.70) / 0.12) * W * 0.55\n    if 2.82 <= t < 2.96: dx = (1 - ease_out((t - 2.82) / 0.14)) * W * 0.55",
    "    if 4.21 <= t < 4.33: dx = -ease_in((t - 4.21) / 0.12) * W * 0.55\n    if 4.33 <= t < 4.47: dx = (1 - ease_out((t - 4.33) / 0.14)) * W * 0.55")
rep("    comp = cf * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])",
    "    base = bg_replace(t, cf, cm)\n    comp = base * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])\n    comp = outline_fx(t, comp, cm)")
rep("    if t >= 33.4:\n        k = ease_io((t - 33.4) / 0.5)","    if t >= 25.95:\n        k = ease_io((t - 25.95) / 0.5)")
rep("P_ = new_layer(); progress(t, P_); caption_layer(t, P_)","P_ = new_layer(); caption_layer(t, P_)")
open("render12.py","w").write(s)
print("built")
