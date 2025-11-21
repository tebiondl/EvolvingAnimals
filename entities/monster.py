import pygame
import random
import math
from settings import *

class Monster(pygame.sprite.Sprite):
    def __init__(self, pos, config, groups, food_group, all_sprites):
        super().__init__(groups)
        self.pos = pygame.math.Vector2(pos)
        self.food_group = food_group
        self.all_sprites = all_sprites
        
        # Stats
        self.stats = config['stats']
        self.health = self.stats['health']
        self.speed = self.stats['speed']
        self.armour = self.stats['armour']
        self.size = self.stats['size']
        self.intelligence = self.stats['intelligence']
        
        # Energy (Based on size)
        # Bigger = More Max Energy, but Faster Decay
        self.max_energy = self.size * 4
        self.energy = self.max_energy
        
        # Appearance
        self.shape = config['shape']
        self.color = config['color']
        
        # Movement
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.move_timer = 0
        self.change_dir_interval = random.randint(500, 2000) # ms
        
        # Inventory
        self.inventory = [] # List of food items
        
        # Visual setup
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.render()

    def render(self):
        center = (self.size, self.size)
        if self.shape == 'Square':
            pygame.draw.rect(self.image, self.color, (0, 0, self.size * 2, self.size * 2))
        elif self.shape == 'Triangle':
            points = [(self.size, 0), (self.size * 2, self.size * 2), (0, self.size * 2)]
            pygame.draw.polygon(self.image, self.color, points)
        elif self.shape == 'Circle':
            pygame.draw.circle(self.image, self.color, center, self.size)
        elif self.shape == 'Pentagon':
            self.draw_polygon(5)
        elif self.shape == 'Hexagon':
            self.draw_polygon(6)
        
        # Draw eyes to show direction (simple)
        eye_offset = self.direction * (self.size * 0.5)
        pygame.draw.circle(self.image, WHITE, center + eye_offset, self.size * 0.2)
        pygame.draw.circle(self.image, BLACK, center + eye_offset, self.size * 0.1)

    def draw_polygon(self, sides):
        points = []
        center = (self.size, self.size)
        angle_step = 360 / sides
        for i in range(sides):
            angle = math.radians(i * angle_step - 90)
            x = center[0] + self.size * math.cos(angle)
            y = center[1] + self.size * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(self.image, self.color, points)

    def update(self):
        self.move()
        self.check_food_collision()
        self.rect.center = self.pos
        
        # Energy Decay
        # Bigger monsters decay faster
        decay_rate = self.size * 0.005
        self.energy -= decay_rate
        
        if self.energy <= 0:
            print(f"Monster died of starvation (Shape: {self.shape}, Size: {self.size})")
            self.kill()

        # Randomly drop food
        if self.inventory and random.random() < 0.005: # 0.5% chance per frame to drop
            self.drop_food()

    def move(self):
        current_time = pygame.time.get_ticks()
        
        # Randomly change direction
        if current_time - self.move_timer > self.change_dir_interval:
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
            self.move_timer = current_time
            self.change_dir_interval = random.randint(500, 2000)
            # Re-render to update eyes
            self.image.fill((0,0,0,0))
            self.render()

        # Apply movement
        self.pos += self.direction * self.speed
        
        # Keep in bounds
        if self.pos.x < 0: self.pos.x = 0; self.direction.x *= -1
        if self.pos.x > MAP_WIDTH: self.pos.x = MAP_WIDTH; self.direction.x *= -1
        if self.pos.y < 0: self.pos.y = 0; self.direction.y *= -1
        if self.pos.y > MAP_HEIGHT: self.pos.y = MAP_HEIGHT; self.direction.y *= -1

    def drop_food(self):
        if not self.inventory:
            return
        
        # Remove from inventory
        food_type = self.inventory.pop(0).food_type # Get type of dropped food
        print(f"Monster dropped {food_type}")
        
        # Create new food entity at current position
        from entities.food import Food
        
        # Offset slightly so it doesn't immediately collide and get picked up again
        drop_pos = self.pos + pygame.math.Vector2(random.randint(-40, 40), random.randint(-40, 40))
        
        # Spawn food
        Food(drop_pos, food_type, [self.all_sprites, self.food_group])

    def check_food_collision(self):
        # Check for collisions with food
        collided_food = pygame.sprite.spritecollide(self, self.food_group, False)
        for food in collided_food:
            self.decide_on_food(food)

    def decide_on_food(self, food):
        # Decision logic based on Intelligence
        roll = random.randint(0, 100)
        
        if roll < 40: # 40% chance to eat
            self.eat(food)
        elif roll < 40 + self.intelligence: # Chance to pickup increases with intelligence
            self.pickup(food)
        else:
            pass # Ignore

    def eat(self, food):
        # "Eat" the food (remove it)
        print(f"Monster ate {food.food_type}")
        food.kill()
        # Increase Energy
        self.energy = min(self.energy + 30, self.max_energy)

    def pickup(self, food):
        if food not in self.inventory:
            print(f"Monster picked up {food.food_type}")
            self.inventory.append(food)
            food.kill() # Remove from world, but keep in inventory object if needed

    def draw_ui(self, surface, rect, zoom):
        # Draw Health Bar
        # Scale bar dimensions
        bar_width = self.size * 2 * zoom
        bar_height = 5 * zoom
        x = rect.left
        y = rect.top - 10 * zoom
        
        # Background
        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))
        # Health
        health_pct = self.health / self.stats['health']
        pygame.draw.rect(surface, RED, (x, y, bar_width * health_pct, bar_height))
        
        # Energy Bar
        y += bar_height + 2 * zoom
        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))
        energy_pct = max(0, self.energy / self.max_energy)
        pygame.draw.rect(surface, YELLOW, (x, y, bar_width * energy_pct, bar_height))
        
        # Draw Inventory Count
        if self.inventory:
            font_size = int(20 * zoom)
            if font_size > 5:
                font = pygame.font.SysFont(None, font_size)
                text = font.render(f"Inv: {len(self.inventory)}", True, WHITE)
                surface.blit(text, (x, y - 25 * zoom)) # Adjusted Y for energy bar
