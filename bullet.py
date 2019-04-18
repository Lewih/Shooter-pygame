import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load("Images/bullet.png")
        self.rect = self.image.get_rect(topleft=(x_pos + 23, y_pos + 5))
        self.speed = 5

    def update(self, keys, interface):
        self.rect.y -= self.speed * interface.dt

        if self.rect.y < 1:
            self.kill()
        if self.rect.y > 600:
            self.kill()
        if self.rect.x < 1:
            self.kill()
        if self.rect.x > 799:
            self.kill()

        interface.screen.blit(self.image, self.rect)

