# Catalogue des 100 bibliothèques Arduino de NexOS

Généré par `electronics/arduino/make_doc.py` à partir de `catalog.json` (métadonnées lues dans chaque dépôt, au tag vérifié) et de `compile-results.json` (compilation réelle).

## Méthode de vérification

- Chaque dépôt a été cloné au **tag publié** indiqué ; nom, version, auteur, architectures, dépendances et exemples proviennent de son `library.properties`. La licence vient du fichier LICENSE du dépôt (ou des en-têtes quand il n'y en a pas).
- Compilation **dans l'image NexOS** (chroot de la rootfs construite) avec la chaîne Debian : arduino-builder 1.3.25, cœur arduino-core-avr 1.8.7, avr-gcc 14.2.0, sans réseau. Les 100 bibliothèques sont installées ensemble dans `~/Arduino/libraries`, comme chez un utilisateur ; les dépendances se résolvent donc entre elles.
- Carte cible : Arduino Mega 2560 (`arduino:avr:mega:cpu=atmega2560`) ; Leonardo (`arduino:avr:leonardo`) pour les bibliothèques HID qui exigent un USB natif.
- Pour chaque bibliothèque, jusqu'à 10 exemples livrés sont essayés (les exemples génériques d'abord, ceux nommés pour ESP/Due/SAMD en dernier) ; le premier qui compile est retenu.
- **Seule adaptation** : les exemples U8g2 sont livrés avec le constructeur d'écran commenté ; le harnais active celui d'un écran SSD1306 128×64 I²C (indiqué dans la ligne).
- « Compilée comme dépendance » : l'exemple propre de la bibliothèque exige un capteur hors catalogue, mais son code a été compilé et lié par une autre bibliothèque qui en dépend.
- **Compiler n'est pas tester sur carte** : aucun téléversement ni essai matériel n'a été fait (aucune carte disponible).
- **Non testable** = la bibliothèque vise des cartes dont le cœur (ESP32, ESP8266, SAMD, mbed, nRF52, megaAVR) se télécharge depuis downloads.arduino.cc / dépôts Espressif, inaccessibles dans l'environnement de construction ; ou elle exige une radio BLE/Wi-Fi absente sur AVR. Elle n'est **pas** déclarée fonctionnelle.

## Bilan : 82 compilées · 0 échecs · 18 non testables

Exclues après vérification : 32 candidates (liste en fin de document).

## 01. Entrées-sorties et fonctions fondamentales

### 1. Bounce2

- **Dépôt** : https://github.com/thomasfredericks/Bounce2
- **Description** : Debouncing library for Arduino and Wiring.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.71 (tag `v2.71`, 2022-03-21)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-07-20
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2.71 https://github.com/thomasfredericks/Bounce2.git ~/Arduino/libraries/Bounce2
- **Exemple** : examples/bounce_basic/bounce_basic.ino
- **Test** : ✅ compilée : `examples/bounce_basic/bounce_basic.ino` (mega) — croquis 1896 bytes (0%) of program storage space. Maximum is 253952 bytes.

### 2. Encoder

- **Dépôt** : https://github.com/PaulStoffregen/Encoder
- **Description** : Counts quadrature pulses from rotary & linear position encoders.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.4.4 (tag `1.4.4`, 2023-12-11)
- **Dépendances** : aucune
- **Licence** : MIT (en-tête)
- **Maintenance** : modérée — dernier commit 2025-01-04
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.4.4 https://github.com/PaulStoffregen/Encoder.git ~/Arduino/libraries/Encoder
- **Exemple** : examples/Basic/Basic.ino
- **Test** : ✅ compilée : `examples/Basic/Basic.ino` (mega) — croquis 3472 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 3. Keypad

- **Dépôt** : https://github.com/Chris--A/Keypad
- **Description** : Keypad is a library for using matrix style keypads with the Arduino.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.1.1 (tag `3.1.1`, 2016-02-03)
- **Dépendances** : aucune
- **Licence** : AGPL-3.0
- **Maintenance** : faible (> 3 ans) (très utilisée, stable mais plus maintenue ; fonctionne sur AVR) — dernier commit 2017-12-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 3.1.1 https://github.com/Chris--A/Keypad.git ~/Arduino/libraries/Keypad
- **Exemple** : examples/HelloKeypad/HelloKeypad.ino
- **Test** : ✅ compilée : `examples/HelloKeypad/HelloKeypad.ino` (mega) — croquis 3658 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 4. OneButton

- **Dépôt** : https://github.com/mathertel/OneButton
- **Description** : Arduino library for improving the usage of a singe input button.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.6.2 (tag `2.6.2`, 2026-02-20)
- **Dépendances** : aucune
- **Licence** : BSD-3-Clause (library.json)
- **Maintenance** : active — dernier commit 2026-02-20
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.6.2 https://github.com/mathertel/OneButton.git ~/Arduino/libraries/OneButton
- **Exemple** : examples/FunctionalButton/FunctionalButton.ino
- **Test** : ✅ compilée : `examples/FunctionalButton/FunctionalButton.ino` (mega) — croquis 4254 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 5. TaskScheduler

- **Dépôt** : https://github.com/arkhipenko/TaskScheduler
- **Description** : Cooperative multitasking for Arduino, ESPx, STM32 and other microcontrollers.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 4.1.0 (tag `v4.1.0`, 2026-09-27)
- **Dépendances** : aucune
- **Licence** : BSD-3-Clause
- **Maintenance** : active — dernier commit 2026-09-27
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v4.1.0 https://github.com/arkhipenko/TaskScheduler.git ~/Arduino/libraries/TaskScheduler
- **Exemple** : examples/Scheduler_template/Scheduler_template.ino
- **Test** : ✅ compilée : `examples/Scheduler_template/Scheduler_template.ino` (mega) — croquis 4560 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 6. TimerOne

- **Dépôt** : https://github.com/PaulStoffregen/TimerOne
- **Description** : Use hardware Timer1 for finer PWM control and/or running an periodic interrupt function
- **Compatibilité (architectures)** : avr
- **Version vérifiée** : 1.1.1 (tag `1.1.1`, 2023-04-14)
- **Dépendances** : aucune
- **Licence** : CC-BY (en-tête)
- **Maintenance** : modérée — dernier commit 2024-09-03
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.1 https://github.com/PaulStoffregen/TimerOne.git ~/Arduino/libraries/TimerOne
- **Exemple** : examples/ATTiny85/ATTiny85.ino
- **Test** : ✅ compilée : `examples/ATTiny85/ATTiny85.ino` (mega) — croquis 1448 bytes (0%) of program storage space. Maximum is 253952 bytes.

## 02. Communication I2C, SPI et UART

### 7. Adafruit BusIO

- **Dépôt** : https://github.com/adafruit/Adafruit_BusIO
- **Description** : This is a library for abstracting away UART, I2C and SPI interfacing
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.17.4 (tag `1.17.4`, 2025-09-22)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2025-09-22
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.17.4 https://github.com/adafruit/Adafruit_BusIO.git ~/Arduino/libraries/Adafruit_BusIO
- **Exemple** : examples/spi_modetest/spi_modetest.ino
- **Test** : ✅ compilée : `examples/spi_modetest/spi_modetest.ino` (mega) — croquis 5378 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 8. AltSoftSerial

- **Dépôt** : https://github.com/PaulStoffregen/AltSoftSerial
- **Description** : Software emulated serial using hardware timers for improved compatibility
- **Compatibilité (architectures)** : avr
- **Version vérifiée** : 1.4 (tag `1.4`, 2016-02-17)
- **Dépendances** : aucune
- **Licence** : MIT (en-tête)
- **Maintenance** : modérée — dernier commit 2024-11-27
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.4 https://github.com/PaulStoffregen/AltSoftSerial.git ~/Arduino/libraries/AltSoftSerial
- **Exemple** : examples/ReceiveTest/ReceiveTest.ino
- **Test** : ✅ compilée : `examples/ReceiveTest/ReceiveTest.ino` (mega) — croquis 4474 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 9. EspSoftwareSerial

- **Dépôt** : https://github.com/plerup/espsoftwareserial
- **Description** : Implementation of the Arduino software serial for ESP8266/ESP32.
- **Compatibilité (architectures)** : esp8266,esp32
- **Version vérifiée** : 3.4.1 (tag `v2019.03.4`, 2019-03-27)
- **Dépendances** : aucune
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : modérée — dernier commit 2024-01-05
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2019.03.4 https://github.com/plerup/espsoftwareserial.git ~/Arduino/libraries/EspSoftwareSerial
- **Exemple** : examples/loopback/LoopBack.ino
- **Test** : ⚪ non testable ici — architectures esp8266,esp32 : cœur absent hors ligne

## 03. Communication série et USB

### 10. CmdMessenger

- **Dépôt** : https://github.com/thijse/Arduino-CmdMessenger
- **Description** : A serial messaging library for the Arduino and .NET/Mono platform.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 5.0.0 (tag `v5.0.0`, 2026-06-08)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-06-16
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v5.0.0 https://github.com/thijse/Arduino-CmdMessenger.git ~/Arduino/libraries/CmdMessenger
- **Exemple** : examples/SimpleWatchdog/SimpleWatchdog.ino
- **Test** : ✅ compilée : `examples/SimpleWatchdog/SimpleWatchdog.ino` (mega) — croquis 3550 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 11. HID-Project

- **Dépôt** : https://github.com/NicoHood/HID
- **Description** : Extended HID Functions for Arduino
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.8.4 (tag `2.8.4`, 2022-09-24)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : faible (> 3 ans) — dernier commit 2022-09-24
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.8.4 https://github.com/NicoHood/HID.git ~/Arduino/libraries/HID-Project
- **Exemple** : examples/KeylayoutTest/KeylayoutTest.ino
- **Test** : ✅ compilée : `examples/KeylayoutTest/KeylayoutTest.ino` (leonardo) — croquis 6556 bytes (22%) of program storage space. Maximum is 28672 bytes.

