import socket
import wave
from jitterbuffer import JitterBuffer
from packet import Packet
import pyaudio
import threading
import time

class VOIP_Receiver:
    """Object that receives the VOIP connection"""
    def __init__(self, listen_ip, listen_port):
        """Voip Receiver object
        
        Params:
            listen_ip: target ip
            listen_port: target port
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((listen_ip, listen_port))
        self.jitter_buffer = JitterBuffer()
        self.audio = pyaudio.PyAudio()
        self.player = self.audio.open(format=pyaudio.paInt16, channels=1, rate=8000, output=True)
        self.frames = []

    def receive_audio(self):
        """
        starts listen and play functions as threads
        """
        print("Starting audio reception...")
        threading.Thread(target=self.listen, daemon=True).start()
        threading.Thread(target=self.play_audio, daemon=True).start()
        
    

    def listen(self):
        """
        listend for a connection request from the sender
        """
        print(f"Listening for audio on port {self.socket.getsockname()[1]}...")
        while True:
            raw_bytes, addr = self.socket.recvfrom(2048)
            seq_num, ack_num, flags, payload, is_corrupted = Packet.unpack(raw_bytes)
            if not is_corrupted:
                self.jitter_buffer.add_packet(seq_num, payload)
                self.frames.append(payload)
        
    def play_audio(self):
        """
        plays the live audio being sent from the sender
        """

        while True:
            packet = self.jitter_buffer.get_next_packet()
            self.player.write(packet if packet else b'\x00' * 160)  # Play silence if no packet is available
    
    def save_audio(self, filename="received_live_audio.wav", sample_rate=8000):
        """
        Saves the audio data and prints it to a .wav file to listen to

        params:
            filename: name of the file audio is being saved to
            sample_rate: sample rate of audio
        """
        if not self.frames:
            print("No audio frames to save.")
            return
        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            f.setframerate(sample_rate)
            f.writeframes(b''.join(self.frames))
        print(f"Live audio saved to {filename}")