import ds18x20
import machine
import network
import onewire
import ubinascii
import time

import secrets
from ota.ota_updater import OTAUpdater
from mqtt.umqttsimple import MQTTClient


# Config
github_source = "https://github.com/cherub-i/teichsensor"
mqtt_topic_base = secrets.MQTT_TOPIC_BASE

topic_pub_temp = mqtt_topic_base + b"/temperature"

last_message = 0
message_interval = 5


def download_and_install_update_if_available(
    github_url, wifi_ssid, wifi_password, secrets_file
):
    ota_updater = OTAUpdater(github_url, secrets_file)
    ota_updater.install_update_if_available_after_boot(
        wifi_ssid, wifi_password
    )


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
    except OSError as e:
        print("Failed to connect to MQTT broker. Reconnecting...")
        time.sleep(10)
        machine.reset()


def read_dssensor(sensor):
    try:
        roms = sensor.scan()
        sensor.convert_temp()
        time.sleep_ms(750)
        temp = "no temp"
        for rom in roms:
            temp = sensor.read_temp(rom)
        if isinstance(temp, float) or (isinstance(temp, int)):
            temp = b"{0:3.1f}".format(temp)
            return temp
        else:
            return "Invalid sensor readings."
    except OSError as e:
        return "Failed to read sensor."


def start():
    client_id = ubinascii.hexlify(machine.unique_id())

    connect_wifi(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    connect_mqtt(
        client_id,
        secrets.MQTT_SERVER,
        secrets.MQTT_PORT,
        secrets.MQTT_USER,
        secrets.MQTT_PASSWORD,
    )

    # ds_pin = machine.Pin(4)
    # ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

    # while True:
    #     try:
    #         if (time.time() - last_message) > message_interval:
    #         temp = read_dssensor(ds_sensor)
    #         print(temp)
    #         client.publish(topic_pub_temp, temp)
    #         last_message = time.time()
    #     except OSError as e:
    #         restart_and_reconnect()


download_and_install_update_if_available(
    github_source, secrets.WIFI_SSID, secrets.WIFI_PASSWORD, "secrets.py"
)
start()