### 12. Keyboard

- **Dépôt** : https://github.com/arduino-libraries/Keyboard
- **Description** : Allows an Arduino board with USB capabilities to act as a Keyboard.
- **Compatibilité (architectures)** : avr, samd, sam, renesas_uno
- **Version vérifiée** : 1.0.7 (tag `1.0.7`, 2026-08-01)
- **Dépendances** : aucune
- **Licence** : LGPL-3.0
- **Maintenance** : active — dernier commit 2026-08-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.0.7 https://github.com/arduino-libraries/Keyboard.git ~/Arduino/libraries/Keyboard
- **Exemple** : examples/Serial/Serial.ino
- **Test** : ✅ compilée : `examples/Serial/Serial.ino` (leonardo) — croquis 5130 bytes (17%) of program storage space. Maximum is 28672 bytes.

## 04. Capteurs (température, pression, humidité, mouvement)

### 13. Adafruit BME280 Library

- **Dépôt** : https://github.com/adafruit/Adafruit_BME280_Library
- **Description** : Arduino library for BME280 sensors.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.3.0 (tag `2.3.0`, 2025-04-30)
- **Dépendances** : Adafruit Unified Sensor, Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2025-04-30
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.3.0 https://github.com/adafruit/Adafruit_BME280_Library.git ~/Arduino/libraries/Adafruit_BME280_Library
- **Exemple** : examples/bme280test/bme280test.ino
- **Test** : ✅ compilée : `examples/bme280test/bme280test.ino` (mega) — croquis 14060 bytes (5%) of program storage space. Maximum is 253952 bytes.

### 14. Adafruit BMP280 Library

- **Dépôt** : https://github.com/adafruit/Adafruit_BMP280_Library
- **Description** : Arduino library for BMP280 sensors.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.0.0 (tag `3.0.0`, 2026-01-13)
- **Dépendances** : Adafruit Unified Sensor, Adafruit BusIO
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-01-13
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 3.0.0 https://github.com/adafruit/Adafruit_BMP280_Library.git ~/Arduino/libraries/Adafruit_BMP280_Library
- **Exemple** : examples/bmp280test/bmp280test.ino
- **Test** : ✅ compilée : `examples/bmp280test/bmp280test.ino` (mega) — croquis 13634 bytes (5%) of program storage space. Maximum is 253952 bytes.

### 15. Adafruit MPU6050

- **Dépôt** : https://github.com/adafruit/Adafruit_MPU6050
- **Description** : Arduino library for the MPU6050 sensors in the Adafruit shop
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.2.9 (tag `2.2.9`, 2026-02-11)
- **Dépendances** : Adafruit BusIO, Adafruit Unified Sensor, Adafruit GFX Library, Adafruit SSD1306
- **Licence** : BSD-3-Clause
- **Maintenance** : active — dernier commit 2026-02-11
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.2.9 https://github.com/adafruit/Adafruit_MPU6050.git ~/Arduino/libraries/Adafruit_MPU6050
- **Exemple** : examples/basic_readings/basic_readings.ino
- **Test** : ✅ compilée : `examples/basic_readings/basic_readings.ino` (mega) — croquis 13944 bytes (5%) of program storage space. Maximum is 253952 bytes.

### 16. Adafruit Unified Sensor

- **Dépôt** : https://github.com/adafruit/Adafruit_Sensor
- **Description** : Required for all Adafruit Unified Sensor based libraries.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.1.15 (tag `1.1.15`, 2025-01-06)
- **Dépendances** : aucune
- **Licence** : Apache-2.0
- **Maintenance** : modérée — dernier commit 2025-01-06
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.15 https://github.com/adafruit/Adafruit_Sensor.git ~/Arduino/libraries/Adafruit_Unified_Sensor
- **Exemple** : examples/sensortest/sensortest.ino
- **Test** : ✅ compilée comme dépendance — compilée comme dépendance de Adafruit BME280 Library (examples/bme280test/bme280test.ino) ; son propre exemple échoue : /tmp/tmpx_6mlxi8/sk/sensortest/sensortest.ino:3:10: fatal error: Adafruit_ADXL343.h: No such file or directory

### 17. Adafruit_VL53L0X

- **Dépôt** : https://github.com/adafruit/Adafruit_VL53L0X
- **Description** : Sensor driver for VL53L0X Time of Flight sensor
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.2.5 (tag `1.2.5`, 2026-02-26)
- **Dépendances** : Adafruit SSD1306, Adafruit GFX Library
- **Licence** : BSD (en-tête)
- **Maintenance** : active — dernier commit 2026-02-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.2.5 https://github.com/adafruit/Adafruit_VL53L0X.git ~/Arduino/libraries/Adafruit_VL53L0X
- **Exemple** : examples/vl53l0x/vl53l0x.ino
- **Test** : ✅ compilée : `examples/vl53l0x/vl53l0x.ino` (mega) — croquis 17114 bytes (6%) of program storage space. Maximum is 253952 bytes.

### 18. BH1750

- **Dépôt** : https://github.com/claws/BH1750
- **Description** : Arduino library for the digital light sensor breakout boards containing the BH1750FVI IC
- **Compatibilité (architectures)** : avr,sam,esp8266,esp32,stm32
- **Version vérifiée** : 1.3.0 (tag `1.3.0`, 2022-01-17)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : faible (> 3 ans) — dernier commit 2022-01-17
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.0 https://github.com/claws/BH1750.git ~/Arduino/libraries/BH1750
- **Exemple** : examples/BH1750test/BH1750test.ino
- **Test** : ✅ compilée : `examples/BH1750test/BH1750test.ino` (mega) — croquis 7332 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 19. DallasTemperature

- **Dépôt** : https://github.com/milesburton/Arduino-Temperature-Control-Library
- **Description** : Arduino library for Dallas/Maxim temperature ICs
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 4.0.6 (tag `v4.0.6`, 2026-02-13)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-04-12
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v4.0.6 https://github.com/milesburton/Arduino-Temperature-Control-Library.git ~/Arduino/libraries/DallasTemperature
- **Exemple** : examples/Simple/Simple.ino
- **Test** : ✅ compilée : `examples/Simple/Simple.ino` (mega) — croquis 6344 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 20. DHT sensor library

- **Dépôt** : https://github.com/adafruit/DHT-sensor-library
- **Description** : Arduino library for DHT11, DHT22, etc Temp & Humidity Sensors
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.4.7 (tag `1.4.7`, 2026-02-26)
- **Dépendances** : Adafruit Unified Sensor
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-02-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.4.7 https://github.com/adafruit/DHT-sensor-library.git ~/Arduino/libraries/DHT_sensor_library
- **Exemple** : examples/DHTtester/DHTtester.ino
- **Test** : ✅ compilée : `examples/DHTtester/DHTtester.ino` (mega) — croquis 6920 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 21. HX711 Arduino Library

- **Dépôt** : https://github.com/bogde/HX711
- **Description** : Library to interface the Avia Semiconductor HX711 ADC.
- **Compatibilité (architectures)** : non déclarées
- **Version vérifiée** : 0.7.5 (tag `0.7.5`, 2021-11-24)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : faible (> 3 ans) — dernier commit 2022-03-17
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.7.5 https://github.com/bogde/HX711.git ~/Arduino/libraries/HX711_Arduino_Library
- **Exemple** : examples/HX711_basic_example/HX711_basic_example.ino
- **Test** : ✅ compilée : `examples/HX711_basic_example/HX711_basic_example.ino` (mega) — croquis 3850 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 22. OneWire

- **Dépôt** : https://github.com/PaulStoffregen/OneWire
- **Description** : Access 1-wire temperature sensors, memory and other chips.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.3.8 (tag `v2.3.8`, 2024-02-08)
- **Dépendances** : aucune
- **Licence** : MIT (en-tête)
- **Maintenance** : modérée — dernier commit 2025-06-24
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2.3.8 https://github.com/PaulStoffregen/OneWire.git ~/Arduino/libraries/OneWire
- **Exemple** : examples/DS250x_PROM/DS250x_PROM.ino
- **Test** : ✅ compilée : `examples/DS250x_PROM/DS250x_PROM.ino` (mega) — croquis 3496 bytes (1%) of program storage space. Maximum is 253952 bytes.

## 05. Écrans LCD, OLED, TFT et LED

### 23. Adafruit GFX Library

- **Dépôt** : https://github.com/adafruit/Adafruit-GFX-Library
- **Description** : Adafruit GFX graphics core library, this is the 'core' class that all our other graphics libraries derive from.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.12.6 (tag `1.12.6`, 2026-04-09)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-2-Clause
- **Maintenance** : active — dernier commit 2026-10-16
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.12.6 https://github.com/adafruit/Adafruit-GFX-Library.git ~/Arduino/libraries/Adafruit_GFX_Library
- **Exemple** : examples/GFXcanvas/GFXcanvas.ino
- **Test** : ✅ compilée : `examples/GFXcanvas/GFXcanvas.ino` (mega) — croquis 15624 bytes (6%) of program storage space. Maximum is 253952 bytes.

### 24. Adafruit ILI9341

- **Dépôt** : https://github.com/adafruit/Adafruit_ILI9341
- **Description** : Library for Adafruit ILI9341 displays
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.6.4 (tag `1.6.4`, 2026-09-22)
- **Dépendances** : Adafruit GFX Library, Adafruit STMPE610, Adafruit TouchScreen, Adafruit TSC2007
- **Licence** : BSD (en-tête)
- **Maintenance** : active — dernier commit 2026-09-22
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.6.4 https://github.com/adafruit/Adafruit_ILI9341.git ~/Arduino/libraries/Adafruit_ILI9341
- **Exemple** : examples/graphicstest/graphicstest.ino
- **Test** : ✅ compilée : `examples/graphicstest/graphicstest.ino` (mega) — croquis 18954 bytes (7%) of program storage space. Maximum is 253952 bytes.

