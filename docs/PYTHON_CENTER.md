# Centre Python NexOS (phase 4)

Code : `packages/nexos-python-center/` (cœur `core.py`, commande `nexos-python`,
interface `nexos-python gui`). Profils : `python/profiles/`. Moteur : **uv** 0.13.1
(binaire officiel, MIT/Apache-2.0, `build/fetch-uv.sh`).

## Organisation
1. **Python système protégé** : Python 3.13 de Debian, réservé à l'OS (PEP 668). Rien n'y est installé.
2. **Profils** = projets uv versionnés (`pyproject.toml` + `uv.lock` + `tests/`), installés à
   l'identique (`uv sync --frozen`) dans `~/.local/share/nexos/python/envs/<profil>`.
3. **Projets** = dossiers dans `~/Projets Python/`, chacun avec son `.venv` et son `uv.lock` ;
   un projet peut partir d'un profil (mêmes versions que le verrou testé).
4. **Catalogue** : bibliothèques courantes classées par usage + fiche PyPI à la demande.

| Profil | Contenu principal | Paquets verrouillés |
|---|---|---|
| base | IPython, pytest, requests, rich | 30 |
| science | NumPy, SciPy, Pandas, SymPy, Matplotlib, JupyterLab, Statsmodels | 115 |
| ai | PyTorch, TensorFlow/Keras, scikit-learn, XGBoost, ONNX, ONNX Runtime | 112 |
| vision | OpenCV, Pillow, Ultralytics YOLO, PyTorch/torchvision, ONNX | 96 |
| electronics | PySerial, PyVISA (+pyvisa-py), PyUSB, SciPy, pyqtgraph, esptool, mpremote, pymodbus | 43 |
| appdev | Kivy, KivyMD, PySide6, pytest(-qt), Ruff, Mypy, build, PyInstaller | 47 |

Les profils sont séparés pour éviter les conflits et les installations inutiles :
on n'installe que ce dont on a besoin. Les gros profils (ai, vision) sont facultatifs.

## Fonctions (interface et `nexos-python`)
Profils : installer, tester, créer un noyau Jupyter, supprimer, voir la taille.
Projets : créer (vide ou depuis un profil), ajouter, supprimer, mettre à jour un paquet ou
tous, arbre des dépendances (`uv tree`), ouvrir le dossier.
Erreurs : la sortie complète d'uv est affichée dans le journal de la fenêtre.
Mise à jour d'un paquet épinglé (`==`) : retrait puis ajout de la dernière version, avec
**restauration automatique** de l'ancienne contrainte si l'ajout échoue (testé).

## GPU
Le profil `ai` contient un test qui n'annonce l'usage du GPU que si un calcul réel y
réussit (`torch.cuda.is_available()` puis opération sur le GPU). Sans GPU : CPU seulement.
**Limite** : le PyTorch de PyPI pour Linux embarque les bibliothèques CUDA (plusieurs Go).
Une variante CPU seule (plus légère) passe par `download.pytorch.org`, non accessible depuis
l'environnement de build : non testée à ce jour.

## Résultats mesurés
Voir `docs/MEASUREMENTS.md` (section Centre Python).
