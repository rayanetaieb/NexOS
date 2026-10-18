#!/usr/bin/python3
"""nexos-admin : actions administrateur du Control Center, appelées via pkexec.

Sécurité : liste FERMÉE d'actions, arguments validés, services critiques protégés,
paquets installables limités à une liste de composants NexOS. Aucune commande
arbitraire n'est acceptée. Journalisation dans le journal système (logger).
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

# Services qu'on ne laisse jamais désactiver depuis l'interface (système inutilisable sinon).
PROTECTED = {"dbus", "systemd-journald", "systemd-logind", "systemd-udevd", "sddm", "NetworkManager",
             "polkit", "getty@", "user@", "systemd-timesyncd"}
# Composants complémentaires installables à la demande (catégorie C).
OPTIONAL_PACKAGES = {
    "kicad-3d": ["kicad-packages3d"],
    "texlive-full-extra": ["texlive-fonts-extra", "texlive-publishers", "texlive-humanities"],
    "android-emulator-deps": ["qemu-system-x86", "libvirt-daemon"],
}
# Applications de jeu installables en un clic depuis Flathub (via NexOS Store).
GAME_APPS = {
    "com.valvesoftware.Steam": "Steam",
    "com.heroicgameslauncher.hgl": "Heroic (Epic Games, GOG, Amazon)",
    "net.lutris.Lutris": "Lutris",
    "org.libretro.RetroArch": "RetroArch (émulateurs)",
    "net.davidotek.pupgui2": "ProtonUp-Qt (versions de Proton)",
}
FLATHUB = "https://dl.flathub.org/repo/flathub.flatpakrepo"
MOK_PUB = "/var/lib/dkms/mok.pub"
UNIT_RE = re.compile(r"^[A-Za-z0-9@._\-]+\.(service|socket|timer)$")
DESC_RE = re.compile(r"^[\w .,:'éèàçùâêîôûÉ\-]{1,80}$")


def log(msg: str) -> None:
    subprocess.run(["logger", "-t", "nexos-admin", msg], check=False)


def run(cmd: list[str]) -> int:
    log("exécute : " + " ".join(cmd))
    return subprocess.run(cmd, check=False).returncode


def protected(unit: str) -> bool:
    base = unit.rsplit(".", 1)[0]
    return any(base == p or (p.endswith("@") and base.startswith(p)) for p in PROTECTED)


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__); return 2
    action, args = argv[0], argv[1:]
    if action in ("service-enable", "service-disable"):
        unit = args[0] if args else ""
        if not UNIT_RE.match(unit):
            print("nom d'unité invalide", file=sys.stderr); return 2
        if action == "service-disable" and protected(unit):
            print(f"{unit} est protégé (indispensable au système)", file=sys.stderr); return 3
        verb = "enable" if action == "service-enable" else "disable"
        return run(["systemctl", verb, "--now", unit])
    if action == "apt-update":
        return run(["apt-get", "update"])
    if action == "apt-upgrade":
        # le hook APT de snapper crée automatiquement un instantané avant/après
        return run(["apt-get", "-y", "-o", "Dpkg::Options::=--force-confold", "full-upgrade"])
    if action == "snapshot-create":
        desc = " ".join(args) or "Instantané manuel"
        if not DESC_RE.match(desc):
            print("description invalide", file=sys.stderr); return 2
        return run(["snapper", "-c", "root", "create", "--description", desc, "--cleanup-algorithm", "number"])
    if action == "snapshot-undo":
        # Annule les modifications du système (sous-volume racine) faites depuis l'instantané N.
        # /home est un sous-volume séparé : les documents ne sont jamais touchés.
        n = args[0] if args else ""
        if not re.fullmatch(r"[1-9]\d{0,5}", n):
            print("numéro d'instantané invalide", file=sys.stderr); return 2
        run(["snapper", "-c", "root", "create", "--description", f"Avant retour à l'instantané {n}",
             "--cleanup-algorithm", "number", "--userdata", "important=yes"])
        return run(["snapper", "-c", "root", "undochange", f"{n}..0"])
    if action == "snapshot-list":
        return run(["snapper", "-c", "root", "list"])
    if action in ("firewall-on", "firewall-off"):
        return run(["ufw", "--force", "enable" if action == "firewall-on" else "disable"])
    if action == "flathub-enable":
        return run(["flatpak", "remote-add", "--if-not-exists", "flathub",
                    "https://dl.flathub.org/repo/flathub.flatpakrepo"])
    if action == "install-nvidia":
        # Pilote propriétaire Debian (non-free) compilé par DKMS pour le noyau installé ;
        # DKMS signe le module avec une clé locale (MOK) → à valider au redémarrage si Secure Boot.
        rc = run(["apt-get", "update"])
        if rc:
            return rc
        return run(["apt-get", "install", "-y", "linux-headers-amd64", "nvidia-kernel-dkms", "nvidia-driver",
                    "firmware-misc-nonfree", "nvidia-settings"])
    if action == "mok-import":
        # Mot de passe à usage unique lu sur l'entrée standard (jamais dans la ligne de commande).
        pw = sys.stdin.readline().rstrip("\n")
        if not (8 <= len(pw) <= 64):
            print("mot de passe : 8 à 64 caractères", file=sys.stderr); return 2
        if not os.path.exists(MOK_PUB):
            print("clé DKMS absente : installez d'abord le pilote", file=sys.stderr); return 3
        log("mokutil --import " + MOK_PUB)
        return subprocess.run(["mokutil", "--import", MOK_PUB], input=f"{pw}\n{pw}\n", text=True, check=False).returncode
    if action == "install-app":
        app = args[0] if args else ""
        if app not in GAME_APPS:
            print("application non autorisée", file=sys.stderr); return 2
        rc = run(["flatpak", "remote-add", "--system", "--if-not-exists", "flathub", FLATHUB])
        if rc:
            return rc
        return run(["flatpak", "install", "--system", "-y", "--noninteractive", "flathub", app])
    if action == "install-optional":
        key = args[0] if args else ""
        if key not in OPTIONAL_PACKAGES:
            print("composant inconnu", file=sys.stderr); return 2
        return run(["apt-get", "install", "-y", *OPTIONAL_PACKAGES[key]])
    print(f"action refusée : {action}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
