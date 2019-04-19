import pygame
import random
import math

# Initialize pygame
pygame.init()

SCREEN_SIZE = (1300, 800)

class Game_Object(pygame.sprite.Sprite):

    def __init__(self, position):
        super().__init__()
        self._speed    = [0, 0] # [x, y]
        self._angle    = 0
        self._spin     = 0
        self.rect      = self._image.get_rect()
        self.rect.x    = position[0]
        self.rect.y    = position[1]

    def update(self):
        self.rect.x += self._speed[0] / interface.fps
        self.rect.y += self._speed[1] / interface.fps

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
        origin = (self.rect.x - self._size[0] / 2 + min_box[0] - pivot_move[0], self.rect.y - self._size[1] / 2 - max_box[1] + pivot_move[1])

        self.rotated_image = pygame.transform.rotate(self._image, self._angle)
        interface.screen.blit(self.rotated_image, origin)


class Ship(Game_Object):

    def __init__(self, position, image, bullet_speed):
        self._image       = pygame.image.load(image).convert_alpha()
        super().__init__(position)
        self.acceleration = 0.7
        self._spin        = 4
        self._max_speed   = [10, 10] # [x, y]
        self._speed_limit = self._max_speed
        self._size        = self._image.get_size()
        self._stabilizer = 0.2
        self._bullet_speed = bullet_speed
    
    def update(self, pressedKeys):
        self._speed_limit = [abs(self._max_speed[0] * math.cos(math.radians(self._angle))), 
                             abs(self._max_speed[1] * math.sin(math.radians(self._angle)))]
        
        if pressedKeys[pygame.K_UP]:
            if self._speed[0] <= self._speed_limit[0] and self._speed[0] >= -self._speed_limit[0]:
                self._speed[0] += self.acceleration * math.cos(math.radians(self._angle)) / interface.fps
            elif self._speed[0] > self._speed_limit[0]:
                self._speed[0] = self._speed[0] - self._stabilizer / interface.fps
            elif self._speed[0] < -self._speed_limit[0]:
                self._speed[0] = self._speed[0] + self._stabilizer / interface.fps

            if self._speed[1] <= self._speed_limit[1] and self._speed[1] >= -self._speed_limit[1]:
                self._speed[1] -= self.acceleration * math.sin(math.radians(self._angle)) / interface.fps
            elif self._speed[1] > self._speed_limit[1]:
                self._speed[1] = self._speed[1] - self._stabilizer / interface.fps
            elif self._speed[1] < -self._speed_limit[1]:
                self._speed[1] = self._speed[1] + self._stabilizer / interface.fps
        
        elif pressedKeys[pygame.K_DOWN]:
            if self._speed[0] <= self._speed_limit[0] and self._speed[0] >= -self._speed_limit[0]:
                self._speed[0] -= self.acceleration / 2 * math.cos(math.radians(self._angle)) / interface.fps
            elif self._speed[0] > self._speed_limit[0]:
                self._speed[0] = self._speed[0] - self._stabilizer / interface.fps
            elif self._speed[0] < -self._speed_limit[0]:
                self._speed[0] = self._speed[0] + self._stabilizer / interface.fps

            if self._speed[1] <= self._speed_limit[1] and self._speed[1] >= -self._speed_limit[1]:
                self._speed[1] += self.acceleration / 2 * math.sin(math.radians(self._angle)) / interface.fps
            elif self._speed[1] > self._speed_limit[1]:
                self._speed[1] = self._speed[1] - self._stabilizer / interface.fps
            elif self._speed[1] < -self._speed_limit[1]:
                self._speed[1] = self._speed[1] + self._stabilizer / interface.fps

        if pressedKeys[pygame.K_LEFT]:
            self._angle += self._spin / interface.fps

        if pressedKeys[pygame.K_RIGHT]:
            self._angle -= self._spin / interface.fps

        if pressedKeys[pygame.K_SPACE]:
            new_bullet = Bullet([self.rect.x, self.rect.y], self._angle, self._bullet_speed)
            interface.bullets.add(new_bullet)
            interface.all.add(new_bullet)

        Game_Object.update(self)


class Bullet(Game_Object):

    def __init__(self, position, angle, bullet_speed):
        self._image = pygame.image.load('Images/bullet.png').convert_alpha()
        super().__init__(position)
        self._angle = angle
        self._spin  = 0
        self._bullet_speed = bullet_speed
        self._size  = self._image.get_size( )

    def update(self):
        self._speed = [self._bullet_speed * math.cos(math.radians(self._angle)) / interface.fps, 
                       self._bullet_speed * - math.sin(math.radians(self._angle)) / interface.fps]
        Game_Object.update(self)


class Solid(Game_Object):

    def __init__(self, position, dimension, color):
        self._image = pygame.Surface(dimension)
        super().__init__(position)
        self._image.fill(color)
        self._size = self._image.get_size()
    
    def update(self):
        Game_Object.update(self)
        self.value = pygame.sprite.groupcollide(interface.all, interface.environment, True, False)
            
        
class UI:

    def __init__(self):
        # Setting up the screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        # Game clock setting
        self.clock = pygame.time.Clock()

        # Group of Ships
        self.ships   = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.environment = pygame.sprite.Group()
        self.all = pygame.sprite.Group()

        # User
        self.user = Ship([100, 200], 'Images/ship.png', 10)
        self.ships.add(self.user)
        self.all.add(self.user)

        # Finalize screen
        pygame.display.set_caption("Shooter")

        dimension = [[[2200, 15], [1, 100]], [[2200, 5], [1, 799]], [[5, 2000], [1, 1]], [[5, 2000], [1099, 1]]]
        for obj in dimension:
            item = Solid(obj[1], obj[0], (255, 0, 0))
            self.environment.add(item)
            
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
            self.environment.update()
            pygame.display.update()
            print(self.user._speed , self.user._angle, self.clock.get_fps(), self.bullets.sprites())

        pygame.quit()


if __name__ == "__main__":
    interface = UI()
    interface.main()
