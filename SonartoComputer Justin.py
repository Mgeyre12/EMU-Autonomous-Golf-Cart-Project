import serial
import time

# Configuration
BAUD_RATE = 115200
MAX_STEPS = 1500
DISTANCE_WINDOW = 5

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
avg_array = 0.0

def update_distance(new_distance):
    distance_array.append(new_distance)
    if len(distance_array) > DISTANCE_WINDOW:
        distance_array.pop(0)

def calculate_steps():
    if len(distance_array) < DISTANCE_WINDOW:
        return 0
    else:
        print(f"Sum: {sum(distance_array)}, Len: {len(distance_array)}")
        avg_array = sum(distance_array)/len(distance_array)
        print(f"Avg Distance: {avg_array}")
        proximity = 1-(avg_array/25)
        braking_ratio = proximity
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
                    if avg_array > 10.0:
                        brakeArduino.write(("X" + '\n').encode())

                    if (avg_array >= 5.0 and avg_array <= 10.0):
                        brakeArduino.write(f"CW{steps}\n".encode())
                        # print(f"Distance: {distance} ft | Steps CW sent: {steps}")
                    else:
                        brakeArduino.write(f"CC{steps}\n".encode())
                        # print(f"Distance: {distance} ft | Steps CC sent: {steps}")
                    
                    if (avg_array < 5.0):
                        brakeArduino.write(("CW" + "<" + str(2000) +"\n").encode())
                    
                    # sonarArduino.flushInput()
                    # sonarArduino.flushOutput()
                    # brakeArduino.flushInput()
                    # brakeArduino.flushOutput()
                    # sonarArduino.flush()
                    # brakeArduino.flush()
                except ValueError:
                    print(f"Ignoring invalid data: {raw_data}")
            #time.sleep(0.1)
    except KeyboardInterrupt:
        brakeArduino.write(("X" + '\n').encode())
        print("Stopped by user.")
    finally:
        brakeArduino.write(("X" + '\n').encode())
        sonarArduino.close()
else:
    print("Serial not initialized.")
