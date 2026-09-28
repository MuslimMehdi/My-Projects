# Project 0 — Build & Submission Instructions

## 1. Assemble the hardware

Wire the components exactly as follows:

```text
HC-SR04
VCC  -> 5V
GND  -> GND
TRIG -> D7
ECHO -> D8

SERVO
Signal -> D9
VCC    -> 5V or external regulated 5V
GND    -> GND

LEDs
ON        -> D2 through 220–330 Ω resistor
PROXIMITY -> D3 through 220–330 Ω resistor
DANGER    -> D4 through 220–330 Ω resistor

BUZZER
+ -> D5
- -> GND
```

If an external servo supply is used, its ground **must** be connected to Arduino GND.

## 2. Upload firmware

1. Install Arduino IDE.
2. Open `arduino/Project_0.ino`.
3. Select **Arduino Uno**.
4. Select the correct USB port.
5. Upload.
6. Close Serial Monitor before starting Python.

## 3. Install Python dependencies

From the project root:

```bash
python -m pip install -r requirements.txt
```

Recommended Python version: 3.10 or newer.

## 4. Start Project 0

Automatic port detection:

```bash
python python/project0.py
```

Manual port:

```bash
python python/project0.py COM3
```

Linux:

```bash
python python/project0.py /dev/ttyACM0
```

## 5. Verify operation

When the system starts:

- ON LED should remain lit.
- Servo should sweep from approximately 0° to 180° and back.
- Python should show live angle and distance values.
- An object within 50 cm should illuminate PROXIMITY.
- An object at or below 20 cm should illuminate DANGER and activate the buzzer.

## 6. GitHub submission

Recommended repository name:

```text
Project-0-Radar-System
```

Commit the project as-is, including:

```text
arduino/Project_0.ino
python/project0.py
requirements.txt
README.md
INSTRUCTIONS.md
LICENSE
.gitignore
```

Do not commit Python virtual environments, IDE cache files, compiled Python files, or personal serial-port configuration.

## 7. Demonstration checklist

For a project demonstration, show:

1. Hardware assembly.
2. Arduino upload.
3. Project 0 GUI starting.
4. Servo scanning.
5. A target entering the proximity zone.
6. A target entering the danger zone.
7. Physical LEDs changing state.
8. Buzzer activating in danger state.
9. GUI reporting the target angle and distance.
10. GitHub repository containing the source and documentation.
