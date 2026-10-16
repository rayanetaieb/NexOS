"""Cycle de vie du moteur : démarrage à la demande, garde RAM, file unique,
déchargement après inactivité et libération immédiate."""
from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass

from . import sysinfo
from .config import Config
from .engine import Engine, GenerationStats, LlamaServerEngine
from .prompts import system_prompt


class AssistantDisabled(RuntimeError):
    pass


class NotEnoughMemory(RuntimeError):
    pass


class Busy(RuntimeError):
    pass


class NoModel(RuntimeError):
    pass


@dataclass
class Status:
    enabled: bool
    model_path: str
    engine_running: bool
    engine_pid: int | None
    engine_rss_mb: float
    mem_available_mb: int
    required_free_mb: int
    idle_for_s: float | None
    unload_in_s: float | None


class AssistantManager:
    def __init__(self, config: Config,
                 engine_factory: Callable[[Config], Engine] | None = None,
                 mem_available: Callable[[], int] = sysinfo.mem_available_mb):
        self.config = config
        self._engine_factory = engine_factory or self._default_engine
        self._mem_available = mem_available
        self._engine: Engine | None = None
        self._request_lock = threading.Lock()   # règle 6 : 1 requête à la fois
        self._state_lock = threading.RLock()
        self._last_activity: float | None = None
        self._stop_watchdog = threading.Event()
        self._watchdog: threading.Thread | None = None

    # ---------- construction du moteur ----------
    @staticmethod
    def _default_engine(cfg: Config) -> Engine:
        threads = cfg.threads or sysinfo.default_threads()
        # GPU : désactivé tant que la détection + test d'exécution réel n'existent pas
        # (voir docs/AI_ASSISTANT.md). "auto" retombe donc sur CPU pour l'instant.
        gpu_layers = 0
        return LlamaServerEngine(cfg.server_binary, cfg.model_path, cfg.ctx_size, threads,
                                 gpu_layers=gpu_layers,
                                 startup_timeout_s=cfg.startup_timeout_s,
                                 request_timeout_s=cfg.request_timeout_s,
                                 weight_repack=cfg.weight_repack)

    # ---------- RAM ----------
    def required_free_mb(self) -> int:
        if self.config.min_free_ram_mb:
            return self.config.min_free_ram_mb
        size_mb = 0
        if self.config.model_path and os.path.isfile(self.config.model_path):
            size_mb = os.path.getsize(self.config.model_path) // (1024 * 1024)
        # Estimation : poids + cache KV (~ proportionnel au contexte) + marge système.
        kv_estimate = self.config.ctx_size // 16
        return size_mb + kv_estimate + self.config.ram_margin_mb

    def check_memory(self) -> None:
        need, avail = self.required_free_mb(), self._mem_available()
        if avail < need:
            raise NotEnoughMemory(
                f"RAM disponible insuffisante : {avail} Mio disponibles, "
                f"{need} Mio requis. Fermez des applications ou choisissez un modèle plus léger.")

    # ---------- cycle de vie ----------
    def ensure_started(self) -> Engine:
        with self._state_lock:
            if not self.config.enabled:
                raise AssistantDisabled("L'assistant IA est désactivé dans les paramètres.")
            if not self.config.model_path:
                raise NoModel("Aucun modèle installé. Ouvrez le gestionnaire de modèles.")
            if self._engine is not None and self._engine.running:
                return self._engine
            self.check_memory()                              # règle 8
            self._engine = self._engine_factory(self.config)
            self._engine.start()                             # règles 1, 2, 9 : seulement ici
            self._touch()
            self._start_watchdog()
            return self._engine

    def unload(self) -> bool:
        """Règle 4 : libère immédiatement la mémoire (arrêt du processus moteur)."""
        with self._state_lock:
            engine, self._engine = self._engine, None
            self._last_activity = None
            self._stop_watchdog.set()
        if engine is not None and engine.running:
            engine.stop()
            return True
        return False

    def shutdown(self) -> None:
        self.unload()

    def _touch(self) -> None:
        self._last_activity = time.monotonic()

    def _start_watchdog(self) -> None:
        if self._watchdog and self._watchdog.is_alive():
            return
        self._stop_watchdog = threading.Event()
        self._watchdog = threading.Thread(target=self._watch, name="nexai-idle", daemon=True)
        self._watchdog.start()

    def _watch(self) -> None:
        stop = self._stop_watchdog
        while not stop.wait(1.0):
            with self._state_lock:
                last = self._last_activity
                busy = self._request_lock.locked()
            if last is None:
                return
            if not busy and time.monotonic() - last >= self.config.idle_unload_seconds:
                self.unload()                                 # règle 3
                return

    # ---------- requêtes ----------
    def ask(self, question: str, history: list[dict] | None = None,
            stats: GenerationStats | None = None) -> Iterator[str]:
        if not self._request_lock.acquire(blocking=False):
            raise Busy("Une réponse est déjà en cours de génération.")
        try:
            engine = self.ensure_started()
            self._touch()
            messages = [{"role": "system", "content": system_prompt()}]
            messages += (history or [])[-6:]          # historique court : contexte borné
            messages.append({"role": "user", "content": question[:4000]})
            stats = stats if stats is not None else GenerationStats()
            for piece in engine.chat(messages, self.config.max_tokens, stats):
                self._touch()
                yield piece
        finally:
            self._touch()
            self._request_lock.release()

    # ---------- état ----------
    def status(self) -> Status:
        with self._state_lock:
            eng = self._engine
            pid = eng.pid if eng else None
            last = self._last_activity
        idle = time.monotonic() - last if last is not None else None
        return Status(
            enabled=self.config.enabled,
            model_path=self.config.model_path,
            engine_running=pid is not None,
            engine_pid=pid,
            engine_rss_mb=round(sysinfo.rss_mb(pid), 1) if pid else 0.0,
            mem_available_mb=self._mem_available(),
            required_free_mb=self.required_free_mb(),
            idle_for_s=round(idle, 1) if idle is not None else None,
            unload_in_s=(round(max(0.0, self.config.idle_unload_seconds - idle), 1)
                         if idle is not None else None),
        )
