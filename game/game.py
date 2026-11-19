from pathlib import Path

import pygame as pg

from game.camera import Camera
from game.terrain import Terrain
from game.vehicle import Vehicle


SCENERY = Path(__file__).resolve().parents[1] / "assets" / "scenery"
PIXELS_PER_METRE = 20
START_X = 100


class Game:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.terrain = Terrain()
        self.finish_x = self.terrain.length - 100
        self.total_metres = round((self.finish_x - START_X) / PIXELS_PER_METRE)
        self.camera = Camera(width)
        self.sky = pg.transform.smoothscale(
            pg.image.load(SCENERY / "sky-bg.png").convert(), (width, height)
        )
        self.cloud = pg.transform.smoothscale(
            pg.image.load(SCENERY / "sky-cloud.png").convert_alpha(), (138, 82)
        )
        self.font = pg.font.Font(None, 26)
        self.title_font = pg.font.Font(None, 40)
        self.restart()

    def restart(self):
        self.vehicle = Vehicle(START_X, self.terrain.height_at(START_X))
        self.vehicle.snap_to_ground(self.terrain)
        self.camera.x = 0.0
        self.finished = False

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            self.restart()

    def update(self, dt, keys):
        dt = max(0, min(dt, 0.05))
        if not self.finished:
            self.vehicle.update(dt, keys, self.terrain)
            if self.vehicle.x >= self.finish_x:
                self.finished = True
                self.vehicle.speed = 0
        self.camera.update(dt, self.vehicle.x, self.terrain.length)

    def draw_background(self, screen):
        screen.blit(self.sky, (0, 0))
        # Skyene og fjellene flytter seg saktere enn bakken.
        for index in range(5):
            x = (240 + index * 370 - self.camera.x * 0.14) % 1850 - 140
            screen.blit(self.cloud, (round(x), 45 + (index * 53) % 120))

        ridge = [(0, 388), (160, 306), (225, 326), (405, 170),
                 (520, 300), (620, 258), (820, 400), (990, 269),
                 (1065, 288), (1250, 208), (1440, 388)]
        offset = round(self.camera.x * 0.24) % 1440
        for start in range(-offset, self.width, 1440):
            peaks = [(start + x, y) for x, y in ridge]
            pg.draw.polygon(screen, (115, 168, 165),
                            peaks + [(start + 1440, self.height), (start, self.height)])

    def draw_markers(self, screen):
        for metres in range(0, self.total_metres + 1, 50):
            world_x = START_X + metres * PIXELS_PER_METRE
            x = round(world_x - self.camera.x)
            if x < -100 or x > self.width + 100:
                continue
            y = round(self.terrain.height_at(world_x))
            pg.draw.line(screen, (90, 68, 50), (x, y), (x, y - 100), 5)
            if world_x == self.finish_x:
                for row in range(3):
                    for col in range(5):
                        color = (248, 245, 227) if (row + col) % 2 else (39, 50, 47)
                        pg.draw.rect(screen, color, (x + col * 9, y - 102 + row * 9, 9, 9))
            else:
                label = "Start" if metres == 0 else f"{metres} m"
                sign = self.font.render(label, True, (40, 55, 45))
                rect = sign.get_rect(midleft=(x, y - 88))
                pg.draw.rect(screen, (251, 239, 204), rect.inflate(12, 6), border_radius=3)
                screen.blit(sign, rect)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_markers(screen)
        self.terrain.draw(screen, self.camera.x)
        self.vehicle.draw(screen, self.camera.x)

        distance = int(max(0, self.vehicle.x - START_X) / PIXELS_PER_METRE)
        distance = min(distance, self.total_metres)
        pg.draw.rect(screen, (37, 57, 54), (18, 18, 230, 70), border_radius=8)
        screen.blit(self.font.render("Fjellveien", True, (251, 245, 221)), (32, 27))
        status = f"{distance} / {self.total_metres} m"
        screen.blit(self.font.render(status, True, (222, 241, 190)), (32, 56))
        help_text = self.font.render("D / høyrepil   Gass     A / venstrepil   Brems og rygg     R   Omstart",
                                     True, (40, 55, 45))
        rect = help_text.get_rect(topright=(self.width - 32, 31))
        pg.draw.rect(screen, (245, 246, 226), rect.inflate(22, 14), border_radius=8)
        screen.blit(help_text, rect)

        if self.finished:
            box = pg.Rect(0, 0, 384, 104)
            box.midtop = (self.width // 2, 104)
            pg.draw.rect(screen, (37, 57, 54), box, border_radius=10)
            title = self.title_font.render("Du er i mål!", True, (251, 245, 221))
            hint = self.font.render("Trykk R for å kjøre igjen", True, (222, 241, 190))
            screen.blit(title, title.get_rect(center=(box.centerx, box.top + 33)))
            screen.blit(hint, hint.get_rect(center=(box.centerx, box.top + 74)))
