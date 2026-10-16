"""Banc de mesure (section G) : toutes les valeurs produites ici sont MESURÉES
sur la machine qui exécute le banc ; rien n'est estimé ni inventé."""
from __future__ import annotations

import json
import platform
import threading
import time
from pathlib import Path

from . import sysinfo
from .config import Config
from .engine import GenerationStats
from .manager import AssistantManager

# Tâches représentatives des usages visés (section A). La qualité est notée
# par un humain à partir des réponses enregistrées dans le rapport.
TASKS = [
    ("question_simple", "Quelle est la différence entre la RAM et le stockage ?"),
    ("parametre", "Comment changer le fond d'écran sur un bureau KDE Plasma ?"),
    ("erreur", "Que signifie l'erreur Python « ModuleNotFoundError: No module named 'numpy' » et comment la corriger ?"),
    ("code", "Écris une fonction Python qui renvoie les nombres premiers inférieurs à n."),
    ("resume", ("Résume en une phrase : Le processeur exécute les instructions des programmes. "
               "La mémoire vive conserve temporairement les données utilisées. Le disque stocke "
               "durablement les fichiers, même lorsque l'ordinateur est éteint.")),
    ("commande", "Quelle commande Linux affiche l'espace disque libre ? Explique-la."),
]


class _PeakSampler(threading.Thread):
    def __init__(self, pid_fn, period=0.05):
        super().__init__(daemon=True)
        self.pid_fn, self.period = pid_fn, period
        self.peak_rss = 0.0
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            pid = self.pid_fn()
            if pid:
                self.peak_rss = max(self.peak_rss, sysinfo.rss_mb(pid))
            time.sleep(self.period)

    def stop(self):
        self._stop.set()
        self.join()


def run(cfg: Config, out: Path | None = None, tasks=TASKS) -> dict:
    mgr = AssistantManager(cfg)
    report: dict = {
        "measured": True,
        "date": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "machine": {"cpu": platform.processor() or platform.machine(),
                    "cores_physical": sysinfo.physical_cores(),
                    "ram_total_mb": sysinfo.mem_total_mb(),
                    "avx2": "avx2" in sysinfo.cpu_flags()},
        "model": cfg.model_path,
        "model_file_mb": round(Path(cfg.model_path).stat().st_size / 2**20, 1) if cfg.model_path else None,
        "settings": {"ctx_size": cfg.ctx_size, "max_tokens": cfg.max_tokens,
                     "weight_repack": cfg.weight_repack,
                     "threads": cfg.threads or sysinfo.default_threads(), "gpu": cfg.gpu},
    }
    report["mem_available_before_mb"] = sysinfo.mem_available_mb()

    t0 = time.monotonic()
    mgr.ensure_started()
    report["engine_start_s"] = round(time.monotonic() - t0, 3)
    pid = mgr.status().engine_pid
    report["engine_rss_loaded_idle_mb"] = round(sysinfo.rss_mb(pid), 1)
    report["engine_pss_loaded_idle_mb"] = round(sysinfo.pss_mb(pid), 1)
    report["engine_anon_loaded_idle_mb"] = round(sysinfo.smaps_mb(pid, "Pss_Anon"), 1)
    report["engine_file_loaded_idle_mb"] = round(sysinfo.smaps_mb(pid, "Pss_File"), 1)

    results = []
    for name, prompt in tasks:
        stats = GenerationStats()
        sampler = _PeakSampler(lambda: mgr.status().engine_pid)
        sampler.start()
        answer = "".join(mgr.ask(prompt, stats=stats))
        sampler.stop()
        results.append({"task": name, "prompt": prompt, "answer": answer,
                        "first_token_s": round(stats.first_token_s, 3) if stats.first_token_s else None,
                        "total_s": round(stats.total_s, 3),
                        "completion_tokens": stats.completion_tokens,
                        "tokens_per_s": round(stats.tokens_per_s, 2) if stats.tokens_per_s else None,
                        "engine_peak_rss_mb": round(sampler.peak_rss, 1)})
    report["tasks"] = results
    report["mem_available_during_mb"] = sysinfo.mem_available_mb()

    mgr.unload()
    time.sleep(1.0)
    report["engine_running_after_unload"] = mgr.status().engine_running
    report["mem_available_after_unload_mb"] = sysinfo.mem_available_mb()
    if out:
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
