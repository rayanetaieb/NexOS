# NexOS (nom de travail)

Système d'exploitation pour PC basé sur Debian : bureau accessible, environnement
Python intégré, outils pour le développement, l'électronique, la vision et l'IA,
et contrôle complet par son propriétaire.

**État : phase 2 (prototype démarrable en VM) + prototype de l'assistant IA local.**
Ce n'est pas encore un système de bureau installable.

| Élément | Statut | Où |
|---|---|---|
| Architecture, choix, plan, risques | ✅ rédigé | `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` |
| Rootfs minimal + image + test de démarrage QEMU automatisé | ✅ opérationnel, testé | `build/`, `tests/boot/` |
| Assistant IA `nexai` (moteur à la demande, déchargement, garde RAM, CLI) | 🟡 prototype testé (tests automatisés + mesures réelles avec modèle proxy) | `packages/nexai/`, `docs/AI_ASSISTANT.md` |
| Fenêtre graphique de l'assistant | 🟡 écrite, **non testée visuellement** | `packages/nexai/nexai/gui.py` |
| Bureau Plasma, Centre Python, ISO installable, mises à jour | ⬜ planifié | `docs/ROADMAP.md` |

Démarrage rapide : `docs/DEV_SETUP.md`. Mesures réelles : `docs/MEASUREMENTS.md`.

## Arborescence
```
nexos/
├── Makefile                  # points d'entrée : rootfs, disk, boot-test, vm, test-nexai
├── build/
│   ├── build-rootfs.sh       # mmdebstrap → out/rootfs.tar
│   ├── make-disk.sh          # → out/nexos.img + vmlinuz + initrd
│   └── config/
│       ├── packages-base.list
│       ├── services.list     # services activés explicitement
│       └── overlay/          # fichiers copiés dans l'image
├── tests/boot/test-boot.sh   # test de démarrage automatisé (QEMU)
├── packages/nexai/           # assistant IA local (Python, stdlib + PySide6 optionnel)
├── tools/                    # outils de développement (ex. modèle proxy de mesure)
└── docs/                     # architecture, plan, mesures, procédures
# prévus : packages/nexos-python-center, packages/nexos-hwdetect, python/profiles/,
#          theme/, live-build/ (ISO), repo/ (dépôt APT signé)
```
