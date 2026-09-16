"""Construit la démo « Méningocoques et couverture vaccinale ».

Lit les CSV Odissé de data/odisse/ et les contours de data/geo/, puis injecte
les données dans src/meningocoque.template.html pour produire
demos/meningocoque/index.html (fichier HTML autonome, sans dépendance réseau).

Usage :  python src/build_meningocoque.py
"""
import json, math, os
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = os.path.join(ROOT, 'data', 'odisse') + os.sep
GEO = os.path.join(ROOT, 'data', 'geo') + os.sep

# ---------- geometry ----------
def dp(points, tol):
    if len(points) < 3:
        return points
    dmax, idx = 0.0, 0
    x1, y1 = points[0]; x2, y2 = points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy)
    for i in range(1, len(points) - 1):
        x0, y0 = points[i]
        if norm == 0:
            d = math.hypot(x0 - x1, y0 - y1)
        else:
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        return dp(points[:idx + 1], tol)[:-1] + dp(points[idx:], tol)
    return [points[0], points[-1]]

def ring_area(r):
    s = 0.0
    for i in range(len(r) - 1):
        s += r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
    return abs(s) / 2

def polys(geom):
    if geom['type'] == 'Polygon':
        return [geom['coordinates']]
    return geom['coordinates']

def simplify_feature(geom, tol, min_area):
    out = []
    for poly in polys(geom):
        ring = [tuple(p) for p in poly[0]]
        if ring_area(ring) < min_area:
            continue
        r = dp(ring, tol)
        if len(r) > 3:
            out.append(r)
    return out

metro = json.load(open(GEO + 'departements-version-simplifiee.geojson'))
shapes = {}
for f in metro['features']:
    code = f['properties']['code']
    shapes[code] = simplify_feature(f['geometry'], 0.003, 0.002)

# project metro: equirectangular scaled by cos(lat0)
LAT0 = math.radians(46.6)
def proj(lon, lat):
    return (lon * math.cos(LAT0), -lat)

pts = [proj(*p) for c in shapes.values() for r in c for p in r]
minx = min(p[0] for p in pts); maxx = max(p[0] for p in pts)
miny = min(p[1] for p in pts); maxy = max(p[1] for p in pts)
W = 620.0
s = W / (maxx - minx)
H = (maxy - miny) * s

geo = {}
for code, rings in shapes.items():
    d = []
    for r in rings:
        seg = []
        for lon, lat in r:
            x, y = proj(lon, lat)
            seg.append('%.1f %.1f' % ((x - minx) * s, (y - miny) * s))
        d.append('M' + 'L'.join(seg) + 'Z')
    geo[code] = ''.join(d)

# DOM insets
dom_names = {'971': 'Guadeloupe', '972': 'Martinique', '973': 'Guyane', '974': 'La Réunion', '976': 'Mayotte'}
dom_tol = {'971': 0.006, '972': 0.006, '973': 0.02, '974': 0.006, '976': 0.004}
dom_minarea = {'971': 0.0008, '972': 0.0005, '973': 0.01, '974': 0.002, '976': 0.0003}
BOX = 74.0
GAP = 8.0
insets = []
for i, code in enumerate(['971', '972', '973', '974', '976']):
    f = json.load(open(GEO + 'dom-%s.geojson' % code))
    rings = simplify_feature(f['geometry'], dom_tol[code], dom_minarea[code])
    lat_c = sum(p[1] for r in rings for p in r) / sum(len(r) for r in rings)
    k = math.cos(math.radians(lat_c))
    P = [((lon * k), -lat) for r in rings for lon, lat in r]
    ax = min(p[0] for p in P); bx = max(p[0] for p in P)
    ay = min(p[1] for p in P); by = max(p[1] for p in P)
    sc = (BOX - 14) / max(bx - ax, by - ay)
    ox = i * (BOX + GAP) + (BOX - (bx - ax) * sc) / 2
    oy = H + 26 + (BOX - (by - ay) * sc) / 2
    d = []
    for r in rings:
        seg = []
        for lon, lat in r:
            x, y = (lon * k, -lat)
            seg.append('%.1f %.1f' % (ox + (x - ax) * sc, oy + (y - ay) * sc))
        d.append('M' + 'L'.join(seg) + 'Z')
    geo[code] = ''.join(d)
    insets.append({'code': code, 'nom': dom_names[code],
                   'x': i * (BOX + GAP), 'y': H + 26, 'w': BOX, 'h': BOX})

