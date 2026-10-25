import pygame as pg

from game.vehicle import Vehicle

class Game:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.vehicle = Vehicle(100,400)

    def handle_event(self, event):
        pass

    def update(self, dt, keys):
        self.vehicle.update(dt,keys)
        