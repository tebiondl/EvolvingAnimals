from settings import *

# Ranges for random generation
STAT_RANGES = {
    "health": (50, 200),
    "speed": (1.0, 8.0),
    "armour": (0, 15),
    "size": (20, 60),
    "intelligence": (0, 50),
    "regen_threshold": (
        0.2,
        0.2,
    ),  # Fixed at 20% for now as per request "more than 20%"
    "regen_rate": (0.01, 0.1),  # Random regeneration rate
    "energy_decay_rate": (0.0015, 0.0005),  # Random energy decay rate
    "max_energy": (3, 5),  # Random max energy
}

SHAPES = ["Square", "Triangle", "Circle", "Pentagon", "Hexagon"]
DIETS = ["Herbivore", "Carnivore", "Omnivore"]
