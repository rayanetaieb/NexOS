"""Petite base de connaissances NexOS injectée dans la question.

Les modèles de 0,5 à 1,5 milliard de paramètres exploitent mal un long prompt
système (mesuré : 0/2 à 1/2 sur les questions NexOS). On ajoute donc, à la
question elle-même, uniquement les faits pertinents trouvés par mots-clés.
Aucun appel réseau, coût négligeable.
"""
from __future__ import annotations

import re
import unicodedata

# (mots-clés, fait). Un fait est retenu si au moins un mot-clé apparaît.
FACTS: list[tuple[tuple[str, ...], str]] = [
    (("bibliotheque python", "librairie", "pip", "pandas", "numpy", "module python", "package python",
      "environnement python", "venv", "profil python", "jupyter", "installer python"),
     ("Sur NexOS, les bibliothèques Python s'installent sans terminal avec l'application « Centre Python » "
     "(onglets Profils, Projets et Catalogue) ; en terminal : nexos-python add <paquet>.")),
    (("mettre a jour", "mise a jour", "mises a jour", "update", "upgrade", "actualiser le systeme"),
     ("Sur NexOS, les mises à jour se font avec l'application « Centre de mises à jour » ; un instantané "
     "est pris avant chaque mise à jour pour pouvoir revenir en arrière.")),
    (("installer un logiciel", "installer une application", "installer une appli", "desinstaller",
      "logitheque", "application", "logiciel"),
     "Sur NexOS, les applications s'installent et se désinstallent avec « NexOS Store » (menu NexOS), qui regroupe les paquets Debian et Flathub."),
    (("fond d'ecran", "fond ecran", "wallpaper", "theme", "mode sombre", "mode clair", "couleur",
      "apparence", "parametre", "reglage", "configurer"),
     ("Sur NexOS, l'application « Paramètres » regroupe l'apparence (mode clair/sombre, fond d'écran), "
     "le réseau, le son, l'affichage, les comptes et le pare-feu. Clic droit sur le bureau → "
     "« Configurer le bureau et le fond d'écran ».")),
    (("memoire", "ram", "processeur", "cpu", "lent", "ralenti", "processus", "moniteur", "gpu", "disque plein"),
     "Sur NexOS, « Moniteur système » (Ctrl+Échap) affiche processeur, mémoire, disque, réseau et processus."),
    (("fichier", "dossier", "explorateur", "documents", "telechargements"),
     "Sur NexOS, l'application « Fichiers » (Meta+E) gère les fichiers et dossiers."),
    (("terminal", "console", "ligne de commande"),
     "Sur NexOS, le terminal s'ouvre avec Ctrl+Alt+T."),
    (("assistant", "ia", "intelligence artificielle", "memoire de l'assistant", "liberer"),
     "L'assistant NexOS s'ouvre avec Meta+Espace ; le bouton « Libérer la mémoire » arrête le modèle."),
    (("capture", "screenshot", "copie d'ecran"),
     "Sur NexOS, la touche Impr. écran ouvre l'outil de capture d'écran."),
]


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def relevant_facts(question: str, limit: int = 2) -> list[str]:
    q = _norm(question)
    hits = []
    for keywords, fact in FACTS:
        score = sum(1 for k in keywords if re.search(r"\b" + re.escape(k), q))
        if score:
            hits.append((score, fact))
    hits.sort(key=lambda h: -h[0])
    return [f for _, f in hits[:limit]]


def augment(question: str) -> str:
    facts = relevant_facts(question)
    if not facts:
        return question
    return "Informations NexOS utiles :\n- " + "\n- ".join(facts) + f"\n\nQuestion : {question}"
