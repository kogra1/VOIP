import socket
import wave
import pyaudio
from packet import Packet

class VOIP_Sender:
    """
    Object that starts VOIP connection
    """
    def __init__(self, target_ip, target_port):
        """
        Intilization of VOIP Sender object

        Params:
            target_ip: target IP
            target_port: tartget port
        """
        self.target = (target_ip, target_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq = 0
        self.audio = pyaudio.PyAudio()
        self.frames = []

    def send_audio(self, audio_data):
        """
        Sends audio data to receiver

        params:
            audio data: Sound data to be sent to the receiver connection
        """
        packet = Packet.create_packet(self.seq, 0, 0, audio_data)
        self.socket.sendto(packet, self.target)
        self.seq += 1
        self.frames.append(audio_data)

    def save_audio(self, filename="sent_live_audio.wav", sample_rate=8000):
        """
        Saves the audio data and prints it to a .wav file to listen to

        params:
            filename: name of the file audio is being saved to
            sample_rate: sample rate of audio
        """
        with wave.open(filename, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            f.setframerate(sample_rate)
            f.writeframes(b''.join(self.frames))
        print(f"Live audio saved to {filename}")