import math
from pathlib import Path

import pygame as pg


class Vehicle:
    # Piksler og sekunder. Juster disse verdiene for å endre kjørefølelsen.
    GRAVITY = 620.0
    DRIVE_ACCELERATION = 470.0
    BRAKE_ACCELERATION = 670.0
    REVERSE_ACCELERATION = 350.0
    DRIVE_SPEED = 510.0
    REVERSE_SPEED = 190.0
    ROLLING_DRAG = 0.08
    AIR_DRAG = 0.025
    AIR_TILT = 2.8
    INVERSE_INERTIA = 1 / 1700
    MAX_STEP = 1 / 240

    def __init__(self, x, y):
        # Bilens midtpunkt ligger i samme høyde som hjulakslingene.
        self.x, self.y = float(x), float(y)
        self.velocity = pg.Vector2()
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.wheel_angle = 0.0
        self.wheel_speed = 0.0
        self.grounded = False
        self.wheel_radius = 13
        self.half_wheelbase = 40
        self.wheels = [(x - self.half_wheelbase, y), (x + self.half_wheelbase, y)]

        folder = Path(__file__).resolve().parents[1] / "assets" / "vehicles"
        body = pg.image.load(folder / "Car.png").convert_alpha()
        tire = pg.image.load(folder / "Tire.png").convert_alpha()
        self.body = pg.transform.smoothscale(body, (128, 64))
        self.tire = pg.transform.smoothscale(tire, (26, 26))

    @property
    def speed(self):
        return self.velocity.x

    @speed.setter
    def speed(self, value):
        self.velocity.x = value

    def snap_to_ground(self, terrain):
        """Setter bilen på bakken ved start og omstart."""
        left = terrain.height_at(self.x - self.half_wheelbase)
        right = terrain.height_at(self.x + self.half_wheelbase)
        self.angle = math.atan2(right - left, 2 * self.half_wheelbase)
        self.y = (left + right) / 2 - self.wheel_radius
        self.velocity.update(0, 0)
        self.angular_velocity = 0.0
        self.grounded = self._resolve_contacts(terrain)
        self._update_wheel_positions()

    def _update_wheel_positions(self):
        half_x = self.half_wheelbase * math.cos(self.angle)
        half_y = self.half_wheelbase * math.sin(self.angle)
        self.wheels = [(self.x - half_x, self.y - half_y),
                       (self.x + half_x, self.y + half_y)]

    def _ground_contact(self, terrain, local_x, local_y, radius):
        # Roter kontaktpunktet med karosseriet, og finn den lokale flaten.
        offset = pg.Vector2(local_x, local_y).rotate_rad(self.angle)
        x, y = self.x + offset.x, self.y + offset.y
        gap = terrain.height_at(x) - y
        if gap > radius + 8:
            return None

        slope = terrain.slope_at(x)
        surface_x = x - gap * slope / (1 + slope * slope)
        normal = pg.Vector2(terrain.slope_at(surface_x), -1).normalize()
        separation = pg.Vector2(x - surface_x, y - terrain.height_at(surface_x))
        penetration = radius - separation.dot(normal)
        if penetration < 0:
            return None
        return offset, normal, penetration

    def _resolve_contacts(self, terrain):
        wheelbase = self.half_wheelbase
        radius = self.wheel_radius
        # Hjørnene beskytter også karosseriet ved en hard landing.
        points = [(-wheelbase, 0, radius), (wheelbase, 0, radius),
                  (-53, -8, 0), (57, -8, 0), (-30, -38, 0), (30, -38, 0)]
        grounded = False
        for _ in range(4):
            found_contact = False
            for index, point in enumerate(points):
                contact = self._ground_contact(terrain, *point)
                if contact is None:
                    continue
                found_contact = True
                grounded |= index < 2
                offset, normal, penetration = contact
                lever = offset.cross(normal)
                effective_mass = 1 + lever * lever * self.INVERSE_INERTIA
                # Bakken skyver bilen ut ved treff, men kan ikke dra den ned.
                normal_speed = self.velocity.dot(normal) + lever * self.angular_velocity
                if normal_speed < 0:
                    impulse = -normal_speed / effective_mass
                    self.velocity += impulse * normal
                    self.angular_velocity += impulse * lever * self.INVERSE_INERTIA
                correction = max(0, penetration - 0.18) * 0.65 / effective_mass
                self.x += normal.x * correction
                self.y += normal.y * correction
                self.angle += lever * correction * self.INVERSE_INERTIA
            if not found_contact:
                break
        return grounded

    def _step(self, dt, throttle, tilt, terrain):
        self.velocity.y += self.GRAVITY * dt
        if self.grounded:
            tangent = pg.Vector2(1, terrain.slope_at(self.x)).normalize()
            forward_speed = self.velocity.dot(tangent)
            if throttle:
                speed_in_direction = forward_speed * throttle
                if speed_in_direction < -8:
                    acceleration = self.BRAKE_ACCELERATION
                else:
                    limit = self.DRIVE_SPEED if throttle > 0 else self.REVERSE_SPEED
                    strength = self.DRIVE_ACCELERATION if throttle > 0 else self.REVERSE_ACCELERATION
                    power = max(0.0, min(1.0, (limit - speed_in_direction) / 70))
                    acceleration = strength * power
                self.velocity += tangent * (acceleration * throttle * dt)
            self.velocity *= math.exp(-self.ROLLING_DRAG * dt)
            self.angular_velocity *= math.exp(-3.6 * dt)
        else:
            self.velocity *= math.exp(-self.AIR_DRAG * dt)
            self.angular_velocity += tilt * self.AIR_TILT * dt
            self.angular_velocity *= math.exp(-0.55 * dt)
        self.angular_velocity = max(-4.0, min(4.0, self.angular_velocity))

        self.x += self.velocity.x * dt
        self.y += self.velocity.y * dt
        self.angle += self.angular_velocity * dt
        self.grounded = self._resolve_contacts(terrain)

        if self.grounded:
            tangent = pg.Vector2(1, terrain.slope_at(self.x)).normalize()
            self.wheel_speed = self.velocity.dot(tangent)
        else:
            self.wheel_speed *= math.exp(-0.15 * dt)
        self.wheel_angle = (self.wheel_angle - math.degrees(self.wheel_speed * dt / self.wheel_radius)) % 360

    def update(self, dt, keys, terrain):
        gas = keys[pg.K_d] or keys[pg.K_RIGHT]
        reverse = keys[pg.K_a] or keys[pg.K_LEFT]
        throttle = int(gas) - int(reverse)
        tilt = int(keys[pg.K_e]) - int(keys[pg.K_q])

        # Små tidssteg gjør landingene stabile også ved lav bildefrekvens.
        remaining = max(0.0, min(dt, 0.05))
        while remaining > 1e-9:
            step = min(remaining, self.MAX_STEP)
            self._step(step, throttle, tilt, terrain)
            remaining -= step
        self.angle = (self.angle + math.pi) % math.tau - math.pi
        self._update_wheel_positions()

    def draw(self, screen, camera_x=0):
        wheel = pg.transform.rotate(self.tire, self.wheel_angle)
        for x, y in self.wheels:
            center = (round(x - camera_x), round(y))
            screen.blit(wheel, wheel.get_rect(center=center))

        # Hjulfestene ligger 24 piksler under karosseribildets midtpunkt.
        body_x = self.x + 24 * math.sin(self.angle) - camera_x
        body_y = self.y - 24 * math.cos(self.angle)
        body = pg.transform.rotate(self.body, -math.degrees(self.angle))
        screen.blit(body, body.get_rect(center=(round(body_x), round(body_y))))
