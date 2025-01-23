import cv2

# Initialize the webcams
cap = cv2.VideoCapture(0)  # Change index if needed
cap2 = cv2.VideoCapture(1) # Change index if needed

# Check if the webcams are opened correctlyq
if not cap.isOpened() or not cap2.isOpened():
    print("Error: Could not open one of the video devices.")
    exit()

# Set video frame width and height (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)


# Capture video feed
while True:
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

    if not ret or not ret2:
        print("Failed to grab frame")
        break
    
    # Display the resulting frames using unique window names
    cv2.imshow('Webcam Feed 1', frame)
    cv2.imshow('Webcam Feed 2', frame2)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcams and close windows
cap.release()
cap2.release()
cv2.destroyAllWindows()
