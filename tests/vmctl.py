#!/usr/bin/env python3
"""Pilotage d'une VM QEMU de test NexOS (ISO + disque cible) par QMP.

  vmctl.py start --iso X.iso --disk D.qcow2 [--uefi] [--mem 4096]   # démarre en arrière-plan
  vmctl.py start --disk D.qcow2 [--uefi]                            # démarre sur le disque installé
  vmctl.py shot NOM                    # capture → DIR/screens/NOM.png
  vmctl.py keys ctrl alt t             # combinaison de touches (codes QEMU)
  vmctl.py type "texte"                # saisie (clavier AZERTY dans l'invité si --azerty)
  vmctl.py click X Y                   # clic gauche (coordonnées écran)
  vmctl.py serial                      # fin du journal série
  vmctl.py quit
Les fichiers de travail vont dans $VMDIR (défaut out/vm).
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

D = Path(os.environ.get("VMDIR", "out/vm")).resolve()
SOCK, SERIAL, PIDF = D / "qmp.sock", D / "serial.log", D / "qemu.pid"
W, H = 1440, 900
AZERTY = {"a": "q", "q": "a", "z": "w", "w": "z", "m": "semicolon"}
# Caractères spéciaux sur un clavier AZERTY français (codes de touches physiques QEMU).
AZERTY_SPECIAL = {
    "/": ["shift", "dot"], ".": ["shift", "comma"], ";": ["comma"], ":": ["dot"], ",": ["m"],
    "!": ["slash"], "=": ["equal"], "+": ["shift", "equal"], "-": ["6"], "_": ["8"],
    '"': ["3"], "'": ["4"], "(": ["5"], ")": ["minus"], "&": ["1"], "<": ["less"],
    ">": ["shift", "less"], "|": ["alt_r", "6"], "\\": ["alt_r", "8"], "*": ["backslash"],
    "@": ["alt_r", "0"], "#": ["alt_r", "3"], "~": ["alt_r", "2"], "{": ["alt_r", "4"], "}": ["alt_r", "equal"],
    "[": ["alt_r", "5"], "]": ["alt_r", "minus"], "$": ["bracket_right"],
}
SHIFTED_QWERTY = {"@": ("shift", "2"), "!": ("shift", "1"), "_": ("shift", "minus"), ":": ("shift", "semicolon")}


def qmp(cmd: str, **args):
    s = socket.socket(socket.AF_UNIX); s.connect(str(SOCK)); f = s.makefile("rw")
    f.readline()
    for name, a in (("qmp_capabilities", {}), (cmd, args)):
        f.write(json.dumps({"execute": name, "arguments": a}) + "\n"); f.flush()
        while True:
            m = json.loads(f.readline())
            if "return" in m or "error" in m:
                break
    s.close()
    if "error" in m:
        raise RuntimeError(m["error"])
    return m["return"]


def start(argv):
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("--iso"); ap.add_argument("--disk", required=True)
    ap.add_argument("--uefi", action="store_true"); ap.add_argument("--mem", default="4096")
    ap.add_argument("--size", default="24G")
    a = ap.parse_args(argv)
    D.mkdir(parents=True, exist_ok=True); (D / "screens").mkdir(exist_ok=True)
    disk = Path(a.disk)
    if not disk.exists():
        subprocess.run(["qemu-img", "create", "-q", "-f", "qcow2", str(disk), a.size], check=True)
    accel = "kvm" if os.access("/dev/kvm", os.W_OK) else "tcg"
    cmd = ["qemu-system-x86_64", "-machine", f"q35,accel={accel}", "-m", a.mem, "-smp", "2",
           "-vga", "none", "-device", f"virtio-vga,xres={W},yres={H}",
           "-device", "qemu-xhci", "-device", "usb-tablet",
           "-drive", f"file={disk},format=qcow2,if=virtio",
           "-display", "none", "-serial", f"file:{SERIAL}", "-qmp", f"unix:{SOCK},server=on,wait=off",
           "-nic", "user,model=virtio-net-pci", "-daemonize", "-pidfile", str(PIDF)]
    if a.iso:
        cmd += ["-drive", f"file={a.iso},media=cdrom,readonly=on", "-boot", "order=dc"]
    if a.uefi:
        vars_ = D / "OVMF_VARS.fd"
        if not vars_.exists():
            vars_.write_bytes(Path("/usr/share/OVMF/OVMF_VARS_4M.fd").read_bytes())
        cmd += ["-drive", "if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd",
                "-drive", f"if=pflash,format=raw,file={vars_}"]
    for p in (SOCK, SERIAL):
        p.unlink(missing_ok=True)
    subprocess.run(cmd, check=True)
    print(f"VM démarrée ({accel}, {'UEFI' if a.uefi else 'BIOS'})")


def shot(name):
    ppm = D / "tmp.ppm"
    qmp("screendump", filename=str(ppm)); time.sleep(0.5)
    out = D / "screens" / f"{name}.png"
    Image.open(ppm).save(out); ppm.unlink()
    print(out)


def keys(k, hold=60):
    qmp("send-key", keys=[{"type": "qcode", "data": x} for x in k], **{"hold-time": hold})


def type_text(text, azerty=True):
    for ch in text:
        if ch == " ":
            keys(["spc"])
        elif ch == "\n":
            keys(["ret"])
        elif azerty and ch in AZERTY_SPECIAL:
            keys(AZERTY_SPECIAL[ch])
        elif ch.isdigit():
            keys(["shift", ch] if azerty else [ch])      # chiffres = Maj en AZERTY
        elif ch.isalpha():
            k = AZERTY.get(ch.lower(), ch.lower()) if azerty else ch.lower()
            keys(["shift", k] if ch.isupper() else [k])
        elif ch == "-":
            keys(["6"] if azerty else ["minus"])
        elif ch == "." :
            keys(["shift", "comma"] if azerty else ["dot"])
        elif not azerty and ch in SHIFTED_QWERTY:
            keys(list(SHIFTED_QWERTY[ch]))
        else:
            raise ValueError(f"caractère non géré : {ch!r}")
        time.sleep(0.12)


def click(x, y, button="left"):
    qmp("input-send-event", events=[{"type": "abs", "data": {"axis": "x", "value": int(x * 32767 / W)}},
                                    {"type": "abs", "data": {"axis": "y", "value": int(y * 32767 / H)}}])
    time.sleep(0.3)
    for down in (True, False):
        qmp("input-send-event", events=[{"type": "btn", "data": {"down": down, "button": button}}])
        time.sleep(0.15)


if __name__ == "__main__":
    c, *rest = sys.argv[1:]
    if c == "start":
        start(rest)
    elif c == "shot":
        shot(rest[0])
    elif c == "keys":
        # Lettres converties vers la touche physique AZERTY (ex. ctrl a → ctrl q), sauf --qwerty.
        qw = "--qwerty" in rest
        keys([k if qw or len(k) != 1 else AZERTY.get(k, k) for k in rest if k != "--qwerty"])
    elif c == "type":
        type_text(rest[0], azerty="--qwerty" not in rest)
    elif c == "click":
        click(int(rest[0]), int(rest[1]))
    elif c == "serial":
        print(SERIAL.read_text(errors="replace")[-3000:] if SERIAL.exists() else "")
    elif c == "quit":
        qmp("quit")
    else:
        raise SystemExit(__doc__)
