import cv2

def list_available_cameras(max_index=5):
    available = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap is None or not cap.isOpened():
            print(f"Camera index {index} is not available.")
        else:
            print(f"Camera index {index} is available!")
            available.append(index)
            cap.release()
    return available

if __name__ == "__main__":
    cams = list_available_cameras(5)
    print(f"Available camera indexes: {cams}")
