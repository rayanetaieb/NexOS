# Mesures publiées

Règle : seules figurent ici des valeurs **réellement obtenues**, avec leurs
conditions. Ce qui n'a pas été mesuré est marqué « NON MESURÉ ».

## Environnement de mesure (16/10/2026)
VM de développement cloud : Intel Xeon @ 2,10 GHz (AVX2, AMX), **2 cœurs**,
8 Go de RAM, sans swap, Ubuntu 24.04 (hôte de build, pas NexOS).
**Pas de KVM** : la VM NexOS tourne en émulation logicielle (QEMU TCG).
Ces chiffres ne représentent PAS un PC de bureau ; ils servent de référence
reproductible et de non-régression.

## Priorité 1 — build Debian 13 (16/10/2026, soir)
Commande : `make keyring && make rootfs disk boot-test OUT=out/debian MIRROR=https://deb.debian.org/debian`
(+ `APT_PROXY`/`APT_CAINFO` dans l'environnement de build qui impose un proxy).

| Mesure | Valeur |
|---|---|
| Vérification des signatures APT | trousseau trixie obtenu par chaîne de confiance (InRelease bookworm → index → paquet), InRelease trixie : 3 signatures valides |
| Test de démarrage automatisé | **SUCCÈS** — `NexOS 0.1 prototype (base trixie)`, noyau `6.12.107+deb13-amd64`, `state=running`, 0 unité en échec, Python 3.13.5 |
| Durée du build rootfs | 189 s |
| RAM utilisée (système minimal, VM 1 Gio) | 141 Mio |

## Priorité 2 — bureau Plasma 6
Voir `docs/DESKTOP.md` : session Wayland ouverte et pilotée en VM (succès), 745 Mio
utilisés après ouverture de session (VM 4 Gio, émulation logicielle).

## Priorité 4 — profils Python (installation exacte depuis uv.lock + tests fonctionnels)
Machine de build (2 cœurs, réseau PyPI). Journaux : `docs/measurements/python-profiles/`.

| Profil | Installation | Taille | Tests | Remarque |
|---|---|---|---|---|
| base | 2 s | 55 Mio | 2/2 | |
| science | 6 s* | 539 Mio | 6/6 | *cache uv partiellement chaud |
| electronics | 51 s | 530 Mio | 5/5 | port série en boucle, VISA, filtrage, pyqtgraph |
| appdev | 37 s | 453 Mio | 4/4 | fenêtre Kivy/KivyMD réelle (Xvfb), PySide6, Ruff/Mypy, exécutable PyInstaller lancé |
| ai | 233 s | **7 819 Mio** | 4/4 | entraînement PyTorch + export ONNX vérifié, Keras, XGBoost ; GPU : aucun (CPU) |
| vision | 168 s | **5 988 Mio** | 3/3 | OpenCV, Pillow, YOLO construit et inféré hors ligne |
| data (0.3) | — | 839 Mio | 3/3 | Pandas = Polars = DuckDB sur le même calcul, Parquet + Excel aller-retour (texte arabe), Seaborn, Plotly |
| quality (0.3) | — | 105 Mio | 3/3 | Ruff et mypy détectent de vraies erreurs, couverture pytest-cov 100 %, Hypothesis |

Taille des profils ai/vision : le PyTorch de PyPI embarque CUDA. Variante CPU seule
(`download.pytorch.org`) non testable depuis l'environnement de build — à faire.
Centre Python : 11/11 tests (cœur, projets, restauration après échec, interface pilotée).

## Phase 2 — démarrage du prototype

Commande : `make rootfs SUITE=noble MIRROR=http://archive.ubuntu.com/ubuntu KERNEL=linux-image-virtual && make disk && make boot-test`
(le miroir Debian n'était pas joignable depuis l'environnement de build : la
chaîne a été validée avec la base Ubuntu 24.04 ; **le build Debian trixie par
défaut n'a pas encore été exécuté**.)

| Mesure | Valeur | Conditions |
|---|---|---|
| Test automatisé | **SUCCÈS** (`NEXOS-BOOT-OK`, `state=running`) | QEMU TCG, 1 Gio, 2 vCPU |
| Unités systemd en échec | 0 | |
| Temps de démarrage (`systemd-analyze`) | 7,3 s noyau + 16,8 s espace utilisateur = 24,2 s | **émulation TCG** : non représentatif d'un vrai PC |
| RAM utilisée après démarrage (`free`, colonne used) | 146 Mio | système minimal sans bureau, 105 processus |
| Taille rootfs (tar) | 236 Mio | |
| Bureau graphique, matériel réel, comparaison Windows/Debian | NON MESURÉ | phases 3, 5, 7 |

## Section 12 — assistant IA (nexai)

### Avertissement sur le modèle
Hugging Face n'était pas joignable depuis l'environnement de build. Les mesures
ont été faites avec un **modèle proxy** : architecture et dimensions exactes de
Qwen2.5‑0.5B, vrai tokenizer Qwen2, **poids aléatoires** (`tools/make_shape_proxy_gguf.py`),
quantifié en Q4_K_M avec `llama-quantize`. Il a le même coût mémoire/calcul
qu'un vrai 0,5B Q4_K_M mais produit du charabia.
→ RAM, chargement et vitesse : **mesurés** et représentatifs de cette taille.
→ Qualité des réponses (français, code, compréhension) : **NON MESURÉE**.

Moteur : llama.cpp compilé depuis les sources (commit `23f7aab`), CPU, 2 threads,
contexte 2048, réponses limitées à 384 tokens, `--parallel 1`, `-ngl 0`.

| Exigence G | Valeur mesurée | Source |
|---|---|---|
| RAM IA au repos (assistant non ouvert) | **0 Mio** — aucun processus nexai ni llama-server n'existe (vérifié par `pgrep`) | par construction + vérifié |
| RAM fenêtre ouverte, modèle non chargé | **77,6 Mio RSS** (dont 23,7 Mio anonymes ; le reste = bibliothèques Qt partagées) | `tests/gui_scenario.py`, Qt hors écran |
| Démarrage du moteur (chargement modèle → prêt) | 0,84 s / 1,04 s (2 passages) | `nexai bench` |
| RAM moteur chargé, au repos | 471 Mio RSS = **80 Mio anonymes** + 388 Mio de pages du fichier modèle (récupérables par le noyau) | `smaps_rollup` |
| RAM moteur, pic pendant génération | 511 Mio RSS | échantillonnage 50 ms |
| Délai avant le 1er token (1re question / suivantes) | 0,94–1,35 s / 0,19–0,67 s | 6 tâches × 2 passages |
| Vitesse de génération (médiane, réponses de 384 tokens) | **18,1 tokens/s** | 2 passages concordants |
| Moteur après déchargement | arrêté (`engine_running_after_unload=false`) ; MemAvailable revient à ±10 Mio de la valeur initiale | `nexai bench` |
| Bouton « Libérer la mémoire » | moteur arrêté immédiatement, 0 processus restant | `tests/gui_scenario.py` |
| Pénurie de RAM réelle (4,5 Gio occupés, 2 977 Mio dispo < 4 007 requis) | refus avec message clair, **aucun** processus lancé | test manuel, marge relevée |
| PC réel avec peu de mémoire (2–4 Go) | NON MESURÉ | à faire en phase 7 |

### Optimisation mesurée : réorganisation des poids (`--no-repack`)
Sur ce CPU, llama.cpp recopie par défaut une partie des poids dans un format
optimisé, en mémoire anonyme, en plus du fichier mappé. 3 passages chacun,
génération de 128 tokens :

| Réglage | Mémoire anonyme | Génération (tokens/s) |
|---|---|---|
| défaut (repack) | 305 Mio | 25,3 / 24,7 / 24,1 |
| `--no-repack` | **80 Mio** | 21,9 / 22,2 / 22,1 |

Décision : `--no-repack` par défaut (−225 Mio, −11 % de vitesse), option
`weight_repack = true` pour qui préfère la vitesse. Le gain dépend du CPU
(AMX/AVX2) : à re-mesurer sur les processeurs ciblés.

Fichiers bruts : `docs/measurements/nexai-bench-proxy-q4km-run{1,2}.json`.

### Priorité 3 — vrais modèles (remplace le proxy pour toute conclusion)
Fichiers téléchargés depuis les dépôts officiels Hugging Face, SHA-256 vérifiés
(`nexai models download`). Licences : Apache-2.0. Évaluation : `nexai eval`, tâches notées
automatiquement (code Python **exécuté** contre des tests, commandes/explications par motifs).

Évaluation v1 (22 tâches ; renotée après correction d'un faux négatif du détecteur de français) :

| Modèle | Fichier | Score | Code |
|---|---|---|---|
| SmolLM2-360M Q8_0 | 369 Mio | 7/22 | 1/5 |
| Qwen3-0.6B Q8_0 | 610 Mio | 12/22 | 3/5 |
| Qwen2.5-0.5B Q4_K_M | 469 Mio | 13/22 | 2/5 |
| Qwen2.5-1.5B Q4_K_M | 1 066 Mio | 18/22 | 5/5 |

Constat v1 : le prompt système (« tu ne peux exécuter aucune commande ») provoquait des
refus d'écrire du code ; les questions NexOS échouaient (mémo du prompt ignoré).
Corrections : prompt réécrit + base de connaissances injectée par mots-clés (`knowledge.py`)
+ 2 questions NexOS de contrôle formulées différemment.

Évaluation v2 (24 tâches, 1 passage chacun, température 0,3) :

| Modèle | Score | Question | Commande | Erreur | Code | Résumé | NexOS | RAM anonyme pic |
|---|---|---|---|---|---|---|---|---|
| **Qwen2.5-1.5B Q4_K_M** | **20/24** | 4/4 | 5/6 | 3/4 | 5/5 | 1/1 | 2/4 | 156 Mio |
| Qwen2.5-0.5B Q4_K_M | 12/24 | 3/4 | 3/6 | 1/4 | 2/5 | 1/1 | 2/4 | 130 Mio |
| Qwen3-0.6B Q8_0 | 10/24 | 1/4 | 2/6 | 1/4 | 3/5 | 1/1 | 2/4 | 381 Mio |

#### Mesures au calme (17/10/2026, 2 passages concordants, `docs/measurements/bench-real/`)
Machine : VM cloud Xeon 2,1 GHz, **2 cœurs**, 8 Go ; contexte 2048, réponses ≤ 384 tokens,
`--no-repack`, CPU uniquement. Charge de fond de l'environnement : ~1,7.

| Modèle | Prêt en | RAM anonyme (non récupérable) | Fichier mappé (récupérable) | Pic RSS | 1er token (médiane) | Génération (médiane) | Après déchargement |
|---|---|---|---|---|---|---|---|
| Qwen2.5-0.5B Q4_K_M | 0,8–1,4 s | 80 Mio | 476 Mio | 595–602 Mio | 0,54–0,57 s | 18,1 tokens/s | processus arrêté, RAM dispo revenue au niveau initial |
| Qwen2.5-1.5B Q4_K_M | 1,0–2,2 s | 112 Mio | 1 073 Mio | 1 255–1 257 Mio | 0,91–0,92 s | 9,8–10,0 tokens/s | idem |

#### Mémoire limitée (PC modeste simulé par cgroup, limite stricte du noyau)
Génération de 96 tokens, `llama-server` portable de l'image :

| Modèle | Limite | Génération | Usage max | Résultat |
|---|---|---|---|---|
| 0.5B | 2048 / 900 Mio | 21,6 tokens/s | 573 Mio | normal |
| 0.5B | 500 Mio | 22,7 tokens/s | 500 Mio | normal (pages du fichier recyclées) |
| 0.5B | 300 Mio | **3,8 tokens/s** | 300 Mio | très ralenti, pas de plantage |
| 1.5B | 2048 / 1300 Mio | 9,9–10,2 tokens/s | 1 204 Mio | normal |
| 1.5B | 800 Mio | **1,7 tokens/s** | 800 Mio | 6× plus lent, pas de plantage |
| 1.5B | 500 Mio | **1,4 tokens/s** | 500 Mio | inutilisable en pratique |

Aucun arrêt par manque de mémoire (OOM) : sous la taille du modèle, le noyau relit le
fichier en permanence. D'où la garde de l'assistant : démarrage refusé si la RAM disponible
est inférieure à taille du modèle + cache + marge (1,7 Go pour le 1,5B, 1,1 Go pour le 0,5B).
Non mesuré : vrai PC de 2–4 Go, CPU sans AVX2.

Les vitesses mesurées pendant les évaluations de qualité ne sont **pas retenues** (machine chargée par
d'autres builds). Choix provisoire : Qwen2.5-1.5B si RAM ≥ 6 Go, sinon Qwen2.5-0.5B
(qualité nettement plus faible : 12/24). Qwen3-0.6B écarté. À faire : passages répétés
(variance), mesure de vitesse au calme, test sur PC réel.
