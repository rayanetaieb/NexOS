#!/usr/bin/env bash
# Tests fonctionnels des applications intégrées, exécutés DANS l'image NexOS (chroot ou VM).
# Chaque test écrit OK/ÉCHEC/NON-EXÉCUTÉ avec sa raison dans $OUT/app-tests.txt.
# Usage (dans l'image) : run_app_tests.sh /tmp/apptests
set -uo pipefail
OUT="${1:-/tmp/apptests}"; mkdir -p "$OUT"; cd "$OUT" || exit 1
REPORT="$OUT/app-tests.txt"; : > "$REPORT"
HERE="$(cd "$(dirname "$0")" && pwd)"
res() { printf '%-42s %-12s %s\n' "$1" "$2" "$3" | tee -a "$REPORT"; }
export HOME="$OUT/home"; mkdir -p "$HOME"

# ---------------------------------------------------------------- Java / Android
cat > Hello.java <<'EOF'
public class Hello { public static void main(String[] a) { System.out.println("Bonjour depuis Java " + Runtime.version().feature()); } }
EOF
if javac Hello.java 2>javac.err && out=$(java Hello); then res "Java : compilation + exécution" OK "$out"; else res "Java : compilation + exécution" ÉCHEC "$(tail -2 javac.err)"; fi
res "adb (outils Android)" "$(adb version >/dev/null 2>&1 && echo OK || echo ÉCHEC)" "$(adb version 2>/dev/null | head -1)"
res "Règles udev Android (51-android)" "$(ls /lib/udev/rules.d/51-android.rules /usr/lib/udev/rules.d/51-android.rules >/dev/null 2>&1 && echo OK || echo ÉCHEC)" ""
res "Kotlin + Gradle : projet Android" NON-EXÉCUTÉ "Gradle, Kotlin et le plugin Android viennent de services.gradle.org / maven.google.com, bloqués dans l'environnement de build"

# ---------------------------------------------------------------- Arduino
mkdir -p Blink build-blink
printf 'void setup(){pinMode(LED_BUILTIN,OUTPUT);}\nvoid loop(){digitalWrite(LED_BUILTIN,HIGH);delay(500);digitalWrite(LED_BUILTIN,LOW);delay(500);}\n' > Blink/Blink.ino
TOOLS=(); for t in /usr/share/arduino/tools-builder /usr/share/arduino/hardware/tools; do [ -d "$t" ] && TOOLS+=(-tools "$t"); done
if arduino-builder -compile -fqbn arduino:avr:uno -hardware /usr/share/arduino/hardware "${TOOLS[@]}" \
     -build-path "$OUT/build-blink" Blink/Blink.ino > blink.log 2>&1; then
  res "Arduino : compilation Blink (Uno, hors ligne)" OK "$(grep -m1 -E 'Sketch uses|croquis' blink.log)"
else res "Arduino : compilation Blink (Uno, hors ligne)" ÉCHEC "$(tail -3 blink.log | tr '\n' ' ')"; fi
res "Arduino : téléversement sur carte" NON-EXÉCUTÉ "aucune carte physique connectée à l'environnement de test"
res "Arduino IDE 1.8.19 présent" "$( [ -x /usr/bin/arduino ] && echo OK || echo ÉCHEC)" ""

