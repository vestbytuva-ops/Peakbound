import pygame as pg

class Terrain:
    def __init__(self):
        self.points = [
         (0, 500), (400, 500), (800, 390),
            (1200, 470), (1550, 330), (1950, 500),
            (2400, 400), (2900, 500), (3300, 370),
            (3800, 470), (4200, 350), (4700, 500),
            (5200, 500),   
        ]

        #hentet fra tutorial
        self.lenght = self.points[-1][0]

    def height_at(self, x)
    #prøver å finne bakkhøyden ved en bestemt x akse posisjon
    x = max(0, min(x,self.lenght))

    for (x1, y1), (x2, y2) in zip(
            self.points, self.points[1:]
        ):
            if x1 <= x <= x2:
                fraction = (x - x1) / (x2 - x1)
                return y1 + (y2 - y1) * fraction
            return self.points[-1][1]
    
    def draw(self, screen, camera_x):
        points = [
            (round(x - camera_x), y)
            for x, y in self.points
        ]

        bottom = screen.get_height()

        ground = points + [
            (points[-1][0], bottom),
            (points[0][0], bottom),
        ]

        pg.draw.polygon(screen, (120, 85, 55), ground)
        pg.draw.lines(
            screen, (65, 150, 70), False, points, 6
        )