"""Generate loss_curve.svg from results/loss.csv (stdlib only)."""
import csv
from pathlib import Path

root = Path(__file__).resolve().parent
rows = list(csv.reader((root / "loss.csv").open()))
data = [(int(r[0]), float(r[1])) for r in rows[1:]]

W, H = 800, 420
ML, MR, MT, MB = 70, 30, 30, 60
pw, ph = W - ML - MR, H - MT - MB
steps = [s for s, _ in data]
losses = [l for _, l in data]
lmin, lmax = 0.12, 0.46
smin, smax = 0, 500

def X(s): return ML + (s - smin) / (smax - smin) * pw
def Y(l): return MT + (lmax - l) / (lmax - lmin) * ph

pts = " ".join(f"{X(s):.1f},{Y(l):.1f}" for s, l in data)

grid = []
for l in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]:
    y = Y(l)
    grid.append(f'<line x1="{ML}" y1="{y:.1f}" x2="{W-MR}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
    grid.append(f'<text x="{ML-8}" y="{y+4:.1f}" text-anchor="end" font-size="12" fill="#6b7280">{l:.2f}</text>')
for s in [0, 100, 200, 300, 400, 500]:
    x = X(s)
    grid.append(f'<text x="{x:.1f}" y="{H-MB+20}" text-anchor="middle" font-size="12" fill="#6b7280">{s}</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">
<rect width="{W}" height="{H}" fill="#ffffff"/>
{''.join(grid)}
<polyline points="{pts}" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linejoin="round"/>
<circle cx="{X(data[0][0]):.1f}" cy="{Y(data[0][1]):.1f}" r="4" fill="#2563eb"/>
<circle cx="{X(data[-1][0]):.1f}" cy="{Y(data[-1][1]):.1f}" r="4" fill="#2563eb"/>
<text x="{ML}" y="{MT-10}" font-size="16" font-weight="bold" fill="#111827">Training loss — SmolVLA fine-tune (svla_so100_pickplace)</text>
<text x="{W-MR}" y="{H-MB+36}" text-anchor="end" font-size="12" fill="#6b7280">steps</text>
<text x="16" y="{MT+ph/2}" text-anchor="middle" font-size="12" fill="#6b7280" transform="rotate(-90 16 {MT+ph/2})">loss</text>
</svg>
"""
(root / "loss_curve.svg").write_text(svg)
print(f"Wrote {root / 'loss_curve.svg'} ({len(svg)} bytes)")
