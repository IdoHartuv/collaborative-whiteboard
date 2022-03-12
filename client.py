import socket

import pygame

from board import Board
from protocol import SERVER_ADDRESS

WIDTH, HEIGHT = 500, 500


def main():
    # name = input("Enter your name:")
    # print(name)

    client = socket.socket()
    client.connect(SERVER_ADDRESS)
    
    # client.sendall(name)


    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    board = Board(screen, client, '')
    board.run()

    client.close()

if __name__ == "__main__":
    main()