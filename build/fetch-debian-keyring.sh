#!/usr/bin/env bash
# Récupère un trousseau Debian à jour (clés trixie incluses) avec une CHAÎNE DE
# CONFIANCE vérifiée, pour les hôtes de build dont le trousseau est trop ancien
# (ex. Ubuntu 24.04) :
#   1. InRelease de bookworm vérifié par gpgv avec les clés bookworm de l'hôte ;
#   2. index Packages vérifié par son SHA-256 listé dans cet InRelease ;
#   3. paquet debian-archive-keyring vérifié par son SHA-256 listé dans l'index ;
#   4. extraction du trousseau → $OUT/debian-archive-keyring.gpg
# Usage : OUT=out ./build/fetch-debian-keyring.sh
set -euo pipefail
OUT="${OUT:-$PWD/out}"
MIRROR="${KEYRING_MIRROR:-https://deb.debian.org/debian}"
HOSTKEYS="${HOSTKEYS:-/usr/share/keyrings/debian-archive-keyring.gpg}"
CURL=(curl -fsSL ${APT_CAINFO:+--cacert "$APT_CAINFO"})
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
mkdir -p "$OUT"

suite=bookworm
"${CURL[@]}" -o "$work/InRelease" "$MIRROR/dists/$suite/InRelease"
# Règle d'APT : au moins une signature valide et aucune signature invalide
# (une signature par une clé plus récente, inconnue de l'hôte, est ignorée).
gpgv --keyring "$HOSTKEYS" --output "$work/Release" "$work/InRelease" 2>"$work/gpgv.log" || true
if ! grep -q 'Good signature' "$work/gpgv.log" || grep -q 'BAD signature' "$work/gpgv.log"; then
  cat "$work/gpgv.log"; echo "ÉCHEC : signature InRelease"; exit 1
fi
echo ">> 1/4 InRelease $suite : signature valide ($(grep -c 'Good signature' "$work/gpgv.log") signature(s))"

idx="main/binary-all/Packages.xz"
want=$(awk -v f="$idx" '/^SHA256:/{s=1;next} /^[A-Z]/{s=0} s && $3==f {print $1}' "$work/Release")
"${CURL[@]}" -o "$work/Packages.xz" "$MIRROR/dists/$suite/$idx"
echo "$want  $work/Packages.xz" | sha256sum -c --quiet
echo ">> 2/4 index $idx : SHA-256 conforme"

xz -dc "$work/Packages.xz" > "$work/Packages"
read -r path sum < <(awk '/^Package: debian-archive-keyring$/{p=1} p&&/^Filename:/{f=$2} p&&/^SHA256:/{s=$2} p&&/^$/{print f, s; exit}' "$work/Packages")
"${CURL[@]}" -o "$work/keyring.deb" "$MIRROR/$path"
echo "$sum  $work/keyring.deb" | sha256sum -c --quiet
echo ">> 3/4 $(basename "$path") : SHA-256 conforme"

dpkg-deb -x "$work/keyring.deb" "$work/x"
cp "$work/x/usr/share/keyrings/debian-archive-keyring.gpg" "$OUT/debian-archive-keyring.gpg"
echo ">> 4/4 trousseau : $OUT/debian-archive-keyring.gpg"
gpg --show-keys "$OUT/debian-archive-keyring.gpg" 2>/dev/null | grep -E '^uid' | sed 's/^/   /'
