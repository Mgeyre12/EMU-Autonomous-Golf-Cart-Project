import cv2
import numpy as np
import serial
import time

def average_slope_intercept(lines, side):
    if lines is None:
        return None
    slopes = []
    intercepts = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        if x2 == x1:
            continue  # Avoid division by zero
        slope = (y2 - y1) / (x2 - x1)
        if side == 'left':
            if slope >= -0.5:  # Adjust slope threshold for left lines
                continue
        elif side == 'right':
            if slope <= 0.5:   # Adjust slope threshold for right lines
               continue
        intercept = y1 - slope * x1
        slopes.append(slope)
        intercepts.append(intercept)
    if not slopes:
        return None
    avg_slope = np.mean(slopes)
    avg_intercept = np.mean(intercepts)
    return (avg_slope, avg_intercept)

def make_coordinates(image, line_params, ymax):
    if line_params is None:
        return None
    slope, intercept = line_params
    y1 = ymax
    y2 = int(y1 * 0.6)  # Upper y for drawing the line
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])

def detect_middle_line(edges, frame, width, height):
    # Define a region in the middle of the frame to look for a middle line
    middle_mask = np.zeros_like(edges)
    
    # Define middle region
    mid_x_start = int(width * 0.4)  # 40% from left
    mid_x_end = int(width * 0.6)    # 60% from left
    mid_y_start = int(height * 0.6)  # Starting from 60% down the frame
    mid_y_end = height               # To the bottom of the frame
    
    # Create a mask for the middle region
    cv2.rectangle(middle_mask, (mid_x_start, mid_y_start), (mid_x_end, mid_y_end), 255, thickness=cv2.FILLED)
    
    # Apply mask to get only edges in the middle region
    middle_edges = cv2.bitwise_and(edges, middle_mask)
    
    # Detect lines in the middle region
    middle_lines = cv2.HoughLinesP(middle_edges, 1, np.pi/180, 30, np.array([]), 
                                  minLineLength=40, maxLineGap=20)
    
    # Check if any vertical-ish lines are found in the middle
    has_middle_line = False
    middle_line_strength = 0
    
    if middle_lines is not None:
        for line in middle_lines:
            x1, y1, x2, y2 = line.reshape(4)
            if x2 == x1:
                continue
            slope = abs((y2 - y1) / (x2 - x1))
            
            # Look for more vertical lines (high slope)
            if slope > 2.0:  # More vertical line
                has_middle_line = True
                # Calculate strength based on line length
                line_length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                middle_line_strength += line_length
                
                # Visualize detected middle lines
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
    
    return has_middle_line, middle_line_strength

# Setup Serial
#steerArduino = serial.Serial(port='COM5', baudrate=115200, timeout=1)
# brakeArduino = serial.Serial(port='COM6', baudrate=115200, timeout=1)
# relayArduino = serial.Serial(port='COM7', baudrate=115200, timeout=1)
# sonarArduino = serial.Serial(port='COM11', baudrate=115200, timeout=1)

time.sleep(2)  # wait for steerArduino reset

# Initialize video capture
#cap =  cv2.VideoCapture("Sidewalk_Video/Sill_Test_Lap.mp4")  # Use 0 for webcam or replace with video path
cap =  cv2.VideoCapture("Sidewalk_Video/Sill_Test_Lap.mp4")  # Use 0 for webcam or replace with video path
#cap =  cv2.VideoCapture(0)  # Use 0 for webcam or replace with video path
last_error = 0
totalError = 0

# Add variables for smoothing and error control
count = 0
prev_steering_angles = []  # For smoothing
max_steering_error = 60    # Maximum allowed steering error
frames_without_lines = 0   # Track consecutive frames without line detection
rough_spot_mode = False    # Flag for rough spot handling

