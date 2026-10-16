"""Installation assistée de MiKTeX (distribution TeX) sur NexOS.

MiKTeX publie ses paquets Debian sur son propre dépôt (miktex.org), non joignable depuis
l'environnement de build NexOS : il n'est donc pas dans l'ISO. NexOS fournit TeX Live
(moteur testé) et ce module, qui installe MiKTeX à la demande :
1. téléchargement de la clé du dépôt MiKTeX, affichage de son empreinte à l'utilisateur ;
2. ajout du dépôt signé (signed-by), installation du paquet « miktex » ;
3. finalisation partagée (miktexsetup --shared=yes finish) et installation des paquets
   manquants à la volée ([MPM]AutoInstall=1).
Les étapes administrateur passent par pkexec (confirmation du mot de passe).
Coexistence : MiKTeX installe ses commandes dans /usr/local/bin, prioritaire sur TeX Live.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

KEY_URL = "https://miktex.org/download/key"
REPO_LINE = "deb [signed-by=/usr/share/keyrings/miktex.gpg] https://miktex.org/download/debian {suite} universe"
# MiKTeX publie des paquets par version Debian ; on essaie la version courante puis la précédente.
SUITES = ("trixie", "bookworm")

ROOT_SCRIPT = """#!/bin/sh
set -e
install -m 0644 "$1" /usr/share/keyrings/miktex.gpg
echo "$2" > /etc/apt/sources.list.d/miktex.list
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y miktex
miktexsetup --shared=yes finish
initexmf --admin --set-config-value [MPM]AutoInstall=1
"""


def installed() -> bool:
    return shutil.which("miktex") is not None or Path("/opt/miktex").exists()


def fetch_key(tmpdir: Path) -> tuple[Path, str]:
    """Télécharge la clé, la convertit (gpg --dearmor) et renvoie (chemin, empreinte)."""
    raw = tmpdir / "miktex.asc"
    with urllib.request.urlopen(KEY_URL, timeout=30) as r:
        raw.write_bytes(r.read())
    gpgfile = tmpdir / "miktex.gpg"
    subprocess.run(["gpg", "--batch", "--yes", "--dearmor", "-o", str(gpgfile), str(raw)], check=True)
    out = subprocess.run(["gpg", "--show-keys", "--with-colons", str(gpgfile)],
                         capture_output=True, text=True, check=True).stdout
    fpr = next((ln.split(":")[9] for ln in out.splitlines() if ln.startswith("fpr:")), "?")
    return gpgfile, fpr


def suite_available(suite: str) -> bool:
    try:
        with urllib.request.urlopen(f"https://miktex.org/download/debian/dists/{suite}/Release", timeout=20):
            return True
    except Exception:  # noqa: BLE001 — absent ou hors ligne
        return False


def install(confirm_fingerprint) -> int:
    """confirm_fingerprint(fpr) -> bool : l'utilisateur valide l'empreinte affichée."""
    with tempfile.TemporaryDirectory() as d:
        key, fpr = fetch_key(Path(d))
        if not confirm_fingerprint(fpr):
            return 2
        suite = next((s for s in SUITES if suite_available(s)), None)
        if not suite:
            raise RuntimeError("aucun dépôt MiKTeX compatible trouvé (trixie/bookworm)")
        script = Path(d) / "install-miktex.sh"
        script.write_text(ROOT_SCRIPT, encoding="utf-8"); script.chmod(0o755)
        return subprocess.run(["pkexec", str(script), str(key), REPO_LINE.format(suite=suite)], check=False).returncode
