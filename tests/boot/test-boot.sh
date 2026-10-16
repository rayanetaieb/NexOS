#!/usr/bin/env bash
# Test automatisé : démarre l'image dans QEMU, attend NEXOS-BOOT-OK sur la console
# série, vérifie qu'aucune unité n'est en échec. Code retour 0 = succès.
set -euo pipefail
OUT="${OUT:-$PWD/out}"
TIMEOUT="${TIMEOUT:-600}"
MEM="${MEM:-1024}"
LOG="$OUT/boot-serial.log"
accel=tcg; [ -w /dev/kvm ] && accel=kvm
echo ">> QEMU (accel=$accel, ${MEM} Mio), délai max ${TIMEOUT}s"
start=$(date +%s)
timeout "$TIMEOUT" qemu-system-x86_64 \
  -machine q35,accel=$accel -m "$MEM" -smp 2 -nographic -no-reboot \
  -kernel "$OUT/vmlinuz" -initrd "$OUT/initrd.img" \
  -append "root=/dev/vda rw console=ttyS0 quiet nexos.autotest=1" \
  -drive file="$OUT/nexos.img",format=raw,if=virtio,snapshot=on \
  -nic none > "$LOG" 2>&1 || true
dur=$(( $(date +%s) - start ))
sed -n '/^NEXOS-REPORT-BEGIN/,/^NEXOS-REPORT-END/p' "$LOG" | tr -d '\r'
grep -q NEXOS-BOOT-OK "$LOG" || { echo "ÉCHEC : marqueur absent (voir $LOG)"; exit 1; }
failed=$(grep -a -o 'failed_units=[0-9]*' "$LOG" | tail -1 | cut -d= -f2)
echo ">> durée totale QEMU (démarrage+extinction, accel=$accel) : ${dur}s"
[ "${failed:-1}" = 0 ] || { echo "ÉCHEC : $failed unité(s) en échec"; exit 1; }
echo "SUCCÈS"
