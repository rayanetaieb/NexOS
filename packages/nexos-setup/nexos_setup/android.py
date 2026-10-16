"""Installation assistée d'Android Studio sur NexOS.

Pourquoi « assistée » : la licence du SDK Android (Google) n'autorise pas sa
redistribution dans une ISO tierce, et l'utilisateur doit accepter ces conditions
lui-même. NexOS préinstalle donc tout ce qui est redistribuable (OpenJDK 21, adb,
fastboot, règles udev Android, outils KVM) et télécharge Android Studio à la demande :
- version et SHA-256 lus sur la page officielle developer.android.com/studio ;
- téléchargement vérifié par SHA-256, installation dans ~/.local/share/nexos sans root ;
- mémoire de l'IDE adaptée à la RAM (pas de -Xmx surdimensionné) ;
- vérification KVM pour l'émulateur, sans rien démarrer en arrière-plan.
"""
from __future__ import annotations

import grp
import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

STUDIO_PAGE = "https://developer.android.com/studio"
TERMS_URL = "https://developer.android.com/studio/terms"


def base_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "nexos" / "android-studio"


@dataclass
class Release:
    url: str
    sha256: str
    filename: str
    version: str


def parse_release(html: str) -> Release:
    """Extrait l'archive Linux et son SHA-256 de la page officielle (tableau des téléchargements)."""
    m = re.search(r'(https://[^"\s]+/(android-studio-([\w.\-]+)-linux\.tar\.gz))', html)
    if not m:
        raise ValueError("archive Linux introuvable sur la page Android Studio")
    url, filename, version = m.group(1), m.group(2), m.group(3)
    # le SHA-256 (64 hex) figure dans la même ligne du tableau que le nom du fichier
    idx = html.find(filename)
    window = html[idx: idx + 1500]
    h = re.search(r"\b([0-9a-f]{64})\b", window)
    if not h:
        raise ValueError("empreinte SHA-256 introuvable à côté de l'archive")
    return Release(url, h.group(1), filename, version)


def fetch_release(timeout: int = 30) -> Release:
    with urllib.request.urlopen(STUDIO_PAGE, timeout=timeout) as r:
        return parse_release(r.read().decode("utf-8", "replace"))


def download(rel: Release, dest_dir: Path, progress=None) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / rel.filename
    part = dest.with_suffix(".part")
    h = hashlib.sha256()
    with urllib.request.urlopen(rel.url, timeout=60) as r, open(part, "wb") as out:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while block := r.read(1 << 20):
            out.write(block); h.update(block); done += len(block)
            if progress:
                progress(done, total)
    if h.hexdigest() != rel.sha256:
        part.unlink(missing_ok=True)
        raise ValueError("SHA-256 incorrect : archive supprimée")
    part.replace(dest)
    return dest


def ide_heap_mb(total_ram_mb: int) -> int:
    """Mémoire max de l'IDE : 1/4 de la RAM, bornée 1–4 Go (Android Studio recommande ≥ 2 Go)."""
    return max(1024, min(4096, (total_ram_mb // 4) // 256 * 256))


def mem_total_mb() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1]) // 1024
    return 4096


def install(archive: Path, target: Path | None = None) -> Path:
    target = target or base_dir()
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.parent / (target.name + ".extract")
    shutil.rmtree(tmp, ignore_errors=True)
    with tarfile.open(archive) as t:
        t.extractall(tmp, filter="data")
    inner = next(tmp.iterdir())          # dossier « android-studio »
    inner.rename(target)
    tmp.rmdir()
    write_vmoptions(target)
    write_launcher(target)
    return target


def write_vmoptions(target: Path) -> Path:
    """Surcharge utilisateur des options JVM (fichier lu par studio.sh)."""
    cfg = Path.home() / ".config/Google"
    heap = ide_heap_mb(mem_total_mb())
    opts = target.parent / "studio64.vmoptions"
    opts.write_text(f"-Xms256m\n-Xmx{heap}m\n-XX:ReservedCodeCacheSize=512m\n", encoding="utf-8")
    cfg.mkdir(parents=True, exist_ok=True)
    return opts


def write_launcher(target: Path) -> Path:
    apps = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "applications"
    apps.mkdir(parents=True, exist_ok=True)
    d = apps / "android-studio.desktop"
    d.write_text(
        "[Desktop Entry]\nType=Application\nName=Android Studio\nComment=IDE Android (Kotlin, Java)\n"
        f"Exec=env STUDIO_VM_OPTIONS={target.parent / 'studio64.vmoptions'} ANDROID_HOME=%h/Android/Sdk "
        f"{target / 'bin/studio.sh'} %f\nIcon={target / 'bin/studio.svg'}\nCategories=Development;IDE;\n"
        "StartupWMClass=jetbrains-studio\nTerminal=false\n", encoding="utf-8")
    return d


def installed() -> bool:
    return (base_dir() / "bin/studio.sh").exists()


def kvm_status() -> dict:
    """État de la virtualisation pour l'émulateur Android (aucune action, lecture seule)."""
    flags = Path("/proc/cpuinfo").read_text()
    cpu_virt = (" vmx" in flags) or (" svm" in flags)
    dev = Path("/dev/kvm")
    try:
        in_group = "kvm" in [grp.getgrgid(g).gr_name for g in os.getgroups()]
    except KeyError:
        in_group = False
    return {"cpu_virtualisation": cpu_virt, "dev_kvm": dev.exists(),
            "dev_kvm_rw": os.access(dev, os.R_OK | os.W_OK) if dev.exists() else False,
            "groupe_kvm": in_group}


def adb_version() -> str:
    try:
        return subprocess.run(["adb", "version"], capture_output=True, text=True, check=False).stdout.splitlines()[0]
    except (FileNotFoundError, IndexError):
        return "adb absent"
