# Teichsensor
A ESP8266 based temperature sensor, using two DS18X20 sensors and
sending sensor readings as MQTT messages.

## Learnings
- writing a log-file is probably a bad idea, as the EEPROM has only a
  limited amount of write-cycles after which it will fail
- a complex logic for determining the frequency of measurements and the
  frequency of transfers of the readings (based on time and on
  difference between current and previous reading) is "nice", but when
  it comes to measuring temperatures outside completely uneccesary
- not using deep sleep will prevent me from ever running the device on
  battery without having to change the battery ever so often (or even
  better solar energy)

## Resources
This project is based on the work of others, who were so generous as to
share their knowledge and allow reusing it.  
Thank you! Not just to the people whose creations enabled this project,
but to everyone who shares with the community ♥🙏.

- hardware setup and basic logic
  - ESP8266 setup with two DS18B20:
    https://florianmai.de/2016/11/13/esp8266-nodemcu-lua-tutorial-temperatursensor-ds18b20-abfragen/
  - Micropython code for ESP8266 with DS18B20:
    https://randomnerdtutorials.com/micropython-mqtt-publish-ds18b10-esp32-esp8266/
  - Power usage and deep sleep:
    https://www.youtube.com/watch?v=6SdyImetbp8&t=7s
    - HT7333 Specs: https://www.angeladvance.com/HT73xx.pdf
  - finding the right pins for deep sleep on WEMOS D1 Mini (it's RST
    with D0):
    https://www.mischianti.org/2019/11/21/wemos-d1-mini-esp8266-the-three-type-of-sleep-mode-to-manage-energy-savings-part-4/
  - EEPROM lifetime: https://youtu.be/r-hEOL007nw?t=50
- ~~https://github.com/rdehuyss/micropython-ota-updater~~ as of writing
  this, there is a problem with MicroPyhton on ESP8266 with SSL
  certificates, so this OTA library cannot be used
- logging: https://github.com/pfalcon/pycopy-lib/tree/master/logging
- MQTT: https://github.com/pfalcon/pycopy-lib/tree/master/umqtt.simple
- TODO Energy Saving:
  https://arduinodiy.wordpress.com/2020/01/18/very-deepsleep-and-energy-saving-on-esp8266/

Basic stuff

[![Code style:
black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)