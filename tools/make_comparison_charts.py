#!/usr/bin/env python3
"""Graphiques de comparaison (docs/assets/) à partir des rapports bruts de
docs/measurements/comparaison/*.txt — aucune valeur saisie à la main."""
import re
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs/measurements/comparaison"
OUT = ROOT / "docs/assets"
import sys
LANG = sys.argv[1] if len(sys.argv) > 1 else "fr"
SYSTEMS = [("nexos", "NexOS 0.3"), ("debian-kde", "Debian 13 KDE*"), ("kubuntu", "Kubuntu 24.04*"), ("ubuntu", "Ubuntu 24.04*")]
T = {"fr": dict(mem="Mémoire utilisée au repos (plus court = mieux)", boot="Démarrage, partie système (plus court = mieux)",
                memu="Mio", memn="Médiane de 3 mesures (points). VM 4 Gio, 90 s après l'affichage du bureau. * référence minimale, sans paquets recommandés.",
                bootn="Premier démarrage en émulation logicielle : valeurs relatives seulement. * référence minimale (sans paquets recommandés).", sfx=""),
     "en": dict(mem="Idle memory used (shorter is better)", boot="Boot time, userspace (shorter is better)",
                memu="MiB", memn="Median of 3 runs (dots). 4 GiB VM, 90 s after the desktop is displayed. * minimal reference, without recommended packages.",
                bootn="First boot under software emulation: relative values only. * minimal reference (without recommended packages).", sfx="-en")}[LANG]


def runs(key):
    mem, boot = [], []
    for f in sorted(SRC.glob(f"{key}-r?.txt")):
        t = f.read_text()
        mem.append(int(re.search(r"^used_kib=(\d+)", t[t.index("NEXOS-MEM-BEGIN"):], re.M).group(1)) / 1024)
        m = re.search(r"\+ (?:(\d+)min )?([\d.]+)s \(userspace\)", t)
        boot.append(int(m.group(1) or 0) * 60 + float(m.group(2)))
    return mem, boot


data = {k: runs(k) for k, _ in SYSTEMS}
THEMES = {
    "light": dict(bg="#FFFFFF", ink="#1B2433", muted="#5B6578", grid="#E3E7EE", other="#A7B0BF", brand="#2E7CF6"),
    "dark": dict(bg="#0D1117", ink="#E6EDF3", muted="#9AA6B8", grid="#263041", other="#5C6779", brand="#4C8DF8"),
}


def chart(idx, title, unit, fname, note):
    for mode, c in THEMES.items():
        fig, ax = plt.subplots(figsize=(8, 3.3), dpi=150)
        fig.patch.set_facecolor(c["bg"]); ax.set_facecolor(c["bg"])
        labels = [lab for _, lab in SYSTEMS][::-1]
        for y, (key, lab) in enumerate(SYSTEMS[::-1]):
            vals = data[key][idx]
            med = statistics.median(vals)
            col = c["brand"] if key == "nexos" else c["other"]
            ax.barh(y, med, height=0.52, color=col, zorder=2)
            ax.scatter(vals, [y] * len(vals), s=14, color=c["bg"], edgecolors=c["ink"], linewidths=0.8, zorder=3)
            ax.text(max(vals) + max(max(v[idx]) for v in data.values()) * 0.015, y,
                    (f"{med:,.0f} {unit}".replace(",", " ") if LANG == "fr" else f"{med:,.0f} {unit}"), va="center", ha="left", color=c["ink"], fontsize=9.5,
                    fontweight="bold" if key == "nexos" else "normal")
        ax.set_yticks(range(len(labels)), labels, color=c["ink"], fontsize=10)
        ax.tick_params(axis="x", colors=c["muted"], labelsize=8.5); ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color=c["grid"], linewidth=0.8, zorder=0)
        for s in ax.spines.values(): s.set_visible(False)
        ax.set_xlim(0, max(max(v[idx]) for v in data.values()) * 1.18)
        ax.set_title(title, loc="left", color=c["ink"], fontsize=12, fontweight="bold", pad=10)
        fig.text(0.01, 0.01, note, color=c["muted"], fontsize=7.5)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        fig.savefig(OUT / f"{fname}-{mode}.png", facecolor=c["bg"]); plt.close(fig)


chart(0, T["mem"], T["memu"], "comparaison-memoire" + T["sfx"], T["memn"])
chart(1, T["boot"], "s", "comparaison-demarrage" + T["sfx"], T["bootn"])
for k, lab in SYSTEMS:
    m, b = data[k]
    print(f"{lab}: mémoire {[round(x) for x in m]} médiane {statistics.median(m):.0f} | démarrage {[round(x,1) for x in b]} médiane {statistics.median(b):.1f}")
