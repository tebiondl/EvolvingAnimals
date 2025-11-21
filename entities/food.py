import pygame
from settings import *

class Food(pygame.sprite.Sprite):
    def __init__(self, pos, food_type, groups):
        super().__init__(groups)
        self.food_type = food_type
        self.pos = pygame.math.Vector2(pos)
        
        # Visual setup
        self.radius = FOOD_SIZE
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        
        self.render()

    def render(self):
        if self.food_type == 'Apple':
            pygame.draw.circle(self.image, RED, (self.radius, self.radius), self.radius)
            # Add a stem
            pygame.draw.line(self.image, BROWN, (self.radius, self.radius - 5), (self.radius, 0), 2)
        elif self.food_type == 'Meat':
            pygame.draw.rect(self.image, BROWN, (0, 0, self.radius * 2, self.radius * 1.5))
            pygame.draw.line(self.image, RED, (2, 2), (self.radius * 2 - 2, self.radius * 1.5 - 2), 2)
        elif self.food_type == 'Plant':
            points = [(self.radius, 0), (self.radius * 2, self.radius * 2), (0, self.radius * 2)]
            pygame.draw.polygon(self.image, GREEN, points)
        elif self.food_type == 'Berry':
            pygame.draw.circle(self.image, PURPLE, (self.radius, self.radius), self.radius * 0.6)
            pygame.draw.circle(self.image, PURPLE, (self.radius + 4, self.radius + 4), self.radius * 0.4)
        elif self.food_type == 'Water':
            pygame.draw.ellipse(self.image, BLUE, (0, self.radius // 2, self.radius * 2, self.radius))
        else:
            pygame.draw.circle(self.image, WHITE, (self.radius, self.radius), self.radius)
