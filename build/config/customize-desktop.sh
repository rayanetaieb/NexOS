#!/usr/bin/env bash
# Personnalisation de l'édition bureau. Appelé par build-rootfs.sh : $1 = racine de l'image.
set -euo pipefail
R="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$HERE/../.."

# --- Langue et clavier (français par défaut, modifiable dans Paramètres) ---
# Français, anglais et arabe (Tunisie, Maroc, Égypte, Arabie saoudite) générés d'avance.
for l in fr_FR en_US ar_TN ar_MA ar_EG ar_SA; do
  sed -i "s/^# *${l}.UTF-8 UTF-8/${l}.UTF-8 UTF-8/" "$R/etc/locale.gen"
done
chroot "$R" locale-gen >/dev/null
printf 'LANG=fr_FR.UTF-8\n' > "$R/etc/default/locale"
cat > "$R/etc/default/keyboard" <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="fr"
XKBVARIANT=""
XKBOPTIONS=""
BACKSPACE="guess"
EOF
mkdir -p "$R/etc/xdg"
# Deux dispositions : français (AZERTY) et arabe ; bascule Alt+Maj, indicateur dans la barre.
printf '[Layout]\nDisplayNames=,\nLayoutList=fr,ara\nVariantList=,\nOptions=grp:alt_shift_toggle\nResetOldOptions=true\nShowFlag=false\nShowLabel=true\nShowLayoutIndicator=true\nShowSingle=false\nUse=true\n' \
  > "$R/etc/xdg/kxkbrc"

# --- Compte de démonstration (PROTOTYPE : remplacé par l'installateur en phase 6) ---
if ! chroot "$R" id nexos >/dev/null 2>&1; then
  chroot "$R" useradd -m -s /bin/bash -c "Utilisateur NexOS" nexos
fi
for g in sudo audio video plugdev netdev render input dialout kvm lpadmin bluetooth; do
  chroot "$R" getent group "$g" >/dev/null && chroot "$R" usermod -aG "$g" nexos
done
echo 'nexos:nexos' | chroot "$R" chpasswd

# Root verrouillé dans l'édition bureau (administration via sudo).
chroot "$R" passwd -l root >/dev/null

# --- Services : rien de lourd au démarrage ---
# Impression : CUPS démarre à la première demande (socket), pas au boot.
chroot "$R" systemctl disable cups.service cups-browsed.service >/dev/null 2>&1 || true
chroot "$R" systemctl enable cups.socket >/dev/null 2>&1 || true

# --- Services ---
chroot "$R" systemctl enable sddm NetworkManager >/dev/null 2>&1
chroot "$R" systemctl set-default graphical.target >/dev/null

# --- Identité système ---
cat > "$R/etc/os-release.nexos" <<'EOF'
PRETTY_NAME="NexOS 0.3 (prototype, base Debian 13)"
NAME="NexOS"
VERSION_ID="0.3"
VERSION="0.3 (prototype)"
ID=nexos
ID_LIKE=debian
LOGO=nexos-logo
HOME_URL="https://github.com/"
EOF
# On garde VERSION_CODENAME Debian (requis par certains outils APT).
grep -E '^(VERSION_CODENAME|DEBIAN_VERSION_FULL)=' "$R/usr/lib/os-release" >> "$R/etc/os-release.nexos" || true
mv "$R/etc/os-release.nexos" "$R/usr/lib/os-release"
ln -sf ../usr/lib/os-release "$R/etc/os-release"
echo nexos > "$R/etc/hostname"
ln -sf /usr/share/zoneinfo/Europe/Paris "$R/etc/localtime"; echo Europe/Paris > "$R/etc/timezone"
printf "NexOS 0.3 \\n \\l\n\n" > "$R/etc/issue"

# --- Noms d'applications NexOS (surcharges, sans toucher aux paquets Debian) ---
LA="$R/usr/local/share/applications"; mkdir -p "$LA"
rename_app() { # $1 fichier .desktop  $2 nouveau nom
  local src="$R/usr/share/applications/$1"
  [ -f "$src" ] || return 0
  sed -E "s/^Name(\[fr\])?=.*/Name=$2/; /^Name\[[a-zA-Z_@]+\]=/d" "$src" > "$LA/$1"
}
rename_app org.kde.dolphin.desktop "Fichiers"
# Un seul magasin : Discover = « NexOS Store » (paquets Debian + Flathub)
rename_app org.kde.discover.desktop "NexOS Store"
rename_app systemsettings.desktop "Paramètres"
rename_app org.kde.plasma-systemmonitor.desktop "Moniteur système"
rename_app org.kde.konsole.desktop "Terminal"

