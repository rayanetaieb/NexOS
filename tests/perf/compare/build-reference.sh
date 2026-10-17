#!/usr/bin/env bash
# Construit un système de RÉFÉRENCE (autre distribution, configuration d'origine) pour la comparaison,
# directement depuis les dépôts officiels, avec le MÊME outillage de mesure que NexOS :
#   - même rapport série (boot-check.sh + service, n'agit que pour mesurer),
#   - connexion automatique d'un compte « test » sur la session par défaut de la distribution.
# Rien d'autre n'est modifié : paquets, services et réglages restent ceux de la distribution.
# Usage : build-reference.sh <debian-kde|kubuntu|ubuntu> <dossier_sortie>
# Sortie : <dossier>/<nom>.img (ext4), vmlinuz, initrd.img, packages.txt
set -euo pipefail
NAME=$1 OUT=$2
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$HERE/../../.."
mkdir -p "$OUT"; ROOT="$OUT/root"; rm -rf "$ROOT"
PROXY=(); [ -n "${APT_PROXY:-}" ] && PROXY=(--aptopt="Acquire::http::Proxy \"$APT_PROXY\"" --aptopt="Acquire::https::Proxy \"$APT_PROXY\"")
[ -n "${APT_CAINFO:-}" ] && PROXY+=(--aptopt="Acquire::https::CaInfo \"$APT_CAINFO\"" --aptopt='APT::Sandbox::User "root"')
case "$NAME" in
  debian-kde)   # ce qu'installe l'installateur Debian 13 avec « KDE Plasma » coché
    SUITE=trixie; KEYRING="$REPO/out/live/debian-archive-keyring.gpg"
    PKGS="task-desktop,task-kde-desktop,task-french,task-french-kde-desktop,linux-image-amd64,initramfs-tools"
    MIRRORS=("deb https://deb.debian.org/debian trixie main contrib non-free-firmware"
             "deb https://deb.debian.org/debian trixie-updates main contrib non-free-firmware"
             "deb https://deb.debian.org/debian-security trixie-security main contrib non-free-firmware")
    DM=sddm; SESSION=plasma ;;
  kubuntu)      # métapaquet officiel kubuntu-desktop (Kubuntu 24.04 LTS)
    SUITE=noble; KEYRING=/usr/share/keyrings/ubuntu-archive-keyring.gpg
    PKGS="kubuntu-desktop,linux-generic,language-pack-fr,language-pack-kde-fr"
    MIRRORS=("deb https://archive.ubuntu.com/ubuntu noble main restricted universe multiverse"
             "deb https://archive.ubuntu.com/ubuntu noble-updates main restricted universe multiverse"
             "deb https://security.ubuntu.com/ubuntu noble-security main restricted universe multiverse")
    DM=sddm; SESSION=plasma ;;   # session par défaut de Kubuntu 24.04 : Plasma 5.27 X11
  ubuntu)       # métapaquet officiel ubuntu-desktop (Ubuntu 24.04 LTS, GNOME)
    SUITE=noble; KEYRING=/usr/share/keyrings/ubuntu-archive-keyring.gpg
    PKGS="ubuntu-desktop,linux-generic,language-pack-fr,language-pack-gnome-fr"
    MIRRORS=("deb https://archive.ubuntu.com/ubuntu noble main restricted universe multiverse"
             "deb https://archive.ubuntu.com/ubuntu noble-updates main restricted universe multiverse"
             "deb https://security.ubuntu.com/ubuntu noble-security main restricted universe multiverse")
    DM=gdm3; SESSION=ubuntu ;;
  *) echo "inconnu : $NAME"; exit 2 ;;
esac
OV="$REPO/build/config/overlay"
mmdebstrap --variant=important --format=directory --keyring="$KEYRING" "${PROXY[@]}" \
  --include="$PKGS" \
  --customize-hook="echo test-vm > \"\$1/etc/hostname\"" \
  --customize-hook="chroot \"\$1\" useradd -m -s /bin/bash -G sudo,audio,video test && echo test:test | chroot \"\$1\" chpasswd" \
  --customize-hook="mkdir -p \"\$1/usr/lib/nexos\" && cp '$OV/usr/lib/nexos/boot-check.sh' \"\$1/usr/lib/nexos/\" && cp '$OV/etc/systemd/system/nexos-boot-check.service' \"\$1/etc/systemd/system/\" && chroot \"\$1\" systemctl enable nexos-boot-check.service" \
  --customize-hook="if [ $DM = sddm ]; then mkdir -p \"\$1/etc/sddm.conf.d\"; printf '[Autologin]\nUser=test\nSession=$SESSION\n' > \"\$1/etc/sddm.conf.d/zz-autologin.conf\"; else sed -i 's/^#*\s*AutomaticLoginEnable.*/AutomaticLoginEnable = true/; s/^#*\s*AutomaticLogin\s*=.*/AutomaticLogin = test/' \"\$1/etc/gdm3/custom.conf\"; fi" \
  --customize-hook="printf '/dev/vda / ext4 defaults 0 1\n' > \"\$1/etc/fstab\"; chroot \"\$1\" systemctl set-default graphical.target" \
  --customize-hook="chroot \"\$1\" dpkg-query -W -f='\${Package} \${Version}\n' > '$OUT/packages.txt'" \
  --customize-hook="chroot \"\$1\" apt-get clean" \
  "$SUITE" "$ROOT" "${MIRRORS[@]}"
cp "$(ls -1 "$ROOT"/boot/vmlinuz-* | sort -V | tail -1)" "$OUT/vmlinuz"
cp "$(ls -1 "$ROOT"/boot/initrd.img-* | sort -V | tail -1)" "$OUT/initrd.img"
du -sb "$ROOT" | awk '{printf "taille_installee_octets=%s\n", $1}' > "$OUT/size.txt"
wc -l < "$OUT/packages.txt" | sed 's/^/paquets=/' >> "$OUT/size.txt"
mke2fs -q -t ext4 -L root -d "$ROOT" "$OUT/$NAME.img" 14G
rm -rf "$ROOT"
cat "$OUT/size.txt"
