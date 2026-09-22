import heapq
import threading


class JitterBuffer:
    """
    Buffer built for the VOIP connectio, ignores small errors instead of resending packets
    """
    def __init__(self, max_size=250):
        """
        Jitter Buffer intialization

        params:
            max_size: Max number of audio packets within buffer before timeout
        """
        self.buffer = []
        self.max_size = max_size
        self.lock = threading.Lock()

    def add_packet(self, seq_num, payload):
        """
        adds audio data to the jitter buffer

        params:
            seq_num: number of the packet in sequence
            payload: the audio data itself
        """
        with self.lock:
            if len(self.buffer) < self.max_size:
                heapq.heappush(self.buffer, (seq_num, payload))
            else:
                print("Jitter buffer is full. Packet dropped.")

    def get_next_packet(self):
        """
        returns the next packet in the buffer
        """
        with self.lock:
            if self.buffer:
                return heapq.heappop(self.buffer)[1]
            else:
                return None