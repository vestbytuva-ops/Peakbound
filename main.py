import os
import pygame as pg

from game.game import Game

os.chdir(os.path.dirname(os.path.abspath(__file__)))

WIDTH = 1280
HEIGHT = 720
FPS = 60

def main():
    pg.init()

    screen = pg.display.set_mode((WIDTH,HEIGHT))
    pg.display.set_caption("Peakbound")

    clock = pg.time.Clock()
    game = Game(WIDTH, HEIGHT)

    running = True

    while running:
        dt = clock.tick(FPS)/1000

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
            game.handle_event(event)

        if not running:
            break

        keys = pg.key.get_pressed()

        game.update(dt, keys)

        screen.fill((135,206,235))
        game.draw(screen)

        pg.display.flip()
    pg.quit()

if __name__ == "__main__":
    main()