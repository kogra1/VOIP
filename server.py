import socket
import argparse
import struct 
import threading
import time 
from packet import Packet

class Server:
    def __init__(self, server_port, target_ip, target_port, timeout):
        """
        Server intialization:

        params:
            server_port: port the server listens on
            traget_ip: ip of the target client the server will send data to
            target_port: port of the client the server will send data to
            timeout: amount of time in seconds the server waits to get an ACK
        """
        self.target = (target_ip, target_port)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', server_port))

        self.base = 0
        self.next_seq = 0
        self.window_size = 5
        self.timeout = timeout

        self.sent_packets = {}
        self.timer = None
        self.lock = threading.Lock()

        self.bps = 500

        #start listining for connections 
        threading.Thread(target=self.wait_for_acks, daemon=True).start()

    def start_timer(self):
        #helper function to start/restart timer
        if self.timer is not None:
            self.timer.cancel()
        
        self.timer = threading.Timer(self.timeout, self.timeout_action)
        self.timer.start()

    def stope_timer(self):
        #helper function to stop the timer
        if self.timer is not None:
            self.timer.cancel()
    
    def timeout_action(self):
        #function that triggers when a time our occurs
        print("Timeout occured")
        with self.lock:
            if self.base == self.next_seq:
                return
            
            for x in range(self.base, self.next_seq):
                if x in self.sent_packets:
                    self.socket.sendto(self.sent_packets[x], self.target)
        
        self.start_timer()
    
    def send_data(self, payload):
        """
        Sends data payload to the client

        parma:
            payload: current chunk of data being sent to the client
        """
        while self.next_seq >= self.base + self.window_size:
            time.sleep(0.1)

        with self.lock:
            flags = 0
            packet = Packet.create_packet(self.next_seq, 0, flags, payload)

            self.sent_packets[self.next_seq] = packet

            self.socket.sendto(packet, self.target)
            print(f"sent packet {self.next_seq}")

            if self.base == self.next_seq:
                self.start_timer()

            self.next_seq += 1
        
        #Rate limiter
        bits =  len(packet) * 8
        sleep_time =  bits / self.bps
        time.sleep(sleep_time)

    def wait_for_acks(self):
        """
        listens for ACKS being sent from the client
        """
        while True:
            try:
                raw_bytes, addr = self.socket.recvfrom(2048)
                seq_num, ack_num, flags, payload, is_corrupt = Packet.unpack(raw_bytes)

                if not is_corrupt and flags & 0x02:
                    with self.lock:
                        print(f"ACK received from packet {ack_num}")

                        if ack_num >  self.base:
                            self.base =  ack_num + 1

                            received_acks = [a for a in self.sent_packets.keys() if a <self.base]
                            for a in received_acks:
                                del self.sent_packets[a]

                            if self.base == self.next_seq:
                                self.stope_timer()
                            else:
                                self.start_timer()
            except Exception as e:
                print(f"Thread error")
    
    def finish_transfer(self):
        """
        Closes connection with client when transfer is finished
        """
        while self.base < self.next_seq:
            time.sleep(0.5)

            with self.lock:
                final_packet = Packet.create_packet(self.next_seq, 0, 2, b'EOF')
                self.socket.sendto(final_packet, self.target)
                print("sent final packet")

