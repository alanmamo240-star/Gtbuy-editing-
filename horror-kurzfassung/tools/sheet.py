# python3 tools/sheet.py out.jpg 6 snaps/*.jpg   -> contact sheet, 6 columns, file name printed on each tile
import sys
from PIL import Image, ImageDraw
out, cols, files = sys.argv[1], int(sys.argv[2]), sorted(sys.argv[3:]); tw = 270
ims = [Image.open(f) for f in files]; th = int(tw * ims[0].height / ims[0].width); rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * tw, rows * th), 'black'); d = ImageDraw.Draw(S)
for i, (im, f) in enumerate(zip(ims, files)):
    x, y = (i % cols) * tw, (i // cols) * th; S.paste(im.resize((tw, th)), (x, y)); d.rectangle([x, y, x + 96, y + 13], fill='black'); d.text((x + 2, y + 1), f.split('/')[-1][:-4], fill='yellow')
S.save(out, quality=88); print(out, len(ims), 'tiles')
