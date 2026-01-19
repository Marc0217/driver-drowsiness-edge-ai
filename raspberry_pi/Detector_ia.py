import subprocess
import serial
import time
import numpy as np
import sys
import requests
import os

# -------------------- SERIAL CONFIG --------------------
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

# -------------------- CAMERA CONFIG --------------------
WIDTH = 640
HEIGHT = 480
FPS = 10

# -------------------- DROWSINESS CONFIG ----------------
DROWSY_TIME = 3.0          # seconds without motion
MOTION_THRESHOLD = 10.0    # motion sensitivity

# -------------------- THINGSPEAK -----------------------
THINGSPEAK_API_KEY = os.getenv("THINGSPEAK_API_KEY")

# -------------------- SERIAL INIT ----------------------
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
    time.sleep(2)
    print("✔ Serial connected to Arduino")
except Exception as e:
    print("❌ Serial error:", e)
    sys.exit(1)

# -------------------- CAMERA INIT ----------------------
Y_SIZE = WIDTH * HEIGHT
FRAME_SIZE = int(Y_SIZE * 1.5)

cmd = [
    "rpicam-vid",
    "-t", "0",
    "--width", str(WIDTH),
    "--height", str(HEIGHT),
    "--framerate", str(FPS),
    "--codec", "yuv420",
    "--nopreview",
    "-o", "-"
]

try:
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10**8)
except Exception as e:
    print("❌ Error launching camera:", e)
    sys.exit(1)

print("📷 Camera started")
print("🧠 Edge AI detector running")

prev_y = None
still_since = None
alarm_sent = False
drowsy_count = 0

# -------------------- MAIN LOOP ------------------------
try:
    while True:
        data = proc.stdout.read(FRAME_SIZE)
        if len(data) < FRAME_SIZE:
            continue

        y = np.frombuffer(
            data[:Y_SIZE], dtype=np.uint8
        ).reshape((HEIGHT, WIDTH))

        if prev_y is not None:
            diff = np.mean(
                np.abs(
                    y.astype(np.int16) - prev_y.astype(np.int16)
                )
            )

            if diff < MOTION_THRESHOLD:
                if still_since is None:
                    still_since = time.time()

                elif (time.time() - still_since) >= DROWSY_TIME and not alarm_sent:
                    drowsy_count += 1
                    print("⚠️ DROWSY DETECTED → Arduino + ThingSpeak")

                    # Send to Arduino
                    ser.write(b"DROWSY\n")

                    # Send to ThingSpeak
                    if THINGSPEAK_API_KEY:
                        url = (
                            "https://api.thingspeak.com/update"
                            f"?api_key={THINGSPEAK_API_KEY}"
                            f"&field1={drowsy_count}"
                            f"&field2={diff:.2f}"
                        )
                        try:
                            r = requests.get(url, timeout=5)
                            if r.status_code == 200:
                                print("📡 ThingSpeak updated")
                            else:
                                print("⚠️ ThingSpeak error:", r.status_code)
                        except Exception as e:
                            print("❌ ThingSpeak request failed:", e)

                    alarm_sent = True
            else:
                still_since = None

        prev_y = y

        # ----------- READ ARDUINO ACK -------------------
        if ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()
            if line == "ACK":
                print("✅ ACK received → system reset")
                still_since = None
                alarm_sent = False

except KeyboardInterrupt:
    print("\n⏹️ Stopped by user")

finally:
    proc.terminate()
    ser.close()
    print("🔌 Closed correctly")
