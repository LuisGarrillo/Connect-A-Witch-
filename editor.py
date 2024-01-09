import pygame, sys
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images

RENDER_SCALE = 2.0

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("editor")

        self.screen = pygame.display.set_mode((960, 540))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()
        
        self.assets = {
            "grass": load_images("tiles/grass"),
            "pink": load_images("tiles/pink"),
            "blue": load_images("tiles/blue"),
            "pink_border": load_images("tiles/pink_border"),
            "blue_border": load_images("tiles/blue_border"),
            "yellow_key_door":load_images("tiles/yellow_key_door"),
        }
        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=48)
        try:
            self.tilemap.load("data/map.json")
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.on_grid = True

    def run(self) -> None:
        counter = 0
        while True:
            self.display.fill((0, 0, 0))
            
            self.scroll[0] += (self.movement[0] - self.movement[1]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2] ) * 2 
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_image.set_alpha(100)

            mouse_position = pygame.mouse.get_pos()
            mouse_position = (mouse_position[0] / RENDER_SCALE, mouse_position[1] / RENDER_SCALE)
            tile_position = (int((mouse_position[0] + self.scroll[0]) // self.tilemap.size), int((mouse_position[1] + self.scroll[1]) // self.tilemap.size)) 
            print(tile_position) if counter % 60 == 0 else None
            self.display.blit(current_tile_image, (5,5))
            if self.on_grid:
                self.display.blit(current_tile_image, (tile_position[0] * self.tilemap.size - self.scroll[0], tile_position[1] * self.tilemap.size - self.scroll[1]))
            else:
                self.display.blit(current_tile_image, mouse_position)

            if self.clicking and self.on_grid:
                self.tilemap.tilemap[str(tile_position[0]) + ";" + str(tile_position[1])] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_variant,
                    "pos": tile_position
                }
            if self.right_clicking :
                tile_location = str(tile_position[0]) + ";" + str(tile_position[1])
                if tile_location in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_location]

                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_image = self.assets[tile["type"]][tile["variant"]]
                    tile_rectangle = pygame.Rect(tile["pos"][0] - self.scroll[0], tile["pos"][1] - self.scroll[1], tile_image.get_width(), tile_image.get_height())
                    
                    if tile_rectangle.collidepoint(mouse_position):
                        self.tilemap.offgrid_tiles.remove(tile)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.on_grid:
                            self.tilemap.offgrid_tiles.append({
                                "type": self.tile_list[self.tile_group],
                                "variant": self.tile_variant,
                                "pos": (mouse_position[0] + self.scroll[0], mouse_position[1] + self.scroll[1])
                            })
                    if event.button == 3:
                        self.right_clicking = True

                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                        if event.button == 5:
                            self.tile_variant = 0
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        self.movement[0] = True
                    if event.key == pygame.K_a:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        self.on_grid = not self.on_grid
                    if event.key == pygame.K_o:
                        self.tilemap.save("data/map.json")
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_d:
                        self.movement[0] = False
                    if event.key == pygame.K_a:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
            counter+= 1

Game().run()