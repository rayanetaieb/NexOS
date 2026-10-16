#!/usr/bin/env python3
"""Fond d'écran NexOS « Flux » (défaut) : dégradé profond, tracés de pouls lumineux
inspirés du logo traversant l'écran, halo bleu. Variantes sombre/claire.
Usage : make_wallpaper_flux.py <dossier_sortie>"""
import math
import random
import sys
from pathlib import Path

BLUE = "#01AFF2"


def pulse_path(y0, w, amp, seed, segments=7):
    rnd = random.Random(seed)
    pts = [(-50, y0)]
    x = -50
    while x < w + 50:
        x += rnd.randint(180, 420)
        pts.append((x, y0))
        if rnd.random() < 0.55:          # motif « battement » du logo
            a = amp * rnd.uniform(0.5, 1.0)
            pts += [(x + 40, y0 - a), (x + 90, y0 + a * 0.75), (x + 140, y0 - a * 0.2), (x + 170, y0)]
            x += 170
    return "M" + " L".join(f"{px:.0f},{py:.0f}" for px, py in pts)


def flux(dark: bool, w=3840, h=2160) -> str:
    if dark:
        g0, g1, g2, line, hexs = "#070A0E", "#0B141C", "#0F2230", "#FFFFFF", 0.035
    else:
        g0, g1, g2, line, hexs = "#F6F9FB", "#E6EEF4", "#D3E4EF", "#0B2233", 0.05
    layers = []
    dot_x, dot_y = w * 0.80, h * 0.36
    y0 = h * 0.60
    # Signal principal : plat, un battement, puis montée vers le point (récit du logo).
    k = 1.6
    main = (f"M-40,{y0:.0f} L{w * 0.48:.0f},{y0:.0f} L{w * 0.48 + 70 * k:.0f},{y0:.0f} "
            f"L{w * 0.48 + 120 * k:.0f},{y0 - 240 * k:.0f} L{w * 0.48 + 190 * k:.0f},{y0 + 120 * k:.0f} "
            f"L{dot_x:.0f},{dot_y:.0f}")
    layers.append(f'<path d="{main}" fill="none" stroke="{BLUE}" stroke-opacity="0.9" stroke-width="9" '
                  f'stroke-linejoin="round" stroke-linecap="round" filter="url(#glow)"/>')
    for y, amp, op, seed in ((0.66, 50, 0.10, 11), (0.53, 70, 0.07, 7)):
        layers.append(f'<path d="{pulse_path(h * y, w, amp, seed)}" fill="none" stroke="{line}" '
                      f'stroke-opacity="{op}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>')
    # trame d'hexagones très discrète, côté droit
    hexes = []
    for row in range(0, 14):
        for col in range(0, 9):
            cx = w * 0.62 + col * 150 + (75 if row % 2 else 0)
            cy = row * 130
            pts = " ".join(f"{cx + 70 * math.cos(math.radians(a)):.0f},{cy + 70 * math.sin(math.radians(a)):.0f}"
                           for a in range(-90, 270, 60))
            fade = max(0.0, 1 - abs(cy - h * 0.55) / (h * 0.6))
            hexes.append(f'<polygon points="{pts}" fill="none" stroke="{line}" stroke-opacity="{hexs * fade:.3f}" stroke-width="3"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{g0}"/><stop offset="0.6" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/>
    </linearGradient>
    <radialGradient id="halo" cx="0.80" cy="0.36" r="0.45">
      <stop offset="0" stop-color="{BLUE}" stop-opacity="{0.22 if dark else 0.18}"/>
      <stop offset="1" stop-color="{BLUE}" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#halo)"/>
  <g>{"".join(hexes)}</g>
  <g>{"".join(layers)}</g>
  <circle cx="{dot_x:.0f}" cy="{dot_y:.0f}" r="40" fill="{BLUE}"/>
  <circle cx="{dot_x:.0f}" cy="{dot_y:.0f}" r="90" fill="{BLUE}" fill-opacity="0.12"/>
</svg>'''


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out.mkdir(parents=True, exist_ok=True)
    (out / "nexos-flux-dark.svg").write_text(flux(True))
    (out / "nexos-flux-light.svg").write_text(flux(False))
    print("ok")
