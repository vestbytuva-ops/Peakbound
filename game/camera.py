import math


class Camera:
    def __init__(self, width):
        self.width = width
        self.x = 0.0

    def update(self, dt, car_x):
        # Vis mer bane foran bilen. Kameraet kan følge bilen forbi målflagget.
        if car_x < self.width * 0.10:
            target = car_x - self.width * 0.10
        else:
            target = max(0, car_x - self.width * 0.34)
        self.x += (target - self.x) * (1 - math.exp(-7 * dt))
