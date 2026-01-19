# Driver Drowsiness Detection System using Edge AI and IoT

This repository contains the source code for a driver drowsiness detection system
developed as part of an Internet of Things (IoT) academic project.

The system uses Edge Artificial Intelligence (Edge AI) to analyse video data locally
on a Raspberry Pi in order to detect prolonged driver inactivity. When a drowsiness
event is detected, a physical alert is triggered using an Arduino-based alert system.
Drowsiness events are also logged to the cloud for monitoring purposes.

---

## System Overview

The project is composed of three main components:

- **Edge AI Processing (Raspberry Pi)**  
  Captures video frames and performs motion-based analysis locally to detect driver
  inactivity in real time.

- **Gateway and Alert System (Arduino + MQTT)**  
  Manages system state and activates a buzzer and LED when a drowsiness condition
  is confirmed.

- **Cloud Integration (ThingSpeak)**  
  Logs abstract event data for visualisation and analysis without transmitting
  any video data.

This architecture ensures low latency, reduced network dependency, and improved
privacy.

---

## Repository Structure

driver-drowsiness-edge-ai/
├── arduino/
│ └── alert_system.ino
│
├── raspberry_pi/
│ ├── detector_ia.py
│ └── gateway.py
│
└── README.md


---

## Hardware Requirements

- Raspberry Pi 4
- Raspberry Pi Camera Module v2
- Arduino Uno
- LED and resistor
- Buzzer
- Push button
- Breadboard and jumper wires

---

## Software Requirements

- Python 3
- NumPy
- PySerial
- Paho-MQTT
- Requests
- Arduino IDE
- ThingSpeak account

---

## Configuration

### ThingSpeak API Key

For security reasons, the ThingSpeak API key is not stored directly in the source code.
It must be provided as an environment variable before running the Python scripts.

export THINGSPEAK_API_KEY="YOUR_API_KEY"


---

## Usage

### 1. Arduino Setup

1. Open `alert_system.ino` in the Arduino IDE.
2. Upload the sketch to the Arduino Uno.
3. Connect the Arduino to the Raspberry Pi via USB.

### 2. Raspberry Pi Setup

1. Connect the Raspberry Pi Camera Module to the Raspberry Pi using the CSI interface.

2. Install the required Python libraries:

pip3 install numpy pyserial paho-mqtt requests


3. Set the ThingSpeak API key as an environment variable:

export THINGSPEAK_API_KEY="YOUR_API_KEY"


4. Run the Edge AI drowsiness detector:



python3 raspberry_pi/drowsiness_detector.py


5. Run the MQTT gateway responsible for system state and alert management:



python3 raspberry_pi/edge_gateway.py


---

## Privacy and Security

All video processing is performed locally on the Raspberry Pi.
No images or video streams are stored or transmitted externally.

Only high-level event data, such as drowsiness alerts, is sent to the cloud platform.
This design follows data minimisation principles and improves user privacy.

---

## Academic Disclaimer

This project was developed for educational purposes as part of a university
Internet of Things (IoT) module. The source code is provided for academic
use and evaluation only.

---

## License

This project is intended for educational use only.

