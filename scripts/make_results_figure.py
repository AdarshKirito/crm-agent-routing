"""Draw the README results figure from results/test_summary.md (light and dark SVG).

One row per system, three panels with one axis each: business single-turn success
with its 95% bootstrap CI, list-price cost per task over all test tasks (the
summary's "Run facts" spend divided by the task count, the same figure as the
README's cost columns), and the refusal rate on confidential requests. Numbers are
parsed from the summary, never typed in.

Usage:  python scripts/make_results_figure.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUMMARY = ROOT / "results" / "test_summary.md"
OUT = ROOT / "docs" / "img"

SYSTEMS = [  # (key in the summary, row label, group)
    ("react", "ReAct (benchmark agent)", "react"),
    ("react_privacy", "ReAct + privacy prompt", "react"),
    ("full", "crmroute, 3.8 Flash only", "crmroute"),
    ("routed", "crmroute, routed", "crmroute"),
]
THEMES = {
    "light": {"surface": "#fcfcfb", "text": "#0b0b0b", "muted": "#52514e", "grid": "#e6e5e1",
              "crmroute": "#2a78d6", "react": "#eb6834"},
    "dark": {"surface": "#1a1a19", "text": "#ffffff", "muted": "#c3c2b7", "grid": "#33332f",
             "crmroute": "#3987e5", "react": "#d95926"},
}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def parse_summary() -> dict:
    rows = {}
    pattern = re.compile(r"^\| (\w+) \| ([^|]+) \| (\d+) \| ([\d.]+) \[([\d.]+), ([\d.]+)\] \|")
    for line in SUMMARY.read_text(encoding="utf-8").splitlines():
        m = pattern.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        system, group = m.group(1), m.group(2).strip()
        rows[(system, group)] = {"n": int(m.group(3)), "rate": float(m.group(4)),
                                 "lo": float(m.group(5)), "hi": float(m.group(6)), "cost": float(cells[8])}
    return rows


def parse_cost_per_task() -> dict:
    """List-price spend per system ("Run facts") divided by the tasks each system ran."""
    text = SUMMARY.read_text(encoding="utf-8")
    n_tasks = int(re.search(r"Tasks common to all systems: (\d+)", text).group(1))
    spend = {m.group(1): float(m.group(2)) for m in re.finditer(r"^\| (\w+) \| \$([\d.]+) \|", text, re.M)}
    return {system: total / n_tasks for system, total in spend.items()}, n_tasks


def bar(x0: float, y: float, w: float, h: float, fill: str) -> str:
    """Bar anchored at the baseline with a 4px rounded data end."""
    if w <= 0:
        return ""
    r = min(4.0, w, h / 2)
    return (f'<path d="M{x0:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} '
            f'a{r},{r} 0 0 1 -{r},{r} h-{w - r:.1f} z" fill="{fill}"/>')


def draw(theme: dict, data: dict, cost: dict, n_tasks: int) -> str:
    W, row_h, top = 960, 36, 92
    H = top + row_h * len(SYSTEMS) + 86
    label_w = 190
    panels = [  # (title, x0, width, max, ticks, tick format)
        ("Business task success", label_w + 20, 230, 100, [0, 25, 50, 75, 100], "{:g}%"),
        (f"Cost per task (all {n_tasks})", label_w + 320, 150, 0.09, [0, 0.03, 0.06, 0.09], "${:.2f}"),
        ("Confidential requests refused", label_w + 545, 150, 100, [0, 50, 100], "{:g}%"),
    ]
    t = theme
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}" role="img" aria-labelledby="t d">',
           '<title id="t">crmroute vs the benchmark agent on the held-out test set</title>',
           '<desc id="d">Business single-turn success: ReAct 56.1%, ReAct with privacy prompt 50.0%, crmroute '
           'on 3.8 Flash 69.3%, crmroute routed 71.1%. Cost per task over all test tasks and refusal rates as labelled.</desc>',
           f'<rect width="{W}" height="{H}" rx="8" fill="{t["surface"]}"/>']
    # legend
    lx = 20
    for key, text in (("crmroute", "crmroute (this project)"), ("react", "ReAct, the benchmark's own agent")):
        out.append(f'<circle cx="{lx + 6}" cy="24" r="6" fill="{t[key]}"/>')
        out.append(f'<text x="{lx + 18}" y="28.5" font-size="13" fill="{t["text"]}">{text}</text>')
        lx += 18 + len(text) * 7.2 + 28
    out.append(f'<text x="{W - 20}" y="28.5" font-size="12" text-anchor="end" fill="{t["muted"]}">'
               'Held-out test set, Gemini 3.8 Flash, 194 tasks per system</text>')
    plot_top, plot_bottom = top - 8, top + row_h * len(SYSTEMS) - 8
    for title, x0, width, vmax, ticks, fmt in panels:
        out.append(f'<text x="{x0}" y="{top - 22}" font-size="12.5" font-weight="600" fill="{t["text"]}">{title}</text>')
        for v in ticks:
            x = x0 + width * v / vmax
            out.append(f'<line x1="{x:.1f}" y1="{plot_top}" x2="{x:.1f}" y2="{plot_bottom}" stroke="{t["grid"]}" stroke-width="1"/>')
            out.append(f'<text x="{x:.1f}" y="{plot_bottom + 16}" font-size="11" text-anchor="middle" '
                       f'fill="{t["muted"]}">{fmt.format(v)}</text>')
    for i, (key, label, group) in enumerate(SYSTEMS):
        cy = top + row_h * i + 10
        color = t[group]
        weight = ' font-weight="600"' if key == "routed" else ""
        out.append(f'<text x="20" y="{cy + 4.5}" font-size="13"{weight} fill="{t["text"]}">{label}</text>')
        biz = data[(key, "business, single-turn")]
        ref = data[(key, "confidentiality (refusal rate)")]
        # panel 1: success with CI whisker
        _, x0, width, vmax, _, _ = panels[0]
        px = lambda v: x0 + width * v / vmax  # noqa: E731
        out.append(f'<line x1="{px(biz["lo"]):.1f}" y1="{cy}" x2="{px(biz["hi"]):.1f}" y2="{cy}" stroke="{color}" '
                   'stroke-width="2" stroke-linecap="round" opacity="0.55"/>')
        out.append(f'<circle cx="{px(biz["rate"]):.1f}" cy="{cy}" r="6" fill="{color}" stroke="{t["surface"]}" stroke-width="2"/>')
        out.append(f'<text x="{px(biz["hi"]) + 8:.1f}" y="{cy + 4}" font-size="12"{weight} fill="{t["text"]}">'
                   f'{biz["rate"]:.1f}%</text>')
        # panel 2: cost bar
        _, x0, width, vmax, _, _ = panels[1]
        w = width * cost[key] / vmax
        out.append(bar(x0, cy - 7, w, 14, color))
        out.append(f'<text x="{x0 + w + 6:.1f}" y="{cy + 4}" font-size="12"{weight} fill="{t["text"]}">'
                   f'${cost[key]:.3f}</text>')
        # panel 3: refusal bar
        _, x0, width, vmax, _, _ = panels[2]
        w = width * ref["rate"] / vmax
        out.append(bar(x0, cy - 7, w, 14, color))
        out.append(f'<text x="{x0 + w + 6:.1f}" y="{cy + 4}" font-size="12"{weight} fill="{t["text"]}">'
                   f'{ref["rate"]:.1f}%</text>')
    out.append(f'<text x="20" y="{H - 34}" font-size="11.5" fill="{t["muted"]}">Single-turn test tasks: 114 '
               'business, 42 confidential. Lines: 95% bootstrap confidence intervals. Cost: list price per task over all test tasks.</text>')
    out.append(f'<text x="20" y="{H - 16}" font-size="11.5" fill="{t["muted"]}">"Routed" sends 9 of 19 task types '
               'to Gemini 3.1 Flash-Lite. Source: results/test_summary.md</text>')
    out.append("</svg>")
    return "\n".join(out)


def main() -> None:
    data = parse_summary()
    cost, n_tasks = parse_cost_per_task()
    for key, _, _ in SYSTEMS:
        for group in ("business, single-turn", "confidentiality (refusal rate)"):
            if (key, group) not in data:
                raise SystemExit(f"missing {key} / {group} in {SUMMARY}")
        if key not in cost:
            raise SystemExit(f"missing {key} in the Run facts spend table of {SUMMARY}")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        path = OUT / f"results_{name}.svg"
        path.write_text(draw(theme, data, cost, n_tasks), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
