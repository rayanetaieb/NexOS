#!/usr/bin/env bash
# Mesure de la mémoire au repos du bureau NexOS dans QEMU (rapport série de boot-check.sh).
# Usage : tests/perf/measure_idle.sh <disque.img> <vmlinuz> <initrd> <sortie.txt> [RAM_MiB=4096]
# Démarrage direct du noyau, session ouverte automatiquement, aucune action pendant la mesure.
# KVM utilisé s'il est disponible, sinon émulation TCG (temps de démarrage NON représentatifs).
set -euo pipefail
IMG=$1 KERNEL=$2 INITRD=$3 OUT=$4 RAM=${5:-4096}
ACCEL=tcg; [ -w /dev/kvm ] && ACCEL=kvm
LOG="$OUT.serial"; : > "$LOG"
qemu-system-x86_64 -machine q35,accel=$ACCEL -cpu max -smp 4 -m "$RAM" \
  -drive file="$IMG",format=raw,if=virtio,snapshot=on \
  -kernel "$KERNEL" -initrd "$INITRD" -append "root=/dev/vda rw console=ttyS0 quiet nexos.autotest=1" \
  -vga virtio -display none -serial file:"$LOG" -nic user,model=virtio-net-pci -no-reboot &
QPID=$!
for _ in $(seq 1 3600); do
  grep -q NEXOS-MEM-END "$LOG" 2>/dev/null && break
  kill -0 $QPID 2>/dev/null || break
  sleep 1
done
sleep 5; kill $QPID 2>/dev/null || true; wait $QPID 2>/dev/null || true
{ echo "accel=$ACCEL ram_mib=$RAM image=$(basename "$IMG")"
  sed -n '/NEXOS-REPORT-BEGIN/,/NEXOS-REPORT-END/p;/NEXOS-MEM-BEGIN/,/NEXOS-MEM-END/p' "$LOG" | tr -d '\r'; } > "$OUT"
grep -q NEXOS-MEM-END "$OUT" && cat "$OUT" || { echo "mesure incomplète (voir $LOG)"; exit 1; }
