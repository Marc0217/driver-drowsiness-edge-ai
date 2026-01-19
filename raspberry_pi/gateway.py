import serial
import time
import json
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion

# -------------------- CONFIG --------------------
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200
MQTT_BROKER = "localhost"

DROWSY_THRESHOLD = 3     # number of detections
WINDOW_SECONDS = 5       # time window (seconds)

# -------------------- STATES --------------------
STATE_NORMAL = "NORMAL"
STATE_DROWSY = "DROWSY"
STATE_ALARM = "ALARM_ACTIVE"

state = STATE_NORMAL
drowsy_events = []

# -------------------- SERIAL INIT ----------------
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(4)  # allow Arduino reset

# -------------------- MQTT CALLBACK --------------
def on_message(client, userdata, msg):
    global state, drowsy_events

    payload = msg.payload.decode().strip()
    now = time.time()

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return

    if msg.topic == "detector/drowsy" and data.get("event") == "drowsy":
        drowsy_events.append(now)

        # keep only events inside the time window
        drowsy_events[:] = [
            t for t in drowsy_events if now - t <= WINDOW_SECONDS
        ]

        print(f"Drowsy events detected: {len(drowsy_events)}")

        if state == STATE_NORMAL and len(drowsy_events) >= DROWSY_THRESHOLD:
            print(">>> STATE CHANGE: NORMAL → ALARM_ACTIVE")
            state = STATE_ALARM
            ser.write(b"DROWSY\n")

# -------------------- MQTT CLIENT ----------------
client = mqtt.Client(
    client_id="edge_gateway",
    callback_api_version=CallbackAPIVersion.VERSION2
)

client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe("detector/drowsy")
client.loop_start()

print(" Edge gateway started")

# -------------------- MAIN LOOP ------------------
try:
    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors="ignore").strip()

            if line == "ACK" and state == STATE_ALARM:
                print(">>> STATE CHANGE: ACKNOWLEDGED → NORMAL")

                state = STATE_NORMAL
                drowsy_events.clear()

                ack_msg = {
                    "event": "ack",
                    "timestamp": int(time.time())
                }

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n Gateway stopped by user")

finally:
    ser.close()
    print(" Serial connection closed")
