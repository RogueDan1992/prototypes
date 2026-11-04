"""Clean vector rebuild of NEI door builder profiles (v2).

Geometry is in inches on the slab (door 36x80, sidelite 14x80), read from the Fangda catalog drawings
(Fiberglass door catalogue 2026.5.14). Writes, in the app's existing formats:
  line/<id>.png    12 px/in, black strokes on white (picker tiles, fallback)
  relief/<id>.png  30 px/in, gray 128 = flat; blended over the wood grain with hard-light

v2 adds any panel shape (rect, bell/cathedral top and bottom, segment, camber and round tops, ellipse),
flat recessed panels, planks and V-grooves, and "trace" (panel masks taken from an existing clean line
drawing). The relief is lit like a photo: Fangda-style raised panel profile (sticking groove, cove,
shallow bevel, fillet, field), light from the upper left, soft cast shadows into the grooves and
ambient occlusion. Usage:  python3 doorgen.py <img root> <slab id> [<slab id> ...]   ("all" = every slab)
"""
import math, sys
import numpy as np, cv2
from PIL import Image, ImageDraw

LPI, RPI = 12, 30          # line / relief pixels per inch (app formats)
P = 60                     # working resolution, px/in (relief is rendered at 2x then reduced)

# ---------- shapes -> polygons (inches) ----------
def _bell(x, y, w, rise, n=60, down=False):
    """bell / cathedral edge across the width: flat ears at the corners, rounded peak in the middle"""
    pts = []
    for i in range(n + 1):
        t = i / n; s = math.sin(math.pi * t) ** 2
        pts.append((x + w * t, y + (rise * s if down else -rise * s)))
    return pts

def poly(spec):
    k = spec[0]
    if k == "rect":
        x, y, w, h = spec[1:5]; return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if k == "bell":        # ("bell", x, y_shoulder, w, y_bottom, rise_top[, dip_bottom]) ; peak at y_shoulder - rise
        x, ys, w, yb, rise = spec[1:6]; dip = spec[6] if len(spec) > 6 else 0
        top = _bell(x, ys, w, rise)
        bot = list(reversed(_bell(x, yb, w, dip, down=True))) if dip else [(x + w, yb), (x, yb)]
        return top + bot
    if k == "arch":        # ("arch", x, y_top, w, h, rise): rectangle whose top edge is a circular segment of the given rise
        x, y, w, h, rise = spec[1:6]; yb = y + h; ys = y + rise
        if rise >= w / 2 - 1e-6:            # half round
            r = w / 2; cx = x + r
            top = [(cx - r * math.cos(a), ys - r * math.sin(a)) for a in np.linspace(0, math.pi, 90)]
        else:
            r = (rise ** 2 + (w / 2) ** 2) / (2 * rise); cx, cy = x + w / 2, y + r; a0 = math.asin((w / 2) / r)
            top = [(cx + r * math.sin(a), cy - r * math.cos(a)) for a in np.linspace(-a0, a0, 90)]
        return top + [(x + w, yb), (x, yb)] if rise < w / 2 - 1e-6 else [(x, yb)] + top + [(x + w, yb)]
    if k == "ellipse":
        cx, cy, rx, ry = spec[1:5]
        return [(cx + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 180, endpoint=False)]
    raise ValueError(k)

def corners(spec):
    """vertices where a miter line belongs (sharp corners of a raised panel)"""
    pts = poly(spec)
    if spec[0] == "rect": return pts
    if spec[0] == "bell": x, ys, w, yb = spec[1:5]; return [(x, ys), (x + w, ys), (x + w, yb), (x, yb)] if len(spec) <= 6 or not spec[6] else [(x, ys), (x + w, ys), (x + w, yb), (x, yb)]
    if spec[0] == "arch": x, y, w, h, rise = spec[1:6]; return [(x, y + rise), (x + w, y + rise), (x + w, y + h), (x, y + h)]
    return []

def mask(W, pts, res=P):
    im = Image.new("L", (int(W * res), int(80 * res)), 0)
    ImageDraw.Draw(im).polygon([(px * res, py * res) for px, py in pts], fill=255)
    return np.asarray(im) > 127

