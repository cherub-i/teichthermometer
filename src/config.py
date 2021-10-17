import sys

# Config
DS_PIN = 4

MQTT_TOPIC_BASE = b"wohnung/sensor_tmp_wp_1"

MEASUREMENT_INTERVAL = 5 * 60
# seconds between measurements (device will deep-sleep during this time)


def all():
    attributes_as_dict = dict()
    for symbol in dir(sys.modules[__name__]):
        if not (symbol.startswith("_")) and symbol.upper() == symbol:
            attributes_as_dict[symbol] = getattr(sys.modules[__name__], symbol)
    return attributes_as_dict
