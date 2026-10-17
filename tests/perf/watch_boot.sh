#!/usr/bin/env bash
# Diagnostic : démarre une image comme measure_idle.sh et prend une capture toutes les 45 s.
# Usage : watch_boot.sh <img> <vmlinuz> <initrd> <dossier_captures> [durée_s=900]
set -uo pipefail
IMG=$1 KERNEL=$2 INITRD=$3 D=$4 DUR=${5:-900}
mkdir -p "$D"; SOCK="$D/qmp.sock"; rm -f "$SOCK"
qemu-system-x86_64 -machine q35,accel=tcg -cpu max -smp 4 -m 4096 \
  -drive file="$IMG",format=raw,if=virtio,snapshot=on -kernel "$KERNEL" -initrd "$INITRD" \
  -append "root=/dev/vda rw console=ttyS0 quiet" -vga virtio -display none -serial file:"$D/serial.log" \
  -nic user,model=virtio-net-pci -qmp unix:"$SOCK",server=on,wait=off &
QPID=$!
for t in $(seq 45 45 "$DUR"); do
  sleep 45
  python3 - "$SOCK" "$D/t$t.ppm" <<'PY'
import json, socket, sys
s = socket.socket(socket.AF_UNIX); s.connect(sys.argv[1]); f = s.makefile("rw")
f.readline(); f.write('{"execute":"qmp_capabilities"}\n'); f.flush(); f.readline()
f.write(json.dumps({"execute": "screendump", "arguments": {"filename": sys.argv[2]}}) + "\n"); f.flush(); f.readline()
PY
  convert "$D/t$t.ppm" -resize 480x "$D/t$t.png" && rm -f "$D/t$t.ppm"
done
kill $QPID
