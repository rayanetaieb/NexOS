#!/usr/bin/env python3
"""Thème GRUB NexOS : fond (Flux sombre assombri + logo), pièces de sélection, theme.txt.
Les polices .pf2 sont générées dans l'image par grub-mkfont (customize-desktop.sh).
Usage : make_grub_theme.py <flux-dark-1920x1080.png> <logo-blanc-256.png> <dossier_sortie>"""
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

bg_path, logo_path, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
bg = Image.open(bg_path).convert("RGB").resize((1920, 1080))
bg = ImageEnhance.Brightness(bg).enhance(0.55)
logo = Image.open(logo_path).convert("RGBA").resize((96, 96))
bg.paste(logo, (150, 150), logo)
bg.save(out / "background.png", optimize=True)
# Sélection : fond bleu nuit + barre d'accent à gauche (9 pièces, seules w/c utilisées)
Image.new("RGBA", (6, 44), (46, 124, 246, 255)).save(out / "select_w.png")
Image.new("RGBA", (8, 44), (20, 32, 58, 235)).save(out / "select_c.png")
Image.new("RGBA", (8, 44), (20, 32, 58, 235)).save(out / "select_e.png")
(out / "theme.txt").write_text("""# Thème GRUB NexOS
desktop-image: "background.png"
desktop-color: "#0B1220"
title-text: ""
terminal-font: "Noto Sans Regular 16"
terminal-box: "select_*.png"

+ label {
    left = 270  top = 162  width = 600  height = 70
    text = "NexOS"  color = "#E8EEF8"  font = "Noto Sans Bold 48"
}
+ boot_menu {
    left = 150  top = 330  width = 900  height = 520
    item_font = "Noto Sans Regular 20"
    selected_item_font = "Noto Sans Bold 20"
    item_color = "#8A9BB8"  selected_item_color = "#FFFFFF"
    item_height = 44  item_padding = 18  item_spacing = 10
    icon_width = 0  icon_height = 0  item_icon_space = 0
    selected_item_pixmap_style = "select_*.png"
    scrollbar = false
}
+ label {
    id = "__timeout__"
    left = 150  top = 940  width = 900  height = 30
    text = "Démarrage automatique dans %d s — flèches pour choisir, Entrée pour démarrer"
    color = "#8A9BB8"  font = "Noto Sans Regular 16"
}
""", encoding="utf-8")
print(out)
