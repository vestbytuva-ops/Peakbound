from pathlib import Path
import random

import pygame as pg


ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "scenery"
SKYLINE_WIDTH = 896
PROP_SPACING = 910

# Motivene er tegnet i en arbeidsflate på 896 × 360 piksler.
# Flater og snørenner er lagt for hånd, med lys fra øverst til venstre.
MASSIFS = {
    "everest": (
        ("#82989e", [(0, 165), (48, 148), (88, 132), (109, 129), (125, 135), (165, 152),
                     (205, 145), (247, 125), (267, 121), (279, 125), (326, 147),
                     (370, 140), (414, 130), (441, 115), (471, 109), (501, 88), (519, 76),
                     (540, 70), (548, 64), (577, 66), (591, 73), (609, 78), (630, 93),
                     (654, 99), (672, 111), (695, 127), (729, 130), (761, 143), (790, 153),
                     (835, 141), (863, 148), (896, 165), (896, 360), (0, 360)]),
        ("#687f89", [(577, 66), (591, 73), (609, 78), (630, 93), (654, 99), (695, 127),
                     (729, 130), (761, 143), (815, 219), (694, 222), (633, 207), (611, 187),
                     (598, 158), (579, 140), (584, 128), (569, 103)]),
        ("#aab7b7", [(441, 115), (471, 109), (501, 88), (519, 76), (540, 70),
                     (548, 64), (577, 66), (564, 76), (550, 79), (551, 84), (536, 86),
                     (522, 98), (518, 114), (502, 119), (491, 138), (455, 145), (433, 161),
                     (449, 138), (470, 127), (478, 114)]),
        ("#dedbd0", [(507, 85), (519, 76), (540, 70), (548, 64), (577, 66), (586, 71),
                     (566, 70), (557, 82), (539, 82), (537, 91), (525, 89), (516, 96),
                     (519, 86), (500, 92)]),
        ("#bfccca", [(562, 98), (569, 109), (591, 118), (604, 142), (619, 157), (614, 164),
                     (594, 147), (584, 134), (570, 133), (561, 117), (546, 112), (538, 101)]),
        ("#a3b0b0", [(259, 125), (267, 121), (279, 125), (315, 141), (297, 139),
                     (296, 144), (274, 133), (261, 139), (250, 136), (232, 140)]),
        ("#98a8aa", [(612, 108), (646, 114), (662, 127), (683, 141), (667, 140),
                     (664, 134), (642, 128), (633, 121), (622, 122)]),
        ("#9aabb0", [(490, 147), (470, 160), (450, 162), (420, 184), (381, 194),
                     (408, 180), (438, 157), (461, 152), (468, 142)]),
    ),
    "k2": (
        ("#847d8e", [(0, 171), (40, 156), (85, 145), (121, 122), (139, 118), (154, 123),
                     (188, 149), (231, 152), (263, 140), (299, 119), (326, 109),
                     (347, 88), (366, 76), (391, 53), (405, 47), (410, 41), (421, 44),
                     (428, 59), (438, 66), (452, 89), (465, 108), (500, 136), (548, 153),
                     (583, 137), (617, 130), (647, 105), (669, 100), (705, 120), (728, 132),
                     (764, 142), (808, 151), (848, 159), (896, 171), (896, 360), (0, 360)]),
        ("#635f77", [(419, 43), (428, 59), (438, 66), (452, 89), (465, 108), (500, 136),
                     (548, 153), (609, 219), (503, 236), (442, 187), (432, 142), (413, 106),
                     (416, 87), (406, 66)]),
        ("#9d91a1", [(326, 109), (347, 88), (366, 76), (391, 53), (405, 47), (410, 41),
                     (421, 44), (399, 66), (400, 74), (378, 93), (376, 112), (337, 134),
                     (323, 150), (293, 164), (304, 139)]),
        ("#e0c9b4", [(366, 76), (391, 53), (405, 47), (410, 41), (421, 44), (428, 59),
                     (418, 57), (416, 53), (404, 60), (402, 68), (386, 72), (391, 65),
                     (379, 70), (371, 83)]),
        ("#bdabb2", [(413, 63), (429, 75), (436, 100), (445, 111), (455, 129), (446, 124),
                     (435, 112), (431, 110), (426, 93), (421, 93), (416, 81), (410, 77)]),
        ("#b49faa", [(384, 85), (378, 99), (373, 115), (359, 125), (349, 139), (327, 151),
                     (344, 133), (355, 116), (369, 106), (371, 95)]),
        ("#a696a1", [(647, 105), (669, 100), (689, 111), (684, 112), (671, 106),
                     (662, 113), (647, 114), (633, 128), (621, 132)]),
        ("#928498", [(472, 130), (495, 151), (517, 163), (534, 183), (512, 175),
                     (500, 169), (490, 155), (485, 152)]),
    ),
    "kilimanjaro": (
        ("#878b7b", [(0, 176), (42, 167), (88, 157), (126, 162), (157, 153), (196, 133),
                     (242, 122), (279, 111), (319, 105), (340, 102), (372, 103), (401, 100),
                     (438, 101), (462, 97), (486, 99), (519, 105), (539, 112), (572, 117),
                     (605, 144), (635, 149), (661, 158), (694, 156), (736, 162),
                     (782, 169), (828, 167), (896, 176), (896, 360), (0, 360)]),
        ("#777962", [(462, 97), (486, 99), (519, 105), (539, 112), (572, 117), (605, 144),
                     (635, 149), (661, 158), (675, 216), (551, 232), (520, 180), (491, 153),
                     (472, 140), (484, 127)]),
        ("#aaa888", [(196, 133), (242, 122), (279, 111), (319, 105), (340, 102), (372, 103),
                     (401, 100), (438, 101), (462, 97), (482, 100), (450, 113), (409, 117),
                     (369, 120), (354, 129), (303, 134), (285, 141), (232, 146), (186, 155)]),
        ("#e4d8b5", [(279, 111), (319, 105), (340, 102), (372, 103), (401, 100), (438, 101),
                     (462, 97), (486, 99), (519, 105), (527, 108), (490, 108), (479, 105),
                     (459, 111), (421, 109), (412, 114), (391, 111), (375, 117), (351, 115),
                     (337, 119), (314, 116), (303, 123), (283, 122), (294, 115)]),
        ("#969477", [(291, 159), (335, 148), (358, 138), (404, 137), (438, 129), (461, 132),
                     (450, 139), (412, 146), (367, 147), (334, 160), (312, 161)]),
        ("#92917a", [(516, 124), (548, 132), (570, 138), (591, 154), (577, 153),
                     (553, 142), (535, 144), (511, 138)]),
    ),
}

