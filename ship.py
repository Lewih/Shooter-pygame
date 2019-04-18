import pygame
from bullet import Bullet

class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('Images/ship.png')
        self.rect = self.image.get_rect(topleft = (375, 540))
        self.speed = 5

    def update(self, pressedKeys, interface):
        " Vertical movement"
        if pressedKeys[pygame.K_UP] and self.rect.y > 10:
            self.rect.y -= self.speed * interface.dt
        elif pressedKeys[pygame.K_DOWN] and self.rect.y < 590:
            self.rect.y += self.speed * interface.dt

        """Horizontal movement"""
        if pressedKeys[pygame.K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed * interface.dt
        elif pressedKeys[pygame.K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed * interface.dt

        """ Shot movement"""
        if pressedKeys[pygame.K_SPACE]:
            new_bullet = Bullet(interface.user.rect.x, interface.user.rect.y)
            interface.all_sprites.add(new_bullet)
            fps = interface.clock.get_fps()
            print(fps)
        
        # New position to screen
        interface.screen.blit(self.image, self.rect)