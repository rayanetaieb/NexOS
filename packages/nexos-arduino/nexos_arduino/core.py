"""Centre Arduino NexOS : catalogue des 100 bibliothèques, gestion des bibliothèques
installées (~/Arduino/libraries) et diagnostic des cartes et de la chaîne de compilation.

Installation = clone Git du dépôt officiel AU TAG VÉRIFIÉ du catalogue (version figée,
pas de « dernière branche » imprévisible). Mise à jour = passage au tag le plus récent.
Dépendances déclarées installées automatiquement si elles sont dans le catalogue ;
doublons et conflits (même bibliothèque à une autre version) signalés.
"""
from __future__ import annotations

import grp
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

CATALOG_PATHS = [Path(os.environ.get("NEXOS_ARDUINO_CATALOG", "")), Path("/usr/share/nexos/arduino/catalog.json"),
                 Path(__file__).resolve().parents[3] / "electronics/arduino/catalog.json"]
USB_IDS = {  # VID → famille de cartes / convertisseurs USB-série courants
    "2341": "Arduino (officielle)", "2a03": "Arduino (arduino.org)", "1a86": "convertisseur CH340/CH341 (clones)",
    "10c4": "convertisseur Silicon Labs CP210x (ESP32, NodeMCU)", "0403": "convertisseur FTDI",
    "303a": "Espressif (ESP32-S2/S3/C3 USB natif)", "239a": "Adafruit", "1b4f": "SparkFun", "2e8a": "Raspberry Pi (RP2040)",
}


def catalog() -> dict:
    for p in CATALOG_PATHS:
        if str(p) and p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError("catalog.json introuvable")


def libraries_dir() -> Path:
    return Path(os.environ.get("NEXOS_ARDUINO_LIBS", Path.home() / "Arduino/libraries"))


def folder_name(entry: dict) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]", "_", entry["name"])


def search(query: str = "", category: str = "") -> list[dict]:
    q = query.lower().strip()
    out = []
    for e in catalog()["libraries"]:
        if category and e["category"] != category:
            continue
        hay = " ".join([e["name"], e.get("description", ""), e.get("author", ""), e["category_name"]]).lower()
        if not q or q in hay:
            out.append(e)
    return out


def read_props(path: Path) -> dict:
    p = path / "library.properties"
    out = {}
    if p.exists():
        for ln in p.read_text(errors="replace").splitlines():
            if "=" in ln:
                k, v = ln.split("=", 1); out[k.strip()] = v.strip()
    return out


@dataclass
class Installed:
    folder: str
    name: str
    version: str


def installed() -> list[Installed]:
    d = libraries_dir()
    if not d.is_dir():
        return []
    res = []
    for f in sorted(d.iterdir()):
        if f.is_dir():
            p = read_props(f)
            res.append(Installed(f.name, p.get("name", f.name), p.get("version", "?")))
    return res


def status(entry: dict) -> str:
    for i in installed():
        if i.name == entry["name"]:
            return "installée" if i.version == entry["version"] else f"installée ({i.version} ≠ catalogue {entry['version']})"
    return "non installée"


def _git(*args, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False,
                          env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})


def install(entry: dict, with_deps: bool = True, _seen: set | None = None) -> list[str]:
    """Installe la bibliothèque (et ses dépendances du catalogue). Renvoie le journal."""
    seen = _seen if _seen is not None else set()
    if entry["name"] in seen:
        return []
    seen.add(entry["name"])
    log: list[str] = []
    dest = libraries_dir() / folder_name(entry)
    for i in installed():
        if i.name == entry["name"] and i.folder != dest.name:
            raise RuntimeError(f"conflit : {entry['name']} déjà présente dans {i.folder} (version {i.version})")
    if dest.exists():
        log.append(f"{entry['name']} déjà installée ({read_props(dest).get('version', '?')})")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        args = ["clone", "--depth", "1", "--quiet"] + (["--branch", entry["tag"]] if entry.get("tag") else [])
        r = _git(*args, entry["repository"] + ".git", str(dest))
        if r.returncode:
            raise RuntimeError(f"échec du téléchargement de {entry['name']} : {r.stderr.strip()[-300:]}")
        shutil.rmtree(dest / ".git", ignore_errors=True)
        log.append(f"{entry['name']} {entry['version']} installée dans {dest}")
    if with_deps:
        names = {e["name"]: e for e in catalog()["libraries"]}
        for dep in entry.get("depends", []):
            dn = dep.split("(")[0].strip()
            if dn in names:
                log += install(names[dn], True, seen)
            else:
                log.append(f"dépendance hors catalogue à installer via l'IDE : {dn}")
    return log


