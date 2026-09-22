import struct
import hashlib


class Packet:

    #defining class variables
    HEADER_FORMAT = 'i i i 16s'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    MAX_PAYLOAD = 1024

    def create_packet(seq_num, ack_num, flags, payload=b''):
        """
        Creates packets that are transferred between the client and server

        params:
            seq_num: current sequence number
            acl_num: current ACK number
            flags: flags triggered during transfer
            payload: data being sent in current packet
        """
        checksum = Packet.checksum(payload)
        header = struct.pack(Packet.HEADER_FORMAT, seq_num, ack_num, flags, checksum)
        return header + payload


    def checksum(data):
        """
        Creates md5 digest which can be usd to detect if bits are courrupted

        params:
            data: current set of data being transferred
        """
        return hashlib.md5(data).digest()
    
    def unpack(raw_bytes):
        """
        unpacks raw bytes being transeferred

        params:
            raw_bytes: raw bytes of data currently in packet
        """
        header = raw_bytes[:Packet.HEADER_SIZE]
        payload = raw_bytes[Packet.HEADER_SIZE:]
        seq_num, ack_num, flags, checksum = struct.unpack(Packet.HEADER_FORMAT, header)

        is_corrupt = Packet.checksum(payload) != checksum
        
        return seq_num, ack_num, flags, payload, is_corrupt

