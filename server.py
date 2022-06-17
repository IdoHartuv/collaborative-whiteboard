import socket
import sys
import threading

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet

from protocol import get_address, receive_data, send_data


clients = []
secret_key = Fernet.generate_key()


def broadcast(message, client_except=None):
    for client in clients:
        if client != client_except:
            try:
                send_data(client, message)
            except Exception as e:
                print("[EXCEPTION IN BROADCASTING]", e)


def send_encrypted_secret_key(client):
    # Receive public key from client and return encrypted secret key

    recv = receive_data(client)
    if recv is not None:
        public_key = serialization.load_pem_public_key(
            recv
        )  # Load public key object from received

        encrypted = public_key.encrypt(
            secret_key,
            padding.OAEP(
                # Mask Generation Function
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )  # Optimal Asymmetric Encryption Padding
        )

        send_data(client, encrypted)


def receive(client):
    while True:
        try:
            recv = receive_data(client)
            if recv is not None:
                print('[RECEIVE]', client.getpeername())
                broadcast(recv, client)
            else:
                break
        except Exception as e:
            print("[EXCEPTION IN RECEIVING]", e)
            break

    clients.remove(client)
    client.close()


def wait_for_connection(server):
    while True:
        try:
            client, address = server.accept()
            print(f'Connected with {address}')

            # Receive public key and send encrypted secret key
            send_encrypted_secret_key(client)

            clients.append(client)
            print("[CLIENTS]", len(clients))
            thread = threading.Thread(
                target=receive, args=(client,), daemon=True)
            thread.start()
        except Exception as e:
            print("[EXCEPTION IN CONNECTION]", e)
            break

    print("SERVER CRASHED!")


def main():
    server = socket.socket()

    argv = sys.argv
    
    SERVER_ADDRESS = get_address("--local" in argv or "-L" in argv)
    server.bind(SERVER_ADDRESS)

    server.listen(5)
    print(f"[STARTED] Waiting for connections on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]} ...")
    wait_for_connection(server)
    
    server.close()


if __name__ == '__main__':
    main()
