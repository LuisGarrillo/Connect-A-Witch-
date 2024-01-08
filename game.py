import pygame, sys

from scripts.utils import load_image, load_images, render_text, Animation, Dialogue
from scripts.planets import Planets
from scripts.entities import Player, Enemy
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
            "player/shooting": Animation(load_images("entities/player/shooting"), 5, loop=False),
            "projectile/pink" : Animation(load_images("projectiles/pink"), 5),
            "projectile/blue" : Animation(load_images("projectiles/blue"), 5),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), 5),
            "enemy/attack": Animation(load_images("entities/enemy/attack"), 5, loop=False),
            "weakness/pink": Animation(load_images("entities/weakness/pink"), 5),
            "weakness/blue": Animation(load_images("entities/weakness/blue"), 5),
        }
        self.ui = {
            "spell/pink": load_image("ui/pink_spell.png"),
            "spell/blue": load_image("ui/blue_spell.png"),
            "staff": load_image("ui/staff.png"),
        }
        self.tilemap = Tilemap(self, tile_size=48)
        self.set_up_game_loop()

    def set_up_game_loop(self):
        self.player = Player(self, [50, 80], (48, 64), 3)
        self.horizontal_movement = [False, False]
        self.projectiles = []
        self.explosions = []

        self.enemies = []
        self.enemies.append(Enemy(self, [400, 80], (48, 64)))

    def game_loop(self):
        
        self.display.blit(self.ui["spell/" + self.player.projectile_type], (16, 16))
        self.display.blit(self.ui["staff"], (16, 16))

        update_movement = ((self.horizontal_movement[1] - self.horizontal_movement[0]) * 3.5, 0)
        self.player.update(update_movement)
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2.5 - self.scroll[0]) / 15
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 1.5 - self.scroll[1])
        self.scroll = [int(self.scroll[0]), int(self.scroll[1])]

        self.tilemap.render(self.display, self.scroll)
        if not self.player.invincibility or self.player.invincibility % 10 == 0:
            self.player.render(self.display, self.scroll)

        for projectile in self.projectiles.copy():
            if projectile.update():
                self.projectiles.remove(projectile)
                continue
            for enemy in self.enemies.copy():
                if projectile.rect().colliderect(enemy.rect()):
                    self.projectiles.remove(projectile)
                    if projectile.type == enemy.weaknesses[0].type:
                        kill = enemy.hit()
                        if kill:
                            self.enemies.remove(enemy)
                    else:
                        enemy.reset()
            projectile.render(self.display, self.scroll)
        
        for enemy in self.enemies.copy():
            enemy.update()
            enemy.render(self.display, self.scroll)
            if enemy.attack_cooldown < 60:
                if enemy.rect().colliderect(self.player.rect()):
                    self.player.hit()

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
                if event.key == pygame.K_f:
                    self.player.shoot()
                if event.key == pygame.K_d:
                    self.player.switch_colors()

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