### 25. Adafruit NeoPixel

- **Dépôt** : https://github.com/adafruit/Adafruit_NeoPixel
- **Description** : Arduino library for controlling single-wire-based LED pixels and strip.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.15.5 (tag `1.15.5`, 2026-05-12)
- **Dépendances** : aucune
- **Licence** : LGPL-3.0
- **Maintenance** : active — dernier commit 2026-05-12
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.15.5 https://github.com/adafruit/Adafruit_NeoPixel.git ~/Arduino/libraries/Adafruit_NeoPixel
- **Exemple** : examples/simple/simple.ino
- **Test** : ✅ compilée : `examples/simple/simple.ino` (mega) — croquis 3012 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 26. Adafruit SSD1306

- **Dépôt** : https://github.com/adafruit/Adafruit_SSD1306
- **Description** : SSD1306 oled driver library for monochrome 128x64 and 128x32 displays
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.5.17 (tag `2.5.17`, 2026-05-29)
- **Dépendances** : Adafruit GFX Library
- **Licence** : BSD-3-Clause
- **Maintenance** : active — dernier commit 2026-05-29
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.5.17 https://github.com/adafruit/Adafruit_SSD1306.git ~/Arduino/libraries/Adafruit_SSD1306
- **Exemple** : examples/ssd1306_64x32_i2c/ssd1306_64x32_i2c.ino
- **Test** : ✅ compilée : `examples/ssd1306_64x32_i2c/ssd1306_64x32_i2c.ino` (mega) — croquis 21538 bytes (8%) of program storage space. Maximum is 253952 bytes.

### 27. Adafruit ST7735 and ST7789 Library

- **Dépôt** : https://github.com/adafruit/Adafruit-ST7735-Library
- **Description** : This is a library for the Adafruit ST7735, ST7789, ST7796S SPI displays.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.11.0 (tag `1.11.0`, 2025-01-28)
- **Dépendances** : Adafruit GFX Library, Adafruit seesaw Library, SD
- **Licence** : MIT (en-tête)
- **Maintenance** : modérée — dernier commit 2025-01-28
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.11.0 https://github.com/adafruit/Adafruit-ST7735-Library.git ~/Arduino/libraries/Adafruit_ST7735_and_ST7789_Library
- **Exemple** : examples/shieldtest/shieldtest.ino
- **Test** : ✅ compilée : `examples/shieldtest/shieldtest.ino` (mega) — croquis 25016 bytes (9%) of program storage space. Maximum is 253952 bytes.

### 28. FastLED

- **Dépôt** : https://github.com/FastLED/FastLED
- **Description** : Multi-platform library for controlling dozens of different types of LEDs along with optimized math, effect, and noise functions.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.10.7 (tag `3.10.7`, 2026-10-10)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-10-16
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 3.10.7 https://github.com/FastLED/FastLED.git ~/Arduino/libraries/FastLED
- **Exemple** : examples/Test/Test.ino
- **Test** : ✅ compilée : `examples/Test/Test.ino` (mega) — croquis 2686 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 29. LiquidCrystal

- **Dépôt** : https://github.com/arduino-libraries/LiquidCrystal
- **Description** : Allows communication with alphanumerical liquid crystal displays (LCDs).
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.0.7 (tag `1.0.7`, 2017-08-10)
- **Dépendances** : aucune
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : active — dernier commit 2026-07-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.0.7 https://github.com/arduino-libraries/LiquidCrystal.git ~/Arduino/libraries/LiquidCrystal
- **Exemple** : examples/HelloWorld/HelloWorld.ino
- **Test** : ✅ compilée : `examples/HelloWorld/HelloWorld.ino` (mega) — croquis 2350 bytes (0%) of program storage space. Maximum is 253952 bytes.

### 30. LiquidCrystal_I2C

- **Dépôt** : https://github.com/johnrickman/LiquidCrystal_I2C
- **Description** : A library for I2C LCD displays.
- **Compatibilité (architectures)** : avr
- **Version vérifiée** : 1.1.2 (tag `1.1.3`, 2016-03-07)
- **Dépendances** : aucune
- **Licence** : non indiquée
- **Maintenance** : faible (> 3 ans) (très utilisée ; licence non indiquée dans le dépôt) — dernier commit 2020-07-07
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.3 https://github.com/johnrickman/LiquidCrystal_I2C.git ~/Arduino/libraries/LiquidCrystal_I2C
- **Exemple** : examples/HelloWorld/HelloWorld.pde
- **Test** : ✅ compilée : `examples/HelloWorld/HelloWorld.pde` (mega) — croquis 3872 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 31. MD_MAX72XX

- **Dépôt** : https://github.com/MajicDesigns/MD_MAX72XX
- **Description** : Implements functions that allow the MAX72xx (eg, MAX7219) to be used for LED matrices (64 individual LEDs)
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.5.1 (tag `v3.5.1`, 2023-12-02)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1
- **Maintenance** : modérée — dernier commit 2024-04-28
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v3.5.1 https://github.com/MajicDesigns/MD_MAX72XX.git ~/Arduino/libraries/MD_MAX72XX
- **Exemple** : examples/MD_MAX72xx_SimplePong/MD_MAX72xx_SimplePong.ino
- **Test** : ✅ compilée : `examples/MD_MAX72xx_SimplePong/MD_MAX72xx_SimplePong.ino` (mega) — croquis 8038 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 32. TFT_eSPI

- **Dépôt** : https://github.com/Bodmer/TFT_eSPI
- **Description** : TFT graphics library for Arduino processors with performance optimisation for RP2040, STM32, ESP8266 and ESP32
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.5.33 (tag `v2.5.33`, 2023-10-30)
- **Dépendances** : aucune
- **Licence** : BSD-2-Clause
- **Maintenance** : active — dernier commit 2026-04-04
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2.5.33 https://github.com/Bodmer/TFT_eSPI.git ~/Arduino/libraries/TFT_eSPI
- **Exemple** : examples/160 x 128/RLE_Font_test/RLE_Font_test.ino
- **Test** : ✅ compilée : `examples/160 x 128/RLE_Font_test/RLE_Font_test.ino` (mega) — croquis 39370 bytes (15%) of program storage space. Maximum is 253952 bytes.

### 33. U8g2

- **Dépôt** : https://github.com/olikraus/U8g2_Arduino
- **Description** : Monochrome LCD, OLED and eInk Library. Display controller: SSD1305, SSD1306, SSD1309, SSD1312, SSD1316, SSD1318, SSD1320, SSD1322, SSD1325, SSD1327, SSD1329, SSD1362, SSD1363, SSD1606, SSD1607, SH1106, SH1107, SH1108, SH1122, T6963, RA8835, LC7981, PCD8544, PCF8812, HX1230, UC1601, UC1604, UC1608, UC1610, UC1611, UC1617, UC1628, UC1638, UC1701, ST7302, ST7511, ST7528, ST7539, ST7565, ST7567, ST7571, ST7586, ST7588, ST75160, ST75161, ST75256, ST75320, NT7534, ST7920, IST3020, IST3088, IST7920, LD7032, KS0108, KS0713, HD44102, T7932, SSD1312, SED1330, SED1520, SBN1661, IL3820, MAX7219, GP1287, GP1247, GP1294, GU800. Interfaces: I2C, SPI, Parallel.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.36.19 (tag `2.37.1`, 2026-05-17)
- **Dépendances** : aucune
- **Licence** : BSD-2-Clause (library.json)
- **Maintenance** : active — dernier commit 2026-05-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.37.1 https://github.com/olikraus/U8g2_Arduino.git ~/Arduino/libraries/U8g2
- **Exemple** : examples/u8x8/HelloWorld/HelloWorld.ino
- **Test** : ✅ compilée : `examples/u8x8/HelloWorld/HelloWorld.ino` (mega) — croquis 6694 bytes (2%) of program storage space. Maximum is 253952 bytes. — adaptation : constructeur SSD1306 128×64 I²C activé

## 06. Écrans tactiles et interfaces graphiques

### 34. Adafruit TouchScreen

- **Dépôt** : https://github.com/adafruit/Adafruit_TouchScreen
- **Description** : Adafruit TouchScreen display library.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.1.6 (tag `1.1.6`, 2025-09-09)
- **Dépendances** : aucune
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2025-09-09
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.6 https://github.com/adafruit/Adafruit_TouchScreen.git ~/Arduino/libraries/Adafruit_TouchScreen
- **Exemple** : examples/touchscreendemo/touchscreendemo.ino
- **Test** : ✅ compilée : `examples/touchscreendemo/touchscreendemo.ino` (mega) — croquis 4290 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 35. lvgl

- **Dépôt** : https://github.com/lvgl/lvgl
- **Description** : Full-featured Graphics Library for Embedded Systems
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 9.6.0 (tag `v9.6.0`, 2026-09-16)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-10-16
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v9.6.0 https://github.com/lvgl/lvgl.git ~/Arduino/libraries/lvgl
- **Exemple** : examples/arduino/LVGL_Arduino/LVGL_Arduino.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/libraries/lvgl__lvgl/src/../include/lvgl/3d/../config/lv_conf_internal.h:147:18: fatal error: ../../../../lv_conf.h: No suc

### 36. MCUFRIEND_kbv

- **Dépôt** : https://github.com/prenticedavid/MCUFRIEND_kbv
- **Description** : TFT Library for 2.4, 2.8, 3.5, 3.6, 3.95 inch mcufriend UNO Shields
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.0.0-Release (tag `v3.0.0`, 2022-06-27)
- **Dépendances** : aucune
- **Licence** : BSD-2-Clause
- **Maintenance** : faible (> 3 ans) — dernier commit 2022-09-22
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v3.0.0 https://github.com/prenticedavid/MCUFRIEND_kbv.git ~/Arduino/libraries/MCUFRIEND_kbv
- **Exemple** : examples/Font_simple/Font_simple.ino
- **Test** : ✅ compilée : `examples/Font_simple/Font_simple.ino` (mega) — croquis 28686 bytes (11%) of program storage space. Maximum is 253952 bytes.

