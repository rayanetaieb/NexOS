#!/bin/sh
# Rapport de démarrage NexOS sur la console série, utilisé par tests/boot/test-boot.sh.
# Le rapport est construit en mémoire PUIS écrit d'un bloc : le getty série fait un
# vhangup du terminal au démarrage, qui invaliderait un descripteur ouvert trop tôt.
# La machine ne s'éteint que si "nexos.autotest=1" est passé au noyau.
state=$(systemctl is-system-running --wait)
. /etc/os-release
report=$(cat <<R
NEXOS-REPORT-BEGIN
os=$PRETTY_NAME
kernel=$(uname -r)
state=$state
failed_units=$(systemctl --failed --no-legend | wc -l)
failed_list=$(systemctl --failed --no-legend --plain | awk '{print $1}' | paste -sd, -)
boot_time: $(systemd-analyze 2>/dev/null | head -1)
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
