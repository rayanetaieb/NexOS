#!/usr/bin/env bash
# Applique le design du dépôt à la racine d'aperçu et repart d'un profil utilisateur vierge.
set -euo pipefail
ROOT="$1"; REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cp -a "$REPO/build/config/overlay-desktop/." "$ROOT/"
python3 "$REPO/branding/plasma/make_theme.py" "$ROOT" >/dev/null
T=$(mktemp -d); OUT=$T "$REPO/build/render-branding.sh" >/dev/null; cp -a "$T/branding-root/." "$ROOT/"; rm -rf "$T"
rm -rf "$ROOT/home/nexos/.config/plasma"* "$ROOT/home/nexos/.config/kdeglobals" "$ROOT/home/nexos/.config/kwinrc" \
       "$ROOT/home/nexos/.local/share/plasma"* "$ROOT/home/nexos/.cache"
echo "design appliqué"
