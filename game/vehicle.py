import pygame as pg

class Vehicle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 80
        self.height = 35

        self.speed = 0
        self.acceleration = 200
        self.max_speed = 400
        self.friction = 120

        self.color = (220,50,50)

    def update(self, dt, keys):
        if keys[pg.K_d]:
            self.speed += self.acceleration * dt
        if keys[pg.K_a]:
            self.speed -= self.acceleration * dt
        else:
            if self.speed > 0:
                self.speed = max(
                    0,self.speed - self.friction * dt
                )
                
        self.x += self.speed * dt