import cv2 as cv
import time

def record_video(duration, filename="output.avi", fps=20.0, frame_size=(640, 480)):
    cap = cv.VideoCapture(0)
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    out = cv.VideoWriter(filename, fourcc, fps, frame_size)

    print("Recording video...")
    start = time.time()

    while time.time() - start < duration:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video")
            break
        out.write(frame)    

    cap.release()
    out.release()
    print(f"Video saved to {filename}")
