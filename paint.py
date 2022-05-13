from socket import socket
import sys
import threading
from tkinter import *
from tkinter.colorchooser import askcolor

from protocol import receive_data, send_data


class Paint(object):

    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'black'
    BUFFER_SIZE = 50

    def __init__(self, client, key):
        self.client = client
        self.key = key

        self.root = Tk()

        # GUI setup
        self.pen_button = Button(
            self.root, text='CLEAR', command=self.clear_board)
        self.pen_button.grid(row=0, column=0)

        self.pen_button = Button(self.root, text='Pen', command=self.use_pen)
        self.pen_button.grid(row=0, column=1)

        self.eraser_button = Button(
            self.root, text='Eraser', command=self.use_eraser)
        self.eraser_button.grid(row=0, column=2)

        self.color_button = Button(
            self.root, text='Color', command=self.choose_color)
        self.color_button.grid(row=0, column=3)

        self.choose_size_scale = Scale(
            self.root, from_=1, to=20, orient=HORIZONTAL)
        self.choose_size_scale.grid(row=0, column=4)

        self.canvas = Canvas(self.root, bg='white', width=600, height=600)
        self.canvas.grid(row=1, columnspan=5)

        self.setup()

        receive_thread = threading.Thread(
            target=self.receive, args=(self.client,), daemon=True)
        receive_thread.start()

        self.root.mainloop()

    def setup(self):
        self.old_x = None
        self.old_y = None
        self.radius = self.choose_size_scale.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False

        self.line = []

        self.active_button = self.pen_button
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.pen_released)

    def clear_board(self):
        self.canvas.delete('all')
        send_data(self.client, {'type': 'CLEAR'}, key=self.key)

    def use_pen(self):
        self.activate_button(self.pen_button)

    def use_eraser(self):
        self.activate_button(self.eraser_button, eraser_mode=True)

    def choose_color(self):
        self.eraser_on = False
        self.activate_button(self.pen_button)
        color = askcolor(color=self.color)[1]
        if color != None:
            self.color = color
        else:
            return None

    def activate_button(self, some_button, eraser_mode=False):
        self.active_button.config(relief='raised')
        some_button.config(relief='sunken')
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        self.radius = self.choose_size_scale.get()
        paint_color = 'white' if self.eraser_on else self.color

        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=self.radius, fill=paint_color,
                                    capstyle='round', smooth=True, splinesteps=36)

            if len(self.line) > self.BUFFER_SIZE:
                self.send_line()
                self.line = [(self.old_x, self.old_y)]

        self.line.append((event.x, event.y))
        self.old_x = event.x
        self.old_y = event.y

    def pen_released(self, event):
        self.send_line()
        self.old_x, self.old_y = None, None
        self.line = []

    def draw_line(self, points, color, radius):
        if points:
            px, py = points[0]
            print(points)
            for x, y in points:
                self.canvas.create_line(px, py, x, y,
                                        width=radius, fill=color,
                                        capstyle='round', smooth=True, splinesteps=36)
                px, py = x, y

    # Socket handling

    def send_line(self):
        if self.eraser_on:
            color = 'white'
        else:
            color = self.color

        send_data(self.client, {
                  'type': 'DRAW', 'points': self.line, 'color': color, 'radius': self.radius}, key=self.key)

    def receive(self, client):
        while True:
            try:
                # GET TWO CLOSE POINTS FROM SERVER AND DRAW TO SCREEN
                recv = receive_data(client, key=self.key)

                if recv['type'] == 'DRAW':
                    points, color, radius = recv['points'], recv['color'], recv['radius']
                    self.draw_line(points, color, radius)
                    print('[RECEIVE]', {'points': len(
                        recv['points']), 'color': recv['color'], 'radius': recv['radius']})
                elif recv['type'] == 'CLEAR':
                    self.canvas.delete('all')
                    print('[RECEIVE] CLEAR')

            except Exception as e:
                print("[EXCEPTION RECEIVING]", e)
                break
        self.client.close()
