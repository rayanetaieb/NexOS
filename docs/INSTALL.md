# Installer NexOS (phase 6)

## Construire l'ISO
```bash
make keyring                                   # hôte non-Debian uniquement (trousseau vérifié)
OUT=$PWD/out/live ./build/build-llama.sh       # moteur IA portable (LLAMA_SRC=clone llama.cpp)
OUT=$PWD/out ./build/fetch-uv.sh               # uv officiel pour le Centre Python
make rootfs EDITION=live OUT=$PWD/out/live
OUT=$PWD/out/live ./build/make-iso.sh          # → out/live/nexos-0.2-amd64.iso (+ .sha256)
```

## Essayer dans VirtualBox (Windows, macOS, Linux)
1. Nouvelle machine : type *Linux*, version *Debian (64-bit)*, **4 Go de RAM** minimum
   (8 Go recommandés pour l'assistant IA 1,5B), 2 processeurs ou plus, disque **25 Go**.
2. Affichage : contrôleur **VMSVGA**, 128 Mo de mémoire vidéo.
3. Système → Carte mère : cocher *Activer EFI* (recommandé) ; l'ISO démarre aussi en BIOS.
4. Stockage : insérer `nexos-0.2-amd64.iso` dans le lecteur optique, démarrer.
5. Menu de démarrage → « Essayer ou installer NexOS ». Le bureau live s'ouvre
   (compte de démonstration, mot de passe `nexos`).
6. Double-cliquer « Installer NexOS » sur le bureau et suivre l'installateur :
   langue, clavier, disque (effacement ; Btrfs par défaut), compte utilisateur.
7. Redémarrer, retirer l'ISO, se connecter avec le compte créé.

Secure Boot : à désactiver pour démarrer l'ISO (chargeur non signé dans ce prototype).
Le système installé utilise le shim et GRUB signés de Debian.

## Ce que fait l'installateur (Calamares, configuration `build/config/overlay-live`)
- Copie du système depuis le squashfs du support, génération de `fstab` et de l'identifiant machine.
- Btrfs avec sous-volumes `@`, `@home`, `@snapshots`, `@log` (compression zstd), ou ext4.
- Suppression du compte de démonstration, création du compte choisi (groupe sudo).
- Installation de GRUB **hors ligne** (UEFI ou BIOS) depuis des paquets embarqués.
- Retrait de l'auto-connexion, des règles et outils propres au live (live-boot, Calamares).
- Régénération de l'initramfs.

## Vérification réelle (17/10/2026, QEMU UEFI, émulation logicielle)
`tests/install/run_install.sh out/live/nexos-0.2-amd64.iso` puis redémarrage sur le disque seul.
Captures : `docs/screenshots/v0.2-installer/`.

| Étape | Résultat |
|---|---|
| Démarrage de l'ISO (UEFI) jusqu'au bureau live | ✅ Plasma Wayland, 0 unité en échec |
| Installateur (langue, Europe/Paris, AZERTY, Btrfs sur disque entier, compte) | ✅ « Installation terminée » |
| Redémarrage sur le disque installé | ✅ GRUB UEFI installé hors ligne, écran de connexion NexOS |
| Connexion avec le compte créé | ✅ bureau NexOS |
| Contrôles dans le système installé | ✅ racine Btrfs `@` ; 5 entrées de sous-volumes dans fstab ; live-boot et calamares retirés ; compte de démo absent ; auto-connexion retirée ; assistant, Centre Python, llama, uv présents ; 0 unité en échec ; 711 Mio utilisés après ouverture de session |

Défauts trouvés par ces essais et corrigés : dictionnaire de mots de passe absent
(cracklib), `unsquashfs` absent (échec de copie), `mkfs.ext4` absent, fuseau New York par
défaut, logos illisibles, verrouillage de l'écran live pendant l'installation.

Non vérifié à ce jour : installation en mode BIOS, chiffrement LUKS, option ext4,
VirtualBox et matériel réel, Secure Boot.