# ---------------------------------------------------------------- KiCad
DEMO=$(ls -d /usr/share/kicad/demos/pic_programmer 2>/dev/null || ls -d /usr/share/doc/kicad/demos/pic_programmer 2>/dev/null)
res "KiCad : kicad-cli" "$(kicad-cli version >/dev/null 2>&1 && echo OK || echo ÉCHEC)" "$(kicad-cli version 2>/dev/null)"
if [ -n "$DEMO" ]; then
  cp -r "$DEMO" kicad && cd kicad
  SCH=$(ls *.kicad_sch | head -1); PCB=$(ls *.kicad_pcb | head -1)
  kicad-cli sch erc "$SCH" -o erc.rpt > erc.log 2>&1; res "KiCad : ERC (schéma)" "$( [ -s erc.rpt ] && echo OK || echo ÉCHEC)" "$(grep -m1 -iE 'violations|errors' erc.rpt)"
  kicad-cli sch export pdf "$SCH" -o schema.pdf > /dev/null 2>&1; res "KiCad : export PDF du schéma" "$( [ -s schema.pdf ] && echo OK || echo ÉCHEC)" "$(du -h schema.pdf 2>/dev/null | cut -f1)"
  kicad-cli sch export netlist "$SCH" -o net.net > /dev/null 2>&1; res "KiCad : export netlist" "$( [ -s net.net ] && echo OK || echo ÉCHEC)" "$(grep -c '(comp ' net.net 2>/dev/null) composants"
  kicad-cli pcb drc "$PCB" -o drc.rpt > drc.log 2>&1; res "KiCad : DRC (PCB)" "$( [ -s drc.rpt ] && echo OK || echo ÉCHEC)" "$(grep -m1 -iE 'violations' drc.rpt)"
  mkdir -p gerbers; kicad-cli pcb export gerbers "$PCB" -o gerbers/ > /dev/null 2>&1
  kicad-cli pcb export drill "$PCB" -o gerbers/ > /dev/null 2>&1
  n=$(ls gerbers | wc -l); res "KiCad : Gerber + perçage (fabrication)" "$( [ "$n" -ge 5 ] && echo OK || echo ÉCHEC)" "$n fichiers"
  kicad-cli pcb render "$PCB" -o rendu3d.png > render.log 2>&1
  res "KiCad : rendu 3D de la carte" "$( [ -s rendu3d.png ] && echo OK || echo ÉCHEC)" "$(tail -1 render.log | cut -c1-80)"
  cd "$OUT"
else res "KiCad : projet de démonstration" ÉCHEC "kicad-demos introuvable"; fi
python3 "$HERE/kicad_sch_to_pcb.py" "$OUT/kicad/net.net" "$OUT/kicad/depuis_schema.kicad_pcb" > sch2pcb.log 2>&1
res "KiCad : schéma → PCB (API pcbnew)" "$( grep -q '^OK' sch2pcb.log && echo OK || echo ÉCHEC)" "$(tail -1 sch2pcb.log | cut -c1-90)"

# ---------------------------------------------------------------- LaTeX
cp "$HERE"/latex/* . 2>/dev/null
if latexmk -pdf -interaction=nonstopmode -halt-on-error rapport.tex > latex1.log 2>&1 && [ -s rapport.pdf ]; then
  pages=$(pdfinfo rapport.pdf 2>/dev/null | awk '/^Pages:/{print $2}')
  res "LaTeX : rapport (maths, image, tableau, biber, FR)" OK "rapport.pdf, $pages page(s)"
else res "LaTeX : rapport (maths, image, tableau, biber, FR)" ÉCHEC "$(grep -m2 '^!' rapport.log)"; fi
if latexmk -xelatex -interaction=nonstopmode -halt-on-error arabe.tex > latex2.log 2>&1 && [ -s arabe.pdf ]; then
  res "LaTeX : document arabe (XeLaTeX + Amiri)" OK "arabe.pdf, $(pdffonts arabe.pdf 2>/dev/null | grep -c Amiri) police(s) Amiri incorporée(s)"
else res "LaTeX : document arabe (XeLaTeX + Amiri)" ÉCHEC "$(grep -m2 '^!' arabe.log)"; fi
res "TeXmaker présent" "$( [ -x /usr/bin/texmaker ] && echo OK || echo ÉCHEC)" ""
res "MiKTeX" NON-EXÉCUTÉ "dépôt miktex.org bloqué dans l'environnement de build ; installation assistée fournie"

echo; echo "Bilan : $(grep -c ' OK ' "$REPORT") OK, $(grep -c ' ÉCHEC ' "$REPORT") ÉCHEC, $(grep -c 'NON-EXÉCUTÉ' "$REPORT") non exécutés" | tee -a "$REPORT"
