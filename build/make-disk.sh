#!/usr/bin/env bash
# Transforme out/rootfs.tar en image disque ext4 (sans root ni périphérique loop)
# et extrait noyau + initramfs pour un démarrage direct QEMU.
set -euo pipefail
OUT="${OUT:-$PWD/out}"
SIZE="${SIZE:-2G}"
work="$OUT/rootfs-dir"
rm -rf "$work" && mkdir -p "$work"
tar -C "$work" -xf "$OUT/rootfs.tar"
# Disque de build limité : DROP_TAR=1 supprime l'archive une fois extraite.
[ "${DROP_TAR:-0}" = 1 ] && rm -f "$OUT/rootfs.tar"
cp "$(ls -1 "$work"/boot/vmlinuz-* | sort -V | tail -1)"  "$OUT/vmlinuz"
cp "$(ls -1 "$work"/boot/initrd.img-* | sort -V | tail -1)" "$OUT/initrd.img"
rm -f "$OUT/nexos.img"
mke2fs -q -t ext4 -L nexos-root -d "$work" "$OUT/nexos.img" "$SIZE"
rm -rf "$work"
echo ">> image : $OUT/nexos.img ; noyau : $OUT/vmlinuz ; initrd : $OUT/initrd.img"
