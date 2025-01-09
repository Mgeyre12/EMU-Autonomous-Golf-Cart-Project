import cv2
import numpy as np

def grass_segmentation(frame):
    """Return a binary mask where grass is white (255) and everything else is black (0)."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Adjust these values to match your grass color
    lower_green = (35, 40, 40)
    upper_green = (85, 255, 255)
    
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    
    # Optional: apply morphological operations to clean noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)
    
    return mask_green

def compute_green_coverage(mask):
    """Compute fraction (0.0 to 1.0) of mask that is white (grass)."""
    total_pixels = mask.shape[0] * mask.shape[1]
    white_pixels = cv2.countNonZero(mask)  # non-zero = white in mask
    coverage = white_pixels / float(total_pixels)
    return coverage

def main():
    left_cam = cv2.VideoCapture(0)   # or whichever index for left camera
    right_cam = cv2.VideoCapture(1)  # or whichever index for right camera
    
    THRESHOLD = 0.2  # Adjust based on testing (20% coverage for example)
    
    while True:
        ret_left, frame_left = left_cam.read()
        ret_right, frame_right = right_cam.read()
        
        if not ret_left or not ret_right:
            break
        
        # 1. Segment grass
        mask_left = grass_segmentation(frame_left)
        mask_right = grass_segmentation(frame_right)
        
        # 2. Measure coverage
        coverage_left = compute_green_coverage(mask_left)
        coverage_right = compute_green_coverage(mask_right)
        
        # 3. Steering logic
        if coverage_left > THRESHOLD:
            print("Grass on left side → steer RIGHT.")
            # Send command to your motor controller, e.g., turn right

        if coverage_right > THRESHOLD:
            print("Grass on right side → steer LEFT.")
            # Send command to your motor controller, e.g., turn left

        # Debug/Visualization
        cv2.imshow("Left Camera Mask", mask_left)
        cv2.imshow("Right Camera Mask", mask_right)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    left_cam.release()
    right_cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

