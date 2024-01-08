import pygame

class Projectile:
    def __init__(self, game, position, size, type, flip=False) -> None:
        self.game = game
        self.position = list(position)
        if not flip:
            self.position[0] += game.player.size[0]
        else:
            self.position[0] -= size[0]
        self.type = type
        self.size = size
        self.velocity = [0, 0]
        self.flip = flip
        self.movement_counter = 0
        self.animation = self.game.assets["projectile/pink"]

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def update(self, movement=5):
        if self.flip:
            frame_movement = movement 
            self.position[0] -= frame_movement
            self.movement_counter -= frame_movement
            self.animation.update()
            return self.movement_counter < -150
        else:
            frame_movement = movement
            self.position[0] += frame_movement
            self.movement_counter += frame_movement
            self.animation.update()
            return self.movement_counter > 150
    
    def render(self, surface, offset=(0,0)):
        surface.blit(self.game.assets["projectile/" + self.type].img(), (self.position[0] - offset[0], self.position[1] - offset[1]))
