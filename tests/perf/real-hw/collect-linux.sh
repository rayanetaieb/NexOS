#!/bin/sh
# Mesures comparables sur un PC réel (Linux : NexOS, Ubuntu, Fedora…). À lancer juste après
# l'ouverture de session, sans rien ouvrir d'autre. Attend 2 min de repos, puis écrit le rapport.
# Usage : sh collect-linux.sh > rapport-$(hostname).txt
sleep 120
echo "os=$(. /etc/os-release; echo "$PRETTY_NAME")"
echo "noyau=$(uname -r)"
echo "cpu=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^ //')"
awk '/^MemTotal:/{t=$2} /^MemAvailable:/{a=$2} END{printf "ram_totale_mio=%d\nram_utilisee_mio=%d\n", t/1024, (t-a)/1024}' /proc/meminfo
echo "processus=$(ps -e --no-headers | wc -l)"
echo "disque_systeme_utilise=$(df -h / | awk 'NR==2{print $3}')"
command -v systemd-analyze >/dev/null && echo "demarrage=$(systemd-analyze | head -1)"
echo "session=$XDG_SESSION_TYPE bureau=$XDG_CURRENT_DESKTOP"
