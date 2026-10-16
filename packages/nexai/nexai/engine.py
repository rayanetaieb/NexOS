"""Moteurs d'inférence. L'interface `Engine` isole l'assistant du moteur choisi.

`LlamaServerEngine` lance le binaire `llama-server` de llama.cpp dans un
processus séparé, écoutant UNIQUEMENT sur 127.0.0.1. Arrêter ce processus rend
au système la totalité de la mémoire du modèle : c'est ce qui permet une
consommation résiduelle quasi nulle quand l'assistant est inactif.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field

LOOPBACK = "127.0.0.1"


class EngineError(RuntimeError):
    pass


@dataclass
class GenerationStats:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    first_token_s: float | None = None   # délai avant le premier token (mesuré côté client)
    total_s: float = 0.0
    tokens_per_s: float | None = None    # vitesse de génération (rapportée par le moteur si dispo)
    extra: dict = field(default_factory=dict)


class Engine(ABC):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @property
    @abstractmethod
    def pid(self) -> int | None: ...

    @property
    def running(self) -> bool:
        return self.pid is not None

    @abstractmethod
    def chat(self, messages: list[dict], max_tokens: int,
             stats: GenerationStats, extra_body: dict | None = None) -> Iterator[str]:
        """Génère la réponse morceau par morceau et remplit `stats`."""


def _free_loopback_port() -> int:
    with socket.socket() as s:
        s.bind((LOOPBACK, 0))
        return s.getsockname()[1]


class LlamaServerEngine(Engine):
    def __init__(self, binary: str, model_path: str, ctx_size: int, threads: int,
                 gpu_layers: int = 0, startup_timeout_s: int = 120,
                 request_timeout_s: int = 300, weight_repack: bool = False,
                 extra_args: list[str] | None = None):
        self.binary = binary
        self.model_path = model_path
        self.ctx_size = ctx_size
        self.threads = threads
        self.gpu_layers = gpu_layers
        self.startup_timeout_s = startup_timeout_s
        self.request_timeout_s = request_timeout_s
        self.weight_repack = weight_repack
        self.extra_args = extra_args or []
        self._proc: subprocess.Popen | None = None
        self._port: int | None = None
        self.load_seconds: float | None = None
        # Aucun proxy : le trafic ne doit jamais quitter 127.0.0.1.
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    @property
    def pid(self) -> int | None:
        if self._proc is not None and self._proc.poll() is None:
            return self._proc.pid
        return None

    def command(self, port: int) -> list[str]:
        return [
            self.binary,
            "--host", LOOPBACK, "--port", str(port),
            "-m", self.model_path,
            "-c", str(self.ctx_size),
            "-t", str(self.threads),
            "--parallel", "1",                 # règle 6 : une seule requête
            "-ngl", str(self.gpu_layers),      # règle 10 : 0 couche GPU par défaut
            "--no-webui",                      # pas d'interface web embarquée
            *([] if self.weight_repack else ["--no-repack"]),  # évite une copie des poids en RAM
            *self.extra_args,
        ]

    def start(self) -> None:
        if self.running:
            return
        if not os.path.isfile(self.model_path):
            raise EngineError(f"Modèle introuvable : {self.model_path}")
        self._port = _free_loopback_port()
        t0 = time.monotonic()
        self._proc = subprocess.Popen(
            self.command(self._port),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            start_new_session=True,
        )
        deadline = t0 + self.startup_timeout_s
        while time.monotonic() < deadline:
            if self._proc.poll() is not None:
                err = (self._proc.stderr.read() or b"").decode(errors="replace")[-2000:]
                self._proc = None
                raise EngineError(f"Le moteur s'est arrêté au démarrage :\n{err}")
            try:
                with self._opener.open(self._url("/health"), timeout=2) as r:
                    if r.status == 200:
                        self.load_seconds = time.monotonic() - t0
                        return
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                pass
            time.sleep(0.1)
        self.stop()
        raise EngineError("Délai de démarrage du moteur dépassé")

    def stop(self) -> None:
        proc, self._proc = self._proc, None
        if proc is None or proc.poll() is not None:
            return
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=10)
        except ProcessLookupError:
            pass
        finally:
            if proc.stderr:
                proc.stderr.close()

    def _url(self, path: str) -> str:
        return f"http://{LOOPBACK}:{self._port}{path}"

    def chat(self, messages: list[dict], max_tokens: int,
             stats: GenerationStats, extra_body: dict | None = None) -> Iterator[str]:
        if not self.running:
            raise EngineError("Moteur non démarré")
        body = json.dumps({
            "messages": messages, "max_tokens": max_tokens, "stream": True,
            "temperature": 0.3, "stream_options": {"include_usage": True},
            **(extra_body or {}),
        }).encode()
        req = urllib.request.Request(self._url("/v1/chat/completions"), data=body,
                                     headers={"Content-Type": "application/json"})
        t0 = time.monotonic()
        with self._opener.open(req, timeout=self.request_timeout_s) as resp:
            for raw in resp:
                line = raw.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                chunk = json.loads(payload)
                if chunk.get("usage"):
                    stats.prompt_tokens = chunk["usage"].get("prompt_tokens", 0)
                    stats.completion_tokens = chunk["usage"].get("completion_tokens", 0)
                if chunk.get("timings"):
                    stats.tokens_per_s = chunk["timings"].get("predicted_per_second")
                    stats.extra["timings"] = chunk["timings"]
                for choice in chunk.get("choices", []):
                    text = (choice.get("delta") or {}).get("content")
                    if text:
                        if stats.first_token_s is None:
                            stats.first_token_s = time.monotonic() - t0
                        yield text
        stats.total_s = time.monotonic() - t0
        if stats.tokens_per_s is None and stats.completion_tokens and stats.first_token_s is not None:
            gen_time = stats.total_s - stats.first_token_s
            if gen_time > 0 and stats.completion_tokens > 1:
                stats.tokens_per_s = (stats.completion_tokens - 1) / gen_time
