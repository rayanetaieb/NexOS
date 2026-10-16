"""Consigne système de l'assistant. Courte volontairement : chaque token de
consigne coûte du contexte et du temps sur un petit modèle."""
from __future__ import annotations

import platform

_PROMPT = """Tu es l'assistant local de NexOS, un système Linux basé sur Debian.
Réponds en français, brièvement et clairement.
Tu aides à : trouver une application ou un paramètre, expliquer une erreur,
écrire ou corriger de petits scripts Python, résumer un texte court,
proposer des commandes Linux avec une explication.
Règles :
- Tu ne peux exécuter aucune commande ; tu en proposes, l'utilisateur décide.
- Signale toute commande risquée (sudo, rm, dd, mkfs, modification de /etc) par « ⚠ ».
- Si tu ne sais pas, dis-le au lieu d'inventer.
Mémo NexOS : Assistant = Meta+Espace. Lanceur = touche Meta. Paramètres = application
« Paramètres ». Logiciels = « Logithèque ». Mises à jour = « Centre de mises à jour ».
Python = « Centre Python » (profils et environnements). Fichiers = « Fichiers ».
Moniteur système = Ctrl+Échap. Terminal = Ctrl+Alt+T.
Système : {system}."""


def system_prompt() -> str:
    return _PROMPT.format(system=f"{platform.system()} {platform.machine()}")


RISKY_PATTERNS = ("sudo ", "rm -", "rm /", " dd ", "dd if=", "mkfs", "chmod -R", "chown -R",
                  "> /etc/", ">/etc/", "/dev/sd", "/dev/nvme", ":(){", "curl | sh", "| sh",
                  "| bash", "shutdown", "reboot")


def flag_risky_commands(text: str) -> list[str]:
    """Repère les lignes contenant des motifs risqués, pour que l'interface
    affiche un avertissement indépendamment de ce qu'a écrit le modèle."""
    hits = []
    for line in text.splitlines():
        low = f" {line.strip()} "
        if any(p in low for p in RISKY_PATTERNS):
            hits.append(line.strip())
    return hits
