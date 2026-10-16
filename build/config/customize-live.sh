#!/usr/bin/env bash
# Personnalisation de l'édition ISO (live + installateur). $1 = racine de l'image.
set -euo pipefail
R="$1"
# GRUB pour le système installé : .deb embarqués (installés hors ligne par Calamares).
POOL="$R/usr/share/nexos/installer/pool"; mkdir -p "$POOL"
( cd "$POOL" && APT_CONFIG="${MMDEBSTRAP_APT_CONFIG:?}" apt-get download -q grub-pc grub-efi-amd64 )
ls "$POOL"
# Pas de fstab fixe sur le support live (Calamares génère celui du système installé).
: > "$R/etc/fstab"
# Lanceur d'installation : icône sur le bureau du compte live + entrée de menu.
mkdir -p "$R/home/nexos/Desktop"
cp "$R/usr/share/applications/org.nexos.Installer.desktop" "$R/home/nexos/Desktop/"
chmod 755 "$R/home/nexos/Desktop/org.nexos.Installer.desktop"
rm -f "$R/usr/share/applications/calamares-install-debian.desktop" "$R/etc/xdg/autostart/calamares-desktop-icon.desktop"
chroot "$R" chown -R nexos:nexos /home/nexos
# initramfs avec live-boot (démarrage depuis le squashfs).
chroot "$R" update-initramfs -u -k all >/dev/null
