import os

tasks = [
    ("door-close-v3", "easy", 100),
    ("button-press-topdown-v3", "easy", 80),
    ("reach-v3", "easy", 30),
    ("basketball-v3", "medium", 20),
    ("bin-picking-v3", "medium", 20),
    ("sweep-v3", "medium", 10),
    ("coffee-push-v3", "medium", 0),
    ("pick-place-v3", "hard", 20),
    ("push-v3", "hard", 20),
    ("assembly-v3", "hard", 0),
    ("shelf-place-v3", "very-hard", 10),
    ("disassemble-v3", "very-hard", 10),
]

colors = {"easy": "#2e7d32", "medium": "#ef6c00", "hard": "#c62828", "very-hard": "#6a1b9a"}

W, H = 960, 580
left = 235
plot_right = 900
top = 60
bar_h = 30
gap = 9

n = len(tasks)
plot_height = n * bar_h + (n - 1) * gap
bottom = top + plot_height
x_scale = (plot_right - left) / 100.0

svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Arial, sans-serif">')
svg.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
svg.append(f'<text x="{left}" y="36" font-size="20" font-weight="bold" fill="#111111">Success rate by task &mdash; M0 (base) = M1 (MT50), 10 episodes/task</text>')

for v in [0, 25, 50, 75, 100]:
    x = left + v * x_scale
    svg.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="#e0e0e0" stroke-width="1"/>')
    svg.append(f'<text x="{x}" y="{bottom + 18}" font-size="12" fill="#666666" text-anchor="middle">{v}%</text>')

for i, (name, diff, val) in enumerate(tasks):
    y = top + i * (bar_h + gap)
    svg.append(f'<text x="{left - 10}" y="{y + bar_h/2 + 4}" font-size="13" fill="#333333" text-anchor="end">{name}</text>')
    svg.append(f'<rect x="{left}" y="{y}" width="{plot_right - left}" height="{bar_h}" fill="#f2f2f2" rx="3"/>')
    w = val * x_scale
    if w > 0.5:
        svg.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{colors[diff]}" rx="3"/>')
    svg.append(f'<text x="{left + w + 6}" y="{y + bar_h/2 + 4}" font-size="12" fill="#333333">{val}%</text>')

lx = left
ly = bottom + 48
for j, (diff, c) in enumerate(colors.items()):
    cx = lx + j * 130
    svg.append(f'<rect x="{cx}" y="{ly}" width="14" height="14" fill="{c}" rx="2"/>')
    svg.append(f'<text x="{cx + 20}" y="{ly + 12}" font-size="13" fill="#333333">{diff}</text>')

svg.append('</svg>')

out = os.path.join("ros-vla-manip", "results", "success_rate.svg")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("written:", out)
