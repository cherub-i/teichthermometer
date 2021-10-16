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

# Config
config = dict()
config["ds_pin"] = 4
config["mqtt_topic_base"] = b"wohnung/sensor_tmp_wp_1"

config["throttle"] = 30
# seconds between sensor reads

config["min_message_interval"] = 60
# seconds, minimum time between transmission of new readings

config["max_message_interval"] = 30 * 60
# seconds, maximum time between transmission of new readings (reading
# will be sent, even if it is the same as the previous reading that was
# sent)

config["relevant_change_increment"] = 0.1
# difference between a reading and the previously sent reading, above
# which a reading is considered to be "different" and worth sending out


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
        temp = "no temp"
        for rom in roms:
            temp = sensor.read_temp(rom)
            if isinstance(temp, float) or (isinstance(temp, int)):
                # temp = b"{0:3.1f}".format(temp)
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
    global config

    client_id = ubinascii.hexlify(machine.unique_id())

    connect_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    mqtt_client = connect_mqtt(
        client_id,
        secrets.MQTT_SERVER,
        secrets.MQTT_PORT,
        secrets.MQTT_USER,
        secrets.MQTT_PASSWORD,
    )

    ds_pin = machine.Pin(config["ds_pin"])
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    log.info("Sensors initialized")

    last_message_sent = dict()
    last_results = dict()

    while True:
        try:
            results = read_dssensor(ds_sensor)
            log.debug("Temperature(s): %s" % results)
            for sensor, measurement in results.items():
                time_since_last_message = time.time() - last_message_sent.get(
                    sensor, 0
                )
                if time_since_last_message > config["min_message_interval"]:
                    if (
                        abs(measurement - last_results.get(sensor, -100))
                        > config["relevant_change_increment"]
                        or time_since_last_message
                        > config["max_message_interval"]
                    ):
                        log.info(
                            "Sending temperature for %s: %.2f"
                            % (sensor, measurement)
                        )
                        mqtt_client.publish(
                            config["mqtt_topic_base"]
                            + b"/"
                            + sensor
                            + b"/temperatur",
                            b"{0:3.1f}".format(measurement),
                        )
                        last_message_sent[sensor] = time.time()
                        last_results[sensor] = measurement
            time.sleep(config["throttle"])
        except OSError as e:
            restart("ERROR: Problem in sensor reading loop")


logging.basicConfig(
    level=logging.DEBUG,
    filename="tt.log",
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger()
log.info("STARTUP")
log.info("config: " + str(config))

start()
