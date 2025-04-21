import serial
import time
import matplotlib.pyplot as plt
from collections import deque
import matplotlib.animation as animation
import math

# Configuration
BAUD_RATE = 115200
MAX_STEPS = 2000
DISTANCE_WINDOW = 10
steps = 0

# For real-time plotting
distance_history = deque(maxlen=100)
steps_history = deque(maxlen=100)
time_history = deque(maxlen=100)
start_time = time.time()

# Setup serial connection
try:
    #steerArduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)
    #brakeArduino = serial.Serial(port='COM6', baudrate=115200, timeout=1)
    #relayArduino = serial.Serial(port='COM7', baudrate=115200, timeout=1)
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
    if len(distance_array) < 1:
        return 0
    
    curr = distance_array[-1]
    
    # Define parameters for exponential function
    # Start applying brakes at this distance (ft)
    start_braking_distance = 10.0
    # Minimum distance where we want maximum braking
    min_distance = 5.0
    # How aggressive the exponential curve is (higher = more aggressive)
    exponent = 2.5
    
    if curr >= start_braking_distance:
        return 0  # No braking needed yet
    elif curr <= min_distance:
        return MAX_STEPS  # Full braking
    
    # Calculate normalized distance (0 = min_distance, 1 = start_braking_distance)
    normalized_distance = (curr - min_distance) / (start_braking_distance - min_distance)
    
    # Apply exponential curve (1 - x^exponent)
    # This gives higher values as distance decreases
    braking_factor = 1 - (normalized_distance ** exponent)
    
    # Calculate steps based on braking factor
    steps = int(braking_factor * MAX_STEPS)
    
    return steps

# Main loop: listens for raw sonar data from another microcontroller or sensor
if sonarArduino:
    try:
        while True:
            if sonarArduino.in_waiting > 0:
                Sonar_input = sonarArduino.readline().decode().strip().split()
                raw_data = Sonar_input[0] 
                try:
                    distance = float(raw_data) * 0.0328084 # Convert cm to ft
                    update_distance(distance)
                    print(distance_array)
                    Prev_step = steps
                    steps = calculate_steps()      

                    # Update real-time plotting data
                    current_time = time.time() - start_time
                    time_history.append(current_time)
                    distance_history.append(distance)
                    steps_history.append(steps)
                    new_step = 0
                    if steps > Prev_step:
                        #Send calculated steps to the motor Arduino
                        new_step = steps
                        print("CW " + str(steps))
                        #brakeArduino.write(f"CW {steps}\n".encode())
                    else:
                        new_step = Prev_step - steps
                        #print("CC | Prev Step: {Prev_step}" + str(new_step))
                        #brakeArduino.write(f"CC {steps}\n".encode())

                    print(f"Distance: {distance:.2f} ft | Steps sent: {new_step} | CURR Step: {steps}| Prev Step: {Prev_step}")
                except ValueError:
                    print(f"Ignoring invalid data: {raw_data}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped by user.")
        # Plot results after stopping
        plt.figure(figsize=(10, 6))
        plt.plot(time_history, steps_history, label='Braking Steps', color='red')
        plt.xlabel('Time (s)')
        plt.ylabel('Steps')
        plt.title('Braking Steps Over Time')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    finally:
        sonarArduino.close()
else:
    print("Serial not initialized.")
