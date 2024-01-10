import pygame, json

PHYSICS_TILES = {"grass", "stone", "pink", "blue", "yellow_key_door"}
MAGIC_TILES = {"pink", "blue"}
NEIGHBOR_OFFSETS = [
    (-1, 0), (-1, -1), (0, -1), (0, 0), (0, 1), (1, 1), (1, 0), (-1, 1), (1, -1)
]

class Tilemap:
    def __init__(self, game, tile_size=16) -> None:
        self.game = game
        self.tilemap = {}
        self.enemy_spawner = []
        self.offgrid_tiles = []
        self.size = tile_size
    
    def load(self, path):
        with open(path, "r") as file:
            map_data = json.load(file)

        self.tilemap = map_data["tilemap"]
        self.size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]

    def save(self, path):
        with open(path, "w") as file:
            json.dump({"tilemap": self.tilemap, "tile_size": self.size, "offgrid": self.offgrid_tiles}, file)

    def extract(self,id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
        
        for location in self.tilemap:
            tile = self.tilemap[location]
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= self.size
                matches[-1]["pos"][1] *= self.size
                if not keep:
                    del self.tilemap["location"]

        return matches
                     

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
    
    def check_below(self, pos, entity_height):
        if entity_height > self.size:
            difference = entity_height - self.size
            tile_location = (int(pos[0] // self.size), int((pos[1] + difference) // self.size))
        else:
            tile_location = (int(pos[0] // self.size), int((pos[1]) // self.size))
        check_position = pos[0] + entity_height
        check_location = str(tile_location[0]) + ";" + str(tile_location[1] + 1)
        if check_location in self.tilemap:
            if self.tilemap[check_location]["type"] in PHYSICS_TILES:
                return (tile_location[1] + 1) * self.size - check_position < 4
            
    def check_tile(self, pos, entity_height):
        if entity_height > self.size:
            difference = entity_height - self.size
            tile_location = (int(pos[0] // self.size), int((pos[1] + difference) // self.size))
        else:
            tile_location = (int(pos[0] // self.size), int((pos[1]) // self.size))
        
        tile_location = str(tile_location[0]) + ";" + str(tile_location[1])

        if tile_location in self.tilemap:
            return self.tilemap[tile_location]["type"]
    
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

    def update_magic_tiles(self):
        for location in self.tilemap:
            tile = self.tilemap[location]
            if self.game.player.projectile_type == "pink":
                if tile["type"] == "pink":
                    self.tilemap[location]["type"] += "_border"
                elif tile["type"] == "blue_border":
                    self.tilemap[location]["type"] = "blue"

            elif self.game.player.projectile_type == "blue":
                if tile["type"] == "blue":
                    self.tilemap[location]["type"] += "_border"
                elif tile["type"] == "pink_border":
                    self.tilemap[location]["type"] = "pink"

    def remove_yellow_door(self):
        for location in self.tilemap.copy():
            tile = self.tilemap[location]
            if tile["type"] == "yellow_key_door":
                del self.tilemap[location]

    def render(self, surface, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surface.blit(
                self.game.assets[tile["type"]][tile["variant"]], 
                (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]) 
            )

        for x in range(offset[0] // self.size - 4, (offset[0] + surface.get_width()) // self.size + 4):
            for y in range(offset[1] // self.size - 4, (offset[1] + surface.get_height()) // self.size + 4):
                location = str(x) + ";" + str(y)

                if location in self.tilemap:
                    tile = self.tilemap[location]
                    surface.blit(
                        self.game.assets[tile["type"]][tile["variant"]],
                        (tile["pos"][0] * self.size - offset[0], tile["pos"][1] * self.size - offset[1])
                    )