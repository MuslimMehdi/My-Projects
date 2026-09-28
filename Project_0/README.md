# Project 0 — Arduino Radar System

Project 0 is a compact 180° scanning proximity radar built around an **Arduino Uno R3**, **HC-SR04 ultrasonic sensor**, **5g servo**, three status LEDs, an active buzzer, and a Python desktop dashboard.

The Arduino performs the time-sensitive hardware work: servo positioning, ultrasonic measurement, state classification, LEDs, and danger alarm. The Python application receives the measurements over USB serial and renders a live HUD-style radar interface.

## Features

- 0–180° servo sweep
- HC-SR04 distance measurement
- Live angle + distance reporting
- CLEAR / PROXIMITY / DANGER classification
- Dedicated physical LEDs:
  - ON — system running
  - PROXIMITY — object within 50 cm but farther than 20 cm
  - DANGER — object at or below 20 cm
- Active buzzer for danger state
- USB serial telemetry at 115200 baud
- Live radar sweep and target points
- Detected-object table
- Serial event log
- Distance-over-angle graph
- Pseudo-3D point-cloud scan panel
- Automatic Arduino-port discovery with manual port override
- No image assets required by the GUI

## Hardware

| Component | Arduino Uno R3 |
|---|---|
| HC-SR04 VCC | 5V |
| HC-SR04 GND | GND |
| HC-SR04 TRIG | D7 |
| HC-SR04 ECHO | D8 |
| 5g servo signal | D9 |
| ON LED | D2 |
| PROXIMITY LED | D3 |
| DANGER LED | D4 |
| Active buzzer + | D5 |
| Active buzzer − | GND |

Use a **220–330 Ω resistor in series with each LED**.

### Servo power

A small 5g servo may work from the Uno's 5V rail, but servos can cause voltage dips. If the board resets or the servo behaves erratically, power the servo from a stable regulated 5V supply and connect that supply's GND to Arduino GND.

## Thresholds

- `> 50 cm` → CLEAR
- `21–50 cm` → PROXIMITY
- `≤ 20 cm` → DANGER
- No valid echo → CLEAR / no target

These values can be changed in `arduino/Project_0.ino`.

## Software

Python 3.10+ is recommended.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Upload `arduino/Project_0.ino` to the Uno using the Arduino IDE.

Then run:

```bash
python python/project0.py
```

To explicitly select a serial port:

```bash
python python/project0.py COM3
```

Linux example:

```bash
python python/project0.py /dev/ttyACM0
```

## Serial protocol

Arduino sends one line per scan:

```text
ANGLE,DISTANCE_CM,STATE
```

Example:

```text
92,34.7,PROXIMITY
```

An invalid/no-echo distance is represented as `-1`.

Startup message:

```text
RADAR,READY,PROJECT_0
```

## Project structure

```text
Project_0/
├── arduino/
│   └── Project_0.ino
├── python/
│   └── project0.py
├── requirements.txt
├── README.md
├── INSTRUCTIONS.md
├── LICENSE
└── .gitignore
```

## Design notes

The project intentionally keeps hardware control on the Arduino rather than depending on the GUI. If the desktop application stops responding, the Arduino can still operate the LEDs and danger buzzer.

The Python interface is a visualization layer, not a safety-critical control system.

The displayed point-cloud panel is a visualization of the 2D ultrasonic scan. It is **not** a true 3D sensor or point cloud.

Likewise, this project is commonly described as a hobby radar, but technically it is a **servo-scanned ultrasonic distance system**. It does not use radio-frequency radar.

## Troubleshooting

### Python cannot find the Arduino

1. Open Arduino IDE → Tools → Port.
2. Note the port assigned to the Uno.
3. Run the program with that port explicitly.

### GUI opens but no data appears

- Confirm the Arduino sketch was uploaded.
- Confirm the selected port.
- Close Arduino Serial Monitor; only one application should own the serial port.
- Confirm baud rate is 115200.

### Arduino resets when the servo moves

Use a separate regulated 5V supply for the servo and connect the grounds together.

### Servo moves but distances are wrong

- Check TRIG/ECHO wiring.
- Keep the HC-SR04 away from vibrating surfaces.
- Make sure the sensor is facing the same direction as the servo mount.
- Avoid very close targets; ultrasonic sensors have a minimum operating distance.

## License

MIT License. See `LICENSE`.
