"""Évaluation de la QUALITÉ des réponses, notée automatiquement.

Chaque tâche a un correcteur objectif :
- code : le code Python de la réponse est EXÉCUTÉ (sous-processus isolé, délai
  court) puis confronté à des assertions ;
- commande / explication / fait : présence (regex) des éléments attendus ;
- toutes les réponses : contrôle que la réponse est en français.
Les réponses complètes sont enregistrées pour une relecture humaine.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import sysinfo
from .config import Config
from .engine import GenerationStats
from .manager import AssistantManager

FR_WORDS = {"le", "la", "les", "des", "est", "une", "un", "pour", "dans", "et", "vous", "qui",
            "pas", "sur", "avec", "cette", "votre", "fichier", "commande", "utilisez", "du", "au"}
EN_WORDS = {"the", "is", "and", "you", "to", "of", "this", "with", "for", "your", "file",
            "command", "use", "that", "are", "it"}


def is_french(text: str) -> bool:
    """Faux seulement si la prose est manifestement en anglais. Une réponse faite
    uniquement de code ou très courte (« 12 multiplié par 15 fait 180. ») est
    neutre et n'est pas pénalisée (correctif après relecture des résultats v1)."""
    prose = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    words = re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", prose.lower())
    fr = sum(w in FR_WORDS for w in words)
    en = sum(w in EN_WORDS for w in words)
    return not (en >= 3 and en > fr)


def extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.DOTALL)
    return "\n\n".join(blocks) if blocks else text


def run_python_checks(code: str, checks: str, timeout: int = 10) -> tuple[bool, str]:
    # Retire les exemples d'utilisation interactifs (input()) qui bloqueraient.
    code = re.sub(r"^.*\binput\(.*$", "", code, flags=re.MULTILINE)
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "t.py"
        f.write_text(code + "\n\n# --- vérifications ---\n" + checks, encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, "-I", str(f)], check=False, cwd=d, capture_output=True,
                               text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return False, "délai dépassé"
        return r.returncode == 0, (r.stderr or "")[-300:]


def has(*patterns: str) -> Callable[[str], tuple[bool, str]]:
    """Tous les motifs (regex, insensible à la casse) doivent apparaître."""
    def check(text: str) -> tuple[bool, str]:
        missing = [p for p in patterns if not re.search(p, text, flags=re.IGNORECASE)]
        return (not missing), ("manque : " + ", ".join(missing)) if missing else ""
    return check


def code_task(checks: str) -> Callable[[str], tuple[bool, str]]:
    return lambda text: run_python_checks(extract_code(text), checks)


@dataclass
class Task:
    id: str
    category: str
    prompt: str
    grade: Callable[[str], tuple[bool, str]]
    require_french: bool = True
    extra: dict = field(default_factory=dict)


SUMMARY_TEXT = ("Le Wi-Fi permet de connecter un ordinateur à Internet sans câble. "
                "Il utilise des ondes radio émises par un routeur. La portée dépend des murs "
                "et des interférences. Pour une meilleure stabilité, un câble Ethernet reste "
                "préférable, notamment pour les jeux en ligne et les appels vidéo.")

