"""Configuration de nexai (fichier TOML lisible et modifiable par l'utilisateur).

Emplacement : $XDG_CONFIG_HOME/nexos/nexai.toml (défaut ~/.config/nexos/nexai.toml).
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import asdict, dataclass, fields
from pathlib import Path


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "nexos"


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local/share")
    return Path(base) / "nexos" / "nexai"


@dataclass
class Config:
    enabled: bool = True                 # règle 7 : désactivation complète
    model_path: str = ""                 # fichier .gguf ; vide = aucun modèle installé
    server_binary: str = "llama-server"  # binaire llama.cpp (paquet nexos-llama-cpp)
    idle_unload_seconds: int = 120       # règle 3 : déchargement après inactivité
    ctx_size: int = 2048                 # règle 5 : contexte limité
    max_tokens: int = 384                # règle 5 : tokens générés limités
    threads: int = 0                     # 0 = auto (cœurs physiques - 1, min 1)
    min_free_ram_mb: int = 0             # 0 = auto (taille du modèle + marge)
    ram_margin_mb: int = 512             # marge laissée au système
    weight_repack: bool = False          # True = +vitesse, +RAM (mesuré : docs/MEASUREMENTS.md)
    gpu: str = "off"                     # règle 10 : "off" par défaut ; "auto" = après test réel
    startup_timeout_s: int = 120
    request_timeout_s: int = 300

    @classmethod
    def load(cls, path: Path | None = None) -> Config:
        path = path or config_dir() / "nexai.toml"
        cfg = cls()
        if path.exists():
            data = tomllib.loads(path.read_text(encoding="utf-8"))
            known = {f.name: f.type for f in fields(cls)}
            for key, value in data.items():
                if key in known:
                    setattr(cfg, key, type(getattr(cfg, key))(value))
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.gpu not in ("off", "auto"):
            raise ValueError("gpu doit valoir 'off' ou 'auto'")
        if not 256 <= self.ctx_size <= 32768:
            raise ValueError("ctx_size hors limites (256..32768)")
        if not 1 <= self.max_tokens <= self.ctx_size:
            raise ValueError("max_tokens doit être entre 1 et ctx_size")
        if self.idle_unload_seconds < 5:
            raise ValueError("idle_unload_seconds doit être >= 5")

    def save(self, path: Path | None = None) -> Path:
        path = path or config_dir() / "nexai.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for key, value in asdict(self).items():
            if isinstance(value, bool):
                lines.append(f"{key} = {'true' if value else 'false'}")
            elif isinstance(value, int):
                lines.append(f"{key} = {value}")
            else:
                escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
                lines.append(f'{key} = "{escaped}"')
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
