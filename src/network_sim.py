import socket
import random


def network_sim(client_port, target_ip, target_port, loss, corrupt, reorder):
    """
    Simulates a network connection between a client and server.
    Includes data loss check and corrupted data check

    params:
        client_port: port of the connected client
        target_ip: ip of the of the target server
        target_port: port of the target server
        loss: chance for a simulated data loss to be triggerd
        corrupt: chance for a simulated data corruption to occur
        reorder: chance for a simulated reorder to occur
    """

    held_packet = None

    #connects client
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', client_port))

    print(f"connected on port {client_port}")


    sock.settimeout(0.5)

    while True:
        try:
            data, addr = sock.recvfrom(2048)
        except:
            if held_packet is not None:
                print("flushing held packet after timeout")
                sock.sendto(held_packet, (target_ip, target_port))
                held_packet = None
            continue
        

        # sim/test lost packet
        if loss:
            if random.random() < loss:
                print("Packet Dropped")
                continue

        #sim/test corrupt packet
        if corrupt:
            if random.random() < corrupt:
                print("Packet is corupted")

                data = bytearray(data)
                data[-1] = data[-1] ^ 0xFF
                data = bytes(data)
                prox =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                prox.sendto(data, (target_ip, target_port))
                continue
            break
        # Holds to test reorder
        if reorder and random.random() < reorder and held_packet is None:
            print("Packet held for reordering")
            held_packet = data
            continue
                
        
        sock.sendto(data, (target_ip, target_port))

        # sends held packet if out of order
        if held_packet is not None:
            print("Sending held packet out of order")
            sock.sendto(held_packet, (target_ip, target_port))
            held_packet = None

