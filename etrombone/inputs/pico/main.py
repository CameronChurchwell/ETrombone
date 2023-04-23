from machine import Pin
import time

button = Pin(1, Pin.IN, Pin.PULL_DOWN)
while True:
    value = button.value()
    print(value)
    time.sleep(1)