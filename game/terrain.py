from pathlib import Path

import pygame as pg

class Terrain:
    def __init__(self):
        # Punktene beskriver kjøreflaten fra start til mål i verdenskoordinater.
        self.points = [
            (0, 500), (400, 500), (800, 390),
            (1200, 470), (1550, 330), (1950, 500),
            (2400, 400), (2900, 500), (3300, 370),
            (3800, 470), (4200, 350), (4700, 500),
            (5200, 500),
        ]
        self.length = self.points[-1][0]

        assets = Path(__file__).resolve().parents[1] / "assets" / "stages"
        self.ground = pg.image.load(assets / "terrain-ground.png").convert()
        self.surface = pg.image.load(assets / "terrain-surface.png").convert_alpha()
        self.top = min(y for x, y in self.points) - self.surface.get_height()
        self.course_image = None

    def height_at(self, x):
        """Finn høyden mellom de to banepunktene på hver side av x."""
        if x <= self.points[0][0]:
            return self.points[0][1]
        for (x1, y1), (x2, y2) in zip(self.points, self.points[1:]):
            if x <= x2:
                fraction = (x - x1) / (x2 - x1)
                return y1 + (y2 - y1) * fraction
        return self.points[-1][1]

    def _build_image(self, height):
        width = self.length + 1
        image = pg.Surface((width, height), pg.SRCALPHA)

        # Fyll med jordfliser og skjær ut himmelen langs kjøreflaten.
        for x in range(0, width, self.ground.get_width()):
            for y in range(0, height, self.ground.get_height()):
                image.blit(self.ground, (x, y))
        outline = [(x, y - self.top) for x, y in self.points]
        sky = [(0, 0), (self.length, 0)] + list(reversed(outline))
        pg.draw.polygon(image, (0, 0, 0, 0), sky)

        # På rad 11 i gressbildet begynner den sammenhengende grønne kanten.
        # Gresstråene over kanten er dekor. Hjulene kjører langs kanten.
        grass_row = 11
        for x in range(width):
            y = round(self.height_at(x)) - self.top - grass_row
            source = (x % self.surface.get_width(), 0, 1, self.surface.get_height())
            image.blit(self.surface, (x, y), source)
        return image

    def draw(self, screen, camera_x):
        # Banen bygges én gang. Pygame viser bare utsnittet innenfor vinduet.
        height = max(1, screen.get_height() - self.top)
        if self.course_image is None or self.course_image.get_height() != height:
            self.course_image = self._build_image(height)
        screen.blit(self.course_image, (-round(camera_x), self.top))
