#!/usr/bin/env bash
# Personnalisation de l'édition bureau. Appelé par build-rootfs.sh : $1 = racine de l'image.
set -euo pipefail
R="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$HERE/../.."

# --- Langue et clavier (français par défaut, modifiable dans Paramètres) ---
sed -i 's/^# *fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/; s/^# *en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' "$R/etc/locale.gen"
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
printf '[Layout]\nLayoutList=fr\nUse=true\n' > "$R/etc/xdg/kxkbrc"

# --- Compte de démonstration (PROTOTYPE : remplacé par l'installateur en phase 6) ---
if ! chroot "$R" id nexos >/dev/null 2>&1; then
  chroot "$R" useradd -m -s /bin/bash -c "Utilisateur NexOS" nexos
fi
for g in sudo audio video plugdev netdev render input; do
  chroot "$R" getent group "$g" >/dev/null && chroot "$R" usermod -aG "$g" nexos
done
echo 'nexos:nexos' | chroot "$R" chpasswd

# Root verrouillé dans l'édition bureau (administration via sudo).
chroot "$R" passwd -l root >/dev/null

# --- Services ---
chroot "$R" systemctl enable sddm NetworkManager >/dev/null 2>&1
chroot "$R" systemctl set-default graphical.target >/dev/null

# --- Identité système ---
cat > "$R/etc/os-release.nexos" <<'EOF'
PRETTY_NAME="NexOS 0.2 (prototype, base Debian 13)"
NAME="NexOS"
VERSION_ID="0.2"
VERSION="0.2 (prototype)"
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
printf "NexOS 0.2 \\n \\l\n\n" > "$R/etc/issue"

# --- Noms d'applications NexOS (surcharges, sans toucher aux paquets Debian) ---
LA="$R/usr/local/share/applications"; mkdir -p "$LA"
rename_app() { # $1 fichier .desktop  $2 nouveau nom
  local src="$R/usr/share/applications/$1"
  [ -f "$src" ] || return 0
  sed -E "s/^Name(\[fr\])?=.*/Name=$2/; /^Name\[[a-zA-Z_@]+\]=/d" "$src" > "$LA/$1"
}
rename_app org.kde.dolphin.desktop "Fichiers"
rename_app org.kde.discover.desktop "Logithèque"
rename_app systemsettings.desktop "Paramètres"
rename_app org.kde.plasma-systemmonitor.desktop "Moniteur système"
rename_app org.kde.konsole.desktop "Terminal"

# --- Écran de connexion : fond NexOS ---
if [ -d "$R/usr/share/sddm/themes/breeze" ]; then
  printf '[General]\nbackground=/usr/share/wallpapers/NexOS/contents/images_dark/3840x2160.png\ntype=image\n' \
    > "$R/usr/share/sddm/themes/breeze/theme.conf.user"
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

# --- Session : pas d'assistant de bienvenue KDE au premier lancement (NexOS a le sien plus tard) ---
mkdir -p "$R/etc/skel/.config"
printf '[General]\nShouldShow=false\n' > "$R/etc/skel/.config/plasma-welcomerc"
install -d -o 1000 -g 1000 "$R/home/nexos/.config" 2>/dev/null || mkdir -p "$R/home/nexos/.config"
cp "$R/etc/skel/.config/plasma-welcomerc" "$R/home/nexos/.config/"
chroot "$R" chown -R nexos:nexos /home/nexos

# --- Nettoyage ---
chroot "$R" apt-get clean
rm -rf "$R/var/lib/apt/lists/"*
