import pygame
from scripts.projectile import Projectile

class PhysicsEntity:
    def __init__(self, game, entity_type, position, size, health) -> None:
        self.game = game
        self.type = entity_type
        self.position = list(position)
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.size = size
        self.velocity = [0, 0]
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

        self.invincibility = 0
        self.shoot_cooldown = 0

        self.set_action("idle")

    def update(self, movement=[0, 0]) -> None:
        super().update(movement)
        if self.position[0] < 0 :
            self.position[0] = 0
            
        if self.invincibility:
            self.invincibility -= 1

        if self.shoot_cooldown:
            self.shoot_cooldown -= 1
            if self.shoot_cooldown == 10:
                self.wait = False

        if not self.wait:
            self.set_action("idle")

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 25
            self.game.projectiles.append(Projectile(self.game, (self.position[0] + self.size[0], self.position[1] + self.size[1]/2), (32, 32)))
            self.wait = True
            self.set_action("shooting")

    def hit(self):
        self.health -= 1
        self.invincibility = 60
    
    def sword(self):
        if self.sword_cooldown == 0 and not self.sword_active:
            self.sword_cooldown = 30
            self.sword_active = True
            self.wait = True
            self.set_action("sword")
        


    