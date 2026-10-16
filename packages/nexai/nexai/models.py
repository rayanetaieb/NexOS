"""Gestion des modèles : catalogue, import local, téléchargement VÉRIFIÉ
(SHA-256 obligatoire), suppression.

Les empreintes SHA-256 du catalogue ont été relevées le 16/10/2026 depuis l'API
Hugging Face (champ lfs.oid des dépôts officiels) puis recontrôlées après
téléchargement. Une entrée sans empreinte n'est pas téléchargeable.
"""
from __future__ import annotations

import hashlib
import shutil
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from .config import data_dir


@dataclass(frozen=True)
class ModelInfo:
    key: str
    name: str
    params: str
    license: str
    url: str | None          # URL HTTPS du fichier GGUF (à valider)
    sha256: str | None       # obligatoire pour autoriser le téléchargement
    notes: str = ""


HF = "https://huggingface.co"

CATALOG: list[ModelInfo] = [
    ModelInfo("qwen2.5-0.5b-q4km", "Qwen2.5 0.5B Instruct (Q4_K_M)", "0,5 G", "Apache-2.0",
              f"{HF}/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf",
              "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
              "Candidat léger."),
    ModelInfo("qwen3-0.6b-q8", "Qwen3 0.6B (Q8_0)", "0,6 G", "Apache-2.0",
              f"{HF}/Qwen/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q8_0.gguf",
              "9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031",
              "Mode réflexion désactivé par /no_think."),
    ModelInfo("smollm2-360m-q8", "SmolLM2 360M Instruct (Q8_0)", "0,36 G", "Apache-2.0",
              f"{HF}/HuggingFaceTB/SmolLM2-360M-Instruct-GGUF/resolve/main/smollm2-360m-instruct-q8_0.gguf",
              "48ab3034d0dd401fbc721eb1df3217902fee7dab9078992d66431f09b7750201",
              "Le plus léger."),
    ModelInfo("qwen2.5-1.5b-q4km", "Qwen2.5 1.5B Instruct (Q4_K_M)", "1,5 G", "Apache-2.0",
              f"{HF}/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
              "6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e",
              "Référence qualité, pour machines >= 8 Go."),
    ModelInfo("gemma3-270m", "Gemma 3 270M IT", "0,27 G", "Gemma Terms of Use",
              None, None, "Licence spécifique : non retenu sans validation juridique."),
]


def models_dir() -> Path:
    d = data_dir() / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def _check_gguf(path: Path) -> None:
    with open(path, "rb") as f:
        if f.read(4) != b"GGUF":
            raise ValueError(f"{path} n'est pas un fichier GGUF valide")


def import_local(src: Path) -> tuple[Path, str]:
    """Copie un fichier GGUF local dans le dossier des modèles ; renvoie (chemin, sha256)."""
    src = Path(src)
    _check_gguf(src)
    dest = models_dir() / src.name
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return dest, sha256_file(dest)


def download(info: ModelInfo, progress=None) -> Path:
    """Téléchargement explicite (jamais automatique), vérifié par SHA-256."""
    if not info.url or not info.sha256:
        raise PermissionError(
            f"{info.name} : URL ou empreinte SHA-256 non validée — téléchargement refusé. "
            "Utilisez « nexai models import <fichier.gguf> » pour un fichier vérifié par vos soins.")
    dest = models_dir() / Path(info.url).name
    tmp = dest.with_suffix(dest.suffix + ".part")
    h = hashlib.sha256()
    with urllib.request.urlopen(info.url, timeout=60) as r, open(tmp, "wb") as out:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while block := r.read(1 << 20):
            out.write(block)
            h.update(block)
            done += len(block)
            if progress:
                progress(done, total)
    if h.hexdigest() != info.sha256.lower():
        tmp.unlink(missing_ok=True)
        raise ValueError("Empreinte SHA-256 incorrecte : fichier supprimé")
    tmp.replace(dest)
    _check_gguf(dest)
    return dest


def installed() -> list[Path]:
    return sorted(models_dir().glob("*.gguf"))


def remove(path: Path) -> None:
    path = Path(path).resolve()
    if models_dir().resolve() not in path.parents:
        raise PermissionError("Suppression limitée au dossier des modèles nexai")
    path.unlink()
