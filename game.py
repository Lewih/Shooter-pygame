import pygame
import pygame.sprite
import pygame.time
import pygame.display

SCREEN = pygame.display.set_mode((800, 600))

### player ship class, static acceleration.
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = "Images/ship.png"

    def update(self):
        pass

### bullet class, static speed.
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = "Images/bullet.png"

    def update(self):
        pass

class UI:
    def __init__(self):
        # Initialize pygame 
        pygame.init()

        # Setting up the screen
        self.screen = SCREEN
        self.background = pygame.image.load("Images/background.jpg").convert()
        self.screen.blit(self.background, (0, 0))

        # Game clock setting
        self.clock = pygame.time.Clock() 

        # Finilize screen
        pygame.display.set_caption("Shooter")
        pygame.display.update()

        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            pass

        pygame.quit()


if __name__ == "__main__":
    interface = UI()