# NexOS — Architecture technique (v0.1, phase 1)

Statut de ce document : **décisions de conception**. Rien ici n'est mesuré sauf
mention explicite « mesuré » avec renvoi vers `docs/MEASUREMENTS.md`.

## 1. Options étudiées

| Option | Avantages | Inconvénients | Verdict |
|---|---|---|---|
| A. Distribution dérivée d'une base éprouvée (Debian) | Pilotes, sécurité, 60 000+ paquets, noyau signé Secure Boot, outillage de build mature | Identité à construire au-dessus | **Retenue pour le prototype** |
| B. Linux From Scratch / sources complètes | Contrôle total | Des années-homme pour la maintenance sécurité, pas de Secure Boot sans infrastructure de signature, compatibilité logicielle à reconstruire | Rejetée (coût ≫ valeur) |
| C. Distribution indépendante + dépôt propre dès le départ | Identité forte | Mêmes coûts que B pour la base | Évolution **progressive** de A : dépôt NexOS qui *surcouche* Debian |
| D. Composants système spécifiques (long terme) | Différenciation | À réserver aux éléments qui apportent une valeur mesurée | Ciblés : shell de bureau, centre Python, assistant IA, outils de mise à jour |

Principe : on ne réécrit pas ce qui marche (noyau, init, pile graphique, gestion
de paquets). L'effort va vers l'intégration, l'UX, l'environnement Python, les
outils NexOS et la qualité mesurée.

## 2. Choix de la base : Debian 13 « trixie » (stable)

- Base stable, cycle long, mises à jour de sécurité, licences claires (DFSG).
- Noyau Debian **6.12 LTS** signé via `shim` → Secure Boot fonctionne sans
  infrastructure de signature propre. Un noyau NexOS personnalisé ferait perdre
  cet avantage : on ne le fera qu'avec un bénéfice mesuré.
- Firmware non libre disponible dans la section `non-free-firmware` (Wi-Fi,
  GPU) : nécessaire pour la compatibilité portable.
- Ubuntu LTS est l'alternative crédible (pilotes NVIDIA plus simples, noyaux HWE
  plus récents) ; Debian est préféré pour l'absence de snap imposé et la
  gouvernance. **Risque connu :** matériel très récent → prévoir le noyau
  `trixie-backports` comme option.

## 3. Couches du système

```
┌────────────────────────────────────────────────────────────────────┐
│ Applications NexOS : Centre Python, Assistant IA (nexai),          │
│ Centre de mises à jour, Moniteur système, Gestionnaire d'apps      │
├────────────────────────────────────────────────────────────────────┤
│ Bureau : KDE Plasma 6 (Wayland) + thème/disposition NexOS          │
│ (alternative mesurée : LXQt 2, édition « Lite »)                    │
├────────────────────────────────────────────────────────────────────┤
│ Apps : APT (dépôt NexOS signé + Debian) · Flatpak (isolées)        │
├────────────────────────────────────────────────────────────────────┤
│ Services : systemd, NetworkManager, PipeWire, BlueZ, firewalld,    │
│ AppArmor, snapper (instantanés Btrfs), fwupd                       │
├────────────────────────────────────────────────────────────────────┤
│ Système de fichiers : Btrfs (sous-volumes @, @home, @snapshots)    │
├────────────────────────────────────────────────────────────────────┤
│ Noyau Debian 6.12 LTS signé · shim · GRUB · firmware               │
└────────────────────────────────────────────────────────────────────┘
```

### 3.1 Noyau et configuration
Noyau Debian `linux-image-amd64` (6.12 LTS). Réglages via `sysctl` et ligne de
commande, pas de recompilation : `zram` (swap compressé, `zram-tools`),
`vm.swappiness` ajusté *après mesure*, `systemd-oomd` actif pour la gestion
sous forte charge. Option `trixie-backports` pour le matériel récent.

### 3.2 Init et services
`systemd` : standard de fait, `systemd-analyze` pour mesurer le démarrage,
cgroups v2 (isolation, limites mémoire par service), timers. La liste des
services activés est versionnée (`build/config/services.list`) et testée :
tout service ajouté doit être justifié.

### 3.3 Système de fichiers
**Btrfs** + `snapper` : instantané automatique avant chaque mise à jour APT,
entrées GRUB pour démarrer un instantané (`grub-btrfs`). Compression `zstd:1`.
ext4 reste proposé à l'installation pour qui préfère la simplicité (sans retour
arrière par instantané).

### 3.4 Paquets
- **APT/dpkg** pour le système, avec un **dépôt NexOS** (aptly ou reprepro)
  signé par une clé GPG NexOS, épinglé (APT pinning) au-dessus de Debian. Les
  paquets NexOS sont des `.deb` construits en CI.
