import socket
import argparse
import threading
import time
import os
from packet import Packet
from client import Client
from server import Server
from network_sim import network_sim

# helper Function to creat files to be transferred
def create_file(file_name, data):
    with open(file_name, "w") as f:
        f.write(data)


def main(ip, client_port, server_port, proxy_port, file_name, data, timeout, loss_rate, corrupt_rate, reorder_rate):
    """
    Main file to test the Data transfer function between a client and server

    Param:
        ip: ip were the data transfer is taking place
        client_port: port of the client requesting data
        server_port: port of the server receiving the request
        proxy_port: port of the proxy server
        file_name: name of the file being transferred
        data: contents of the file being sent
        timeout: Time in seconds the server waits for a response from the client
        loss_rate: chance that data is lost in the transfer (used for testing)
        corrupt_rate: chance that data is corrupted in the transefer (used for testing)
    """

    #starts proxy server
    proxy_thread = threading.Thread(target=network_sim, args=(proxy_port, ip, client_port, loss_rate, corrupt_rate, reorder_rate), daemon=True)
    proxy_thread.start()

    #start clients request
    client_done = threading.Event()
    client = Client(client_port, ip, server_port, client_done)
    client_thread = threading.Thread(target=client.listen, daemon=True)
    client_thread.start()

    time.sleep(1)

    #creates file stored on server
    create_file(file_name, data)

    #starts server contianing requested file
    server = Server(server_port, ip, proxy_port, timeout)


    print("Transferring file...")

    #transfer file in chunks to the client
    with open(file_name, "rb") as f:
        while True:
            chunk = f.read(Packet.MAX_PAYLOAD)
            if not chunk:
                break

            server.send_data(chunk)
    
    # closing connection after transfer is finished
    print('file sent')
    server.finish_transfer()
    client_done.wait(timeout=10)

    print('Transfer complete')

    #File transfer verification

    original_size = os.path.getsize(file_name)
    if os.path.exists('received_data.txt'):
        received_size = os.path.getsize('received_data.txt')

        print(f"original file size {original_size}")
        print(f"received file size {received_size}")

        if original_size == received_size:
            print("File Transfer was a success")
        else:
            print("File sizes do not match")
    else:
        print("file was never received")

            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="simulate network transfer", description="Simulates a file transfer",)
    parser.add_argument('--ip', type=str, default='127.0.0.1')
    parser.add_argument('--client_port', '-cp', type=int, default=12345)
    parser.add_argument('--server_port', '-sp', type=int, default=12346)
    parser.add_argument('--proxy_port', '-pp', type=int, default=12727)
    parser.add_argument('--file_name', '-fn', type=str, default='send_data/test_file.txt')
    parser.add_argument('--data', '-d', type=str, default="This is a test file")
    parser.add_argument('--timeout', '-t', type=int,default=10.0)
    parser.add_argument('--loss_rate', type=float, default=0.0, help='Chance for a packet to be lost')
    parser.add_argument('--corrupt_rate', type=float, default=0.0, help='Chance for a packet to be corrupted')
    parser.add_argument('--reorder_rate', type=float, default=0.0, help='Chance for a packet to arrive out of order ')

    args = parser.parse_args()

    
    main(ip=args.ip, client_port=args.client_port, server_port=args.server_port, proxy_port=args.proxy_port, file_name=args.file_name, 
         data=args.data, timeout=args.timeout, loss_rate=args.loss_rate, corrupt_rate=args.corrupt_rate, reorder_rate=args.reorder_rate)