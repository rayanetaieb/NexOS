# Assistant IA local (nexai) — conception et état

Code : `packages/nexai/`. Statut : **prototype opérationnel et testé** (moteur,
cycle de vie, CLI, fenêtre) ; **modèle définitif non choisi** (évaluation
qualité impossible sans vrais poids, voir plus bas).

## Architecture
```
 Raccourci Meta+Espace / lanceur  ──►  nexai gui (PySide6)          ← seul processus quand la fenêtre est ouverte
                                         │ AssistantManager
                                         │  · garde RAM · 1 requête · minuteur d'inactivité
                                         ▼ (à la 1re question seulement)
                                    llama-server (llama.cpp, processus séparé)
                                         écoute 127.0.0.1:<port aléatoire>, sans proxy, sans web UI
                                         ▲
                              modèle GGUF dans ~/.local/share/nexos/nexai/models/
```
Le moteur est un **processus séparé** : l'arrêter rend toute sa mémoire au
système, ce qu'aucun déchargement en place ne garantit aussi bien. Le remplacer
(autre moteur, autre modèle) ne touche pas l'interface : interface `Engine`
dans `nexai/engine.py`.

## Les 10 règles mémoire → implémentation
| # | Règle | Implémentation | Vérifié par |
|---|---|---|---|
| 1 | Pas de chargement au démarrage de NexOS | aucun service système ni autostart | inspection + `pgrep` |
| 2 | Moteur lancé à l'ouverture/usage | `ensure_started()` appelé uniquement par `ask()` (plus économe que « à l'ouverture ») | `test_no_engine_process_until_first_question`, scénario GUI |
| 3 | Déchargement après inactivité configurable | fil `nexai-idle`, `idle_unload_seconds` | `test_idle_unload` |
| 4 | Bouton de libération immédiate | « Libérer la mémoire » → `unload()` | scénario GUI |
| 5 | Contexte et tokens limités | `ctx_size` 2048, `max_tokens` 384, historique 6 messages, question tronquée à 4000 caractères | validation de config |
| 6 | Une requête à la fois | verrou non bloquant + `--parallel 1` | `test_single_request_at_a_time` |
| 7 | Désactivation complète | `enabled = false` / `nexai disable` | `test_disabled` |
| 8 | Avertissement si RAM insuffisante | `MemAvailable` ≥ taille modèle + cache estimé + marge, sinon refus explicite | `test_low_memory_refuses_to_start` + test réel |
| 9 | Pas de processus IA en arrière-plan | idem 1 ; fermer la fenêtre arrête le moteur | scénario GUI |
| 10 | GPU jamais sans vérification | `-ngl 0` forcé ; `gpu="auto"` retombe sur CPU tant que le test d'exécution GPU n'existe pas | test d'arguments |

## Fonctionnement local et sécurité
- Le moteur écoute uniquement sur `127.0.0.1` ; le client ignore les variables
  de proxy. Aucune donnée ne quitte la machine.
- Aucun téléchargement automatique. `nexai models download` refuse tout modèle
  dont l'URL et l'empreinte SHA-256 n'ont pas été validées dans le catalogue ;
  `nexai models import` accepte un GGUF local (vérifie l'en-tête, affiche le SHA-256).
- L'assistant **n'exécute rien** : aucun code d'exécution de commande n'existe.
  Les commandes proposées contenant des motifs sensibles (`sudo`, `rm -`, `dd`,
  `mkfs`, `| sh`…) sont signalées par l'interface, indépendamment du modèle.
- Une future fonction « action » passera par une liste blanche d'opérations
  documentées, confirmées une à une, sans privilège permanent (polkit).

## Comparaison des modèles — protocole (à exécuter)
Candidats (tous à re-vérifier : nom de fichier, licence, empreinte) :
Qwen2.5‑0.5B‑Instruct Q4_K_M (Apache‑2.0), Qwen3‑0.6B Q8_0 (Apache‑2.0),
SmolLM2‑360M‑Instruct Q8_0 (Apache‑2.0), Gemma 3 270M (licence Gemma : revue
juridique avant redistribution).

Pour chacun : `nexai bench -o <modèle>.json` (RAM, taille, latence, vitesse,
réponses aux 6 tâches de `nexai/bench.py`), puis notation humaine 0–2 par
tâche (exactitude, français, code exécutable — les scripts Python générés sont
exécutés par pytest). Choix = meilleur score qualité sous contrainte
RAM anonyme < 300 Mio et ≥ 10 tokens/s sur la machine cible la plus modeste.

## Reste à faire
- Mesures avec de vrais poids et notation qualité (bloqué ici : Hugging Face inaccessible).
- Test sur PC réel 2–4 Go de RAM ; test sur CPU sans AVX2.
- Paquet `.deb` (`nexai` + `nexos-llama-cpp` compilé pour x86-64-v2 et v3).
- Gestionnaire graphique des modèles (aujourd'hui : CLI `nexai models`).
- Détection GPU + test d'exécution réel avant toute utilisation de `-ngl > 0`.
- Icône `nexos-assistant`, vérification visuelle de la fenêtre sur Plasma.
