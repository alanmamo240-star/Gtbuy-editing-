s=open("../v8/render8.py").read()
def between(a,b): i=s.index(a); j=s.index(b,i); return i,j
def rep(a,b):
    global s
    assert s.count(a)==1,a[:70]; s=s.replace(a,b)
rep('"""v8 talking-head edit','"""v13 haul edit (5 kg GTBuy haul, orange) — built from v8 by build13.py. Original v8 doc:\nv8 talking-head edit')
rep("from lib8 import *","from lib13 import *")
rep("BLUE = np.array([70, 125, 255], np.float32) / 255","BLUE = np.array([255, 140, 0], np.float32) / 255   # GTBuy orange (name kept from v8)")
rep("NSRC = 1012\nDUR = 36.4\nFREEZE = 1001                       # 33.37 s, after the last word","NSRC = 705\nDUR = 26.8\nFREEZE = 704")
rep("CUTS = [0, 399, 471, 660, NSRC]","CUTS = [0, 63, 240, 285, 330, 375, 420, 465, 510, 555, 600, 660, 690, NSRC]")
rep("        seg = np.interp(idx, idx[ok], seg[ok])","        seg = np.interp(idx, idx[ok], seg[ok]) if ok.any() else np.full(len(seg), 540.0, np.float32)")
i,j=between("CAM = [(0.00","# ------------------------------------------------------------------ typography")
s=s[:i]+'''CLIPS_T = [8.0, 9.5, 11.0, 12.5, 14.0, 15.5, 17.0, 18.5, 20.0, 22.0, 23.0]
def camera(i, t):
    if t < 2.10:
        s = 1.20 + 0.30 * (1 - ease_out(t / 0.5)) + 0.04 * t / 2.1
        x0 = clamp(FX[i] - 0.5 * W / s, 0, W - W / s); y0 = clamp(FY[i] - 0.40 * H / s, 0, H - H / s)
    elif t < 8.0:
        s = 1.10 + 0.07 * ease_io((t - 2.1) / 5.9) + 0.10 * (1 - ease_out((t - 2.1) / 0.4))
        x0 = clamp(FX[i] - 0.36 * W / s, 0, W - W / s); y0 = clamp(FY[i] - 0.44 * H / s, 0, H - H / s)
    else:
        t0 = max(c for c in CLIPS_T if c <= t)
        s = 1.04 + 0.10 * (1 - ease_out((t - t0) / 0.45)) + 0.02 * (t - t0)
        x0 = (W - W / s) / 2; y0 = (H - H / s) * 0.42
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])

'''+s[j:]
i,j=between("S = {}\nTHREE_M","def card(img, cw, ch")
s=s[:i]+'''S = {}
KG_M = tmask("5 KG", font("Unbounded", 250, 900), 6)[0]
S["haulw"] = sprite_fill(tmask("GTBUY HAUL", font("Archivo", 86, 900, 118), 6)[0], WHITE, shadow=0.0, stroke=(BLUE * 0.85, 7))
S["yalla"] = chip("YALLA!", bg=BLUE, fg=WHITE, size=64)
S["c40"] = chip("2× 40 %", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("2× 30 %", bg=BLUE, fg=WHITE, size=60)
S["aufship"] = chip("Auf Shipping", tick=True, size=42)
S["jetzt"] = sprite_fill(tmask("JETZT", font("Archivo", 130, 900, 125), 10)[0], BLUE, shadow=0.0, stroke=(INK, 6))
ANM_M = tmask("ANMELDEN", font("Unbounded", 94, 900), 2)[0]
S["detail"] = chip("Detail-Check", tick=True, size=52)
KGH_M = tmask("5 KG HAUL", font("Archivo", 140, 900, 118), 2)[0]
S["e1"] = chip("9 Teile  ·  über GTBuy", tick=True, size=42)
S["e2"] = chip("Coupons: 2× 40 %  +  2× 30 %", bg=BLUE, fg=WHITE, size=40)
S["link"] = link_card(size=52)
_lg = Image.open("img/gtbuy_logo.png").convert("RGBA")
def _logo(sz):
    arr = np.asarray(_lg.resize((sz, sz), Image.LANCZOS)).astype(np.float32) / 255; return arr[..., :3], arr[..., 3], (0, 0)
S["logo_s"] = _logo(150); S["logo_m"] = _logo(210)

'''+s[j:]
rep('IMG = {k: load_img(f"img/{k}.png") for k in ("coupons", "payment_clean", "warehouse", "delivery")}\nS["coupon_card"] = card(IMG["coupons"], 380, 470, None)\nS["pay_card"] = card(IMG["payment_clean"], 400, 500, None)',
    'S["haul_card"] = card(load_img("img/haulbox.png"), 400, 560, None)')
i,j=between("def stamp_sprite():","# ------------------------------------------------------------------ phone mock-up")
s=s[:i]+s[j:]
i,j=between("def phone_state(t):","# ------------------------------------------------------------------ captions")
s=s[:i]+'''def phone_state(t):
    if t < 3.55:
        z = 1 + 1.4 * ease_io((t - 2.75) / 0.35); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 2.75) / 0.35)
        return "profile", z, cy, ease_io((t - 2.9) / 0.25), (clamp((t - 3.15) / 0.3) if t >= 3.15 else -1), 0.0
    if t < 10.0:
        z = 1 + 0.9 * ease_io((t - 3.6) / 0.35); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 3.6) / 0.35)
        return "beacons", z, cy, ease_io((t - 3.8) / 0.25), (clamp((t - 4.1) / 0.3) if t >= 4.1 else -1), ease_out((t - 3.9) / 0.25)
    k = clamp((t - 24.8) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 25.1) / 0.3), (clamp((t - 25.4) / 0.4) if t >= 25.4 else -1), ease_out((t - 25.3) / 0.3)

'''+s[j:]
i,j=between("    rep = {\"Paypal,\"","KEY = {")
s=s[:i]+'''    if t_ == "GT": words.append(dict(w="GTBuy-Haul!", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    rep = {"Video": "Bio", "erhält": "erhaltet", "Fünf": "5"}
    words.append(dict(w=rep.get(t_, t_), s=w["s"], e=w["e"])); i += 1
'''+s[j:]
i,j=between("KEY = {","def clean(s)")
s=s[:i]+'KEY = {"5", "kilo", "gtbuy-haul", "yalla", "link", "bio", "coupons", "2× 40 %", "2× 30 %", "shipping", "jetzt"}\n'+s[j:]
rep('nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 33.9','nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 8.0')
rep("col = (120, 165, 255) if (active or (spoken and k)) else (255, 255, 255)","col = (255, 170, 60) if (active or (spoken and k)) else (255, 255, 255)")
i,j=between("def progress(t, L):","# ------------------------------------------------------------------ main")
s=s[:i]+open("scene13.py").read()+s[j:]
rep("    dx = 0.0\n    if 2.70 <= t < 2.82: dx = -ease_in((t - 2.70) / 0.12) * W * 0.55\n    if 2.82 <= t < 2.96: dx = (1 - ease_out((t - 2.82) / 0.14)) * W * 0.55","    dx = whip(t)")
rep("    if t >= 33.4:\n        k = ease_io((t - 33.4) / 0.5)","    if t >= 23.45:\n        k = ease_io((t - 23.45) / 0.5)")
rep("P_ = new_layer(); progress(t, P_); caption_layer(t, P_)","P_ = new_layer(); caption_layer(t, P_)")
open("render13.py","w").write(s)
print("built")
