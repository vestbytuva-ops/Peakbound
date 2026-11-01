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
    