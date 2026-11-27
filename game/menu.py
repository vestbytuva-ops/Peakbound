from math import atan
from pathlib import Path

import pygame as pg

from game.terrain import WORLDS
from game.vehicle import VEHICLES, Vehicle


ASSETS = Path(__file__).resolve().parents[1] / "assets"
PREVIEW_CAMERA_X = 250
INK = (19, 30, 35)
TRIM = (73, 91, 97)
PAPER = (242, 240, 224)
MUTED = (173, 190, 191)
GOLD = (246, 203, 132)


def _icon(relative, height):
    image = pg.image.load(ASSETS / relative).convert_alpha()
    image = image.subsurface(image.get_bounding_rect())
    width = round(height * image.get_width() / image.get_height())
    return pg.transform.smoothscale(image, (width, height))


class MainMenu:
    """Banekort og startvalg rundt en aktiv forhåndsvisning av terrenget."""

    def __init__(self, width, height):
        self.width = width
        self.left = pg.Rect(28, 26, 468, height - 52)
        self.right = pg.Rect(self.left.right + 20, height - 218, width - self.left.right - 48, 192)
        self.flag = _icon("menu/start-flag.png", 25)
        self.camera = _icon("menu/replay-camera.png", 18)
        self.toolbox = _icon("menu/garage-toolbox.png", 22)
        self.coin = _icon("pickups/mynt.png", 19)
        self.name_font = pg.font.SysFont("segoeui,arial", 19, bold=True)
        self.cars = {key: Vehicle(0, 0, key) for key in VEHICLES}
        self.vehicle_icons = {}
        for key, car in self.cars.items():
            icon = pg.Surface((128, 72), pg.SRCALPHA)
            car.draw_pose(icon, 0, (64, 56, 0, 0))
            icon = icon.subsurface(icon.get_bounding_rect())
            size = (56, round(56 * icon.get_height() / icon.get_width()))
            self.vehicle_icons[key] = pg.transform.scale(icon, size)

    def _panel(self, screen, ui, rect):
        pg.draw.rect(screen, (11, 19, 22), rect.move(3, 5), border_radius=14)
        ui.box(screen, rect, INK, TRIM, 14)

    def _draw_car(self, screen, game):
        # Finn et synlig punkt over menybrettet og plasser hjulene ved bakken.
        candidates = range(self.left.right + 135, self.width - 120, 35)
        positions = [(x, game.terrain.height_at(x + PREVIEW_CAMERA_X)) for x in candidates]
        target = self.width * 0.72
        x, y = min(positions, key=lambda point:
                   abs(point[0] - target) + 7 * max(0, point[1] - self.right.top + 28))
        world_x = x + PREVIEW_CAMERA_X
        angle = atan(game.terrain.slope_at(world_x))
        self.cars[game.vehicle_id].draw_pose(screen, PREVIEW_CAMERA_X, (world_x, y - 13, angle, 0))

    def _profile(self, screen, game, ui):
        card = pg.Rect(self.width - 329, 26, 301, 70)
        self._panel(screen, ui, card)
        profile = game.progress.name
        if self.name_font.size(profile)[0] > card.width - 34:
            while self.name_font.size(profile + "…")[0] > card.width - 34:
                profile = profile[:-1]
            profile += "…"
        ui.text(screen, profile, (card.left + 17, card.top + 7), 19, PAPER, True)
        screen.blit(self.coin, self.coin.get_rect(midleft=(card.left + 17, card.top + 49)))
        ui.text(screen, f"{game.progress.balance} mynter", (card.left + 44, card.top + 38), 16, GOLD)

    def draw(self, screen, game, ui):
        self._draw_car(screen, game)
        self._profile(screen, game, ui)
        self._panel(screen, ui, self.left)
        self._panel(screen, ui, self.right)
        self._route_sheet(screen, game, ui)
        self._travel_dock(screen, game, ui)

    def _route_sheet(self, screen, game, ui):
        left = self.left
        x = left.left + 20
        w = left.width - 40
        ui.text(screen, "Peakbound", (x, left.top + 5), 60, PAPER, True)
        pg.draw.line(screen, WORLDS[game.world_id].accent,
                     (x + 1, left.top + 90), (left.right - 21, left.top + 90), 2)
        ui.text(screen, "Velg fjell", (x, left.top + 108), 23, PAPER, True)

        # Startknappen er første fokuspunkt på denne skjermen.
        ui.add("start", (x, left.bottom - 71, w, 51), "Start kjøring", icon=self.flag)
        for index, spec in enumerate(WORLDS.values()):
            ui.add("world:" + spec.id, (x, left.top + 147 + index * 68, w, 60),
                   spec.name, active=game.world_id == spec.id, marker=spec.accent,
                   subtitle=f"{spec.difficulty} · {spec.description}")

        mode_y = left.top + 427
        ui.text(screen, "Spillmodus", (x, mode_y), 21, PAPER, True)
        half = (w - 10) // 2
        ui.add("mode:free", (x, mode_y + 33, half, 42), "Fri kjøring", active=game.mode == "free")
        ui.add("mode:post", (x + half + 10, mode_y + 33, half, 42), "Fjellpost", active=game.mode == "post")
        subtitle = ("Kjør så langt du kan før turen tar slutt." if game.mode == "free"
                    else "Lever pakker uten for harde landinger.")
        ui.text(screen, subtitle, (x, mode_y + 85), 17, MUTED)

    def _travel_dock(self, screen, game, ui):
        dock = self.right
        x = dock.left + 19
        w = dock.width
        two_sides = round(w * 0.48)
        log_x = dock.left + two_sides + 13
        log_width = dock.right - log_x - 19
        car_width = two_sides - 27
        y = dock.top
        pg.draw.line(screen, TRIM, (log_x - 13, y + 16), (log_x - 13, dock.bottom - 17))
        ui.text(screen, "Kjøretøy", (x, y + 11), 21, PAPER, True)
        small = (car_width - 8) // 2
        for index, (key, spec) in enumerate(VEHICLES.items()):
            ui.add("vehicle:" + key, (x + index * (small + 8), y + 46, small, 43),
                   spec.name, active=game.vehicle_id == key, icon=self.vehicle_icons[key])
        ui.text(screen, VEHICLES[game.vehicle_id].description, (x, y + 101), 15, MUTED)
        ui.add("garage", (x, y + 135, car_width, 39), "Garasje", icon=self.toolbox)

        best = game.progress.best(game.world_id, game.mode)
        if best is None:
            record = "Ingen tur lagret ennå"
        elif game.mode == "free":
            record = f"{best.distance:.0f} m"
        else:
            record = f"{best.deliveries} leveringer"
        ui.text(screen, "Rekord", (log_x, y + 11), 21, PAPER, True)
        ui.text(screen, record, (log_x, y + 42), 18, GOLD if best else MUTED)
        selected = game._selected_record()
        if selected is not None:
            label = f"Spøkelsesløp valgt  ·  {selected.distance:.0f} m"
            ui.text(screen, label, (log_x, y + 99), 15, MUTED)
        ui.add("history", (log_x, y + 135, log_width, 39), "Tidligere turer og spøkelsesløp",
               icon=self.camera)
