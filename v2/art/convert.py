#!/usr/bin/env python3
"""Downscale an upscaled 'pixel-art-style' image back to a true, crisp pixel sprite.

Steps: knock out the flat background -> auto-crop to the subject ->
downscale to a target height -> reduce the palette -> hard-threshold the alpha.

Usage:
    python3 convert.py SRC.png OUT.png [--h 38] [--colors 16] [--bgtol 32]
"""
import sys, argparse, base64
from PIL import Image

def corner_bg(img, tol):
    """Estimate bg as the MEDIAN border colour (robust to dark corners/edges),
    then build a mask of pixels close to it."""
    px = img.load(); w, h = img.size
    edge = []
    for x in range(w):                       # top + bottom rows
        edge.append(px[x,0]); edge.append(px[x,h-1])
    for y in range(h):                       # left + right cols
        edge.append(px[0,y]); edge.append(px[w-1,y])
    def med(i):
        v = sorted(c[i] for c in edge); return v[len(v)//2]
    bg = (med(0), med(1), med(2))
    out = Image.new("L", (w, h), 0)
    op = out.load()
    for y in range(h):
        for x in range(w):
            r,g,b = px[x,y][:3]
            d = abs(r-bg[0])+abs(g-bg[1])+abs(b-bg[2])
            op[x,y] = 0 if d <= tol else 255      # 0 = background, 255 = keep
    return out

def autocrop(img, mask):
    bbox = mask.getbbox()
    return (img.crop(bbox), mask.crop(bbox)) if bbox else (img, mask)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--h", type=int, default=38)
    ap.add_argument("--colors", type=int, default=16)
    ap.add_argument("--bgtol", type=int, default=32)
    a = ap.parse_args()

    img = Image.open(a.src).convert("RGB")
    mask = corner_bg(img, a.bgtol)
    img, mask = autocrop(img, mask)

    # downscale to target height (LANCZOS averages the blur away cleanly)
    w, h = img.size
    nw = max(1, round(w * a.h / h))
    img  = img.resize((nw, a.h),  Image.LANCZOS)
    mask = mask.resize((nw, a.h), Image.LANCZOS)

    # reduce palette on the colour data, then re-attach a hard alpha
    q = img.quantize(colors=a.colors, method=Image.MEDIANCUT).convert("RGB")
    rgba = q.convert("RGBA")
    pa = rgba.load(); pm = mask.load()
    for y in range(a.h):
        for x in range(nw):
            r,g,b,_ = pa[x,y]
            pa[x,y] = (r,g,b, 255 if pm[x,y] >= 128 else 0)   # crisp edges
    rgba.save(a.out)

    # x8 preview + base64 data-uri for embedding in the single-file game
    rgba.resize((nw*8, a.h*8), Image.NEAREST).save(a.out.replace(".png","_x8.png"))
    uri = "data:image/png;base64," + base64.b64encode(open(a.out,"rb").read()).decode()
    print(f"{a.out}: {nw}x{a.h}, {a.colors} colors")
    print("DATA_URI " + a.out + " " + uri)

if __name__ == "__main__":
    main()
