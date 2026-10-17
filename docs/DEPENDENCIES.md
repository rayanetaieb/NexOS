# Technologies et dépendances

Licences à confirmer par l'inventaire automatique (SBOM) avant toute redistribution.

## Système (image NexOS)
| Composant | Choix | Licence | Rôle |
|---|---|---|---|
| Base | Debian 13 trixie | DFSG (diverses) | paquets, sécurité |
| Noyau | linux-image-amd64 (6.12 LTS), backports en option | GPL-2.0 | matériel |
| Démarrage | shim-signed, GRUB 2 | BSD / GPL-3.0 | UEFI + Secure Boot, BIOS |
| Init | systemd (+ oomd, journald, timers) | LGPL-2.1 | services, journaux |
| FS | Btrfs + snapper + grub-btrfs | GPL | instantanés, retour arrière |
| Mémoire | zram-tools | GPL | swap compressé |
| Paquets | APT/dpkg + dépôt NexOS (aptly), Flatpak | GPL / LGPL | logiciels |
| Bureau | KDE Plasma 6 (Wayland), Dolphin, Discover, KRunner, Konsole | GPL/LGPL | interface |
| Réseau / son / BT | NetworkManager, PipeWire, BlueZ | GPL/MIT/LGPL | matériel |
| Sécurité | AppArmor, ufw, bubblewrap, polkit | GPL/LGPL | isolation |
| Firmware | firmware-linux-nonfree, fwupd | variées (non libres) | Wi-Fi, GPU |
| Installateur | Calamares | GPL-3.0 | installation |
| Build ISO | live-build (phase 6), mmdebstrap (prototype) | GPL | images |

## Python
| Composant | Rôle |
|---|---|
| python3 (Debian, système, protégé PEP 668) | outils de l'OS uniquement |
| uv (MIT/Apache-2.0) | interpréteurs, venvs, verrous `uv.lock` |
| Profils verrouillés | core, science, ai-cpu, ai-cuda, vision, electronics, appdev (bibliothèques listées dans la mission ; versions fixées par la CI de compatibilité) |
| PySide6 (LGPL-3.0) | interfaces NexOS (Centre Python, nexai) |

## Assistant IA
| Composant | Licence | Rôle |
|---|---|---|
| llama.cpp / ggml (`llama-server`) | MIT | inférence GGUF CPU |
| Modèle GGUF (à choisir) | Apache-2.0 privilégiée | poids, téléchargés à la demande |
| nexai | Apache-2.0 (proposée) | assistant |

## Outillage de développement
git, mmdebstrap, qemu-system-x86, qemu-utils, e2fsprogs, xorriso, squashfs-tools,
cmake, build-essential, pytest, ruff, mypy.
