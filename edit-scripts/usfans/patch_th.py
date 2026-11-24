"""Create USFans versions (render{N}_us.py) of the talking-head scripts v8, v9, v10, v12, v13.
Logo files: img/brand_logo.png (USFans logo from the creator). Screenshots: img/shot_profile.png / img/shot_beacons.png
(new USFans screenshots); highlight boxes come from hl_us.json if present."""
import re, json, os
S = "/tmp/claude-0/-home-user-Gtbuy-editing-/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/scratchpad"
common = open(f"{S}/us_common.py").read()
KLARNA = '''
KPINK = np.array([255, 179, 199], np.float32) / 255     # Klarna pink
_KI = Image.open("img/klarna_icon.png").convert("RGBA")   # Klarna app icon (pink square, black K.)
def klarna_icon(sz):
    arr = np.asarray(_KI.resize((sz, sz), Image.LANCZOS)).astype(np.float32) / 255; pad = 30
    a = np.pad(arr[..., 3], pad); rgb = np.pad(arr[..., :3], ((pad, pad), (pad, pad), (0, 0)))
    sh = cv2.GaussianBlur(np.roll(a, 10, 0), (0, 0), 12) * 0.45; A_ = a + sh * (1 - a)
    return rgb * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
def klarna_chip(text="Klarna", size=48):
    """dark pill, Klarna app icon on the left, pink text"""
    f = font("Archivo", size, 900, 112); ic = int(size * 1.45); ph = int(size * 1.9); pad = 40
    pw = int(14 + ic + 18 + f.getlength(text) + 34)
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], ph // 2, fill=(18, 14, 16, 238))
    im.alpha_composite(_KI.resize((ic, ic), Image.LANCZOS), (pad + 14, pad + (ph - ic) // 2))
    d.text((pad + 14 + ic + 18, pad + ph / 2), text, font=f, fill=(255, 179, 199, 255), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255; a = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(a, 12, 0), (0, 0), 14) * 0.45; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
'''
DROP = {"v8": [6.66, 7.60, 10.00, 10.84, 27.32, 31.96], "v9": [16.22, 17.52, 20.50, 21.40],
        "v10": [21.08, 22.68, 24.62, 25.92], "v12": [2.24, 8.72, 9.68], "v13": [4.48, 5.46]}
