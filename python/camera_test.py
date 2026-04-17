import time
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2

# Create a folder named by the current date/time
folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_dir = Path(folder_name)
output_dir.mkdir(parents=True, exist_ok=True)
print(f"Saving images to: {output_dir}")

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(2)  # warmup

interval = 0.1   # seconds between shots
count = 20     # number of images to capture

for i in range(count):
    filepath = output_dir / f"image_{i:03d}.jpg"
    picam2.capture_file(str(filepath))
    print(f"Captured {filepath}")
    time.sleep(interval)

picam2.stop()
print("Done.")
