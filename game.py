import pygame, sys

from scripts.utils import load_image, load_images, render_text, Animation, Dialogue
from scripts.planets import Planets
from scripts.entities import Player
from scripts.tilemap import Tilemap

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Connect a Witch!")

        self.screen = pygame.display.set_mode((960, 540))
        self.display = pygame.Surface((480, 270))
        self.clock = pygame.time.Clock()

        self.scroll = [0, 0]
        self.playing = True
        self.on_title_sreen = True
        self.on_game = False
        self.on_tutorial = False
        self.game_over = False
        self.advance = False
        self.finished = False

        self.assets = {
            "grass": load_images("tiles/grass"),
            "player/idle": Animation(load_images("entities/player/idle"), 5),
        }
        self.tilemap = Tilemap(self, tile_size=48)
        self.set_up_game_loop()

    def set_up_game_loop(self):
        self.player = Player(self, [50, 80], (48, 64), 3)
        self.horizontal_movement = [False, False]
        self.projectiles = []
        self.explosions = []

        self.enemies = []

    def game_loop(self):
        
        update_movement = ((self.horizontal_movement[1] - self.horizontal_movement[0]) * 3, 0)
        self.player.update(update_movement)
        self.scroll[0] += int((self.player.rect().centerx - self.display.get_width() / 3 - self.scroll[0]) / 30)
        self.tilemap.render(self.display, self.scroll)
        self.player.render(self.display, self.scroll)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.horizontal_movement[0] = True
                if event.key == pygame.K_RIGHT:
                    self.horizontal_movement[1] = True
                if event.key == pygame.K_SPACE:
                    self.player.velocity[1] = -7

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.horizontal_movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.horizontal_movement[1] = False

    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            self.game_loop()
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()