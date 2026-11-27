import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pygame as pg


@dataclass(frozen=True)
class VehicleSpec:
    name: str
    image: str
    description: str
    power: float
    speed: float
    grip: float
    fuel_use: float


VEHICLES = {
    "ridge": VehicleSpec("Ridge", "Ridge.png", "Lett bil med høy toppfart.", 470, 510, 1.0, 1.0),
    "tinde": VehicleSpec("Tinde", "Tinde.png", "Sterk i bakker. Bruker mer drivstoff.", 565, 465, 1.20, 1.16),
}


@lru_cache(maxsize=4)
def _sprite(filename, size):
    folder = Path(__file__).resolve().parents[1] / "assets" / "vehicles"
    return pg.transform.scale(pg.image.load(folder / filename).convert_alpha(), size)


@lru_cache(maxsize=4)
def _ghost_sprite(filename, size):
    image = _sprite(filename, size).copy()
    # Fargelås for spøkelsesbilen. Bevar lyse og mørke felt og eksisterende alfa.
    image.fill((125, 191, 215, 255), special_flags=pg.BLEND_RGBA_MULT)
    image.set_alpha(145)
    return image


class Vehicle:
    # Piksler og sekunder. Juster disse verdiene for å endre kjørefølelsen.
    GRAVITY = 620.0
    BRAKE_ACCELERATION = 670.0
    REVERSE_ACCELERATION = 350.0
    REVERSE_SPEED = 190.0
    ROLLING_DRAG = 0.08
    AIR_DRAG = 0.025
    AIR_TILT = 2.8
    INVERSE_INERTIA = 1 / 1700
    MAX_STEP = 1 / 240

    def __init__(self, x, y, vehicle_id="ridge", upgrades=None):
        # Bilens midtpunkt ligger i samme høyde som hjulakslingene.
        self.spec = VEHICLES[vehicle_id]
        levels = upgrades or {}
        self.drive_acceleration = self.spec.power * (1 + 0.10 * levels.get("engine", 0))
        self.drive_speed = self.spec.speed + 18 * levels.get("engine", 0)
        self.grip = self.spec.grip * (1 + 0.10 * levels.get("grip", 0))
        self.x, self.y = float(x), float(y)
        self.velocity = pg.Vector2()
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.wheel_angle = 0.0
        self.wheel_speed = 0.0
        self.grounded = False
        self.landing_impact = 0.0
        self.body_contact = False
        self.wheel_radius = 13
        self.half_wheelbase = 40
        self.wheels = [(x - self.half_wheelbase, y), (x + self.half_wheelbase, y)]

        self.body = _sprite(self.spec.image, (128, 64))
        self.tire = _sprite("Fjellhjul.png", (26, 26))
        self.ghost_body = _ghost_sprite(self.spec.image, (128, 64))
        self.ghost_tire = _ghost_sprite("Fjellhjul.png", (26, 26))

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
                self.body_contact |= index >= 2
                offset, normal, penetration = contact
                lever = offset.cross(normal)
                effective_mass = 1 + lever * lever * self.INVERSE_INERTIA
                # Bakken skyver bilen ut ved treff, men kan ikke dra den ned.
                normal_speed = self.velocity.dot(normal) + lever * self.angular_velocity
                if normal_speed < 0:
                    if index < 2:
                        self.landing_impact = max(self.landing_impact, -normal_speed)
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
                    limit = self.drive_speed if throttle > 0 else self.REVERSE_SPEED
                    strength = self.drive_acceleration if throttle > 0 else self.REVERSE_ACCELERATION
                    power = max(0.0, min(1.0, (limit - speed_in_direction) / 70))
                    acceleration = strength * power
                self.velocity += tangent * (acceleration * self.grip * throttle * dt)
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
        tilt = int(keys[pg.K_e] or keys[pg.K_DOWN]) - int(keys[pg.K_q] or keys[pg.K_UP])
        self.landing_impact = 0.0
        self.body_contact = False

        # Små tidssteg gjør landingene stabile også ved lav bildefrekvens.
        remaining = max(0.0, min(dt, 0.05))
        while remaining > 1e-9:
            step = min(remaining, self.MAX_STEP)
            self._step(step, throttle, tilt, terrain)
            remaining -= step
        self.angle = (self.angle + math.pi) % math.tau - math.pi
        self._update_wheel_positions()

    def pose(self):
        return self.x, self.y, self.angle, self.wheel_angle

    def draw_pose(self, screen, camera_x, pose, ghost=False):
        x, y, angle, wheel_angle = pose
        wheel_art = self.ghost_tire if ghost else self.tire
        body_art = self.ghost_body if ghost else self.body
        wheel = pg.transform.rotate(wheel_art, wheel_angle)
        span_x = self.half_wheelbase * math.cos(angle)
        span_y = self.half_wheelbase * math.sin(angle)
        for direction in (-1, 1):
            center = (round(x + direction * span_x - camera_x), round(y + direction * span_y))
            screen.blit(wheel, wheel.get_rect(center=center))

        # Hjulfestene ligger 24 piksler under karosseribildets midtpunkt.
        body_x = x + 24 * math.sin(angle) - camera_x
        body_y = y - 24 * math.cos(angle)
        body = pg.transform.rotate(body_art, -math.degrees(angle))
        screen.blit(body, body.get_rect(center=(round(body_x), round(body_y))))

    def draw(self, screen, camera_x=0):
        self.draw_pose(screen, camera_x, self.pose())
