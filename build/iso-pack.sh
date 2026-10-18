#!/usr/bin/env bash
# Assemble l'ISO hybride NexOS à partir d'une arborescence prête (live/, boot/grub/grub.cfg, thème).
#   - UEFI : shim + GRUB SIGNÉS de Debian → démarre avec Secure Boot ACTIVÉ (Windows 11 + BitLocker
#            n'ont pas à être touchés). Le noyau Debian est lui-même signé.
#   - BIOS : GRUB i386-pc (El Torito + MBR hybride) pour les vieux PC.
# Usage : iso-pack.sh <arborescence> <sortie.iso> <volid> <dossier_rootfs_avec_shim_et_grub_signés>
set -euo pipefail
TREE=$1 ISO=$2 VOLID=$3 ROOT=$4
SHIM="$ROOT/usr/lib/shim/shimx64.efi.signed"
MM="$ROOT/usr/lib/shim/mmx64.efi.signed"
GCD="$ROOT/usr/lib/grub/x86_64-efi-signed/gcdx64.efi.signed"   # GRUB signé « CD » de Debian
for f in "$SHIM" "$MM" "$GCD"; do [ -f "$f" ] || { echo "manquant : $f"; exit 1; }; done

# Le GRUB signé « CD » cherche /.disk/info puis lit /boot/grub/grub.cfg
mkdir -p "$TREE/.disk"; echo "NexOS $VOLID" > "$TREE/.disk/info"

# Image FAT de démarrage UEFI : chemin de secours standard EFI/BOOT/BOOTX64.EFI = shim
mkdir -p "$TREE/EFI/BOOT" "$TREE/boot/grub"
EFIIMG="$TREE/boot/grub/efi.img"; rm -f "$EFIIMG"
dd if=/dev/zero of="$EFIIMG" bs=1M count=8 status=none
mformat -i "$EFIIMG" ::
mmd -i "$EFIIMG" ::/EFI ::/EFI/BOOT
mcopy -i "$EFIIMG" "$SHIM" ::/EFI/BOOT/BOOTX64.EFI
mcopy -i "$EFIIMG" "$GCD" ::/EFI/BOOT/grubx64.efi
mcopy -i "$EFIIMG" "$MM" ::/EFI/BOOT/mmx64.efi
# mêmes fichiers dans l'arborescence (démarrage depuis une clé copiée « à la main »)
cp "$SHIM" "$TREE/EFI/BOOT/BOOTX64.EFI"; cp "$GCD" "$TREE/EFI/BOOT/grubx64.efi"; cp "$MM" "$TREE/EFI/BOOT/mmx64.efi"

# BIOS : image El Torito GRUB + modules
mkdir -p "$TREE/boot/grub/i386-pc"
cp /usr/lib/grub/i386-pc/*.mod /usr/lib/grub/i386-pc/*.lst "$TREE/boot/grub/i386-pc/"
grub-mkimage -O i386-pc-eltorito -p /boot/grub -o "$TREE/boot/grub/i386-pc/eltorito.img" \
  biosdisk iso9660 part_msdos part_gpt normal search search_fs_file configfile linux \
  all_video gfxterm png font echo test

rm -f "$ISO"
xorriso -as mkisofs -iso-level 3 -full-iso9660-filenames -rational-rock -joliet -joliet-long \
  -volid "$VOLID" \
  -eltorito-boot boot/grub/i386-pc/eltorito.img -no-emul-boot -boot-load-size 4 -boot-info-table \
  --grub2-boot-info --grub2-mbr /usr/lib/grub/i386-pc/boot_hybrid.img \
  -eltorito-alt-boot -e boot/grub/efi.img -no-emul-boot \
  -append_partition 2 0xef "$EFIIMG" -appended_part_as_gpt \
  -o "$ISO" "$TREE" 2>&1 | grep -vE "^xorriso : (UPDATE|NOTE)" | tail -3
ls -l "$ISO"
