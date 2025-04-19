import time
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
import serial
import pynmea2
import threading
import re 

# Configure serial port
SERIAL_PORT = 'COM10'
BAUD_RATE = 460800
# gpsSerial = serial.Serial(port='COM11', baudrate=460800, timeout=1)

# Setup Serial
# steerArduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)
brakeArduino = serial.Serial(port='COM6', baudrate=115200, timeout=1)
# relayArduino = serial.Serial(port='COM7', baudrate=115200, timeout=1)
# sonarArduino = serial.Serial(port='COM11', baudrate=115200, timeout=1)



# Map image bounds
MAP_BOUNDS = {
    'min_lat': 42.247728,
    'max_lat': 42.250253,
    'min_lon': -83.621026,
    'max_lon': -83.618467
}

"""________________________________________________GUI________________________________________________"""
# Initialize the main window
root = Tk()
root.title("GPS Map Viewer")
# Make window full screen
root.state("zoomed")

# Create a frame for the image
my_label = LabelFrame(root)
my_label.pack(pady=20)

# Load and resize map image
# Keep a copy of the original image
original_map_image = Image.open("images/Sill_Hall2.jpg")
map_width, map_height = original_map_image.size
map_photo = ImageTk.PhotoImage(original_map_image)

#Game Above Image
# Load and resize the image
game_above_image = Image.open("images/EMU_GameAbove2.jpg")
game_above_image = game_above_image.resize((250, 150))

# Convert to Tkinter-compatible image
game_above_photo = ImageTk.PhotoImage(game_above_image)
# Create a label for the image
game_above_label = Label(root, image=game_above_photo)
game_above_label.image = game_above_photo  # Keep a reference
# Place in the lower-right corner
game_above_label.place(relx=1.0, rely=1.0, anchor="se", x=-50, y=-20)

# Create a label to display the image
map_label = Label(my_label, image=map_photo)
map_label.pack()

# Label to display clicked coordinates
coords_label = Label(root, text="Click on the map to see coordinates", font=("Arial", 12))
coords_label.place(relx=0.0, rely=1.0, anchor="sw", x=30, y=-50)

# GPS update control flag
gps_running = False
gps_lock = threading.Lock()

# List to hold GPS points (latitude, longitude)
gps_path = []

# Create a frame for speed
speed_frame = Frame(root, bg="lightgray", padx=30, pady=25)
speed_frame.place(x=50, y=350)

# Create the speed label inside the frame
speed_label = Label(speed_frame, text="Speed: 0.0 mph", font=("Arial", 14), bg="lightgray", fg="black")
speed_label.pack()

# Create a frame for current GPS coordinates
coords_frame = Frame(root, bg="lightgray", padx=56, pady=25)
coords_frame.place(x=50, y=475)

# Create a label inside the frame to show live GPS coordinates
gps_coords_label = Label(coords_frame, text="Lat: ---\n Lon: ---", font=("Arial", 14), bg="lightgray", fg="black")
gps_coords_label.pack()

# Battery Display Frame
battery_frame = Frame(root, bg="lightgray", padx=25, pady=15)
battery_frame.place(x=50, y=620)

battery_width = 160
battery_height = 30

battery_canvas = Canvas(battery_frame, width=battery_width + 10, height=battery_height)
battery_canvas.pack()

# Draw battery outline
battery_canvas.create_rectangle(0, 0, battery_width, battery_height, outline='black')
battery_canvas.create_rectangle(battery_width, battery_height // 3, battery_width + 10, 2 * battery_height // 3, fill='black')

battery_label = Label(battery_frame, text="0%", font=("Arial", 12), bg="lightgray", fg="black")
battery_label.pack()

"""______________________________________FUNCTIONS_________________________________________"""
### Read battery level from serial and update battery canvas ###
def monitor_battery_level():
    try:
        ser = serial.Serial('com7', 115200, timeout=1)
        print("Connected to serial for battery monitoring.")

        while True:
            # line = ser.readline().decode('utf-8', errors='ignore').strip()
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
            if line.startswith("Battery level: "):
                try:
                    battery_percent = float(line.split(":")[1].strip())
                    update_battery_canvas(battery_percent)
                except (IndexError, ValueError):
                    battery_percent = None
                    update_battery_canvas(battery_percent)

            # if "Battery level: " in line:
            #     match = re.search(r"Battery level:\s*([\d.]+)", line)
            #     if match:
            #         try:
            #             percent = float(match.group(1))
            #             percent = max(0, min(100, int(percent)))  # Clamp between 0–100
            #             update_battery_canvas(percent)
            #         except ValueError:
            #             print("Invalid battery value:", match.group(1))
            time.sleep(0.5)

    except serial.SerialException as e:
        print("Battery monitoring serial error:", e)

### Display battery life ###
def update_battery_canvas(level):
    battery_canvas.delete("charge")
    fill_width = int((level / 100) * (battery_width - 4))
    fill_color = "green" if level > 50 else "orange" if level > 20 else "red"
    battery_canvas.create_rectangle(2, 2, 2 + fill_width, battery_height - 2, fill=fill_color, tags="charge")
    battery_label.config(text=f"{level}%")

### Read GPS data from serial and extract long/lat and speed ###
def parse_nmea():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to", SERIAL_PORT)

        while gps_running:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line.startswith('$'):
                try:
                    msg = pynmea2.parse(line)
                    if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                        lat = round(msg.latitude, 6)
                        lon = round(msg.longitude, 6)
                        speed = round(msg.spd_over_grnd * 1.15078, 2) \
                            if hasattr(msg, 'spd_over_grnd') else 0.0  # Convert knots to mph

                        # Update speed label
                        speed_label.config(text=f"Speed: {speed} mph")
                        #Update coordinates label
                        gps_coords_label.config(text=f"Lat: {lat}, Lon: {lon}")

                        return lat, lon
                except pynmea2.ParseError:
                    print("Parse error:", line)
            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

### Update the map with the GPS point and path ###
def update_map(lat, lon):
    global map_photo, gps_path

    with gps_lock:  # Prevent updating while stopping
        if not gps_running:
            return  # Don't update if GPS is stopped

        # Normalize latitude and longitude to pixel coordinates
        x = ((lon - MAP_BOUNDS['min_lon']) / (MAP_BOUNDS['max_lon'] - MAP_BOUNDS['min_lon'])) * map_width
        y = map_height - ((lat - MAP_BOUNDS['min_lat']) / (MAP_BOUNDS['max_lat'] - MAP_BOUNDS['min_lat'])) * map_height  # Flip y-axis

        # Add new position to path
        gps_path.append((x, y))

        # Draw the GPS position and path
        map_with_point = original_map_image.copy()
        draw = ImageDraw.Draw(map_with_point)

        # Draw path (line between consecutive points)
        if len(gps_path) > 1:
            draw.line(gps_path, fill='blue', width=3)

        # Draw the current GPS position
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill='red')

        map_photo = ImageTk.PhotoImage(map_with_point)
        map_label.configure(image=map_photo)
        map_label.image = map_photo

