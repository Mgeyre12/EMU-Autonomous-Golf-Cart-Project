import time
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
import serial
import pynmea2
import threading

# Configure serial port
SERIAL_PORT = 'COM5'
BAUD_RATE = 460800

# Map image bounds
MAP_BOUNDS = {
    'min_lat': 42.247728,
    'max_lat': 42.250253,
    'min_lon': -83.621026,
    'max_lon': -83.618467
}

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
original_map_image = Image.open("Sill_Hall2.jpg")
map_width, map_height = original_map_image.size
map_photo = ImageTk.PhotoImage(original_map_image)

#Game Above Image
# Load and resize the image
game_above_image = Image.open("EMU_GameAbove2.jpg")
game_above_image = game_above_image.resize((300, 200))

# Convert to Tkinter-compatible image
game_above_photo = ImageTk.PhotoImage(game_above_image)
# Create a label for the image
game_above_label = Label(root, image=game_above_photo)
game_above_label.image = game_above_photo  # Keep a reference
# Place in the lower-right corner
game_above_label.place(relx=1.0, rely=1.0, anchor="se", x=-40, y=-20)

# Create a label to display the image
map_label = Label(my_label, image=map_photo)
map_label.pack()

# Label to display clicked coordinates
coords_label = Label(root, text="Click on the map to see coordinates", font=("Arial", 12))
coords_label.place(relx=0.0, rely=1.0, anchor="sw", x=60, y=-30)

# GPS update control flag
gps_running = False
gps_lock = threading.Lock()

# List to hold GPS points (latitude, longitude)
gps_path = []

# Create a frame for speed
speed_frame = Frame(root, bg="lightgray", padx=50, pady=25)
speed_frame.place(x=75, y=350)

# Create the speed label inside the frame
speed_label = Label(speed_frame, text="Speed: 0.0 mph", font=("Arial", 14), bg="lightgray", fg="black")
speed_label.pack()

# Create a frame for current GPS coordinates
coords_frame = Frame(root, bg="lightgray", padx=56, pady=25)
coords_frame.place(x=75, y=475)

# Create a label inside the frame to show live GPS coordinates
gps_coords_label = Label(coords_frame, text="Lat: ---, Lon: ---", font=("Arial", 14), bg="lightgray", fg="black")
gps_coords_label.pack()



def parse_nmea():
    """ Reads GPS data from the serial port and extracts lat/lon and speed. """
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
                        speed = round(msg.spd_over_grnd * 1.15078, 2) if hasattr(msg, 'spd_over_grnd') else 0.0  # Convert knots to mph

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


def update_map(lat, lon):
    """ Updates the map with the GPS point and path. """
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

def update_gps():
    """ Continuously fetch GPS data and update the map. """
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

# Function to start GPS tracking
def start_gps():
    """ Starts the GPS tracking thread. """
    global gps_running, gps_thread
    if not gps_running:
        gps_running = True
        gps_thread = threading.Thread(target=update_gps, daemon=True)
        gps_thread.start()
        print("GPS tracking started")

# Function to stop GPS tracking and reset the map
def stop_gps():
    """ Stops GPS tracking and clears the map. """
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

def on_map_click(event):
    """ Converts clicked pixel position to latitude and longitude. """
    x, y = event.x, event.y

    # Convert x, y pixel position to latitude/longitude
    lon = MAP_BOUNDS['min_lon'] + (x / map_width) * (MAP_BOUNDS['max_lon'] - MAP_BOUNDS['min_lon'])
    lat = MAP_BOUNDS['max_lat'] - (y / map_height) * (MAP_BOUNDS['max_lat'] - MAP_BOUNDS['min_lat'])  # Flip y-axis

    coords_label.config(text=f"Clicked Coordinates: \nLat {lat:.6f}, Lon {lon:.6f}")
    print(f"Clicked at ({x}, {y}) -> Lat: {lat:.6f}, Lon: {lon:.6f}")

# Adding event listener for mouse click event similar to TkinterMapview
def map_click_handler(event):
    """ Handle map left-click event to show the coordinates at the clicked location. """
    on_map_click(event)

# Bind left-click event to the map label
map_label.bind("<Button-1>", map_click_handler)

# Create Start and Stop buttons with larger size and rounded corners
button_frame = Frame(root)
button_frame.pack(pady=10)

# Place Start and Stop buttons in the top-left corner
start_button = Button(
    root,
    text="Start GPS",
    command=start_gps,
    bg="#00A6FF",
    fg="white",
    width=25,
    height=4,
    relief="flat",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
start_button.place(x=50, y=50)  # Explicitly position in the top-left corner

stop_button = Button(
    root,
    text="Stop GPS",
    command=stop_gps,
    bg="orange",
    fg="white",
    width=25,
    height=4,
    relief="flat",
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
    width=25,
    height=4,
    relief="flat",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
drive_button.place(x=1165, y=50)

emergency_button = Button(
    root,
    text="EMERGENCY STOP",
    command=stop_gps,
    bg="red",
    fg="white",
    width=25,
    height=4,
    relief="flat",
    font=("Arial", 14, "bold"),
    bd=5,
    highlightthickness=0
)
emergency_button.place(x=1165, y=200)

# Run Tkinter loop
root.mainloop()
