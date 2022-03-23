import json
import struct
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()


SERVER_ADDRESS = ('127.0.0.1', 1339)
key=os.environ.get('SECRET_KEY')
f = Fernet(key)

def send_data(conn, payload, to_encrypt=False):
    '''
    @brief: send payload along with data size and data identifier to the connection
    @args[in]:
        conn: socket object for connection to which data is supposed to be sent
        payload: payload to be sent
    '''
    # serialize payload and encrypt it
    if to_encrypt:
        serialized = json.dumps(payload)
        encrypted = f.encrypt(serialized.encode())
        payload=encrypted

    # send data size and payload
    conn.sendall(struct.pack('>I', len(payload)))
    conn.sendall(payload)
    # print('[SEND]', serialized_payload)


def receive_data(conn, encrypted=False):
    # receive first 4 bytes of data as data size of payload
    data_size = struct.unpack('>I', conn.recv(4))[0]

    # receive payload till received payload size is equal to data_size received
    received_payload = b""
    reamining_payload_size = data_size
    
    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    
    # decrypt the payload if it is encrypted
    if encrypted:
        decrypted = f.decrypt(received_payload)
        print(decrypted)

        payload = json.loads(decrypted)
    else: payload = received_payload
    # print('[RECEIVE]', payload)

    return payload