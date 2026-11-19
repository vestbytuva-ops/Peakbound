from pathlib import Path

import pygame as pg


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "scenery"


def load_sprite(name, height):
    image = pg.image.load(ASSET_DIR / name).convert_alpha()
    bounds = image.get_bounding_rect()
    image = image.subsurface(bounds)
    width = round(height * image.get_width() / image.get_height())
    return pg.transform.smoothscale(image, (width, height))


def make_tree(height):
    trunk = load_sprite("tree-part1.png", round(height * 0.53))
    crown = load_sprite("tree-part2.png", round(height * 0.62))
    tree = pg.Surface((max(trunk.get_width(), crown.get_width()), height), pg.SRCALPHA)
    tree.blit(trunk, trunk.get_rect(midbottom=tree.get_rect().midbottom))
    tree.blit(crown, crown.get_rect(midtop=tree.get_rect().midtop))
    return tree


class Scenery:
    def __init__(self, width, height, terrain):
        sky = pg.image.load(ASSET_DIR / "super-countryside-day-sky.png").convert()
        sky_height = max(round(height * 1.22), round(width * sky.get_height() / sky.get_width()))
        sky_width = round(sky_height * sky.get_width() / sky.get_height())
        self.sky = pg.transform.smoothscale(sky, (sky_width, sky_height))
        self.sky_x = (width - sky_width) // 2
        self.cloud = load_sprite("sky-cloud.png", 48)
        self.cloud.set_alpha(205)
        self.cloud_width = width + 480
        self.layers = []
        for file_name, speed, y, scale, opacity in (
            ("super-countryside-day-parallax2.png", 0.15, 0.18, 0.86, 229),
            ("super-countryside-day-parallax.png", 0.29, 0.19, 1.0, 203),
        ):
            image = pg.image.load(ASSET_DIR / file_name).convert_alpha()
            layer_width = round(width * scale)
            layer_height = round(layer_width * image.get_height() / image.get_width())
            image = pg.transform.smoothscale(image, (layer_width, layer_height))
            image.set_alpha(opacity)
            self.layers.append((image, speed, round(y * height)))

        trees = {
            "small": make_tree(85),
            "medium": make_tree(107),
            "large": make_tree(128),
        }
        bush = load_sprite("action-bush.png", 31)
        rock = load_sprite("rock-small.png", 21)
        finish = load_sprite("finishline-front.png", 124)
        placements = [
            (260, trees["medium"]), (383, bush), (514, trees["small"]),
            (1040, rock), (1280, trees["large"]), (1365, trees["small"]),
            (1480, bush), (1990, trees["medium"]), (2175, bush),
            (2420, rock), (2830, trees["small"]), (3010, trees["large"]),
            (3095, bush), (3350, rock), (3890, trees["medium"]),
            (4060, trees["large"]), (4170, bush), (4520, trees["small"]),
            (4870, rock), (5105, trees["medium"]),
            (terrain.length - 420, finish), (terrain.length - 155, trees["large"]),
        ]
        self.props = []
        for x, sprite in placements:
            y = round(terrain.height_at(x))
            self.props.append((sprite, sprite.get_rect(midbottom=(x, y + 4))))

    def draw_background(self, screen, camera_x):
        screen.blit(self.sky, (self.sky_x, 0))
        for x, y in ((265, 54), (750, 87), (1230, 43), (1620, 103)):
            position = (x - camera_x * 0.08) % self.cloud_width - self.cloud.get_width()
            screen.blit(self.cloud, (round(position), y))
        for image, speed, y in self.layers:
            tile_width = image.get_width()
            offset = round(camera_x * speed) % tile_width
            for x in range(-offset, screen.get_width(), tile_width):
                screen.blit(image, (x, y))

    def draw_props(self, screen, camera_x):
        shift = -round(camera_x)
        for image, world_rect in self.props:
            position = world_rect.move(shift, 0)
            if position.right >= 0 and position.left < screen.get_width():
                screen.blit(image, position)
