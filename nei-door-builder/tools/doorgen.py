"""Clean vector rebuild of NEI door builder profiles.
Geometry is in inches on the slab (door 36x80, sidelite 14x80).
Writes line/<id>.png (12 px/in) and relief/<id>.png (30 px/in) in the app's existing styles."""
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter

LPI, RPI = 12, 30          # line / relief pixels per inch

def line_img(W, items):
    s = 4  # supersample for smooth anti-aliased strokes
    im = Image.new("L", (int(W * LPI * s), int(80 * LPI * s)), 255); d = ImageDraw.Draw(im)
    S = lambda v: v * LPI * s; lw = int(3.4 * s)
    def rect(x, y, w, h): d.rectangle([S(x), S(y), S(x + w), S(y + h)], outline=0, width=lw)
    for it in items:
        x, y, w, h = it["box"]
        if it["t"] == "raised":
            b = it.get("bevel", 1.2); rect(x, y, w, h); rect(x + b, y + b, w - 2 * b, h - 2 * b)
            for (ax, ay), (bx, by) in [((x, y), (x + b, y + b)), ((x + w, y), (x + w - b, y + b)),
                                       ((x, y + h), (x + b, y + h - b)), ((x + w, y + h), (x + w - b, y + h - b))]:
                d.line([S(ax), S(ay), S(bx), S(by)], fill=0, width=lw)
        elif it["t"] == "flat":
            rect(x, y, w, h)
        elif it["t"] == "lite":
            m = it.get("frame", 0.75); rect(x - m, y - m, w + 2 * m, h + 2 * m); rect(x, y, w, h)
    d.rectangle([0, 0, im.width - 1, im.height - 1], outline=0, width=lw)
    return im.resize((int(W * LPI), int(80 * LPI)), Image.LANCZOS)

def relief_img(W, items):
    w, h = int(W * RPI), int(80 * RPI)
    H = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) / RPI
    for it in items:
        x, y, bw, bh = it["box"]
        if it["t"] in ("raised", "flat"):
            b = it.get("bevel", 1.2) if it["t"] == "raised" else 0.35
            # distance inside the panel from its (softly rounded) edge; the distance field creases at the
            # corners, which gives the mitered bevel seams the real panels have
            import cv2
            mk = Image.new("L", (w, h), 0); ImageDraw.Draw(mk).rounded_rectangle([x * RPI, y * RPI, (x + bw) * RPI, (y + bh) * RPI], radius=0.45 * RPI, fill=255)
            dist = cv2.distanceTransform(np.asarray(mk), cv2.DIST_L2, 5) / RPI
            inside = dist > 0
            prof = np.where(dist < b, -0.55 + 0.55 * (dist / b), 0.0)   # bevel rises from the groove to the field
            prof = np.where(dist < 0.22, -0.42, prof)                     # crisp sticking groove at the edge
            prof = np.where((dist >= 0.55) & (dist < 0.68), prof - 0.09, prof)  # fine groove just inside the edge
            lip = (dist >= b) & (dist < b + 0.28); prof = np.where(lip, 0.20, prof)  # lip where bevel meets the field
            prof = np.where((dist >= b + 0.28) & (dist < b + 0.42), -0.05, prof)
            if it["t"] == "flat": prof = np.where(dist < b, -0.45, -0.45) # shaker: whole panel recessed
            H = np.where(inside, prof, H)
        elif it["t"] == "lite":
            m = it.get("frame", 0.75)
            dist = np.minimum.reduce([xx - (x - m), x + bw + m - xx, yy - (y - m), y + bh + m - yy])
            ring = (dist > 0) & (dist < m)
            H = np.where(ring, 0.45 * np.sin(np.pi * dist / m), H)       # rounded glazing bead
            H = np.where(dist >= m, -0.2, H)
    import cv2; H = cv2.GaussianBlur(H, (0, 0), 1.15)
    gy, gx = np.gradient(H)
    shade = 128 + (gx * 0.75 + gy * 0.9) * 1500          # light from upper left, like the existing reliefs
    return Image.fromarray(np.clip(shade, 0, 255).astype(np.uint8))

def build(slab_id, W, items, root):
    fn = slab_id.replace(" ", "_")
    line_img(W, items).save(f"{root}/line/{fn}.png", optimize=True)
    relief_img(W, items).save(f"{root}/relief/{fn}.png", optimize=True)

# Door geometry (inches), read from the Fangda catalog drawings and checked against Fangda's renders /
# production photos; glass openings match each slab's glass_box in the database.
DOORS = {
  "FG02-M01": (36, [dict(t="lite", box=(6.8, 7.7, 22.1, 45.0)), dict(t="raised", box=(6.05, 56.4, 23.6, 13.0))]),
  "CG02-K01": (36, [dict(t="lite", box=(6.1, 6.4, 23.6, 36.6)),
                    dict(t="raised", box=(5.35, 49.25, 11.05, 22.35)), dict(t="raised", box=(19.4, 49.25, 11.05, 22.35))]),
  "FG03-M02": (36, [dict(t="lite", box=(7.0, 7.3, 21.8, 14.5)),
                    dict(t="flat", box=(6.35, 27.2, 9.15, 40.5)), dict(t="flat", box=(20.5, 27.2, 9.15, 40.5))]),
  "P02-K01 SL": (14, [dict(t="raised", box=(2.4, 10.15, 9.25, 12.45), bevel=1.3), dict(t="raised", box=(2.4, 50.9, 9.25, 20.5), bevel=1.3)]),
}

if __name__ == "__main__":
    root = sys.argv[1]
    for k in sys.argv[2:]:
        W, items = DOORS[k]; build(k, W, items, root); print("built", k)
