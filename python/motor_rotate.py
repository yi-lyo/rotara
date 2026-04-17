from time import sleep
import RPi.GPIO as GPIO

# Constants for convenience
CLOCKWISE = 1
COUNTERCLOCKWISE = 0

# Electrical wiring
EN_PIN = 17
DIR_PIN = 20
STEP_PIN = 21
M0_PIN = 14
M1_PIN = 15
M2_PIN = 18

# Stepper motor characteristics
FULL_ROTATION = 200

# Driver configurations
MICROSTEPPING = 8
NUM_STOPS = 40
STEP_DELAY = 0
STOP_DELAY = 0.015
DELAY_AFTER_ROTATION = 0

MICROSTEPS = {
    1: (GPIO.LOW, GPIO.LOW, GPIO.LOW),
    2: (GPIO.HIGH, GPIO.LOW, GPIO.LOW),
    4: (GPIO.LOW, GPIO.HIGH, GPIO.LOW),
    8: (GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
    16: (GPIO.LOW, GPIO.LOW, GPIO.HIGH),
    32: (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
}


def set_microstep(microstep):
    try:
        GPIO.output((M0_PIN, M1_PIN, M2_PIN), MICROSTEPS[microstep])
    except KeyError:
        raise ValueError(f"Invalid Microstep: {microstep}. " +
                         f"Valid microsteps are: {list(MICROSTEPS.keys())}")


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([DIR_PIN, STEP_PIN, M0_PIN, M1_PIN, M2_PIN, EN_PIN], GPIO.OUT)

    set_direction(CLOCKWISE)
    set_microstep(MICROSTEPPING)


def turn_driver_on(turn_on):
    GPIO.output(EN_PIN, GPIO.LOW if turn_on else GPIO.HIGH)


def rotate(num_steps):
    for _ in range(num_steps * MICROSTEPPING):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        sleep(STEP_DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        sleep(STEP_DELAY)


def set_direction(direction):
    GPIO.output(DIR_PIN, direction)


if __name__ == '__main__':
    try:
        setup()
        turn_driver_on(True)
        while True:
            set_direction(CLOCKWISE)
            for i in range(NUM_STOPS):
                rotate(FULL_ROTATION // NUM_STOPS)
                sleep(STOP_DELAY)

            set_direction(COUNTERCLOCKWISE)
            rotate(FULL_ROTATION)
            sleep(DELAY_AFTER_ROTATION)
    finally:
        turn_driver_on(False)
        GPIO.cleanup()
