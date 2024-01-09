import pygame, random
from scripts.projectile import Projectile
from scripts.utils import load_image
COLORS = ("blue", "pink")
class PhysicsEntity:
    def __init__(self, game, entity_type, position, size, health) -> None:
        self.game = game
        self.type = entity_type
        self.position = list(position)
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.size = size
        self.velocity = [0, 0]
        self.flip = False
        self.health = health
        self.wait = False
        self.action = ""

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + "/" + self.action].copy()

    def update(self, movement=(0,0)) -> None:
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        if not self.wait:
            self.position[0] += frame_movement[0]
            entity_rect = self.rect()
            for rect in self.game.tilemap.rects_around(self.position, self.size[1]):
                if entity_rect.colliderect(rect):
                    if frame_movement[0] > 0:
                        entity_rect.right = rect.left
                        self.collisions['right'] = True
                    if frame_movement[0] < 0:
                        entity_rect.left = rect.right
                        self.collisions['left'] = False
                    self.position[0] = entity_rect.x

            self.position[1] += frame_movement[1]
            entity_rect = self.rect()
            for rect in self.game.tilemap.rects_around(self.position, self.size[1]):
                if entity_rect.colliderect(rect):
                    if frame_movement[1] > 0:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True
                    if frame_movement[1] < 0:
                        entity_rect.top = rect.bottom
                        self.collisions['up'] = True
                    self.position[1] = entity_rect.y
            
            if frame_movement[0] > 0:
                self.flip = False
            elif frame_movement[0] < 0:
                self.flip = True 

        self.velocity[1] = min(5, self.velocity[1] + 0.3)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        if self.collisions["right"] or self.collisions["left"]:
            self.velocity[0] = 0

        self.animation.update()

    def render(self, surface, offset) -> None:
        surface.blit(self.animation.img(), (self.position[0] - offset[0], self.position[1] - offset[1]))
class Player(PhysicsEntity):
    def __init__(self, game, position, size, health) -> None:
        super().__init__(game, "player", position, size, health)
        self.health = 3
        self.projectile_type = "pink"
        self.invincibility = 0
        self.shoot_cooldown = 0
        self.air_time = 0
        self.jump_cap = 1
        self.jumps = self.jump_cap

        self.set_action("idle")

    def update(self, movement=[0, 0]) -> None:
        super().update(movement)
        if self.position[0] < 0 :
            self.position[0] = 0
            
        if self.invincibility:
            self.invincibility -= 1

        self.air_time += 1
        if self.collisions["down"]:
            self.jumps = self.jump_cap
            self.air_time = 0  

        if self.shoot_cooldown:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown == 10:
                self.wait = False

        if self.game.yellow_key and self.position[0] > 2550:
            self.game.tilemap.remove_yellow_door()

        if not self.wait:
            self.set_action("idle")

    def jump(self) -> None:
        if self.jumps:
            self.velocity[1] = -7
            self.jumps = max(0, self.jumps - 1)
    
    def shoot(self) -> None:
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            self.game.projectiles.append(Projectile(self.game, (self.position[0], self.position[1] + self.size[1]/2), (48, 16), self.projectile_type, flip=self.flip))
            self.wait = True
            self.set_action("shooting")

    def hit(self, damage) -> None:
        self.health -= damage
        self.invincibility = 60
        for _ in range(damage):
            self.game.hearts.pop()
            if len(self.game.hearts) <= 0:
                break
            self.game.heartless.append((load_image("ui/heartless.png"), (self.game.hearts[len(self.game.hearts) - 1][1][0] + 30, 16)))
                
    
    def switch_colors(self) -> None:
        if self.projectile_type == "pink":
            self.projectile_type = "blue"
        else:
            self.projectile_type = "pink"

class Weakness:
    def __init__(self, game, position, size, count) -> None:
        self.game = game
        if count == 0:
            self.position = [position[0] - 16, position[1] - 30]
        else:
            self.position = [position[0] - 16 + (size[0] + 10) * count, position[1] - 30]
        self.count = count
        self.size = size
        self.type = random.choice(COLORS)
        self.animation = self.game.assets["weakness/" + self.type]

    def update(self, enemy_position) -> None:
        if self.count == 0:
            self.position[0] = enemy_position[0] - 16
        else:
            self.position[0] = enemy_position[0] - 16 + (self.size[0] + 10) * self.count

        self.position[1] = enemy_position[1] - 30
            
    def render(self, surface, offset) -> None:
        surface.blit(self.animation.img(), (self.position[0] - offset[0], self.position[1] - offset[1]))
class Enemy(PhysicsEntity):
    def __init__(self, id, game, position, size, health=3) -> None:
        super().__init__(game, "enemy", position, size, health)
        self.id = id
        self.health = health
        self.weaknesses = []
        self.auxiliar_weaknesses = []
        for i in range(self.health):
            weakness = Weakness(self.game, (self.position[0], self.position[1]), (20, 20), i)
            self.weaknesses.append(weakness)
            self.auxiliar_weaknesses.append(weakness)
        self.boundaries = (-100, 100)
        self.stunned = False
        self.attack_cooldown = 0

        self.set_action("idle")

    def update(self, movement=[0, 0]) -> None:
        if not self.attack_cooldown:
            if self.position[0] > self.game.player.position[0] and self.position[0] - self.game.player.position[0] - self.game.player.size[0] < 260:
                movement[0] = -1
                if self.position[0] - self.game.player.position[0] - self.game.player.size[0] < 20:
                    self.attack()
            elif self.position[0] < self.game.player.position[0] and self.game.player.position[0] - self.position[0] - self.size[0]  < 260:
                movement[0] = 1
                if self.game.player.position[0] - self.position[0] - self.size[0] < 20:
                    self.attack()
            else:
                movement[0] = 0
                self.set_action("idle")
        else:
            movement[0] = 0
            

        super().update(movement)

        if self.attack_cooldown:
            self.attack_cooldown -= 1
            if self.attack_cooldown == 60:
                if self.flip:
                    self.velocity[0] = -5
                else:
                    self.velocity[0] = 5
            elif self.attack_cooldown < 60:
                if self.flip:
                    self.velocity[0] = min(0, self.velocity[0] + 0.3)
                else:
                    self.velocity[0] = max(0, self.velocity[0] - 0.3)

        if self.position[0] < 0:
            self.position[0] = 0

        for weakness in self.weaknesses:
            weakness.update(self.position)
    
    def render(self, surface, offset) -> None:
        super().render(surface, offset)
        for weakness in self.weaknesses:
            weakness.render(surface, offset)

    def hit(self):
        self.weaknesses.remove(self.weaknesses[0])
        return len(self.weaknesses) == 0
    
    def attack(self):
        self.attack_cooldown = 120
        self.set_action("attack")
        
    def reset(self):
        self.weaknesses.clear()
        for weakness in self.auxiliar_weaknesses:
            self.weaknesses.append(weakness)
        self.health = len(self.weaknesses)
        

        


    