import ds18x20
import machine
import network
import onewire
import ubinascii
import time
import sys

import logging
from umqtt.simple import MQTTClient

import secrets
import config


def connect_wifi(wifi_ssid, wifi_password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(wifi_ssid, wifi_password)
    while station.isconnected() == False:
        pass
    log.info(
        "Network connection successful, client IP: %s" % station.ifconfig()[0]
    )


def connect_mqtt(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password):
    try:
        mqtt_client = MQTTClient(
            client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password
        )
        mqtt_client.connect()
        log.info("MQTT connection successful")
        return mqtt_client
    except OSError as e:
        restart("ERROR: Failed to connect to MQTT broker")


def read_dssensor(sensor):
    results = dict()
    try:
        roms = sensor.scan()
        sensor.convert_temp()
        time.sleep_ms(750)
        temp = ""
        for rom in roms:
            temp = sensor.read_temp(rom)
            if isinstance(temp, float) or (isinstance(temp, int)):
                results[sensor_id_from_bytearray(rom)] = temp
            else:
                results[sensor_id_from_bytearray(rom)] = "ERROR"
        return results
    except OSError as e:
        return "Failed to read sensor."


def sensor_id_from_bytearray(bytearray):
    sensor_id = str(bytearray)
    sensor_id = sensor_id.replace("bytearray(b'(", "")
    sensor_id = sensor_id.replace("')", "")
    sensor_id = sensor_id.replace("\\", "")
    sensor_id = sensor_id.replace(" ", "-")
    return sensor_id


def restart(message):
    log.error(message)
    time.sleep(5)
    machine.reset()


def start():
    global log, watchdog

    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    client_id = ubinascii.hexlify(machine.unique_id())

    connect_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    watchdog.feed()

    mqtt_client = connect_mqtt(
        client_id,
        secrets.MQTT_SERVER,
        secrets.MQTT_PORT,
        secrets.MQTT_USER,
        secrets.MQTT_PASSWORD,
    )
    watchdog.feed()

    ds_pin = machine.Pin(config.DS_PIN)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    log.info("Sensors initialized")
    watchdog.feed()

    while True:
        try:
            results = read_dssensor(ds_sensor)
            log.debug("Temperature(s): %s" % results)
            watchdog.feed()
            for sensor, measurement in results.items():
                log.info(
                    "Sending temperature for %s: %.2f" % (sensor, measurement)
                )
                mqtt_client.publish(
                    config.MQTT_TOPIC_BASE + b"/" + sensor + b"/temperatur",
                    b"{0:3.1f}".format(measurement),
                )
                watchdog.feed()
            log.debug("going to deep sleep")
            rtc.alarm(rtc.ALARM0, config.MEASUREMENT_INTERVAL * 1000)
            machine.deepsleep()
        except OSError as e:
            restart("ERROR: Problem in sensor reading loop")


watchdog = machine.WDT()  # enable it with a timeout of 2s

logging.basicConfig(
    level=logging.DEBUG,
    filename="tt.log",
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger()
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    log.info("WAKEUP from deep sleep")
else:
    log.info("STARTUP")
log.info("config: " + str(config.all()))
watchdog.feed()

start()
