from packet import Packet
from jitterbuffer import JitterBuffer
from voip_send import VOIP_Sender
from voip_receive import VOIP_Receiver
import threading
import time
from rec_sound import live_capture
from network_sim import network_sim
import argparse


def main(ip, proxy_port, receiver_port):

    """
    Tests the VOIP connection from VOIP sender to VOIP receiver using the network sim and jitter buffer

    params:
        ip: IP of the network
        proxy_port: port of the proxy connection
        receiver: prot of the receiver connection
    """
    
    #intializes VOIP Sender, VOIP receiver and stars the connection over the network sim
    proxy_port = args.proxy_port
    receiver_port = args.receiver_port
    sender = VOIP_Sender(ip, proxy_port)
    receiver = VOIP_Receiver(ip, receiver_port)
    threading.Thread(target=network_sim, args=(proxy_port, ip, receiver_port, 0, 0, 0), daemon=True).start()

    threading.Thread(target=receiver.receive_audio, daemon=True).start()

    #checks for intterupts in the connection, if interrupt is detected audio is saved
    try:
        for audio_chunk in live_capture(8000):
                sender.send_audio(audio_chunk)
                
    except KeyboardInterrupt:
        print("Stopping VOIP test...")
        sender.save_audio()
        receiver.save_audio()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VOIP Test")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="Ip")
    parser.add_argument("--proxy-port", type=int, default=12347, help="Proxy port")
    parser.add_argument("--receiver-port", type=int, default=12346, help="Receiver port")
    args = parser.parse_args()
    main(args.ip, args.proxy_port, args.receiver_port)