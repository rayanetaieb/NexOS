#!/usr/bin/env python3
"""Génère l'identité Plasma de NexOS (aucune ressource KDE copiée) :
- Style Plasma « nexos » (desktoptheme) : cadres SVG 9 parties, arrondis, verre sombre,
  liseré d'accent ; couleurs liées au schéma actif (ColorScheme-*) → clair/sombre auto.
- Schémas de couleurs « NexOS Sombre » et « NexOS Clair ».
- Décoration de fenêtres Aurorae « NexOS » (boutons hexagonaux).
Usage : make_theme.py <racine de sortie>   (écrit sous usr/share/...)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ACCENT = (1, 175, 242)

STYLE = """<style type="text/css" id="current-color-scheme">
 .ColorScheme-Background {{ color:{bg}; }}
 .ColorScheme-Text {{ color:{fg}; }}
 .ColorScheme-Highlight {{ color:#01AFF2; }}
</style>"""


def frame_svg(r: int, fill_op: float, border_op: float, margin: int, prefix: str = "",
              bg: str = "#14181d", fg: str = "#e6edf3", extra: str = "") -> str:
    """Cadre Plasma : éléments topleft/top/…/center + hint-*-margin. r = rayon d'arrondi."""
    c = 16                      # taille du centre dans le fichier (étiré par Plasma)
    W = H = 2 * r + c
    p = prefix
    b = 1.0                     # épaisseur du liseré
    parts = []

    def corner(name, ccx, ccy, a0, a1):
        """Quart de disque de centre (ccx, ccy) entre les angles a0→a1 (degrés, y vers le bas)."""
        def arc(rad):
            x0, y0 = ccx + rad * math.cos(math.radians(a0)), ccy + rad * math.sin(math.radians(a0))
            x1, y1 = ccx + rad * math.cos(math.radians(a1)), ccy + rad * math.sin(math.radians(a1))
            sweep = 1 if a1 > a0 else 0
            return f"M{ccx:.2f},{ccy:.2f} L{x0:.2f},{y0:.2f} A{rad},{rad} 0 0 {sweep} {x1:.2f},{y1:.2f} Z"
        parts.append(f'<g id="{p}{name}">'
                     f'<path d="{arc(r)} {arc(r - b)}" fill-rule="evenodd" class="ColorScheme-Highlight" fill="currentColor" fill-opacity="{border_op}"/>'
                     f'<path d="{arc(r - b)}" class="ColorScheme-Background" fill="currentColor" fill-opacity="{fill_op}"/></g>')

    corner("topleft", r, r, 270, 180)
    corner("topright", r + c, r, 270, 360)
    corner("bottomleft", r, r + c, 180, 90)
    corner("bottomright", r + c, r + c, 0, 90)

    def edge(name, x, y, w, h, lx, ly, lw, lh):
        parts.append(f'<g id="{p}{name}">'
                     f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="ColorScheme-Background" fill="currentColor" fill-opacity="{fill_op}"/>'
                     f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" class="ColorScheme-Highlight" fill="currentColor" fill-opacity="{border_op}"/></g>')

    # fond sans recouvrement du liseré (sinon les transparences s'additionnent)
    edge("top", r, b, c, r - b, r, 0, c, b)
    edge("bottom", r, r + c, c, r - b, r, 2 * r + c - b, c, b)
    edge("left", b, r, r - b, c, 0, r, b, c)
    edge("right", r + c, r, r - b, c, 2 * r + c - b, r, b, c)
    parts.append(f'<rect id="{p}center" x="{r}" y="{r}" width="{c}" height="{c}" '
                 f'class="ColorScheme-Background" fill="currentColor" fill-opacity="{fill_op}"/>')
    hints = "".join(
        f'<rect id="{p}hint-{s}-margin" x="{W + 4}" y="{i * (margin + 2)}" width="{margin}" height="{margin}" fill="none"/>'
        for i, s in enumerate(("top", "bottom", "left", "right")))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + margin + 8}" height="{max(H, 4 * (margin + 2))}">'
            f'{STYLE.format(bg=bg, fg=fg)}{"".join(parts)}{hints}{extra}</svg>')


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def desktoptheme(root: Path):
    t = root / "usr/share/plasma/desktoptheme/nexos"
    write(t / "metadata.json", json.dumps({
        "KPlugin": {"Id": "nexos", "Name": "NexOS", "Description": "Style Plasma NexOS : îlots en verre sombre, accent bleu",
                    "Authors": [{"Name": "NexOS"}], "License": "GPL-2.0-or-later", "Version": "0.3"},
        "X-Plasma-API-Minimum-Version": "6.0"}, ensure_ascii=False, indent=1))
    write(t / "plasmarc", "[Settings]\nFallbackTheme=default\n\n[ContrastEffect]\nenabled=false\n\n[BlurBehindEffect]\nenabled=false\n")
    # Panneau « îlot » : très arrondi, quasi opaque (pas de flou → coût GPU nul)
    write(t / "widgets/panel-background.svg", frame_svg(r=18, fill_op=0.94, border_op=0.30, margin=6))
    # Menus, fenêtres contextuelles, calendrier…
    write(t / "dialogs/background.svg", frame_svg(r=16, fill_op=0.97, border_op=0.25, margin=12))
    write(t / "widgets/tooltip.svg", frame_svg(r=10, fill_op=0.97, border_op=0.35, margin=8))
    write(t / "widgets/background.svg", frame_svg(r=16, fill_op=0.85, border_op=0.20, margin=14))
    write(t / "solid/widgets/panel-background.svg", frame_svg(r=18, fill_op=1.0, border_op=0.30, margin=6))
    write(t / "solid/dialogs/background.svg", frame_svg(r=16, fill_op=1.0, border_op=0.25, margin=12))
    write(t / "opaque/widgets/panel-background.svg", frame_svg(r=18, fill_op=1.0, border_op=0.30, margin=6))
    write(t / "opaque/dialogs/background.svg", frame_svg(r=16, fill_op=1.0, border_op=0.25, margin=12))


def colors(root: Path):
    """Palettes NexOS (inspirées du logo : anthracite + bleu #01AFF2)."""
    def scheme(name, dark):
        if dark:
            win, view, btn, text, inactive, tip = "22,27,33", "17,21,26", "30,36,44", "230,237,243", "139,150,161", "12,15,19"
            header = "14,18,22"
        else:
            win, view, btn, text, inactive, tip = "240,244,247", "252,253,254", "232,237,241", "28,32,38", "104,114,124", "250,251,252"
            header = "226,232,237"
        acc = "1,175,242"; acc_text = "255,255,255" if dark else "255,255,255"
        link = "64,196,255" if dark else "0,121,176"
        def group(g, bg, alt):
            return (f"[Colors:{g}]\nBackgroundNormal={bg}\nBackgroundAlternate={alt}\nForegroundNormal={text}\n"
                    f"ForegroundInactive={inactive}\nForegroundActive={acc}\nForegroundLink={link}\nForegroundVisited=155,89,182\n"
                    f"ForegroundNegative=237,85,85\nForegroundNeutral=246,180,60\nForegroundPositive=46,204,113\n"
                    f"DecorationFocus={acc}\nDecorationHover={acc}\n\n")
        out = (f"[General]\nColorScheme={name.replace(' ', '')}\nName={name}\nshadeSortColumn=true\n\n"
               f"[KDE]\ncontrast=4\n\n")
        out += group("Window", win, view)
        out += group("View", view, win)
        out += group("Button", btn, win)
        out += group("Complementary", tip, view)
        out += group("Header", header, win)
        out += group("Header][Inactive", header, win)
        out += group("Tooltip", tip, view)
        out += (f"[Colors:Selection]\nBackgroundNormal={acc}\nBackgroundAlternate=0,140,196\nForegroundNormal={acc_text}\n"
                f"ForegroundInactive=210,240,252\nForegroundActive=255,255,255\nForegroundLink=255,255,255\n"
                f"ForegroundVisited=230,230,255\nForegroundNegative=255,200,200\nForegroundNeutral=255,240,200\n"
                f"ForegroundPositive=200,255,220\nDecorationFocus={acc}\nDecorationHover={acc}\n\n")
        out += (f"[WM]\nactiveBackground={header}\nactiveForeground={text}\ninactiveBackground={header}\n"
                f"inactiveForeground={inactive}\nactiveBlend={header}\ninactiveBlend={header}\n")
        return out
    d = root / "usr/share/color-schemes"
    dark = scheme("NexOS Sombre", True)
    write(d / "NexOSDark.colors", dark)
    write(d / "NexOSLight.colors", scheme("NexOS Clair", False))
    # KDE lit les couleurs dans kdeglobals (le nom du schéma seul ne suffit pas) :
    # kdeglobals système = réglages NexOS + couleurs du schéma sombre par défaut.
    colors_only = dark[dark.index("[Colors:"):]
    write(root / "etc/xdg/kdeglobals",
          "[KDE]\nLookAndFeelPackage=org.nexos.desktop.dark\nwidgetStyle=Breeze\nSingleClick=false\n\n"
          "[General]\nColorScheme=NexOSDark\nAccentColor=1,175,242\nfont=Inter,10\nmenuFont=Inter,10\n"
          "toolBarFont=Inter,9\nsmallestReadableFont=Inter,8\n\n[Icons]\nTheme=breeze-dark\n\n" + colors_only)


def hexagon(cx, cy, r):
    return " ".join(f"{cx + r * math.cos(math.radians(a)):.2f},{cy + r * math.sin(math.radians(a)):.2f}"
                    for a in range(-90, 270, 60))


def aurorae(root: Path):
    """Décoration de fenêtres : barre de titre unie, boutons hexagonaux discrets à droite."""
    a = root / "usr/share/aurorae/themes/NexOS"
    bar = "#0E1216"
    write(a / "metadata.desktop", "[Desktop Entry]\nName=NexOS\nComment=Décoration de fenêtres NexOS\n"
          "X-KDE-PluginInfo-Name=NexOS\nX-KDE-PluginInfo-Version=0.3\nX-KDE-PluginInfo-License=GPL\n"
          "X-KDE-ServiceTypes=KWin/Decoration\nX-Plasma-API=declarativeappletscript\n")
    write(a / "NexOSrc", "[General]\nActiveTextColor=230,237,243\nInactiveTextColor=120,130,140\n"
          "TitleAlignment=Center\nTitleVerticalAlignment=Center\nAnimation=120\nUseTextShadow=false\n"
          "Shadow=true\n\n[Layout]\nBorderLeft=1\nBorderRight=1\nBorderBottom=1\nTitleEdgeTop=6\nTitleEdgeBottom=6\n"
          "TitleEdgeLeft=10\nTitleEdgeRight=10\nTitleHeight=22\nButtonWidth=22\nButtonHeight=22\nButtonSpacing=6\n"
          "ButtonMarginTop=0\nExplicitButtonSpacer=10\nPaddingTop=0\nPaddingBottom=0\nPaddingLeft=0\nPaddingRight=0\n")
    # décoration (9 parties) : même générateur que les cadres, couleur fixe, arrondi en haut
    deco = frame_svg(r=10, fill_op=1.0, border_op=0.0, margin=1, prefix="decoration-", bg=bar)
    deco_in = frame_svg(r=10, fill_op=1.0, border_op=0.0, margin=1, prefix="decoration-inactive-", bg="#15191E")
    # Aurorae attend un seul fichier avec les deux jeux d'éléments
    body = deco[deco.index(">") + 1:deco.rindex("</svg>")] + deco_in[deco_in.index("</style>") + 8:deco_in.rindex("</svg>")]
    write(a / "decoration.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80">' + body + "</svg>")

    def button(fname, glyph, color):
        states = ("active", "hover", "pressed", "inactive", "deactivated")
        elems = []
        for i, st in enumerate(states):
            x = i * 26
            fill = {"active": "none", "hover": color, "pressed": color, "inactive": "none", "deactivated": "none"}[st]
            stroke = {"active": "#8B96A1", "hover": color, "pressed": color, "inactive": "#4A535C", "deactivated": "#30363C"}[st]
            gcol = {"active": "#C9D2DA", "hover": "#FFFFFF", "pressed": "#FFFFFF", "inactive": "#6B747D", "deactivated": "#3A4148"}[st]
            op = "0.85" if st == "pressed" else "1"
            elems.append(f'<g id="{st}-center"><rect x="{x}" y="0" width="22" height="22" fill="#000" fill-opacity="0.004"/>'
                         f'<polygon points="{hexagon(x + 11, 11, 9)}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1.4"/>'
                         f'{glyph(x + 11, 11, gcol)}</g>')
        write(a / f"{fname}.svg", f'<svg xmlns="http://www.w3.org/2000/svg" width="{26 * 5}" height="22">{"".join(elems)}</svg>')

    button("close", lambda x, y, c: f'<path d="M{x - 3},{y - 3} L{x + 3},{y + 3} M{x + 3},{y - 3} L{x - 3},{y + 3}" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>', "#E5484D")
    button("maximize", lambda x, y, c: f'<rect x="{x - 3.2}" y="{y - 3.2}" width="6.4" height="6.4" rx="1" fill="none" stroke="{c}" stroke-width="1.4"/>', "#01AFF2")
    button("restore", lambda x, y, c: f'<rect x="{x - 3.5}" y="{y - 1.5}" width="5" height="5" rx="1" fill="none" stroke="{c}" stroke-width="1.3"/><path d="M{x - 1.5},{y - 3.5} h5 v5" fill="none" stroke="{c}" stroke-width="1.3"/>', "#01AFF2")
    button("minimize", lambda x, y, c: f'<path d="M{x - 3.5},{y + 2} L{x + 3.5},{y + 2}" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>', "#01AFF2")


if __name__ == "__main__":
    out = Path(sys.argv[1])
    desktoptheme(out); colors(out); aurorae(out)
    print("thème NexOS généré dans", out)
