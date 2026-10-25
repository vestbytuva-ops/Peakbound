
import pygame as pg


class Vehicle:
    def __init__(self, x, y):
        # Position
        self.x = x
        self.y = y

        self.width = 80
        self.height = 35

        self.speed = 0
        self.acceleration = 200
        self.max_speed = 400
        self.friction = 120

        self.color = (220, 50, 50)

    def update(self, dt, keys):
        if keys[pg.K_d]:
            self.speed += self.acceleration * dt

        elif keys[pg.K_a]:
            self.speed -= self.acceleration * dt

        else:
            if self.speed > 0:
                self.speed = max(
                    0, self.speed - self.friction * dt
                )

            elif self.speed < 0:
                self.speed = min(
                    0, self.speed + self.friction * dt
                )

        self.speed = max(
            -self.max_speed,
            min(self.speed, self.max_speed)
        )

        self.x += self.speed * dt

    def draw(self, screen):

        pg.draw.rect(
            screen,
            self.color,
            (int(self.x), int(self.y),
             self.width, self.height),
            border_radius=5
        )

        wheel_color = (30, 30, 30)

        pg.draw.circle(
            screen, wheel_color,
            (int(self.x + 18), int(self.y + 35)), 12
        )

        pg.draw.circle(
            screen, wheel_color,
            (int(self.x + 62), int(self.y + 35)), 12
        )
