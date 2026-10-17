# Bureau NexOS (phase 3)

Base : **KDE Plasma 6.3.6 sous Wayland** (Debian 13), personnalisé par configuration
(aucun composant KDE recompilé ou modifié).

## Identité visuelle
Dérivée du logo fourni (hexagone, tracé « pouls », point bleu) — `branding/` :

| Élément | Fichier | Remarque |
|---|---|---|
| Logo vectoriel | `branding/nexos-logo.svg`, `nexos-mark*.svg` | redessiné à partir des coordonnées mesurées sur l'image fournie ; couleurs extraites : bleu `#01AFF2`, anthracite `#252121` |
| Fonds d'écran clair/sombre | `branding/make_wallpapers.py` → `/usr/share/wallpapers/NexOS` | paquet Plasma avec variantes `images` / `images_dark` |
| Icônes | menu (`nexos-start`), Assistant, Centre Python | lisibles sur fond clair et sombre |
| Thèmes globaux | `org.nexos.desktop.dark` (défaut), `org.nexos.desktop.light` | Breeze + accent `#01AFF2` |
| Écran de connexion / installateur | SDDM Breeze + fond NexOS ; Calamares `branding/nexos` | |

## Disposition (différente de Windows, gestes familiers conservés)
- **Barre supérieure fine** : menu NexOS (logo, touche Meta) · horloge et date au centre · zone système à droite.
- **Dock flottant centré en bas**, ajusté à son contenu, qui s'efface devant les fenêtres :
  Fichiers, Firefox, Terminal, Centre Python, Assistant, NexOS Store, Paramètres, Corbeille.
- Raccourcis : Meta (menu et recherche), Meta+E (Fichiers), Ctrl+Alt+T (Terminal),
  **Meta+Espace (Assistant IA)**, Ctrl+Échap (Moniteur système), Alt+Tab.
- Noms d'applications NexOS en français : Fichiers, NexOS Store, Paramètres, Terminal, Moniteur système.
- Français et clavier AZERTY par défaut, fuseau Europe/Paris (modifiables dans Paramètres).

## Vérification réelle (VM QEMU, émulation logicielle sans KVM)
Commande : `make rootfs EDITION=desktop && make disk SIZE=10G && python3 tests/desktop/test_desktop.py out --scenario`

Résultat du 16/10/2026 (`docs/measurements/desktop-test-v0.2-tcg.json`) : **succès**.

| Contrôle | Résultat |
|---|---|
| Session graphique | `plasmashell` et `kwin_wayland` actifs, session de type **wayland** |
| Unités systemd en échec | 0 |
| Menu NexOS (touche Meta) | s'ouvre — capture `docs/screenshots/v0.2-tcg/04-fermer-menu.png` |
| Terminal (Ctrl+Alt+T) + commande `uname -r` | exécutée, affiche `6.12.107+deb13-amd64` — capture `06-…` |
| Assistant (Meta+Espace) | s'ouvre, indique « Moteur arrêté (aucune mémoire IA utilisée) » — capture `08-…` |
| Fichiers (Meta+E) | Dolphin s'ouvre sur le dossier personnel — capture `10-…` |
| RAM utilisée après ouverture de session (VM 4 Go) | 745 Mio (`free`), plasmashell 184 Mio RSS |

Limites de cette vérification : émulation logicielle (≈ 10× plus lente qu'un PC ; le
premier rendu de l'écran a pris plusieurs minutes), rendu graphique logiciel (llvmpipe),
pas de matériel réel. Les temps mesurés ne sont **pas** représentatifs.

## Défauts relevés et corrigés après le premier test
- Icône Assistant invisible sur le dock sombre → nouvelle icône.
- Fenêtre de l'assistant non rattachée à son icône → `setDesktopFileName`.
- Heure en UTC → fuseau Europe/Paris ; dossier « Desktop » en anglais → `xdg-user-dirs`.
- Centre Python absent de l'image → intégré.

## Reste à faire
- Vérification sur matériel réel et dans VirtualBox (avec accélération).
- Assistant de premier démarrage NexOS ; Centre de mises à jour NexOS (aujourd'hui : NexOS Store/Discover).
- Mesures comparatives de RAM (phase 5).
