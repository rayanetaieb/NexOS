"""Candidates au catalogue NexOS des 100 bibliothèques Arduino (dépôts officiels GitHub).

Critères de sélection (documentés dans docs/ARDUINO_LIBRARIES.md) : bibliothèques de
référence de leur catégorie (fabricants Arduino, Adafruit, SparkFun, auteurs historiques),
documentation et exemples, licence libre identifiable, maintenance (dernier commit),
compatibilité. Les métadonnées sont ensuite VÉRIFIÉES sur chaque dépôt par fetch_catalog.py ;
les candidates introuvables ou inexploitables sont écartées et remplacées.
"""
CANDIDATES: list[tuple[str, str]] = [
    # 1. Entrées-sorties et fondamentaux
    ("01-io", "thomasfredericks/Bounce2"), ("01-io", "mathertel/OneButton"), ("01-io", "Chris--A/Keypad"),
    ("01-io", "PaulStoffregen/Encoder"), ("01-io", "PaulStoffregen/TimerOne"), ("01-io", "contrem/arduino-timer"),
    ("01-io", "arkhipenko/TaskScheduler"), ("01-io", "ArduinoGetStarted/button"),
    # 2. I2C, SPI, UART
    ("02-bus", "adafruit/Adafruit_BusIO"), ("02-bus", "PaulStoffregen/AltSoftSerial"),
    ("02-bus", "plerup/espsoftwareserial"), ("02-bus", "Testato/SoftwareWire"),
    # 3. Série et USB
    ("03-usb", "arduino-libraries/Keyboard"), ("03-usb", "arduino-libraries/Mouse"), ("03-usb", "NicoHood/HID"),
    ("03-usb", "thijse/Arduino-CmdMessenger"), ("03-usb", "bakercp/PacketSerial"),
    # 4. Capteurs
    ("04-capteurs", "adafruit/DHT-sensor-library"), ("04-capteurs", "adafruit/Adafruit_Sensor"),
    ("04-capteurs", "adafruit/Adafruit_BME280_Library"), ("04-capteurs", "adafruit/Adafruit_BMP280_Library"),
    ("04-capteurs", "milesburton/Arduino-Temperature-Control-Library"), ("04-capteurs", "PaulStoffregen/OneWire"),
    ("04-capteurs", "adafruit/Adafruit_MPU6050"), ("04-capteurs", "rfetick/MPU6050_light"),
    ("04-capteurs", "sparkfun/SparkFun_BME280_Arduino_Library"), ("04-capteurs", "adafruit/Adafruit_SHT31"),
    ("04-capteurs", "teckel12/NewPing"), ("04-capteurs", "bogde/HX711"), ("04-capteurs", "adafruit/Adafruit_ADXL345"),
    ("04-capteurs", "sparkfun/SparkFun_MAX3010x_Sensor_Library"), ("04-capteurs", "claws/BH1750"),
    ("04-capteurs", "adafruit/Adafruit_VL53L0X"),
    # 5. Écrans LCD, OLED, TFT, LED
    ("05-ecrans", "arduino-libraries/LiquidCrystal"), ("05-ecrans", "johnrickman/LiquidCrystal_I2C"),
    ("05-ecrans", "adafruit/Adafruit_SSD1306"), ("05-ecrans", "adafruit/Adafruit-GFX-Library"),
    ("05-ecrans", "olikraus/U8g2_Arduino"), ("05-ecrans", "Bodmer/TFT_eSPI"), ("05-ecrans", "adafruit/Adafruit_ILI9341"),
    ("05-ecrans", "adafruit/Adafruit-ST7735-Library"), ("05-ecrans", "wayoda/LedControl"),
    ("05-ecrans", "MajicDesigns/MD_Parola"), ("05-ecrans", "MajicDesigns/MD_MAX72XX"), ("05-ecrans", "avishorp/TM1637"),
    ("05-ecrans", "FastLED/FastLED"), ("05-ecrans", "adafruit/Adafruit_NeoPixel"),
    # 6. Tactile et interfaces graphiques
    ("06-tactile", "lvgl/lvgl"), ("06-tactile", "adafruit/Adafruit_TouchScreen"),
    ("06-tactile", "PaulStoffregen/XPT2046_Touchscreen"), ("06-tactile", "adafruit/Adafruit_FT6206_Library"),
    ("06-tactile", "prenticedavid/MCUFRIEND_kbv"),
    # 7. Wi-Fi et Bluetooth
    ("07-sansfil", "arduino-libraries/WiFiNINA"), ("07-sansfil", "tzapu/WiFiManager"),
    ("07-sansfil", "h2zero/NimBLE-Arduino"), ("07-sansfil", "arduino-libraries/ArduinoBLE"),
    ("07-sansfil", "JAndrassy/WiFiEspAT"),
    # 8. ESP32 et microcontrôleurs
    ("08-esp32", "madhephaestus/ESP32Servo"), ("08-esp32", "mathieucarbou/ESPAsyncWebServer"),
    ("08-esp32", "mathieucarbou/AsyncTCP"), ("08-esp32", "fbiego/ESP32Time"), ("08-esp32", "khoih-prog/ESP32TimerInterrupt"),
    # 9. Réseau et MQTT
    ("09-reseau", "knolleary/pubsubclient"), ("09-reseau", "arduino-libraries/ArduinoMqttClient"),
    ("09-reseau", "arduino-libraries/Ethernet"), ("09-reseau", "bblanchon/ArduinoJson"),
    ("09-reseau", "arduino-libraries/NTPClient"), ("09-reseau", "arduino-libraries/ArduinoHttpClient"),
    ("09-reseau", "Links2004/arduinoWebSockets"), ("09-reseau", "UIPEthernet/UIPEthernet"),
    ("09-reseau", "arduino-libraries/ArduinoModbus"), ("09-reseau", "arduino-libraries/ArduinoRS485"),
    # 10. Stockage, EEPROM, SD
    ("10-stockage", "arduino-libraries/SD"), ("10-stockage", "greiman/SdFat"), ("10-stockage", "JChristensen/extEEPROM"),
    ("10-stockage", "sparkfun/SparkFun_External_EEPROM_Arduino_Library"),
    # 11. Horloges temps réel
    ("11-rtc", "adafruit/RTClib"), ("11-rtc", "JChristensen/DS3232RTC"), ("11-rtc", "PaulStoffregen/Time"),
    ("11-rtc", "JChristensen/Timezone"),
    # 12. Moteurs, servos, puissance
    ("12-moteurs", "arduino-libraries/Servo"), ("12-moteurs", "waspinator/AccelStepper"),
    ("12-moteurs", "arduino-libraries/Stepper"), ("12-moteurs", "adafruit/Adafruit_Motor_Shield_V2_Library"),
    ("12-moteurs", "adafruit/Adafruit-PWM-Servo-Driver-Library"), ("12-moteurs", "teemuatlut/TMCStepper"),
    ("12-moteurs", "AndreaLombardo/L298N"),
    # 13. ADC, DAC, acquisition
    ("13-adc", "adafruit/Adafruit_ADS1X15"), ("13-adc", "adafruit/Adafruit_MCP4725"), ("13-adc", "wollewald/ADS1115_WE"),
    ("13-adc", "adafruit/Adafruit_MCP3008"),
    # 14. Mesures électroniques, instrumentation
    ("14-mesure", "adafruit/Adafruit_INA219"), ("14-mesure", "RobTillaart/INA226"),
    ("14-mesure", "openenergymonitor/EmonLib"), ("14-mesure", "adafruit/Adafruit-MAX31855-library"),
    ("14-mesure", "adafruit/MAX6675-library"), ("14-mesure", "adafruit/Adafruit_MAX31865"),
    # 15. Filtres et traitement du signal
    ("15-signal", "kosme/arduinoFFT"), ("15-signal", "denyssene/SimpleKalmanFilter"),
    ("15-signal", "RobTillaart/RunningMedian"), ("15-signal", "RobTillaart/RunningAverage"),
    ("15-signal", "jonnieZG/EWMA"), ("15-signal", "br3ttb/Arduino-PID-Library"), ("15-signal", "Dlloydev/QuickPID"),
    # 16. Batteries et énergie
    ("16-energie", "rocketscream/Low-Power"), ("16-energie", "adafruit/Adafruit_MAX1704X"),
    ("16-energie", "sparkfun/SparkFun_BQ27441_Arduino_Library"), ("16-energie", "arduino-libraries/ArduinoLowPower"),
    ("16-energie", "rlogiacco/BatterySense"),
    # 17. Cartes d'extension et modules courants
    ("17-modules", "adafruit/Adafruit-MCP23017-Arduino-Library"), ("17-modules", "RobTillaart/PCF8574"),
    ("17-modules", "Arduino-IRremote/Arduino-IRremote"), ("17-modules", "miguelbalboa/rfid"), ("17-modules", "nRF24/RF24"),
    ("17-modules", "sandeepmistry/arduino-LoRa"), ("17-modules", "mikalhart/TinyGPSPlus"),
    ("17-modules", "DFRobot/DFRobotDFPlayerMini"), ("17-modules", "adafruit/Adafruit-PN532"),
    # 18. Systèmes de fichiers
    ("18-fichiers", "adafruit/Adafruit_SPIFlash"), ("18-fichiers", "Marzogh/SPIMemory"),
    ("18-fichiers", "lorol/LITTLEFS"),
    # 19. Sécurité et cryptographie
    ("19-crypto", "arduino-libraries/ArduinoBearSSL"), ("19-crypto", "arduino-libraries/ArduinoECCX08"),
    ("19-crypto", "suculent/AESLib"), ("19-crypto", "Densaugeo/base64_arduino"), ("19-crypto", "OperatorFoundation/Crypto"),
    # 20. Débogage et tests
    ("20-debug", "bxparks/AUnit"), ("20-debug", "mmurdoch/arduinounit"), ("20-debug", "thijse/Arduino-Log"),
    ("20-debug", "jdolinay/avr_debug"), ("20-debug", "mpflaga/Arduino-MemoryFree"), ("20-debug", "janelia-arduino/Streaming"),
]

CATEGORIES = {
    "01-io": "Entrées-sorties et fonctions fondamentales", "02-bus": "Communication I2C, SPI et UART",
    "03-usb": "Communication série et USB", "04-capteurs": "Capteurs (température, pression, humidité, mouvement)",
    "05-ecrans": "Écrans LCD, OLED, TFT et LED", "06-tactile": "Écrans tactiles et interfaces graphiques",
    "07-sansfil": "Wi-Fi et Bluetooth", "08-esp32": "ESP32 et microcontrôleurs courants",
    "09-reseau": "Protocoles réseau et MQTT", "10-stockage": "Stockage, EEPROM et cartes SD",
    "11-rtc": "Horloges temps réel", "12-moteurs": "Moteurs, servomoteurs et commandes de puissance",
    "13-adc": "ADC, DAC et acquisition de données", "14-mesure": "Mesures électroniques et instrumentation",
    "15-signal": "Filtres numériques et traitement du signal", "16-energie": "Gestion des batteries et de l'énergie",
    "17-modules": "Cartes d'extension et modules courants", "18-fichiers": "Systèmes de fichiers",
    "19-crypto": "Sécurité et cryptographie", "20-debug": "Outils de débogage et de test",
}