### 37. XPT2046_Touchscreen

- **Dépôt** : https://github.com/PaulStoffregen/XPT2046_Touchscreen
- **Description** : Touchscreens using the XPT2046 controller chip.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.4 (tag `v1.4`, 2021-06-27)
- **Dépendances** : aucune
- **Licence** : MIT (en-tête)
- **Maintenance** : modérée — dernier commit 2024-06-03
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v1.4 https://github.com/PaulStoffregen/XPT2046_Touchscreen.git ~/Arduino/libraries/XPT2046_Touchscreen
- **Exemple** : examples/TouchTest/TouchTest.ino
- **Test** : ✅ compilée : `examples/TouchTest/TouchTest.ino` (mega) — croquis 4732 bytes (1%) of program storage space. Maximum is 253952 bytes.

## 07. Wi-Fi et Bluetooth

### 38. ArduinoBLE

- **Dépôt** : https://github.com/arduino-libraries/ArduinoBLE
- **Description** : Enables Bluetooth® Low Energy connectivity on the Arduino MKR WiFi 1010, Arduino UNO WiFi Rev2, Arduino Nano 33 IoT, Arduino Nano 33 BLE, Nicla Sense ME and UNO R4 WiFi.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.1.0 (tag `2.1.0`, 2026-06-22)
- **Dépendances** : Arduino_SpiNINA
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-06-22
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.1.0 https://github.com/arduino-libraries/ArduinoBLE.git ~/Arduino/libraries/ArduinoBLE
- **Exemple** : examples/Central/LedControl/LedControl.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : <artificial>:(.text+0x11ce): undefined reference to `HCITransport'

### 39. NimBLE-Arduino

- **Dépôt** : https://github.com/h2zero/NimBLE-Arduino
- **Description** : Bluetooth low energy (BLE) library for Arduino based on NimBLE.
- **Compatibilité (architectures)** : esp32,arm-ble
- **Version vérifiée** : 2.5.1 (tag `2.5.1`, 2026-07-29)
- **Dépendances** : aucune
- **Licence** : Apache-2.0
- **Maintenance** : active — dernier commit 2026-09-13
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.5.1 https://github.com/h2zero/NimBLE-Arduino.git ~/Arduino/libraries/NimBLE-Arduino
- **Exemple** : examples/ANCS/ANCS.ino
- **Test** : ⚪ non testable ici — architectures esp32,arm-ble : cœur absent hors ligne

### 40. WiFiManager

- **Dépôt** : https://github.com/tzapu/WiFiManager
- **Description** : WiFi Configuration manager with web configuration portal for Espressif ESPx boards, by tzapu
- **Compatibilité (architectures)** : esp8266,esp32
- **Version vérifiée** : 2.0.17 (tag `v2.0.17`, 2024-03-01)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-02-24
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2.0.17 https://github.com/tzapu/WiFiManager.git ~/Arduino/libraries/WiFiManager
- **Exemple** : examples/Advanced/Advanced.ino
- **Test** : ⚪ non testable ici — architectures esp8266,esp32 : cœur absent hors ligne

### 41. WiFiNINA

- **Dépôt** : https://github.com/arduino-libraries/WiFiNINA
- **Description** : Enables network connection (local and Internet) with the Arduino MKR WiFi 1010, Arduino MKR VIDOR 4000, Arduino Uno WiFi Rev.2 and Nano 33 IoT.
- **Compatibilité (architectures)** : samd,mbed_nano,megaavr,zephyr_main
- **Version vérifiée** : 2.1.1 (tag `2.1.1`, 2026-07-06)
- **Dépendances** : Arduino_SpiNINA
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-08-25
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.1.1 https://github.com/arduino-libraries/WiFiNINA.git ~/Arduino/libraries/WiFiNINA
- **Exemple** : examples/AP_SimpleWebServer/AP_SimpleWebServer.ino
- **Test** : ⚪ non testable ici — architectures samd,mbed_nano,megaavr,zephyr_main : cœur absent hors ligne

## 08. ESP32 et microcontrôleurs courants

### 42. Async TCP

- **Dépôt** : https://github.com/mathieucarbou/AsyncTCP
- **Description** : Async TCP Library for ESP32
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.3.2 (tag `v3.3.2`, 2025-01-07)
- **Dépendances** : aucune
- **Licence** : LGPL-3.0 (library.json)
- **Maintenance** : modérée — dernier commit 2025-01-21
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v3.3.2 https://github.com/mathieucarbou/AsyncTCP.git ~/Arduino/libraries/Async_TCP
- **Exemple** : examples/Client/Client.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/libraries/mathieucarbou__AsyncTCP/src/AsyncTCP.h:33:12: fatal error: IPv6Address.h: No such file or directory

### 43. ESP Async WebServer

- **Dépôt** : https://github.com/mathieucarbou/ESPAsyncWebServer
- **Description** : Asynchronous HTTP and WebSocket Server Library for ESP32, ESP8266 and RP2040
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.6.0 (tag `v3.6.0`, 2025-01-09)
- **Dépendances** : aucune
- **Licence** : LGPL-3.0 (library.json)
- **Maintenance** : modérée — dernier commit 2025-01-21
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v3.6.0 https://github.com/mathieucarbou/ESPAsyncWebServer.git ~/Arduino/libraries/ESP_Async_WebServer
- **Exemple** : examples/CaptivePortal/CaptivePortal.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/libraries/mathieucarbou__ESPAsyncWebServer/src/ESPAsyncWebServer.h:26:10: fatal error: FS.h: No such file or directory

### 44. ESP32Servo

- **Dépôt** : https://github.com/madhephaestus/ESP32Servo
- **Description** : Allows ESP32 PWM library with MCPWM support for optimal servo performance.
- **Compatibilité (architectures)** : esp32
- **Version vérifiée** : 3.2.1 (tag `3.2.1`, 2026-05-31)
- **Dépendances** : aucune
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : active — dernier commit 2026-07-22
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 3.2.1 https://github.com/madhephaestus/ESP32Servo.git ~/Arduino/libraries/ESP32Servo
- **Exemple** : examples/AllOutputsSimultaneous/AllOutputsSimultaneous.ino
- **Test** : ⚪ non testable ici — architectures esp32 : cœur absent hors ligne

### 45. ESP32Time

- **Dépôt** : https://github.com/fbiego/ESP32Time
- **Description** : Set and retrieve internal RTC time on ESP32 boards.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.0.6 (tag `2.0.6`, 2024-03-17)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2024-10-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.0.6 https://github.com/fbiego/ESP32Time.git ~/Arduino/libraries/ESP32Time
- **Exemple** : examples/esp32_time/esp32_time.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/libraries/fbiego__ESP32Time/ESP32Time.cpp:27:10: fatal error: sys/time.h: No such file or directory

## 09. Protocoles réseau et MQTT

### 46. ArduinoHttpClient

- **Dépôt** : https://github.com/arduino-libraries/ArduinoHttpClient
- **Description** : [EXPERIMENTAL] Easily interact with web servers from Arduino, using HTTP and WebSockets.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.6.2 (tag `0.6.2`, 2026-09-24)
- **Dépendances** : aucune
- **Licence** : Apache-2.0
- **Maintenance** : active — dernier commit 2026-09-24
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.6.2 https://github.com/arduino-libraries/ArduinoHttpClient.git ~/Arduino/libraries/ArduinoHttpClient
- **Exemple** : examples/ParseURL/ParseURL.ino
- **Test** : ✅ compilée : `examples/ParseURL/ParseURL.ino` (mega) — croquis 5338 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 47. ArduinoJson

- **Dépôt** : https://github.com/bblanchon/ArduinoJson
- **Description** : A simple and efficient JSON library for embedded C++.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 7.4.3 (tag `v7.4.3`, 2026-03-02)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-08-11
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v7.4.3 https://github.com/bblanchon/ArduinoJson.git ~/Arduino/libraries/ArduinoJson
- **Exemple** : examples/JsonServer/JsonServer.ino
- **Test** : ✅ compilée : `examples/JsonServer/JsonServer.ino` (mega) — croquis 24502 bytes (9%) of program storage space. Maximum is 253952 bytes.

### 48. ArduinoModbus

- **Dépôt** : https://github.com/arduino-libraries/ArduinoModbus
- **Description** : Use Modbus equipment with your Arduino.
- **Compatibilité (architectures)** : megaavr,samd,mbed_nano,mbed_portenta,mbed_opta
- **Version vérifiée** : 1.0.9 (tag `1.0.9`, 2023-10-27)
- **Dépendances** : ArduinoRS485
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : active — dernier commit 2026-07-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.0.9 https://github.com/arduino-libraries/ArduinoModbus.git ~/Arduino/libraries/ArduinoModbus
- **Exemple** : examples/RTU/ModbusRTUClientKitchenSink/ModbusRTUClientKitchenSink.ino
- **Test** : ⚪ non testable ici — architectures megaavr,samd,mbed_nano,mbed_portenta,mbed_opta : cœur absent hors ligne

### 49. ArduinoMqttClient

- **Dépôt** : https://github.com/arduino-libraries/ArduinoMqttClient
- **Description** : [BETA] Allows you to send and receive MQTT messages using Arduino.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.1.8 (tag `0.1.8`, 2024-01-31)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-07-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.1.8 https://github.com/arduino-libraries/ArduinoMqttClient.git ~/Arduino/libraries/ArduinoMqttClient
- **Exemple** : examples/WiFiAdvancedCallback/WiFiAdvancedCallback.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/sk/WiFiSimpleSender/WiFiSimpleSender.ino:39:1: error: ‘WiFiClient’ does not name a type

### 50. ArduinoRS485

- **Dépôt** : https://github.com/arduino-libraries/ArduinoRS485
- **Description** : Enables sending and receiving data using the RS-485 standard with RS-485 shields, like the MKR 485 Shield.
- **Compatibilité (architectures)** : samd,mbed_portenta,mbed_opta,mbed_nano,renesas_uno,zephyr
- **Version vérifiée** : 1.1.1 (tag `1.1.1`, 2025-11-05)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-07-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.1 https://github.com/arduino-libraries/ArduinoRS485.git ~/Arduino/libraries/ArduinoRS485
- **Exemple** : examples/RS485Passthrough/RS485Passthrough.ino
- **Test** : ⚪ non testable ici — architectures samd,mbed_portenta,mbed_opta,mbed_nano,renesas_uno,zephyr : cœur absent hors ligne

### 51. Ethernet

- **Dépôt** : https://github.com/arduino-libraries/Ethernet
- **Description** : Enables network connection (local and Internet) using the Arduino Ethernet Board or Shield.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.0.2 (tag `2.0.2`, 2023-03-21)
- **Dépendances** : aucune
- **Licence** : Apache-2.0 (en-tête)
- **Maintenance** : active — dernier commit 2026-07-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.0.2 https://github.com/arduino-libraries/Ethernet.git ~/Arduino/libraries/Ethernet
- **Exemple** : examples/WebClient/WebClient.ino
- **Test** : ✅ compilée : `examples/WebClient/WebClient.ino` (mega) — croquis 17350 bytes (6%) of program storage space. Maximum is 253952 bytes.

### 52. NTPClient

- **Dépôt** : https://github.com/arduino-libraries/NTPClient
- **Description** : An NTPClient to connect to a time server
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.2.1 (tag `3.2.1`, 2022-04-25)
- **Dépendances** : aucune
- **Licence** : MIT (en-tête)
- **Maintenance** : active — dernier commit 2026-07-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 3.2.1 https://github.com/arduino-libraries/NTPClient.git ~/Arduino/libraries/NTPClient
- **Exemple** : examples/Advanced/Advanced.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/sk/Basic/Basic.ino:3:10: fatal error: ESP8266WiFi.h: No such file or directory

### 53. PubSubClient

- **Dépôt** : https://github.com/knolleary/pubsubclient
- **Description** : A client library for MQTT messaging.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.8 (tag `v2.8`, 2020-05-20)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-06-10
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2.8 https://github.com/knolleary/pubsubclient.git ~/Arduino/libraries/PubSubClient
- **Exemple** : examples/mqtt_basic/mqtt_basic.ino
- **Test** : ✅ compilée : `examples/mqtt_basic/mqtt_basic.ino` (mega) — croquis 15182 bytes (5%) of program storage space. Maximum is 253952 bytes.

### 54. WebSockets

- **Dépôt** : https://github.com/Links2004/arduinoWebSockets
- **Description** : WebSockets for Arduino (Server + Client)
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.7.2 (tag `2.7.2`, 2025-12-20)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1 (library.json)
- **Maintenance** : active — dernier commit 2026-09-22
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.7.2 https://github.com/Links2004/arduinoWebSockets.git ~/Arduino/libraries/WebSockets
- **Exemple** : examples/arduino_renesas/arduino_uno_r4_wifi/arduino_uno_r4_wifi.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/libraries/Links2004__arduinoWebSockets/src/WebSockets.h:37:2: error: #error Version 2.x.x currently does not support Arduin

## 10. Stockage, EEPROM et cartes SD

### 55. SD

- **Dépôt** : https://github.com/arduino-libraries/SD
- **Description** : Enables reading and writing on SD cards.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.3.0 (tag `1.3.0`, 2024-07-15)
- **Dépendances** : aucune
- **Licence** : AGPL-3.0
- **Maintenance** : active — dernier commit 2026-07-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.0 https://github.com/arduino-libraries/SD.git ~/Arduino/libraries/SD
- **Exemple** : examples/Files/Files.ino
- **Test** : ✅ compilée : `examples/Files/Files.ino` (mega) — croquis 12694 bytes (4%) of program storage space. Maximum is 253952 bytes.

### 56. SdFat

- **Dépôt** : https://github.com/greiman/SdFat
- **Description** : Provides access to SD memory cards.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.3.1 (tag `2.3.1`, 2025-08-12)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2025-08-12
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.3.1 https://github.com/greiman/SdFat.git ~/Arduino/libraries/SdFat
- **Exemple** : examples/examplesV1/#attic/HelloWorld/HelloWorld.ino
- **Test** : ✅ compilée : `examples/examplesV1/#attic/HelloWorld/HelloWorld.ino` (mega) — croquis 2274 bytes (0%) of program storage space. Maximum is 253952 bytes.

