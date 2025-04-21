import serial
import time

# Configuration
SERIAL_PORT = 'COM3'  # Replace with the appropriate port name
BAUD_RATE = 115200
MAX_STEPS = 11000
DISTANCE_WINDOW = 5

# Setup serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow Arduino or device to initialize
except Exception as e:
    print(f"Failed to connect to serial port: {e}")
    ser = None

# Initialize distance buffer
distance_array = []

def update_distance(new_distance):
    distance_array.append(new_distance)
    if len(distance_array) > DISTANCE_WINDOW:
        distance_array.pop(0)

def calculate_steps():
    if len(distance_array) < 2:
        return 0
    prev = distance_array[-2]
    curr = distance_array[-1]
    
    if curr <= 5:
        return MAX_STEPS  # Full stop
    
    delta = prev - curr  # Positive = approaching
    rate = max(0.0, min(delta / 3.0, 1.0))
    proximity = max(0.0, min((15 - curr) / 10.0, 1.0))
    braking_ratio = rate * proximity
    
    return int(braking_ratio * MAX_STEPS)

# Main loop: listens for raw sonar data from another microcontroller or sensor
if ser:
    try:
        while True:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode().strip()
                try:
                    distance = float(raw_data)
                    update_distance(distance)
                    steps = calculate_steps()
                    
                    # Send calculated steps to the motor Arduino
                    ser.write(f"{steps}\n".encode())
                    print(f"Distance: {distance} ft | Steps sent: {steps}")
                except ValueError:
                    print(f"Ignoring invalid data: {raw_data}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        ser.close()
else:
    print("Serial not initialized.")
