#!/usr/bin/env bash
# Mesure de la mémoire au repos du bureau NexOS dans QEMU (rapport série de boot-check.sh).
# Usage : tests/perf/measure_idle.sh <disque.img> <vmlinuz> <initrd> <sortie.txt> [RAM_MiB=4096]
# Démarrage direct du noyau, session ouverte automatiquement, aucune action pendant la mesure.
# KVM utilisé s'il est disponible, sinon émulation TCG (temps de démarrage NON représentatifs).
# Processeur virtuel Nehalem par défaut : avec « -cpu max », le pilote graphique logiciel (llvmpipe)
# génère des instructions AVX mal émulées par TCG et plante (mesuré le 17/10/2026, voir docs/COMPARISON.md).
set -euo pipefail
IMG=$1 KERNEL=$2 INITRD=$3 OUT=$4 RAM=${5:-4096}
ACCEL=tcg; [ -w /dev/kvm ] && ACCEL=kvm
LOG="$OUT.serial"; : > "$LOG"; SOCK="$OUT.qmp"; rm -f "$SOCK"
qemu-system-x86_64 -machine q35,accel=$ACCEL -cpu "${CPU:-Nehalem}" -smp 4 -m "$RAM" \
  -drive file="$IMG",format=raw,if=virtio,snapshot=on \
  -kernel "$KERNEL" -initrd "$INITRD" -append "root=/dev/vda rw console=ttyS0 quiet nexos.autotest=1" \
  -vga virtio -display none -serial file:"$LOG" -nic user,model=virtio-net-pci -no-reboot -qmp unix:"$SOCK",server=on,wait=off &
QPID=$!
# Capture d'écran 60 s après le rapport de bureau (pendant la période de repos mesurée) :
# preuve que le bureau est réellement affiché.
shot() {
python3 - "$SOCK" "$OUT.ppm" <<'PY' 2>/dev/null || true
import json, socket, sys
s = socket.socket(socket.AF_UNIX); s.connect(sys.argv[1]); f = s.makefile("rw")
f.readline(); f.write('{"execute":"qmp_capabilities"}\n'); f.flush(); f.readline()
f.write(json.dumps({"execute": "screendump", "arguments": {"filename": sys.argv[2]}}) + "\n"); f.flush(); f.readline()
PY
command -v convert >/dev/null && [ -f "$OUT.ppm" ] && convert "$OUT.ppm" -resize 960x "$OUT.png" && rm -f "$OUT.ppm"
}
shot_at=""
for _ in $(seq 1 3600); do
  grep -q NEXOS-MEM-END "$LOG" 2>/dev/null && break
  if [ -z "$shot_at" ] && grep -q NEXOS-REPORT-END "$LOG" 2>/dev/null; then shot_at=$(( $(date +%s) + 60 )); fi
  if [ -n "$shot_at" ] && [ "$shot_at" != done ] && [ "$(date +%s)" -ge "$shot_at" ]; then shot; shot_at=done; fi
  kill -0 $QPID 2>/dev/null || break
  sleep 1
done
sleep 5; kill $QPID 2>/dev/null || true; wait $QPID 2>/dev/null || true
{ echo "accel=$ACCEL ram_mib=$RAM image=$(basename "$IMG")"
  sed -n '/NEXOS-REPORT-BEGIN/,/NEXOS-REPORT-END/p;/NEXOS-MEM-BEGIN/,/NEXOS-MEM-END/p' "$LOG" | tr -d '\r'; } > "$OUT"
grep -q NEXOS-MEM-END "$OUT" && cat "$OUT" || { echo "mesure incomplète (voir $LOG)"; exit 1; }
