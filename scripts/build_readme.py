#!/usr/bin/env python3
"""
Injects terminal-card.svg + info-card.svg side-by-side (HTML table) and
github-contribution-animation.svg (centered) into README.md, between
marker comments so it's safe to re-run.
"""
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
README_PATH = os.path.join(REPO_ROOT, "README.md")
ASSETS_DIR = "assets"

START = "<!-- ANIMATED-CARDS:START -->"
END = "<!-- ANIMATED-CARDS:END -->"

BLOCK = f"""{START}
<table>
  <tr>
    <td><img src="{ASSETS_DIR}/terminal-card.svg" alt="ASCII portrait terminal" /></td>
    <td><img src="{ASSETS_DIR}/info-card.svg" alt="Neofetch info card" /></td>
  </tr>
</table>

<p align="center">
  <img src="{ASSETS_DIR}/github-contribution-animation.svg" alt="Animated contribution graph" />
</p>
{END}"""


def main():
    with open(README_PATH, "r") as f:
        content = f.read()

    if START in content and END in content:
        pre = content.split(START)[0]
        post = content.split(END)[1]
        content = pre + BLOCK + post
    else:
        # insert right after the first H1 heading
        lines = content.splitlines()
        insert_at = 1
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_at = i + 1
                break
        lines[insert_at:insert_at] = ["", BLOCK, ""]
        content = "\n".join(lines) + "\n"

    with open(README_PATH, "w") as f:
        f.write(content)

    print(f"README updated at {README_PATH}")


if __name__ == "__main__":
    main()
