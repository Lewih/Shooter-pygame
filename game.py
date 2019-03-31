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

        # Shoot
        if keys[pygame.K_SPACE]:
            new_bullet = Bullet(interface.user.rect.x, interface.user.rect.y)
            interface.all_sprites.add(new_bullet)
        # New position to screen
        interface.screen.blit(self.image, self.rect)

### bullet class, static speed.
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load("Images/bullet.png")
        self.rect = self.image.get_rect(topleft=(x_pos+23, y_pos+5))
        self.speed = 5
        
    def update(self, keys):
        self.rect.y -= self.speed
        
        if(self.rect.y < 1):
            self.kill()
        if(self.rect.y > 600):
            self.kill()
        if(self.rect.x < 1):
            self.kill()
        if(self.rect.x > 799):
            self.kill()

        interface.screen.blit(self.image, self.rect)

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
        self.all_sprites = pygame.sprite.Group()

        # User
        self.user = Ship()
        self.ships.add(self.user)
        self.all_sprites.add(self.user)

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
            self.all_sprites.update(pygame.key.get_pressed())
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    interface = UI()
    interface.main()