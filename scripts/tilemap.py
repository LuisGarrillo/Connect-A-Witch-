import pygame, json

PHYSICS_TILES = {"grass"}
NEIGHBOR_OFFSETS = [
    (-1, 0), (-1, -1), (0, -1), (0, 0), (0, 1), (1, 1), (1, 0), (-1, 1), (1, -1)
]

class Tilemap:
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tilemap = {}
        self.offgrid_tiles = []
        self.size = tile_size

        for i in range(10):
            self.tilemap[str(i) + ";5"] = {
                "type": "grass",
                "variant": 0,
                "pos": [i, 5]
            }
        for i in range(10):
            self.tilemap[str(i) + ";0"] = {
                "type": "grass",
                "variant": 0,
                "pos": [i, 0]
            }

    def tiles_around(self, pos, entity_height):
        tiles = []
        tile_locations = []
        difference = 0
        tile_locations.append((int(pos[0] // self.size), int((pos[1]) // self.size)))

        if entity_height > self.size:
            difference = entity_height - self.size
            tile_locations.append((int(pos[0] // self.size), int((pos[1] + difference) // self.size)))

        for offset in NEIGHBOR_OFFSETS:
            for tile_location in tile_locations:
                check_location = str(tile_location[0] + offset[0]) + ";" + str(tile_location[1] + offset[1])
                if check_location in self.tilemap:
                    tiles.append(self.tilemap[check_location])
        return tiles
    
    def rects_around(self, pos, entity_height):
        rects = []
        tiles = self.tiles_around(pos, entity_height)
        for tile in tiles:
            if tile["type"] in PHYSICS_TILES:
                rects.append(pygame.Rect(
                    tile["pos"][0] * self.size,
                    tile["pos"][1] * self.size,
                    self.size,
                    self.size
                ))
        return rects

    def render(self, surface, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surface.blit(
                self.game.assets[tile["type"]][tile["variant"]], 
                (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]) 
            )

        for x in range(offset[0] // self.size, (offset[0] + surface.get_width()) // self.size + 1):
            for y in range(offset[1] // self.size, (offset[1] + surface.get_height()) // self.size + 1):
                location = str(x) + ";" + str(y)

                if location in self.tilemap:
                    tile = self.tilemap[location]
                    surface.blit(
                        self.game.assets[tile["type"]][tile["variant"]],
                        (tile["pos"][0] * self.size - offset[0], tile["pos"][1] * self.size - offset[1])
                    )