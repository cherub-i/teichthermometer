import ds18x20
import machine
import network
import onewire
import ubinascii
import time

import secrets
from mqtt.umqttsimple import MQTTClient


# Config
topic_pub_temp = secrets.MQTT_TOPIC_BASE

throttle = 5
min_message_interval = 30  # seconds
max_message_interval = 5 * 60  # seconds
relevant_change_increment = 0.1


def connect_wifi(wifi_ssid, wifi_password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(wifi_ssid, wifi_password)
    while station.isconnected() == False:
        pass
    print(
        "Network connection successful, client IP: %s" % station.ifconfig()[0]
    )


def connect_mqtt(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password):
    try:
        mqtt_client = MQTTClient(
            client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password
        )
        mqtt_client.connect()
        print("MQTT connection successful")
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
    print(message)
    time.sleep(5)
    machine.reset()


def start():
    global topic_pub_temp, min_message_interval, max_message_interval, relevant_change_increment, throttle

    client_id = ubinascii.hexlify(machine.unique_id())

    connect_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    mqtt_client = connect_mqtt(
        client_id,
        secrets.MQTT_SERVER,
        secrets.MQTT_PORT,
        secrets.MQTT_USER,
        secrets.MQTT_PASSWORD,
    )

    ds_pin = machine.Pin(4)
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    print("Sensors initialized")

    last_message_sent = dict()
    last_results = dict()
    while True:
        try:
            time.sleep(throttle)
            results = read_dssensor(ds_sensor)
            # print("Temperature(s): %s" % results)
            for sensor, measurement in results.items():
                time_since_last_message = time.time() - last_message_sent.get(
                    sensor, 0
                )
                if time_since_last_message > min_message_interval:
                    if (
                        abs(measurement - last_results.get(sensor, -100))
                        > relevant_change_increment
                        or time_since_last_message > max_message_interval
                    ):
                        print(
                            "Sending temperature for %s: %.2f"
                            % (sensor, measurement)
                        )
                        mqtt_client.publish(
                            topic_pub_temp + b"/" + sensor + b"/temperatur",
                            b"{0:3.1f}".format(measurement),
                        )
                        last_message_sent[sensor] = time.time()
                        last_results[sensor] = measurement
        except OSError as e:
            restart("ERROR: Problem in sensor reading loop")


start()
