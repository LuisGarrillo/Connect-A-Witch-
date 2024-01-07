import pygame

class Projectile:
    def __init__(self, game, position, size) -> None:
        self.game = game
        self.position = list(position)
        self.size = size
        self.velocity = [0, 0]
        self.animation = self.game.assets["projectile"]

    def rect(self):
        return pygame.Rect(self.position[0], self.position[1], self.size[0], self.size[1])
    
    def update(self, movement=0):
        frame_movement = movement + self.velocity[0]
        self.position[0] += frame_movement
        self.animation.update()
        return self.position[0] > self.game.display.get_width() + 100
    
    def render(self, surface):
        surface.blit(self.game.assets["projectile"].img(), self.position)
