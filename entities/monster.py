import pygame
import random
import math
from settings import *


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos, config, groups, food_group, monster_group, all_sprites):
        super().__init__(groups)
        self.pos = pygame.math.Vector2(pos)
        self.food_group = food_group
        self.monster_group = monster_group
        self.all_sprites = all_sprites

        # Battle State
        self.state = "IDLE"  # IDLE, BATTLING, STAGGERED
        self.opponent = None
        self.battle_timer = 0
        self.stagger_timer = 0

        # Stats
        self.stats = config["stats"]
        self.health = self.stats["health"]
        self.speed = self.stats["speed"]
        self.armour = self.stats["armour"]
        self.size = self.stats["size"]
        self.intelligence = self.stats["intelligence"]

        # Energy (Based on size)
        # Bigger = More Max Energy, but Faster Decay
        self.max_energy = self.size * 4
        self.energy = self.max_energy
        # Bigger monsters decay faster
        self.energy_decay_rate = self.size * 0.001

        # Diet
        self.diet = config.get("diet", "Omnivore")

        # Appearance
        self.shape = config["shape"]
        self.color = config["color"]

        # Movement
        self.direction = pygame.math.Vector2(
            random.uniform(-1, 1), random.uniform(-1, 1)
        ).normalize()
        self.move_timer = 0
        self.change_dir_interval = random.randint(500, 2000)  # ms

        # Inventory
        self.inventory = []  # List of food items

        # Visual setup
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.render()

    def render(self):
        center = (self.size, self.size)
        if self.shape == "Square":
            pygame.draw.rect(
                self.image, self.color, (0, 0, self.size * 2, self.size * 2)
            )
        elif self.shape == "Triangle":
            points = [
                (self.size, 0),
                (self.size * 2, self.size * 2),
                (0, self.size * 2),
            ]
            pygame.draw.polygon(self.image, self.color, points)
        elif self.shape == "Circle":
            pygame.draw.circle(self.image, self.color, center, self.size)
        elif self.shape == "Pentagon":
            self.draw_polygon(5)
        elif self.shape == "Hexagon":
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
        current_time = pygame.time.get_ticks()

        # Handle States
        if self.state == "STAGGERED":
            if current_time - self.stagger_timer > 1000:  # 1 second stagger
                self.state = "IDLE"
            return  # Don't do anything else while staggered

        if self.state == "BATTLING":
            self.battle_logic(current_time)
            return

        # IDLE Behavior
        self.move()
        self.check_food_collision()
        self.check_monster_collision()
        self.rect.center = self.pos

        # Energy Decay
        self.energy -= self.energy_decay_rate

        if self.energy <= 0:
            print(
                f"Monster died of starvation (Shape: {self.shape}, Size: {self.size})"
            )
            self.kill_monster()

        # Randomly drop food
        if self.inventory and random.random() < 0.005:  # 0.5% chance per frame to drop
            self.drop_food()

    def check_monster_collision(self):
        # Check for collisions with other monsters
        collided_monsters = pygame.sprite.spritecollide(self, self.monster_group, False)
        for other in collided_monsters:
            if other != self and other.shape != self.shape:  # Different species
                if self.state == "IDLE" and other.state == "IDLE":
                    self.start_battle(other)

    def start_battle(self, other):
        print(f"Battle Started: {self.shape} vs {other.shape}")
        self.state = "BATTLING"
        other.state = "BATTLING"
        self.opponent = other
        other.opponent = self

        current_time = pygame.time.get_ticks()
        self.battle_timer = current_time
        other.battle_timer = current_time

    def battle_logic(self, current_time):
        if not self.opponent or not self.opponent.alive():
            self.end_battle()
            return

        # Turn Logic (1 second per turn)
        if current_time - self.battle_timer > 1000:
            # Reset timer for both (to keep sync)
            self.battle_timer = current_time
            self.opponent.battle_timer = current_time

            # Decide whose turn it is
            # Weighted random based on speed * energy
            my_score = self.speed * self.energy
            opp_score = self.opponent.speed * self.opponent.energy
            total_score = my_score + opp_score

            if total_score == 0:
                return

            roll = random.uniform(0, total_score)
            if roll < my_score:
                self.execute_turn_action()
            else:
                # Opponent's turn logic handled in their update
                pass

    def execute_turn_action(self):
        # Decide Action: Attack or Run
        action = random.choice(["ATTACK", "RUN"])

        if action == "ATTACK":
            self.attack_opponent()
        else:
            self.try_run()

    def attack_opponent(self):
        # Chance to hit: Opponent Speed and Size
        hit_chance = 0.8 - (self.opponent.speed * 0.05) + (self.opponent.size * 0.005)
        hit_chance = max(0.1, min(0.95, hit_chance))

        if random.random() < hit_chance:
            # Hit!
            damage = self.size * 0.5
            print(f"{self.shape} hits {self.opponent.shape} for {damage:.1f} dmg!")
            self.opponent.take_damage(damage)
        else:
            print(f"{self.shape} missed attack on {self.opponent.shape}!")

    def try_run(self):
        # Run chance: My Speed and Size
        run_chance = 0.5 + (self.speed * 0.05) - (self.size * 0.005)
        run_chance = max(0.1, min(0.9, run_chance))

        if random.random() < run_chance:
            print(f"{self.shape} ran away successfully!")
            self.opponent.stagger()
            self.end_battle()
        else:
            print(f"{self.shape} failed to run away!")

    def take_damage(self, amount):
        reduced_damage = max(1, amount - (self.armour * 0.5))
        self.health -= reduced_damage
        if self.health <= 0:
            print(f"{self.shape} died in battle!")
            self.kill_monster()

    def kill_monster(self):
        # Drop Meat
        from entities.food import Food

        Food(self.pos, "Meat", [self.all_sprites, self.food_group])
        print(f"{self.shape} dropped Meat on death.")

        # Handle death (drop inventory?)
        if self.inventory:
            for _ in range(len(self.inventory)):
                self.drop_food()
        self.kill()
        if self.opponent:
            self.opponent.end_battle()

    def stagger(self):
        self.state = "STAGGERED"
        self.stagger_timer = pygame.time.get_ticks()
        self.opponent = None  # Battle ended for me

    def end_battle(self):
        self.state = "IDLE"
        self.opponent = None

    def move(self):
        current_time = pygame.time.get_ticks()

        # Change direction randomly
        if current_time - self.move_timer > self.change_dir_interval:
            self.direction = pygame.math.Vector2(
                random.uniform(-1, 1), random.uniform(-1, 1)
            ).normalize()
            self.move_timer = current_time
            self.change_dir_interval = random.randint(500, 2000)

        # Move
        self.pos += self.direction * self.speed

        # Constrain to map
        self.pos.x = max(self.size, min(self.pos.x, MAP_WIDTH - self.size))
        self.pos.y = max(self.size, min(self.pos.y, MAP_HEIGHT - self.size))

    def check_food_collision(self):
        collided_food = pygame.sprite.spritecollide(self, self.food_group, False)
        for food in collided_food:
            self.decide_on_food(food)

    def decide_on_food(self, food):
        # Decision logic based on Intelligence
        roll = random.randint(0, 100)
        pickup_chance = self.intelligence

        if roll < pickup_chance:
            self.pickup(food)
        elif roll < 80:  # High chance to eat
            self.eat(food)
        # else ignore

    def eat(self, food):
        # Check Diet
        can_eat = False
        if self.diet == "Omnivore":
            can_eat = True
        elif self.diet == "Carnivore":
            if food.food_type in ["Meat", "Water"]:
                can_eat = True
        elif self.diet == "Herbivore":
            if food.food_type in ["Plant", "Apple", "Berry", "Water"]:
                can_eat = True

        if can_eat:
            print(f"Monster ({self.diet}) ate {food.food_type} (+{food.energy} Energy)")
            self.energy = min(self.max_energy, self.energy + food.energy)
            food.kill()
        else:
            # Ignore or maybe pickup?
            pass

    def pickup(self, food):
        print(f"Monster picked up {food.food_type}")
        self.inventory.append(food.food_type)
        food.kill()

    def drop_food(self):
        if not self.inventory:
            return

        food_type = self.inventory.pop(0)
        # Spawn new food entity
        from entities.food import Food

        offset = pygame.math.Vector2(random.uniform(-20, 20), random.uniform(-20, 20))
        Food(self.pos + offset, food_type, [self.all_sprites, self.food_group])
        print(f"Monster dropped {food_type}")

    def draw_ui(self, surface, rect, zoom):
        # Draw Health Bar
        bar_width = self.size * 2 * zoom
        bar_height = 5 * zoom
        x = rect.left
        y = rect.top - 10 * zoom

        # Background
        pygame.draw.rect(surface, BLACK, (x, y, bar_width, bar_height))
        # Health
        health_pct = self.health / self.stats["health"]
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
                surface.blit(text, (x, y - 25 * zoom))

        # Draw State (Battle/Stagger)
        if self.state != "IDLE":
            font_size = int(20 * zoom)
            if font_size > 5:
                font = pygame.font.SysFont(None, font_size)
                state_text = "VS" if self.state == "BATTLING" else "STUN"
                color = RED if self.state == "BATTLING" else YELLOW
                text = font.render(state_text, True, color)
                surface.blit(text, (x, y - 45 * zoom))
