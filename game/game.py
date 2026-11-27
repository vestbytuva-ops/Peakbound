from math import degrees
from pathlib import Path

import pygame as pg

from game.camera import Camera
from game.menu import PREVIEW_CAMERA_X
from game.progress import ProgressStore
from game.replay import GhostReplay
from game.run import Run
from game.scenery import Scenery
from game.terrain import Terrain, WORLDS
from game.ui import UI
from game.vehicle import Vehicle, VEHICLES


ROOT = Path(__file__).resolve().parents[1]
FIXED_STEP = 1 / 120


class Game:
    def __init__(self, width, height, save_path=None):
        self.width = width
        self.height = height
        self.progress = ProgressStore(save_path if save_path is not None else ROOT / "saves" / "saves.json")
        self.ui = UI(width, height)
        self.camera = Camera(width)
        self.world_id = "everest"
        self.mode = "free"
        self.vehicle_id = "ridge"
        self.run = None
        self.ghost_id = None
        self.ghost = None
        self.ghost_vehicle = None
        self.last_record = None
        self.new_best = False
        self.pending_save = False
        self.editing_name = False
        self.name_input = ""
        self.notice = self.progress.error or ""
        self.state = "menu"
        self.running = True
        self.accumulator = 0.0
        self.terrain = Terrain(self.world_id)
        self.scenery = Scenery(width, height, self.terrain)
        self.sprites = {}
        for key, filename, size in (
            ("coin", "mynt.png", (32, 32)),
            ("fuel", "drivstoff.png", (32, 40)),
            ("parcel", "pakke.png", (40, 32)),
            ("damaged", "pakke-skadet.png", (40, 32)),
            ("depot", "posthytte.png", (112, 88)),
        ):
            image = pg.image.load(ROOT / "assets" / "pickups" / filename).convert_alpha()
            self.sprites[key] = pg.transform.scale(image, size)

    def transition(self, state):
        self.state = state
        self.accumulator = 0
        self.ui.reset()

    def _choose_world(self, world_id):
        if self.world_id != world_id:
            self.world_id = world_id
            self.ghost_id = None
            self.terrain = Terrain(world_id)
            self.scenery = Scenery(self.width, self.height, self.terrain)
            self.camera.x = 0.0

    def _selected_record(self):
        return next((record for record in self.progress.records(self.world_id, self.mode)
                     if record.id == self.ghost_id and record.frames), None)

    def start_run(self):
        if self.pending_save and not self.save_result():
            return
        self.run = Run(self.terrain, self.world_id, self.mode, self.vehicle_id, self.progress.upgrades)
        record = self._selected_record()
        self.ghost = GhostReplay(record.frames) if record else None
        ghost_id = record.vehicle if record and record.vehicle in VEHICLES else self.vehicle_id
        self.ghost_vehicle = Vehicle(0, 0, ghost_id) if record else None
        self.camera.x = 0.0
        self.last_record = None
        self.new_best = False
        self.notice = ""
        self.transition("playing")

    def save_result(self):
        if not self.pending_save:
            return True
        run = self.run
        best_before = self.progress.best(run.world_id, run.mode)
        frames = run.recorder.finish(run.elapsed, run.vehicle.pose())
        record = self.progress.save_run(
            run.world_id, run.mode, run.vehicle_id, run.distance, run.coins,
            run.deliveries, run.elapsed, run.reason, frames,
        )
        if record is None:
            self.notice = self.progress.error or "Kunne ikke lagre turen."
            return False
        self.last_record = record
        self.pending_save = False
        self.notice = ""
        best_now = self.progress.best(run.world_id, run.mode)
        self.new_best = bool(best_now and best_now.id == record.id
                             and (best_before is None or best_before.id != record.id))
        return True

    def finish_run(self, reason):
        if self.state not in ("playing", "paused"):
            return False
        self.run.reason = reason
        self.pending_save = self.run.elapsed >= 1 or self.run.coins > 0
        saved = self.save_result()
        self.transition("result")
        return saved

    def request_quit(self):
        if self.state in ("playing", "paused") and not self.finish_run("Turen ble avsluttet"):
            return
        self.running = False

    def _finish_name(self, save):
        if save and not self.progress.set_name(self.name_input):
            self.notice = self.progress.error or "Skriv et gyldig navn."
            return
        self.editing_name = False
        pg.key.stop_text_input()
        self.notice = ""

    def action(self, action):
        if action == "name_save":
            self._finish_name(True)
        elif action == "name":
            self.editing_name = True
            self.name_input = self.progress.name
            pg.key.start_text_input()
        elif action in ("start", "retry"):
            self.start_run()
        elif action == "race":
            self.ghost_id = self.last_record.id
            self.start_run()
        elif action == "restart":
            if self.finish_run("Turen ble startet på nytt"):
                self.start_run()
        elif action == "resume":
            self.transition("playing")
        elif action == "finish":
            self.finish_run("Turen ble avsluttet")
        elif action == "retry_save":
            self.save_result()
        elif action in ("back", "menu"):
            if self.editing_name:
                self._finish_name(False)
            if self.pending_save and not self.save_result():
                return
            self.transition("menu")
        elif action == "discard_run":
            self.pending_save = False
            self.notice = ""
            self.transition("menu")
        elif action in ("history", "ghost"):
            self.transition("history")
        elif action == "garage":
            self.transition("garage")
        elif action == "ghost_off":
            self.ghost_id = None
            self.transition("menu")
        else:
            kind, _, value = action.partition(":")
            if kind == "world":
                self._choose_world(value)
            elif kind == "mode" and value != self.mode:
                self.mode = value
                self.ghost_id = None
            elif kind == "vehicle":
                self.vehicle_id = value
            elif kind == "select":
                self.ghost_id = value
                self.transition("menu")
            elif kind == "upgrade":
                if self.progress.buy_upgrade(value):
                    self.notice = "Oppgraderingen gjelder fra neste tur."
                else:
                    self.notice = self.progress.error or "Oppgraderingen kunne ikke kjøpes."

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.request_quit()
            return
        if event.type == getattr(pg, "WINDOWFOCUSLOST", -1) and self.state == "playing":
            self.transition("paused")
            return
        if self.editing_name:
            if event.type == pg.TEXTINPUT:
                self.name_input = (self.name_input + event.text)[:24]
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key == pg.K_ESCAPE:
                    self._finish_name(False)
                elif event.key == pg.K_RETURN:
                    self._finish_name(True)
                return
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.state == "playing":
                    self.transition("paused")
                elif self.state == "paused":
                    self.transition("playing")
                elif self.state == "menu":
                    self.request_quit()
                else:
                    self.action("back")
                return
            if event.key == pg.K_r:
                if self.state in ("playing", "paused"):
                    self.action("restart")
                    return
                if self.state == "result":
                    self.start_run()
                    return
        if self.state != "playing":
            action = self.ui.handle(event)
            if action:
                self.action(action)

    def update(self, dt, keys):
        if self.state != "playing":
            return
        dt = max(0, min(dt, 0.05))
        self.accumulator += dt
        while self.accumulator >= FIXED_STEP:
            self.run.step(FIXED_STEP, keys)
            self.accumulator -= FIXED_STEP
            if self.run.reason:
                self.finish_run(self.run.reason)
                break
        self.camera.update(dt, self.run.vehicle.x)

    def _draw_pickups(self, screen, camera_x):
        shift = round(camera_x)
        run = self.run
        for x in run.nearby_posts(shift - 120, shift + self.width + 120):
            sprite = self.sprites["depot"]
            y = round(self.terrain.height_at(x)) + 5
            screen.blit(sprite, sprite.get_rect(midbottom=(x - shift, y)))
        for item in run.nearby_pickups(shift - 40, shift + self.width + 40):
            sprite = self.sprites[item.kind]
            screen.blit(sprite, sprite.get_rect(center=(item.x - shift, round(item.y))))

    def draw(self, screen):
        showing_run = self.state in ("playing", "paused", "result") and self.run is not None
        camera_x = self.camera.x if showing_run else PREVIEW_CAMERA_X
        self.scenery.draw_background(screen, camera_x)
        self.scenery.draw_props(screen, camera_x)
        self.terrain.draw(screen, camera_x)
        if showing_run:
            self._draw_pickups(screen, camera_x)
            if self.ghost:
                pose = self.ghost.pose_at(self.run.elapsed)
                if pose is not None:
                    self.ghost_vehicle.draw_pose(screen, camera_x, pose, ghost=True)
            car = self.run.vehicle
            car.draw(screen, camera_x)
            if self.run.mode == "post" and self.run.package_health:
                art = self.sprites["parcel" if self.run.package_health == 2 else "damaged"]
                sprite = pg.transform.rotate(art, -degrees(car.angle))
                offset = pg.Vector2(-31, -36).rotate_rad(car.angle)
                screen.blit(sprite, sprite.get_rect(center=(round(car.x + offset.x - camera_x),
                                                            round(car.y + offset.y))))
        self.ui.draw(screen, self)
