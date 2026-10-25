import pygame as pg

class Terrain:
    def __init__(self):
        self.ground = pg.image.load(
            "assets/stages/terrain-ground.png"
        )

        self.surface = pg.image.load(
            "assets/stages/terrain-surface.png"
        ).convert_alpha()
        