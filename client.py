import sys
import socket

from paint import Paint
from protocol import get_address, receive_data, send_data

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

WIDTH, HEIGHT = 500, 500


def get_secret_key(client):

    # Generate private and public keys
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        # backend=default_backend()
    )

    public_key = private_key.public_key()
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Send public key to server
    send_data(client, pem)

    # Receive encrypted secret key and decrypt it
    while True:
        encrypted = receive_data(client)
        if encrypted is not None:
            secret_key = private_key.decrypt(
                encrypted,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()), # Mask Generation Function
                    algorithm=hashes.SHA256(),
                    label=None
                ) # Optimal Asymmetric Encryption Padding
            )
            return secret_key


def main():
    client = socket.socket()

    argv = sys.argv
    name = ''
    if "--name" in argv:
        name = argv[argv.index("--name")+1] 
    
    SERVER_ADDRESS = get_address("--local" in argv or "-L" in argv)
    
    client.connect(SERVER_ADDRESS)
    print(f"Connected to {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")

    key = get_secret_key(client)
    
    Paint(client, key, name)
    client.close()


if __name__ == "__main__":
    main()
