# Teichsensor
A ESP8266 based temperature sensor, using two DS18X20 sensors.

## Resources
This project is based on the work of others, who were so generous as to
share their knowledge and allow reusing it.  
Thank you! Not just to the people whose creations enabled this project,
but to everyone who shares with the community ♥🙏.

- hardware setup and basic logic:
  https://randomnerdtutorials.com/micropython-mqtt-publish-ds18b10-esp32-esp8266/
- ~~https://github.com/rdehuyss/micropython-ota-updater~~ as of writing
  this, there is a problem with MicroPyhton on ESP8266 with SSL
  certificates, so this OTA library cannot be used
- logging: https://github.com/pfalcon/pycopy-lib/tree/master/logging
- MQTT: https://github.com/pfalcon/pycopy-lib/tree/master/umqtt.simple

Basic stuff

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)