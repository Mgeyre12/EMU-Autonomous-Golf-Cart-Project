import cv2
import os

def record_video(output_folder, filename="output4.mp4", duration=50
                 , fps=20):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, filename)
    
    cap = cv2.VideoCapture(0)  # Open default camera
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    frame_count = 0
    max_frames = duration * fps
    
    while cap.isOpened() and frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow('Recording...', frame)  # Display the frame while recording
        frame_count += 1
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video saved at: {output_path}")

# Example usage
output_directory = "./recorded_videos"  # Change this to your desired folder
record_video(output_directory)