# --- Pare-feu : ufw activé, entrant refusé / sortant autorisé (politique par défaut d'ufw) ---
sed -i 's/^ENABLED=.*/ENABLED=yes/' "$R/etc/ufw/ufw.conf"
chroot "$R" systemctl enable ufw.service >/dev/null 2>&1

# --- Démarrage léger (vérifié par build/check-autostart.sh) ---
# Attente réseau inutile pour un poste de travail ; instantanés horaires/à chaque démarrage
# remplacés par les instantanés APT avant/après et les instantanés manuels.
for u in NetworkManager-wait-online.service snapper-timeline.timer snapper-boot.timer; do
  chroot "$R" systemctl disable "$u" >/dev/null 2>&1 || true
done
sed -i 's/^TIMELINE_CREATE=.*/TIMELINE_CREATE="no"/' "$R/usr/share/snapper/config-templates/default" 2>/dev/null || true
# Notificateur Discover résident (≈140 Mo RSS mesurés au repos) remplacé par un minuteur
# utilisateur quotidien qui lit les listes APT et envoie une notification (aucun processus permanent).
if [ -f "$R/etc/xdg/autostart/org.kde.discover.notifier.desktop" ]; then
  echo 'Hidden=true' >> "$R/etc/xdg/autostart/org.kde.discover.notifier.desktop"
fi
chroot "$R" systemctl --global enable nexos-update-check.timer >/dev/null 2>&1 || true
# Flathub activé automatiquement à la première connexion Internet (minuteur, une seule fois)
chroot "$R" systemctl enable nexos-flathub.timer >/dev/null 2>&1 || true
# Proxy de menu global (barre de menus façon macOS) : non utilisé par la disposition NexOS
if [ -f "$R/etc/xdg/autostart/gmenudbusmenuproxy.desktop" ]; then
  echo 'Hidden=true' >> "$R/etc/xdg/autostart/gmenudbusmenuproxy.desktop"
fi
# Indexation de fichiers Baloo : désactivée par défaut (catégorie C), activable dans Paramètres → Recherche.
printf '[Basic Settings]\nIndexing-Enabled=false\n' > "$R/etc/xdg/baloofilerc"

# --- Écran de connexion : thème SDDM « nexos » (copié par branding-root) ; Breeze reste installé en secours ---
# --- GRUB : polices du thème NexOS générées depuis Noto Sans de l'image ---
GT="$R/usr/share/grub/themes/nexos"
if [ -d "$GT" ] && [ -x "$R/usr/bin/grub-mkfont" ]; then
  for spec in "Regular 16" "Regular 20" "Bold 20" "Bold 48"; do
    set -- $spec
    chroot "$R" grub-mkfont -s "$2" -o "/usr/share/grub/themes/nexos/noto-${1,,}-$2.pf2" \
      "/usr/share/fonts/truetype/noto/NotoSans-$1.ttf"
  done
fi

# --- Assistant IA (nexai) : module Python + lanceur + raccourci Meta+Espace ---
PY="$R/usr/lib/python3/dist-packages"
rm -rf "$PY/nexai"; cp -r "$REPO/packages/nexai/nexai" "$PY/nexai"
find "$PY/nexai" -name '__pycache__' -prune -exec rm -rf {} +
printf '#!/usr/bin/python3\nimport sys\nfrom nexai.cli import main\nsys.exit(main())\n' > "$R/usr/bin/nexai"
chmod 755 "$R/usr/bin/nexai"
cp "$REPO/packages/nexai/data/org.nexos.Assistant.desktop" "$R/usr/share/applications/"
mkdir -p "$R/etc/xdg/nexos"
sed 's|^server_binary = .*|server_binary = "/usr/lib/nexos/llama/llama-server"|' \
  "$REPO/packages/nexai/data/nexai.toml.example" > "$R/etc/xdg/nexos/nexai.toml"
