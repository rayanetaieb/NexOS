#!/usr/bin/env bash
# Rejoue une installation NexOS complète dans QEMU (UEFI) depuis l'ISO, par QMP.
# Séquence validée écran par écran le 16/10/2026 (captures dans $VMDIR/screens).
# Les positions de clic correspondent à la fenêtre Calamares centrée en 1440x900.
# Usage : tests/install/run_install.sh out/live/nexos-0.3-amd64.iso
set -euo pipefail
ISO="$1"
export VMDIR="${VMDIR:-out/vm}"
V="python3 tests/vmctl.py"
NEXT="1102 786"
step() { echo ">> $1"; }

rm -rf "$VMDIR"
$V start --iso "$ISO" --disk "$VMDIR/target.qcow2" --uefi --mem 4096 --size 24G
step "attente de la session live (rapport série)"
until grep -q NEXOS-REPORT-END "$VMDIR/serial.log" 2>/dev/null; do sleep 10; done
sleep 90; $V shot 01-live
step "lancement de l'installateur"
$V click 59 70; sleep 0.2; $V click 59 70; sleep 120; $V shot 02-bienvenue
$V click $NEXT; sleep 30; $V shot 03-emplacement
$V click $NEXT; sleep 30; $V shot 04-clavier
$V click $NEXT; sleep 45; $V shot 05-partitions
$V click $NEXT; sleep 30; $V shot 06-utilisateurs
step "compte de test"
$V click 498 232; sleep 2; $V type "Testeur"; sleep 3
for x in 498 712; do $V click $x 420; sleep 2; $V type "hexpulsenexus"; sleep 4; done
sleep 8; $V shot 07-utilisateurs-rempli
$V click $NEXT; sleep 40; $V shot 08-resume
step "installation"
$V click 1103 820; sleep 15; $V shot 09-confirmation
$V click 755 513; sleep 60; $V shot 10-installation-debut
echo "Installation lancée : suivre avec « $V shot NOM »."
