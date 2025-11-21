import pygame
import random
from settings import *
from entities.food import Food
from entities.monster import Monster

from monster_config import MONSTER_CONFIGS


class World:
    def __init__(self, screen):
        self.screen = screen
        self.display_surface = pygame.display.get_surface()

        # Camera
        self.camera_pos = pygame.math.Vector2(
            MAP_WIDTH // 2 - SCREEN_WIDTH // 2, MAP_HEIGHT // 2 - SCREEN_HEIGHT // 2
        )
        self.zoom = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 2.0
        self.camera_speed = 10

        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()
        self.monster_group = pygame.sprite.Group()

        self.setup_world()

    def setup_world(self):
        # Spawn Food
        for _ in range(FOOD_COUNT):
            x = random.randint(0, MAP_WIDTH)
            y = random.randint(0, MAP_HEIGHT)
            food_type = random.choice(
                ["Apple", "Plant", "Berry", "Water"]
            )  # No Meat naturally
            Food((x, y), food_type, [self.all_sprites, self.food_group])

        # Spawn Monsters
        for _ in range(MONSTER_COUNT):
            config = random.choice(MONSTER_CONFIGS)
            x = random.randint(0, MAP_WIDTH)
            y = random.randint(0, MAP_HEIGHT)
            Monster(
                (x, y),
                config,
                [self.all_sprites, self.monster_group],
                self.food_group,
                self.monster_group,
                self.all_sprites,
            )

    def handle_input(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.zoom = min(self.max_zoom, self.zoom + 0.1)
            elif event.y < 0:
                self.zoom = max(self.min_zoom, self.zoom - 0.1)

    def update(self):
        # Camera Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera_pos.y -= self.camera_speed / self.zoom
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera_pos.y += self.camera_speed / self.zoom
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera_pos.x -= self.camera_speed / self.zoom
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera_pos.x += self.camera_speed / self.zoom

        # Clamp camera
        # Visible width/height in world coordinates
        visible_w = SCREEN_WIDTH / self.zoom
        visible_h = SCREEN_HEIGHT / self.zoom

        self.camera_pos.x = max(0, min(self.camera_pos.x, MAP_WIDTH - visible_w))
        self.camera_pos.y = max(0, min(self.camera_pos.y, MAP_HEIGHT - visible_h))

        self.all_sprites.update()

    def draw(self):
        # Draw Map Background
        # Calculate screen position of map (0,0)
        map_x = -self.camera_pos.x * self.zoom
        map_y = -self.camera_pos.y * self.zoom
        map_w = MAP_WIDTH * self.zoom
        map_h = MAP_HEIGHT * self.zoom

        map_rect = pygame.Rect(map_x, map_y, map_w, map_h)
        pygame.draw.rect(self.display_surface, BG_COLOR, map_rect)

        # Draw grid for reference
        self.draw_grid()

        # Draw sprites with camera offset and zoom
        for sprite in self.all_sprites:
            # Calculate screen position
            # sprite.pos is center or topleft? In Monster/Food it seems to be center or used as such.
            # Monster: self.rect.center = self.pos
            # Food: self.rect = self.image.get_rect(center=pos)
            # So sprite.pos is the center in world coordinates.

            # We need top-left for blit, but let's calculate center then offset
            screen_center_x = (sprite.pos.x - self.camera_pos.x) * self.zoom
            screen_center_y = (sprite.pos.y - self.camera_pos.y) * self.zoom

            # Scale image
            # Note: Scaling every frame is expensive. For optimization, could cache or only scale if zoom changes.
            # But for < 200 sprites it might be okay.
            original_w = sprite.rect.width
            original_h = sprite.rect.height
            new_w = int(original_w * self.zoom)
            new_h = int(original_h * self.zoom)

            if new_w > 0 and new_h > 0:
                scaled_image = pygame.transform.scale(sprite.image, (new_w, new_h))
                scaled_rect = scaled_image.get_rect(
                    center=(screen_center_x, screen_center_y)
                )

                # Only draw if on screen
                if scaled_rect.colliderect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT):
                    self.display_surface.blit(scaled_image, scaled_rect)

                    # Debug/Info drawing (optional, e.g. health bars)
                    if isinstance(sprite, Monster):
                        # Pass scaled rect and zoom to draw_ui
                        sprite.draw_ui(self.display_surface, scaled_rect, self.zoom)

    def draw_grid(self):
        # Grid needs to be scaled too
        scaled_tile_size = int(TILE_SIZE * self.zoom)
        if scaled_tile_size <= 0:
            return

        # Calculate start offset
        start_x = int((self.camera_pos.x % TILE_SIZE) * self.zoom)
        start_y = int((self.camera_pos.y % TILE_SIZE) * self.zoom)

        # Draw vertical lines
        for x in range(-start_x, SCREEN_WIDTH, scaled_tile_size):
            pygame.draw.line(
                self.display_surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT)
            )

        # Draw horizontal lines
        for y in range(-start_y, SCREEN_HEIGHT, scaled_tile_size):
            pygame.draw.line(
                self.display_surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y)
            )