PAL = {
    "everest": ("#98b1b8", "#b0c3c5", "#c7d0cb", "#e1dec9", "#a7bdbf", "#91a8ac",
                "#7f989f", "#698589"),
    "k2": ("#9990a4", "#b6a0ae", "#d5b5b1", "#ead2b8", "#c1a9b4", "#a08e9e",
           "#8a7d92", "#756a82"),
    "kilimanjaro": ("#a1b3a4", "#c4c5a1", "#d8ca9e", "#eee0b7", "#d7d5ae", "#acae87",
                    "#a5a17a", "#909773"),
}

FOOTHILLS = {
    "everest": [(0, 237), (51, 232), (104, 217), (159, 215), (235, 231), (288, 227),
                (364, 212), (403, 224), (464, 227), (539, 215), (597, 217), (669, 225),
                (724, 207), (782, 212), (825, 227), (896, 237)],
    "k2": [(0, 243), (43, 228), (87, 215), (154, 216), (184, 210), (246, 233),
           (292, 239), (354, 228), (419, 228), (484, 213), (513, 208), (582, 229),
           (625, 227), (690, 218), (759, 217), (813, 227), (896, 243)],
    "kilimanjaro": [(0, 231), (84, 223), (165, 225), (231, 219), (287, 222), (373, 232),
                    (472, 231), (524, 224), (594, 225), (649, 219), (738, 218),
                    (814, 227), (896, 231)],
}


def load_sprite(name, height):
    image = pg.image.load(ASSET_DIR / name).convert_alpha()
    image = image.subsurface(image.get_bounding_rect())
    width = round(height * image.get_width() / image.get_height())
    return pg.transform.smoothscale(image, (width, height))


