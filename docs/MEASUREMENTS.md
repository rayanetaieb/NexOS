# Mesures publiées

Règle : seules figurent ici des valeurs **réellement obtenues**, avec leurs
conditions. Ce qui n'a pas été mesuré est marqué « NON MESURÉ ».

## Environnement de mesure (16/10/2026)
VM de développement cloud : Intel Xeon @ 2,10 GHz (AVX2, AMX), **2 cœurs**,
8 Go de RAM, sans swap, Ubuntu 24.04 (hôte de build, pas NexOS).
**Pas de KVM** : la VM NexOS tourne en émulation logicielle (QEMU TCG).
Ces chiffres ne représentent PAS un PC de bureau ; ils servent de référence
reproductible et de non-régression.

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
