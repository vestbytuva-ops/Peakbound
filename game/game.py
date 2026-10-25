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
    
    def draw(self, screen):
        screen.fill((135, 206, 235))
        
        pg.draw.rect(
        screen,
        (70, 160, 70),
        (0, 450, self.width, self.height - 450)
    )
        self.vehicle.draw(screen)