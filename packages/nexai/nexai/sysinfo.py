"""Mesures système sans dépendance (lecture de /proc et /sys, Linux)."""
from __future__ import annotations

import os
from pathlib import Path


def mem_available_mb() -> int:
    """RAM réellement disponible (MemAvailable du noyau), en Mio."""
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    raise RuntimeError("MemAvailable introuvable dans /proc/meminfo")


def mem_total_mb() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1]) // 1024
    raise RuntimeError("MemTotal introuvable")


def _status_kib(pid: int, field: str) -> int:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith(field + ":"):
                return int(line.split()[1])
    except (FileNotFoundError, ProcessLookupError):
        return 0
    return 0


def rss_mb(pid: int) -> float:
    """Mémoire résidente (VmRSS) d'un processus, en Mio."""
    return _status_kib(pid, "VmRSS") / 1024


def pss_mb(pid: int) -> float:
    """PSS (part proportionnelle des pages partagées) : plus juste que RSS, en Mio."""
    try:
        for line in Path(f"/proc/{pid}/smaps_rollup").read_text().splitlines():
            if line.startswith("Pss:"):
                return int(line.split()[1]) / 1024
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
    return rss_mb(pid)


def smaps_mb(pid: int, field: str) -> float:
    """Champ de /proc/<pid>/smaps_rollup (ex. Pss_Anon = mémoire non récupérable,
    Pss_File = pages du fichier modèle, récupérables par le noyau), en Mio."""
    try:
        for line in Path(f"/proc/{pid}/smaps_rollup").read_text().splitlines():
            if line.startswith(field + ":"):
                return int(line.split()[1]) / 1024
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
    return 0.0


def physical_cores() -> int:
    cores = set()
    try:
        block = {}
        for line in Path("/proc/cpuinfo").read_text().splitlines() + [""]:
            if not line.strip():
                if "physical id" in block and "core id" in block:
                    cores.add((block["physical id"], block["core id"]))
                block = {}
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                block[k.strip()] = v.strip()
    except OSError:
        pass
    return len(cores) or (os.cpu_count() or 1)


def cpu_flags() -> set[str]:
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("flags"):
            return set(line.split(":", 1)[1].split())
    return set()


def default_threads() -> int:
    return max(1, physical_cores() - 1) if physical_cores() > 2 else max(1, physical_cores())
