"""Re-brand a render script's end card from USFans to Litbuy: Litbuy pill instead of the USFans logo, Litbuy flame icon
instead of the USFans mascot, and a plain 'LINK IN BIO' chip (the USFans coupon line is dropped).
usage: python3 litbuy_patch.py <render.py>"""
import sys
p = sys.argv[1]; s = open(p).read()
def R(a, b):
    global s
    assert a in s, a[:60]; s = s.replace(a, b)
R("MASC = end_card_sprite()", """MASC = end_card_sprite()
def _lit(path, shadow=True):
    im = Image.open(path).convert("RGBA"); return T.shadow(pil2np(im), 24, 0, 18, 0.5) if shadow else pil2np(im)
LOGO_P = _lit("img/litbuy_pill.png")
MASC = _lit("img/litbuy_icon.png")""")
R('CHIP_END = chip("1. LINK IN BIO  ·  40% + 30% SHIPPING", OR, WHITE, 30)', 'CHIP_END = chip("LINK IN BIO  ↑", (240, 140, 50), WHITE, 34)')
open(p, "w").write(s); print("litbuy end card:", p)
