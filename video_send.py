import socket
import cv2 as cv
import time
from packet import Packet

FRAG_SIZE = 1024


class Video_Sender:      
    def __init__(self, target_ip, target_port):
        self.target = (target_ip, target_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.frame_id = 0

    def send_frame(self, frame_data):
        frags = [frame_data[x:x+FRAG_SIZE] for x in range(0, len(frame_data), FRAG_SIZE)]

        for i, frag in enumerate(frags):
            is_last = (i == len(frags) - 1)

            flags = 1 if is_last else 0
            packet = Packet.create_packet(self.frame_id, i, flags, frag)
            self.socket.sendto(packet, self.target)
    
    def stream(self, fps=24):
        cap = cv.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open video capture")
            return

        interval = 1.0 / fps
        last_frame_time = time.time()

        print("Starting video stream...")

        try:
            while True:
                start = time.time()
                ret, frame = cap.read()
                if not ret:
                    continue

                frame = cv.resize(frame, (640, 480))
                
                _, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 50])
                self.send_frame(buffer.tobytes())
                self.frame_id += 1

                elapsed = time.time() - start
                time.sleep(max(0, interval - elapsed))
        finally:
            cap.release()