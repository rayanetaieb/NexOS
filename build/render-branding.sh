#!/usr/bin/env bash
# Rend les éléments graphiques NexOS (SVG → PNG) dans $OUT/branding-root,
# arborescence copiée telle quelle dans l'image. Outils : rsvg-convert, python3.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; B="$HERE/../branding"
OUT="${OUT:-$PWD/out}"; R="$OUT/branding-root"
rm -rf "$R"; mkdir -p "$R"
WP="$R/usr/share/wallpapers/NexOS/contents"
mkdir -p "$WP/images" "$WP/images_dark"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
python3 "$B/make_wallpapers.py" "$tmp" >/dev/null
for res in 3840x2160 1920x1080; do
  w=${res%x*}; h=${res#*x}
  rsvg-convert -w "$w" -h "$h" "$tmp/nexos-wallpaper-light.svg" -o "$WP/images/$res.png"
  rsvg-convert -w "$w" -h "$h" "$tmp/nexos-wallpaper-dark.svg"  -o "$WP/images_dark/$res.png"
done
rsvg-convert -w 400 -h 225 "$tmp/nexos-wallpaper-dark.svg" -o "$WP/screenshot.png"
ICO="$R/usr/share/icons/hicolor/scalable/apps"; mkdir -p "$ICO" "$R/usr/share/pixmaps" "$R/usr/share/nexos/branding"
cp "$B/nexos-mark.svg" "$ICO/nexos-logo.svg"
cp "$B/nexos-mark-white.svg" "$ICO/nexos-start.svg"
cp "$B/nexos-assistant.svg" "$ICO/nexos-assistant.svg"
cp "$B/nexos-python-center.svg" "$ICO/nexos-python-center.svg"
cp "$B/nexos-installer.svg" "$ICO/nexos-installer.svg"
cp "$B"/*.svg "$R/usr/share/nexos/branding/"
rsvg-convert -w 256 "$B/nexos-mark.svg" -o "$R/usr/share/pixmaps/nexos-logo.png"
for s in 16 22 24 32 48 64 128 256; do
  d="$R/usr/share/icons/hicolor/${s}x${s}/apps"; mkdir -p "$d"
  rsvg-convert -w "$s" -h "$s" --keep-aspect-ratio "$B/nexos-mark.svg" -o "$d/nexos-logo.png"
done
echo ">> branding rendu dans $R ($(du -sh "$R" | cut -f1))"
