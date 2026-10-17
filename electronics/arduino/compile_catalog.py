#!/usr/bin/env python3
"""Compile un exemple de chaque bibliothèque du catalogue avec la chaîne Arduino de NexOS
(arduino-builder + cœur AVR Debian, sans réseau). Résultat RÉEL par bibliothèque :
  ok · échec (extrait d'erreur) · non testable (architecture non AVR : cœur absent hors ligne)
Usage : compile_catalog.py catalog.json <dossier_des_clones> <résultats.json> [fqbn]
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FQBN = sys.argv[4] if len(sys.argv) > 4 else "arduino:avr:mega:cpu=atmega2560"
FQBN_USB = "arduino:avr:leonardo"          # cartes à USB natif (clavier/souris HID)
USB_LIBS = {"Keyboard", "HID-Project"}
# En-têtes propres à d'autres cartes : un exemple qui en dépend n'est pas un échec de la bibliothèque sur AVR.
OTHER_BOARD_HEADERS = ("WiFi.h", "ESP8266WiFi.h", "WiFiS3.h", "WiFi101.h", "IPv6Address.h", "DNSServer.h",
                       "sys/time.h", "rtc_clock.h", "esp_", "WiFiNINA.h", "ILI9341_t3.h", "Adafruit_TinyUSB",
                       "SdFat_Adafruit_Fork.h", "Wire1", "lv_conf.h", "BLEDevice.h", "mbed", "Arduino_LSM",
                       "WiFiClient", "FS.h", "does not support Arduino with AVR", "Use Version 1.x.x",
                       "WiFiMulti.h", "rpcWiFi.h", "Arduino_SpiNINA.h", "HCITransport")
# Exemples livrés avec le constructeur d'écran commenté (l'utilisateur choisit son écran) :
# on active celui d'un écran courant (SSD1306 128×64 en I²C) — signalé dans le résultat.
DISPLAY_CTOR = re.compile(r"^//\s*((?:U8G2|U8X8)_SSD1306_128X64_NONAME_\w*HW_I2C\s+\w+\()", re.MULTILINE)
PRIORITY = ("basic", "simple", "hello", "test", "example", "blink", "demo", "read", "single", "minimal")
HARDWARE = ["/usr/share/arduino/hardware"]
TOOLS = ["/usr/share/arduino/tools-builder", "/usr/share/arduino/hardware/tools"]


def avr_compatible(arch: str) -> bool:
    a = arch.replace(" ", "").lower()
    return a in ("*", "nondéclarées", "non déclarées") or "avr" in a.split(",") or a == ""


def compile_sketch(sketch: Path, libdir: Path, build: Path, fqbn: str = FQBN) -> tuple[bool, str]:
    cmd = ["arduino-builder", "-compile", "-logger=human", "-fqbn", fqbn, "-core-api-version", "10819",
           "-libraries", str(libdir), "-build-path", str(build), "-warnings", "none"]
    for h in HARDWARE:
        cmd += ["-hardware", h]
    for t in TOOLS:
        if Path(t).exists():
            cmd += ["-tools", t]
    cmd.append(str(sketch))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=False)
    except subprocess.TimeoutExpired:
        return False, "délai dépassé"
    out = r.stdout + r.stderr
    if r.returncode == 0:
        size = next((ln.strip() for ln in out.splitlines() if "Sketch uses" in ln or "Le croquis utilise" in ln), "")
        return True, size
    errs = [ln for ln in out.splitlines() if "error" in ln.lower() or "undefined reference" in ln]
    return False, "\n".join(errs[:4])[-600:] or out[-600:]


def ranked_examples(e: dict, src: Path) -> list[str]:
    exs = sorted({str(p.relative_to(src)) for d in ("examples", "Examples", "example")
                  for pat in ("*.ino", "*.pde") for p in src.glob(f"{d}/**/{pat}")})
    if not exs:  # certains dépôts rangent leur croquis de test ailleurs (ex. arduino-test/)
        exs = sorted(str(p.relative_to(src)) for p in src.glob("**/*.ino") if ".git" not in p.parts)
    def score(x):
        low = x.lower()
        bad = any(k in low for k in ("esp32", "esp8266", "due", "feather", "teensy", "rp2040", "samd", "nano33", "wifi", "r4"))
        good = next((i for i, k in enumerate(PRIORITY) if k in low), len(PRIORITY))
        return (bad, good, len(x))
    return sorted(exs, key=score)[:10]


def main(cat_path: str, clones: str, out_path: str) -> int:
    cat = json.load(open(cat_path, encoding="utf-8"))
    clones_dir = Path(clones)
    results = []
    with tempfile.TemporaryDirectory() as t:
        # Situation réelle : bibliothèques du catalogue installées dans ~/Arduino/libraries.
        lib = Path(t) / "libraries"; lib.mkdir()
        for e in cat["libraries"]:
            slug = e["repository"].split("github.com/")[1].replace("/", "__")
            shutil.copytree(clones_dir / slug, lib / slug, ignore=shutil.ignore_patterns(".git"))
        for e in cat["libraries"]:
            slug = e["repository"].split("github.com/")[1].replace("/", "__")
            src = clones_dir / slug
            res = {"id": e["id"], "name": e["name"], "repository": e["repository"], "architectures": e["architectures"]}
            exs = ranked_examples(e, src)
            if not avr_compatible(e["architectures"]):
                res.update(status="non testable", detail=f"architectures {e['architectures']} : cœur absent hors ligne")
            elif not exs:
                res.update(status="non testable", detail="aucun exemple fourni par la bibliothèque")
            else:
                fqbn = FQBN_USB if e["name"] in USB_LIBS else FQBN
                attempts = []
                for ex_rel in exs:
                    ex = src / ex_rel
                    sk = Path(t) / "sk" / ex.stem
                    shutil.rmtree(sk.parent, ignore_errors=True); sk.mkdir(parents=True)
                    for f in ex.parent.iterdir():
                        if f.is_file():
                            shutil.copy(f, sk / f.name)
                    prepared = ""
                    ino = sk / ex.name
                    text = ino.read_text(errors="replace")
                    if DISPLAY_CTOR.search(text) and not re.search(r"^\s*(U8G2|U8X8)_\w+\s+\w+\(", text, re.MULTILINE):
                        ino.write_text(DISPLAY_CTOR.sub(r"\1", text, count=1))
                        prepared = "constructeur SSD1306 128×64 I²C activé"
                    build = Path(t) / "build"; shutil.rmtree(build, ignore_errors=True); build.mkdir()
                    t0 = time.time()
                    ok, detail = compile_sketch(sk / ex.name, lib, build, fqbn)
                    attempts.append({"example": ex_rel, "ok": ok, "detail": detail, "seconds": round(time.time() - t0, 1),
                                     **({"preparation": prepared} if prepared else {})})
                    if ok:
                        break
                good = next((a for a in attempts if a["ok"]), None)
                if good:
                    res.update(status="ok", example=good["example"], detail=good["detail"], fqbn=fqbn,
                               **({"preparation": good["preparation"]} if "preparation" in good else {}))
                elif all(any(h in a["detail"] for h in OTHER_BOARD_HEADERS) for a in attempts):
                    res.update(status="non testable", detail="exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : "
                               + attempts[0]["detail"][:200])
                else:
                    res.update(status="échec", detail=attempts[0]["detail"])
                res["essais"] = attempts
            results.append(res)
            print(f"{res['id']:3} {res['status']:13} {res['name']}", flush=True)
    # Bibliothèque sans exemple compilable seul mais compilée comme dépendance d'une autre : vérifiée indirectement.
    by_name = {r["name"]: r for r in results}
    for e in cat["libraries"]:
        if by_name[e["name"]]["status"] != "ok":
            continue
        for dep in e.get("depends", []):
            r = by_name.get(dep.split("(")[0].strip())
            if r and r["status"] != "ok":
                r.update(status="ok", detail=f"compilée comme dépendance de {e['name']} ({by_name[e['name']].get('example','')}) ; "
                         f"son propre exemple échoue : {r['detail'][:160]}", indirect=True)
    json.dump({"fqbn": FQBN, "results": results}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = {s: sum(r["status"] == s for r in results) for s in ("ok", "échec", "non testable")}
    print(n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
