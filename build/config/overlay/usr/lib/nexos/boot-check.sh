#!/bin/sh
# Rapport de démarrage NexOS sur la console série (tests/boot, tests/desktop).
# Construit en mémoire puis écrit d'un bloc (le getty série fait un vhangup du terminal).
# Édition bureau : attend aussi l'ouverture de la session graphique (plasmashell).
# La machine ne s'éteint que si "nexos.autotest=1" est passé au noyau.
state=$(systemctl is-system-running --wait)
desktop=""
if command -v sddm >/dev/null 2>&1; then
  t0=$(cut -d. -f1 /proc/uptime)
  for i in $(seq 1 900); do pgrep -x plasmashell >/dev/null && break; sleep 1; done
  sleep 20   # laisse la session se stabiliser avant de mesurer
  pid=$(pgrep -x plasmashell | head -1)
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
if grep -q 'nexos.autotest=1' /proc/cmdline; then systemctl --no-block poweroff; fi
