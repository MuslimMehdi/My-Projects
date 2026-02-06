import serial
import pyautogui
import time

# Replace 'COM3' with your Arduino COM port
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Give Arduino time to reset

print("Waiting for data...")

while True:
    if arduino.in_waiting:
        data = arduino.readline().decode('utf-8').strip()
        print(f"Received: Successful")
        pyautogui.typewrite(data)
        break  # Stop after one message (remove if you want it to keep listening)
