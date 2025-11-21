import pygame
import sys
from settings import *
from world import World

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.world = World(self.screen)

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            self.world.handle_input(event)

    def update(self):
        self.world.update()

    def draw(self):
        self.screen.fill(VOID_COLOR)
        self.world.draw()
        pygame.display.flip()

    def close(self):
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        game.close()