TASKS: list[Task] = [
    # Questions simples
    Task("q_capitale", "question", "Quelle est la capitale de l'Australie ?", has(r"canberra")),
    Task("q_calcul", "question", "Combien font 12 multiplié par 15 ?", has(r"\b180\b")),
    Task("q_ram", "question", "Quelle est la différence entre la RAM et un disque SSD ? Réponds en deux phrases.",
         has(r"temporaire|volatile|s'efface|perdu|éteint", r"stock|conserv|durabl|permanent")),
    Task("q_octets", "question", "Combien d'octets y a-t-il dans un kilooctet ?", has(r"\b10(00|24)\b")),
    # Commandes Linux
    Task("cmd_disque", "commande", "Quelle commande Linux affiche l'espace disque libre ? Explique-la brièvement.",
         has(r"\bdf\b")),
    Task("cmd_dossier", "commande", "Quelle commande Linux donne la taille totale d'un dossier ?",
         has(r"\bdu\b")),
    Task("cmd_ip", "commande", "Comment afficher mon adresse IP dans le terminal Linux ?",
         has(r"\bip (a|addr|address)\b|hostname -I|ifconfig")),
    Task("cmd_find", "commande", "Comment trouver tous les fichiers .pdf dans mon dossier personnel avec le terminal ?",
         has(r"\bfind\b|\blocate\b", r"\.pdf|pdf")),
    Task("cmd_exec", "commande", "Comment rendre le script monscript.sh exécutable ?",
         has(r"chmod\s+(\+x|u\+x|7\d\d)")),
    Task("cmd_proc", "commande", "Quelle commande montre les processus qui utilisent le plus le processeur ?",
         has(r"\b(h?top|ps)\b")),
    # Erreurs courantes
    Task("err_module", "erreur", "J'ai l'erreur Python « ModuleNotFoundError: No module named 'numpy' ». Que faire ?",
         has(r"pip3? install numpy|install(er|ez)? numpy|apt install python3-numpy")),
    Task("err_perm", "erreur", "Dans le terminal j'obtiens « Permission denied » en lançant ./run.sh. Pourquoi ?",
         has(r"permission|droit", r"chmod|exécut")),
    Task("err_cmd", "erreur", "Le terminal affiche « bash: htop: command not found ». Que signifie ce message ?",
         has(r"install|n'est pas install|introuvable|pas trouvé|n'existe pas")),
    Task("err_syntax", "erreur",
         "Pourquoi ce code Python provoque une SyntaxError ?\nif x > 3\n    print(x)",
         has(r":|deux[- ]points")),
    # Code Python (exécuté)
    Task("code_premiers", "code",
         "Écris une fonction Python premiers(n) qui renvoie la liste des nombres premiers strictement inférieurs à n.",
         code_task("assert premiers(20) == [2,3,5,7,11,13,17,19]\nassert premiers(2) == []\n")),
    Task("code_voyelles", "code",
         "Écris une fonction Python compter_voyelles(texte) qui compte les voyelles a, e, i, o, u, y (minuscules ou majuscules).",
         code_task("assert compter_voyelles('Bonjour') == 3\nassert compter_voyelles('xyz') == 1\nassert compter_voyelles('AEIOU') == 5\n")),
    Task("code_inverse", "code",
         "Écris une fonction Python inverser(mot) qui renvoie le mot écrit à l'envers.",
         code_task("assert inverser('python') == 'nohtyp'\nassert inverser('') == ''\n")),
    Task("code_moyenne", "code",
         "Corrige cette fonction pour qu'elle renvoie la moyenne de la liste, et renvoie 0 pour une liste vide :\n"
         "```python\ndef moyenne(l):\n    return sum(l) / len(l) + 1\n```",
         code_task("assert moyenne([2,4,6]) == 4\nassert moyenne([]) == 0\n")),
    Task("code_fichier", "code",
         "Écris une fonction Python compter_lignes(chemin) qui renvoie le nombre de lignes d'un fichier texte.",
         code_task("open('f.txt','w').write('a\\nb\\nc\\n')\nassert compter_lignes('f.txt') == 3\n")),
    # Résumé
    Task("resume", "resume", f"Résume ce texte en une seule phrase :\n{SUMMARY_TEXT}",
         lambda t: ((len(t.split()) <= 45 and bool(re.search(r"wi-?fi|sans fil", t, re.IGNORECASE))),
                    f"{len(t.split())} mots")),
    # Outils NexOS
    Task("nexos_python", "nexos", "Sur NexOS, où puis-je installer une bibliothèque Python comme pandas sans terminal ?",
         has(r"centre python")),
    Task("nexos_maj", "nexos", "Comment mettre à jour NexOS ?", has(r"centre de mises? à jour")),
    # Questions NexOS de contrôle, formulées autrement (ajoutées avec la base de connaissances)
    Task("nexos_fond", "nexos", "Je voudrais changer l'image derrière mes fenêtres, comment faire ?",
         has(r"param[eè]tres|configurer le bureau")),
    Task("nexos_ram", "nexos", "Mon ordinateur rame, comment voir quel programme utilise toute la mémoire ?",
         has(r"moniteur syst[eè]me|ctrl\+[ée]chap")),
]


