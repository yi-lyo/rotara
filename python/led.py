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
