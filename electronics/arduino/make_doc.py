#!/usr/bin/env python3
"""Génère docs/ARDUINO_LIBRARIES.md et ajoute le résultat de compilation réel à catalog.json.
Usage : make_doc.py catalog.json compile-results.json ../../docs/ARDUINO_LIBRARIES.md"""
import json
import sys
from collections import Counter

cat_p, res_p, doc_p = sys.argv[1:4]
cat = json.load(open(cat_p, encoding="utf-8"))
res = {r["id"]: r for r in json.load(open(res_p, encoding="utf-8"))["results"]}
for e in cat["libraries"]:
    r = res[e["id"]]
    e["test"] = {"status": r["status"], "example": r.get("example", ""), "fqbn": r.get("fqbn", ""),
                 "detail": r["detail"].split("\n")[0][:240], "preparation": r.get("preparation", ""),
                 "indirect": bool(r.get("indirect"))}
json.dump(cat, open(cat_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

n = Counter(res[e["id"]]["status"] for e in cat["libraries"])
L = ["# Catalogue des 100 bibliothèques Arduino de NexOS", "",
     "Généré par `electronics/arduino/make_doc.py` à partir de `catalog.json` (métadonnées lues dans chaque dépôt, au tag vérifié) "
     "et de `compile-results.json` (compilation réelle).", "",
     "## Méthode de vérification", "",
     "- Chaque dépôt a été cloné au **tag publié** indiqué ; nom, version, auteur, architectures, dépendances et exemples "
     "proviennent de son `library.properties`. La licence vient du fichier LICENSE du dépôt (ou des en-têtes quand il n'y en a pas).",
     "- Compilation **dans l'image NexOS** (chroot de la rootfs construite) avec la chaîne Debian : arduino-builder 1.3.25, "
     "cœur arduino-core-avr 1.8.7, avr-gcc 14.2.0, sans réseau. Les 100 bibliothèques sont installées ensemble dans `~/Arduino/libraries`, "
     "comme chez un utilisateur ; les dépendances se résolvent donc entre elles.",
     "- Carte cible : Arduino Mega 2560 (`arduino:avr:mega:cpu=atmega2560`) ; Leonardo (`arduino:avr:leonardo`) pour les bibliothèques "
     "HID qui exigent un USB natif.",
     "- Pour chaque bibliothèque, jusqu'à 10 exemples livrés sont essayés (les exemples génériques d'abord, ceux nommés pour ESP/Due/SAMD en dernier) ; "
     "le premier qui compile est retenu.",
     "- **Seule adaptation** : les exemples U8g2 sont livrés avec le constructeur d'écran commenté ; le harnais active celui d'un écran SSD1306 128×64 I²C (indiqué dans la ligne).",
     "- « Compilée comme dépendance » : l'exemple propre de la bibliothèque exige un capteur hors catalogue, mais son code a été compilé "
     "et lié par une autre bibliothèque qui en dépend.",
     "- **Compiler n'est pas tester sur carte** : aucun téléversement ni essai matériel n'a été fait (aucune carte disponible).",
     "- **Non testable** = la bibliothèque vise des cartes dont le cœur (ESP32, ESP8266, SAMD, mbed, nRF52, megaAVR) se télécharge depuis "
     "downloads.arduino.cc / dépôts Espressif, inaccessibles dans l'environnement de construction ; ou elle exige une radio BLE/Wi-Fi absente sur AVR. "
     "Elle n'est **pas** déclarée fonctionnelle.", "",
     f"## Bilan : {n['ok']} compilées · {n['échec']} échecs · {n['non testable']} non testables", "",
     f"Exclues après vérification : {len(cat['excluded'])} candidates (liste en fin de document).", ""]
cur = None
for e in cat["libraries"]:
    if e["category"] != cur:
        cur = e["category"]
        L += [f"## {cur[:2]}. {e['category_name']}", ""]
    t = e["test"]
    if t["status"] == "ok":
        how = (f"✅ compilée comme dépendance — {t['detail']}" if t["indirect"] else
               f"✅ compilée : `{t['example']}` ({t['fqbn'].split(':')[2]}) — {t['detail'].replace('Sketch uses', 'croquis')}"
               + (f" — adaptation : {t['preparation']}" if t["preparation"] else ""))
    elif t["status"] == "non testable":
        how = f"⚪ non testable ici — {t['detail'][:200]}"
    else:
        how = f"❌ échec — {t['detail'][:200]}"
    maint = e["maintenance"] + (f" ({e['note']})" if e.get("note") else "")
    deps = ", ".join(e["depends"]) or "aucune"
    L += [f"### {e['id']}. {e['name']}", "",
          f"- **Dépôt** : {e['repository']}",
          f"- **Description** : {e.get('description') or e.get('paragraph', '')}",
          f"- **Compatibilité (architectures)** : {e['architectures']}",
          f"- **Version vérifiée** : {e['version']}" + (f" (tag `{e['tag']}`, {e.get('release_date', '?')})" if e.get('tag') else " (pas de version publiée : branche principale)"),
          f"- **Dépendances** : {deps}",
          f"- **Licence** : {e['license']}",
          f"- **Maintenance** : {maint} — dernier commit {e.get('last_commit', '?')}",
          f"- **Installation** : {e['install']}",
          f"- **Exemple** : {(e['examples'] or ['aucun'])[0] if not t['example'] else t['example']}",
          f"- **Test** : {how}", ""]
L += ["## Candidates exclues", "", "| Dépôt | Raison |", "|---|---|"]
L += [f"| {x['repository']} | {x['reason']} |" for x in cat["excluded"]]
open(doc_p, "w", encoding="utf-8").write("\n".join(L) + "\n")
print(dict(n))