def rescore(report: dict) -> dict:
    """Renote des réponses déjà enregistrées avec les correcteurs actuels."""
    by_id = {t.id: t for t in TASKS}
    for r in report["results"]:
        t = by_id.get(r["id"])
        if t:
            r["pass"], r["detail"] = t.grade(r["answer"])
            r["french"] = is_french(r["answer"]) if t.require_french else True
    _summarize(report)
    return report


def _summarize(report: dict) -> None:
    results = report["results"]
    cats: dict[str, list[bool]] = {}
    for r in results:
        cats.setdefault(r["category"], []).append(r["pass"])
    report["score"] = sum(r["pass"] for r in results)
    report["score_french_and_pass"] = sum(r["pass"] and r["french"] for r in results)
    report["total"] = len(results)
    report["french_rate"] = round(sum(r["french"] for r in results) / len(results), 2)
    report["by_category"] = {c: f"{sum(v)}/{len(v)}" for c, v in cats.items()}


def evaluate(cfg: Config, tasks: list[Task] = TASKS, out: Path | None = None) -> dict:
    mgr = AssistantManager(cfg)
    t0 = time.monotonic()
    mgr.ensure_started()
    load_s = time.monotonic() - t0
    pid = mgr.status().engine_pid
    anon_idle = sysinfo.smaps_mb(pid, "Pss_Anon")
    results, peak_rss, peak_anon = [], 0.0, 0.0
    for t in tasks:
        stats = GenerationStats()
        answer = "".join(mgr.ask(t.prompt, stats=stats))
        ok, detail = t.grade(answer)
        fr = is_french(answer) if t.require_french else True
        peak_rss = max(peak_rss, sysinfo.rss_mb(pid))
        peak_anon = max(peak_anon, sysinfo.smaps_mb(pid, "Pss_Anon"))
        results.append({"id": t.id, "category": t.category, "pass": ok, "french": fr,
                        "detail": detail, "answer": answer, "prompt": t.prompt,
                        "first_token_s": round(stats.first_token_s or 0, 3),
                        "total_s": round(stats.total_s, 2),
                        "tokens": stats.completion_tokens,
                        "tokens_per_s": round(stats.tokens_per_s or 0, 2)})
    mgr.unload()
    cats: dict[str, list[bool]] = {}
    for r in results:
        cats.setdefault(r["category"], []).append(r["pass"])
    tps = sorted(r["tokens_per_s"] for r in results if r["tokens_per_s"])
    report = {
        "measured": True,
        "date": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "model": Path(cfg.model_path).name,
        "model_file_mb": round(Path(cfg.model_path).stat().st_size / 2**20, 1),
        "machine": {"cores_physical": sysinfo.physical_cores(), "ram_total_mb": sysinfo.mem_total_mb()},
        "settings": {"ctx_size": cfg.ctx_size, "max_tokens": cfg.max_tokens,
                     "weight_repack": cfg.weight_repack},
        "load_s": round(load_s, 2),
        "engine_anon_idle_mb": round(anon_idle, 1),
        "engine_anon_peak_mb": round(peak_anon, 1),
        "engine_rss_peak_mb": round(peak_rss, 1),
        "score": sum(r["pass"] for r in results),
        "score_french_and_pass": sum(r["pass"] and r["french"] for r in results),
        "total": len(results),
        "french_rate": round(sum(r["french"] for r in results) / len(results), 2),
        "by_category": {c: f"{sum(v)}/{len(v)}" for c, v in cats.items()},
        "median_first_token_s": sorted(r["first_token_s"] for r in results)[len(results) // 2],
        "median_tokens_per_s": tps[len(tps) // 2] if tps else None,
        "results": results,
    }
    if out:
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
