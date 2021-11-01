import machine
import time

led = machine.Pin(2, machine.Pin.OUT)

def blink(times = 3, duration = 0.25):
    for _ in range(times):
        led.off()
        time.sleep(duration)
        led.on()
        time.sleep(duration)
