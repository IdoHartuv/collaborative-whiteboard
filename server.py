import os
import socket
import threading
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from protocol import SERVER_ADDRESS, receive_data, send_data


clients = []


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
            recv,
            backend=default_backend()
        )

        encrypted = public_key.encrypt(
            os.environ.get('SECRET_KEY').encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
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
    server.bind(SERVER_ADDRESS)

    server.listen(5)
    print("[STARTED] Waiting for connections...")
    accept_thread = threading.Thread(
        target=wait_for_connection, args=(server,))
    accept_thread.start()
    accept_thread.join()
    server.close()


if __name__ == '__main__':
    main()
