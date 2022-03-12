import random
import socket
import sys
import threading
import pygame
from protocol import receive_data, send_data

class Board():
    def __init__(self, screen, client, name):
        self.draw_on = False
        self.last_pos = (0, 0)
        self.color = (255, 128, 0)
        self.radius = 3

        self.client = client
        self.name = name

        self.screen = screen

    def draw_point(self, pos):
        pygame.draw.circle(self.screen, self.color, pos, self.radius)

    def roundline(self, start, end):
        dx = end[0]-start[0]
        dy = end[1]-start[1]
        distance = max(abs(dx), abs(dy))
        for i in range(distance):
            x = int(start[0]+float(i)/distance*dx)
            y = int(start[1]+float(i)/distance*dy)
            self.draw_point((x, y))
    
    def receive(self, client):
        while True:
            try:
                #GET TWO CLOSE POINTS FROM SERVER AND DRAW TO SCREEN
                recv = receive_data(client)
                points, color, radius = recv['points'], recv['color'], recv['radius']
                self.color = color
                self.radius = radius

                last_point = points[0]
                for p in points:
                    self.roundline(p, last_point)
                    last_point = p

                print('[RECEIVE]', {'points': len(recv['points']), 'color': recv['color'], 'radius': recv['radius']})
                pygame.display.update()

            except socket.error as e:
                print("An error occurred!", e)
                break

        self.client.close()


    def run(self):
        # line = []

        receive_thread = threading.Thread(target=self.receive, args=(self.client,), daemon=True)
        receive_thread.start()

        while True:
            try:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        raise StopIteration

                    if e.type == pygame.MOUSEBUTTONDOWN:
                        self.color = (random.randrange(256), random.randrange(
                            256), random.randrange(256))
                        
                        self.draw_point(e.pos)
                        self.draw_on = True

                    if e.type == pygame.MOUSEBUTTONUP:
                        self.draw_on = False

                        # print("[LINE]", len(line))
                        # send_data(self.client, {'points': line, 'color': self.color, 'radius': self.radius}) # SEND LINE TO SERVER
                        # line = []

                        

                    if e.type == pygame.MOUSEMOTION:
                        if self.draw_on:
                            # line.append(e.pos)
                            self.draw_point(e.pos)
                            self.roundline(e.pos, last_pos)

                            send_data(self.client, {'points': [last_pos, e.pos], 'color': self.color, 'radius': self.radius})
                        last_pos = e.pos
                    
                pygame.display.update()
                    
            except StopIteration:
                break

        pygame.quit()
        sys.exit()