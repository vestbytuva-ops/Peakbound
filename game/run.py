from dataclasses import dataclass
from math import cos

import pygame as pg

from game.replay import ReplayRecorder
from game.vehicle import Vehicle


START_X = 150
PIXELS_PER_METRE = 20
SECTOR_WIDTH = 2400
POST_SPACING = 2100
POST_BONUS = 10
HARD_LANDING = 195


@dataclass(frozen=True)
class Pickup:
    kind: str
    x: int
    y: float


class Run:
    def __init__(self, terrain, world_id, mode, vehicle_id, upgrades):
        self.terrain = terrain
        self.world_id = world_id
        self.mode = mode
        self.vehicle_id = vehicle_id
        self.vehicle = Vehicle(START_X, terrain.height_at(START_X), vehicle_id, upgrades)
        self.vehicle.snap_to_ground(terrain)
        self.capacity = 60 + 12 * upgrades.get("tank", 0)
        self.fuel = self.capacity
        self.distance = 0.0
        self.coins = 0
        self.deliveries = 0
        self.elapsed = 0.0
        self.reason = None
        self.package_health = 2 if mode == "post" else 0
        self.last_post = set()
        self.airtime = 0.0
        self.rollover_time = 0.0
        self.refuel_amount = 0.0
        self.refuel_until = 0.0
        self.pickups = {}
        self.collected = set()
        self.recorder = ReplayRecorder()
        self.recorder.capture(0, self.vehicle.pose())

    @property
    def score(self):
        return int(self.distance) + self.coins * 5

    def _spawn_sector(self, sector):
        base = sector * SECTOR_WIDTH
        items = []
        for start in (490, 1080, 1900):
            for gap in (0, 68, 136):
                x = base + start + gap
                items.append(Pickup("coin", x, self.terrain.height_at(x) - 37))
        fuel_x = base + 1580
        items.append(Pickup("fuel", fuel_x, self.terrain.height_at(fuel_x) - 27))
        return items

    def nearby_pickups(self, left, right):
        sectors = range(max(0, int(left // SECTOR_WIDTH)), max(0, int(right // SECTOR_WIDTH) + 1))
        for index in tuple(self.pickups):
            if index not in sectors:
                del self.pickups[index]
        for index in sectors:
            if index not in self.pickups:
                self.pickups[index] = self._spawn_sector(index)
            for item in self.pickups[index]:
                if left <= item.x <= right and (item.kind, item.x) not in self.collected:
                    yield item

    def nearby_posts(self, left, right):
        if self.mode == "post":
            first = max(1, int(left // POST_SPACING))
            last = int(right // POST_SPACING)
            for number in range(first, last + 1):
                x = POST_SPACING * number
                if left <= x <= right:
                    yield x

    def _collect(self):
        car = self.vehicle
        # Nærhet rundt karosseriet tar med både landinger og rolig kjøring.
        for item in list(self.nearby_pickups(car.x - 54, car.x + 54)):
            if abs(item.y - (car.y - 10)) <= 35:
                self.collected.add((item.kind, item.x))
                if item.kind == "coin":
                    self.coins += 5
                else:
                    amount = min(24, self.capacity - self.fuel)
                    self.fuel += amount
                    if amount >= 0.5:
                        self.refuel_amount = amount
                        self.refuel_until = self.elapsed + 1.5

    def _update_post(self, dt):
        car = self.vehicle
        if car.grounded:
            if self.airtime > 0.12 and car.landing_impact >= HARD_LANDING and self.package_health:
                self.package_health -= 1
            self.airtime = 0.0
        else:
            self.airtime += dt
        for x in self.nearby_posts(car.x - 36, car.x + 36):
            if x in self.last_post or abs(self.terrain.height_at(x) - car.y) > 86:
                continue
            self.last_post.add(x)
            if self.package_health > 0:
                self.deliveries += 1
                self.coins += POST_BONUS
            self.package_health = 2

    def step(self, dt, keys):
        if self.reason:
            return
        self.vehicle.update(dt, keys, self.terrain)
        self.elapsed += dt
        self.distance = max(self.distance, (self.vehicle.x - START_X) / PIXELS_PER_METRE)
        accelerating = keys[pg.K_d] or keys[pg.K_RIGHT] or keys[pg.K_a] or keys[pg.K_LEFT]
        burn = (0.8 + 1.8 * accelerating) * self.vehicle.spec.fuel_use
        self.fuel = max(0, self.fuel - burn * dt)
        self._collect()
        if self.mode == "post":
            self._update_post(dt)
        car = self.vehicle
        overturned = cos(car.angle) < -0.5 and car.body_contact
        self.rollover_time = self.rollover_time + dt if overturned else max(0, self.rollover_time - dt)
        if self.rollover_time >= 0.75:
            self.reason = "Bilen veltet"
        elif self.fuel <= 0:
            self.reason = "Tom for drivstoff"
        self.recorder.capture(self.elapsed, car.pose())