### Continuously fetch GPS data and update the map ###
def update_gps():
    global gps_running

    while gps_running:
        lat, lon = parse_nmea()
        if not gps_running:  # Double-check before updating
            return
        if MAP_BOUNDS['min_lat'] <= lat <= MAP_BOUNDS['max_lat'] and MAP_BOUNDS['min_lon'] <= lon <= MAP_BOUNDS['max_lon']:
            update_map(lat, lon)
        else:
            print("Coordinates outside map bounds")
        time.sleep(1)

### Start GPS tracking ###
def start_gps():
    global gps_running, gps_thread
    if not gps_running:
        gps_running = True
        gps_thread = threading.Thread(target=update_gps, daemon=True)
        gps_thread.start()
        print("GPS tracking started")

### Stop GPS tracking and reset the map ###
def stop_gps():
    global gps_running, map_photo, gps_path

    with gps_lock:  # Lock to ensure no updates happen while stopping
        gps_running = False  # Signal the update thread to stop

    time.sleep(0.5)  # Small delay to let the update loop exit

    # Reset the map after ensuring no more updates happen
    with gps_lock:
        gps_path.clear()  # Clear the path
        map_photo = ImageTk.PhotoImage(original_map_image)
        map_label.configure(image=map_photo)
        map_label.image = map_photo

    print("GPS tracking stopped and map reset")

### Send the STOP command to the arduino to brake the cart ###
def send_emergency_stop():
    try:
        brakeArduino.write(("CW" + "<" + str(2000) + ">" + '\n').encode())
        print("Emergency STOP command sent.")
        time.sleep(5) #pause for five seconds
        brakeArduino.write(("X" + '\n').encode())
    except:
        print("Failed to send emergency stop!")

### Converts clicked pixel position to lat/long ###
def on_map_click(event):
    x, y = event.x, event.y

    # Convert x, y pixel position to latitude/longitude
    lon = MAP_BOUNDS['min_lon'] + (x / map_width) * (MAP_BOUNDS['max_lon'] - MAP_BOUNDS['min_lon'])
    lat = MAP_BOUNDS['max_lat'] - (y / map_height) * (MAP_BOUNDS['max_lat'] - MAP_BOUNDS['min_lat'])  # Flip y-axis

    coords_label.config(text=f"Chosen Coordinates:\n Lat {lat:.6f}, \nLon {lon:.6f}")
    print(f"Clicked at ({x}, {y}) -> Lat: {lat:.6f}, Lon: {lon:.6f}")

### Adding event listener for mouse click event similar to TkinterMapview ###
def map_click_handler(event):
    on_map_click(event)

# Bind left-click event to the map label
map_label.bind("<Button-1>", map_click_handler)

# Create Start and Stop buttons with larger size and rounded corners
button_frame = Frame(root)
button_frame.pack(pady=10)

"""___________________________________BUTTONS_________________________________________"""

start_button = Button(
    root,
    text="Start GPS",
    command=start_gps,
    bg="#00A6FF",
    fg="white",
    width=15,
    height=4,
    relief="raised",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
start_button.place(x=50, y=50)

stop_button = Button(
    root,
    text="Stop GPS",
    command=stop_gps,
    bg="orange",
    fg="white",
    width=15,
    height=4,
    relief="raised",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
stop_button.place(x=50, y=200)

drive_button = Button(
    root,
    text="Drive",
    command=stop_gps,
    bg="green",
    fg="white",
    width=15,
    height=4,
    relief="raised",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
drive_button.place(x=1260, y=50)

emergency_button = Button(
    root,
    text="EMERGENCY STOP",
    command=send_emergency_stop,
    bg="red",
    fg="white",
    width=15,
    height=4,
    relief="raised",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
emergency_button.place(x=1260, y=200)

# Simulate battery level changes every 5 seconds
# def simulate_battery_drain():
#    import random
#    current = 100
#    def drain():
#        nonlocal current
#        current = max(0, current - random.randint(1, 5))
#        update_battery_canvas(current)
#        if current > 0:
#            root.after(5000, drain)
#    drain()

#simulate_battery_drain()
# battery_thread = threading.Thread(target=monitor_battery_level, daemon=True)
# battery_thread.start()

# Run Tkinter loop
root.mainloop()