def _double(image):
    return pg.transform.scale(image, (2 * image.get_width(), 2 * image.get_height()))


def _sky(width, height, world_id):
    top, middle, haze, light, cloud, *_ = PAL[world_id]
    image = pg.Surface((width, height)).convert()
    image.fill(top)
    upper_band = 104 if world_id == "k2" else 110
    image.fill(middle, (0, upper_band, width, height - upper_band))
    image.fill(haze, (0, 155, width, height - 155))
    pg.draw.circle(image, light, (116, 84 if world_id != "k2" else 92), 16)
    # Lette, brutte skybånd på den samme pikselruta som resten av bildet.
    for x, y, size in ((29, 112, 107), (204, 76, 73), (389, 117, 80), (531, 56, 74)):
        pg.draw.polygon(image, cloud, [(x, y), (x+12, y-2), (x+29, y-2), (x+35, y-4),
                                      (x+size-17, y-4), (x+size, y), (x+13, y+1)])
        pg.draw.line(image, cloud, (x+size//3, y+5), (x+size-7, y+5))
    return _double(image)


def _far_layer(world_id):
    image = pg.Surface((SKYLINE_WIDTH, 360), pg.SRCALPHA)
    for color, points in MASSIFS[world_id]:
        pg.draw.polygon(image, color, points)
    # Et lavt disdrag demper foten av hovedfjellet.
    haze = PAL[world_id][5]
    pg.draw.polygon(image, haze, [(0, 196), (110, 194), (176, 196), (230, 194), (385, 194),
                                  (411, 197), (598, 198), (663, 195), (792, 197), (896, 196),
                                  (896, 204), (620, 205), (509, 207), (335, 206),
                                  (191, 203), (0, 204)])
    return _double(image)


def _near_layer(world_id):
    image = pg.Surface((SKYLINE_WIDTH, 360), pg.SRCALPHA)
    top, lower = PAL[world_id][-2:]
    points = FOOTHILLS[world_id]
    pg.draw.polygon(image, top, points + [(896, 360), (0, 360)])
    lower_ridge = [(0, 252), (130, 242), (186, 245), (275, 238), (324, 242),
                   (421, 260), (513, 253), (559, 245), (724, 240), (776, 244), (896, 252)]
    pg.draw.polygon(image, lower, lower_ridge + [(896, 360), (0, 360)])
    for x, y, w in ((101, 240, 54), (178, 234, 77), (528, 241, 65), (698, 231, 67)):
        pg.draw.lines(image, top, False, [(x, y+4), (x+16, y), (x+w, y+1)], 2)
    return _double(image)


def _prop_images(world_id):
    # små silhuetter i horisonten; varm farge er forbeholdt spillgjenstander
    images = []
    for kind in ("tent", "stones", "tree" if world_id == "kilimanjaro" else "ridge"):
        image = pg.Surface((46, 36), pg.SRCALPHA)
        deep = PAL[world_id][-1]
        mid = PAL[world_id][-2]
        light = PAL[world_id][5]
        if kind == "tent":
            pg.draw.polygon(image, deep, [(3, 35), (15, 16), (30, 18), (43, 34), (41, 35)])
            pg.draw.polygon(image, mid, [(4, 34), (15, 17), (21, 34)])
            pg.draw.polygon(image, light, [(15, 17), (30, 18), (40, 32), (23, 32)])
            pg.draw.line(image, deep, (14, 25), (13, 34), 2)
        elif kind == "stones":
            pg.draw.polygon(image, deep, [(7, 35), (11, 29), (33, 28), (39, 34), (37, 35)])
            pg.draw.polygon(image, mid, [(12, 31), (17, 25), (30, 24), (34, 28), (31, 31)])
            pg.draw.polygon(image, light, [(17, 26), (20, 21), (30, 22), (31, 25)])
        elif kind == "tree":
            pg.draw.polygon(image, deep, [(19, 35), (20, 22), (14, 16), (19, 16),
                                         (24, 22), (29, 14), (33, 15), (26, 26), (25, 35)])
            pg.draw.polygon(image, mid, [(2, 14), (9, 8), (18, 8), (21, 5), (34, 5),
                                        (42, 8), (44, 14), (41, 17), (14, 17)])
            pg.draw.line(image, light, (11, 9), (32, 8), 2)
        else:
            pg.draw.polygon(image, deep, [(4, 35), (12, 22), (19, 25), (28, 13), (36, 20), (42, 35)])
            pg.draw.lines(image, light, False, [(13, 24), (19, 27), (28, 15), (35, 22)], 2)
        images.append(_double(image.subsurface(image.get_bounding_rect())))
    return images


def _fir(height):
    trunk = load_sprite("tree-part1.png", round(height * 0.52))
    crown = load_sprite("tree-part2.png", round(height * 0.63))
    tree = pg.Surface((max(trunk.get_width(), crown.get_width()), height), pg.SRCALPHA)
    tree.blit(trunk, trunk.get_rect(midbottom=tree.get_rect().midbottom))
    tree.blit(crown, crown.get_rect(midtop=tree.get_rect().midtop))
    return tree


class Scenery:
    def __init__(self, width, height, terrain):
        self.terrain = terrain
        self.world = terrain.world
        self.legacy = self.world.id == "fjellveien"
        if self.legacy:
            self._use_fjellveien_scenery(width, height)
        else:
            world_id = self.world.id
            self.sky = _sky((width + 1) // 2, (height + 1) // 2, world_id)
            self.sky_left = 0
            self.layers = [(_far_layer(world_id), 0.11, 0), (_near_layer(world_id), 0.26, 0)]
            self.props = _prop_images(world_id)

    def _use_fjellveien_scenery(self, width, height):
        sky = pg.image.load(ASSET_DIR / "super-countryside-day-sky.png").convert()
        sky_height = max(round(height * 1.22), width * sky.get_height() // sky.get_width())
        sky_width = round(sky_height * sky.get_width() / sky.get_height())
        self.sky = pg.transform.smoothscale(sky, (sky_width, sky_height))
        self.sky_left = (width - sky_width) // 2
        self.cloud = load_sprite("sky-cloud.png", 44)
        self.cloud.set_alpha(205)
        self.cloud_span = width + 300
        self.layers = []
        for name, rate, y, scale, opacity in (
            ("super-countryside-day-parallax2.png", 0.15, 0.18, 0.86, 229),
            ("super-countryside-day-parallax.png", 0.29, 0.19, 1.0, 203),
        ):
            image = pg.image.load(ASSET_DIR / name).convert_alpha()
            layer_width = round(width * scale)
            layer_height = round(layer_width * image.get_height() / image.get_width())
            image = pg.transform.smoothscale(image, (layer_width, layer_height))
            image.set_alpha(opacity)
            self.layers.append((image, rate, round(y * height)))
        self.props = [_fir(106), _fir(74), load_sprite("rock-small.png", 23),
                      load_sprite("action-bush.png", 28)]

    def draw_background(self, screen, camera_x):
        screen.blit(self.sky, (self.sky_left, 0))
        if self.legacy:
            for x, y in ((230, 55), (710, 110), (1185, 59), (1490, 142)):
                offset = (x - camera_x * 0.07) % self.cloud_span
                screen.blit(self.cloud, (round(offset - self.cloud.get_width()), y))
        for image, rate, y in self.layers:
            width = image.get_width()
            offset = round(camera_x * rate) if self.legacy else 2 * round(camera_x * rate / 2)
            offset %= width
            for x in range(-offset, screen.get_width(), width):
                screen.blit(image, (x, y))

    def draw_props(self, screen, camera_x):
        spacing = 580 if self.legacy else PROP_SPACING
        first = int((camera_x - 190) // spacing)
        last = int((camera_x + screen.get_width() + 190) // spacing)
        for index in range(first, last + 1):
            rng = random.Random(self.world.seed + index * 373)
            x = index * spacing + rng.randint(245, 500)
            image = self.props[rng.randrange(len(self.props))]
            y = round(self.terrain.height_at(x)) + 4
            if self.legacy:
                position = (round(x - camera_x), y)
            else:
                position = (2 * round((x - camera_x) / 2), 2 * round(y / 2))
            screen.blit(image, image.get_rect(midbottom=position))
