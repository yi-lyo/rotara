"""
This script turns the motor and captures images from the camera for one revolution,
with the timing of the step pulses controlled by an Arduino.
"""

from time import sleep, perf_counter
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# Electrical wiring
TRIG_PIN = 26

# Driver configurations
NUM_STOPS = 40
NUM_ROUNDS = 1
STEP_DELAY = 0
STOP_DELAY = 9/256
DELAY_AFTER_ROTATION = 0

# --- Camera Settings ---
EXPOSURE_TIME   = 10000  # microseconds (min: 1, max: 66666)
ANALOGUE_GAIN   = 1.0    # 1.0 to 16.0
BRIGHTNESS      = 0.0    # -1.0 to 1.0 (0.0 = default)
CONTRAST        = 1.0    # 0.0 to 32.0 (1.0 = default)
SATURATION      = 1.0    # 0.0 to 32.0 (1.0 = default) -- if supported
SHARPNESS       = 1.0    # 0.0 to 16.0 (1.0 = default)
NOISE_REDUCTION = 0      # 0=Off, 1=Fast, 4=HighQuality

def motor_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)

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
        for r in range(NUM_ROUNDS):
            for stop in range(NUM_STOPS):
                GPIO.output(TRIG_PIN, GPIO.HIGH)
                sleep(0.005)
                GPIO.output(TRIG_PIN, GPIO.LOW)
                filepath = output_dir / f"image_{r:03d}_{stop:03d}.tiff"
                sleep(STOP_DELAY)
                photo_start = perf_counter()
                picam2.capture_file(str(filepath))
                photo_end = perf_counter()
                photo_time = photo_end - photo_start
                print(f"Photo capture time: \t{photo_time * 1000} ms")
                print(f"Captured {filepath}")

            rotate_start = perf_counter()
            rotate_end = perf_counter()
            rotate_time = rotate_end - rotate_start
            print(f"Back rotate time: \t{rotate_time * 1000} ms")
            sleep(DELAY_AFTER_ROTATION)
    finally:
        GPIO.cleanup()
        picam2.stop()
        print("Done.")
