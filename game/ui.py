from dataclasses import dataclass
from functools import lru_cache

import pygame as pg

from game.instruments import Instruments
from game.menu import MainMenu
from game.terrain import WORLDS
from game.vehicle import VEHICLES


INK = (15, 25, 35)
PANEL = (23, 37, 49)
FIELD = (30, 48, 62)
EDGE = (50, 73, 86)
PAPER = (242, 247, 242)
MUTED = (165, 189, 198)
LIME = (208, 235, 147)
GOLD = (255, 203, 104)
MODES = {"free": "Fri kjøring", "post": "Fjellpost"}
UPGRADES = {
    "engine": ("Motor", "Bedre akselerasjon og høyere motorfart"),
    "tank": ("Drivstofftank", "+12 enheter kapasitet per nivå"),
    "grip": ("Dekk", "Mer kraft ned i bakken ved kontakt"),
}


@dataclass
class Button:
    action: str
    rect: pg.Rect
    label: str
    active: bool
    enabled: bool
    subtitle: str = ""
    marker: tuple | None = None
    icon: pg.Surface | None = None


class UI:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.fonts = {}
        self.buttons = []
        self.focus = 0
        self.keyboard = True
        self.pointer = (-1, -1)
        self.shade = pg.Surface((width, height), pg.SRCALPHA)
        self.shade.fill((9, 17, 26, 188))
        self.instruments = Instruments()
        self.menu = MainMenu(width, height)

    def reset(self):
        self.buttons.clear()
        self.focus = 0
        self.keyboard = True

    def handle(self, event):
        available = [button for button in self.buttons if button.enabled]
        if not available:
            return None
        self.focus %= len(available)
        if event.type == pg.MOUSEMOTION:
            self.pointer = event.pos
            self.keyboard = False
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.pointer = event.pos
            for button in available:
                if button.rect.collidepoint(event.pos):
                    return button.action
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_TAB, pg.K_DOWN, pg.K_RIGHT, pg.K_UP, pg.K_LEFT):
                backwards = event.key in (pg.K_UP, pg.K_LEFT) or getattr(event, "mod", 0) & pg.KMOD_SHIFT
                self.focus = (self.focus + (-1 if backwards else 1)) % len(available) if self.keyboard else 0
                self.keyboard = True
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
                return available[self.focus].action
        return None

    @lru_cache(maxsize=320)
    def _label(self, value, size, color, bold):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = pg.font.SysFont("segoeui,arial", size, bold=bold)
        return self.fonts[key].render(value, True, color)

    def text(self, screen, value, pos, size=22, color=PAPER, bold=False, anchor="topleft"):
        image = self._label(str(value), size, color, bold)
        screen.blit(image, image.get_rect(**{anchor: pos}))

    def box(self, screen, rect, fill=PANEL, outline=EDGE, radius=13):
        pg.draw.rect(screen, fill, rect, border_radius=radius)
        if outline:
            pg.draw.rect(screen, outline, rect, width=1, border_radius=radius)

    def add(self, action, rect, label, active=False, enabled=True, subtitle="", marker=None, icon=None):
        self.buttons.append(Button(action, pg.Rect(rect), label, active, enabled, subtitle, marker, icon))

    def _draw_buttons(self, screen):
        available = [b for b in self.buttons if b.enabled]
        focused = available[self.focus % len(available)] if self.keyboard and available else None
        for button in self.buttons:
            r = button.rect
            primary = button.action in ("start", "retry", "resume", "race")
            hover = button.enabled and r.collidepoint(self.pointer)
            bg = LIME if primary else ((39, 65, 69) if button.active else FIELD)
            if hover and not primary:
                bg = (48, 72, 82)
            elif hover:
                bg = (227, 246, 179)
            if not button.enabled:
                bg = PANEL
            line = LIME if button.active else EDGE
            self.box(screen, r, bg, line, 9)
            if button is focused:
                pg.draw.rect(screen, GOLD, r.inflate(6, 6), width=2, border_radius=12)
            fg = INK if primary else (PAPER if button.enabled else MUTED)
            if button.marker:
                pg.draw.rect(screen, button.marker, (r.left + 12, r.top + 13, 4, r.height - 26), border_radius=2)
            if button.subtitle:
                inset = 25
                if button.icon:
                    screen.blit(button.icon, button.icon.get_rect(midleft=(r.left + 20, r.centery)))
                    inset = button.icon.get_width() + 29
                self.text(screen, button.label, (r.left + inset, r.top + 6), 20, fg, True)
                self.text(screen, button.subtitle, (r.left + inset, r.top + 34), 14, MUTED)
            elif button.icon:
                label = self._label(button.label, 18, fg, True)
                start = r.centerx - (button.icon.get_width() + 9 + label.get_width()) // 2
                screen.blit(button.icon, button.icon.get_rect(midleft=(start, r.centery)))
                screen.blit(label, label.get_rect(midleft=(start + button.icon.get_width() + 9, r.centery)))
            else:
                self.text(screen, button.label, r.center, 18, fg, True, "center")

    def draw(self, screen, game):
        self.buttons.clear()
        if game.state == "playing":
            self.instruments.draw(screen, game.run, self.text)
            return
        if game.state != "menu":
            screen.blit(self.shade, (0, 0))
        if game.state == "menu":
            self.menu.draw(screen, game, self)
        elif game.state == "history":
            self._history(screen, game)
        elif game.state == "garage":
            self._garage(screen, game)
        elif game.state == "paused":
            self._pause(screen)
        elif game.state == "result":
            self._result(screen, game)
        self._draw_buttons(screen)
        if game.notice:
            self.box(screen, (245, 666, 790, 39), INK, GOLD, 9)
            self.text(screen, game.notice, (640, 686), 16, PAPER, anchor="center")

    def _history(self, screen, game):
        self.box(screen, (115, 48, 1050, 630), INK)
        self.text(screen, "Tidligere turer", (148, 66), 47, PAPER, True)
        self.text(screen, f"{WORLDS[game.world_id].name} · {MODES[game.mode]}", (149, 130), 21, MUTED)
        self.add("back", (940, 85, 187, 44), "Tilbake")
        records = game.progress.records(game.world_id, game.mode)
        best = game.progress.best(game.world_id, game.mode)
        if not records:
            self.text(screen, "Fullfør en tur for å få din første spøkelsesbil.", (149, 208), 25, PAPER)
        for n, record in enumerate(records[:6]):
            y = 172 + n * 64
            self.box(screen, (149, y, 978, 56), FIELD, EDGE, 8)
            self.text(screen, record.created, (165, y + 7), 17, PAPER, True)
            self.text(screen, VEHICLES[record.vehicle].name if record.vehicle in VEHICLES else record.vehicle,
                      (165, y + 29), 14, MUTED)
            score = f"{record.distance:.0f} m · {record.score} poeng"
            if record.mode == "post":
                score = f"{record.deliveries} leverte · {record.distance:.0f} m"
            self.text(screen, score, (427, y + 16), 19, PAPER)
            if best and record.id == best.id:
                self.text(screen, "Rekord", (748, y + 17), 17, GOLD, True)
            self.add("select:" + record.id, (888, y + 8, 221, 40),
                     "Valgt" if record.id == game.ghost_id else "Kjør mot denne",
                     active=record.id == game.ghost_id, enabled=bool(record.frames))
        self.add("ghost_off", (149, 585, 241, 44), "Slå av spøkelsesbil",
                 enabled=game.ghost_id is not None)

    def _garage(self, screen, game):
        self.box(screen, (90, 51, 1100, 615), INK)
        self.text(screen, "Garasje", (127, 74), 46, PAPER, True)
        self.text(screen, f"{game.progress.balance} mynter", (1150, 94), 23, GOLD, True, "topright")
        self.text(screen, "Oppgraderinger gjelder begge biler.", (129, 145), 21, MUTED)
        for i, (key, (label, description)) in enumerate(UPGRADES.items()):
            x = 129 + i * 343
            self.box(screen, (x, 195, 321, 249), PANEL)
            self.text(screen, label, (x + 20, 219), 26, PAPER, True)
            self.text(screen, description, (x + 20, 264), 15, MUTED)
            level = game.progress.upgrades[key]
            for mark in range(5):
                pg.draw.rect(screen, LIME if mark < level else EDGE, (x + 21 + mark * 53, 313, 42, 8), border_radius=4)
            cost = game.progress.upgrade_cost(key)
            self.add("upgrade:" + key, (x + 18, 365, 285, 49),
                     "Maksnivå" if cost is None else f"Oppgrader · {cost} mynter",
                     enabled=cost is not None and game.progress.balance >= cost)
        if game.editing_name:
            self.text(screen, "Skriv navnet. Enter lagrer, Esc avbryter.", (130, 473), 17, MUTED)
            self.box(screen, (130, 505, 560, 51), FIELD, LIME)
            self.text(screen, game.name_input + "│", (147, 516), 24, PAPER)
            self.add("name_save", (706, 505, 230, 51), "Lagre navn")
        else:
            self.add("name", (130, 481, 525, 51), f"Spillernavn · {game.progress.name}")
        self.add("back", (130, 585, 255, 48), "Tilbake")

    def _pause(self, screen):
        self.box(screen, (406, 164, 468, 374), INK)
        self.text(screen, "Pause", (640, 199), 48, PAPER, True, "midtop")
        self.add("resume", (458, 291, 364, 49), "Fortsett")
        self.add("restart", (458, 351, 364, 49), "Start på nytt")
        self.add("finish", (458, 411, 364, 49), "Avslutt turen")

    def _result(self, screen, game):
        run = game.run
        self.box(screen, (311, 116, 658, 496), INK)
        self.text(screen, run.reason, (640, 142), 38, PAPER, True, "midtop")
        self.text(screen, f"{run.distance:.0f} m", (640, 200), 68, LIME, True, "midtop")
        package_word = "pakke" if run.deliveries == 1 else "pakker"
        tail = f" · {run.deliveries} {package_word} levert" if run.mode == "post" else ""
        self.text(screen, f"{run.score} poeng · +{run.coins} mynter{tail}", (640, 301), 22, PAPER, False, "midtop")
        line = "Rekord lagret" if game.new_best else "Turen er lagret som spøkelsesbil"
        if game.last_record is None:
            line = "Kjør litt lenger for å lagre et forsøk." if not game.progress.error else game.progress.error
        self.text(screen, line, (640, 351), 17, MUTED, anchor="midtop")
        self.add("retry", (357, 409, 271, 60), "Kjør igjen",
                 enabled=not game.pending_save)
        self.add("race", (649, 409, 271, 60), "Slå denne turen",
                 enabled=bool(game.last_record and game.last_record.frames))
        if game.pending_save:
            self.add("retry_save", (357, 489, 271, 52), "Prøv å lagre igjen")
            self.add("discard_run", (649, 489, 271, 52), "Gå til meny uten å lagre")
        else:
            self.add("menu", (357, 489, 563, 52), "Til hovedmenyen")