### 57. SparkFun External EEPROM Arduino Library

- **Dépôt** : https://github.com/sparkfun/SparkFun_External_EEPROM_Arduino_Library
- **Description** : Library for I2C Communication with external EEPROMs
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.2.13 (tag `v3.2.13`, 2026-06-24)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-06-24
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v3.2.13 https://github.com/sparkfun/SparkFun_External_EEPROM_Arduino_Library.git ~/Arduino/libraries/SparkFun_External_EEPROM_Arduino_Library
- **Exemple** : examples/Example1_BasicReadWrite/Example1_BasicReadWrite.ino
- **Test** : ✅ compilée : `examples/Example1_BasicReadWrite/Example1_BasicReadWrite.ino` (mega) — croquis 9370 bytes (3%) of program storage space. Maximum is 253952 bytes.

## 11. Horloges temps réel

### 58. RTClib

- **Dépôt** : https://github.com/adafruit/RTClib
- **Description** : A fork of Jeelab's fantastic RTC library
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.1.4 (tag `2.1.4`, 2024-04-09)
- **Dépendances** : Adafruit BusIO
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2024-04-09
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.1.4 https://github.com/adafruit/RTClib.git ~/Arduino/libraries/RTClib
- **Exemple** : examples/ds1307/ds1307.ino
- **Test** : ✅ compilée : `examples/ds1307/ds1307.ino` (mega) — croquis 7570 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 59. Time

- **Dépôt** : https://github.com/PaulStoffregen/Time
- **Description** : Timekeeping functionality for Arduino
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.6.1 (tag `v1.6.1`, 2021-06-21)
- **Dépendances** : aucune
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : faible (> 3 ans) (référence historique ; TimeLib.h) — dernier commit 2021-06-21
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v1.6.1 https://github.com/PaulStoffregen/Time.git ~/Arduino/libraries/Time
- **Exemple** : examples/TimeSerialDateStrings/TimeSerialDateStrings.ino
- **Test** : ✅ compilée : `examples/TimeSerialDateStrings/TimeSerialDateStrings.ino` (mega) — croquis 4320 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 60. Timezone

- **Dépôt** : https://github.com/JChristensen/Timezone
- **Description** : Arduino library to facilitate time zone conversions and automatic daylight saving (summer) time adjustments.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.3.1 (tag `1.3.1`, 2026-07-20)
- **Dépendances** : Time
- **Licence** : AGPL-3.0
- **Maintenance** : active — dernier commit 2026-07-20
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.1 https://github.com/JChristensen/Timezone.git ~/Arduino/libraries/Timezone
- **Exemple** : examples/tzTest/tzTest.ino
- **Test** : ✅ compilée : `examples/tzTest/tzTest.ino` (mega) — croquis 7182 bytes (2%) of program storage space. Maximum is 253952 bytes.

## 12. Moteurs, servomoteurs et commandes de puissance

### 61. AccelStepper

- **Dépôt** : https://github.com/waspinator/AccelStepper
- **Description** : Allows Arduino boards to control a variety of stepper motors.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.64 (tag `1.64`, 2022-11-23)
- **Dépendances** : aucune
- **Licence** : GPL-3.0
- **Maintenance** : faible (> 3 ans) — dernier commit 2022-11-23
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.64 https://github.com/waspinator/AccelStepper.git ~/Arduino/libraries/AccelStepper
- **Exemple** : examples/Bounce/Bounce.pde
- **Test** : ✅ compilée : `examples/Bounce/Bounce.pde` (mega) — croquis 6344 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 62. Adafruit Motor Shield V2 Library

- **Dépôt** : https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library
- **Description** : Library for the Adafruit Motor Shield V2 for Arduino. It supports DC motors & stepper motors with microstepping as well as stacking-support.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.1.4 (tag `1.1.4`, 2026-02-26)
- **Dépendances** : Adafruit ILI9341, Adafruit GFX Library, Adafruit SSD1306, AccelStepper, Servo
- **Licence** : BSD-3-Clause
- **Maintenance** : active — dernier commit 2026-02-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.4 https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library.git ~/Arduino/libraries/Adafruit_Motor_Shield_V2_Library
- **Exemple** : examples/DCMotorTest/DCMotorTest.ino
- **Test** : ✅ compilée : `examples/DCMotorTest/DCMotorTest.ino` (mega) — croquis 6390 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 63. Adafruit PWM Servo Driver Library

- **Dépôt** : https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library
- **Description** : Adafruit PWM Servo Driver Library
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 3.0.3 (tag `3.0.3`, 2026-02-26)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : active — dernier commit 2026-02-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 3.0.3 https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library.git ~/Arduino/libraries/Adafruit_PWM_Servo_Driver_Library
- **Exemple** : examples/pwmtest/pwmtest.ino
- **Test** : ✅ compilée : `examples/pwmtest/pwmtest.ino` (mega) — croquis 7136 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 64. Servo

