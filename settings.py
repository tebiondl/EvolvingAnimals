import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Evolving Animals"

# Map settings
MAP_WIDTH = 5120
MAP_HEIGHT = 2880
TILE_SIZE = 64

# Colors
BG_COLOR = (15, 15, 35)  # Map Color
VOID_COLOR = (5, 5, 10)  # Non-playable area color (Darker)
GRID_COLOR = (40, 40, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
CYAN = (50, 255, 255)
MAGENTA = (255, 50, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (165, 42, 42)

# Entity settings
FOOD_SIZE = 10  # Radius or general size
FOOD_COUNT = 100
MONSTER_COUNT = 20

FOOD_ENERGY = {"Apple": 20, "Meat": 50, "Plant": 15, "Berry": 10, "Water": 5}
