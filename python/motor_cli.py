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

# Globals for CLI control
CURRENT_MICROSTEPPING = 8
STEP_DELAY = 0.0005  # Default speed

MICROSTEPS = {
    1: (GPIO.LOW, GPIO.LOW, GPIO.LOW),
    2: (GPIO.HIGH, GPIO.LOW, GPIO.LOW),
    4: (GPIO.LOW, GPIO.HIGH, GPIO.LOW),
    8: (GPIO.HIGH, GPIO.HIGH, GPIO.LOW),
    16: (GPIO.LOW, GPIO.LOW, GPIO.HIGH),
    32: (GPIO.HIGH, GPIO.LOW, GPIO.HIGH)
}

def set_microstep(microstep):
    global CURRENT_MICROSTEPPING
    if microstep in MICROSTEPS:
        GPIO.output((M0_PIN, M1_PIN, M2_PIN), MICROSTEPS[microstep])
        CURRENT_MICROSTEPPING = microstep
        print(f"Microstepping set to {microstep}")
    else:
        print(f"Invalid Microstep. Valid: {list(MICROSTEPS.keys())}")

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([DIR_PIN, STEP_PIN, M0_PIN, M1_PIN, M2_PIN, EN_PIN], GPIO.OUT)
    set_microstep(CURRENT_MICROSTEPPING)
    GPIO.output(EN_PIN, GPIO.LOW) # Turn driver ON

def rotate(steps, direction):
    GPIO.output(DIR_PIN, direction)
    total_pulses = abs(steps) * CURRENT_MICROSTEPPING

    print(f"Moving {steps} steps... (Delay: {STEP_DELAY}s)")
    for _ in range(total_pulses):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        sleep(STEP_DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        sleep(STEP_DELAY)

def run_cli():
    global STEP_DELAY
    print("\n--- Stepper Control CLI ---")
    print("m <val> : Set Microstepping (1, 2, 4, 8, 16, 32)")
    print("s <val> : Set Step Delay in seconds (e.g., 0.001)")
    print("r <val> : Rotate (Positive = CW, Negative = CCW)")
    print("q       : Quit")

    while True:
        try:
            user_input = input("\n> ").strip().lower().split()
            if not user_input: continue

            cmd = user_input[0]

            if cmd == 'q':
                break

            elif cmd == 'm':
                set_microstep(int(user_input[1]))

            elif cmd == 's':
                # Update the global delay variable
                new_delay = float(user_input[1])
                if new_delay < 0:
                    print("Delay cannot be negative.")
                else:
                    STEP_DELAY = new_delay
                    print(f"Step delay updated to {STEP_DELAY}s")

            elif cmd == 'r':
                steps = int(user_input[1])
                direction = CLOCKWISE if steps >= 0 else COUNTERCLOCKWISE
                rotate(steps, direction)

            else:
                print("Unknown command.")

        except (ValueError, IndexError):
            print("Error: Invalid input format. Use 'cmd value'.")
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    try:
        setup()
        run_cli()
    finally:
        GPIO.output(EN_PIN, GPIO.HIGH) # Disable driver
        GPIO.cleanup()
