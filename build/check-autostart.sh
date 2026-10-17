#!/usr/bin/env bash
# Audit de ce qui démarre automatiquement dans une image NexOS (règle : rien de lourd au démarrage).
# Compare les unités systemd activées et les entrées /etc/xdg/autostart à une liste justifiée.
# Catégories : A = indispensable, B = léger et utile, C = à la demande (ne doit PAS démarrer seul).
# Usage : build/check-autostart.sh <racine_de_l_image>   → code 1 si un élément non justifié démarre.
set -uo pipefail
R="${1:?racine de l image}"
declare -A ALLOW=(
  [accounts-daemon.service]="A comptes (écran de connexion)"
  [bluetooth.service]="B Bluetooth (démarre, inactif sans adaptateur)"
  [console-setup.service]="A clavier/console"
  [keyboard-setup.service]="A clavier"
  [drkonqi-coredump-processor@.service]="B rapport de plantage (à l'événement)"
  [e2scrub_reap.service]="B nettoyage ext4 (instantané)"
  [firewalld.service]="A pare-feu"
  [getty@.service]="A console texte"
  [grub-common.service]="A état du démarrage GRUB"
  [networking.service]="A réseau de base"
  [NetworkManager.service]="A réseau"
  [NetworkManager-dispatcher.service]="A réseau (événements)"
  [nexos-boot-check.service]="B rapport de test : VM ou nexos.autotest=1 uniquement"
  [power-profiles-daemon.service]="A profils d'énergie (performances/autonomie)"
  [sddm.service]="A écran de connexion"
  [snapperd.service]="B à la demande D-Bus (ne tourne pas en continu)"
  [systemd-oomd.service]="A protection mémoire"
  [systemd-oomd.socket]="A protection mémoire"
  [systemd-pstore.service]="B journaux de plantage noyau"
  [udisks2.service]="A disques/clés USB"
  [zramswap.service]="A mémoire compressée"
  [cups.socket]="B impression : activée par socket, CUPS ne démarre qu'à la première impression"
  [remote-fs.target]="A cible systemd"
  [apt-daily.timer]="B listes de mises à jour (1×/jour)"
  [apt-daily-upgrade.timer]="B (ne fait rien sans unattended-upgrades)"
  [dpkg-db-backup.timer]="B sauvegarde base dpkg (1×/jour)"
  [e2scrub_all.timer]="B (1×/semaine)"
  [fstrim.timer]="B TRIM SSD (1×/semaine)"
  [snapper-cleanup.timer]="B nettoyage des instantanés (1×/jour)"
  [at-spi-dbus-bus.desktop]="A accessibilité"
  [gmenudbusmenuproxy.desktop]="A menus d'applications"
  [kaccess.desktop]="A accessibilité"
  [kglobalacceld.desktop]="A raccourcis clavier"
  [orca-autostart.desktop]="A lecteur d'écran (inactif sauf si activé)"
  [org.kde.plasma-fallback-session-restore.desktop]="A session"
  [org.kde.plasmashell.desktop]="A bureau"
  [polkit-kde-authentication-agent-1.desktop]="A demandes de mot de passe administrateur"
  [spice-vdagent.desktop]="B presse-papiers en VM (inactif hors VM)"
  [user-dirs-update-gtk.desktop]="B dossiers utilisateur (instantané)"
  [xdg-user-dirs.desktop]="B dossiers utilisateur (instantané)"
  [calamares-desktop-icon.desktop]="B image live uniquement : icône de l installateur (retirée à l installation)"
  [xembedsniproxy.desktop]="A icônes de la zone de notification"
)
# Doivent rester désactivés (catégorie C ou inutiles au démarrage)
DENY=(NetworkManager-wait-online.service snapper-timeline.timer snapper-boot.timer ssh.service \
      cups.service cups-browsed.service ModemManager.service avahi-daemon.service)
bad=0
enabled=$(chroot "$R" systemctl list-unit-files --state=enabled --no-legend 2>/dev/null | awk '{print $1}')
autostart=$(for f in "$R"/etc/xdg/autostart/*.desktop; do
  n=$(basename "$f"); grep -qiE '^(Hidden=true|X-KDE-autostart-condition=.*:false)' "$f" && continue; echo "$n"; done)
# Indexation de fichiers (Baloo) : son autostart ne fait rien si l'indexation est désactivée.
if grep -qs '^Indexing-Enabled=false' "$R/etc/xdg/baloofilerc"; then
  ALLOW[baloo_file.desktop]="C indexation de fichiers : désactivée par défaut, activable dans Paramètres"
fi
printf '%-48s %s\n' "ÉLÉMENT" "CATÉGORIE / JUSTIFICATION"
for u in $enabled $autostart; do
  if [[ -n "${ALLOW[$u]:-}" ]]; then printf '%-48s %s\n' "$u" "${ALLOW[$u]}"
  else printf '%-48s %s\n' "$u" "NON JUSTIFIÉ"; bad=1; fi
done
for u in "${DENY[@]}"; do
  if grep -qx "$u" <<<"$enabled"; then printf '%-48s %s\n' "$u" "INTERDIT au démarrage (catégorie C)"; bad=1; fi
done
echo; [ $bad -eq 0 ] && echo "Bilan : conforme" || echo "Bilan : NON conforme"
exit $bad
