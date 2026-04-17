from time import sleep, perf_counter
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2
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
NUM_ROUNDS = 1
STEP_DELAY = 0
STOP_DELAY = 9/256
DELAY_AFTER_ROTATION = 0

MICROSTEPS = {
    1: (GPIO.LOW, GPIO.LOW, GPIO.LOW),
    2: (GPIO.HIGH, GPIO.LOW, GPIO.LOW),
    4: (GPIO.LOW, GPIO.HIGH, GPIO.LOW),
    8: (GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
    16: (GPIO.LOW, GPIO.LOW, GPIO.HIGH),
    32: (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
}

# --- Camera Settings ---
EXPOSURE_TIME   = 10000  # microseconds (min: 1, max: 66666)
ANALOGUE_GAIN   = 1.0    # 1.0 to 16.0
BRIGHTNESS      = 0.0    # -1.0 to 1.0 (0.0 = default)
CONTRAST        = 1.0    # 0.0 to 32.0 (1.0 = default)
SATURATION      = 1.0    # 0.0 to 32.0 (1.0 = default) -- if supported
SHARPNESS       = 1.0    # 0.0 to 16.0 (1.0 = default)
NOISE_REDUCTION = 0      # 0=Off, 1=Fast, 4=HighQuality


def set_microstep(microstep):
    try:
        GPIO.output((M0_PIN, M1_PIN, M2_PIN), MICROSTEPS[microstep])
    except KeyError:
        raise ValueError(f"Invalid Microstep: {microstep}. " +
                         f"Valid microsteps are: {list(MICROSTEPS.keys())}")


def motor_setup():
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
    # Create a folder named by the current date/time
    folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(folder_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving images to: {output_dir}")

    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        # main={"size": (1332,990)},
        # raw={}
    )
    picam2.configure(config)
    picam2.set_controls({
        "AeEnable":           False,
        "ExposureTime":       EXPOSURE_TIME,
        "AnalogueGain":       ANALOGUE_GAIN,
        "Brightness":         BRIGHTNESS,
        "Contrast":           CONTRAST,
        "Sharpness":          SHARPNESS,
        "NoiseReductionMode": NOISE_REDUCTION,
    })
    picam2.start()
    sleep(2)  # warmup
    try:
        motor_setup()
        turn_driver_on(True)
        for r in range(NUM_ROUNDS):
            set_direction(CLOCKWISE)
            for stop in range(NUM_STOPS):
                rotate_start = perf_counter()
                rotate(FULL_ROTATION // NUM_STOPS)
                rotate_end = perf_counter()
                rotate_time = rotate_end - rotate_start
                print(f"Step rotate time: \t{rotate_time * 1000} ms")
                filepath = output_dir / f"image_{r:03d}_{stop:03d}.tiff"
                sleep(STOP_DELAY)
                photo_start = perf_counter()
                picam2.capture_file(str(filepath))
                photo_end = perf_counter()
                photo_time = photo_end - photo_start
                print(f"Photo capture time: \t{photo_time * 1000} ms")
                print(f"Captured {filepath}")

            rotate_start = perf_counter()
            set_direction(COUNTERCLOCKWISE)
            rotate(FULL_ROTATION)
            rotate_end = perf_counter()
            rotate_time = rotate_end - rotate_start
            print(f"Back rotate time: \t{rotate_time * 1000} ms")
            sleep(DELAY_AFTER_ROTATION)
    finally:
        turn_driver_on(False)
        GPIO.cleanup()
        picam2.stop()
        print("Done.")
