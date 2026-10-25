import pygame as pg

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.speed = 0
        self.acceleration = 200
        self.max_speed = 400

    def update(self, dt, keys):
        if keys[pg.K_d]:
            self.speed += self.acceleration * dt
        if keys[pg.K_a]:
            self.speed -= self.acceleration * dt
            
        self.x += self.speed * dt