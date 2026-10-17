# Matrice de compatibilité matérielle — NexOS 0.3

**Important** : tous les essais de NexOS ont été faits en **machine virtuelle QEMU** (sans KVM).
Aucun PC physique n'a été testé à ce jour. La colonne « Vérifié » ne contient que ce qui a été
réellement exécuté ; le reste découle du noyau et des firmwares Debian 13 inclus et doit être confirmé
sur matériel (rapports bienvenus : `journalctl -b`, `lspci -nnk`, `lsusb`).

Base : Debian 13 « trixie », noyau `linux-image-amd64` (6.12 LTS), Mesa, PipeWire, BlueZ.

| Domaine | Pris en charge par | Vérifié | Remarques |
|---|---|---|---|
| Processeurs x86-64 Intel / AMD | noyau 6.12, `intel-microcode`, `amd64-microcode` | QEMU `-cpu max`, 4 cœurs | ARM non pris en charge (image amd64 seulement) |
| Micrologiciel UEFI | GRUB EFI, shim signé Debian (système installé) | OVMF : démarrage ISO + installation complète + redémarrage | ISO : chargeur non signé → Secure Boot à désactiver pour l'ISO |
| BIOS hérité (CSM) | grub-pc | démarrage de l'ISO en BIOS : non re-testé en 0.3 | installation BIOS non testée |
| Disques SATA / NVMe / virtio | noyau | virtio uniquement | Btrfs par défaut, LUKS proposé (non testé) |
| Graphique Intel (i915/xe) | Mesa `iris`, noyau | non | |
| Graphique AMD (amdgpu) | Mesa `radeonsi`, `firmware-amd-graphics` | non | |
| Graphique NVIDIA | `nouveau` (libre) | non | pilote propriétaire non inclus (voir Limites) |
| Affichage virtuel | `virtio-gpu`, `bochs`/std VGA, VMSVGA | std VGA + virtio-vga en QEMU | VirtualBox : non testé |
| Wi-Fi Intel | `firmware-iwlwifi` | non | |
| Wi-Fi/Ethernet Realtek, Atheros | `firmware-realtek`, `firmware-atheros` | Ethernet virtio en QEMU | |
| Bluetooth | BlueZ, `bluetooth.service` | service démarré ; aucun adaptateur en VM | appairage non testé |
| Son | PipeWire + WirePlumber, `firmware-sof-signed`, `firmware-intel-sound` | non (pas de carte son émulée) | |
| Imprimantes | CUPS (socket : démarre à la 1re impression), `printer-driver-cups-pdf`, gestionnaire d'impression KDE | impression PDF virtuelle : non re-testée | pilotes propriétaires non inclus |
| Webcam | UVC (noyau), Kamoso | non | |
| Cartes Arduino / ESP32 | `cdc_acm`, `ch341`, `cp210x`, `ftdi_sio` (noyau), groupe `dialout` | compilation seulement (aucune carte branchée) | diagnostic USB dans le Centre Arduino |
| Téléphones Android (adb) | `adb`, règles udev `51-android` | `adb version` | |
| Virtualisation (émulateur Android) | KVM (`kvm-ok` via cpu-checker) | non : pas de KVM dans l'environnement de test | |
| Gestion d'énergie portable | `power-profiles-daemon` | service actif en VM | autonomie non mesurée |
| Mémoire | `zram-tools` (swap compressé en RAM), `systemd-oomd` | actifs en VM | |

## Configuration recommandée
| | Minimum mesuré | Recommandé |
|---|---|---|
| Mémoire | 4 Go (bureau + applications courantes, voir MEASUREMENTS.md) | 8 Go (assistant IA 1,5B, Android Studio) |
| Disque | 25 Go | 64 Go et plus (SDK Android, TeX Live, profils Python IA ≈ 8 Go) |
| Processeur | x86-64-v1 | 4 cœurs ou plus |

## Limites connues
- Pas de pilote NVIDIA propriétaire préinstallé : à ajouter depuis les dépôts Debian
  (`nvidia-driver`, section non-free) — à intégrer au Control Center (prévu).
- Puces Wi-Fi Broadcom (`broadcom-sta`) non incluses.
- Aucun test sur matériel réel : c'est la prochaine étape de validation.