if [ -x "$REPO/out/llama-dist/llama-server" ]; then
  mkdir -p "$R/usr/lib/nexos/llama"
  cp -a "$REPO/out/llama-dist/." "$R/usr/lib/nexos/llama/"
fi

# --- Centre Python : module, commande, profils verrouillés, uv ---
rm -rf "$PY/nexos_python"; cp -r "$REPO/packages/nexos-python-center/nexos_python" "$PY/nexos_python"
find "$PY/nexos_python" -name '__pycache__' -prune -exec rm -rf {} +
printf '#!/usr/bin/python3\nimport sys\nfrom nexos_python.cli import main\nsys.exit(main())\n' > "$R/usr/bin/nexos-python"
chmod 755 "$R/usr/bin/nexos-python"
cp "$REPO/packages/nexos-python-center/data/org.nexos.PythonCenter.desktop" "$R/usr/share/applications/"
mkdir -p "$R/usr/share/nexos/python"
rm -rf "$R/usr/share/nexos/python/profiles"
cp -r "$REPO/python/profiles" "$R/usr/share/nexos/python/profiles"
find "$R/usr/share/nexos/python/profiles" -name '.venv' -prune -exec rm -rf {} +
if [ -x "$REPO/out/uv-dist/uv" ]; then
  mkdir -p "$R/usr/lib/nexos/uv"; cp -a "$REPO/out/uv-dist/." "$R/usr/lib/nexos/uv/"
fi

# --- Control Center, nexos-admin (polkit), installations assistées ---
for pkg in nexos-control-center:nexos_cc nexos-setup:nexos_setup nexos-arduino:nexos_arduino; do
  src="${pkg%%:*}"; mod="${pkg##*:}"
  rm -rf "$PY/$mod"; cp -r "$REPO/packages/$src/$mod" "$PY/$mod"
  find "$PY/$mod" -name '__pycache__' -prune -exec rm -rf {} +
  cp "$REPO/packages/$src/data/"*.desktop "$R/usr/share/applications/"
done
printf '#!/usr/bin/python3\nimport sys\nfrom nexos_cc.gui import main\nsys.exit(main())\n' > "$R/usr/bin/nexos-control-center"
mkdir -p "$R/usr/share/nexos/templates"; cp -r "$REPO/packages/nexos-setup/templates/." "$R/usr/share/nexos/templates/"
printf '#!/usr/bin/python3\nimport sys\nfrom nexos_setup.cli import main\nsys.exit(main())\n' > "$R/usr/bin/nexos-setup"
chmod 755 "$R/usr/bin/nexos-control-center" "$R/usr/bin/nexos-setup"
install -D -m 0755 "$REPO/packages/nexos-control-center/nexos_cc/admin.py" "$R/usr/lib/nexos/nexos-admin"
install -D -m 0644 "$REPO/electronics/arduino/catalog.json" "$R/usr/share/nexos/arduino/catalog.json"
install -D -m 0644 "$REPO/packages/nexos-control-center/data/org.nexos.admin.policy" "$R/usr/share/polkit-1/actions/org.nexos.admin.policy"

# Lanceurs sur le bureau (demandés) : TeXmaker et MiKTeX
mkdir -p "$R/etc/skel/Desktop"
for f in texmaker.desktop org.nexos.MiKTeX.desktop; do
  [ -f "$R/usr/share/applications/$f" ] && install -m 0755 "$R/usr/share/applications/$f" "$R/etc/skel/Desktop/$f"
done
mkdir -p "$R/home/nexos/Desktop"; cp -a "$R/etc/skel/Desktop/." "$R/home/nexos/Desktop/" 2>/dev/null || true

# --- Session : pas d'assistant de bienvenue KDE au premier lancement (NexOS a le sien plus tard) ---
mkdir -p "$R/etc/skel/.config"
printf '[General]\nShouldShow=false\n' > "$R/etc/skel/.config/plasma-welcomerc"
install -d -o 1000 -g 1000 "$R/home/nexos/.config" 2>/dev/null || mkdir -p "$R/home/nexos/.config"
cp "$R/etc/skel/.config/plasma-welcomerc" "$R/home/nexos/.config/"
chroot "$R" chown -R nexos:nexos /home/nexos

