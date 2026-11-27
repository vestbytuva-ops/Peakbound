from bisect import bisect_right
from collections import OrderedDict
from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path
import random

import pygame as pg


Color = tuple[int, int, int]
STAGES = Path(__file__).resolve().parents[1] / "assets" / "stages"
CHUNK_WIDTH = 640
GRASS_EDGE = 11


@dataclass(frozen=True)
class WorldSpec:
    id: str
    name: str
    description: str
    difficulty: str
    accent: Color
    seed: int
    spacing: int
    crest: int
    valley: int
    radius: int
    sky: tuple[Color, Color]
    far_rock: Color
    near_rock: Color
    soil: tuple[Color, Color, Color]
    surface: Color


WORLDS = {
    "everest": WorldSpec(
        "everest", "Mount Everest", "Snødekte rygger og lange svev.", "Middels",
        (167, 221, 238), 4831, 477, 365, 522, 208,
        ((62, 103, 152), (203, 228, 237)), (128, 166, 190), (88, 124, 150),
        ((78, 97, 120), (95, 117, 139), (66, 83, 105)), (207, 229, 237),
    ),
    "k2": WorldSpec(
        "k2", "K2", "Brattere kneiker og tett på toppene.", "Vanskelig",
        (252, 180, 143), 7141, 433, 366, 534, 170,
        ((55, 55, 104), (253, 188, 153)), (139, 118, 160), (81, 81, 129),
        ((54, 54, 76), (77, 73, 98), (46, 44, 66)), (189, 202, 229),
    ),
    "kilimanjaro": WorldSpec(
        "kilimanjaro", "Kilimanjaro", "Brede rygger over en gyllen slette.", "Lett",
        (239, 195, 119), 5189, 573, 381, 507, 260,
        ((92, 166, 179), (250, 218, 159)), (155, 153, 138), (120, 123, 98),
        ((108, 71, 47), (135, 90, 53), (94, 61, 45)), (190, 157, 83),
    ),
    "fjellveien": WorldSpec(
        "fjellveien", "Fjellveien", "Den opprinnelige banen, nå uten ende.", "Lett",
        (165, 207, 124), 3041, 520, 380, 515, 230,
        ((116, 176, 208), (222, 236, 206)), (145, 174, 158), (103, 140, 104),
        ((95, 72, 49), (125, 94, 58), (75, 59, 42)), (145, 174, 72),
    ),
}

# Den håndlagde Fjellveien ligger først. Deretter fortsetter genererte bakker.
FJELLVEIEN = (
    (0, 505, 0), (360, 505, 0), (795, 396, 1 / 205), (1245, 513, -1 / 295),
    (1750, 366, 1 / 180), (2240, 531, -1 / 300), (2675, 406, 1 / 177),
    (3115, 493, -1 / 330), (3640, 350, 1 / 167), (4170, 512, -1 / 245),
    (4705, 397, 1 / 190), (5220, 505, 0), (6020, 505, 0),
)
FJELL_X = tuple(point[0] for point in FJELLVEIEN)


def _curve(start, end):
    x1, y1, curvature1 = start
    x2, y2, curvature2 = end
    width = x2 - x1
    change = y2 - y1
    q1 = curvature1 * width ** 2
    q2 = curvature2 * width ** 2
    # Nabostykker har samme høyde, stigning og krumming i skjøtene.
    return (
        x1, width, y1, q1 / 2,
        10 * change - 1.5 * q1 + 0.5 * q2,
        -15 * change + 1.5 * q1 - q2,
        6 * change - 0.5 * q1 + 0.5 * q2,
    )


FJELL_CURVES = tuple(_curve(a, b) for a, b in zip(FJELLVEIEN, FJELLVEIEN[1:]))


def _start_x(world_id):
    return FJELLVEIEN[-1][0] if world_id == "fjellveien" else 350


@lru_cache(maxsize=512)
def _profile_point(world_id, index):
    world = WORLDS[world_id]
    start_x = _start_x(world_id)
    if index == 0:
        return start_x, 505, 0

    # Hvert punkt har sin egen seed. Rekkefølgen spillet besøker dem påvirker ikke banen.
    rng = random.Random(world.seed + 1009 * index)
    x = start_x + index * world.spacing + rng.randint(-34, 34)
    if index % 2:
        return x, world.crest + rng.randint(-12, 14), 1 / (world.radius + rng.randint(-16, 16))
    return x, world.valley + rng.randint(-15, 14), -1 / (world.radius + rng.randint(25, 95))


@lru_cache(maxsize=512)
def _generated_curve(world_id, index):
    return _curve(_profile_point(world_id, index), _profile_point(world_id, index + 1))


