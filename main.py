import pygame
import random
import math

# Initialize pygame
pygame.init()

SCREEN_SIZE = (1000, 1000)

class Object(pygame.sprite.Sprite):

    def __init__(self, position):
        super().__init__()
        self._speed    = [0, 0] # [x, y]
        self._angle    = 0
        self._spin     = 0
        self._position = position

    def update(self):
        self._position[1] += self._speed[1] / interface.fps
        self._position[0] += self._speed[0] / interface.fps

        w, h       = self._image.get_size()
        box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(self._angle) for p in box]
        min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

        # calculate the translation of the pivot 
        pivot        = pygame.math.Vector2(self._size[0] /2 , - self._size[1] /2)
        pivot_rotate = pivot.rotate(self._angle)
        pivot_move   = pivot_rotate - pivot

        # calculate the upper left origin of the rotated image
        origin = (self._position[0] - self._size[0] / 2 + min_box[0] - pivot_move[0], self._position[1] - self._size[1] / 2 - max_box[1] + pivot_move[1])

        self.rotated_image = pygame.transform.rotate(self._image, self._angle)
        interface.screen.blit(self.rotated_image, origin)


class Ship(Object):

    def __init__(self, position):
        super().__init__(position)
        self._image       = pygame.image.load('Images/ship.png')
        self.acceleration = 1
        self._spin        = 4
        self._max_speed   = [10, 10] # [x, y]
        self._size        = self._image.get_size()
    
    def update(self, pressedKeys):
        if pressedKeys[pygame.K_UP]:
            if self._speed[0] <= self._max_speed[0] and self._speed[0] >= -self._max_speed[0]:
                self._speed[0] += self.acceleration * math.cos(math.radians(self._angle)) / interface.fps
            elif self._speed[0] > self._max_speed[0]:
                self._speed[0] = self._max_speed[0] - 0.1
            elif self._speed[0] < -self._max_speed[0]:
                self._speed[0] = -self._max_speed[0] + 0.1

            if self._speed[1] <= self._max_speed[1] and self._speed[1] >= -self._max_speed[1]:
                self._speed[1] -= self.acceleration * math.sin(math.radians(self._angle)) / interface.fps
            elif self._speed[1] > self._max_speed[1]:
                self._speed[1] = self._max_speed[1] - 0.1
            elif self._speed[1] < -self._max_speed[1]:
                self._speed[1] = -self._max_speed[1] + 0.1

        if pressedKeys[pygame.K_LEFT]:
            self._angle += self._spin / interface.fps

        if pressedKeys[pygame.K_RIGHT]:
            self._angle -= self._spin / interface.fps
        
        if pressedKeys[pygame.K_DOWN]:
            self._speed = [0, 0]

        if pressedKeys[pygame.K_SPACE]:
            new_bullet = Bullet(self._position, self._angle)
            interface.bullets.add(new_bullet)
        
        Object.update(self)


class Bullet(Object):

    def __init__(self, position, angle):
        super().__init__(position)
        self._image = pygame.image.load('Images/bullet.png')
        self._angle = angle
        self._spin  = 0
        self._speed = [1, 1]
        self._size  = self._image.get_size()
    
    def update(self):
        Object.update(self)


class UI:
    def __init__(self):
        # Setting up the screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        # Game clock setting
        self.clock = pygame.time.Clock()

        # Group of Ships
        self.ships   = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        # User
        self.user = Ship([100, 100])
        self.ships.add(self.user)
        self.bullets.add()

        # Finalize screen
        pygame.display.set_caption("Shooter")

    def main(self):
        done = False

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            self.fps = 30.0 / self.clock.tick(60)

            # Refresh screen and update sprites
            self.screen.fill((0, 0, 0))
            self.bullets.update()
            self.ships.update(pygame.key.get_pressed())
            pygame.display.update()
            print(self.user._speed , self.user._angle, self.clock.get_fps(), self.bullets.sprites())

        pygame.quit()


if __name__ == "__main__":
    interface = UI()
    interface.main()
