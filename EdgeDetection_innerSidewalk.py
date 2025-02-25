import cv2
import numpy as np

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

# Initialize video capture
cap =  cv2.VideoCapture("Sidewalk_Video/SillHall_side_turn.mov")  # Use 0 for webcam or replace with video path

while True:
    ret, frame = cap.read()
    if not ret:
        break
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blur, 50, 150, L2gradient = True)  # Adjust Canny thresholds as needed

    # Define region of interest (lower half)
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (0, height),
        (width, height),
        (width, height // 2),
        (0, height // 2),
    ]], dtype=np.int32)
    cv2.fillPoly(mask, polygon, 255)
    masked_edges = cv2.bitwise_and(edges, mask)

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, np.array([]), minLineLength=50, maxLineGap=30)

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
    if left_line is not None and right_line is not None:
        left_x_bottom = left_line[0]
        right_x_bottom = right_line[0]
        midpoint_x = (left_x_bottom + right_x_bottom) // 2
        midpoint_y = height
        cv2.circle(frame, (midpoint_x, midpoint_y), 10, (0, 255, 0), -1)

        # Calculate error from center
        desired_center = width // 2
        error = desired_center - midpoint_x
        steering_angle = error * 0.1  # Adjust gain for responsiveness

        # Apply threshold to ignore minor adjustments
        if abs(steering_angle) < 10:
            steering_angle = 0
    else:
        steering_angle =  0
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

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()