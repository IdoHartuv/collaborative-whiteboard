import json
import struct

SERVER_ADDRESS = ('127.0.0.1', 1339)

def send_data(conn, payload):
    '''
    @brief: send payload along with data size and data identifier to the connection
    @args[in]:
        conn: socket object for connection to which data is supposed to be sent
        payload: payload to be sent
    '''
    # serialize payload
    serialized_payload = json.dumps(payload)

    # send data size and payload
    conn.sendall(struct.pack('>I', len(serialized_payload)))
    conn.sendall(bytes(serialized_payload, encoding='utf-8'))
    # print('[SEND]', serialized_payload)


def receive_data(conn):
    '''
    @brief: receive data from the connection assuming that 
        first 4 bytes represents data size,  
        successive bytes of the size 'data size'is payload
    @args[in]: 
        conn: socket object for conection from which data is supposed to be received
    '''
    # receive first 4 bytes of data as data size of payload
    data_size = struct.unpack('>I', conn.recv(4))[0]
    # receive payload till received payload size is equal to data_size received
    received_payload = b""
    reamining_payload_size = data_size

    while reamining_payload_size != 0:
        received_payload += conn.recv(reamining_payload_size)
        reamining_payload_size = data_size - len(received_payload)
    payload = json.loads(received_payload)
    # print('[RECEIVE]', payload)

    return payload