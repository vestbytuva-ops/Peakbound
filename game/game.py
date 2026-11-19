import pygame as pg

from game.camera import Camera
from game.scenery import Scenery
from game.terrain import Terrain
from game.vehicle import Vehicle


FIXED_STEP = 1 / 120
START_X = 150


class Game:
    def __init__(self, width, height):
        self.terrain = Terrain()
        self.camera = Camera(width)
        self.scenery = Scenery(width, height, self.terrain)
        self.restart()

    def restart(self):
        self.vehicle = Vehicle(START_X, self.terrain.height_at(START_X))
        self.vehicle.snap_to_ground(self.terrain)
        self.camera.x = 0.0
        self.accumulator = 0.0

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            self.restart()

    def update(self, dt, keys):
        # Små, faste fysikksteg gir samme oppførsel ved ulik bildefrekvens.
        dt = max(0, min(dt, 0.05))
        self.accumulator += dt
        while self.accumulator >= FIXED_STEP:
            self.vehicle.update(FIXED_STEP, keys, self.terrain)
            self.accumulator -= FIXED_STEP
        self.camera.update(dt, self.vehicle.x)

    def draw(self, screen):
        self.scenery.draw_background(screen, self.camera.x)
        self.scenery.draw_props(screen, self.camera.x)
        self.terrain.draw(screen, self.camera.x)
        self.vehicle.draw(screen, self.camera.x)
