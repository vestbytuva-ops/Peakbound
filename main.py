import pygame as pg

from game.game import Game


WIDTH = 1280
HEIGHT = 720
FPS = 60


def fit_viewport(size):
    return pg.Rect(0, 0, WIDTH, HEIGHT).fit(pg.Rect((0, 0), size))


def game_event(event, viewport):
    if event.type not in (pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
        return event
    x, y = event.pos
    position = ((x - viewport.x) * WIDTH // max(1, viewport.width),
                (y - viewport.y) * HEIGHT // max(1, viewport.height))
    return pg.event.Event(event.type, {**event.dict, "pos": position})


def main():
    pg.init()
    try:
        window = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
        screen = pg.Surface((WIDTH, HEIGHT)).convert()
        pg.display.set_caption("Peakbound")
        clock = pg.time.Clock()
        game = Game(WIDTH, HEIGHT)
        game.draw(screen)
        window.blit(screen, (0, 0))
        pg.display.flip()
        while game.running:
            dt = clock.tick(FPS) / 1000
            for event in pg.event.get():
                viewport = fit_viewport(window.get_size())
                game.handle_event(game_event(event, viewport))
                if not game.running:
                    break
            if not game.running:
                break
            game.update(dt, pg.key.get_pressed())
            game.draw(screen)
            viewport = fit_viewport(window.get_size())
            if viewport.size == (WIDTH, HEIGHT) and viewport.topleft == (0, 0):
                window.blit(screen, (0, 0))
            elif viewport.width > 0 and viewport.height > 0:
                window.fill((13, 21, 28))
                window.blit(pg.transform.scale(screen, viewport.size), viewport)
            pg.display.flip()
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
