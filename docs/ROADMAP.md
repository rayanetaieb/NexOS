# NexOS — Plan de développement, critères et risques

Légende de statut : ✅ fait et vérifié · 🟡 prototype · ⬜ planifié.

## Phases

| Phase | Livrables | Critères de réussite mesurables | Statut |
|---|---|---|---|
| 1. Étude | `ARCHITECTURE.md`, ce plan, arborescence | Décisions écrites et argumentées | ✅ |
| 2. Prototype démarrable | `build/build-rootfs.sh`, `build/make-disk.sh`, `tests/boot/test-boot.sh` | L'image démarre dans QEMU **sans intervention**, atteint `multi-user.target`, le test lit `NEXOS-BOOT-OK` sur la console série ; build reproductible par une seule commande | ✅ Debian 13 vérifié (`MEASUREMENTS.md`) |
| 3. Bureau | Plasma 6 Wayland + thème NexOS, Dolphin, Discover | Session graphique ouverte en < 30 s après login sur VM 4 Go ; 0 erreur critique `journalctl -p 3` ; checklist UX (12 tâches courantes sans terminal) | 🟡 session Wayland + 4 scénarios vérifiés en VM émulée (`DESKTOP.md`) ; temps < 30 s, journal et checklist UX : à mesurer avec KVM/matériel réel |
| 4. Python | Profils uv verrouillés, Centre Python | 100 % des tests d'import/fonction de chaque profil passent en CI ; installation profil `science` hors-ligne depuis cache | 🟡 6/6 profils installés et testés (24/24 tests), Centre 11/11 ; CI et installation hors ligne : à faire ; variante PyTorch CPU : à faire |
| 5. Optimisation | Protocole de bench, comparaisons | Résultats publiés vs Debian+Plasma et Windows 11 sur même matériel ; aucune optimisation sans gain mesuré > bruit (≥ 3 répétitions) | ⬜ |
| 6. Installation/MAJ | ISO live-build, Calamares, dépôt signé, snapshots | Installation UEFI+BIOS en VM ; MAJ signée ; rollback testé automatiquement après MAJ volontairement cassée | 🟡 ISO hybride + installation UEFI complète vérifiées en VM (`INSTALL.md`) ; BIOS, mises à jour signées, snapper/rollback : à faire |
| 7. Matériel | Matrice de compatibilité | ≥ 5 PC réels testés : Wi-Fi, BT, audio, GPU, veille/reprise | ⬜ |
| 8. Bêta | Docs, suivi des bugs, procédure de retour arrière | Testeurs externes, taux de crash suivi | ⬜ |
| 12. Assistant IA | `packages/nexai` | RAM résiduelle mesurée ≈ 0 hors utilisation (aucun processus), déchargement vérifié, 1 requête simultanée, aucun accès réseau | 🟡 vrais modèles évalués (Qwen2.5-1.5B 20/24), moteur portable intégré à l'image ; mesure au calme et PC réel : à faire |

## Risques principaux

| Risque | Impact | Mitigation |
|---|---|---|
| Ampleur du projet (OS complet) | Élevé | Base Debian, développement concentré sur les composants différenciants |
| RAM de Plasma vs objectif « faible mémoire » | Moyen | Mesure phase 5, édition Lite LXQt si nécessaire |
| Pilotes NVIDIA / Secure Boot | Moyen | Pilote optionnel, signature DKMS (MOK), Mesa par défaut |
| Conflits de dépendances Python (TF vs PyTorch, CUDA) | Élevé | Profils séparés, verrous, CI de compatibilité |
| Licences de redistribution (firmware, modèles IA, CUDA) | Élevé | SBOM, revue licence avant inclusion, CUDA/poids IA téléchargés par l'utilisateur |
| Matériel récent non supporté par noyau 6.12 | Moyen | Option backports |
| Sécurité du dépôt (clé de signature) | Élevé | Clé hors-ligne, sous-clé de signature, rotation documentée |
| Maintenance à long terme (une petite équipe) | Élevé | Suivre Debian au plus près, peu de patchs locaux |
