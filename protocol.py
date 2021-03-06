import json
import socket
import struct
from cryptography.fernet import Fernet

#Handle address
def get_address(local=False):
    PORT = 8000
    
    if local:
        return ('127.0.0.1', PORT)
    else: # do a little trick to get LAN address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('8.8.8.8', 80))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return (IP,PORT)

#Handle data
def send_data(conn, payload, key=None):
    # Serialize payload and encrypt it
    if key:
        f = Fernet(key)
        serialized = json.dumps(payload)
        encrypted = f.encrypt(serialized.encode())
        payload = encrypted

    # Send data size and payload
    conn.sendall(struct.pack('>I', len(payload)))
    conn.sendall(payload)


def receive_data(conn, key=None):
    # Receive first 4 bytes of data as data size of payload
    data_size = struct.unpack('>I', conn.recv(4))[0]

    # Receive payload till received payload size is equal to data_size received
    received_payload = b""
    reamining_payload_size = data_size

    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)

    # Decrypt the payload if it is encrypted
    if key:
        f = Fernet(key)
        decrypted = f.decrypt(received_payload)
        print(decrypted)

        payload = json.loads(decrypted)
    else:
        payload = received_payload

    return payload