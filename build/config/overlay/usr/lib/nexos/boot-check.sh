#!/bin/sh
# Rapport de démarrage NexOS sur la console série (tests/boot, tests/desktop).
# Construit en mémoire puis écrit d'un bloc (le getty série fait un vhangup du terminal).
# Édition bureau : attend aussi l'ouverture de la session graphique (plasmashell).
# La machine ne s'éteint que si "nexos.autotest=1" est passé au noyau.
state=$(systemctl is-system-running --wait)
desktop=""
if [ "$(systemctl get-default)" = graphical.target ]; then
  # Shell de bureau : plasmashell (KDE) ou gnome-shell (GNOME) — permet de comparer d'autres systèmes.
  # (processus d'un utilisateur ordinaire seulement : le gnome-shell de l'écran de connexion GDM est exclu)
  usershell() { ps -eo uid=,pid=,comm= | awk '$1>=1000 && $3 ~ /^(plasmashell|gnome-shell)$/ {print $2; exit}'; }
  t0=$(cut -d. -f1 /proc/uptime)
  for i in $(seq 1 900); do [ -n "$(usershell)" ] && break; sleep 1; done
  sleep 20   # laisse la session se stabiliser avant de mesurer
  pid=$(usershell)
  # session graphique de l'utilisateur connecté (quel qu'il soit)
  sess=$(for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do
           t=$(loginctl show-session "$s" -p Type --value); c=$(loginctl show-session "$s" -p Class --value)
           [ "$c" = user ] && [ "$t" = wayland -o "$t" = x11 ] && echo "$s" && break; done)
  desktop=$(cat <<D
desktop_plasmashell=$( [ -n "$pid" ] && echo running || echo ABSENT )
desktop_session_type=$( [ -n "$sess" ] && loginctl show-session "$sess" -p Type --value )
desktop_ready_uptime_s=$(cut -d. -f1 /proc/uptime)
desktop_kwin=$(pgrep -x kwin_wayland >/dev/null && echo running || echo ABSENT)
desktop_plasmashell_rss_kib=$( [ -n "$pid" ] && awk '/VmRSS/{print $2}' /proc/$pid/status )
D
)
fi
. /etc/os-release
report=$(cat <<R
NEXOS-REPORT-BEGIN
os=$PRETTY_NAME
kernel=$(uname -r)
state=$state
failed_units=$(systemctl --failed --no-legend | wc -l)
failed_list=$(systemctl --failed --no-legend --plain | awk '{print $1}' | paste -sd, -)
boot_time: $(systemd-analyze 2>/dev/null | head -1)
$desktop
$(free -k | awk '/^Mem:/ {print "mem_used_kib=" $3 " mem_total_kib=" $2}')
processes=$(ps -e --no-headers | wc -l)
python=$(python3 --version 2>&1)
NEXOS-BOOT-OK
NEXOS-REPORT-END
R
)
sleep 2
printf '\n%s\n' "$report" > /dev/ttyS0
# Mesure mémoire « au repos » : 90 s après le premier rapport, sans aucune action.
if [ -n "$desktop" ]; then
  sleep 90
  mem=$(cat <<M
NEXOS-MEM-BEGIN
settle_s=90
$(awk '/^(MemTotal|MemFree|MemAvailable|Buffers|Cached|Shmem|AnonPages|SwapTotal|SwapFree):/ {printf "%s=%s\n", $1, $2}' /proc/meminfo | tr -d ':')
used_kib=$(awk '/^MemTotal:/{t=$2} /^MemAvailable:/{a=$2} END{print t-a}' /proc/meminfo)
processes=$(ps -e --no-headers | wc -l)
blame_top10:
$(systemd-analyze blame 2>/dev/null | head -10 | sed 's/^ */  /')
critical_chain:
$(systemd-analyze critical-chain graphical.target 2>/dev/null | tail -n +3 | head -12 | sed 's/^/  /')
top_rss_kib:
$(ps -eo rss=,comm= --sort=-rss | head -15 | awk '{printf "  %s %s\n", $2, $1}')
NEXOS-MEM-END
M
)
  printf '\n%s\n' "$mem" > /dev/ttyS0
fi
if grep -q 'nexos.autotest=1' /proc/cmdline; then systemctl --no-block poweroff; fi