- **Dépôt** : https://github.com/arduino-libraries/Servo
- **Description** : Allows Arduino boards to control a variety of servo motors.
- **Compatibilité (architectures)** : avr,megaavr,sam,samd,nrf52,stm32f4,mbed,mbed_nano,mbed_portenta,mbed_rp2040,renesas,renesas_portenta,renesas_uno,zephyr
- **Version vérifiée** : 1.3.0 (tag `1.3.0`, 2025-11-06)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-09-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.0 https://github.com/arduino-libraries/Servo.git ~/Arduino/libraries/Servo
- **Exemple** : examples/Knob/Knob.ino
- **Test** : ✅ compilée : `examples/Knob/Knob.ino` (mega) — croquis 3008 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 65. Stepper

- **Dépôt** : https://github.com/arduino-libraries/Stepper
- **Description** : Allows Arduino boards to control a variety of stepper motors.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.1.3 (tag `1.1.3`, 2016-03-08)
- **Dépendances** : aucune
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : active — dernier commit 2026-07-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.3 https://github.com/arduino-libraries/Stepper.git ~/Arduino/libraries/Stepper
- **Exemple** : examples/MotorKnob/MotorKnob.ino
- **Test** : ✅ compilée : `examples/MotorKnob/MotorKnob.ino` (mega) — croquis 2506 bytes (0%) of program storage space. Maximum is 253952 bytes.

### 66. TMCStepper

- **Dépôt** : https://github.com/teemuatlut/TMCStepper
- **Description** : Arduino library for Trinamic stepper drivers
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.7.3 (tag `v0.7.3`, 2021-08-18)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : faible (> 3 ans) — dernier commit 2021-10-17
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v0.7.3 https://github.com/teemuatlut/TMCStepper.git ~/Arduino/libraries/TMCStepper
- **Exemple** : examples/Simple/Simple.ino
- **Test** : ✅ compilée : `examples/Simple/Simple.ino` (mega) — croquis 6484 bytes (2%) of program storage space. Maximum is 253952 bytes.

## 13. ADC, DAC et acquisition de données

### 67. Adafruit ADS1X15

- **Dépôt** : https://github.com/adafruit/Adafruit_ADS1X15
- **Description** : Arduino library for ADS1015/1115 ADCs.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.6.2 (tag `2.6.2`, 2026-01-20)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : active — dernier commit 2026-01-20
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.6.2 https://github.com/adafruit/Adafruit_ADS1X15.git ~/Arduino/libraries/Adafruit_ADS1X15
- **Exemple** : examples/comparator/comparator.ino
- **Test** : ✅ compilée : `examples/comparator/comparator.ino` (mega) — croquis 6152 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 68. Adafruit MCP3008

- **Dépôt** : https://github.com/adafruit/Adafruit_MCP3008
- **Description** : MCP3008 8-Channel 10-Bit ADC
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.3.3 (tag `1.3.3`, 2023-11-15)
- **Dépendances** : Adafruit BusIO
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2023-11-15
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.3 https://github.com/adafruit/Adafruit_MCP3008.git ~/Arduino/libraries/Adafruit_MCP3008
- **Exemple** : examples/simpletest/simpletest.ino
- **Test** : ✅ compilée : `examples/simpletest/simpletest.ino` (mega) — croquis 5478 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 69. Adafruit MCP4725

- **Dépôt** : https://github.com/adafruit/Adafruit_MCP4725
- **Description** : MCP4725 12-bit I2C DAC
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.0.2 (tag `2.0.2`, 2023-11-15)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2023-11-15
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.0.2 https://github.com/adafruit/Adafruit_MCP4725.git ~/Arduino/libraries/Adafruit_MCP4725
- **Exemple** : examples/sinewave/sinewave.ino
- **Test** : ✅ compilée : `examples/sinewave/sinewave.ino` (mega) — croquis 5530 bytes (2%) of program storage space. Maximum is 253952 bytes.

## 14. Mesures électroniques et instrumentation

### 70. Adafruit INA219

- **Dépôt** : https://github.com/adafruit/Adafruit_INA219
- **Description** : INA219 Current Sensor
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.1.0 (tag `2.1.0`, 2021-01-05)
- **Dépendances** : Adafruit NeoPixel, Adafruit GFX Library, Adafruit SSD1306, Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2023-11-15
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.1.0 https://github.com/adafruit/Adafruit_INA219.git ~/Arduino/libraries/Adafruit_INA219
- **Exemple** : examples/getcurrent/getcurrent.ino
- **Test** : ✅ compilée : `examples/getcurrent/getcurrent.ino` (mega) — croquis 9946 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 71. Adafruit MAX31855 library

- **Dépôt** : https://github.com/adafruit/Adafruit-MAX31855-library
- **Description** : Library for the Adafruit Thermocouple breakout with MAX31855K
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.4.2 (tag `1.4.2`, 2023-11-15)
- **Dépendances** : Adafruit BusIO, LiquidCrystal
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2023-11-15
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.4.2 https://github.com/adafruit/Adafruit-MAX31855-library.git ~/Arduino/libraries/Adafruit_MAX31855_library
- **Exemple** : examples/lcdthermocouple/lcdthermocouple.ino
- **Test** : ✅ compilée : `examples/lcdthermocouple/lcdthermocouple.ino` (mega) — croquis 8540 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 72. Adafruit MAX31865 library

- **Dépôt** : https://github.com/adafruit/Adafruit_MAX31865
- **Description** : Library for the Adafruit RTD Amplifier breakout with MAX31865
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.6.2 (tag `1.6.2`, 2023-11-15)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD (en-tête)
- **Maintenance** : modérée — dernier commit 2023-11-15
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.6.2 https://github.com/adafruit/Adafruit_MAX31865.git ~/Arduino/libraries/Adafruit_MAX31865_library
- **Exemple** : examples/max31865/max31865.ino
- **Test** : ✅ compilée : `examples/max31865/max31865.ino` (mega) — croquis 8354 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 73. EmonLib

- **Dépôt** : https://github.com/openenergymonitor/EmonLib
- **Description** : Energy Monitoring Library
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.1.0 (tag `1.1.0`, 2016-10-19)
- **Dépendances** : aucune
- **Licence** : non indiquée
- **Maintenance** : faible (> 3 ans) (licence non indiquée dans le dépôt) — dernier commit 2019-05-31
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.1.0 https://github.com/openenergymonitor/EmonLib.git ~/Arduino/libraries/EmonLib
- **Exemple** : examples/current_only/current_only.ino
- **Test** : ✅ compilée : `examples/current_only/current_only.ino` (mega) — croquis 4494 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 74. INA226

- **Dépôt** : https://github.com/RobTillaart/INA226
- **Description** : Arduino library for INA226 power sensor
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.6.6 (tag `0.6.6`, 2026-01-10)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-08-13
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.6.6 https://github.com/RobTillaart/INA226.git ~/Arduino/libraries/INA226
- **Exemple** : examples/INA226_test_I2C/INA226_test_I2C.ino
- **Test** : ✅ compilée : `examples/INA226_test_I2C/INA226_test_I2C.ino` (mega) — croquis 5396 bytes (2%) of program storage space. Maximum is 253952 bytes.

## 15. Filtres numériques et traitement du signal

### 75. arduinoFFT

- **Dépôt** : https://github.com/kosme/arduinoFFT
- **Description** : A library for implementing floating point Fast Fourier Transform calculations on the Arduino framework.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.0.4 (tag `v2.0.4`, 2024-11-21)
- **Dépendances** : aucune
- **Licence** : AGPL-3.0
- **Maintenance** : modérée — dernier commit 2025-03-23
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v2.0.4 https://github.com/kosme/arduinoFFT.git ~/Arduino/libraries/arduinoFFT
- **Exemple** : Examples/FFT_01/FFT_01.ino
- **Test** : ✅ compilée : `Examples/FFT_01/FFT_01.ino` (mega) — croquis 7342 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 76. PID

- **Dépôt** : https://github.com/br3ttb/Arduino-PID-Library
- **Description** : PID controller
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.2.0 (tag `v1.2.0`, 2017-06-19)
- **Dépendances** : aucune
- **Licence** : GPL-3.0 (en-tête)
- **Maintenance** : modérée — dernier commit 2024-05-31
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v1.2.0 https://github.com/br3ttb/Arduino-PID-Library.git ~/Arduino/libraries/PID
- **Exemple** : examples/PID_Basic/PID_Basic.ino
- **Test** : ✅ compilée : `examples/PID_Basic/PID_Basic.ino` (mega) — croquis 3854 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 77. RunningAverage

- **Dépôt** : https://github.com/RobTillaart/RunningAverage
- **Description** : The library stores the last N individual values in a circular buffer to calculate the running average.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.4.9 (tag `0.4.9`, 2026-03-19)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-03-19
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.4.9 https://github.com/RobTillaart/RunningAverage.git ~/Arduino/libraries/RunningAverage
- **Exemple** : examples/ra_test/ra_test.ino
- **Test** : ✅ compilée : `examples/ra_test/ra_test.ino` (mega) — croquis 6328 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 78. RunningMedian

- **Dépôt** : https://github.com/RobTillaart/RunningMedian
- **Description** : The library stores the last N individual values in a buffer to select the median.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.3.11 (tag `0.3.11`, 2026-03-19)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-03-19
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.3.11 https://github.com/RobTillaart/RunningMedian.git ~/Arduino/libraries/RunningMedian
- **Exemple** : examples/RunningMedianTest1/RunningMedianTest1.ino
- **Test** : ✅ compilée : `examples/RunningMedianTest1/RunningMedianTest1.ino` (mega) — croquis 7488 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 79. SimpleKalmanFilter

