"""Draw the README's flow diagram (light and dark SVG).

The four steps of "How it works" on one row, with the two ways out: a guard refusal above
the guard, and a hand-off to a person below the check. Drawn as a picture rather than a
mermaid block so that it stays readable at the README's width and GitHub's diagram controls
do not cover it. Colours and font follow scripts/make_results_figure.py.

Usage:  python scripts/make_flow_figure.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img"

THEMES = {
    "light": {"surface": "#fcfcfb", "text": "#0b0b0b", "muted": "#52514e", "node": "#ffffff",
              "border": "#b4b3ad", "arrow": "#6f6e69", "accent": "#2a78d6", "accent_fill": "#e9f1fb"},
    "dark": {"surface": "#1a1a19", "text": "#ffffff", "muted": "#c3c2b7", "node": "#242423",
             "border": "#5c5b56", "arrow": "#a3a29a", "accent": "#3987e5", "accent_fill": "#16304f"},
}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

W, H = 960, 272
ROW_Y, ROW_H = 92, 72           # the main row: top and height
GAP = 30                        # arrow length between main-row nodes
POINT = 16                      # how far a hexagon's left and right points stick out
# (key, width, shape, title lines, detail lines); titles in bold, details in the muted colour
MAIN = [
    ("question", 92, "box", ["Business", "question"], []),
    ("guard", 132, "hex", ["Guard"], ["private or", "confidential?"]),
    ("route", 118, "box", ["Route"], ["picks the model", "by task type"]),
    ("solve", 152, "box", ["Solve"], ["read-only CRM tools,", "3 independent runs"]),
    ("check", 176, "hex", ["Check"], ["receipts, agreement,", "certified rule"]),
    ("answer", 112, "accent", ["Answer +", "its evidence"], []),
]
TITLE_SIZE, DETAIL_SIZE, LABEL_SIZE = 14, 12.5, 12
TITLE_LINE, DETAIL_LINE = 17, 15.5


def text_block(cx: float, cy: float, titles: list, details: list, t: dict, accent: bool = False) -> list:
    """Centred lines: bold titles, then muted details, the block centred on (cx, cy)."""
    height = len(titles) * TITLE_LINE + len(details) * DETAIL_LINE
    y = cy - height / 2
    out = []
    for line in titles:
        y += TITLE_LINE
        colour = t["accent"] if accent else t["text"]
        out.append(f'<text x="{cx:.1f}" y="{y - 4.5:.1f}" font-size="{TITLE_SIZE}" font-weight="600" '
                   f'text-anchor="middle" fill="{colour}">{line}</text>')
    for line in details:
        y += DETAIL_LINE
        out.append(f'<text x="{cx:.1f}" y="{y - 4:.1f}" font-size="{DETAIL_SIZE}" text-anchor="middle" '
                   f'fill="{t["muted"]}">{line}</text>')
    return out


def node(x: float, y: float, w: float, h: float, shape: str, t: dict) -> str:
    if shape == "hex":
        points = [(x, y + h / 2), (x + POINT, y), (x + w - POINT, y), (x + w, y + h / 2),
                  (x + w - POINT, y + h), (x + POINT, y + h)]
        coords = " ".join(f"{px:.1f},{py:.1f}" for px, py in points)
        return f'<polygon points="{coords}" fill="{t["node"]}" stroke="{t["border"]}" stroke-width="1.3"/>'
    fill, stroke = (t["accent_fill"], t["accent"]) if shape == "accent" else (t["node"], t["border"])
    width = 1.6 if shape == "accent" else 1.3
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="8" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>')


def arrow(x1: float, y1: float, x2: float, y2: float, t: dict) -> str:
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{t["arrow"]}" '
            'stroke-width="1.5" marker-end="url(#head)"/>')


def label(x: float, y: float, text: str, t: dict, anchor: str = "middle") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{LABEL_SIZE}" text-anchor="{anchor}" '
            f'fill="{t["muted"]}">{text}</text>')


def draw(t: dict) -> str:
    total = sum(w for _, w, *_ in MAIN) + GAP * (len(MAIN) - 1)
    x = (W - total) / 2
    cy = ROW_Y + ROW_H / 2
    boxes = {}
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}" role="img" aria-labelledby="t d">',
           '<title id="t">How crmroute handles a business question</title>',
           '<desc id="d">In customer sessions the guard refuses private or confidential requests. Otherwise the '
           'question is routed to a model by task type and solved with read-only CRM tools in three independent '
           'runs. If the receipts check out, the runs agree and the certified release rule allows it, the answer '
           'is given with its evidence; otherwise the question goes to a person with the reason.</desc>',
           '<defs><marker id="head" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{t["arrow"]}"/></marker></defs>',
           f'<rect width="{W}" height="{H}" rx="8" fill="{t["surface"]}"/>']
    for key, w, shape, titles, details in MAIN:
        boxes[key] = (x, w)
        out.append(node(x, ROW_Y, w, ROW_H, shape, t))
        if key == "question":  # a plain label, not a step
            out += [f'<text x="{x + w / 2:.1f}" y="{cy - 3:.1f}" font-size="{TITLE_SIZE}" text-anchor="middle" '
                    f'fill="{t["text"]}">Business</text>',
                    f'<text x="{x + w / 2:.1f}" y="{cy + 14:.1f}" font-size="{TITLE_SIZE}" text-anchor="middle" '
                    f'fill="{t["text"]}">question</text>']
        else:
            out += text_block(x + w / 2, cy, titles, details, t, accent=shape == "accent")
        x += w + GAP
    keys = [k for k, *_ in MAIN]
    for left, right in zip(keys, keys[1:]):
        lx, lw = boxes[left]
        rx, _ = boxes[right]
        out.append(arrow(lx + lw, cy, rx - 1.5, cy, t))
    # labels on the two decisions' main-row exits
    gx, gw = boxes["guard"]
    out.append(label(gx + gw + GAP / 2, cy - 8, "no", t))
    kx, kw = boxes["check"]
    out.append(label(kx + kw + GAP / 2, cy - 8, "pass", t))
    # the guard's way out: up to a refusal; the guard runs in customer sessions only
    gc = gx + gw / 2
    out.append(node(gc - 58, 16, 116, 38, "box", t))
    out.append(f'<text x="{gc:.1f}" y="{16 + 24:.1f}" font-size="{TITLE_SIZE}" font-weight="600" '
               f'text-anchor="middle" fill="{t["text"]}">Refuse</text>')
    out.append(arrow(gc, ROW_Y, gc, 16 + 38 + 1.5, t))
    out.append(label(gc + 8, ROW_Y - 13, "yes", t, anchor="start"))
    out.append(f'<text x="{gc:.1f}" y="{ROW_Y + ROW_H + 22:.1f}" font-size="{LABEL_SIZE}" text-anchor="middle" '
               f'fill="{t["muted"]}">in customer sessions</text>')
    # the check's way out: down to a person
    kc = kx + kw / 2
    py = ROW_Y + ROW_H + 40
    out.append(node(kc - 92, py, 184, 52, "box", t))
    out += text_block(kc, py + 26, ["Hand to a person,"], ["with the reason"], t)
    out.append(arrow(kc, ROW_Y + ROW_H, kc, py - 1.5, t))
    out.append(label(kc + 8, ROW_Y + ROW_H + 29, "fail", t, anchor="start"))
    out.append("</svg>")
    return "\n".join(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, theme in THEMES.items():
        path = OUT / f"flow_{name}.svg"
        path.write_text(draw(theme) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