def sdist(m, res=P):
    """signed distance in inches: positive inside the mask, negative outside"""
    m8 = m.astype(np.uint8)
    din = cv2.distanceTransform(m8, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    dout = cv2.distanceTransform(1 - m8, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    return (din - dout) / res

def trace_masks(line_path, W, close=0.06):
    """panel masks from an existing clean line drawing: every region the stile/rail field can't reach"""
    a = np.asarray(Image.open(line_path).convert("L")); h, w = a.shape; ppi = w / W
    ink = (a < 170).astype(np.uint8); b = max(2, int(0.3 * ppi))
    ink[:b] = 0; ink[-b:] = 0; ink[:, :b] = 0; ink[:, -b:] = 0
    n, lab = cv2.connectedComponents(1 - ink, connectivity=4)
    edge = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]); bg = np.bincount(edge).argmax()
    m = (lab != bg).astype(np.uint8)
    n2, lab2, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    out = []
    for i in range(1, n2):
        if st[i][2] < 1.5 * ppi or st[i][3] < 1.5 * ppi: continue
        sm = cv2.resize((lab2 == i).astype(np.float32), (int(W * P), int(80 * P)), interpolation=cv2.INTER_CUBIC)
        sm = cv2.GaussianBlur(sm, (0, 0), P * 0.10) > 0.5
        # the drawn outline sits on the panel edge: pull the mask in by half a stroke
        out.append(sdist(sm) > close)
    return out

# ---------- profiles (height in inches; stile surface = 0) ----------
def raised_profile(d, b):
    """Fangda raised panel, measured from the outer edge inward: sticking step, cove, bevel, fillet, field"""
    h = np.zeros_like(d)
    h = np.where(d < 0.12, -0.08, h)
    cove = (d >= 0.12) & (d < 0.32); t = (d - 0.12) / 0.20
    h = np.where(cove, -0.08 - 0.42 * np.sin(t * math.pi / 2), h)
    e = 0.32 + b; bev = (d >= 0.32) & (d < e); t = (d - 0.32) / b
    h = np.where(bev, -0.50 + 0.40 * (np.clip(t, 0, 1) ** 0.85), h)
    fil = (d >= e) & (d < e + 0.10); h = np.where(fil, -0.13, h)
    h = np.where(d >= e + 0.10, -0.07, h)
    return h, e

def flat_profile(d):
    h = np.where(d < 0.30, -0.06 - 0.30 * np.sin(np.clip(d / 0.30, 0, 1) * math.pi / 2), -0.36)
    return h

def lite_frame(dout, m):
    """raised glazing frame around a lite opening (dout = distance outside the opening, inches)"""
    t = np.clip(dout / m, 0, 1)
    return 0.30 * np.sin(math.pi * t ** 0.75) - 0.04 * t

# ---------- build ----------
def heightfield(W, items):
    H = np.zeros((80 * P, int(W * P)), np.float32)
    lines = []          # (signed-distance field, level) pairs and miter segments for the line drawing
    global inks; inks = []
    yy = xx = None
    for it in items:
        t = it["t"]
        if t in ("raised", "flat"):
            sd = sdist(mask(W, poly(it["shape"])))
            inside = sd > 0
            if t == "raised":
                prof, e = raised_profile(sd, it.get("bevel", 1.5))
                lines += [("sd", sd, 0.0), ("sd", sd, e)]
                for (cx, cy) in corners(it["shape"]):
                    lines.append(("miter", cx, cy, it["shape"], e))
            else:
                prof = flat_profile(sd); lines.append(("sd", sd, 0.0))
            H = np.where(inside, prof, H)
        elif t == "trace":
            for m in trace_masks(it["src"], W):
                sd = sdist(m); prof, e = raised_profile(sd, it.get("bevel", 1.5))
                H = np.where(sd > 0, prof, H)
                if it.get("ink"):   # dark metalwork drawn inside the panel field (clavos, speakeasy grille)
                    a = np.asarray(Image.open(it["src"]).convert("L")).astype(np.float32) / 255
                    a = cv2.resize(a, (H.shape[1], H.shape[0]), interpolation=cv2.INTER_CUBIC)
                    inks.append(np.where(sd > e + 0.35, 1 - a, 0))
        elif t == "lite":
            shp = it.get("shape") or ("rect", *it["box"])
            sd = sdist(mask(W, poly(shp))); m = it.get("frame", 0.9)
            ring = (sd <= 0) & (sd > -m)
            H = np.where(ring, lite_frame(-sd, m), H)
            H = np.where(sd > 0, -0.65, H)            # glass sits below; the app paints the glass over it
            lines += [("sd", sd, 0.0), ("sd", sd, -m)]
        elif t == "groove":   # V-groove along a segment
            (x0, y0), (x1, y1) = it["a"], it["b"]
            if yy is None:
                yy, xx = np.mgrid[0:H.shape[0], 0:H.shape[1]].astype(np.float32) / P
            vx, vy = x1 - x0, y1 - y0; L2 = vx * vx + vy * vy
            u = np.clip(((xx - x0) * vx + (yy - y0) * vy) / L2, 0, 1)
            dd = np.hypot(xx - (x0 + u * vx), yy - (y0 + u * vy))
            w = it.get("w", 0.20)
            H = H - np.where(dd < w, 0.34 * np.clip(1 - dd / w, 0, 1) ** 0.8, 0).astype(np.float32)
            lines.append(("seg", x0, y0, x1, y1))
    return H, lines

