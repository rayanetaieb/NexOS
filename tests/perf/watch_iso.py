#!/usr/bin/env python3
"""Démarre l'ISO NexOS avec une carte graphique donnée et prend une capture toutes les 40 s.
Sert à reproduire les problèmes d'affichage d'autres hyperviseurs :
  --vga vmware  ≈ VirtualBox « VMSVGA » / VMware (pilote vmwgfx)
  --vga std     ≈ VirtualBox « VBoxVGA » (affichage VGA/VESA simple)
Usage : watch_iso.py <iso> <dossier> [--vga vmware] [--duree 900] [--bios]
"""
from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import time
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("iso"); ap.add_argument("out")
ap.add_argument("--vga", default="vmware"); ap.add_argument("--duree", type=int, default=900)
ap.add_argument("--bios", action="store_true"); ap.add_argument("--cpu", default="Nehalem")
ap.add_argument("--secureboot", action="store_true", help="UEFI avec Secure Boot ACTIVÉ (clés Microsoft, comme un PC Windows 11)")
ap.add_argument("--disk", help="disque qcow2 supplémentaire")
a = ap.parse_args()
d = Path(a.out); d.mkdir(parents=True, exist_ok=True)
sock = d / "qmp.sock"; sock.unlink(missing_ok=True)
cmd = ["qemu-system-x86_64", "-machine", "q35,accel=tcg" + (",smm=on" if a.secureboot else ""), "-cpu", a.cpu, "-smp", "2", "-m", "4096",
       "-vga", a.vga, "-drive", f"file={a.iso},media=cdrom,readonly=on", "-display", "none", "-serial", f"file:{d / 'serial.log'}",
       "-nic", "user,model=e1000", "-qmp", f"unix:{sock},server=on,wait=off"]
if a.disk:
    cmd += ["-drive", f"file={a.disk},format=qcow2,if=virtio"]
if a.secureboot:
    shutil.copy("/usr/share/OVMF/OVMF_VARS_4M.ms.fd", d / "vars.fd")
    cmd += ["-global", "driver=cfi.pflash01,property=secure,value=on",
            "-drive", "if=pflash,format=raw,unit=0,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.secboot.fd",
            "-drive", f"if=pflash,format=raw,unit=1,file={d / 'vars.fd'}"]
elif not a.bios:
    shutil.copy("/usr/share/OVMF/OVMF_VARS_4M.fd", d / "vars.fd")
    cmd += ["-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd",
            "-drive", f"if=pflash,format=raw,file={d / 'vars.fd'}"]
q = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=open(d / "qemu.err", "w"))
shots = []
try:
    for t in range(40, a.duree + 1, 40):
        time.sleep(40)
        if q.poll() is not None:
            print("QEMU arrêté, code", q.returncode); break
        s = socket.socket(socket.AF_UNIX); s.connect(str(sock)); f = s.makefile("rw")
        f.readline(); f.write('{"execute":"qmp_capabilities"}\n'); f.flush(); f.readline()
        ppm = d / f"t{t}.ppm"
        f.write(json.dumps({"execute": "screendump", "arguments": {"filename": str(ppm)}}) + "\n"); f.flush(); f.readline()
        s.close(); time.sleep(0.5)
        im = Image.open(ppm).convert("RGB"); ppm.unlink()
        im.save(d / f"t{t}.png"); shots.append(d / f"t{t}.png")
        print(t, im.size, flush=True)
finally:
    q.kill(); q.wait()
if shots:
    subprocess.run(["montage", "-geometry", "320x200+2+2", "-tile", "6x", "-label", "%f",
                    *map(str, shots), str(d / "montage.png")], check=False)
