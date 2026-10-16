#!/usr/bin/env bash
# Construit le système de fichiers racine du prototype NexOS avec mmdebstrap.
# N'écrit que dans $OUT (par défaut ./out) : aucune modification du système hôte.
#
# Variables :
#   SUITE   (défaut trixie)                 distribution de base
#   MIRROR  (défaut http://deb.debian.org/debian)
#   KERNEL  (défaut linux-image-amd64)      paquet noyau
#   OUT     (défaut ./out)
# Exemple de repli testé dans un environnement sans accès Debian :
#   SUITE=noble MIRROR=http://archive.ubuntu.com/ubuntu KERNEL=linux-image-virtual ./build/build-rootfs.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SUITE="${SUITE:-trixie}"
MIRROR="${MIRROR:-http://deb.debian.org/debian}"
KERNEL="${KERNEL:-linux-image-amd64}"
OUT="${OUT:-$PWD/out}"
ROOTFS="$OUT/rootfs.tar"

mkdir -p "$OUT"
pkgs="$(grep -vE '^\s*(#|$)' "$HERE/config/packages-base.list" | paste -sd, -),$KERNEL"

case "$SUITE" in
  noble|jammy) components="main,universe" ;;
  *)           components="main,non-free-firmware" ;;
esac

# NB : root sans mot de passe = PROTOTYPE VM UNIQUEMENT (console de test).
echo ">> mmdebstrap $SUITE depuis $MIRROR"
mmdebstrap \
  --variant=minbase \
  --components="$components" \
  --include="$pkgs" \
  --customize-hook="cp -a '$HERE/config/overlay/.' \"\$1/\"" \
  --customize-hook='echo nexos > "$1/etc/hostname"' \
  --customize-hook='printf "127.0.0.1 localhost\n127.0.1.1 nexos\n" > "$1/etc/hosts"' \
  --customize-hook='printf "/dev/vda / ext4 defaults 0 1\n" > "$1/etc/fstab"' \
  --customize-hook="sed -i 's/^PRETTY_NAME=.*/PRETTY_NAME=\"NexOS 0.1 prototype (base $SUITE)\"/' \"\$1/usr/lib/os-release\"" \
  --customize-hook='chroot "$1" passwd -d root' \
  --customize-hook="for s in \$(grep -vE '^\\s*(#|\$)' '$HERE/config/services.list'); do chroot \"\$1\" systemctl enable \"\$s\"; done" \
  "$SUITE" "$ROOTFS" "$MIRROR"

echo ">> rootfs : $ROOTFS ($(du -h "$ROOTFS" | cut -f1))"
