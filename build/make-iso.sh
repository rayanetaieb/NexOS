#!/usr/bin/env bash
# Fabrique l'ISO live/installable NexOS à partir de $OUT/rootfs.tar (EDITION=live).
# Démarrage hybride BIOS + UEFI (grub-mkrescue), système en squashfs (live-boot).
# Secure Boot : l'ISO démarre avec shim + GRUB signés de Debian (vérifié sous OVMF avec les clés
# Microsoft, et une ISO non signée y est refusée « Access Denied ») — voir build/iso-pack.sh.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-$PWD/out}"
VERSION="${VERSION:-0.4}"
ISO="$OUT/nexos-$VERSION-amd64.iso"
work="$OUT/iso-work"; root="$work/rootfs"; tree="$work/iso"
rm -rf "$work"; mkdir -p "$root" "$tree/live" "$tree/boot/grub"

echo ">> extraction du rootfs"
tar -C "$root" -xf "$OUT/rootfs.tar"
cp "$(ls -1 "$root"/boot/vmlinuz-* | sort -V | tail -1)" "$tree/live/vmlinuz"
cp "$(ls -1 "$root"/boot/initrd.img-* | sort -V | tail -1)" "$tree/live/initrd.img"

echo ">> squashfs (zstd)"
mksquashfs "$root" "$tree/live/filesystem.squashfs" -comp zstd -Xcompression-level 15 \
  -noappend -quiet -e boot/efi
du -h "$tree/live/filesystem.squashfs" | cut -f1 | sed 's/^/   taille squashfs : /'

# Thème GRUB NexOS (celui du système installé, polices comprises)
fonts=""
if [ -d "$root/usr/share/grub/themes/nexos" ]; then
  mkdir -p "$tree/boot/grub/themes"; cp -r "$root/usr/share/grub/themes/nexos" "$tree/boot/grub/themes/"
  for f in "$tree"/boot/grub/themes/nexos/*.pf2; do fonts+="loadfont /boot/grub/themes/nexos/$(basename "$f")"$'\n'; done
fi
{ cat <<'EOF'
set default=0
set timeout=5
insmod all_video
insmod gfxterm
insmod png
set gfxmode=auto
terminal_output gfxterm
EOF
printf '%s' "$fonts"
[ -n "$fonts" ] && echo 'set theme=/boot/grub/themes/nexos/theme.txt'
cat <<'EOF'

menuentry "Essayer ou installer NexOS" {
    linux /live/vmlinuz boot=live components quiet splash
    initrd /live/initrd.img
}
menuentry "NexOS (mode sans échec graphique)" {
    linux /live/vmlinuz boot=live components nomodeset
    initrd /live/initrd.img
}
menuentry "NexOS (console de diagnostic, sans bureau)" {
    linux /live/vmlinuz boot=live components systemd.unit=multi-user.target console=ttyS0 console=tty0
    initrd /live/initrd.img
}
EOF
} > "$tree/boot/grub/grub.cfg"

echo ">> ISO hybride BIOS/UEFI (UEFI : shim + GRUB signés Debian → Secure Boot activé accepté)"
need=$(( $(du -sm "$tree" | cut -f1) + 300 )); free=$(df -Pm "$OUT" | awk 'NR==2{print $4}')
if [ "$free" -lt "$need" ]; then
  echo "ERREUR : espace disque insuffisant pour écrire l'ISO ($free Mo libres, $need Mo nécessaires)."
  echo "Libérez de la place puis relancez : build/iso-pack.sh $tree $ISO NEXOS_${VERSION//./_} $root"
  exit 1
fi
"$HERE/iso-pack.sh" "$tree" "$ISO" "NEXOS_${VERSION//./_}" "$root"
rm -rf "$root"
( cd "$OUT" && sha256sum "$(basename "$ISO")" > "$(basename "$ISO").sha256" )
ls -lh "$ISO"; cat "$ISO.sha256"
