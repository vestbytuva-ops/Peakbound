import math


class Camera:
    def __init__(self, width):
        self.width = width
        self.x = 0.0

    def update(self, dt, car_x, map_length):
        limit = max(0, map_length - self.width)
        target = max(0, min(car_x - self.width / 3, limit))
        self.x += (target - self.x) * (1 - math.exp(-7 * dt))
