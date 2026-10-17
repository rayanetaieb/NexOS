# NexOS face aux autres systèmes — mesures réelles

État au 17/10/2026. **Ce document ne contient que des valeurs réellement mesurées.** Les mesures
invalidées en cours de route sont listées à la fin avec la raison.

## Ce qui est comparé, et comment

| Système | Origine de l'image | Bureau |
|---|---|---|
| NexOS 0.3 | `make rootfs EDITION=desktop` (ce dépôt) | Plasma 6.3, Wayland, thème NexOS |
| Debian 13 KDE « d'origine » | `tests/perf/compare/build-reference.sh debian-kde` : tâches `task-desktop` + `task-kde-desktop` + français, comme l'installateur Debian | Plasma 6.3, Wayland |
| Kubuntu 24.04 LTS | même script, métapaquet officiel `kubuntu-desktop` | Plasma 5.27, X11 |
| Ubuntu 24.04 LTS | même script, métapaquet officiel `ubuntu-desktop` | GNOME 46, Wayland |

Les images ISO officielles n'étaient pas téléchargeables depuis l'environnement de construction
(cdimage.ubuntu.com, Fedora, Microsoft bloqués). Les systèmes de référence sont donc construits
depuis **leurs dépôts officiels**, sans aucune modification hormis : un compte « test » en connexion
automatique et le service de mesure `boot-check.sh` (identique pour tous).

**Banc** (`tests/perf/measure_idle.py`) : QEMU sans KVM (émulation logicielle TCG), 4 Gio de RAM,
4 processeurs virtuels « Nehalem », disque en lecture seule (chaque mesure = premier démarrage),
démarrage direct du noyau, connexion automatique, aucune action. Le bureau est considéré **affiché**
quand une capture d'écran montre plus de 60 % de pixels non noirs deux fois de suite ; la mémoire est
lue **90 s après cet affichage** (MemTotal − MemAvailable). Une capture est conservée comme preuve.
3 mesures par système.

**Limites** : l'émulation logicielle est 10 à 50 fois plus lente qu'un vrai PC ; les durées ne valent
que **en comparaison relative** dans ce banc. La mémoire, elle, dépend peu de la vitesse. Aucun PC
réel n'a été mesuré (scripts fournis : `tests/perf/real-hw/`).

## Résultats valides : NexOS 0.3 contre Debian 13 KDE d'origine

| | NexOS 0.3 (3 mesures) | Debian 13 KDE (3 mesures) | Écart |
|---|---|---|---|
| Mémoire utilisée 90 s après l'affichage | 1 070 / 1 070 / 1 088 Mio | 956 / 964 / 967 Mio | **NexOS +115 Mio** |
| Démarrage, partie système (userspace) | 57,0 / 56,9 / 53,9 s | 36,7 / 33,1 / 40,2 s | **NexOS +19 s** |
| Bureau affiché après lancement du shell | 94 / 78 / 94 s | 63 / 63 / 79 s | NexOS +20 s |
| Services en échec | 0 | 0 | |
| Paquets installés | voir `docs/` | 1 001 (2,06 Go) | NexOS fournit en plus KiCad, TeX Live, JDK, LibreOffice, Arduino… |

Preuves : `docs/measurements/comparaison/*-preuve.png` et `*.txt` (rapport série complet, liste des
processus, durées par service).

**Conclusion honnête : à ce jour, NexOS 0.3 n'est pas plus performant que la Debian sur laquelle il
repose.** Il utilise environ 115 Mio de plus au repos et démarre environ 19 s plus lentement dans ce banc.

### D'où vient l'écart (relevé dans les mesures)
- **Portail de bureau** (`xdg-desktop-portal`, ≈130 Mo de mémoire résidente, en partie partagée) :
  démarré avec la session Plasma de NexOS, absent de la Debian d'origine (qui ne l'installe pas).
  Il sert au partage d'écran, aux sélecteurs de fichiers des applications Flatpak et à d'autres
  fonctions Wayland. Le retirer réduirait la mémoire mais casserait ces fonctions — non fait.
- **Démarrage** : `ufw` (pare-feu, 15–19 s ici) et le pré-réseau sont sur le chemin critique ;
  la Debian d'origine n'a pas de pare-feu actif. Arbitrage sécurité / démarrage assumé.
