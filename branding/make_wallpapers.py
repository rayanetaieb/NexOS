#!/usr/bin/env python3
"""Génère les fonds d'écran NexOS (SVG) à partir des formes du logo :
grand hexagone en filigrane, tracé « pouls » et point bleu.
Usage : python3 make_wallpapers.py <dossier_sortie>  (puis rsvg-convert → PNG)"""
import math
import sys
from pathlib import Path

BLUE = "#01AFF2"


def hexagon(cx, cy, r):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
           for a in range(-90, 270, 60)]
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def wallpaper(dark: bool, w=3840, h=2160) -> str:
    bg1, bg2 = ("#0F1316", "#1B2228") if dark else ("#F4F7F9", "#DDE7EE")
    line = "#FFFFFF" if dark else "#252121"
    cx, cy, r = w * 0.66, h * 0.50, h * 0.34
    # petits hexagones de trame
    grid = []
    step = 150
    for row in range(-1, h // int(step * 0.866) + 2):
        for col in range(-1, w // step + 2):
            x = col * step + (step / 2 if row % 2 else 0)
            y = row * step * 0.866
            d = math.hypot(x - cx, y - cy)
            op = max(0.0, 0.06 - d / (w * 9))
            if op > 0.004:
                grid.append(f'<path d="{hexagon(x, y, step * 0.5)}" stroke-opacity="{op:.3f}"/>')
    # tracé « pouls » à l'échelle du grand hexagone (proportions du logo)
    k = r / 376
    def p(x, y):
        return f"{cx + (x - 591) * k:.1f} {cy + (y - 898) * k:.1f}"
    pulse = f"M{p(261, 991)} L{p(414, 991)} L{p(492, 768)} L{p(584, 1072)} L{p(700, 772)}"
    dot_x, dot_y = cx + (709 - 591) * k, cy + (747 - 898) * k
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/>
    </linearGradient>
    <radialGradient id="glow"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.45"/>
      <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <g fill="none" stroke="{line}" stroke-width="3">{"".join(grid)}</g>
  <g fill="none" stroke="{line}" opacity="{0.13 if dark else 0.14}" stroke-width="{40 * k:.0f}"
     stroke-linejoin="round" stroke-linecap="round">
    <path d="{hexagon(cx, cy, r)}"/>
    <path d="{pulse}"/>
  </g>
  <circle cx="{dot_x:.1f}" cy="{dot_y:.1f}" r="{38 * k * 3:.0f}" fill="url(#glow)"/>
  <circle cx="{dot_x:.1f}" cy="{dot_y:.1f}" r="{38 * k:.0f}" fill="{BLUE}"/>
</svg>'''


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    (out / "nexos-wallpaper-dark.svg").write_text(wallpaper(True))
    (out / "nexos-wallpaper-light.svg").write_text(wallpaper(False))
    print("ok")
