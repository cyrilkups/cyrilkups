#!/usr/bin/env python3
"""
Generates info-card.svg
A small neofetch-style card: About / Stack / Highlights sections.
Each line slides up + fades in with a staggered 0.06s delay per row.
Pure SMIL, no external CSS/JS.
"""
import os

MIN_WIDTH = 380
CHAR_W = 7.9
LINE_H = 20
PAD_X = 22
PAD_Y = 20
TITLEBAR_H = 30
STAGGER = 0.06
LINE_DUR = 0.45

ORANGE = "#ff9d3d"
BLUE = "#5ac8fa"
GREEN = "#39ff88"
CYAN = "#00f6ff"
WHITE = "#e6edf3"
DIM = "#8b949e"

# (label, value, label_color, value_color) -- label None => section header
LINES = [
    (None, "cyrilkups@github", None, ORANGE),
    (None, "-----------------", None, DIM),
    ("OS", "Product x Engineering", BLUE, WHITE),
    ("Role", "Technical PM & Software Engineer", BLUE, WHITE),
    ("Focus", "Systems, Infrastructure, Backend & Product", BLUE, WHITE),
    (None, "", None, None),
    ("Stack", "Go  Python  Java  TypeScript", GREEN, WHITE),
    ("Tools", "SpecLinter  Georim", GREEN, WHITE),
    (None, "", None, None),
    ("Highlight", "Designs backend systems that scale under real load", CYAN, WHITE),
    ("Highlight", "Bridges product strategy with hands-on engineering", CYAN, WHITE),
    ("Highlight", "Ships infrastructure that teams trust in production", CYAN, WHITE),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_char_len(label, value) -> int:
    if label is None:
        return len(value)
    return len(f"{label}:") + 1 + len(value)


def build_svg() -> str:
    n = len(LINES)
    height = TITLEBAR_H + PAD_Y * 2 + n * LINE_H

    longest = max((line_char_len(l, v) for l, v, _, _ in LINES), default=0)
    WIDTH = max(MIN_WIDTH, int(PAD_X * 2 + longest * CHAR_W + 12))

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" font-family="Menlo, Consolas, monospace">'
    )

    parts.append(f'''
  <defs>
    <filter id="cardGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="titlebarGrad2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#20262e"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <clipPath id="infoClip">
      <rect x="0" y="0" width="{WIDTH}" height="{height}" rx="14"/>
    </clipPath>
  </defs>

  <g clip-path="url(#infoClip)">
    <rect x="0" y="0" width="{WIDTH}" height="{height}" fill="#0d1117"/>
    <rect x="0" y="0" width="{WIDTH}" height="{height}" fill="none"
          stroke="#8a2be2" stroke-opacity="0.18" stroke-width="1.5" rx="14" filter="url(#cardGlow)"/>

    <rect x="0" y="0" width="{WIDTH}" height="{TITLEBAR_H}" fill="url(#titlebarGrad2)"/>
    <circle cx="18" cy="{TITLEBAR_H/2}" r="5.5" fill="#ff5f57"/>
    <circle cx="36" cy="{TITLEBAR_H/2}" r="5.5" fill="#febc2e"/>
    <circle cx="54" cy="{TITLEBAR_H/2}" r="5.5" fill="#28c840"/>
    <text x="{WIDTH/2}" y="{TITLEBAR_H/2 + 4}" fill="#8b949e" font-size="12" text-anchor="middle">neofetch</text>
''')

    for i, (label, value, label_color, value_color) in enumerate(LINES):
        y = TITLEBAR_H + PAD_Y + (i + 1) * LINE_H
        begin = round(i * STAGGER, 3)
        rise = 10

        if not value and not label:
            continue

        if label is None:
            text = f'<text x="{PAD_X}" y="{y}" fill="{value_color}" font-size="13">{esc(value)}</text>'
        else:
            label_txt = f'{label}:'
            text = (
                f'<text x="{PAD_X}" y="{y}" fill="{label_color}" font-size="13" font-weight="bold">{esc(label_txt)}</text>'
                f'<text x="{PAD_X + len(label_txt)*CHAR_W + 8:.1f}" y="{y}" fill="{value_color}" font-size="13">{esc(value)}</text>'
            )

        parts.append(f'''
    <g opacity="0" transform="translate(0,{rise})">
      <animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="{LINE_DUR}s" fill="freeze"
               calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
      <animateTransform attributeName="transform" attributeType="XML" type="translate"
                         from="0,{rise}" to="0,0" begin="{begin}s" dur="{LINE_DUR}s" fill="freeze"
                         calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
      {text}
    </g>''')

    parts.append('\n  </g>\n</svg>')
    return "".join(parts)


def main():
    svg = build_svg()
    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "info-card.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
