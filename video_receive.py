import socket
import cv2 as cv
import numpy as np
import threading
from packet import Packet

class Video_Receiver:
    def __init__(self, listen_ip, listen_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((listen_ip, listen_port))
        self.frames = {}       # frame_id -> {frag_index: data}
        self.latest_frame = None
        self.lock = threading.Lock()

    def receive(self):
        threading.Thread(target=self.listen, daemon=True).start()
        self.display()

    def listen(self):
        print(f"Listening for video on port {self.socket.getsockname()[1]}...")
        while True:
            try:
                raw_bytes, _ = self.socket.recvfrom(2048)
                frame_id, frag_index, flags, payload, is_corrupt = Packet.unpack(raw_bytes)

                if is_corrupt:
                    continue

                if frame_id not in self.frames:
                    self.frames[frame_id] = {}
                self.frames[frame_id][frag_index] = payload

                if flags == 1:
                    frame_data = self.frames.pop(frame_id)
                    assembled = b''.join(frame_data[i] for i in sorted(frame_data))

                    with self.lock:
                        self.latest_frame = assembled

                    stale = [fid for fid in self.frames if frame_id - fid > 5]
                    for fid in stale:
                        del self.frames[fid]

            except Exception as e:
                print(f"Receive error: {e}")

    def display(self):
        while True:
            with self.lock:
                frame = self.latest_frame

            if frame:
                img = cv.imdecode(
                    np.frombuffer(frame, dtype=np.uint8),
                    cv.IMREAD_COLOR
                )
                if img is not None:
                    cv.imshow('Video', img)

            # q to quit
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()