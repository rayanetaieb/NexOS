# Récupération et retour arrière — NexOS 0.3

Ce document décrit ce qui est **en place dans l'image** et comment s'en servir. Les points
marqués « vérifié » ont été exécutés ; les autres sont décrits mais pas encore testés en VM.

## 1. Ce que l'installateur met en place

| Élément | Réglage | État |
|---|---|---|
| Système de fichiers | Btrfs, sous-volumes `@` (/), `@home`, `@snapshots` (/.snapshots), `@log` (/var/log), compression zstd | vérifié (installation UEFI, v0.2) |
| Snapper | configuration `root` créée par `nexos-cleanup` ; 10 instantanés « number » au plus (5 importants), 30 % d'espace au plus | ajouté en 0.3, à vérifier en VM |
| Instantanés automatiques | **avant et après chaque opération APT** (crochet `80snapper` du paquet Debian) ; un instantané « Installation de NexOS » | ajouté en 0.3 |
| Instantanés horaires / à chaque démarrage | **désactivés** (`snapper-timeline.timer`, `snapper-boot.timer`) : coût disque et E/S sans bénéfice pour un poste de travail | contrôlé par `build/check-autostart.sh` |
| Nettoyage | `snapper-cleanup.timer` (1×/jour) | |
| Menu GRUB | entrée « mode de récupération » conservée (`GRUB_DISABLE_RECOVERY=false`), délai 3 s | |

`/home` est un sous-volume séparé : **un retour arrière du système ne touche jamais aux documents**.

## 2. Annuler une mise à jour ou une installation qui pose problème

### Depuis le Control Center (recommandé)
1. Control Center → **Sauvegardes et récupération** → « Lister les instantanés ».
2. Repérer la paire `pre`/`post` de l'opération APT fautive (description `apt`), ou un instantané manuel.
3. « Revenir à un instantané… » → saisir le numéro → confirmer.
   NexOS crée d'abord un instantané de l'état actuel (pour pouvoir annuler l'annulation),
   puis exécute `snapper -c root undochange N..0` : les fichiers système modifiés depuis N
   reprennent leur état d'alors.
4. Redémarrer.

### En ligne de commande (équivalent)
```bash
sudo snapper -c root list
sudo snapper -c root create -d "avant retour arrière" --userdata important=yes
sudo snapper -c root undochange 42..0      # 42 = numéro choisi
sudo reboot
```

### Restauration complète du sous-volume racine
Si le système démarre mais est trop abîmé pour `undochange` : **Btrfs Assistant**
(Control Center → Sauvegardes → « Btrfs Assistant ») → onglet *Snapper* → *Browse/Restore* →
choisir l'instantané → *Restore*. L'outil remplace le sous-volume `@` par une copie de
l'instantané (l'ancien est conservé) ; redémarrer ensuite.

## 3. Le système ne démarre plus

1. **Mode de récupération** : au menu GRUB (touche Échap pendant les 3 s si le menu est masqué),
   « Options avancées » → entrée *recovery mode* → shell root.
   - Réparer les paquets : `dpkg --configure -a && apt-get -f install`
   - Revenir en arrière : `snapper -c root undochange N..0` (voir §2).
2. **Clé USB NexOS** → « NexOS (console de diagnostic, sans bureau) » ou session live, puis :
   ```bash
   sudo cryptsetup open /dev/nvme0n1p2 nexos      # seulement si le disque est chiffré (LUKS)
   sudo mount -o subvolid=5 /dev/mapper/nexos /mnt   # ou /dev/nvme0n1p2 sans chiffrement
   ls /mnt/@snapshots/                             # instantanés : /mnt/@snapshots/N/snapshot
   sudo mv /mnt/@ /mnt/@.casse
   sudo btrfs subvolume snapshot /mnt/@snapshots/N/snapshot /mnt/@
   sudo reboot
   ```
   (adapter les noms de partitions avec `lsblk -f`).
3. **Chargeur de démarrage endommagé** : depuis la session live, monter le système dans `/mnt`
   (sous-volume `@`, puis `/mnt/boot/efi`), `for d in dev proc sys run; do sudo mount --rbind /$d /mnt/$d; done`,
   `sudo chroot /mnt grub-install && sudo chroot /mnt update-grub`.

## 4. Journaux utiles
- `journalctl -b -1 -p err` : erreurs du démarrage précédent.
- `journalctl -t nexos-admin` : actions administrateur faites depuis le Control Center.
- `/var/log` est un sous-volume séparé : les journaux survivent à un retour arrière.

## 5. Limites connues
- Les instantanés ne sont **pas** des sauvegardes : ils sont sur le même disque. Pour les documents,
  utiliser une copie externe (Déjà Dup / rsync vers un disque USB — non intégré au Control Center à ce jour).
- Pas d'entrées d'instantanés dans le menu GRUB (`grub-btrfs` n'est pas empaqueté dans Debian 13).
- Installation en ext4 (si l'utilisateur la choisit) : pas d'instantanés.
