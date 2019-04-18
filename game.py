import pygame
from bullet import Bullet
from ship import Ship
# Initialize pygame
pygame.init()

SCREEN_SIZE = (800, 600)


class UI:
    def __init__(self):
        # Setting up the screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.background = pygame.image.load("Images/background.jpg").convert()

        # Game clock setting
        self.clock = pygame.time.Clock()

        # TODO Group of Ships
        self.ships = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # User
        self.user = Ship()
        self.ships.add(self.user)
        self.all_sprites.add(self.user)

        # Finalize screen
        pygame.display.set_caption("Shooter")

    def main(self):
        done = False

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            
            self.dt = 30.0 / self.clock.tick(100)

            # Refresh screen and update sprites
            self.screen.blit(self.background, (0, 0))
            self.all_sprites.update(pygame.key.get_pressed(), interface)
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    interface = UI()
    interface.main()
