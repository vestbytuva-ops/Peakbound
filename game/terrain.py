from bisect import bisect_right
from math import lcm
from pathlib import Path

import pygame as pg


# x, bakkehøyde og krumming. En topp krummer nedover (positiv y).
PROFILE = (
    (0, 505, 0),
    (360, 505, 0),
    (795, 396, 1 / 205),
    (1245, 513, -1 / 295),
    (1750, 366, 1 / 180),
    (2240, 531, -1 / 300),
    (2675, 406, 1 / 177),
    (3115, 493, -1 / 330),
    (3640, 350, 1 / 167),
    (4170, 512, -1 / 245),
    (4705, 397, 1 / 190),
    (5220, 505, 0),
    (6020, 505, 0),
)
GRASS_EDGE = 11  # Den sammenhengende gresskanten i teksturbildet.


class Terrain:
    def __init__(self):
        self.points = [(x, y) for x, y, _ in PROFILE]
        self.length = self.points[-1][0]
        self._xs = [x for x, _ in self.points]
        self._curves = [
            self._make_curve(start, end) for start, end in zip(PROFILE, PROFILE[1:])
        ]

        assets = Path(__file__).resolve().parents[1] / "assets" / "stages"
        self.ground = pg.image.load(assets / "terrain-ground.png").convert()
        self.surface = pg.image.load(assets / "terrain-surface.png").convert_alpha()
        self.top = min(y for _, y in self.points) - self.surface.get_height()
        self.course_image = None
        self._extensions = {}

    @staticmethod
    def _make_curve(start, end):
        x1, y1, curvature1 = start
        x2, y2, curvature2 = end
        width = x2 - x1
        change = y2 - y1
        q1 = curvature1 * width ** 2
        q2 = curvature2 * width ** 2
        # Femtegradskurven matcher høyde, vannrett tangent og krumming
        # i begge ender. Stykkene møtes uten knekk på topper og i bunner.
        a2 = q1 / 2
        a3 = 10 * change - 1.5 * q1 + 0.5 * q2
        a4 = -15 * change + 1.5 * q1 - q2
        a5 = 6 * change - 0.5 * q1 + 0.5 * q2
        return x1, width, y1, a2, a3, a4, a5

    def height_at(self, x):
        if x <= 0:
            return self.points[0][1]
        if x >= self.length:
            return self.points[-1][1]
        x1, width, y1, a2, a3, a4, a5 = self._curves[bisect_right(self._xs, x) - 1]
        t = (x - x1) / width
        return y1 + t ** 2 * (a2 + t * (a3 + t * (a4 + t * a5)))

    def slope_at(self, x):
        if x <= 0 or x >= self.length:
            return 0.0
        x1, width, _, a2, a3, a4, a5 = self._curves[bisect_right(self._xs, x) - 1]
        t = (x - x1) / width
        return t * (2 * a2 + t * (3 * a3 + t * (4 * a4 + t * 5 * a5))) / width

    def _ground_image(self, width, height):
        image = pg.Surface((width, height), pg.SRCALPHA)
        for x in range(0, width, self.ground.get_width()):
            for y in range(0, height, self.ground.get_height()):
                image.blit(self.ground, (x, y))
        return image

    def _build_course_image(self, height):
        width = self.length
        image = self._ground_image(width, height)
        # Tegning og fysikk bruker samme kurve, avrundet til hele bildepiksler.
        outline = [(x, round(self.height_at(x)) - self.top) for x in range(width)]
        sky = [(0, 0), (width - 1, 0)] + list(reversed(outline))
        pg.draw.polygon(image, (0, 0, 0, 0), sky)
        texture_width = self.surface.get_width()
        for x, y in outline:
            source = (x % texture_width, 0, 1, self.surface.get_height())
            image.blit(self.surface, (x, y - GRASS_EDGE), source)
        return image

    def _flat_tile(self, height, ground_y):
        # Felles periode holder jord og gress i samme fase ved skjøtene.
        width = lcm(self.ground.get_width(), self.surface.get_width())
        tile = self._ground_image(width, height)
        y = ground_y - self.top
        tile.fill((0, 0, 0, 0), (0, 0, width, y + 1))
        for x in range(0, width, self.surface.get_width()):
            tile.blit(self.surface, (x, y - GRASS_EDGE))
        return tile

    def _draw_extension(self, screen, camera, left, right, ground_y):
        if left >= right:
            return
        if ground_y not in self._extensions:
            height = self.course_image.get_height()
            self._extensions[ground_y] = self._flat_tile(height, ground_y)
        tile = self._extensions[ground_y]
        width = tile.get_width()
        x = left
        while x < right:
            source_x = x % width
            count = min(width - source_x, right - x)
            area = (source_x, 0, count, tile.get_height())
            screen.blit(tile, (x - camera, self.top), area)
            x += count

    def draw(self, screen, camera_x):
        # Banen og de flate endestykkene mellomlagres som teksturer.
        height = max(1, screen.get_height() - self.top)
        if self.course_image is None or self.course_image.get_height() != height:
            self.course_image = self._build_course_image(height)
            self._extensions.clear()
        left = round(camera_x)
        right = left + screen.get_width()
        if left < 0:
            self._draw_extension(screen, left, left, min(0, right), self.points[0][1])
        if right > self.length:
            start = max(self.length, left)
            self._draw_extension(screen, left, start, right, self.points[-1][1])
        screen.blit(self.course_image, (-left, self.top))
