"""Generate MOCK data for the OCEAVERA UI -> data.js (placeholder values, not results).

Schema (window.OCEAVERA_DATA) that the real export must match:
  run:      {mock: bool, species, region, dataset_version, generated}
  grid:     {lon0, lat0, step, cols, rows}   cell (r, c) is at lon0+c*step, lat0+r*step (r=0 is south)
  coast:    [[[lon, lat], ...], ...]         land outline: list of polygon rings (see sri_lanka_outline.json)
  models:   [{id, name, selected, metrics:{random|spatial:{roc_auc, pr_auc, f1, precision, recall}},
              importance:{variable: value} | null,
              scores:[rows*cols numbers 0..1, row-major, null = not modelled]}]
Run:  python make_mock_data.py
"""
import json, math, random

random.seed(45)
# Real Sri Lanka outline (Natural Earth 1:10m, public domain): list of rings, main island + small islands
with open("sri_lanka_outline.json") as _f:
    RINGS = json.load(_f)
LON0, LAT0, STEP, COLS, ROWS = 78.8, 5.2, 0.1, 38, 52


def inside(x, y):
    ok = False
    for ring in RINGS:
        n = len(ring)
        for i in range(n):
            (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                ok = not ok
    return ok


shore = []
for ring in RINGS:
    for i in range(len(ring)):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % len(ring)]
        k = max(1, int(math.hypot(x2 - x1, y2 - y1) / 0.02))
        shore += [(x1 + (x2 - x1) * t / k, y1 + (y2 - y1) * t / k) for t in range(k)]

HOT = [(79.3, 8.6, .5), (79.9, 6.2, .45), (81.5, 8.7, .4)]  # mock hotspots (lon, lat, spread)


def cell(r, c):
    x, y = LON0 + (c + .5) * STEP, LAT0 + (r + .5) * STEP
    if inside(x, y):
        return None
    d = min(math.hypot(x - sx, y - sy) for sx, sy in shore)
    if d > 1.6:
        return None
    base = math.exp(-((d - .35) / .5) ** 2)
    hot = max(math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / s ** 2) for hx, hy, s in HOT)
    return base, hot


raw = [[cell(r, c) for c in range(COLS)] for r in range(ROWS)]


def scores(wb, wh, noise):
    out = []
    for row in raw:
        for v in row:
            out.append(None if v is None else round(min(1, max(0, wb * v[0] + wh * v[1] + random.gauss(0, noise))), 2))
    return out


def metrics(ra, pa, f, p, rc, drop):
    rnd = dict(roc_auc=ra, pr_auc=pa, f1=f, precision=p, recall=rc)
    spa = {k: round(v - drop * (1.2 if k in ("pr_auc", "f1") else 1), 2) for k, v in rnd.items()}
    return {"random": rnd, "spatial": spa}


FEATS = ["Sea temperature", "Bathymetry", "Salinity", "Chlorophyll", "Dissolved oxygen", "Current velocity"]


def imp(*w):
    return {f: v for f, v in zip(FEATS, w)}


models = [
    dict(id="baseline", name="Baseline (distance to coast)", selected=False,
         metrics=metrics(.62, .55, .58, .56, .60, .02), importance=None, scores=scores(.9, 0, .03)),
    dict(id="logreg", name="Logistic Regression", selected=False,
         metrics=metrics(.84, .79, .75, .74, .77, .06), importance=imp(.31, .27, .14, .13, .09, .06),
         scores=scores(.5, .55, .04)),
    dict(id="rf", name="Random Forest", selected=False,
         metrics=metrics(.96, .94, .89, .88, .90, .16), importance=imp(.28, .33, .12, .15, .07, .05),
         scores=scores(.4, .7, .09)),
    dict(id="gb", name="Gradient Boosting", selected=True,
         metrics=metrics(.95, .93, .88, .89, .87, .09), importance=imp(.30, .31, .10, .17, .07, .05),
         scores=scores(.4, .7, .06)),
]

data = dict(
    run=dict(mock=True, species="Chelonia mydas (placeholder)", region="Sri Lanka waters (OBIS Area 230)",
             dataset_version="mock-0", generated="2026-10-16"),
    grid=dict(lon0=LON0, lat0=LAT0, step=STEP, cols=COLS, rows=ROWS),
    coast=RINGS, models=models)

with open("data.js", "w") as f:
    f.write("window.OCEAVERA_DATA = " + json.dumps(data, separators=(",", ":")) + ";\n")
print("wrote data.js")
