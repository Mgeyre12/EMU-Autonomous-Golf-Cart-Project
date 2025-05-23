import serial
import time

# Configuration
BAUD_RATE = 115200
MAX_STEPS = 11000
DISTANCE_WINDOW = 5
isApproach = True

# Setup serial connection
try:
    brakeArduino = serial.Serial(port='COM6', baudrate=115200, timeout=1)
    sonarArduino = serial.Serial(port='COM11', baudrate=115200, timeout=1)
    time.sleep(2)  # Allow Arduino or device to initialize
except Exception as e:
    print(f"Failed to connect to serial port: {e}")
    brakeArduino = None
    sonarArduino = None

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

    avg_array = sum(distance_array)/len(distance_array)
    
    if curr <= 5:
        return MAX_STEPS  # Full stop
    
    delta = prev - curr  # Positive = approaching
    # print("Delta: " + str(delta))
    if delta < 0:
        isApproach = False
    else:
        isApproach = True
    rate = max(0.0, min(delta / 3.0, 1.0))
    proximity = max(0.0, min((15 - avg_array) / 10.0, 1.0))
    braking_ratio = rate * proximity
    
    return int(braking_ratio * MAX_STEPS)

# Main loop: listens for raw sonar data from another microcontroller or sensor
if sonarArduino and brakeArduino:
    try:
        while True:
            if sonarArduino.in_waiting > 0:
                Sonar_input = sonarArduino.readline().decode().strip().split()
                raw_data = Sonar_input[0] 
                try:
                    distance = float(raw_data) * 0.0328084 # Convert cm to ft
                    update_distance(distance)
                    # print(distance_array)
                    steps = calculate_steps()
                    
                    # Send calculated steps to the motor Arduino
                    if steps == 0:
                        brakeArduino.write(("X" + '\n').encode())

                    if isApproach or (distance >= 5.0 and distance <= 10.0):
                        brakeArduino.write(f"CW{steps}\n".encode())
                        # print(f"Distance: {distance} ft | Steps CW sent: {steps}")
                    else:
                        brakeArduino.write(f"CC{steps}\n".encode())
                        # print(f"Distance: {distance} ft | Steps CC sent: {steps}")
                    
                    if (distance <= 5.0):
                        brakeArduino.write(("CW" + "<" + str(2000) +"\n").encode())
                    
                    print(f"Distance: {distance} ft")

                except ValueError:
                    print(f"Ignoring invalid data: {raw_data}")
            #time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        sonarArduino.close()
else:
    print("Serial not initialized.")
