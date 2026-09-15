#!/usr/bin/env python3
"""
Generates terminal-card.svg
Fetches the GitHub avatar for GITHUB_USERNAME, converts it to dense ASCII art
with Pillow, and places it inside an animated macOS-style terminal window.
Rows reveal top-to-bottom with a sweeping cursor block; footer types out
`$ whoami` -> username. Pure SMIL, no external CSS/JS.
"""
import io
import os
import requests
from PIL import Image

GITHUB_USERNAME = "cyrilkups"
DISPLAY_NAME = "cyril"

ASCII_COLS = 46
ASCII_ROWS = 26
ASCII_RAMP = "@%#*+=-:. "[::-1]  # dark -> light becomes dense -> sparse

FONT_W = 6.2
FONT_H = 11
PAD_X = 18
PAD_Y = 16
TITLEBAR_H = 30
FOOTER_H = 34

ROW_STAGGER = 0.05     # s between row reveals
ROW_DUR = 0.28
CURSOR_DUR = 0.22       # sweep time across a row


def fetch_avatar(username: str) -> Image.Image:
    url = f"https://github.com/{username}.png?size=256"
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("L")
    except Exception as exc:
        print(f"warning: could not fetch avatar ({exc}); using placeholder gradient")
        img = Image.new("L", (256, 256))
        for y in range(256):
            for x in range(256):
                img.putpixel((x, y), (x + y) // 2)
    return img


def image_to_ascii(img: Image.Image, cols: int, rows: int) -> list:
    img = img.resize((cols, rows))
    pixels = list(img.getdata())
    ramp_len = len(ASCII_RAMP) - 1
    lines = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            p = pixels[r * cols + c]
            idx = int((p / 255) * ramp_len)
            row_chars.append(ASCII_RAMP[idx])
        lines.append("".join(row_chars))
    return lines


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(ascii_lines: list) -> str:
    art_w = ASCII_COLS * FONT_W
    art_h = ASCII_ROWS * FONT_H
    width = int(art_w + PAD_X * 2)
    height = int(TITLEBAR_H + art_h + PAD_Y * 2 + FOOTER_H)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Menlo, Consolas, monospace">'
    )

    parts.append(f'''
  <defs>
    <filter id="termGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="titlebarGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#20262e"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <clipPath id="cardClip">
      <rect x="0" y="0" width="{width}" height="{height}" rx="14"/>
    </clipPath>
  </defs>

  <g clip-path="url(#cardClip)">
    <rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117"/>
    <rect x="0" y="0" width="{width}" height="{height}" fill="none"
          stroke="#00f6ff" stroke-opacity="0.18" stroke-width="1.5" rx="14" filter="url(#termGlow)"/>

    <rect x="0" y="0" width="{width}" height="{TITLEBAR_H}" fill="url(#titlebarGrad)"/>
    <circle cx="18" cy="{TITLEBAR_H/2}" r="5.5" fill="#ff5f57"/>
    <circle cx="36" cy="{TITLEBAR_H/2}" r="5.5" fill="#febc2e"/>
    <circle cx="54" cy="{TITLEBAR_H/2}" r="5.5" fill="#28c840"/>
    <text x="{width/2}" y="{TITLEBAR_H/2 + 4}" fill="#8b949e" font-size="12"
          text-anchor="middle">{GITHUB_USERNAME}@github &#8212; ascii-portrait</text>
''')

    # ascii rows with row reveal + sweeping cursor
    for r, line in enumerate(ascii_lines):
        y = TITLEBAR_H + PAD_Y + (r + 1) * FONT_H
        begin = round(r * ROW_STAGGER, 3)
        row_w = len(line) * FONT_W
        colors = ["#39ff88", "#00f6ff", "#c792ea"]
        color = colors[r % len(colors)]

        parts.append(f'''
    <g opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.05s" fill="freeze"/>
      <text x="{PAD_X}" y="{y}" fill="{color}" font-size="{FONT_H}" xml:space="preserve">{esc(line)}</text>
      <rect x="{PAD_X}" y="{y - FONT_H + 2}" width="{FONT_W*1.4:.1f}" height="{FONT_H}" fill="#eafff5" opacity="0.85">
        <animate attributeName="x" from="{PAD_X}" to="{PAD_X + row_w}"
                 begin="{begin}s" dur="{CURSOR_DUR}s" fill="freeze"/>
        <animate attributeName="opacity" values="0.85;0.85;0" keyTimes="0;0.85;1"
                 begin="{begin}s" dur="{CURSOR_DUR}s" fill="freeze"/>
      </rect>
    </g>''')

    # footer typewriter: $ whoami -> name
    footer_y = height - FOOTER_H / 2 + 4
    prompt = "$ whoami"
    cmd_delay = round(len(ascii_lines) * ROW_STAGGER + 0.3, 3)
    name_delay = cmd_delay + len(prompt) * 0.06 + 0.25

    parts.append(f'''
    <line x1="0" y1="{height - FOOTER_H}" x2="{width}" y2="{height - FOOTER_H}" stroke="#21262d" stroke-width="1"/>
''')

    x = PAD_X
    for i, ch in enumerate(prompt):
        cw = FONT_W
        parts.append(f'''
    <text x="{x:.1f}" y="{footer_y}" fill="#39ff88" font-size="12.5" opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{cmd_delay + i*0.06:.3f}s" dur="0.01s" fill="freeze"/>
      {esc(ch)}
    </text>''')
        x += cw

    x = PAD_X + len(prompt) * FONT_W + 10
    for i, ch in enumerate(DISPLAY_NAME):
        parts.append(f'''
    <text x="{x:.1f}" y="{footer_y}" fill="#00f6ff" font-size="12.5" opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="{name_delay + i*0.06:.3f}s" dur="0.01s" fill="freeze"/>
      {esc(ch)}
    </text>''')
        x += FONT_W

    cursor_x = x + 2
    blink_start = name_delay + len(DISPLAY_NAME) * 0.06
    parts.append(f'''
    <rect x="{cursor_x:.1f}" y="{footer_y - FONT_H + 3}" width="7" height="{FONT_H}" fill="#eafff5" opacity="0">
      <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.001;0.5;0.501;1"
               begin="{blink_start:.3f}s" dur="1s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>''')

    return "".join(parts)


def main():
    img = fetch_avatar(GITHUB_USERNAME)
    ascii_lines = image_to_ascii(img, ASCII_COLS, ASCII_ROWS)
    svg = build_svg(ascii_lines)
    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "terminal-card.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