- **Flatpak** (Flathub optionnel, activable à l'installation) pour les
  applications de bureau isolées.
- Gestionnaire graphique : KDE Discover (backends APT + Flatpak), personnalisé.

### 3.5 Bureau
**KDE Plasma 6 sous Wayland** pour le prototype, parce qu'il fournit déjà :
barre des tâches, menu, notifications, KRunner (recherche apps/fichiers/
paramètres), paramètres centralisés, Dolphin, Discover, mode clair/sombre,
raccourcis familiers (Meta, Alt+Tab, Meta+E…), et qu'il est Qt — cohérent avec
PySide6 pour nos outils.

Identité NexOS (contrainte : ressemblance visuelle minimale avec Windows) :
dock flottant centré-gauche + panneau supérieur fin, lanceur plein écran par
catégories, palette, icônes et typographie propres. On garde *les gestes*
familiers (raccourcis, clic droit, glisser-déposer), pas l'apparence.

**Risque RAM :** Plasma consomme plus que LXQt/XFCE. Décision **conditionnée à
la mesure** (phase 5) : si l'écart sur le même matériel est jugé inacceptable
pour la cible « PC modestes », une édition NexOS Lite (LXQt 2) sera maintenue.

### 3.6 Mises à jour et récupération
1. Le Centre de mises à jour lit le dépôt signé (APT vérifie `InRelease`).
2. Instantané Btrfs pré-mise à jour (snapper, hook APT).
3. Mise à jour ; en cas d'échec ou de non-démarrage → entrée GRUB
   « Démarrer l'instantané précédent » puis `snapper rollback`.
4. Image ISO = support de récupération (mode live + outils).

### 3.7 Sécurité et isolation
AppArmor (actif par défaut Debian), firewalld + module graphique (entrant
refusé par défaut), Flatpak/bubblewrap pour les applis, `sudo` avec mot de
passe, comptes non-root, Secure Boot via shim, mises à jour signées, journaux
`journald` consultables graphiquement. Pas de télémétrie. SBOM et inventaire
des licences générés à chaque build (`build/licenses/`).

### 3.8 Matériel et pilotes
Firmware `non-free-firmware`, `fwupd`, Mesa (Intel/AMD), pilotes NVIDIA
propriétaires *optionnels* proposés après détection (`nexos-hwdetect`), jamais
installés sans accord. Détection : `/proc/cpuinfo`, `lspci`, `lsusb`,
`/sys/class/drm`, et pour le GPU un **test d'exécution réel** avant d'annoncer
une accélération.

### 3.9 Image installable
- Prototype (phase 2) : `mmdebstrap` → rootfs → image disque → test QEMU
  automatisé. Simple, reproductible, sans root sur l'hôte grâce au mode
  `unshare`.
- Phase 6 : ISO hybride BIOS/UEFI via **live-build** (outil officiel Debian),
  installateur **Calamares**.

## 4. Environnement Python

- **Python système** (Debian, 3.13) protégé par PEP 668 : réservé à l'OS.
- **uv** (Astral, MIT/Apache-2.0) : installe des interpréteurs isolés,
  environnements virtuels et **fichiers de verrouillage** (`uv.lock`).
- Profils = projets uv versionnés dans `python/profiles/<nom>/` :
  `core`, `science`, `ai-cpu`, `ai-cuda`, `vision`, `electronics`, `appdev`.
  La version Python de chaque profil est fixée par ce qui passe la suite de
  tests de compatibilité, pas par la plus récente.
- Centre Python (PySide6) : recherche, installation, mise à jour,
  suppression, affichage de l'arbre de dépendances (`uv tree`) et des erreurs.
- Les gros profils (PyTorch, TensorFlow, CUDA) sont **facultatifs** et
  téléchargés à la demande.

## 5. Assistant IA local (nexai)

Voir `docs/AI_ASSISTANT.md`. Résumé : interface séparée du moteur ;
moteur = processus `llama-server` (llama.cpp) lancé **à la demande** et tué
après inactivité ; aucun processus IA au démarrage ; aucune connexion réseau
en usage normal.

## 6. Ce qui sera développé par NexOS (valeur propre)

| Composant | Langage | Justification |
|---|---|---|
| nexai (assistant) | Python + PySide6 | Exigence produit |
| Centre Python | Python + PySide6 | Différenciation principale |
| nexos-hwdetect | Python | Suggestions matériel/pilotes vérifiées |
| Thème/disposition Plasma | QML/config | Identité visuelle |
| Hooks de mise à jour + snapshots | Shell/Python | Fiabilité |
| Outillage build/test/bench | Shell/Python | Reproductibilité |