- **Dépôt** : https://github.com/denyssene/SimpleKalmanFilter
- **Description** : A simple implementation of Kalman Filter.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.2.0 (tag `v0.2`, 2024-08-30)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2025-10-29
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v0.2 https://github.com/denyssene/SimpleKalmanFilter.git ~/Arduino/libraries/SimpleKalmanFilter
- **Exemple** : examples/BasicKalmanFilterExample/BasicKalmanFilterExample.ino
- **Test** : ✅ compilée : `examples/BasicKalmanFilterExample/BasicKalmanFilterExample.ino` (mega) — croquis 4436 bytes (1%) of program storage space. Maximum is 253952 bytes.

## 16. Gestion des batteries et de l'énergie

### 80. Adafruit MAX1704X

- **Dépôt** : https://github.com/adafruit/Adafruit_MAX1704X
- **Description** : Arduino library for the MAX17048 battery monitors in the Adafruit shop
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.0.3 (tag `1.0.3`, 2024-03-25)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2024-03-25
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.0.3 https://github.com/adafruit/Adafruit_MAX1704X.git ~/Arduino/libraries/Adafruit_MAX1704X
- **Exemple** : examples/MAX17048_basic/MAX17048_basic.ino
- **Test** : ✅ compilée : `examples/MAX17048_basic/MAX17048_basic.ino` (mega) — croquis 10086 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 81. Arduino Low Power

- **Dépôt** : https://github.com/arduino-libraries/ArduinoLowPower
- **Description** : Power save primitives features for SAMD and nRF52 32bit boards
- **Compatibilité (architectures)** : samd,nrf52
- **Version vérifiée** : 1.2.2 (tag `1.2.2`, 2020-12-21)
- **Dépendances** : RTCZero
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-07-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.2.2 https://github.com/arduino-libraries/ArduinoLowPower.git ~/Arduino/libraries/Arduino_Low_Power
- **Exemple** : examples/AdcWakeup/AdcWakeup.ino
- **Test** : ⚪ non testable ici — architectures samd,nrf52 : cœur absent hors ligne

### 82. Battery Sense

- **Dépôt** : https://github.com/rlogiacco/BatterySense
- **Description** : Arduino battery sensing library
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.2.0 (tag `1.2.0`, 2024-01-25)
- **Dépendances** : aucune
- **Licence** : LGPL-3.0
- **Maintenance** : modérée — dernier commit 2024-01-27
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.2.0 https://github.com/rlogiacco/BatterySense.git ~/Arduino/libraries/Battery_Sense
- **Exemple** : examples/CustomRatio/CustomRatio.ino
- **Test** : ✅ compilée : `examples/CustomRatio/CustomRatio.ino` (mega) — croquis 4096 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 83. Low-Power

- **Dépôt** : https://github.com/rocketscream/Low-Power
- **Description** : Lightweight power management library
- **Compatibilité (architectures)** : avr,samd
- **Version vérifiée** : 1.81 (pas de version publiée : branche principale)
- **Dépendances** : aucune
- **Licence** : CC-BY-SA (en-tête)
- **Maintenance** : faible (> 3 ans) (AVR/SAMD uniquement ; aucune version publiée (branche principale)) — dernier commit 2021-10-09
- **Installation** : git clone --depth 1 https://github.com/rocketscream/Low-Power.git ~/Arduino/libraries/Low-Power
- **Exemple** : Examples/powerDownWakePeriodic/powerDownWakePeriodic.ino
- **Test** : ✅ compilée : `Examples/powerDownWakePeriodic/powerDownWakePeriodic.ino` (mega) — croquis 868 bytes (0%) of program storage space. Maximum is 253952 bytes.

## 17. Cartes d'extension et modules courants

### 84. Adafruit MCP23017 Arduino Library

- **Dépôt** : https://github.com/adafruit/Adafruit-MCP23017-Arduino-Library
- **Description** : Arduino Library for MCP23XXX I2C and SPI GPIO port expanders
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 2.3.2 (tag `2.3.2`, 2023-11-15)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2023-11-15
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 2.3.2 https://github.com/adafruit/Adafruit-MCP23017-Arduino-Library.git ~/Arduino/libraries/Adafruit_MCP23017_Arduino_Library
- **Exemple** : examples/mcp23xxx_blink/mcp23xxx_blink.ino
- **Test** : ✅ compilée : `examples/mcp23xxx_blink/mcp23xxx_blink.ino` (mega) — croquis 7834 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 85. Adafruit PN532

- **Dépôt** : https://github.com/adafruit/Adafruit-PN532
- **Description** : Arduino library for SPI and I2C access to the PN532 RFID/Near Field Communication chip
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.3.4 (tag `1.3.4`, 2025-02-18)
- **Dépendances** : Adafruit BusIO
- **Licence** : BSD-3-Clause
- **Maintenance** : modérée — dernier commit 2025-02-18
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.4 https://github.com/adafruit/Adafruit-PN532.git ~/Arduino/libraries/Adafruit_PN532
- **Exemple** : examples/readMifare/readMifare.ino
- **Test** : ✅ compilée : `examples/readMifare/readMifare.ino` (mega) — croquis 10150 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 86. IRremote

- **Dépôt** : https://github.com/Arduino-IRremote/Arduino-IRremote
- **Description** : Send and receive infrared signals with multiple protocols
- **Compatibilité (architectures)** : avr,megaavr,samd,esp8266,esp32,stm32,STM32F1,mbed,mbed_nano,rp2040,mbed_rp2040,renesas_uno,riscv,nRF5
- **Version vérifiée** : 4.7.1 (tag `v4.7.1`, 2026-04-08)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-10-10
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v4.7.1 https://github.com/Arduino-IRremote/Arduino-IRremote.git ~/Arduino/libraries/IRremote
- **Exemple** : examples/SimpleSender/SimpleSender.ino
- **Test** : ✅ compilée : `examples/SimpleSender/SimpleSender.ino` (mega) — croquis 3986 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 87. LoRa

- **Dépôt** : https://github.com/sandeepmistry/arduino-LoRa
- **Description** : An Arduino library for sending and receiving data using LoRa radios.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.8.0 (tag `0.8.0`, 2020-12-05)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2024-06-12
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.8.0 https://github.com/sandeepmistry/arduino-LoRa.git ~/Arduino/libraries/LoRa
- **Exemple** : examples/LoRaSimpleNode/LoRaSimpleNode.ino
- **Test** : ✅ compilée : `examples/LoRaSimpleNode/LoRaSimpleNode.ino` (mega) — croquis 7208 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 88. MFRC522

- **Dépôt** : https://github.com/miguelbalboa/rfid
- **Description** : Arduino RFID Library for MFRC522 (SPI)
- **Compatibilité (architectures)** : avr,megaavr,STM32F1,teensy,esp8266,esp32,samd,atmelsam,rp2040
- **Version vérifiée** : 1.4.12 (tag `1.4.12`, 2025-02-17)
- **Dépendances** : aucune
- **Licence** : Unlicense (library.json)
- **Maintenance** : active — dernier commit 2026-07-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.4.12 https://github.com/miguelbalboa/rfid.git ~/Arduino/libraries/MFRC522
- **Exemple** : examples/DumpInfo/DumpInfo.ino
- **Test** : ✅ compilée : `examples/DumpInfo/DumpInfo.ino` (mega) — croquis 8612 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 89. PCF8574

- **Dépôt** : https://github.com/RobTillaart/PCF8574
- **Description** : Arduino library for PCF8574 - 8 channel I2C IO expander
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.4.6 (tag `0.4.6`, 2026-10-12)
- **Dépendances** : aucune
- **Licence** : MIT (library.json)
- **Maintenance** : active — dernier commit 2026-10-12
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.4.6 https://github.com/RobTillaart/PCF8574.git ~/Arduino/libraries/PCF8574
- **Exemple** : examples/PCF8574_test/PCF8574_test.ino
- **Test** : ✅ compilée : `examples/PCF8574_test/PCF8574_test.ino` (mega) — croquis 5080 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 90. RF24

- **Dépôt** : https://github.com/nRF24/RF24
- **Description** : Radio driver, OSI layer 2 library for nrf24L01(+) modules.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.6.2 (tag `v1.6.2`, 2026-08-13)
- **Dépendances** : aucune
- **Licence** : GPL-2.0-only (library.json)
- **Maintenance** : active — dernier commit 2026-08-13
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v1.6.2 https://github.com/nRF24/RF24.git ~/Arduino/libraries/RF24
- **Exemple** : examples/scanner/scanner.ino
- **Test** : ✅ compilée : `examples/scanner/scanner.ino` (mega) — croquis 5712 bytes (2%) of program storage space. Maximum is 253952 bytes.

### 91. TinyGPSPlus

- **Dépôt** : https://github.com/mikalhart/TinyGPSPlus
- **Description** : TinyGPSPlus provides object-oriented parsing of GPS (NMEA) sentences
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.0.3 (tag `v1.0.3`, 2022-01-19)
- **Dépendances** : aucune
- **Licence** : LGPL (version non précisée) (en-tête)
- **Maintenance** : modérée — dernier commit 2024-05-20
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v1.0.3 https://github.com/mikalhart/TinyGPSPlus.git ~/Arduino/libraries/TinyGPSPlus
- **Exemple** : examples/BasicExample/BasicExample.ino
- **Test** : ✅ compilée : `examples/BasicExample/BasicExample.ino` (mega) — croquis 7590 bytes (2%) of program storage space. Maximum is 253952 bytes.

## 18. Systèmes de fichiers

### 92. Adafruit SPIFlash

- **Dépôt** : https://github.com/adafruit/Adafruit_SPIFlash
- **Description** : SPI Flash filesystem support for FAT and CircuitPython FS support from within Arduino
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 5.1.1 (tag `5.1.1`, 2025-04-01)
- **Dépendances** : Adafruit NeoPixel, SdFat - Adafruit Fork
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2025-04-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 5.1.1 https://github.com/adafruit/Adafruit_SPIFlash.git ~/Arduino/libraries/Adafruit_SPIFlash
- **Exemple** : examples/SdFat_Flash_and_SDcard/SdFat_Flash_and_SDcard.ino
- **Test** : ⚪ non testable ici — exemples réservés à d'autres cartes (Wi-Fi, ESP, 32 bits) : /tmp/tmpx_6mlxi8/sk/flash_speedtest/flash_speedtest.ino:4:10: fatal error: SdFat_Adafruit_Fork.h: No such file or directory

