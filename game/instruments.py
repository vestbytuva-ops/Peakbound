from pathlib import Path

import pygame as pg

from game.run import PIXELS_PER_METRE


ASSETS = Path(__file__).resolve().parents[1] / "assets"
MAX_SPEED = 120
GAUGE_BG = (25, 35, 41)
LCD = (13, 26, 29)
PAPER = (246, 241, 222)
MUTED = (174, 194, 188)
GREEN = (181, 226, 146)
GOLD = (241, 197, 103)
RED = (247, 126, 109)


def _sprite(filename, size, folder="instruments", crop=False):
    sprite = pg.image.load(ASSETS / folder / filename).convert_alpha()
    if crop:
        sprite = sprite.subsurface(sprite.get_bounding_rect())
    return pg.transform.smoothscale(sprite, size)


class Instruments:
    def __init__(self):
        self.face = _sprite("meter-rpm.png", (168, 168))
        self.needle = _sprite("meter-needle.png", (21, 79))
        self.fuel_icon = _sprite("fuel-icon.png", (22, 22), crop=True)
        self.distance_icon = _sprite("distance-icon.png", (19, 19), crop=True)
        self.coin_icon = _sprite("coin-icon.png", (19, 19), crop=True)
        self.track = _sprite("progressbar-bg.png", (128, 14), crop=True)
        self.parcel = _sprite("pakke.png", (22, 17), folder="pickups", crop=True)
        self.case = {False: self._case(149), True: self._case(174)}

    def _case(self, height):
        case = pg.Surface((383, height), pg.SRCALPHA)
        outline = [(14, 0), (367, 0), (382, 14), (382, height - 15),
                   (367, height - 1), (14, height - 1), (0, height - 15), (0, 14)]
        pg.draw.polygon(case, GAUGE_BG, outline)
        pg.draw.lines(case, (74, 91, 95), True, outline, 2)
        pg.draw.line(case, (55, 72, 75), (173, 16), (173, height - 18))
        case.blit(self.face, (0, 2))
        # The speed display sits over the RPM label drawn on the source dial.
        pg.draw.rect(case, LCD, (50, 102, 66, 34), border_radius=5)
        pg.draw.rect(case, (57, 77, 78), (50, 102, 66, 34), width=1, border_radius=5)
        for x, y in ((14, 14), (367, 14), (14, height - 15), (367, height - 15)):
            pg.draw.circle(case, (78, 95, 96), (x, y), 2)
        return case

    def draw(self, screen, run, text):
        x, y = 18, 17
        post = run.mode == "post"
        screen.blit(self.case[post], (x, y))

        # The needle rotates around the round hub, not the sprite's centre.
        speed = run.vehicle.velocity.length() / PIXELS_PER_METRE * 3.6
        angle = 120 - 240 * min(1, speed / MAX_SPEED)
        offset = pg.Vector2(-0.3, -25.3).rotate(-angle)
        pivot = pg.Vector2(x + 84, y + 85)
        needle = pg.transform.rotate(self.needle, angle)
        rect = needle.get_rect(center=(round(pivot.x + offset.x), round(pivot.y + offset.y)))
        screen.blit(needle, rect)
        for label, dx, dy in (("0", 40, 113), ("60", 84, 29), ("120", 130, 113)):
            text(screen, label, (x + dx, y + dy), 11, MUTED, True, "center")
        text(screen, f"{speed:.0f}", (x + 83, y + 113), 21, PAPER, True, "center")
        text(screen, "km/t", (x + 83, y + 128), 11, MUTED, anchor="center")

        # The rest of the data shares the dashboard's housing.
        screen.blit(self.distance_icon, (x + 189, y + 24))
        text(screen, f"{int(run.distance)} m", (x + 216, y + 20), 23, PAPER, True)
        screen.blit(self.coin_icon, (x + 189, y + 58))
        text(screen, f"{run.coins}", (x + 215, y + 54), 20, GOLD, True)
        text(screen, f"{run.score} poeng", (x + 358, y + 58), 16, MUTED, anchor="topright")

        screen.blit(self.fuel_icon, (x + 187, y + 98))
        screen.blit(self.track, (x + 217, y + 102))
        fraction = max(0, min(1, run.fuel / run.capacity))
        pg.draw.rect(screen, LCD, (x + 220, y + 105, 122, 8), border_radius=2)
        if fraction:
            color = RED if fraction < 0.22 else GREEN
            fill = round(122 * fraction)
            pg.draw.rect(screen, color, (x + 220, y + 105, max(1, fill), 8), border_radius=2)
        if run.refuel_until > run.elapsed:
            text(screen, f"+{run.refuel_amount:.0f}", (x + 363, y + 109), 15, GREEN, True, "center")

        if post:
            pg.draw.line(screen, (55, 72, 75), (x + 188, y + 131), (x + 358, y + 131))
            screen.blit(self.parcel, (x + 188, y + 141))
            text(screen, f"{run.package_health}/2", (x + 217, y + 141), 16, MUTED, True)
            text(screen, f"{run.deliveries} levert", (x + 358, y + 140), 18, PAPER, True, "topright")
