import cv2
import numpy as np

def process_frame(frame):
    # Step 1: Preprocessing
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_sidewalk = np.array([0, 0, 200])     # Example thresholds
    upper_sidewalk = np.array([255, 50, 255])
    sidewalk_mask = cv2.inRange(hsv, lower_sidewalk, upper_sidewalk)
    color_filtered = cv2.bitwise_and(frame, frame, mask=sidewalk_mask)
    
    gray = cv2.cvtColor(color_filtered, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Step 2: Edge Detection
    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(blur_gray, low_threshold, high_threshold)
    
    # Step 3: Define ROI
    imshape = frame.shape
    vertices = np.array([[
        (0, imshape[0]),
        (0, int(imshape[0] * 0.6)),
        (imshape[1], int(imshape[0] * 0.6)),
        (imshape[1], imshape[0])
    ]], dtype=np.int32)

    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, vertices, 255)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    # -- DEBUG VISUALIZATIONS --
    # 1. Show the ROI polygon on top of the original frame.
    annotated_roi = frame.copy()
    cv2.polylines(annotated_roi, [vertices], isClosed=True, color=(0, 255, 0), thickness=2)
    cv2.imshow("ROI Visualization", annotated_roi)

    # 2. Show the edges before masking.
    cv2.imshow("Edges (Pre-ROI)", edges)

    # 3. Show the edges after applying the ROI.
    cv2.imshow("Edges (Masked)", masked_edges)
    # ----------------------------------------

    # Step 4: Line Detection via Hough Transform
    rho = 2
    theta = np.pi / 180
    threshold = 30
    min_line_length = 20
    max_line_gap = 1
    lines = cv2.HoughLinesP(masked_edges, rho, theta, threshold,
                            np.array([]), min_line_length, max_line_gap)
    
    if lines is None:
        # If no lines found, return original frame + zero error
        return frame, 0
    
    # Step 5: Classify and Average the Lines
    left_lines = []
    right_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            if x2 == x1:  # avoid division by zero
                continue
            slope = (y2 - y1) / (x2 - x1)
            # Adjust slopes if needed
            if slope < -0.5:
                left_lines.append((x1, y1, x2, y2))
            elif slope > 0.5:
                right_lines.append((x1, y1, x2, y2))
    
    def average_line(lines_list):
        if len(lines_list) == 0:
            return None
        x_coords = []
        y_coords = []
        for x1, y1, x2, y2 in lines_list:
            x_coords += [x1, x2]
            y_coords += [y1, y2]
        avg_x = int(np.mean(x_coords))
        avg_y = int(np.mean(y_coords))
        return (avg_x, avg_y)
    
    left_point = average_line(left_lines)
    right_point = average_line(right_lines)
    
    if left_point is None or right_point is None:
        return frame, 0
    
    # Step 7: Calculate the Midpoint and Error
    midpoint_x = int((left_point[0] + right_point[0]) / 2)
    center_x = imshape[1] // 2
    error = center_x - midpoint_x
    
    # Step 8: Annotate for visualization
    annotated = frame.copy()
    cv2.circle(annotated, (left_point[0], imshape[0] - 10), 5, (0, 0, 255), -1)
    cv2.circle(annotated, (right_point[0], imshape[0] - 10), 5, (0, 0, 255), -1)
    cv2.circle(annotated, (midpoint_x, imshape[0] - 10), 5, (0, 255, 0), -1)
    cv2.line(annotated, (center_x, imshape[0]), (midpoint_x, imshape[0] - 10), (255, 0, 0), 2)
    
    return annotated, error

def main():
    cap = cv2.VideoCapture(0)  # or a video file path
    if not cap.isOpened():
        print("Error: Could not open video capture.")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        annotated_frame, steering_error = process_frame(frame)
        print("Steering Error:", steering_error)
        
        cv2.imshow("Final Annotated Frame", annotated_frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
