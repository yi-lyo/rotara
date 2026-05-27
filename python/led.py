"""
This script tests the GPIO functionality of the Raspberry Pi.
You can confirm it is working by connecting an LED to `GPIO_PIN`,
then observing that the LED blinks when this script is run.
"""

from time import sleep
import RPi.GPIO as GPIO

LED_PIN = 17
DELAY = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

for x in range(10):
    GPIO.output(LED_PIN, GPIO.HIGH)
    sleep(DELAY)
    GPIO.output(LED_PIN, GPIO.LOW)
    sleep(DELAY)

GPIO.cleanup()
