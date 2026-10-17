#!/usr/bin/env bash
# Construit le système de fichiers racine du prototype NexOS avec mmdebstrap.
# N'écrit que dans $OUT (par défaut ./out) : aucune modification du système hôte.
#
# Variables :
#   SUITE   (défaut trixie)                 distribution de base
#   MIRROR  (défaut http://deb.debian.org/debian)
#   KERNEL  (défaut linux-image-amd64)      paquet noyau
#   OUT     (défaut ./out)
#   KEYRING    (facultatif) trousseau de vérification (voir build/fetch-debian-keyring.sh)
#   APT_PROXY  (facultatif) proxy HTTP(S) utilisé UNIQUEMENT pendant le build
#   APT_CAINFO (facultatif) certificat d'autorité pour ce proxy
# Exemple de repli testé dans un environnement sans accès Debian :
#   SUITE=noble MIRROR=http://archive.ubuntu.com/ubuntu KERNEL=linux-image-virtual ./build/build-rootfs.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUITE="${SUITE:-trixie}"
MIRROR="${MIRROR:-http://deb.debian.org/debian}"
KERNEL="${KERNEL:-linux-image-amd64}"
OUT="${OUT:-$PWD/out}"
EDITION="${EDITION:-base}"             # base | desktop | live (ISO)
ROOTFS="$OUT/rootfs.tar"

mkdir -p "$OUT"
lists=("$HERE/config/packages-base.list")
case "$EDITION" in desktop|live) lists+=("$HERE/config/packages-desktop.list" "$HERE/config/packages-apps.list") ;; esac
[ "$EDITION" = live ] && lists+=("$HERE/config/packages-live.list")
pkgs="$(cat "${lists[@]}" | grep -vE '^\s*(#|$)' | paste -sd, -),$KERNEL"
hooks=()
if [ "$EDITION" = desktop ] || [ "$EDITION" = live ]; then
  "$HERE/render-branding.sh"
  hooks+=(--customize-hook="cp -a '$HERE/config/overlay-desktop/.' \"\$1/\"")
  hooks+=(--customize-hook="cp -a '$OUT/branding-root/.' \"\$1/\"")
  hooks+=(--customize-hook="'$HERE/config/customize-desktop.sh' \"\$1\"")
fi
if [ "$EDITION" = live ]; then
  hooks+=(--customize-hook="cp -a '$HERE/config/overlay-live/.' \"\$1/\"")
  hooks+=(--customize-hook="'$HERE/config/customize-live.sh' \"\$1\"")
fi
if [ "$EDITION" = desktop ] || [ "$EDITION" = live ]; then
  # Audit « rien de lourd au démarrage » : rapport conservé avec l'image (n'arrête pas le build).
  hooks+=(--customize-hook="'$HERE/check-autostart.sh' \"\$1\" > '$OUT/autostart-audit.txt' 2>&1 || true")
fi

case "$SUITE" in
  noble|jammy) components="main,universe" ;;
  *)           components="main,non-free-firmware" ;;
esac

# NB : root sans mot de passe = PROTOTYPE VM UNIQUEMENT (console de test).
aptopts=()
if [ -n "${KEYRING:-}" ]; then aptopts+=(--keyring="$KEYRING"); fi
if [ -n "${APT_PROXY:-}" ]; then
  aptopts+=(--aptopt="Acquire::http::Proxy \"$APT_PROXY\"" --aptopt="Acquire::https::Proxy \"$APT_PROXY\"")
fi
if [ -n "${APT_CAINFO:-}" ]; then
  # _apt ne peut pas lire un CA situé dans un dossier privé : téléchargement en root (build seulement).
  aptopts+=(--aptopt="Acquire::https::CaInfo \"$APT_CAINFO\"" --aptopt="APT::Sandbox::User \"root\"")
fi

echo ">> mmdebstrap $SUITE depuis $MIRROR"
mmdebstrap \
  --variant=minbase \
  --components="$components" \
  --include="$pkgs" \
  "${aptopts[@]}" \
  --customize-hook="cp -a '$HERE/config/overlay/.' \"\$1/\"" \
  --customize-hook='echo nexos > "$1/etc/hostname"' \
  --customize-hook='printf "127.0.0.1 localhost\n127.0.1.1 nexos\n" > "$1/etc/hosts"' \
  --customize-hook='printf "/dev/vda / ext4 defaults 0 1\n" > "$1/etc/fstab"' \
  --customize-hook="sed -i 's/^PRETTY_NAME=.*/PRETTY_NAME=\"NexOS 0.3 prototype $EDITION (base $SUITE)\"/' \"\$1/usr/lib/os-release\"" \
  --customize-hook='chroot "$1" passwd -d root' \
  --customize-hook="for s in \$(grep -vE '^\\s*(#|\$)' '$HERE/config/services.list'); do chroot \"\$1\" systemctl enable \"\$s\"; done" \
  "${hooks[@]}" \
  --customize-hook='chroot "$1" apt-get clean' \
  --customize-hook='rm -f "$1/etc/apt/apt.conf.d/99mmdebstrap"' \
  "$SUITE" "$ROOTFS" "$MIRROR"

echo ">> rootfs : $ROOTFS ($(du -h "$ROOTFS" | cut -f1))"