names = {f['properties']['code']: f['properties']['nom'] for f in metro['features']}
names.update(dom_names)

# ---------- data ----------
iim = pd.read_csv(U + 'infection-invasive-a-meningocoque-notifications.csv',
                  dtype={'Département Code': str, 'Région Code': str})
iim = iim[iim['Département Code'] != '0']
Y0, Y1 = int(iim['Année'].min()), int(iim['Année'].max())
years = list(range(Y0, Y1 + 1))
sero = ['Tous types', 'B', 'C', 'W', 'Y']

cases = {}   # code -> sero -> [by year]
pop = {}     # code -> [by year]
for code, g in iim.groupby('Département Code'):
    cases[code] = {s: [None] * len(years) for s in sero}
    pop[code] = [None] * len(years)
    for _, r in g.iterrows():
        yi = int(r['Année']) - Y0
        cases[code][r['Méningocoque']][yi] = int(r['Nombre de cas']) if pd.notna(r['Nombre de cas']) else None
        if pd.notna(r['Population']):
            pop[code][yi] = int(r['Population'])

regions = {}
for code, g in iim.groupby('Département Code'):
    regions[code] = None if g['Région'].isna().all() else g['Région'].dropna().iloc[0]

# coverage
arch = pd.read_csv(U + 'couvertures-vaccinales-archives-departement.csv', dtype={'Département Code': str})
ado = pd.read_csv(U + 'couvertures-vaccinales-des-adolescent-et-adultes-departement.csv', dtype={'Département Code': str})

indicators = [
    ('C24', 'Méningocoque C à 24 mois', arch, 'C', '24 mois'),
    ('C24a', 'Méningocoque C à 2-4 ans', arch, 'C', '2-4 ans'),
    ('C59', 'Méningocoque C à 5-9 ans', arch, 'C', '5-9 ans'),
    ('C1014', 'Méningocoque C 10-14 ans', arch, 'C', '10-14 ans'),
    ('C1519', 'Méningocoque C 15-19 ans', arch, 'C', '15-19 ans'),
    ('C2024', 'Méningocoque C 20-24 ans', arch, 'C', '20-24 ans'),
    ('ACWY1114', 'Méningocoques ACWY 11-14 ans', ado, 'ACWY', '11-14 ans'),
    ('ACWY15', 'Méningocoques ACWY 15 ans', ado, 'ACWY', '15 ans'),
    ('ACWY1524', 'Méningocoques ACWY 15-24 ans', ado, 'ACWY', '15-24 ans'),
]

cov = {}      # ind -> code -> [by year]
cov_meta = []
for key, col, df, vac, age in indicators:
    d = df[['Année', 'Département Code', col]].dropna(subset=[col])
    cov[key] = {}
    for _, r in d.iterrows():
        code = r['Département Code']
        yi = int(r['Année']) - Y0
        if code not in cov[key]:
            cov[key][code] = [None] * len(years)
        if 0 <= yi < len(years):
            cov[key][code][yi] = round(float(r[col]), 1)
    ys = sorted(set(int(y) for y in d['Année']))
    cov_meta.append({'key': key, 'label': col, 'vac': vac, 'age': age,
                     'years': ys, 'n': len(cov[key])})

out = {
    'years': years,
    'sero': sero,
    'names': names,
    'regions': regions,
    'cases': cases,
    'pop': pop,
    'cov': cov,
    'covMeta': cov_meta,
    'geo': geo,
    'insets': insets,
    'mapW': round(W, 1), 'mapH': round(H, 1),
    'totalH': round(H + 26 + BOX + 16, 1),
}
DATA = json.dumps(out, ensure_ascii=False, separators=(',', ':'))

tpl = open(os.path.join(ROOT, 'src', 'meningocoque.template.html'), encoding='utf-8').read()
dest = os.path.join(ROOT, 'demos', 'meningocoque', 'index.html')
os.makedirs(os.path.dirname(dest), exist_ok=True)
with open(dest, 'w', encoding='utf-8') as fh:
    fh.write(tpl.replace('__DATA__', DATA))

print('données : %.0f Ko' % (len(DATA) / 1024))
print('écrit   : %s (%.0f Ko)' % (dest, os.path.getsize(dest) / 1024))
