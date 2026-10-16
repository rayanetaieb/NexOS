#!/usr/bin/env bash
# Aperçu rapide du bureau NexOS : lance le vrai Plasma de l'image dans un chroot, sur un
# écran Wayland VIRTUEL (kwin_wayland --virtual), sans émulation, et capture l'écran.
# Outil de développement du design uniquement : ce n'est pas un test de démarrage.
#   preview.sh ROOT start|shot NOM|run "commande"|stop
set -euo pipefail
ROOT="$1"; CMD="$2"; shift 2
U=nexos; RUN=/run/user/1000
mnt() { mountpoint -q "$ROOT/$1" || mount --bind "/$1" "$ROOT/$1"; }
inchroot() { chroot "$ROOT" runuser -u $U -- env XDG_RUNTIME_DIR=$RUN WAYLAND_DISPLAY=wayland-nexos \
  QT_QPA_PLATFORM=wayland XDG_SESSION_TYPE=wayland XDG_CURRENT_DESKTOP=KDE KDE_FULL_SESSION=true \
  LANG=fr_FR.UTF-8 XDG_MENU_PREFIX=plasma- HOME=/home/$U DBUS_SESSION_BUS_ADDRESS=unix:path=$RUN/bus "$@"; }
case "$CMD" in
  start)
    for d in proc sys dev dev/pts; do mnt $d; done
    mkdir -p "$ROOT$RUN" "$ROOT/tmp/.X11-unix"; chroot "$ROOT" chown $U:$U $RUN; chmod 700 "$ROOT$RUN"
    chroot "$ROOT" runuser -u $U -- env XDG_RUNTIME_DIR=$RUN dbus-daemon --session \
      --address=unix:path=$RUN/bus --fork --nopidfile
    # Écran X virtuel de l'hôte (rendu OpenGL logiciel) dans lequel KWin s'affiche.
    if ! pgrep -x Xvfb >/dev/null; then rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
      setsid nohup Xvfb :99 -screen 0 1440x900x24 +extension GLX >/dev/null 2>&1 &
    fi
    sleep 2; mountpoint -q "$ROOT/tmp/.X11-unix" || mount --bind /tmp/.X11-unix "$ROOT/tmp/.X11-unix"
    inchroot sh -c 'DISPLAY=:99 kwin_wayland --x11-display :99 --width 1440 --height 900 \
      --socket wayland-nexos --no-lockscreen >/tmp/kwin.log 2>&1 &'
    sleep 6
    inchroot sh -c '/usr/lib/x86_64-linux-gnu/libexec/kactivitymanagerd >/tmp/kamd.log 2>&1 &'
    inchroot sh -c 'kded6 >/tmp/kded.log 2>&1 &'
    sleep 3
    inchroot sh -c 'plasmashell >/tmp/plasmashell.log 2>&1 &'
    sleep 25; echo "aperçu démarré" ;;
  shot)
    xwd -root -display :99 -silent | convert xwd:- "${OUTDIR:-.}/$1.png" && echo "${OUTDIR:-.}/$1.png" ;;
  run)
    inchroot sh -c "$1" ;;
  stop)
    pkill -x kwin_wayland || true; pkill -x plasmashell || true; pkill -x kactivitymanagerd || true; pkill -x kded6 || true
    pkill -x -U 1000 dbus-daemon || true
    sleep 2
    pkill -x Xvfb || true; for i in $(seq 1 20); do pgrep -x Xvfb >/dev/null || break; sleep 0.5; done
    for d in tmp/.X11-unix dev/pts dev sys proc; do umount -l "$ROOT/$d" 2>/dev/null || true; done ;;
esac
