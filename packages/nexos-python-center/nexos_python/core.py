"""Cœur du Centre Python NexOS : profils verrouillés et projets, pilotés par uv.

Principes :
- Le Python système (Debian) n'est jamais modifié (PEP 668) : tout s'installe
  dans des environnements virtuels.
- Un profil = un projet uv versionné (pyproject.toml + uv.lock) livré dans
  /usr/share/nexos/python/profiles. Il est installé tel que verrouillé
  (`uv sync --frozen`) dans ~/.local/share/nexos/python/envs/<profil>.
- Un projet utilisateur = un dossier avec son pyproject.toml, son uv.lock et
  son .venv ; ajout/suppression/mise à jour via uv add/remove/lock.
Chaque opération renvoie un `OpResult` (commande, code, sortie, erreurs) pour
que l'interface affiche les erreurs telles quelles.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tomllib
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

SYSTEM_PROFILES = Path("/usr/share/nexos/python/profiles")
SYSTEM_PYTHON = "/usr/bin/python3"


def data_home() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "nexos" / "python"


def profiles_root() -> Path:
    override = os.environ.get("NEXOS_PYTHON_PROFILES")
    return Path(override) if override else SYSTEM_PROFILES


def uv_binary() -> str:
    for cand in (os.environ.get("NEXOS_UV"), "/usr/lib/nexos/uv/uv", shutil.which("uv")):
        if cand and Path(cand).exists():
            return cand
    raise FileNotFoundError("uv introuvable (paquet nexos-python-center incomplet)")


def python_interpreter() -> str:
    return os.environ.get("NEXOS_PYTHON", SYSTEM_PYTHON)


@dataclass
class OpResult:
    command: list[str]
    returncode: int
    output: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None,
        on_line: Callable[[str], None] | None = None, timeout: int | None = None) -> OpResult:
    """Exécute une commande en flux : chaque ligne est transmise à on_line (journal de l'interface)."""
    full_env = {**os.environ, "UV_PYTHON_DOWNLOADS": "never", "UV_NO_PROGRESS": "1", **(env or {})}
    proc = subprocess.Popen(cmd, cwd=cwd, env=full_env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, bufsize=1)
    lines = []
    assert proc.stdout is not None
    for line in proc.stdout:
        lines.append(line)
        if on_line:
            on_line(line.rstrip("\n"))
    proc.wait(timeout=timeout)
    return OpResult(cmd, proc.returncode, "".join(lines))


# ---------------------------------------------------------------- profils
@dataclass
class Profile:
    name: str
    path: Path
    description: str
    dependencies: list[str]
    locked_packages: int

    @property
    def env_path(self) -> Path:
        return data_home() / "envs" / self.name

    @property
    def installed(self) -> bool:
        return (self.env_path / "bin" / "python").exists()

    def size_mb(self) -> float:
        if not self.env_path.exists():
            return 0.0
        total = sum(f.stat().st_size for f in self.env_path.rglob("*") if f.is_file() and not f.is_symlink())
        return round(total / 2**20, 1)


def list_profiles() -> list[Profile]:
    out = []
    root = profiles_root()
    for d in sorted(root.glob("*/pyproject.toml")):
        meta = tomllib.loads(d.read_text(encoding="utf-8"))["project"]
        lock = d.parent / "uv.lock"
        n = lock.read_text(encoding="utf-8").count("[[package]]") if lock.exists() else 0
        out.append(Profile(d.parent.name, d.parent, meta.get("description", ""),
                           meta.get("dependencies", []), n))
    return out


def get_profile(name: str) -> Profile:
    for p in list_profiles():
        if p.name == name:
            return p
    raise KeyError(f"Profil inconnu : {name}")


def install_profile(name: str, on_line=None) -> OpResult:
    """Installe exactement les versions verrouillées (aucune résolution nouvelle)."""
    p = get_profile(name)
    p.env_path.parent.mkdir(parents=True, exist_ok=True)
    return run([uv_binary(), "sync", "--frozen", "--project", str(p.path),
                "--python", python_interpreter()],
               env={"UV_PROJECT_ENVIRONMENT": str(p.env_path)}, on_line=on_line)


def test_profile(name: str, on_line=None) -> OpResult:
    p = get_profile(name)
    if not p.installed:
        return OpResult(["test", name], 2, "Profil non installé.")
    return run([str(p.env_path / "bin" / "python"), "-m", "pytest", "-q", "-p", "no:cacheprovider",
                str(p.path / "tests")], cwd=p.path, env={"QT_QPA_PLATFORM": "offscreen",
                                                         "MPLBACKEND": "Agg"}, on_line=on_line)


def remove_profile(name: str) -> OpResult:
    p = get_profile(name)
    if p.env_path.exists():
        shutil.rmtree(p.env_path)
    return OpResult(["remove", name], 0, f"Environnement {p.env_path} supprimé.")


def register_kernel(name: str, on_line=None) -> OpResult:
    """Rend le profil disponible comme noyau Jupyter (« Python NexOS — <profil> »)."""
    p = get_profile(name)
    return run([str(p.env_path / "bin" / "python"), "-m", "ipykernel", "install", "--user",
                "--name", f"nexos-{name}", "--display-name", f"Python NexOS — {name}"], on_line=on_line)


# ---------------------------------------------------------------- projets
def projects_root() -> Path:
    return Path(os.environ.get("NEXOS_PROJECTS", Path.home() / "Projets Python"))


def create_project(name: str, profile: str | None = None, on_line=None) -> OpResult:
    """Nouveau projet uv. Si un profil est donné, ses dépendances directes sont reprises
    avec les versions exactes de son verrou (même combinaison testée)."""
    path = projects_root() / name
    if path.exists():
        return OpResult(["init", name], 1, f"Le dossier {path} existe déjà.")
    path.parent.mkdir(parents=True, exist_ok=True)
    r = run([uv_binary(), "init", "--app", "--vcs", "none", "--no-readme", "--python", python_interpreter(),
             "--name", name, str(path)], on_line=on_line)
    if not r.ok or not profile:
        return r
    pins = locked_versions(get_profile(profile))
    deps = [f"{_dist_name(d)}=={pins[_dist_name(d).lower()]}" if _dist_name(d).lower() in pins else d
            for d in get_profile(profile).dependencies]
    return add_packages(path, deps, on_line=on_line)


def _dist_name(req: str) -> str:
    for sep in "<>=!~[; ":
        req = req.split(sep)[0]
    return req.strip()


def locked_versions(profile: Profile) -> dict[str, str]:
    data = tomllib.loads((profile.path / "uv.lock").read_text(encoding="utf-8"))
    return {p["name"].lower(): p["version"] for p in data.get("package", []) if "version" in p}


def add_packages(project: Path, packages: list[str], on_line=None) -> OpResult:
    return run([uv_binary(), "add", "--project", str(project), *packages], on_line=on_line)


def remove_packages(project: Path, packages: list[str], on_line=None) -> OpResult:
    return run([uv_binary(), "remove", "--project", str(project), *packages], on_line=on_line)


def _current_spec(project: Path, name: str) -> str | None:
    deps = tomllib.loads((project / "pyproject.toml").read_text(encoding="utf-8"))["project"].get("dependencies", [])
    return next((d for d in deps if _dist_name(d).lower() == name.lower()), None)


def upgrade_packages(project: Path, packages: list[str] | None = None, on_line=None) -> OpResult:
    """Paquets nommés : passage à la dernière version, même s'ils étaient épinglés (==).
    uv conserve la contrainte existante lors d'un `uv add`, on la remplace donc :
    retrait puis ajout ; en cas d'échec de l'ajout, l'ancienne contrainte est restaurée.
    Sans nom : toutes les dépendances montent au maximum permis par leurs contraintes."""
    if not packages:
        r = run([uv_binary(), "lock", "--project", str(project), "--upgrade"], on_line=on_line)
        return r if not r.ok else run([uv_binary(), "sync", "--project", str(project)], on_line=on_line)
    log: list[str] = []
    for name in (_dist_name(p) for p in packages):
        old = _current_spec(project, name)
        if old is None:
            return OpResult(["upgrade", name], 1, f"{name} n'est pas une dépendance directe du projet.")
        r = remove_packages(project, [name], on_line=on_line)
        if r.ok:
            r = add_packages(project, [name], on_line=on_line)
            if not r.ok:
                add_packages(project, [old], on_line=on_line)   # restauration
        log.append(r.output)
        if not r.ok:
            return OpResult(r.command, r.returncode, "".join(log))
    return OpResult(["upgrade", *packages], 0, "".join(log))


def dependency_tree(project: Path, depth: int = 3) -> OpResult:
    return run([uv_binary(), "tree", "--project", str(project), "--depth", str(depth), "--frozen"])


def project_packages(project: Path) -> list[dict]:
    """Paquets installés dans le .venv du projet (nom, version)."""
    py = project / ".venv" / "bin" / "python"
    if not py.exists():
        return []
    # stdout seul : uv écrit ses avertissements sur stderr, qui casseraient le JSON.
    r = subprocess.run([uv_binary(), "pip", "list", "--format", "json", "--python", str(py)],
                       capture_output=True, text=True, check=False,
                       env={**os.environ, "UV_PYTHON_DOWNLOADS": "never"})
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else []


def list_projects() -> list[Path]:
    root = projects_root()
    return sorted(p.parent for p in root.glob("*/pyproject.toml")) if root.exists() else []


# ---------------------------------------------------------------- catalogue
@dataclass
class CatalogEntry:
    name: str
    category: str
    summary: str
    extra: dict = field(default_factory=dict)


CATALOG = [
    CatalogEntry("numpy", "Science", "Tableaux et calcul numérique"),
    CatalogEntry("pandas", "Science", "Tableaux de données, CSV, Excel"),
    CatalogEntry("scipy", "Science", "Algorithmes scientifiques, signal, optimisation"),
    CatalogEntry("sympy", "Science", "Calcul symbolique"),
    CatalogEntry("matplotlib", "Science", "Graphiques"),
    CatalogEntry("plotly", "Science", "Graphiques interactifs"),
    CatalogEntry("polars", "Science", "Tableaux de données rapides"),
    CatalogEntry("jupyterlab", "Science", "Carnets interactifs"),
    CatalogEntry("statsmodels", "Science", "Statistiques et économétrie"),
    CatalogEntry("torch", "IA", "Réseaux de neurones (PyTorch)"),
    CatalogEntry("tensorflow", "IA", "Réseaux de neurones (TensorFlow/Keras)"),
    CatalogEntry("scikit-learn", "IA", "Apprentissage automatique classique"),
    CatalogEntry("xgboost", "IA", "Gradient boosting"),
    CatalogEntry("onnxruntime", "IA", "Inférence de modèles ONNX"),
    CatalogEntry("transformers", "IA", "Modèles de langage et de vision (Hugging Face)"),
    CatalogEntry("opencv-python", "Vision", "Traitement d'images et vidéo"),
    CatalogEntry("pillow", "Vision", "Lecture et écriture d'images"),
    CatalogEntry("ultralytics", "Vision", "Détection d'objets YOLO"),
    CatalogEntry("pyserial", "Électronique", "Port série"),
    CatalogEntry("pyvisa", "Électronique", "Instruments de mesure (VISA)"),
    CatalogEntry("pyusb", "Électronique", "Périphériques USB"),
    CatalogEntry("esptool", "Électronique", "Programmation ESP32/ESP8266"),
    CatalogEntry("mpremote", "Électronique", "Cartes MicroPython"),
    CatalogEntry("pymodbus", "Électronique", "Protocole Modbus"),
    CatalogEntry("kivy", "Applications", "Interfaces tactiles multiplateformes"),
    CatalogEntry("PySide6", "Applications", "Interfaces Qt"),
    CatalogEntry("flask", "Applications", "Applications web légères"),
    CatalogEntry("fastapi", "Applications", "API web"),
    CatalogEntry("pytest", "Qualité", "Tests"),
    CatalogEntry("ruff", "Qualité", "Linter et formateur"),
    CatalogEntry("mypy", "Qualité", "Vérification de types"),
]


def search_catalog(query: str) -> Iterator[CatalogEntry]:
    q = query.lower().strip()
    for e in CATALOG:
        if not q or q in e.name.lower() or q in e.summary.lower() or q in e.category.lower():
            yield e


def pypi_info(name: str, timeout: int = 10) -> dict | None:
    """Fiche d'un paquet sur PyPI (nom exact). None si introuvable ou hors ligne."""
    try:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json", timeout=timeout) as r:
            info = json.load(r)["info"]
        return {"name": info["name"], "version": info["version"], "summary": info.get("summary") or "",
                "license": info.get("license_expression") or info.get("license") or "",
                "requires_python": info.get("requires_python") or ""}
    except Exception:  # noqa: BLE001 — réseau absent ou nom inexistant : réponse vide
        return None
