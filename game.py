import pygame

SCREEN_SIZE = (800, 600)

### player ship class.
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Images/ship.png")
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.speed = 5

    def update(self, keys):
        # Using pygame constants
        # Horizontal movement
        if keys[pygame.K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed

        # Vertical movement
        if keys[pygame.K_DOWN] and self.rect.y < 590:
            self.rect.y += self.speed
        if keys[pygame.K_UP] and self.rect.y > 10:
            self.rect.y -= self.speed

        # New position to screen
        interface.screen.blit(self.image, self.rect)

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
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.background = pygame.image.load("Images/background.jpg").convert()

        # Game clock setting
        self.clock = pygame.time.Clock() 

        # TODO Group of Ships 
        self.ships = pygame.sprite.Group()

        # User
        self.user = Ship()
        self.ships.add(self.user)

        # Finalize screen
        pygame.display.set_caption("Shooter")
        pygame.display.update()

    def main(self):        
        done = False

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # Refresh screen and update sprites
            self.screen.blit(self.background, (0, 0))
            self.user.update(pygame.key.get_pressed())
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    interface = UI()
    interface.main()