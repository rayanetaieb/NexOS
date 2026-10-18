#!/usr/bin/env bash
# Sources APT définitives de l'image (dernier crochet du build, après toute utilisation d'APT pendant
# la construction) : version, mises à jour ET CORRECTIFS DE SÉCURITÉ — absents de l'image 0.3.
# contrib/non-free : pilote NVIDIA, steam-devices. Format deb822 (Debian 13). $1 = racine.
set -euo pipefail
R="$1"
rm -f "$R/etc/apt/sources.list"
mkdir -p "$R/etc/apt/sources.list.d"
cat > "$R/etc/apt/sources.list.d/debian.sources" <<'SRC'
Types: deb
URIs: https://deb.debian.org/debian
Suites: trixie trixie-updates
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: https://security.debian.org/debian-security
Suites: trixie-security
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
SRC