FILES = {"v8": "render8.py", "v9": "render9.py", "v10": "render10.py", "v12": "render12.py", "v13": "render13.py"}
for v, fn in FILES.items():
    s = open(f"{S}/{v}/{fn}").read()
    def rep(a, b, n=1):
        global s
        c = s.count(a)
        assert c == n, (v, a[:80], c)
        s = s.replace(a, b)
    # brand name everywhere in on-screen text
    s = s.replace('"GTBuy"', '"USFans"').replace("für GTBuy", "für USFans").replace("über GTBuy", "über USFans")
    s = s.replace('img/gtbuy_logo.png', 'img/brand_logo.png')
    # offer numbers out of the picture
    s = re.sub(r'S\["c40"\] = chip\("2× 40 %", bg=BLUE, fg=WHITE, size=60\); S\["c30"\] = chip\("2× 30 %", bg=BLUE, fg=WHITE, size=60\)',
               'S["c40"] = chip("Coupons", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("Über meinen Link", bg=BLUE, fg=WHITE, size=52)', s)
    if 'S["three_w"]' in s:
        s = re.sub(r'S\["three_w"\] = sprite_fill\(tmask\("3".*\n', 'S["three_w"] = (np.zeros((4, 4, 3), np.float32), np.zeros((4, 4), np.float32), (0, 0))\n', s)
        s = s.replace('FOUR_M = tmask("4", font("Unbounded", 380, 900))[0]', 'FOUR_M = tmask("+", font("Unbounded", 380, 900))[0]')
        s = s.replace("def strike(L, x0, y0, x1, y1, prog, alpha):\n    if prog <= 0: return", "def strike(L, x0, y0, x1, y1, prog, alpha):\n    return")
    # captions: brand swap + drop spoken offer numbers
    i = s.index("KEY = {")
    s = s[:i] + common + KLARNA + f"words = _us_words(words, {DROP[v]})\n" + s[i:]
    s = s.replace("KEY = {", 'KEY = {"usfans", "klarna", "usfans-haul", "klarna-user", ', 1)
    if v == "v8":
        rep('S["paypal"] = chip("PayPal", tick=True, size=48)', 'S["paypal"] = klarna_chip("Klarna", 48)')
        rep('TAGE67_M = tmask("6–7 TAGE", font("Archivo", 170, 900, 118), 2)[0]', 'TAGE67_M = tmask("SCHNELL", font("Archivo", 170, 900, 118), 2)[0]')
        rep('TAGE13_M = tmask("1–3 TAGE", font("Archivo", 170, 900, 118), 2)[0]', 'TAGE13_M = tmask("WAREHOUSE", font("Archivo", 132, 900, 112), 2)[0]')
        rep('    subs = ["", "1–3 Tage", "6–7 Tage", ""]', '    subs = ["", "", "", ""]')
        # klarna_chip is defined after the sprite block -> move the definition up
        s = s.replace(KLARNA, "")
        s = s.replace("S = {}\n", "S = {}\n" + KLARNA, 1)
    if v == "v9":
        rep("SKY = np.array([0, 156, 222], np.float32) / 255", "SKY = np.array([255, 168, 205], np.float32) / 255   # Klarna-style pink")
        rep("NAVY = np.array([0, 48, 135], np.float32) / 255", "NAVY = np.array([28, 20, 36], np.float32) / 255")
        rep('S["paypal_big"] = sprite_fill(tmask("PayPal", font("Archivo", 230, 900, 118), 2)[0], WHITE, shadow=0.0, stroke=(NAVY, 9))',
            'S["paypal_big"] = sprite_fill(tmask("Klarna.", font("Archivo", 230, 900, 118), 2)[0], SKY, shadow=0.0, stroke=(NAVY, 9))')
        rep('S["pp2"] = sprite_fill(tmask("PayPal", font("InstrumentSerif-Italic", 150))[0], WHITE, shadow=0.6, sblur=12)',
            'S["pp2"] = sprite_fill(tmask("Klarna", font("InstrumentSerif-Italic", 150))[0], WHITE, shadow=0.6, sblur=12)')
        rep('S["seit"] = chip("Schon seit Monaten", tick=True, size=46)', 'S["seit"] = klarna_chip("Jetzt mit Klarna", 46)')
        rep('S["versand_l"] = chip("Versand  ·  PayPal", bg=BLUE, fg=WHITE, size=40)', 'S["versand_l"] = klarna_chip("Versand  ·  Klarna", 40)')
        rep('S["produkt_l"] = chip("Produkte  ·  PayPal", bg=BLUE, fg=WHITE, size=40)', 'S["produkt_l"] = klarna_chip("Produkte  ·  Klarna", 40)')
        rep('txt = "NEWS   •   GTBUY × PAYPAL   •   "', 'txt = "NEWS   •   USFANS × KLARNA   •   "')
        rep("def calendar(t, L, x, y, a):\n", "def calendar(t, L, x, y, a):\n    return\n")
        s = s.replace(KLARNA, ""); s = s.replace("S = {}\n", "S = {}\n" + KLARNA + 'S["kicon"] = klarna_icon(210); S["kicon_s"] = klarna_icon(120)\n', 1)
        rep('        place(front, S["paypal_big"], W / 2, 1180, s=back_out((t - 1.78) / 0.4, 2.0), rot=-4, alpha=a)\n',
            '        place(front, S["paypal_big"], W / 2, 1180, s=back_out((t - 1.78) / 0.4, 2.0), rot=-4, alpha=a)\n'
            '        place(front, S["kicon"], W / 2, 960, s=back_out((t - 1.70) / 0.4, 2.2), rot=6, alpha=a)\n')
        rep('        k3 = ease_out((t - 3.30) / 0.5); place(back, S["pp2"], 815 + (1 - k3) * 200, 300, alpha=a * k3)\n',
            '        k3 = ease_out((t - 3.30) / 0.5); place(back, S["pp2"], 815 + (1 - k3) * 200, 300, alpha=a * k3)\n'
            '        place(back, S["kicon_s"], 815 + (1 - k3) * 200, 160, s=back_out((t - 3.45) / 0.35, 2.0), rot=-6, alpha=a * k3)\n')
        rep('GTB_M = tmask("USFans", font("Unbounded", 112, 900), 2)[0]', 'GTB_M = tmask("USFans", font("Unbounded", 100, 900), 2)[0]')
    if v == "v12":
        rep('S["hooklab"] = chip("HAUL  ·  NACH HAUSE IN", size=38)', 'S["hooklab"] = chip("HAUL  ·  SCHNELL NACH HAUSE", size=38)')
        rep('SEVEN_M = tmask("7", font("Unbounded", 600, 900))[0]', 'SEVEN_M = tmask("SCHNELL", font("Unbounded", 150, 900), 4)[0]')
        rep('S["tage"] = sprite_fill(tmask("TAGEN", font("Archivo", 118, 900, 118), 4)[0]', 'S["tage"] = sprite_fill(tmask("ZUHAUSE", font("Archivo", 118, 900, 118), 4)[0]')
        rep('IN7_M = tmask("IN 7 TAGEN", font("Archivo", 130, 900, 118), 2)[0]', 'IN7_M = tmask("SCHNELL ZU DIR", font("Archivo", 112, 900, 112), 2)[0]')
        rep("    day = 1 + int(min(prog, 0.999) * 7)\n", "")
        rep('    d.text((pw - 112, 52), "TAG", font=font("SpaceGrotesk", 30, 700), fill=VIO_L + (255,), anchor="mm")\n', "")
        rep('    d.text((pw - 112, 110), str(day), font=font("Unbounded", 76, 900), fill=(255, 255, 255, 255), anchor="mm")\n', "")
        rep('    if k1 > 0.9: d.text((40 + 350 + 18, 93), "7 Tage", font=f2, fill=(255, 255, 255, 255), anchor="lm")',
            '    if k1 > 0.9: d.text((40 + 350 + 18, 93), "schnell", font=f2, fill=(255, 255, 255, 255), anchor="lm")')
        s = re.sub(r'place\(back, chrome_cached\("seven", SEVEN_M, 24, (.*?)\), 235, 400, s=1.5 - 0.5 \* k,', r'place(back, chrome_cached("seven", SEVEN_M, 24, \1), W / 2, 300, s=1.5 - 0.5 * k,', s)
        rep('place(back, S["tage"], 775 + (1 - k2) * 200, 330, alpha=a * k2)', 'place(back, S["tage"], W / 2 + (1 - k2) * 200, 460, alpha=a * k2)')
    if v == "v13":
        rep('S["haulw"] = sprite_fill(tmask("GTBUY HAUL"', 'S["haulw"] = sprite_fill(tmask("USFANS HAUL"')
        rep('S["e2"] = chip("Coupons: 2× 40 %  +  2× 30 %", bg=BLUE, fg=WHITE, size=40)', 'S["e2"] = chip("Coupons über meinen Link", bg=BLUE, fg=WHITE, size=40)')
    # new screenshot highlight boxes
    if os.path.exists(f"{S}/hl_us.json"):
        hl = json.load(open(f"{S}/hl_us.json"))
        s = re.sub(r'HL = \{"profile": \(.*?\), "beacons": \(.*?\)\}', f'HL = {{"profile": {tuple(hl["profile"])}, "beacons": {tuple(hl["beacons"])}}}', s)
        s = re.sub(r"SW_, SH_ = \d+, \d+", f"SW_, SH_ = {hl['size'][0]}, {hl['size'][1]}", s)
    left = [l.strip()[:100] for l in s.splitlines() if re.search(r'gtbuy|paypal|2× 40|2× 30|"6–7|"1–3', l, re.I)
            and not l.strip().startswith(("#", '"""', "v8 talking", "if t_", "rep =", "for a, b", "KEY", "txt", "words.append"))]
    open(f"{S}/{v}/{fn.replace('.py', '_us.py')}", "w").write(s)
    print(v, "ok; leftover:", left[:6])
for lib in ("v8/lib8.py", "v9/lib8.py", "v10/lib10.py", "v12/lib12.py", "v13/lib13.py"):
    p = f"{S}/{lib}"
    if os.path.exists(p):
        t = open(p).read().replace('sub="1. Link  →  GTBuy"', 'sub="1. Link  →  USFans"'); open(p, "w").write(t)