class Terrain:
    def __init__(self, world_id="everest"):
        self.world = WORLDS[world_id]
        self.top = 270
        self._chunks = OrderedDict()
        self.render_scale = 1 if world_id == "fjellveien" else 2
        if world_id == "fjellveien":
            self.ground = pg.image.load(STAGES / "terrain-ground.png").convert()
            self.edge = pg.image.load(STAGES / "terrain-surface.png").convert_alpha()
            self.edge_y = GRASS_EDGE
        else:
            self.ground = self._make_ground()
            self.edge = self._make_edge()
            self.edge_y = 2

    def _curve_at(self, x):
        if self.world.id == "fjellveien" and x < FJELLVEIEN[-1][0]:
            return FJELL_CURVES[bisect_right(FJELL_X, x) - 1]
        start = _start_x(self.world.id)
        if x < start:
            return None
        index = int((x - start) // self.world.spacing)
        if x < _profile_point(self.world.id, index)[0]:
            index -= 1
        elif x >= _profile_point(self.world.id, index + 1)[0]:
            index += 1
        return _generated_curve(self.world.id, index)

    def height_at(self, x):
        if x <= 0:
            return 505
        curve = self._curve_at(x)
        if curve is None:
            return 505
        start, width, y, a2, a3, a4, a5 = curve
        t = (x - start) / width
        return y + t * t * (a2 + t * (a3 + t * (a4 + t * a5)))

    def slope_at(self, x):
        if x <= 0:
            return 0.0
        curve = self._curve_at(x)
        if curve is None:
            return 0.0
        start, width, _, a2, a3, a4, a5 = curve
        t = (x - start) / width
        return t * (2 * a2 + t * (3 * a3 + t * (4 * a4 + t * 5 * a5))) / width

    def _make_ground(self):
        ground = pg.Surface((320, 128)).convert()
        base, light, shade = {
            "everest": ("#465a60", "#52676a", "#3f525a"),
            "k2": ("#504a60", "#5e566c", "#474155"),
            "kilimanjaro": ("#6a593f", "#78664a", "#615239"),
        }[self.world.id]
        ground.fill(base)
        # Brede steinlag og noen korte bruddflater, malt på 2-pikselruten.
        bands = [
            [(0, 27), (47, 26), (96, 22), (133, 23), (190, 30), (225, 31), (273, 27),
             (319, 27), (319, 30), (265, 32), (221, 34), (181, 34), (132, 25), (89, 25), (0, 30)],
            [(0, 86), (64, 83), (113, 85), (149, 84), (201, 79), (239, 78), (281, 84),
             (319, 86), (319, 88), (264, 88), (237, 82), (203, 82), (148, 89), (75, 86), (0, 88)],
        ]
        for band in bands:
            pg.draw.polygon(ground, shade, band)
        for x, y, width in [(18, 61, 18), (73, 37, 13), (126, 107, 31), (183, 45, 20),
                            (245, 109, 17), (279, 54, 23), (300, 96, 10)]:
            pg.draw.lines(ground, light, False, [(x, y+2), (x+width//3, y), (x+width, y)])
            pg.draw.line(ground, shade, (x+width//4, y+3), (x+width+2, y+3))
        return ground

    def _make_edge(self):
        edge = pg.Surface((320, 9), pg.SRCALPHA)
        top, middle, dark = {
            "everest": ("#e1e2ce", "#a4b9b4", "#789097"),
            "k2": ("#e9d9ca", "#b5a9ba", "#817b95"),
            "kilimanjaro": ("#e2c68b", "#a98958", "#947349"),
        }[self.world.id]
        edge.fill(top, (0, 2, 320, 2))
        edge.fill(middle, (0, 4, 320, 2))
        edge.fill(dark, (0, 6, 320, 1))
        for x, size in [(8, 16), (43, 8), (70, 14), (99, 9), (127, 20), (164, 6), (200, 16),
                        (243, 12), (271, 7), (307, 11)]:
            pg.draw.line(edge, top, (x, 1), (x+size, 1))
            pg.draw.line(edge, dark, (x+4, 7), (x+size+3, 7))
        return edge

    def _build_chunk(self, index, height):
        scale = self.render_scale
        width = CHUNK_WIDTH // scale
        height = (height + scale - 1) // scale
        start = index * width
        image = pg.Surface((width, height), pg.SRCALPHA)
        ground_w, ground_h = self.ground.get_size()
        for x in range(-(start % ground_w), width, ground_w):
            for y in range(0, height, ground_h):
                image.blit(self.ground, (x, y))
        outline = [(x, round((self.height_at((start + x) * scale) - self.top) / scale))
                   for x in range(width)]
        pg.draw.polygon(image, (0, 0, 0, 0), [(0, 0), (width - 1, 0)] + outline[::-1])
        edge_w, edge_h = self.edge.get_size()
        for x, y in outline:
            area = ((start + x) % edge_w, 0, 1, edge_h)
            image.blit(self.edge, (x, y - self.edge_y), area)
        return image if scale == 1 else pg.transform.scale(image, (CHUNK_WIDTH, height * scale))

    def draw(self, screen, camera_x):
        left = self.render_scale * round(camera_x / self.render_scale)
        height = max(1, screen.get_height() - self.top)
        first = left // CHUNK_WIDTH
        last = (left + screen.get_width() - 1) // CHUNK_WIDTH
        for index in range(first, last + 1):
            key = (index, height)
            if key not in self._chunks:
                self._chunks[key] = self._build_chunk(index, height)
                if len(self._chunks) > 10:
                    self._chunks.popitem(last=False)
            self._chunks.move_to_end(key)
            screen.blit(self._chunks[key], (index * CHUNK_WIDTH - left, self.top))
