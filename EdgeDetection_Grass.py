import cv2
import numpy as np

def sidewalk_segmentation(frame):
    """
    Return a binary mask where the sidewalk (grey) is white (255) and everything else is black (0).
    Adjust the HSV ranges below to suit your sidewalk color.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # HSV ranges for grey. These are starting values—tweak as needed.
    # Hue: full range (since grey doesn't have a distinct hue)
    # Saturation: low values (grey is unsaturated)
    # Value: depends on brightness of the sidewalk; here 40 to 255 is used as an example.
    lower_grey = (0, 0, 40)
    upper_grey = (179, 50, 255)
    
    mask_sidewalk = cv2.inRange(hsv, lower_grey, upper_grey)
    
    # Optional: Apply morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_sidewalk = cv2.morphologyEx(mask_sidewalk, cv2.MORPH_OPEN, kernel)
    mask_sidewalk = cv2.morphologyEx(mask_sidewalk, cv2.MORPH_CLOSE, kernel)
    
    return mask_sidewalk

def compute_coverage(mask):
    """Compute fraction (0.0 to 1.0) of the mask that is white (detected sidewalk)."""
    total_pixels = mask.shape[0] * mask.shape[1]
    white_pixels = cv2.countNonZero(mask)
    coverage = white_pixels / float(total_pixels)
    return coverage

def main():
    # Open cameras; adjust indices as needed for your system
    left_cam = cv2.VideoCapture(0)
    right_cam = cv2.VideoCapture(1)
    
    # Set the threshold for sidewalk coverage to 80%
    COVERAGE_THRESHOLD = 0.5  # 80% sidewalk coverage

    while True:
        ret_left, frame_left = left_cam.read()
        ret_right, frame_right = right_cam.read()
        
        if not ret_left or not ret_right:
            print("Error capturing from cameras")
            break
        
        # 1. Segment sidewalk in both frames
        mask_left = sidewalk_segmentation(frame_left)
        mask_right = sidewalk_segmentation(frame_right)
        
        # 2. Compute sidewalk coverage for each camera
        coverage_left = compute_coverage(mask_left)
        coverage_right = compute_coverage(mask_right)
        
        # 3. Steering or decision logic based on sidewalk coverage.
        #    Here we print a message if the sidewalk coverage is less than 80%.
        #    You can replace these prints with commands to your motor controller.
        if coverage_left < COVERAGE_THRESHOLD:
            print("Left camera: Less than 80% sidewalk detected → adjust steering (or take action).")
        else:
            print("Left camera: Sufficient sidewalk coverage.")

        if coverage_right < COVERAGE_THRESHOLD:
            print("Right camera: Less than 80% sidewalk detected → adjust steering (or take action).")
        else:
            print("Right camera: Sufficient sidewalk coverage.")
        
        # 4. Debug/Visualization: display the masks
        cv2.imshow("Left Camera Sidewalk Mask", mask_left)
        cv2.imshow("Right Camera Sidewalk Mask", mask_right)

        # Press ESC to exit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    left_cam.release()
    right_cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
