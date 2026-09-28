# Project 0 — Technical Project Summary

## Objective

Project 0 demonstrates a complete embedded-to-desktop sensing pipeline using an Arduino Uno R3 and an HC-SR04 ultrasonic sensor mounted to a small servo. The sensor scans a 180° field and transmits angle, distance, and classification data to a Python application over USB serial.

## System architecture

```text
HC-SR04 ──> Arduino Uno ──USB Serial──> Python / PySide6
              │                            │
              ├── Servo                    ├── Radar display
              ├── ON LED                   ├── Object table
              ├── Proximity LED            ├── Serial log
              ├── Danger LED               ├── Angle graph
              └── Buzzer                   └── Scan visualization
```

## State machine

```text
                 distance > 50 cm
              ┌────────────────────┐
              │                    ▼
          ┌───────┐           ┌─────────┐
          │ CLEAR │           │PROXIMITY│
          └───┬───┘           └────┬────┘
              │                     │
              │ distance <= 50      │ distance <= 20
              └─────────────────────┘
                         │
                         ▼
                      DANGER
```

The implementation uses three independent physical indicators: system power/running state, proximity state, and danger state. The active buzzer is reserved for danger.

## Serial protocol

The protocol is intentionally simple so it can be inspected with a serial terminal and reproduced by other software:

```text
92,34.7,PROXIMITY
```

Fields are:

1. Servo angle in degrees.
2. Distance in centimeters; `-1` means no valid echo.
3. State string: `CLEAR`, `PROXIMITY`, or `DANGER`.

## Engineering considerations

- HC-SR04 echo reads have a timeout to prevent an absent echo from blocking indefinitely.
- The Python serial port uses a short timeout so GUI reads do not hang.
- Hardware alarm logic runs on the Arduino rather than depending on the desktop GUI.
- Servo movement is scheduled with `millis()` rather than long blocking delays.
- GUI rendering is separated from serial acquisition.

## Limitations

This is an ultrasonic scanning system rather than electromagnetic radar. The scan reconstructs a 2D angular map from sequential measurements. The GUI's point-cloud panel is a visual representation of the scan and is not a true 3D measurement system.
