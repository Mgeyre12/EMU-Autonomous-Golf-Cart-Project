import serial
import time

ser1 = serial.Serial('com3', 115200) # Replace 'COM3' with real port name 
time.sleep(2) # Give time for serial connection to initialize

while True:
    line = ser1.readline().decode('utf-8').rstrip()
    print(line) 