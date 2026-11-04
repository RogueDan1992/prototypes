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
            w = it.get("w", 0.16)
            H = H - np.where(dd < w, 0.22 * (1 - dd / w), 0).astype(np.float32)
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
    rel = Image.fromarray(light(H).astype(np.uint8)).resize((int(W * RPI), 80 * RPI), Image.LANCZOS)
    if line: line_drawing(W, H, lines).save(f"{root}/line/{fn}.png", optimize=True)
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
  "P04-K01 #2": (36, [dict(t="lite", shape=("arch", 6.6, 8.0, 22.8, 6.0, 6.0), frame=0.9)]
                 + [R(x, 17.2, w, 25.0, 1.8) for x, w in K4_COL] + bottom_pair(49.2, 21.2, 1.8)),
  "P04-K01 #3": (36, [dict(t="lite", shape=("arch", 6.6, 4.2, 22.8, 9.9, 2.0), frame=0.9)]
                 + [R(x, 17.2, w, 25.0, 1.8) for x, w in K4_COL] + bottom_pair(49.2, 21.2, 1.8)),
  "P04-K01 #4": (36, [dict(t="lite", shape=("arch", 6.6, 6.0, 22.8, 36.6, 11.4), frame=0.9)] + bottom_pair(49.2, 20.0, 1.8)),
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
TRACED = {k for k, (_, its) in DOORS.items() if any(i["t"] == "trace" for i in its)}

if __name__ == "__main__":
    root = sys.argv[1]
    ids = list(DOORS) if sys.argv[2:] == ["all"] else sys.argv[2:]
    for k in ids:
        W, items = DOORS[k]; build(k, W, items, root, line=k not in TRACED); print("built", k)
