#!/usr/bin/env python3
"""Mesure de la mémoire « au repos » d'un bureau Linux dans QEMU, identique pour tous les systèmes.

Protocole (docs/COMPARISON.md) :
 1. démarrage direct du noyau, disque en lecture seule (snapshot), connexion automatique ;
 2. le service boot-check.sh envoie un rapport sur le port série quand le shell de bureau est lancé,
    puis un bloc mémoire par minute pendant 8 minutes ;
 3. ce banc prend une capture d'écran toutes les 15 s : le bureau est « affiché » quand plus de 60 %
    des pixels ne sont pas noirs sur deux captures de suite ;
 4. on retient le premier bloc mémoire arrivé AU MOINS 90 s après cet affichage, avec une capture
    d'écran prise à ce moment comme preuve.
Mémoire utilisée = MemTotal − MemAvailable (même définition que « free » et que le script Windows).

Usage : measure_idle.py <disque.img> <vmlinuz> <initrd> <sortie.txt> [RAM_Mio=4096]
Processeur virtuel : Nehalem (variable CPU) — avec « max », llvmpipe plante sous émulation TCG.
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

SETTLE_S = 90


def qmp(sock: Path, cmd: str, **args) -> dict:
    s = socket.socket(socket.AF_UNIX)
    s.settimeout(30)
    s.connect(str(sock))
    f = s.makefile("rw")
    f.readline()
    f.write(json.dumps({"execute": "qmp_capabilities"}) + "\n"); f.flush(); f.readline()
    f.write(json.dumps({"execute": cmd, "arguments": args}) + "\n"); f.flush()
    r = json.loads(f.readline())
    s.close()
    return r


def screenshot(sock: Path, png: Path) -> float:
    """Capture l'écran ; renvoie la fraction de pixels non noirs."""
    ppm = png.with_suffix(".ppm")
    qmp(sock, "screendump", filename=str(ppm))
    time.sleep(0.5)
    im = Image.open(ppm).convert("RGB")
    small = im.resize((160, 100))
    raw = small.tobytes()
    frac = sum(1 for i in range(0, len(raw), 3) if max(raw[i:i + 3]) > 8) / (len(raw) // 3)
    im.resize((960, int(960 * im.height / im.width))).save(png)
    ppm.unlink(missing_ok=True)
    return frac


def main() -> int:
    img, kernel, initrd, out = sys.argv[1:5]
    ram = sys.argv[5] if len(sys.argv) > 5 else "4096"
    out = Path(out)
    serial, sock = out.with_suffix(".serial"), out.with_suffix(".qmp")
    serial.write_text(""); sock.unlink(missing_ok=True)
    accel = "kvm" if os.access("/dev/kvm", os.W_OK) else "tcg"
    cpu = os.environ.get("CPU", "Nehalem")
    q = subprocess.Popen(["qemu-system-x86_64", "-machine", f"q35,accel={accel}", "-cpu", cpu, "-smp", "4", "-m", ram,
                          "-drive", f"file={img},format=raw,if=virtio,snapshot=on",
                          "-kernel", kernel, "-initrd", initrd,
                          "-append", "root=/dev/vda rw console=ttyS0 quiet nexos.autotest=1",
                          "-vga", "virtio", "-display", "none", "-serial", f"file:{serial}",
                          "-nic", "user,model=virtio-net-pci", "-no-reboot",
                          "-qmp", f"unix:{sock},server=on,wait=off"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t_start = time.time()
    text = lambda: serial.read_text(errors="replace").replace("\r", "")
    blocks_seen: list[tuple[float, str]] = []      # (heure d'arrivée, bloc)
    visible_at = None; streak = 0; chosen = None; report = ""
    try:
        while time.time() - t_start < 3600 and q.poll() is None:
            time.sleep(5)
            t = text()
            if not report:
                m = re.search(r"NEXOS-REPORT-BEGIN.*?NEXOS-REPORT-END", t, re.S)
                if not m:
                    continue
                report = m.group(0); t_report = time.time(); last_shot = 0.0
            for b in re.findall(r"NEXOS-MEM-BEGIN.*?NEXOS-MEM-END", t, re.S)[len(blocks_seen):]:
                blocks_seen.append((time.time(), b))
            if visible_at is None and time.time() - last_shot >= 15:
                last_shot = time.time()
                frac = screenshot(sock, out.with_name(out.stem + "-affichage.png"))
                streak = streak + 1 if frac > 0.6 else 0
                if streak >= 2:
                    visible_at = time.time()
            if visible_at is not None:
                late = [b for (ta, b) in blocks_seen if ta - visible_at >= SETTLE_S]
                if late and chosen is None:
                    chosen = late[0]
                    screenshot(sock, out.with_name(out.stem + "-preuve.png"))
                if len(late) >= 3:      # deux blocs de plus : montre si la mémoire est stabilisée
                    break
            if len(blocks_seen) >= 8:
                break
    finally:
        q.kill(); q.wait()
    lines = [f"accel={accel} cpu={cpu} ram_mib={ram} image={Path(img).name}"]
    if visible_at is not None:
        lines.append(f"bureau_affiche_apres_rapport_s={int(visible_at - t_report)}")
    lines += [report, chosen or "MESURE-INVALIDE : bureau jamais affiché ou aucun bloc 90 s après l'affichage"]
    serie = [int(re.search(r"^used_kib=(\d+)", b, re.M).group(1)) // 1024 for _, b in blocks_seen]
    lines.append("serie_used_mib_par_minute=" + ",".join(map(str, serie)))
    out.write_text("\n".join(lines) + "\n")
    print(out.read_text())
    return 0 if chosen else 1


if __name__ == "__main__":
    sys.exit(main())