### 93. SPIMemory

- **Dépôt** : https://github.com/Marzogh/SPIMemory
- **Description** : SPI Memory library for Arduino. (Formerly SPIFlash)
- **Compatibilité (architectures)** : avr,sam,samd,esp8266,esp32,Simblee,stm32,nrf52
- **Version vérifiée** : 3.4.0 (tag `v3.4.0`, 2019-06-03)
- **Dépendances** : aucune
- **Licence** : AGPL-3.0
- **Maintenance** : active — dernier commit 2026-03-05
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v3.4.0 https://github.com/Marzogh/SPIMemory.git ~/Arduino/libraries/SPIMemory
- **Exemple** : examples/TestFlash/TestFlash.ino
- **Test** : ✅ compilée : `examples/TestFlash/TestFlash.ino` (mega) — croquis 22294 bytes (8%) of program storage space. Maximum is 253952 bytes.

## 19. Sécurité et cryptographie

### 94. ArduinoBearSSL

- **Dépôt** : https://github.com/arduino-libraries/ArduinoBearSSL
- **Description** : Port of BearSSL to Arduino.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.8.0 (tag `1.8.0`, 2026-06-09)
- **Dépendances** : Arduino_SecureElement
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2026-07-01
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.8.0 https://github.com/arduino-libraries/ArduinoBearSSL.git ~/Arduino/libraries/ArduinoBearSSL
- **Exemple** : examples/DES/DES.ino
- **Test** : ✅ compilée : `examples/DES/DES.ino` (mega) — croquis 48420 bytes (19%) of program storage space. Maximum is 253952 bytes.

### 95. ArduinoECCX08

- **Dépôt** : https://github.com/arduino-libraries/ArduinoECCX08
- **Description** : Arduino Library for the Atmel/Microchip ECC508 and ECC608 crypto chips
- **Compatibilité (architectures)** : samd,megaavr,mbed,mbed_nano,mbed_portenta,mbed_opta,mbed_giga,esp32,zephyr_main
- **Version vérifiée** : 1.4.1 (tag `1.4.1`, 2026-05-12)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-08-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.4.1 https://github.com/arduino-libraries/ArduinoECCX08.git ~/Arduino/libraries/ArduinoECCX08
- **Exemple** : examples/ECCX08Counter/ECCX08Counter.ino
- **Test** : ⚪ non testable ici — architectures samd,megaavr,mbed,mbed_nano,mbed_portenta,mbed_opta,mbed_giga,esp32,zephyr_main : cœur absent hors ligne

### 96. base64

- **Dépôt** : https://github.com/Densaugeo/base64_arduino
- **Description** : Base64 encoder/decoder for arduino repo
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.3.0 (tag `1.3.0`, 2022-07-05)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2024-10-02
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.3.0 https://github.com/Densaugeo/base64_arduino.git ~/Arduino/libraries/base64
- **Exemple** : arduino-test/arduino-test.ino
- **Test** : ✅ compilée : `arduino-test/arduino-test.ino` (mega) — croquis 2794 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 97. Crypto

- **Dépôt** : https://github.com/OperatorFoundation/Crypto
- **Description** : Rhys Weatherley's arduinolibs Crypto library.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 0.4.0 (tag `0.4.0`, 2022-05-17)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : faible (> 3 ans) (fork maintenu de la bibliothèque de Rhys Weatherley) — dernier commit 2022-05-17
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 0.4.0 https://github.com/OperatorFoundation/Crypto.git ~/Arduino/libraries/Crypto
- **Exemple** : examples/AES128_Basics/AES128_Basics.ino
- **Test** : ✅ compilée : `examples/AES128_Basics/AES128_Basics.ino` (mega) — croquis 5970 bytes (2%) of program storage space. Maximum is 253952 bytes.

## 20. Outils de débogage et de test

### 98. ArduinoLog

- **Dépôt** : https://github.com/thijse/Arduino-Log
- **Description** : Small logging framework
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.0.3 (tag `1.03`, 2018-12-23)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : active — dernier commit 2025-12-23
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 1.03 https://github.com/thijse/Arduino-Log.git ~/Arduino/libraries/ArduinoLog
- **Exemple** : examples/Log/Log.ino
- **Test** : ✅ compilée : `examples/Log/Log.ino` (mega) — croquis 8184 bytes (3%) of program storage space. Maximum is 253952 bytes.

### 99. AUnit

- **Dépôt** : https://github.com/bxparks/AUnit
- **Description** : A unit testing framework for Arduino platforms inspired by ArduinoUnit and Google Test.
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 1.7.1 (tag `v1.7.1`, 2023-06-15)
- **Dépendances** : aucune
- **Licence** : MIT
- **Maintenance** : modérée — dernier commit 2023-10-31
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch v1.7.1 https://github.com/bxparks/AUnit.git ~/Arduino/libraries/AUnit
- **Exemple** : examples/basic/basic.ino
- **Test** : ✅ compilée : `examples/basic/basic.ino` (mega) — croquis 4794 bytes (1%) of program storage space. Maximum is 253952 bytes.

### 100. Streaming

- **Dépôt** : https://github.com/janelia-arduino/Streaming
- **Description** : Streaming C++-style Output with Operator <<
- **Compatibilité (architectures)** : *
- **Version vérifiée** : 6.3.0 (tag `6.3.0`, 2026-05-26)
- **Dépendances** : aucune
- **Licence** : LGPL-2.1
- **Maintenance** : active — dernier commit 2026-05-26
- **Installation** : Centre Arduino NexOS → Installer, ou : git clone --depth 1 --branch 6.3.0 https://github.com/janelia-arduino/Streaming.git ~/Arduino/libraries/Streaming
- **Exemple** : examples/StreamingTests/StreamingTests.ino
- **Test** : ✅ compilée : `examples/StreamingTests/StreamingTests.ino` (mega) — croquis 13668 bytes (5%) of program storage space. Maximum is 253952 bytes.

## Candidates exclues

| Dépôt | Raison |
|---|---|
| https://github.com/contrem/arduino-timer | doublon : TaskScheduler retenue |
| https://github.com/ArduinoGetStarted/button | doublon : Bounce2 et OneButton retenues |
| https://github.com/Testato/SoftwareWire | maintenance faible (2021) |
| https://github.com/arduino-libraries/Mouse | proche de Keyboard (même usage HID) ; HID-Project couvre souris et clavier |
| https://github.com/bakercp/PacketSerial | maintenance faible (2022) |
| https://github.com/rfetick/MPU6050_light | doublon : Adafruit MPU6050 retenue |
| https://github.com/sparkfun/SparkFun_BME280_Arduino_Library | doublon : Adafruit BME280 retenue |
| https://github.com/adafruit/Adafruit_SHT31 | humidité déjà couverte (DHT, BME280), maintenance faible |
| https://github.com/teckel12/NewPing | dépôt introuvable à cette adresse lors de la vérification |
| https://github.com/adafruit/Adafruit_ADXL345 | doublon fonctionnel : Adafruit MPU6050 retenue |
| https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library | maintenance faible (2022) |
| https://github.com/wayoda/LedControl | dernier commit 2015 ; alternative retenue : MD_MAX72XX |
| https://github.com/MajicDesigns/MD_Parola | surcouche de MD_MAX72XX (retenue) ; installable à la demande |
| https://github.com/avishorp/TM1637 | maintenance faible (2020) ; catégorie écrans déjà fournie |
| https://github.com/adafruit/Adafruit_FT6206_Library | doublon : XPT2046 et TouchScreen retenues |
| https://github.com/JAndrassy/WiFiEspAT | usage spécialisé (ESP-AT) ; WiFiNINA et WiFiManager retenues |
| https://github.com/khoih-prog/ESP32TimerInterrupt | auteur inactif depuis 2022 ; minuteries matérielles intégrées au cœur ESP32 |
| https://github.com/UIPEthernet/UIPEthernet | maintenance faible ; alternative retenue : Ethernet (officielle) |
| https://github.com/JChristensen/extEEPROM | pas de library.properties ; alternative retenue : SparkFun External EEPROM |
| https://github.com/JChristensen/DS3232RTC | doublon : RTClib retenue |
| https://github.com/AndreaLombardo/L298N | fonction triviale (2 broches + PWM), maintenance faible |
| https://github.com/wollewald/ADS1115_WE | doublon : Adafruit ADS1X15 retenue |
| https://github.com/adafruit/MAX6675-library | doublon : Adafruit MAX31855 (thermocouple) retenue |
| https://github.com/jonnieZG/EWMA | doublon : RunningAverage retenue |
| https://github.com/Dlloydev/QuickPID | doublon : PID (br3ttb) retenue |
| https://github.com/sparkfun/SparkFun_BQ27441_Arduino_Library | dernier commit 2020 ; alternative retenue : Adafruit MAX1704X |
| https://github.com/DFRobot/DFRobotDFPlayerMini | maintenance faible ; module spécifique |
| https://github.com/lorol/LITTLEFS | obsolète : LittleFS est intégré au cœur ESP32 ; dépôt archivé |
| https://github.com/suculent/AESLib | dépôt introuvable à cette adresse lors de la vérification |
| https://github.com/mmurdoch/arduinounit | doublon : AUnit retenue (plus active) |
| https://github.com/jdolinay/avr_debug | pas au format bibliothèque Arduino (library.properties absent), aucune version publiée |
| https://github.com/mpflaga/Arduino-MemoryFree | pas de library.properties, aucune version publiée |
