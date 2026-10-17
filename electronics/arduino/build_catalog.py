#!/usr/bin/env python3
"""Sélectionne les 100 bibliothèques du catalogue à partir des dépôts vérifiés (catalog-raw.json)
et écrit catalog.json (catalogue NexOS) + la liste motivée des exclusions.
Usage : build_catalog.py catalog-raw.json catalog.json"""
from __future__ import annotations

import json
import sys

EXCLUDED = {
    "teckel12/NewPing": "dépôt introuvable à cette adresse lors de la vérification",
    "suculent/AESLib": "dépôt introuvable à cette adresse lors de la vérification",
    "jdolinay/avr_debug": "pas au format bibliothèque Arduino (library.properties absent), aucune version publiée",
    "mpflaga/Arduino-MemoryFree": "pas de library.properties, aucune version publiée",
    "JChristensen/extEEPROM": "pas de library.properties ; alternative retenue : SparkFun External EEPROM",
    "lorol/LITTLEFS": "obsolète : LittleFS est intégré au cœur ESP32 ; dépôt archivé",
    "wayoda/LedControl": "dernier commit 2015 ; alternative retenue : MD_MAX72XX",
    "khoih-prog/ESP32TimerInterrupt": "auteur inactif depuis 2022 ; minuteries matérielles intégrées au cœur ESP32",
    "UIPEthernet/UIPEthernet": "maintenance faible ; alternative retenue : Ethernet (officielle)",
    "AndreaLombardo/L298N": "fonction triviale (2 broches + PWM), maintenance faible",
    "rfetick/MPU6050_light": "doublon : Adafruit MPU6050 retenue",
    "sparkfun/SparkFun_BME280_Arduino_Library": "doublon : Adafruit BME280 retenue",
    "ArduinoGetStarted/button": "doublon : Bounce2 et OneButton retenues",
    "contrem/arduino-timer": "doublon : TaskScheduler retenue",
    "Dlloydev/QuickPID": "doublon : PID (br3ttb) retenue",
    "jonnieZG/EWMA": "doublon : RunningAverage retenue",
    "wollewald/ADS1115_WE": "doublon : Adafruit ADS1X15 retenue",
    "mmurdoch/arduinounit": "doublon : AUnit retenue (plus active)",
    "arduino-libraries/Mouse": "proche de Keyboard (même usage HID) ; HID-Project couvre souris et clavier",
    "adafruit/Adafruit_ADXL345": "doublon fonctionnel : Adafruit MPU6050 retenue",
    "adafruit/Adafruit_FT6206_Library": "doublon : XPT2046 et TouchScreen retenues",
    "adafruit/Adafruit_SHT31": "humidité déjà couverte (DHT, BME280), maintenance faible",
    "adafruit/MAX6675-library": "doublon : Adafruit MAX31855 (thermocouple) retenue",
    "JChristensen/DS3232RTC": "doublon : RTClib retenue",
    "Testato/SoftwareWire": "maintenance faible (2021)",
    "bakercp/PacketSerial": "maintenance faible (2022)",
    "sparkfun/SparkFun_BQ27441_Arduino_Library": "dernier commit 2020 ; alternative retenue : Adafruit MAX1704X",
    "MajicDesigns/MD_Parola": "surcouche de MD_MAX72XX (retenue) ; installable à la demande",
    "avishorp/TM1637": "maintenance faible (2020) ; catégorie écrans déjà fournie",
    "sparkfun/SparkFun_MAX3010x_Sensor_Library": "maintenance faible (2022)",
    "JAndrassy/WiFiEspAT": "usage spécialisé (ESP-AT) ; WiFiNINA et WiFiManager retenues",
    "DFRobot/DFRobotDFPlayerMini": "maintenance faible ; module spécifique",
}
# Retenues malgré une maintenance faible : très utilisées, sans équivalent direct dans le catalogue.
NOTES = {
    "Chris--A/Keypad": "très utilisée, stable mais plus maintenue ; fonctionne sur AVR",
    "johnrickman/LiquidCrystal_I2C": "très utilisée ; licence non indiquée dans le dépôt",
    "wayoda/LedControl": "",
    "avishorp/TM1637": "stable, peu d'évolutions",
    "PaulStoffregen/Time": "référence historique ; TimeLib.h",
    "openenergymonitor/EmonLib": "licence non indiquée dans le dépôt",
    "rocketscream/Low-Power": "AVR/SAMD uniquement ; aucune version publiée (branche principale)",
    "OperatorFoundation/Crypto": "fork maintenu de la bibliothèque de Rhys Weatherley",
}


def main(src, dst):
    raw = json.load(open(src, encoding="utf-8"))
    kept, excl = [], []
    for e in raw:
        slug = e["repository"].split("github.com/")[1]
        if slug in EXCLUDED or not e.get("ok"):
            excl.append({"repository": e["repository"], "reason": EXCLUDED.get(slug, e.get("error", "échec"))})
            continue
        e = {k: v for k, v in e.items() if k not in ("path", "ok")}
        if NOTES.get(slug):
            e["note"] = NOTES[slug]
        e["install"] = (f"Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch {e['tag']} "
                        f"{e['repository']}.git ~/Arduino/libraries/{e['name'].replace(' ', '_')}"
                        if e.get("tag") else
                        f"git clone --depth 1 {e['repository']}.git ~/Arduino/libraries/{e['name'].replace(' ', '_')}")
        kept.append(e)
    kept.sort(key=lambda e: (e["category"], e["name"].lower()))
    for i, e in enumerate(kept, 1):
        e["id"] = i
    json.dump({"generated": "nexos/electronics/arduino", "count": len(kept), "libraries": kept, "excluded": excl},
              open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(kept)} retenues, {len(excl)} exclues")
    return len(kept)


if __name__ == "__main__":
    n = main(sys.argv[1], sys.argv[2])
    sys.exit(0 if n == 100 else 1)