- La mémoire continue de monter pendant les minutes suivantes **sur les deux systèmes**
  (≈ +130 Mio/min, puis le verrouillage d'écran automatique à 5 min) : c'est le comportement de
  Plasma au premier démarrage, pas propre à NexOS (séries minute par minute dans les fichiers `.txt`).

### Ce que les optimisations de NexOS ont réellement apporté (même banc, NexOS seul)
| Changement | Effet mesuré |
|---|---|
| Attente réseau au démarrage désactivée (0.2 → 0.3) | partie système 134 s → 66 s (mesure 0.2 faite avec l'ancien banc ; ordre de grandeur seulement) |
| firewalld → ufw | firewalld : 19,6 s sur le chemin critique + démon résident ≈46 Mo ; ufw : aucun démon |
| Clavier console et cache des bibliothèques préparés à la construction | console-setup (≈36 s) et ldconfig (≈25 s) n'apparaissent plus dans les durées du premier démarrage |
| Notificateur Discover résident remplacé par un minuteur quotidien | processus de ≈140 Mo absent de la liste au repos |
| Indexation de fichiers (Baloo) désactivée par défaut | aucun indexeur au repos |

## Kubuntu 24.04 et Ubuntu 24.04 (références minimales)

| Médiane de 3 mesures (min–max) | NexOS 0.3 | Debian 13 KDE | Kubuntu 24.04 | Ubuntu 24.04 |
|---|---|---|---|---|
| Bureau | Plasma 6, Wayland | Plasma 6, Wayland | Plasma 5.27, X11 | GNOME 46, Wayland |
| Mémoire au repos | 1 074 (1 070–1 089) Mio | 964 (956–968) Mio | 758 (743–767) Mio | 649 (638–650) Mio |
| Démarrage, partie système | 57 (54–57) s | 37 (33–40) s | 56 (55–59) s | 48 (44–50) s |

Graphiques générés à partir des fichiers bruts : `tools/make_comparison_charts.py` → `docs/assets/`.

**Important : ces trois références ont été construites SANS leurs paquets recommandés** (mmdebstrap ne les
installe pas par défaut). Exemple : la référence Kubuntu n'avait même pas le gestionnaire de fichiers.
Elles sont donc plus légères qu'une installation réelle (pas de notificateur de mises à jour, de
KDE Connect, d'application de bienvenue, de serveur de courrier…). Les listes de paquets sont jointes.

### Tentative avec installations complètes (paquets recommandés) — non comparable
`references-completes-non-comparables/` : Debian 13 KDE complète (2 142 paquets) et Kubuntu complète
(1 988 paquets) mesurées 3 fois. **Résultats écartés** : sur ces systèmes plus lents à s'afficher, la
mesure est tombée après la mise en veille de l'écran et le verrouillage automatique (captures « Display
output is not active »), avec en plus l'application de bienvenue du premier démarrage et la compilation
initiale des profils AppArmor (2 min). À refaire au **deuxième** démarrage avec la veille désactivée
pour tous les systèmes. Noter aussi : l'image NexOS 0.3 ne contient **pas AppArmor** (oubli à corriger),
ce qui l'avantage au démarrage par rapport à ces installations complètes.

## Windows, Fedora
**Non mesurés.** Téléchargement des images impossible depuis l'environnement de construction ; Windows 11
exigerait en plus une puce TPM virtuelle et des heures d'installation en émulation. Pour comparer sur
un vrai PC : `tests/perf/real-hw/collect-windows.ps1` (non testé, pas de Windows disponible) et
`collect-linux.sh`, mêmes grandeurs.

## Mesures invalidées (et pourquoi)
1. **Toutes les mesures avec le processeur virtuel « max »** : le pilote graphique logiciel (llvmpipe)
   y génère des instructions AVX mal émulées et **plante** (SIGSEGV dans son code JIT, pile capturée
   avec gdb) ; le shell de bureau redémarrait en boucle. Artefact du banc, pas un défaut de NexOS
   (disparaît avec « Nehalem »). Les chiffres « NexOS 850 Mio < Debian 922 Mio » et ceux de
   Kubuntu/Ubuntu donnés auparavant sont retirés.
2. **Mesures prises 90 s après le lancement du shell** (et non après son affichage) : sous émulation,
   l'écran restait noir à ce moment ; valeurs prises pendant le chargement, non comparables.
