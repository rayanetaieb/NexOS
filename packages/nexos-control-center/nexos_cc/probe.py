"""Mesures et inventaires RÉELS du système (aucune valeur simulée).
Chaque fonction lit /proc, /sys ou un outil système ; si l'outil manque, elle le dit."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


def sh(cmd: list[str], timeout: int = 10) -> str:
    if not shutil.which(cmd[0]):
        return ""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False).stdout
    except subprocess.TimeoutExpired:
        return ""


# ------------------------------------------------------------------ ressources
def meminfo() -> dict[str, int]:
    out = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        k, v = line.split(":", 1)
        out[k] = int(v.split()[0]) // 1024
    return out


def cpu_times() -> tuple[int, int]:
    f = [int(x) for x in Path("/proc/stat").read_text().splitlines()[0].split()[1:]]
    idle = f[3] + (f[4] if len(f) > 4 else 0)
    return idle, sum(f)


def cpu_percent(interval: float = 0.3) -> float:
    i0, t0 = cpu_times(); time.sleep(interval); i1, t1 = cpu_times()
    return round(100 * (1 - (i1 - i0) / max(1, t1 - t0)), 1)


def disk_usage(path: str = "/") -> dict:
    st = os.statvfs(path)
    total = st.f_blocks * st.f_frsize // 2**20
    free = st.f_bavail * st.f_frsize // 2**20
    return {"total_mb": total, "free_mb": free, "used_pct": round(100 * (1 - free / max(1, total)), 1)}


def uptime_s() -> int:
    return int(float(Path("/proc/uptime").read_text().split()[0]))


@dataclass
class Proc:
    pid: int
    name: str
    rss_mb: float


def top_processes(n: int = 8) -> list[Proc]:
    procs = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            st = (d / "status").read_text()
        except OSError:
            continue
        name = next((ln.split(":", 1)[1].strip() for ln in st.splitlines() if ln.startswith("Name:")), "?")
        rss = next((int(ln.split()[1]) for ln in st.splitlines() if ln.startswith("VmRSS:")), 0)
        procs.append(Proc(int(d.name), name, round(rss / 1024, 1)))
    return sorted(procs, key=lambda p: -p.rss_mb)[:n]


def os_release() -> dict:
    out = {}
    for line in Path("/etc/os-release").read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k] = v.strip('"')
    return out


# ------------------------------------------------------------------ services
def enabled_services() -> list[str]:
    out = sh(["systemctl", "list-unit-files", "--type=service,socket,timer", "--state=enabled", "--no-legend", "--plain"])
    return sorted(ln.split()[0] for ln in out.splitlines() if ln.strip())


def running_services() -> list[str]:
    out = sh(["systemctl", "list-units", "--type=service", "--state=running", "--no-legend", "--plain"])
    return sorted(ln.split()[0] for ln in out.splitlines() if ln.strip())


def autostart_entries() -> list[tuple[str, str, bool]]:
    """(fichier, nom, actif) des programmes lancés à l'ouverture de session."""
    entries: dict[str, tuple[str, str, bool]] = {}
    for d in (Path("/etc/xdg/autostart"), Path.home() / ".config/autostart"):
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.desktop")):
            txt = f.read_text(errors="replace")
            name = next((ln.split("=", 1)[1] for ln in txt.splitlines() if ln.startswith("Name=")), f.stem)
            hidden = any(ln.strip() in ("Hidden=true", "X-KDE-autostart-enabled=false") for ln in txt.splitlines())
            only = next((ln.split("=", 1)[1] for ln in txt.splitlines() if ln.startswith("OnlyShowIn=")), "")
            if only and "KDE" not in only:
                continue
            entries[f.name] = (f.name, name, not hidden)
    return list(entries.values())


def set_user_autostart(filename: str, enabled: bool) -> Path:
    """Désactive/réactive un programme de session pour l'utilisateur (sans droits admin)."""
    user = Path.home() / ".config/autostart" / filename
    user.parent.mkdir(parents=True, exist_ok=True)
    src = user if user.exists() else Path("/etc/xdg/autostart") / filename
    lines = [ln for ln in src.read_text().splitlines() if not ln.startswith("Hidden=")]
    lines.append(f"Hidden={'false' if enabled else 'true'}")
    user.write_text("\n".join(lines) + "\n")
    return user


# ------------------------------------------------------------------ matériel
def block_devices() -> list[dict]:
    out = sh(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,RM"])
    try:
        return json.loads(out)["blockdevices"] if out else []
    except (ValueError, KeyError):
        return []


def usb_devices() -> list[str]:
    return [ln for ln in sh(["lsusb"]).splitlines() if ln.strip()]


def serial_ports() -> list[str]:
    return sorted(str(p) for pat in ("ttyUSB*", "ttyACM*", "ttyS[0-3]") for p in Path("/dev").glob(pat))


def gpus() -> list[str]:
    out = sh(["lspci", "-k"])
    res, cur = [], None
    for ln in out.splitlines():
        if not ln.startswith(("\t", " ")):
            cur = ln if any(k in ln for k in ("VGA", "3D controller", "Display")) else None
            if cur:
                res.append(cur)
        elif cur and "Kernel driver in use" in ln:
            res[-1] += "  →  pilote : " + ln.split(":", 1)[1].strip()
    return res


def network() -> list[str]:
    return [ln for ln in sh(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device"]).splitlines() if ln]


def bluetooth() -> str:
    out = sh(["bluetoothctl", "show"], timeout=5)
    if not out:
        return "aucun contrôleur Bluetooth détecté"
    powered = next((ln.split(":", 1)[1].strip() for ln in out.splitlines() if "Powered" in ln), "?")
    return f"contrôleur présent, alimenté : {powered}"


# ------------------------------------------------------------------ sécurité
def firewall_state() -> str:
    """État d'ufw lisible sans droits : ufw.conf (ENABLED) + service de chargement des règles."""
    conf = Path("/etc/ufw/ufw.conf")
    if not conf.exists():
        return "ufw absent"
    enabled = any(ln.strip() == "ENABLED=yes" for ln in conf.read_text().splitlines())
    active = sh(["systemctl", "is-active", "ufw"]).strip() == "active"
    return "actif (entrant bloqué par défaut)" if enabled and active else ("activé, non chargé" if enabled else "désactivé")


def apparmor_enabled() -> bool:
    p = Path("/sys/module/apparmor/parameters/enabled")
    return p.exists() and p.read_text().strip() == "Y"


def secure_boot() -> str:
    out = sh(["mokutil", "--sb-state"]).strip()
    if out:
        return out
    efi = Path("/sys/firmware/efi")
    return "démarrage UEFI (état Secure Boot : mokutil absent)" if efi.exists() else "démarrage BIOS (Secure Boot non applicable)"


def root_fs() -> str:
    return sh(["findmnt", "-no", "SOURCE,FSTYPE", "/"]).strip()


# ------------------------------------------------------------------ IA / Python
def nexai_engines() -> list[Proc]:
    return [p for p in top_processes(400) if p.name.startswith("llama-server")]


def python_profiles_installed() -> list[str]:
    envs = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "nexos/python/envs"
    return sorted(p.name for p in envs.iterdir()) if envs.is_dir() else []
