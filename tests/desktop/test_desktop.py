#!/usr/bin/env python3
"""Test du bureau NexOS dans QEMU : démarrage jusqu'à la session Plasma, captures
d'écran RÉELLES et interactions clavier/souris envoyées par QMP.

Usage : python3 tests/desktop/test_desktop.py OUT_DIR [--scenario]
Produit OUT_DIR/screens/*.png et OUT_DIR/desktop-test.json. Code retour 0 = succès.
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

OUT = Path(sys.argv[1]).resolve()
SCENARIO = "--scenario" in sys.argv
SHOTS = OUT / "screens"
SHOTS.mkdir(parents=True, exist_ok=True)
SERIAL = OUT / "desktop-serial.log"
QMP_SOCK = OUT / "qmp.sock"
TIMEOUT = int(os.environ.get("TIMEOUT", "2400"))
MEM = os.environ.get("MEM", "4096")


class QMP:
    def __init__(self, path: Path):
        self.s = socket.socket(socket.AF_UNIX)
        for _ in range(100):
            try:
                self.s.connect(str(path)); break
            except (FileNotFoundError, ConnectionRefusedError):
                time.sleep(0.1)
        self.f = self.s.makefile("rw")
        self.f.readline()
        self.cmd("qmp_capabilities")

    def cmd(self, name, **args):
        self.f.write(json.dumps({"execute": name, "arguments": args}) + "\n"); self.f.flush()
        while True:
            msg = json.loads(self.f.readline())
            if "return" in msg or "error" in msg:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg["return"]

    def screenshot(self, name: str) -> Path:
        ppm = OUT / "tmp.ppm"
        self.cmd("screendump", filename=str(ppm))
        time.sleep(0.5)
        png = SHOTS / f"{name}.png"
        Image.open(ppm).save(png)
        ppm.unlink()
        return png

    def keys(self, *combo: str, hold_ms: int = 60):
        self.cmd("send-key", keys=[{"type": "qcode", "data": k} for k in combo], **{"hold-time": hold_ms})

    def type_text(self, text: str):
        # Clavier AZERTY dans l'invité : on envoie les codes physiques correspondant aux lettres.
        azerty = {"a": "q", "q": "a", "z": "w", "w": "z", "m": "semicolon"}
        for ch in text:
            if ch == " ":
                self.keys("spc")
            elif ch.isalpha():
                k = azerty.get(ch.lower(), ch.lower())
                self.keys("shift", k) if ch.isupper() else self.keys(k)
            time.sleep(0.15)

    def click(self, x: int, y: int, w: int, h: int, button="left"):
        ax, ay = int(x * 32767 / w), int(y * 32767 / h)
        self.cmd("input-send-event", events=[
            {"type": "abs", "data": {"axis": "x", "value": ax}},
            {"type": "abs", "data": {"axis": "y", "value": ay}}])
        time.sleep(0.3)
        for down in (True, False):
            self.cmd("input-send-event", events=[{"type": "btn", "data": {"down": down, "button": button}}])
            time.sleep(0.1)


def wait_serial(pattern: str, timeout: int) -> str:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if SERIAL.exists():
            txt = SERIAL.read_text(errors="replace")
            if re.search(pattern, txt):
                return txt
        time.sleep(2)
    raise TimeoutError(pattern)


def main() -> int:
    for p in (SERIAL, QMP_SOCK):
        p.unlink(missing_ok=True)
    accel = "kvm" if os.access("/dev/kvm", os.W_OK) else "tcg"
    W, H = 1440, 900
    cmd = ["qemu-system-x86_64", "-machine", f"q35,accel={accel}", "-m", MEM, "-smp", "2",
           "-kernel", str(OUT / "vmlinuz"), "-initrd", str(OUT / "initrd.img"),
           "-append", "root=/dev/vda rw console=ttyS0 quiet",
           "-drive", f"file={OUT / 'nexos.img'},format=raw,if=virtio,snapshot=on",
           "-vga", "none", "-device", f"virtio-vga,xres={W},yres={H}",
           "-device", "qemu-xhci", "-device", "usb-tablet",
           "-display", "none", "-serial", f"file:{SERIAL}",
           "-qmp", f"unix:{QMP_SOCK},server=on,wait=off", "-nic", "user,model=virtio-net-pci"]
    t0 = time.time()
    vm = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    result = {"accel": accel, "memory_mib": int(MEM), "measured": True}
    qmp = None
    try:
        qmp = QMP(QMP_SOCK)
        # captures périodiques du démarrage jusqu'au rapport de session
        n = 0
        while True:
            try:
                txt = wait_serial(r"NEXOS-REPORT-END", 60)
                break
            except TimeoutError:
                if time.time() - t0 > TIMEOUT:
                    qmp.screenshot("timeout")
                    raise
                n += 1
                if n % 3 == 0:
                    qmp.screenshot(f"boot-{n:03d}")
        result["desktop_ready_wallclock_s"] = round(time.time() - t0)
        report = re.search(r"NEXOS-REPORT-BEGIN(.*?)NEXOS-REPORT-END", txt, re.S).group(1)
        for line in report.strip().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                result[k.strip()] = v.strip()
        time.sleep(30)
        result["screens"] = [str(qmp.screenshot("01-bureau"))]
        if SCENARIO:
            # NB : clavier AZERTY dans l'invité ; « - » est sur la touche physique 6.
            steps = [
                ("02-menu", lambda: qmp.keys("meta_l"), 15),
                ("03-recherche-parametres", lambda: qmp.type_text("param"), 15),
                ("04-fermer-menu", lambda: qmp.keys("esc"), 8),
                ("05-terminal", lambda: qmp.keys("ctrl", "alt", "t"), 40),
                ("06-terminal-commande", lambda: (qmp.type_text("uname "), qmp.keys("6"), qmp.type_text("r"), qmp.keys("ret")), 10),
                ("07-fermer-terminal", lambda: qmp.keys("ctrl", "shift", "w"), 10),
                ("08-assistant", lambda: qmp.keys("meta_l", "spc"), 45),
                ("09-fermer-assistant", lambda: qmp.keys("esc"), 8),
                ("10-fichiers", lambda: qmp.keys("meta_l", "e"), 45),
            ]
            for name, action, wait in steps:
                action(); time.sleep(wait)
                result["screens"].append(str(qmp.screenshot(name)))
        ok = (result.get("desktop_plasmashell") == "running" and result.get("desktop_session_type") == "wayland"
              and result.get("failed_units") == "0")
        result["success"] = ok
        return 0 if ok else 1
    finally:
        (OUT / "desktop-test.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        try:
            if qmp is None:
                raise RuntimeError("QMP indisponible")
            qmp.cmd("quit")
        except Exception:  # noqa: BLE001 — arrêt au mieux
            vm.kill()
        vm.wait(timeout=30)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
