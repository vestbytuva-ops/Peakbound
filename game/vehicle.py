import math
from pathlib import Path

import pygame as pg


class Vehicle:
    def __init__(self, x, y):
        # Midtpunktet mellom hjulene, målt i banens koordinater.
        self.x, self.y = x, y
        self.angle = 0.0
        self.wheel_angle = 0.0
        self.speed = 0.0
        self.acceleration = 200.0
        self.max_speed = 400.0
        self.friction = 120.0

        folder = Path(__file__).resolve().parent.parent / 'assets' / 'vehicles'
        body = pg.image.load(folder / 'Car.png').convert_alpha()
        tire = pg.image.load(folder / 'Tire.png').convert_alpha()
        self.body = pg.transform.smoothscale(body, (128, 64))
        self.tire = pg.transform.smoothscale(tire, (26, 26))
        self.wheel_radius = 13
        self.half_wheelbase = 40
        # Punkter langs undersiden av et hjul brukes til å finne bakkekontakten.
        self.tire_edge = [(dx, math.sqrt(self.wheel_radius ** 2 - dx ** 2))
                          for dx in range(-self.wheel_radius, self.wheel_radius + 1)]
        self.wheels = [(x - self.half_wheelbase, y), (x + self.half_wheelbase, y)]

    def snap_to_ground(self, terrain):
        # Avstanden mellom hjulene langs x-aksen blir kortere på skrå bakke.
        rear_y = terrain.height_at(self.x - self.half_wheelbase)
        front_y = terrain.height_at(self.x + self.half_wheelbase)
        slope = math.atan2(front_y - rear_y, 2 * self.half_wheelbase)
        half_span = self.half_wheelbase * math.cos(slope)

        self.wheels = []
        for x in (self.x - half_span, self.x + half_span):
            y = min(terrain.height_at(x + dx) - dy for dx, dy in self.tire_edge)
            self.wheels.append((x, y))
        rear, front = self.wheels
        self.y = (rear[1] + front[1]) / 2
        self.angle = math.atan2(front[1] - rear[1], front[0] - rear[0])

    def update(self, dt, keys, terrain):
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            self.speed += self.acceleration * dt
        elif keys[pg.K_a] or keys[pg.K_LEFT]:
            self.speed -= self.acceleration * dt
        elif self.speed > 0:
            self.speed = max(0, self.speed - self.friction * dt)
        else:
            self.speed = min(0, self.speed + self.friction * dt)

        self.speed = max(-self.max_speed, min(self.speed, self.max_speed))
        old_x, old_y = self.x, self.y
        half_width = self.body.get_width() / 2
        target = self.x + self.speed * dt
        self.x = max(half_width, min(target, terrain.length - half_width))
        if self.x != target:
            self.speed = 0.0
        self.snap_to_ground(terrain)

        if self.x != old_x:
            distance = math.hypot(self.x - old_x, self.y - old_y)
            roll = math.copysign(distance / self.wheel_radius, self.x - old_x)
            self.wheel_angle = (self.wheel_angle - math.degrees(roll)) % 360

    def draw(self, screen, camera_x=0):
        wheel = pg.transform.rotate(self.tire, self.wheel_angle)
        for x, y in self.wheels:
            center = (round(x - camera_x), round(y))
            screen.blit(wheel, wheel.get_rect(center=center))

        # Hjulfestene i Car.png ligger 24 piksler under bildets midtpunkt.
        body_x = self.x + 24 * math.sin(self.angle) - camera_x
        body_y = self.y - 24 * math.cos(self.angle)
        body = pg.transform.rotate(self.body, -math.degrees(self.angle))
        screen.blit(body, body.get_rect(center=(round(body_x), round(body_y))))
