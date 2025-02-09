import cv2
import numpy as np

def Preprocessing(frame):
    # Optional: Adjust orientation if needed
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to the grayscale image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection with adjusted thresholds
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imshow("Edges", edges)

    imshape = frame.shape
    # Define a polygon; adjust the vertices as needed for your setup
    vertices = np.array([
        [
            (int(imshape[1] * 0.01), imshape[0]),  # Bottom-left (moved further left)
            (int(imshape[1] * 0.1), int(imshape[0] * 0.3)),  # Top-left (unchanged)
            (int(imshape[1] * 0.9), int(imshape[0] * 0.3)),  # Top-right (unchanged)
            (int(imshape[1] * 0.99), imshape[0])  # Bottom-right (moved further right)
        ]
    ], dtype=np.int32)

    # Inner polygon (blocking out middle)
    """
    inner_vertices = np.array([
        [
            (int(imshape[1] * 0.02), imshape[0]),  # Bottom-left (closer to center)
            (int(imshape[1] * 0.25), int(imshape[0] * 0.3)),  # Top-left (higher up)
            (int(imshape[1] * 0.55), int(imshape[0] * 0.3)),  # Top-right
            (int(imshape[1] * 0.98), imshape[0])  # Bottom-right (closer to center)
        ]
    ], dtype=np.int32)
    """

    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, vertices, 255)
    """ cv2.fillPoly(mask, inner_vertices, 0) """
    masked_edges = cv2.bitwise_and(edges, mask)
    cv2.imshow("Masked Edges", masked_edges)
    
    lines = cv2.HoughLinesP(masked_edges, 
                        rho=6,                    # Increase resolution
                        theta=np.pi/180,          # Keep same angle resolution
                        threshold=80,             # Increase threshold
                        minLineLength=60,         # Increase minimum line length
                        maxLineGap=25)            # Increase max gap
    line_img = frame.copy()
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow("Detected Lines", line_img)

    left_lines, right_lines = [], []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 == x1:  # Skip vertical lines
                continue
            slope = (y2 - y1) / (x2 - x1)
            if slope < -0.3:  # Adjust threshold as needed
                left_lines.append(line[0])
            elif slope > 0.3:
                right_lines.append(line[0])

    def average_line_point(lines):
        if not lines:
            return None
        x_vals = [x1 for (x1, y1, x2, y2) in lines] + [x2 for (x1, y1, x2, y2) in lines]
        return int(np.mean(x_vals))

    left_avg = average_line_point(left_lines)
    right_avg = average_line_point(right_lines)

    if left_avg is not None and right_avg is not None:
        midpoint = (left_avg + right_avg) // 2
        image_center = imshape[1] // 2
    else:
        midpoint = image_center = None

    if midpoint is not None:
        error = image_center - midpoint
        print("Steering Error:", error)
    else:
        error = 0  # or use previous error if available

    annotated = frame.copy()
    if left_avg is not None:
        cv2.circle(annotated, (left_avg, imshape[0]-10), 5, (255, 0, 0), -1)
    if right_avg is not None:
        cv2.circle(annotated, (right_avg, imshape[0]-10), 5, (255, 0, 0), -1)
    if midpoint is not None:
        cv2.circle(annotated, (midpoint, imshape[0]-10), 5, (0, 255, 0), -1)
    cv2.line(annotated, (image_center, imshape[0]), (midpoint, imshape[0]-10), (0, 0, 255), 2)
    cv2.imshow("Annotated", annotated)

    # Return the edges
    return masked_edges  # Return edges instead of blurred

# Open the default webcam
cap = cv2.VideoCapture("Sidewalk POV Walking.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # Adjust as needed
    
    # Preprocess the captured frame
    processed_frame = Preprocessing(frame)
    
    # Display the processed frame (which is now the edges)
    cv2.imshow("Processed Frame", processed_frame)
    
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
