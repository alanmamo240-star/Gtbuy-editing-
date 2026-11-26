#!/bin/bash
# usage: prev.sh <dir> "src1,src2,..."  -> <dir>/sheet.jpg (plus end card)
cd "$1" && mkdir -p frames && T=$(python3 -c "
from tl import s2o,DUR_MAIN
print(','.join(f'{s2o(float(t)):.2f}' for t in '$2'.split(','))+f',{DUR_MAIN+1.0:.2f}')") && OUTDIR=frames python3 render.py preview $T 2>&1 | grep -v "^W0000\|^INFO\|^WARNING" | tail -4
python3 -c "
from PIL import Image
fs=['frames/p_%05.2f.jpg'%float(t) for t in '$T'.split(',')]
n=len(fs);c=min(n,8);r=(n+c-1)//c;im=Image.new('RGB',(c*240,r*427))
for i,f in enumerate(fs): im.paste(Image.open(f).resize((240,427)),((i%c)*240,(i//c)*427))
im.save('sheet.jpg',quality=88)"
