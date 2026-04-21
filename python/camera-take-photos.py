import time
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2, Preview
#from picamera2.previews import Preview
import os, sys, termios, tty


# --- Camera Settings ---
EXPOSURE_TIME   = 10000  # microseconds (min: 1, max: 66666)
ANALOGUE_GAIN   = 1.0    # 1.0 to 16.0
BRIGHTNESS      = 0.0    # -1.0 to 1.0 (0.0 = default)
CONTRAST        = 1.0    # 0.0 to 32.0 (1.0 = default)
SATURATION      = 1.0    # 0.0 to 32.0 (1.0 = default) -- if supported
SHARPNESS       = 1.0    # 0.0 to 16.0 (1.0 = default)
NOISE_REDUCTION = 0      # 0=Off, 1=Fast, 4=HighQuality

CAPTURE_KEY="g"
QUIT_KEY="q"
def read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1) # the single key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        
    return
    

# Create a folder named by the current date/time
folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(folder_name)
output_dir.mkdir(parents=True, exist_ok=True)
print(f"Saving images to: {output_dir}")

# init camera
picam2 = Picamera2()
#picam2.configure(picam2.create_still_configuration())

# show preview
cfg = picam2.create_preview_configuration(main={"size" : (1280, 800)})
picam2.configure(cfg)
picam2.start_preview(Preview.QT)
picam2.start()
time.sleep(5)  # warmup

print(f"Preview on. Press `{CAPTURE_KEY}` to capture, `{QUIT_KEY}` to quit")
i = 0

try:
    while True:
        k = read_key()
        
        if k == "\x03":
            raise KeyboardInterrupt
            
        if k == QUIT_KEY:
            break
            
        if k == CAPTURE_KEY:
            i += 1
            filepath = output_dir / f"image_{i:03d}.png"
            picam2.capture_file(str(filepath))
            print(f"saved to: {filepath}") 
            
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    picam2.stop()
    picam2.stop_preview()
    picam2.close()
    print("Done!")