while True:
    ret, frame = cap.read()
    if not ret:
        break
    height, width = frame.shape[:2]
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    lowerThresh = 15
    ratio = 2
    edges = cv2.Canny(blur, lowerThresh, lowerThresh, L2gradient = True)

    # Define region of interest (lower half)
    mask = np.zeros_like(edges)  # Create a blank mask

    # Define rectangle coordinates
    x1 = int(width * 0.1)  # Move left edge 10% toward the center
    y1 = int(height * 0.7)  # Top-left corner of rectangle
    x2, y2 = width, height  # Bottom-right corner of rectangle

    # Draw a white rectangle on the mask
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=cv2.FILLED)
    print("x: " + str(x1) + " y: " + str(y1))
    # Apply the mask to the edges
    masked_edges = cv2.bitwise_and(edges, mask)
    
    # Detect if there's a middle line
    has_middle_line, middle_line_strength = detect_middle_line(edges, frame, width, height)
    
    # Display middle line status
    if has_middle_line:
        cv2.putText(frame, f"Middle Line: YES (Strength: {middle_line_strength:.1f})", 
                   (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    else:
        cv2.putText(frame, "Middle Line: NO", 
                   (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, np.array([]), minLineLength=50, maxLineGap=30)

    # Create a blank image (or use the original image if available)
    line_image = np.copy(masked_edges)  # or use original image instead of masked_edges
    line_image = cv2.cvtColor(line_image, cv2.COLOR_GRAY2BGR)  # convert to BGR if it's grayscale

    # Draw lines on the image
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Display the image
    cv2.imshow("Detected Lines", line_image)

    left_lines = []
    right_lines = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            if x2 == x1:
                continue
            slope = (y2 - y1) / (x2 - x1)
            if slope < -0.5:  # Left lane candidates
                left_lines.append(line)
            elif slope > 0.5:  # Right lane candidates
                right_lines.append(line)

    # Average and extrapolate lines
    left_params = average_slope_intercept(left_lines, 'left')
    right_params = average_slope_intercept(right_lines, 'right')
    left_line = make_coordinates(frame, left_params, height)
    right_line = make_coordinates(frame, right_params, height)

    # Calculate midpoint and steering angle
    steering_angle = 0
    desired_center = width // 2  # Ideal center of the lane
    midpoint_x = None
    
    # Track if we found any lines this frame
    lines_detected = (left_line is not None or right_line is not None)
    
    # Check for rough spot conditions
    if not lines_detected and not has_middle_line:
        frames_without_lines += 1
        if frames_without_lines > 10:  # After 10 frames with no lines
            rough_spot_mode = True
    else:
        frames_without_lines = 0
        if lines_detected or has_middle_line:
            rough_spot_mode = False
    
    # Display rough spot mode status
    if rough_spot_mode:
        cv2.putText(frame, "ROUGH SPOT MODE", (width//2-150, height//2-30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if left_line is not None and right_line is not None:
    # Both lanes detected, use actual midpoint
        left_x_bottom = left_line[0]
        right_x_bottom = right_line[0]
        midpoint_x = (left_x_bottom + right_x_bottom) // 2
    elif left_line is not None:
    # Only left lane detected, estimate right lane
        left_x_bottom = left_line[0]
        estimated_right_x = left_x_bottom + width // 3  # Assume right lane at 1/3 width
        midpoint_x = (left_x_bottom + estimated_right_x) // 2
    elif right_line is not None:
        # Only right lane detected, estimate left lane
        right_x_bottom = right_line[0]
        estimated_left_x = right_x_bottom - width // 3  # Assume left lane at 1/3 width
        midpoint_x = (right_x_bottom + estimated_left_x) // 2
    
    if midpoint_x is not None:
        midpoint_y = height
        
        # Draw a vertical line from the midpoint up the frame
        line_top_y = int(height * 0.6)  # Match the height of lane lines
        if left_line is not None and right_line is not None:
          cv2.line(frame, (midpoint_x, midpoint_y), (midpoint_x, line_top_y), (0, 255, 0), 3)

        # PID Controller
        Kp = 0.1   # Proportional gain
        Ki = 0.01  # Integral gain
        Kd = 0.1   # Derivative gain
        
        # Increase PID gains in rough spot mode for quicker recovery
        if rough_spot_mode:
            Kp *= 1.5  # Increase proportional gain for faster response
            Kd *= 2.0  # Increase derivative gain to respond to rapid changes
        
        # Calculate error from desired center
        error = (desired_center - midpoint_x)
        
        # Limit error to prevent extreme values
        error = max(min(error, max_steering_error), -max_steering_error)
        
        changeError = error - last_error  # derivative term
        totalError += error               # accumulate errors for integral term
        
        # Prevent integral windup
        totalError = max(min(totalError, 100), -100)
        
        steering_angle = (Kp * error) + (Ki * totalError) + (Kd * changeError)  # total gain
        last_error = error

        # Apply smoothing to avoid sudden changes
        if abs(steering_angle) < 5:
          steering_angle = 0
    else:
        # If no lanes detected, keep previous steering but reduce it faster
        decay_rate = 0.8  # Normal decay
        if rough_spot_mode:
            decay_rate = 0.5  # Faster decay in rough spots
        
        steering_angle *= decay_rate  # Gradually return to 0
    
    # If middle line is detected, bring steering back to zero more aggressively
    if has_middle_line:
        # More aggressive correction based on middle line strength
        decay_factor = min(0.95, middle_line_strength / 300)  # Increased from 0.8 to 0.95, decreased divisor
        
        # Reset integral error when middle line is detected
        totalError = 0
        
        # Apply strong correction to steering angle
        steering_angle = steering_angle * (1 - decay_factor)
        
        # Visual feedback
        cv2.putText(frame, "CENTERLINE: CORRECTING", (width//2-150, height//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    # Apply smoother steering by averaging with previous values
    prev_steering_angles.append(steering_angle)
    if len(prev_steering_angles) > 3:  # Keep last 3 values
        prev_steering_angles.pop(0)
    
    # Calculate weighted average (more weight to recent values)
    if len(prev_steering_angles) > 1:
        # In rough spots, use less smoothing
        if rough_spot_mode or has_middle_line:
            # More weight to current value (faster response)
            weights = [0.2, 0.3, 0.5][:len(prev_steering_angles)]
        else:
            # Normal smoothing
            weights = [0.2, 0.3, 0.5][:len(prev_steering_angles)]
        
        steering_angle = sum(a*w for a,w in zip(prev_steering_angles, weights)) / sum(weights)

    # Limit the maximum steering angle
    steering_angle = max(min(steering_angle, 30), -30)  # Clamp steering to avoid extreme values

    # count += 1
    # if count > 2:
    #     count = 0
    #     command = str(abs(steering_angle*1))
    #     if steering_angle < 0 and abs(steering_angle) > 1:
    #         command = ("L" + "<" + command + ">")
    #     elif steering_angle > 0 and abs(steering_angle) > 1:
    #         command = ("R" + "<" + command + ">") 
    #     if command:
    #         steerArduino.write((command + '\n').encode())
    #         #print("Sending to steerArduino:", command)

    # Draw detected lines
    if left_line is not None:
        x1, y1, x2, y2 = left_line.astype(int)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
    if right_line is not None:
        x1, y1, x2, y2 = right_line.astype(int)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)

    # Display steering angle
    cv2.putText(frame, f"Steering: {steering_angle:.2f}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show frames
    cv2.imshow('Frame', frame)
    cv2.imshow('Edges', edges)

    if cv2.waitKey(60) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()