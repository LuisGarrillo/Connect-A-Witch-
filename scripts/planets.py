import pygame, random

class Planet:
    def __init__(self, position, image, speed, depth) -> None:
        self.position = position
        self.image = image
        self.speed = speed
        self.depth = depth
    
    def update(self):
        self.position[0] += self.speed

    def render(self, surface):
        render_position = (self.position[0] * self.depth, self.position[1] * self.depth)
        surface.blit(self.image,
                (render_position[0] % (surface.get_width() + self.image.get_width()) - self.image.get_width(),
                render_position[1] % (surface.get_height() + self.image.get_height()) - self.image.get_height())
        )

class Planets:
    def __init__(self, cloud_images, count=10) -> None:
        self.planets = []
        for _ in range(count):
            self.planets.append(
                Planet(
                    [
                        random.random() * 99999,
                        random.random() * 99999
                    ],
                    random.choice(cloud_images),
                    random.random() * 0.05 + 0.03,
                    random.random() * 0.6 + 0.02
                )
            )
    
    def update(self):
        for planet in self.planets:
            planet.update()
    
    def render(self, surface):
        for planet in self.planets:
            planet.render(surface)