import socket

from paint import Paint
from protocol import SERVER_ADDRESS

WIDTH, HEIGHT = 500, 500


def main():
    # name = input("Enter your name:")
    # print(name)

    client = socket.socket()
    client.connect(SERVER_ADDRESS)
    
    # client.sendall(name)

    Paint(client, '')
    client.close()

if __name__ == "__main__":
    main()