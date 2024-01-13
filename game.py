import pygame, sys

from scripts.utils import load_image, load_images, render_text, load, Animation, Dialogue
from scripts.entities import Player, Enemy, Villager
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
        self.on_title_screen = True
        self.on_game = False
        self.on_tutorial = False
        self.game_over = False
        self.advance = False
        self.on_victory_screen = False

        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.sub_title_font = pygame.font.SysFont("Arial", 20, bold=True)

        self.assets = {
            "background": load_image("background.png"),
            "grass": load_images("tiles/grass"),
            "stone": load_images("tiles/stone"),
            "pink": load_images("tiles/pink"),
            "pink_border": load_images("tiles/pink_border"),
            "blue": load_images("tiles/blue"),
            "blue_border": load_images("tiles/blue_border"),
            "yellow_key_door":load_images("tiles/yellow_key_door"),
            "red_key_door":load_images("tiles/red_key_door"),
            "player/idle": Animation(load_images("entities/player/idle"), 5),
            "player/run": Animation(load_images("entities/player/run"), 5),
            "player/jump": Animation(load_images("entities/player/jump"), 5),
            "player/fall": Animation(load_images("entities/player/fall"), 5),
            "player/shooting": Animation(load_images("entities/player/shooting"), 5, loop=False),
            "projectile/pink" : Animation(load_images("projectiles/pink"), 5),
            "projectile/blue" : Animation(load_images("projectiles/blue"), 5),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), 5),
            "enemy/chase": Animation(load_images("entities/enemy/chase"), 5),
            "enemy/attack": Animation(load_images("entities/enemy/attack"), 60, loop=False),
            "villager/idle": Animation(load_images("entities/villager/idle"), 5),
            "weakness/pink": Animation(load_images("entities/weakness/pink"), 5),
            "weakness/blue": Animation(load_images("entities/weakness/blue"), 5),
        }
        self.ui = {
            "spell/pink": load_image("ui/pink_spell.png"),
            "spell/blue": load_image("ui/blue_spell.png"),
            "staff": load_image("ui/staff.png"),
            "heart": load_image("ui/heart.png"),
            "heartless": load_image("ui/heartless.png"),
            "yellow_key": load_image("ui/yellow_key.png"),
            "red_key": load_image("ui/red_key.png"),
        }

        self.sfx = {
            "jump": pygame.mixer.Sound("data/sfxs/jump.wav"),
            "shoot": pygame.mixer.Sound("data/sfxs/shoot.wav"),
            "switch": pygame.mixer.Sound("data/sfxs/switch.wav"),
            "attack": pygame.mixer.Sound("data/sfxs/attack.wav"),
            "hit": pygame.mixer.Sound("data/sfxs/hit.wav"),
            "key": pygame.mixer.Sound("data/sfxs/key.wav"),
        }
        self.sfx["jump"].set_volume(0.3)
        self.sfx["shoot"].set_volume(0.5)
        self.sfx["switch"].set_volume(0.3)
        self.sfx["attack"].set_volume(0.5)
        self.sfx["hit"].set_volume(0.4)
        self.sfx["key"].set_volume(0.3)


        self.tilemap = Tilemap(self, tile_size=48)
        try:
            self.tilemap.load("data/map.json")
        except FileNotFoundError:
            pass

    def set_up_game_loop(self):
        enemy_spawners, player_spawner = load()
        self.player = Player(self, [player_spawner[0], player_spawner[1]], (48, 64), 3)
        self.hearts = []
        self.heartless = []
        for i in range(self.player.health):
            self.hearts.append((load_image("ui/heart.png"), (80 + 30 * i, 16)))
        self.horizontal_movement = [False, False]
        self.projectiles = []
        self.explosions = []

        self.yellow_key = False
        self.yellow_door_removed = False
        self.red_key = False
        self.red_door_removed = False

        self.enemies = []
        id = 0
        for spawner in enemy_spawners:
            self.enemies.append(Enemy(id, self, [spawner[0], spawner[1]], (48, 64)))
            id+=1
        self.villagers= []
        self.enemy_total = len(self.enemies)
        self.enemy_counter = 0

    def title_screen(self):
        render_text(self.display, "Connect a Witch!", self.title_font, (255, 255, 255), (self.display.get_width() / 4, self.display.get_height() / 2 - 80))
        render_text(self.display, "Move with arrow keys\nJump with Space\nSwitch magic with D\nShoot with F\nPress Space to play!", self.sub_title_font, (255, 255, 255), (self.display.get_width() / 3, self.display.get_height() / 2 - 25))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.set_up_game_loop()
                    self.on_title_screen = False
                    self.on_game = True

    def game_loop(self):
        def rewards(enemy):
            if enemy.id == 0:
                self.sfx["key"].play()
                self.yellow_key = True
            elif enemy.id == 6:
                self.player.upgrade_life()
            #elif enemy.id == 5:
            #   self.red_key = True

        update_movement = ((self.horizontal_movement[1] - self.horizontal_movement[0]) * 3.5, 0)
        self.player.update(update_movement)
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2.5 - self.scroll[0]) / 15
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 1.9 - self.scroll[1])
        self.scroll = [int(self.scroll[0]), int(self.scroll[1])]

        for villager in self.villagers.copy():
            villager.update()
            villager.render(self.display, self.scroll)

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
                            rewards(enemy)
                            self.enemies.remove(enemy)
                            self.enemy_counter +=1
                            self.villagers.append(Villager(self, enemy.position, (48, 64)))
                    else:
                        enemy.reset()
            projectile.render(self.display, self.scroll)
        
        for enemy in self.enemies.copy():
            enemy.update()
            enemy.render(self.display, self.scroll)
            if enemy.attack_cooldown > 0 and enemy.attack_cooldown < 60:
                if enemy.rect().colliderect(self.player.rect()) and not self.player.invincibility:
                    self.player.hit(1)

        self.display.blit(self.ui["spell/" + self.player.projectile_type], (16, 16))
        self.display.blit(self.ui["staff"], (16, 16))
        for heart in self.hearts:
            self.display.blit(heart[0], heart[1])
        for heart in self.heartless:
            self.display.blit(heart[0], heart[1])
        render_text(self.display, str(self.enemy_counter) + "/" + str(self.enemy_total), self.title_font, (255, 255, 255), (self.display.get_width() - 80, 16))
        if self.yellow_key:
            self.display.blit(self.ui["yellow_key"], (90, 48))
        if self.red_key:
            self.display.blit(self.ui["red_key"], (120, 48))

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
                    self.player.jump()
                if event.key == pygame.K_f:
                    self.player.shoot()
                if event.key == pygame.K_d:
                    if not self.tilemap.check_tile(self.player.position, self.player.size[1]) in {"pink_border", "blue_border"}:
                        self.tilemap.update_magic_tiles()
                        self.player.switch_colors()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.horizontal_movement[0] = False
                if event.key == pygame.K_RIGHT:
                    self.horizontal_movement[1] = False

        if self.enemy_counter == self.enemy_total:
            self.on_game = False
            self.on_victory_screen = True
            
        elif self.player.health == 0:
            self.on_game = False
            self.game_over = True

    def game_over_screen(self):
        render_text(self.display, "Game Over!", self.title_font, (255, 255, 255), (self.display.get_width() / 3, self.display.get_height() / 2 - 50))
        render_text(self.display, "Press Space to go \nback to the title screen!", self.sub_title_font, (255, 255, 255), (self.display.get_width() / 3, self.display.get_height() / 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.on_title_screen = True
                    self.game_over = False

    def victory_screen(self):
        render_text(self.display, "You Saved all the villagers!", self.title_font, (255, 255, 255), (self.display.get_width() / 6, self.display.get_height() / 2 - 50))
        render_text(self.display, "Press Space to go \nback to the title screen!", self.sub_title_font, (255, 255, 255), (self.display.get_width() / 3, self.display.get_height() / 2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.on_title_screen = True
                    self.on_victory_screen = False

    def run(self):
        while True:
            self.display.blit(self.assets["background"], (0, 0))
            if self.on_title_screen:
                self.title_screen()
            elif self.on_game:
                self.game_loop()
            elif self.game_over:
                self.game_over_screen()
            elif self.on_victory_screen:
                self.victory_screen()
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Game().run()