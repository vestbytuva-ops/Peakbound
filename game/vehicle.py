import pygame as pg

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.speed = 0
        self.acceleration = 200
        self.max_speed = 400
    def update (self, dt, keys):
        self.speed += self.acceleration * dt
        pass