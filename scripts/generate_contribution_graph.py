#!/usr/bin/env python3
"""
Generates github-contribution-animation.svg
53x7 contribution grid, pure SMIL, diagonal bottom-left -> top-right reveal
with a bright glint flash on arrival. Level 3+ cells get an outer neon glow.
No external CSS/JS.
"""
import random
import os

WEEKS = 53
DAYS = 7
CELL = 11
GAP = 3
MARGIN = 20
STEP = 0.018          # seconds between adjacent diagonals
CELL_ANIM_DUR = 0.5   # base fade-in duration
GLINT_DUR = 0.35       # glint flash+fade duration

BG = "#0d1117"

# neon palette per contribution level (0 = empty -> 4 = max)
LEVELS = {
    0: "#161b22",
    1: "#0e4a4a",   # dim cyan
    2: "#1f6f3a",   # green
    3: "#c9660d",   # orange (glow)
    4: "#8a2be2",   # purple (glow)
}

GLINT_COLOR = "#eafff5"

random.seed(7)


def gen_grid():
    grid = []
    for w in range(WEEKS):
        col = []
        for d in range(DAYS):
            r = random.random()
            if r < 0.35:
                lvl = 0
            elif r < 0.60:
                lvl = 1
            elif r < 0.80:
                lvl = 2
            elif r < 0.93:
                lvl = 3
            else:
                lvl = 4
            col.append(lvl)
        grid.append(col)
    return grid


def build_svg(grid):
    width = MARGIN * 2 + WEEKS * (CELL + GAP)
    height = MARGIN * 2 + DAYS * (CELL + GAP)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, Menlo, monospace">'
    )

    parts.append(f'''
  <defs>
    <filter id="glow3" x="-150%" y="-150%" width="400%" height="400%">
      <feGaussianBlur stdDeviation="2.2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="glow4" x="-150%" y="-150%" width="400%" height="400%">
      <feGaussianBlur stdDeviation="3.2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <radialGradient id="bgGlow" cx="50%" cy="50%" r="75%">
      <stop offset="0%" stop-color="#132029"/>
      <stop offset="100%" stop-color="{BG}"/>
    </radialGradient>
  </defs>

  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#bgGlow)" rx="14"/>
''')

    for w in range(WEEKS):
        for d in range(DAYS):
            lvl = grid[w][d]
            x = MARGIN + w * (CELL + GAP)
            y = MARGIN + d * (CELL + GAP)

            # diagonal index: 0 at bottom-left, increases toward top-right
            diagonal = w + (DAYS - 1 - d)
            begin = round(diagonal * STEP, 3)
            color = LEVELS[lvl]

            filter_attr = ""
            if lvl == 3:
                filter_attr = ' filter="url(#glow3)"'
            elif lvl == 4:
                filter_attr = ' filter="url(#glow4)"'

            # base cell: fades in and holds
            parts.append(f'''
  <g>
    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" ry="2.5"
          fill="{color}"{filter_attr} opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{begin}s"
               dur="{CELL_ANIM_DUR}s" fill="freeze" calcMode="spline"
               keySplines="0.2 0.8 0.2 1"/>
    </rect>
    <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" ry="2.5"
          fill="{GLINT_COLOR}" opacity="0">
      <animate attributeName="opacity" values="0;0.95;0" keyTimes="0;0.15;1"
               begin="{begin}s" dur="{GLINT_DUR}s" fill="freeze"/>
    </rect>
  </g>''')

    parts.append("\n</svg>")

    return "".join(parts)


def main():
    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "github-contribution-animation.svg")
    grid = gen_grid()
    svg = build_svg(grid)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
