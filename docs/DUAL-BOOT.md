# Installer NexOS à côté de Windows 11 (double démarrage)

Testé en machine virtuelle (UEFI, **Secure Boot activé** avec les clés Microsoft, disque avec une
partition Windows NTFS et sa partition EFI) — **pas encore sur un vrai PC**. Lisez tout avant de commencer.

## 1. Sous Windows, avant de toucher à quoi que ce soit
1. **Sauvegardez vos fichiers importants** (disque externe ou cloud). Le redimensionnement de Windows
   est fiable, mais on ne le fait jamais sans sauvegarde.
2. **BitLocker / chiffrement de l'appareil** : Paramètres → Confidentialité et sécurité → Chiffrement de
   l'appareil (ou « Gérer BitLocker »).
   - Notez votre **clé de récupération** : https://aka.ms/myrecoverykey (compte Microsoft).
   - Si BitLocker est **activé** : NexOS ne peut pas réduire une partition chiffrée. Faites la place
     depuis Windows (étape 3) puis choisissez « Partitionnement manuel » (§ 3, variante B).
3. **Faire de la place (recommandé dans tous les cas)** : clic droit sur Démarrer → Gestion du disque →
   clic droit sur C: → **Réduire le volume** → au moins **60 Go** (100 Go si vous jouez).
4. **Désactiver le démarrage rapide** : Panneau de configuration → Options d'alimentation → Choisir
   l'action des boutons → décocher « Activer le démarrage rapide ». (Sinon Windows garde le disque
   « verrouillé » et l'heure peut se dérégler.)
5. **Secure Boot : laissez-le ACTIVÉ.** La clé NexOS 0.4 démarre avec Secure Boot (chargeur signé
   Debian/Microsoft). Le désactiver sur un PC avec BitLocker ferait demander la clé de récupération.

## 2. Créer la clé USB et démarrer dessus
- Rufus (Windows) : sélectionner l'ISO, schéma **GPT**, cible **UEFI**, mode **« Image DD »** si demandé.
- Redémarrer en maintenant la touche du menu de démarrage (souvent **F12**, F11, F8 ou Échap selon la
  marque) → choisir la clé USB (« UEFI: … »).
- Menu NexOS → « Essayer ou installer NexOS ». Testez Wi-Fi, son, clavier dans la session live.

## 3. Installer
Double-cliquez sur **Installer NexOS** sur le bureau, puis à l'étape **Partitions** :

**A. Cas normal (Windows sans BitLocker)** → **« Installer à côté »** → cliquez sur la partition Windows
(la plus grande, NTFS) → faites glisser la barre « Après » pour choisir la taille de NexOS.
L'installateur réutilise la partition EFI de Windows **sans la formater**. Vérifiez au résumé :
« Redimensionner /dev/… », « Configurer la partition fat32 … /boot/efi » (et **pas** « Formater »).

**B. Si vous avez fait la place depuis Windows (BitLocker)** → **« Partitionnement manuel »** :
- sélectionnez l'**espace libre** → Créer → système de fichiers **btrfs**, point de montage **/** ;
- sélectionnez la petite partition **FAT32 (EFI)** de Windows → Modifier → point de montage **/boot/efi**,
  **ne cochez pas « Formater »**.

**Ne choisissez jamais « Effacer le disque »** : cela supprime Windows. Aucune option n'est cochée par
défaut pour éviter ce piège.

## 4. Après l'installation
- Au redémarrage, le **menu NexOS** propose **NexOS** et **Windows Boot Manager**. Si le PC démarre
  directement sur Windows : réglages du BIOS/UEFI → ordre de démarrage → placer « NexOS » en premier.
- Windows et NexOS gardent la **même heure** (NexOS règle l'horloge en heure locale quand il trouve Windows).
- Carte NVIDIA : Control Center → **Jeux et pilotes** → « Installer le pilote NVIDIA », puis
  « Valider la clé Secure Boot » ; au redémarrage, écran bleu **MOK management** → *Enroll MOK* →
  *Continue* → *Yes* → mot de passe choisi → *Reboot*.

## En cas de problème
- **Windows ne démarre plus / demande la clé BitLocker** : entrez la clé de récupération notée à
  l'étape 1 ; Windows reprend normalement.
- **Le menu NexOS n'apparaît pas** : menu de démarrage du PC (F12…) → « NexOS ».
- **Revenir en arrière** : depuis Windows, Gestion du disque → supprimer les partitions NexOS → étendre
  C: ; puis réparer le démarrage avec `bcdboot C:\Windows` (invite de commandes administrateur).