def light(H):
    """photo-like lighting of the height field -> hard-light gray (128 = flat)"""
    Hs = cv2.GaussianBlur(H, (0, 0), P * 0.035)
    gy, gx = np.gradient(Hs, 1.0 / P)
    n = np.dstack([-gx, -gy, np.ones_like(Hs)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    L = np.array([-0.50, -0.70, 0.85]); L /= np.linalg.norm(L)
    lam = (n @ L) / L[2]                                     # 1.0 on flat faces
    # soft shadow cast by edges onto the recesses (march toward the light)
    sh = np.zeros_like(Hs); lx, ly = L[0] / math.hypot(L[0], L[1]), L[1] / math.hypot(L[0], L[1])
    tanE = L[2] / math.hypot(L[0], L[1])
    for s in np.linspace(0.04, 0.9, 18):
        dx, dy = -lx * s * P, -ly * s * P
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        Hm = cv2.warpAffine(Hs, M, (Hs.shape[1], Hs.shape[0]), borderMode=cv2.BORDER_REPLICATE)
        sh = np.maximum(sh, np.clip((Hm - Hs - s * tanE * 0.55) * 3.2, 0, 1))
    sh = cv2.GaussianBlur(sh, (0, 0), P * 0.08)
    ao = np.clip((cv2.GaussianBlur(Hs, (0, 0), P * 0.45) - Hs) * 1.6, 0, 0.45)
    spec = np.clip(n @ (L + np.array([0, 0, 1.0])) / np.linalg.norm(L + np.array([0, 0, 1.0])), 0, 1) ** 60
    spec0 = (np.array([0, 0, 1.0]) @ (L + np.array([0, 0, 1.0])) / np.linalg.norm(L + np.array([0, 0, 1.0]))) ** 60
    v = 128 * lam * (1 - 0.42 * sh) * (1 - ao) + 60 * (spec - spec0)
    return np.clip(v, 0, 255)

def line_drawing(W, H, lines):
    """crisp line art for the picker tiles, from the same geometry"""
    s = 4; res = LPI * s; lw = 0.135        # half stroke width, inches
    ink = np.zeros((80 * res, int(W * res)), np.float32)
    im = Image.new("L", (int(W * res), 80 * res), 0); d = ImageDraw.Draw(im)
    for ln in lines:
        if ln[0] == "sd":
            sd = cv2.resize(ln[1], (int(W * res), 80 * res), interpolation=cv2.INTER_LINEAR)
            ink = np.maximum(ink, np.clip(1 - (np.abs(sd - ln[2]) - lw) * res, 0, 1))
        elif ln[0] == "seg":
            d.line([ln[1] * res, ln[2] * res, ln[3] * res, ln[4] * res], fill=255, width=int(2 * lw * res))
        elif ln[0] == "miter":
            cx, cy, shp, e = ln[1:]
            pts = corners(shp); mx = sum(p[0] for p in pts) / 4; my = sum(p[1] for p in pts) / 4
            dx, dy = (1 if mx > cx else -1), (1 if my > cy else -1)
            d.line([cx * res, cy * res, (cx + dx * e) * res, (cy + dy * e) * res], fill=255, width=int(2 * lw * res))
    ink = np.maximum(ink, np.asarray(im) / 255.0)
    b = int(2 * lw * res); ink[:b] = 1; ink[-b:] = 1; ink[:, :b] = 1; ink[:, -b:] = 1   # slab outline
    out = Image.fromarray((255 * (1 - ink)).astype(np.uint8))
    return out.resize((int(W * LPI), 80 * LPI), Image.LANCZOS)

def build(slab_id, W, items, root, line=True):
    fn = slab_id.replace(" #", "_").replace(" ", "_")
    items = [dict(it, src=it["src"].format(root=root)) if "src" in it else it for it in items]
    H, lines = heightfield(W, items)
    v = light(H)
    for ink in inks: v = v * (1 - 0.82 * np.clip(ink * 1.6, 0, 1))
    rel = Image.fromarray(v.astype(np.uint8)).resize((int(W * RPI), 80 * RPI), Image.LANCZOS)
    if line: line_drawing(W, H, lines).save(f"{root}/line/{fn}.png", optimize=True)
    elif lines:   # traced panels keep their drawing; add the extra items (lite frames) on top of it
        src = next(it["src"] for it in items if it["t"] == "trace")
        base = np.asarray(Image.open(src).convert("L"))
        add = np.asarray(line_drawing(W, H, lines).convert("L"))
        b = int(0.3 * LPI); add = add.copy(); add[:b] = 255; add[-b:] = 255; add[:, :b] = 255; add[:, -b:] = 255
        Image.fromarray(np.minimum(base, add)).save(f"{root}/line/{fn}.png", optimize=True)
    rel.save(f"{root}/relief/{fn}.png", optimize=True)

# ---------- geometry ----------
R = lambda x, y, w, h, b=1.5: dict(t="raised", shape=("rect", x, y, w, h), bevel=b)
F = lambda x, y, w, h: dict(t="flat", shape=("rect", x, y, w, h))
LITE = lambda x, y, w, h, m=0.9: dict(t="lite", box=(x, y, w, h), frame=m)
TRACE = lambda fn, b=1.5: dict(t="trace", src="{root}/line/" + fn, bevel=b)

# Oak (K). Numbers read from the catalog cells (page 08, ±0.3"; the small cells are ±0.5") and, where the
# app's existing drawing already matched the catalog, from that drawing. Shared grids:
K4_COL = [(6.35, 9.35), (20.3, 9.35)]                         # two-column panels, P04/P03 families
K6_COL = [(5.85, 10.55), (19.35, 10.55)]                       # six panel
P03_TOP = ("bell", 6.35, 10.2, 23.3, 53.2, 2.8)                # bell (cathedral) top, P03-K01
P03K03_TOP = ("bell", 6.35, 10.2, 23.3, 50.4, 2.8, 2.6)        # bell top + inverted bell bottom, P03-K03
OVAL = ("ellipse", 17.85, 30.35, 6.85, 17.75)                  # matches glass_box [11, 12.6, 13.7, 35.5]

def bottom_pair(y, h, b=1.5): return [R(x, y, w, h, b) for x, w in K4_COL]

DOORS = {
  # --- earlier rebuilds (same geometry, new lighting) ---
  "FG02-M01": (36, [LITE(6.8, 7.7, 22.1, 45.0), R(6.05, 56.4, 23.6, 13.0, 1.2)]),
  "CG02-K01": (36, [LITE(6.1, 6.4, 23.6, 36.6), R(5.35, 49.25, 11.05, 22.35), R(19.4, 49.25, 11.05, 22.35)]),
  "FG03-M02": (36, [LITE(7.0, 7.3, 21.8, 14.5), F(6.35, 27.2, 9.15, 40.5), F(20.5, 27.2, 9.15, 40.5)]),
  "P02-K01 SL": (14, [R(2.4, 10.15, 9.25, 12.45, 1.6), R(2.4, 50.9, 9.25, 20.5, 1.6)]),

  # --- oak ---
  "P00-K01": (36, []),
  "P00-K01 #2": (36, [LITE(8.0, 7.0, 20.0, 61.0)]),
  "P00-K01 #3": (36, [LITE(5.9, 5.5, 5.4, 64.6, 0.8)]),
  "P00-K06": (36, [F(7.3, 5.8, 21.4, 62.1)] + [dict(t="groove", a=(7.6, y), b=(28.4, y)) for y in
                   (11.6, 17.8, 24.0, 30.2, 36.5, 42.7, 48.9, 55.1, 61.4)]),
  "P00-K07": (36, [F(6.6, 6.6, 22.8, 63.0)] + [dict(t="groove", a=(x, 6.9), b=(x, 69.3)) for x in
                   (10.4, 14.2, 18.0, 21.8, 25.6)]),
  "P02-K01 SL #2": (14, [LITE(2.7, 6.4, 8.6, 36.6, 0.9), R(2.4, 50.9, 9.25, 20.5, 1.6)]),   # VERIFY 836 lite position
  "P02-K03": (36, [R(6.35, 7.25, 23.2, 46.15, 1.8), R(6.35, 57.2, 23.2, 12.4, 1.8)]),
  "P02-K03 #2": (36, [LITE(6.8, 7.7, 22.1, 45.0), R(6.35, 57.2, 23.2, 12.4, 1.8)]),
  "P02-K05 SL": (14, [F(2.9, 6.75, 8.35, 15.55), F(2.9, 27.5, 8.35, 41.4)]),
  "P03-K01": (36, [dict(t="raised", shape=P03_TOP, bevel=1.8)] + bottom_pair(58.0, 12.4)),
  "P03-K01 #2": (36, [dict(t="raised", shape=P03_TOP, bevel=1.8), dict(t="lite", shape=OVAL, frame=0.9)] + bottom_pair(58.0, 12.4)),
  "P03-K01 #3": (36, [LITE(7.0, 6.9, 22.0, 46.4)] + bottom_pair(58.0, 12.4)),
  "P03-K02": (36, [F(6.6, 6.8, 22.8, 15.0), F(6.6, 27.5, 9.0, 40.7), F(20.4, 27.5, 9.0, 40.7)]),
  "P03-K03": (36, [dict(t="raised", shape=P03K03_TOP, bevel=1.8)] + bottom_pair(58.0, 12.4)),
  "P03-K03 #2": (36, [dict(t="raised", shape=P03K03_TOP, bevel=1.8), dict(t="lite", shape=OVAL, frame=0.9)] + bottom_pair(58.0, 12.4)),
  # P04-K01 "4 panel BT": tall top rail; variants with a segment, camber or round-top lite in it (catalog cells b-d)
  "P04-K01": (36, [R(x, 17.2, w, 25.0, 1.8) for x, w in K4_COL] + bottom_pair(49.2, 21.2, 1.8)),
  "P04-K01 #2": (36, [dict(t="lite", shape=("arch", 6.6, 5.0, 22.8, 9.0, 9.0), frame=0.9)]
                 + [R(x, 17.2, w, 25.0, 1.8) for x, w in K4_COL] + bottom_pair(49.2, 21.2, 1.8)),
  "P04-K01 #3": (36, [dict(t="lite", shape=("arch", 6.6, 4.2, 22.8, 9.9, 2.0), frame=0.9)]
                 + [R(x, 17.2, w, 25.0, 1.8) for x, w in K4_COL] + bottom_pair(49.2, 21.2, 1.8)),
  "P04-K01 #4": (36, [dict(t="lite", shape=("arch", 6.6, 5.3, 22.8, 36.9, 11.4), frame=0.9)] + bottom_pair(49.2, 20.0, 1.8)),
  "P04-K03": (36, [R(6.35, 6.75, 9.4, 35.5), R(20.15, 6.75, 9.35, 35.5), R(6.35, 47.85, 9.4, 21.0), R(20.15, 47.85, 9.35, 21.0)]),
  "P04-K03-TN": (36, [LITE(7.15, 7.6, 7.8, 33.9), LITE(20.95, 7.6, 7.75, 33.9), R(6.35, 47.85, 9.4, 21.0), R(20.15, 47.85, 9.35, 21.0)]),
  "P04-K03 #2": (36, [LITE(6.1, 6.4, 23.6, 36.6), R(5.35, 49.25, 11.05, 22.35), R(19.4, 49.25, 11.05, 22.35)]),  # = CG02-K01 (same catalog drawing)
  "P06-K01": (36, [R(x, y, w, h, 2.0) for (x, w) in K6_COL for (y, h) in ((5.65, 9.35), (20.1, 22.8), (48.85, 21.8))]),
  "P06-K01 #2": (36, [LITE(6.3, 6.1, 9.3, 8.2, 0.8), LITE(20.0, 6.0, 9.2, 8.4, 0.8)]          # = its lites in the database
                 + [R(x, y, w, h, 2.0) for (x, w) in K6_COL for (y, h) in ((20.1, 22.8), (48.85, 21.8))]),
  "P06-K10": (36, [TRACE("P06-K10.png", 1.6)]),
  "P08-K01": (36, [TRACE("P08-K01.png", 1.5)]),
  "P08-K01 #2": (36, [TRACE("P08-K01_2.png", 1.5), dict(t="lite", shape=("arch", 15.5, 15.7, 4.9, 37.0, 2.45), frame=0.7)]),
  "FG05-K01": (36, [LITE(*b, 0.6) for b in ((6.9, 8.5, 22.1, 5.2), (6.9, 22.2, 22.1, 5.2), (6.9, 36, 22.1, 5.1), (6.9, 49.8, 22.1, 5.2), (6.9, 63.6, 22.1, 5.2))]),
}
# Mahogany (M), catalog page 06. Same conventions as oak; where the app drawing already matched the
# catalog its numbers are kept. Several glass doors were stretched to the full 80" (no bottom rail): rebuilt.
def grid(x, y, w, h, cols, rows, bar=0.8):
    cw, rh = (w - bar * (cols - 1)) / cols, (h - bar * (rows - 1)) / rows
    return [(round(x + c * (cw + bar), 2), round(y + r * (rh + bar), 2), round(cw, 2), round(rh, 2)) for r in range(rows) for c in range(cols)]
def lites(boxes, m=0.6): return [LITE(*b, m) for b in boxes]
def planks(x0, x1, y0, y1, xs): return [dict(t="groove", a=(x, y0), b=(x, y1)) for x in xs]
P03M_FLATS = [F(6.33, 6.75, 23.33, 15.58), F(6.58, 27.42, 9.33, 41.33), F(20.25, 27.33, 9.42, 41.25)]
FG00M06 = grid(6.6, 6.0, 22.8, 61.8, 2, 4)        # glass measured from the catalog fill (wider than FG00-M02)
FG02M05 = grid(6.8, 7.7, 22.1, 45.0, 2, 3)
DOORS.update({
  "P00-M01": (36, []),
  "P00-M01 #2": (36, [LITE(8.0, 7.1, 20.0, 60.9)]),
  "P02-M01": (36, [dict(t="raised", shape=("arch", 5.8, 7.6, 24.4, 34.7, 1.0), bevel=1.4), R(5.8, 48.1, 24.4, 18.8, 1.4)]
              + planks(0, 0, 9.4, 40.6, (12.7, 16.2, 19.7, 23.3)) + planks(0, 0, 49.9, 65.1, (12.7, 16.2, 19.7, 23.3))),
  "P02-M03": (36, [dict(TRACE("P02-M03.png", 1.4), ink=True)]),
  "P02-M04": (36, [R(6.33, 7.25, 23.17, 46.0, 1.8), R(6.33, 57.0, 23.17, 12.33, 1.8)]),
  "P02-M04 #2": (36, [LITE(6.8, 7.7, 22.1, 45.0), R(6.33, 57.0, 23.17, 12.33, 1.8)]),
  "P02-M08": (36, [TRACE("P02-M08.png", 1.6)]),
  "P02-M11": (36, [R(4.67, 4.75, 26.58, 42.75, 1.4), R(4.67, 52.83, 26.58, 20.17, 1.4)]
              + planks(0, 0, 6.5, 45.7, (10.8, 15.6, 20.3, 25.0)) + planks(0, 0, 54.6, 71.2, (10.8, 15.6, 20.3, 25.0))),
  "P02-M15 SL": (14, [R(2.42, 10.25, 9.17, 12.33, 1.6), R(2.42, 51.0, 9.17, 20.42, 1.6)]),
  "P02-M17": (36, [R(7.7, 4.6, 20.6, 40.6, 1.5), R(7.7, 50.2, 20.6, 21.1, 1.5)]),
  "P03-M01": (36, [TRACE("P03-M01.png", 1.6)]),
  "P03-M01 #2": (36, [TRACE("P03-M01.png", 1.6), dict(t="lite", shape=OVAL, frame=0.9)]),   # catalog p06, 2nd P03-M01 cell; not in the database yet
  "P03-M02": (36, P03M_FLATS),
  "P03-M02 #2": (36, [LITE(7.0, 7.4, 22.0, 14.4)] + P03M_FLATS[1:]),
  "P03-M05": (36, [dict(t="raised", shape=P03_TOP, bevel=1.8)] + bottom_pair(58.0, 12.4)),
  "P05-M01": (36, [R(4.67, 4.67, 26.58, 68.17, 1.4)] + planks(0, 0, 6.4, 71.1, (11.0, 15.6, 20.4, 25.0))),
  "P06-M01": (36, [TRACE("P06-M01.png", 1.8)]),
  "P07-M01": (36, planks(0, 0, 0.3, 79.7, (6.4, 29.6)) + [dict(t="groove", a=(6.4, y), b=(29.6, y)) for y in (11.0, 21.8, 32.6, 43.4, 54.2, 65.0)]),
  "P08-M01": (36, [TRACE("P08-M01.png", 1.5)]),
  "P08-M01 #2": (36, [TRACE("P08-M01_2.png", 1.5), dict(t="lite", shape=("arch", 15.5, 15.7, 4.9, 37.0, 2.45), frame=0.7)]),
  "P08-M02": (36, [TRACE("P08-M02.png", 1.5)]),
  "FG00-M01 SL": (14, [LITE(4.1, 7.6, 5.9, 59.9, 0.8)]),
  "FG00-M02": (36, [LITE(8.0, 7.0, 20.0, 61.0)]),
  "FG00-M06": (36, [LITE(6.6, 6.0, 22.8, 61.8)] + lites(FG00M06, 0.4)),          # VERIFY bars: wood muntins vs grille
  "FG00-M07 SL": (14, [LITE(4.4, 7.5, 5.1, 59.0, 0.8)] + lites([(4.4, 7.5, 5.1, 12.9), (4.4, 22.8, 5.1, 13), (4.4, 38, 5.1, 13), (4.4, 53.4, 5.1, 13.1)], 0.4)),
  "FG00-M10": (36, [LITE(5.9, 5.5, 5.4, 64.6, 0.8)]),
  "FG02-M05": (36, [LITE(6.8, 7.7, 22.1, 45.0)] + lites(FG02M05, 0.4) + [R(6.05, 59.3, 23.6, 12.0, 1.2)]),
  "FG02-M07 SL": (14, [LITE(2.9, 6.9, 8.1, 45.8, 0.8), R(2.42, 57.08, 9.25, 12.33, 1.3)]),
  "FG02-M09": (36, lites([(7.2, 8.5, 9.9, 16), (18.6, 8.5, 9.9, 16), (7.2, 26.1, 9.9, 15.9), (18.6, 26.1, 9.9, 15.9)], 0.7) + [R(6.75, 48.33, 22.33, 21.0, 1.6)]),
  "FG02-M10 SL": (14, lites([(3, 8.5, 8, 16.3), (3, 25.9, 8, 16.1)], 0.6) + [R(2.5, 48.33, 9.08, 21.0, 1.5)]),
  "FG02-M11 SL": (14, lites([(3.3, 6.9, 7.4, 14.4), (3.3, 22.3, 7.4, 14.4), (3.3, 37.5, 7.4, 14.3)], 0.6) + [R(2.92, 55.92, 8.33, 13.17, 1.3)]),
  "FG02-M13 SL": (14, lites([(4.4, 7.1, 5.1, 6.4), (4.4, 15.4, 5.1, 6.2)], 0.6) + [F(3.92, 27.5, 6.25, 42.08)]),
  "FG02-M18 SL": (14, [LITE(3.5, 7.1, 7.1, 14.4, 0.6), F(3.0, 27.58, 8.33, 42.0)]),
  "FG02-M21": (36, lites([(7, 7.3, 6, 10.4), (15, 7.3, 5.9, 10.4), (22.6, 7.3, 6.1, 10.4), (7, 19.4, 6, 10), (15, 19.4, 5.9, 10), (22.6, 19.5, 6.1, 10),
                         (7, 31.2, 6, 10.4), (15, 31.2, 5.9, 10.4), (22.6, 31.2, 6.1, 10.4)], 0.6) + [R(6.25, 48.0, 9.5, 20.83, 1.6), R(20.08, 48.0, 9.5, 20.83, 1.6)]),
  "FG03-M01": (36, lites([(7.6, 7.6, 20.5, 15.8), (7.6, 30.1, 20.5, 15.7), (7.6, 52.5, 20.5, 15.9)], 0.7)),
  "FG04-M01": (36, lites([(7.1, 7.3, 6.1, 6.2), (15, 7.4, 5.9, 6.1), (22.6, 7.3, 5.9, 6.2), (7.1, 15.4, 6.1, 6.2), (15, 15.4, 5.9, 6.2), (22.6, 15.4, 5.9, 6.2)], 0.5)
                + [F(6.67, 27.58, 5.92, 42.0), F(14.92, 27.58, 5.92, 42.0), F(23.33, 27.58, 5.92, 42.0)]),
  "FG05-M01": (36, [LITE(*b, 0.6) for b in ((6.9, 8.5, 22.1, 5.2), (6.9, 22.2, 22.1, 5.2), (6.9, 36, 22.1, 5.1), (6.9, 49.8, 22.1, 5.2), (6.9, 63.6, 22.1, 5.2))]),
})

# Smooth (MS), catalog page 11, left half. Glass rectangles measured from the catalog's glass fill.
FLATS3 = [F(6.67, 27.58, 5.92, 42.0), F(14.92, 27.58, 5.92, 42.0), F(23.33, 27.58, 5.92, 42.0)]
FLATS2 = [F(6.35, 27.2, 9.15, 40.5), F(20.5, 27.2, 9.15, 40.5)]
DOORS.update({
  "P00-MS04": (36, []),
  "P00-MS04 #2": (36, [LITE(8.0, 7.0, 20.0, 61.0)]),
  "P00-MS04 #3": (36, lites([(20.9, 8.7, 8.7, 5.1), (20.9, 27.9, 8.7, 5.1), (20.9, 47.2, 8.7, 5.1), (20.9, 66.2, 8.7, 5.1)], 0.6)),   # VERIFY lite size
  "P00-MS04 #4": (36, [LITE(24.6, 5.5, 5.4, 64.6, 0.8)]),
  "P00-MS04 #5": (36, [LITE(14.45, 9.2, 7.1, 59.7, 0.8)]),     # catalog cell 4: centered narrow lite (app had it as "P00-MS04 SL")
  "P02-MS01": (36, [R(5.8, 7.4, 24.4, 34.9, 1.4), R(5.8, 48.1, 24.4, 18.8, 1.4)]
               + planks(0, 0, 9.2, 40.5, (12.7, 16.2, 19.7, 23.3)) + planks(0, 0, 49.9, 65.1, (12.7, 16.2, 19.7, 23.3))),
  "P02-MS02": (36, [R(6.33, 7.25, 23.17, 46.0, 1.8), R(6.33, 57.0, 23.17, 12.33, 1.8)]),
  "P02-MS02 #2": (36, [LITE(6.8, 7.7, 22.1, 45.0), R(6.33, 57.0, 23.17, 12.33, 1.8)]),
  "P02-MS06 SL": (14, [R(2.42, 10.25, 9.25, 12.33, 1.6), R(2.42, 51.0, 9.17, 20.42, 1.6)]),
  "P02-MS07": (36, [dict(t="raised", shape=("arch", 6.33, 7.3, 23.33, 35.0, 1.5), bevel=1.6), R(6.33, 48.9, 23.33, 21.9, 1.6)]),
  "P02-MS09": (36, [F(6.33, 4.6, 23.5, 35.6), F(6.33, 46.8, 23.5, 20.5)]),
  "P02-MS11": (36, [R(7.7, 4.6, 20.6, 40.6, 1.5), R(7.7, 50.2, 20.6, 21.1, 1.5)]),          # same layout as P02-M17
  "P02-MS13 SL": (14, [F(3.42, 10.92, 7.33, 12.25), F(3.42, 48.58, 7.17, 20.75)]),
  "P03-MS04": (36, P03M_FLATS),
  "P04-MS01": DOORS["P04-K01"], "P04-MS01 #2": DOORS["P04-K01 #2"], "P04-MS01 #3": DOORS["P04-K01 #3"], "P04-MS01 #4": DOORS["P04-K01 #4"],
  "P06-MS04": DOORS["P06-K01"],
  "P06-MS04 #2": DOORS["CG02-K01"],                     # catalog: 2236 cutout over 2 panels
  "P06-MS04 #3": DOORS["P04-K03-TN"],                   # catalog: 2 tall lites over 2 panels (app had it as "P06-MS04 SL")
  "FG00-MS02": (36, [LITE(7.9, 7.0, 20.0, 61.0)]),
  "FG00-MS04": (36, [LITE(5.9, 5.5, 5.4, 64.6, 0.8)]),
  "FG00-MS06 SL": (14, [LITE(4.1, 7.6, 5.9, 59.9, 0.8)]),
  "FG00-MS09": (36, [LITE(7.7, 6.2, 20.5, 42.0)]),
  "FG00-MS10": DOORS["FG00-M06"],
  "FG00-MS11 SL": DOORS["FG00-M07 SL"],
  "FG02-MS02 SL": (14, [LITE(3.5, 7.1, 7.1, 14.4, 0.6), F(3.0, 27.58, 8.33, 42.0)]),
  "FG02-MS03": (36, lites([(7.2, 8.5, 9.9, 16), (18.6, 8.5, 9.9, 16), (7.2, 26.1, 9.9, 15.8), (18.6, 26.1, 9.9, 15.9)], 0.7) + [R(6.75, 48.33, 22.33, 21.0, 1.6)]),
  "FG02-MS04": (36, lites([(7.1, 7, 9.6, 13.7), (19.1, 7, 9.6, 13.7), (7, 22.9, 9.8, 13.1), (19.1, 22.9, 9.6, 13.1), (7, 38.1, 9.8, 13.8), (19, 38.1, 9.7, 13.8)], 0.6)
                + [R(6.05, 56.4, 23.6, 13.0, 1.2)]),
  "FG02-MS06 SL": DOORS["FG02-M10 SL"],
  "FG02-MS08 SL": DOORS["FG02-M11 SL"],
  "FG02-MS12": (36, [LITE(7.3, 7.7, 21.6, 34.0), R(6.75, 48.33, 22.33, 21.0, 1.6)]),
  "FG02-MS13 SL": (14, [LITE(3.3, 8.5, 7.4, 33.5, 0.7), R(2.5, 48.33, 9.08, 21.0, 1.5)]),
  "FG03-MS02": (36, lites([(7.2, 7.3, 5.8, 6.3), (15, 7.3, 6, 6.3), (22.7, 7.3, 6, 6.3), (7.2, 15.4, 5.9, 6.2), (15, 15.4, 6, 6.2), (22.6, 15.4, 6, 6.2)], 0.5) + FLATS2),
  "FG03-MS05": (36, [LITE(7.1, 7.3, 21.9, 14.5)] + FLATS2),
  "FG03-MS06": (36, lites([(6.6, 6.4, 6.1, 14.5), (14.7, 6.4, 6.1, 14.5), (22.6, 6.4, 6.1, 14.5)], 0.6) + FLATS2),   # not in the database yet
  "FG03-MS07": (36, lites([(7.2, 7.1, 9.9, 6.4), (18.9, 7.1, 9.8, 6.4), (7.2, 15.4, 9.9, 6.2), (18.8, 15.4, 10, 6.2)], 0.5) + FLATS2),
})

TRACED = {k for k, (_, its) in DOORS.items() if any(i["t"] == "trace" for i in its)}

if __name__ == "__main__":
    root = sys.argv[1]
    ids = list(DOORS) if sys.argv[2:] == ["all"] else sys.argv[2:]
    for k in ids:
        W, items = DOORS[k]; build(k, W, items, root, line=k not in TRACED); print("built", k)