def remove(entry: dict) -> str:
    dest = libraries_dir() / folder_name(entry)
    if not dest.exists():
        return f"{entry['name']} n'est pas installée"
    shutil.rmtree(dest)
    return f"{entry['name']} supprimée"


def update(entry: dict) -> str:
    """Passe à la dernière version publiée (tag) du dépôt officiel."""
    r = _git("ls-remote", "--tags", "--refs", entry["repository"] + ".git")
    tags = [ln.split("refs/tags/")[1] for ln in r.stdout.splitlines() if re.search(r"refs/tags/v?\d", ln)]
    if not tags:
        return "aucune version publiée"
    key = lambda t: [int(n) for n in re.findall(r"\d+", t)[:4]]
    newest = max(tags, key=key)
    remove(entry)
    install({**entry, "tag": newest}, with_deps=False)
    return f"{entry['name']} mise à jour vers {newest}"


# ------------------------------------------------------------------ diagnostic
def diagnose() -> dict:
    ports = sorted(str(p) for pat in ("ttyUSB*", "ttyACM*") for p in Path("/dev").glob(pat))
    lsusb = subprocess.run(["lsusb"], capture_output=True, text=True, check=False).stdout if shutil.which("lsusb") else ""
    boards = []
    for ln in lsusb.splitlines():
        m = re.search(r"ID ([0-9a-f]{4}):([0-9a-f]{4})", ln)
        if m and m.group(1) in USB_IDS:
            boards.append(f"{USB_IDS[m.group(1)]} — {ln.split(m.group(0))[1].strip()}")
    try:
        in_dialout = "dialout" in [grp.getgrgid(g).gr_name for g in os.getgroups()]
    except KeyError:
        in_dialout = False
    return {"ports": ports, "cartes": boards, "groupe_dialout": in_dialout,
            "arduino_ide": shutil.which("arduino") is not None, "arduino_builder": shutil.which("arduino-builder") is not None,
            "avr_gcc": shutil.which("avr-gcc") is not None, "avrdude": shutil.which("avrdude") is not None,
            "esptool": shutil.which("esptool") is not None or shutil.which("esptool.py") is not None}


BLINK = "void setup(){ pinMode(LED_BUILTIN, OUTPUT); }\nvoid loop(){ digitalWrite(LED_BUILTIN, HIGH); delay(500); digitalWrite(LED_BUILTIN, LOW); delay(500); }\n"


def compile_test(fqbn: str = "arduino:avr:uno") -> tuple[bool, str]:
    """Compile Blink avec la chaîne locale (aucun réseau). Vérifie que l'environnement fonctionne."""
    with tempfile.TemporaryDirectory() as t:
        sk = Path(t) / "Blink"; sk.mkdir(); (sk / "Blink.ino").write_text(BLINK)
        build = Path(t) / "build"; build.mkdir()
        cmd = ["arduino-builder", "-compile", "-fqbn", fqbn, "-hardware", "/usr/share/arduino/hardware",
               "-build-path", str(build), str(sk / "Blink.ino")]
        for tl in ("/usr/share/arduino/tools-builder", "/usr/share/arduino/hardware/tools"):
            if Path(tl).exists():
                cmd[2:2] = ["-tools", tl]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=False)
        except FileNotFoundError:
            return False, "arduino-builder absent"
        out = r.stdout + r.stderr
        return r.returncode == 0, next((ln for ln in out.splitlines() if "Sketch uses" in ln or "croquis" in ln), out[-400:])
