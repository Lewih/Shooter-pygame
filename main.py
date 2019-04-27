import math
import random
import threading
import pygame

# Initialize pygame
pygame.init()

# Constants
SCREEN_SIZE = (1300, 800)
CAMERA_X = 0
CAMERA_Y = 0
DB_FONT = pygame.font.SysFont("monospace", 15)
DEBUG = False


class Game_Object(pygame.sprite.Sprite):
    """Generic game object.
    Implements sprites rotation and movement.
    """

    def __init__(self, position, image, need_max_rect=False, camera_mode="normal"):
        super().__init__()
        self._image = image
        self._size = self._image.get_size()
        self._life = "immortal"
        self._speed = [0, 0] # [x, y]
        self._angle = 0
        self._spin = 0
        self.image_handler() # initialize image attributes
        if need_max_rect:
            self.max_rect = self.get_max_rect()
            self.rect = pygame.Rect((0, 0),
                                    (self.max_rect,
                                     self.max_rect))
            self.rect.center = position
        else:
            self.rect = self._image.get_rect(center=position)
        self._position = [position[0], position[1]]
        self._camera_mode = camera_mode
        self._need_update = True

    def __str__(self):
        return """
        game_object = {
        _life: %s,
        _rect: %s,
        _origin: %s,
        _position: %s,
        _speed: [%f, %f],
        _spin: %f,
        _angle: %f,
        _camera: %s}""" % (self._life, self.rect, self._origin, self._position,
                           self._speed[0], self._speed[1],
                           self._spin, self._angle, self._camera_mode)

    def hit(self, damage):
        """hit the object, life drops according to damage {int}"""

        if self._life != "immortal":
            self._life -= damage
            if self._life <= 0:
                self.kill()

    def spin(self, value):
        """spin the object"""

        if value != 0:
            self._angle += value
            self._need_update = True

    def is_in_screen(self):
        """return True if the object is in sight"""

        if abs((CAMERA_X - self._position[0]) < (SCREEN_SIZE[0] / 2) and
               abs(CAMERA_Y - self._position[1]) < (SCREEN_SIZE[1] / 2)):
            return True
        return False

    def distance_from(self, obj):
        pass #TODO

    def get_max_rect(self):
        """get rect that contains the image at every angolation"""

        max_value = 0
        for angle in range(360):
            self._angle = angle
            self.image_handler()
            rect = self.rotated_image.get_rect()
            if rect.width > max_value:
                max_value = rect.width
            if rect.height > max_value:
                max_value = rect.height
        self._angle = 0
        return max_value

    def display_label(self):
        """Display object __str__ as a label in game"""

        values = self.__str__()
        values = values.split("\n")
        offset = -15

        for string in values:
            offset += 15
            display_label = DB_FONT.render(string, 1, (255, 255, 0))
            GAME.screen.blit(display_label, (self.label_position[0], 
                                             self.label_position[1] + offset))

    def display_rect(self):
        pass #TODO

    def image_handler(self):
        """Redefine rotated image and center"""

        box = [pygame.math.Vector2(p) for p in [(0, 0), (self._size[0], 0),
               (self._size[0], -self._size[1]), (0, -self._size[1])]]
        box_rotate = [p.rotate(self._angle) for p in box]
        self.min_box = (min(box_rotate, key=lambda p: p[0])[0],
                        min(box_rotate, key=lambda p: p[1])[1])
        self.max_box = (max(box_rotate, key=lambda p: p[0])[0],
                        max(box_rotate, key=lambda p: p[1])[1])

        # calculate the translation of the pivot 
        pivot = pygame.math.Vector2(self._size[0] / 2, -self._size[1] / 2)
        pivot_rotate = pivot.rotate(self._angle)
        self.pivot_move = pivot_rotate - pivot

        self.rotated_image = pygame.transform.rotate(self._image, self._angle)

    def update(self):
        """Overridden update method.
        Updates sprite position and image"""

        # redefine position and rotate sprite image 
        if self._need_update and self.is_in_screen():
            self.image_handler()
            self._need_update = False

        self._position[0] += self._speed[0] / DELTA_TIME
        self._position[1] += self._speed[1] / DELTA_TIME
        self.rect.centerx = int(self._position[0])
        self.rect.centery = int(self._position[1])

        if self._camera_mode == 'scrolling':
            global CAMERA_X, CAMERA_Y
            CAMERA_X = int(self._position[0])
            CAMERA_Y = int(self._position[1])
            w, h = self.rotated_image.get_size()
            x = (SCREEN_SIZE[0] / 2.0) - w / 2
            y = (SCREEN_SIZE[1] / 2.0) - h / 2
            self.label_position = (x + 45, y)

            GAME.screen.blit(self.rotated_image, (x, y))

        elif self._camera_mode == "normal" and self.is_in_screen():
             # calculate the upper left origin of the rotated image
            self._origin = (self._position[0] - self._size[0] / 2 + self.min_box[0] - self.pivot_move[0],
                            self._position[1] - self._size[1] / 2 - self.max_box[1] + self.pivot_move[1])
            self.label_position = ((SCREEN_SIZE[0] / 2) - ((CAMERA_X - self._origin[0])),
                                   (SCREEN_SIZE[1] / 2) - ((CAMERA_Y - self._origin[1])) - 30)

            GAME.screen.blit(self.rotated_image, ((SCREEN_SIZE[0] / 2) - ((CAMERA_X - self._origin[0])),
                                                  (SCREEN_SIZE[1] / 2) - ((CAMERA_Y - self._origin[1]))))
        if DEBUG:
            self.display_label()
            self.display_rect()


class Ship(Game_Object):
    """Ship game object.

    Arguments:
        start_pos {float: array} -- [x, y]
        image {str} -- Ship Image directory
        acceleration {float} -- Ship acceleration
        h_acceleration {float} -- horizontal acceleration
        spin {float} -- Ship spin
        max_speed {float} -- nominal max vertical speed
        bullet_speed {float} -- Ship bullet speed
        fire_rate {float} -- fire sleep in game tick / DELTA_TIME
        camera_mode{string} -- normal = not player object
                               scrolling = locked camera on player ship
        controlled{bool}  -- ship is controlled by user"""
    
    def __init__(self, start_pos, image, acceleration,
                 h_acceleration, spin, max_speed, bullet_speed,
                 fire_rate, camera_mode='normal', controlled=False):
        super().__init__(start_pos, pygame.image.load(image).convert_alpha(),
                         need_max_rect=True, camera_mode=camera_mode)
        self._image_dir = image
        self._life = 100.0
        self._acceleration = acceleration
        self._spin = spin
        self._max_speed = max_speed
        self._h_acceleration = h_acceleration
        self._bullet_speed = bullet_speed
        self._fire_rate = fire_rate
        self._bullet_timer = 0
        self._controlled = controlled

    def __str__(self):
        return("""    Ship = {
        _life: %s,
        _rect: %s,
        _position: %s,
        _speed: [%f, %f],
        _angle: %s,
        _acceleration: %f,
        _max_speed: %f,
        _h_acceleration: %f,
        _spin: %f,
        _bullet_speed: %f
        _fire_rate: %f,
        _bullet_timer: %f,
        _image: %s,
        _camera_mode: %s,
        _controlled: %d}""" % (self._life, self.rect, self._position, self._speed[0], self._speed[1],
                               self._angle, self._acceleration, self._max_speed, self._h_acceleration,
                               self._spin, self._bullet_speed, self._fire_rate, self._bullet_timer,
                               self._image_dir, self._camera_mode, self._controlled))

    def controls(self, pressedKeys):
        """keyboard handling"""

        cos = math.cos(math.radians(self._angle))
        sin = math.sin(math.radians(self._angle))
        cos90 = math.cos(math.radians(self._angle + 90))
        sin90 = math.sin(math.radians(self._angle + 90))

        self.rel_max_speed = [self._max_speed * cos, 
                              self._max_speed * -sin]

        self.rel_max_h_speed = [self._max_speed * cos90, 
                                self._max_speed * -sin90]

        if pressedKeys[pygame.K_UP]:
            shine = Shine([self.rect.centerx, self.rect.centery],
                          self._angle, dimension=[2, 2], color=(255, 255, 255))
            GAME.environment.add(shine)
            GAME.all.add(shine)

            if self.rel_max_speed[0] > 0:
                if self._speed[0] <= self.rel_max_speed[0]:
                    self._speed[0] += self._acceleration * cos / DELTA_TIME
            else:
                if self._speed[0] >= self.rel_max_speed[0]:
                    self._speed[0] += self._acceleration * cos / DELTA_TIME

            if self.rel_max_speed[1] > 0:
                if self._speed[1] <= self.rel_max_speed[1]:
                    self._speed[1] += self._acceleration * -sin / DELTA_TIME
            else:
                if self._speed[1] >= self.rel_max_speed[1]:
                    self._speed[1] += self._acceleration * -sin / DELTA_TIME

        elif pressedKeys[pygame.K_DOWN]:
            if self.rel_max_speed[0] > 0:
                if self._speed[0] >= -self.rel_max_speed[0]:
                    self._speed[0] -= self._acceleration * cos / DELTA_TIME
            else:
                if self._speed[0] <= -self.rel_max_speed[0]:
                    self._speed[0] -= self._acceleration * cos / DELTA_TIME

            if self.rel_max_speed[1] > 0:
                if self._speed[1] >= -self.rel_max_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / DELTA_TIME
            else:
                if self._speed[1] <= -self.rel_max_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / DELTA_TIME

        if pressedKeys[pygame.K_q]:
            if self.rel_max_h_speed[0] > 0:
                if self._speed[0] <= self.rel_max_h_speed[0]:
                    self._speed[0] += self._h_acceleration * cos90 / DELTA_TIME
            else:
                if self._speed[0] >= self.rel_max_h_speed[0]:
                    self._speed[0] += self._h_acceleration * cos90 / DELTA_TIME

            if self.rel_max_h_speed[1] > 0:
                if self._speed[1] <= self.rel_max_h_speed[1]:
                    self._speed[1] += self._h_acceleration * -sin90 / DELTA_TIME
            else:
                if self._speed[1] >= self.rel_max_h_speed[1]:
                    self._speed[1] += self._h_acceleration * -sin90 / DELTA_TIME

        elif pressedKeys[pygame.K_e]:
            if self.rel_max_h_speed[0] > 0:
                if self._speed[0] >= -self.rel_max_h_speed[0]:
                    self._speed[0] -= self._h_acceleration * cos90 / DELTA_TIME
            else:
                if self._speed[0] <= -self.rel_max_h_speed[0]:
                    self._speed[0] -= self._h_acceleration * cos90 / DELTA_TIME

            if self.rel_max_h_speed[1] > 0:
                if self._speed[1] >= -self.rel_max_h_speed[1]:
                    self._speed[1] -= self._h_acceleration * -sin90 / DELTA_TIME
            else:
                if self._speed[1] <= -self.rel_max_h_speed[1]:
                    self._speed[1] -= self._h_acceleration * -sin90 / DELTA_TIME

        if pressedKeys[pygame.K_LEFT]:
            self.spin(self._spin / DELTA_TIME)

        if pressedKeys[pygame.K_RIGHT]:
            self.spin(-self._spin / DELTA_TIME)

        if pressedKeys[pygame.K_w]:
            self._speed = [0, 0]

        if pressedKeys[pygame.K_SPACE] and self._bullet_timer <= 0:
            self._bullet_timer = self._fire_rate
            new_bullet = Bullet(self._position, self._angle, self._bullet_speed)
            GAME.bullets.add(new_bullet)

    def update(self, pressedKeys):
        """Overriden pygame.sprite.sprite method.
        Acceleration is applied according to its vectorial component and in-game events.
        
        Arguments:
            pressedKeys {Tuple} -- collection of events generated by pygame.key"""

        for caught in pygame.sprite.spritecollide(self, GAME.edge, False):
            self.kill()
            for x in range(20):
                shine = Shine([self.rect.centerx, self.rect.centery], self._angle)
                GAME.environment.add(shine)
                GAME.all.add(shine)

        if self._bullet_timer > 0:
            self._bullet_timer -= 1 / DELTA_TIME

        if self._controlled:
            self.controls(pressedKeys)

        Game_Object.update(self)


class Bullet(Game_Object):
    """Bullet game object shot by sprites according to their angle.
        
        Arguments:
            start_pos {array: float} -- [x, y] start position
            angle {float} -- angle of the vector in degrees
            bullet_speed {float} -- bullet speed
            image {string} -- default is standard bullet"""

    def __init__(self, start_pos, angle, bullet_speed,
                 image='Images/bullet.png'):
        super().__init__(start_pos, pygame.image.load(image).convert_alpha())
        self._angle = angle
        self._spin = 0
        self._bullet_speed = bullet_speed
        self._speed = [self._bullet_speed * math.cos(math.radians(self._angle)), 
                       self._bullet_speed * -math.sin(math.radians(self._angle))]
        self._damage = 1

    def update(self):
        for caught in pygame.sprite.spritecollide(self, GAME.targets, False):
            self.kill()
            for x in range(20):
                shine = Shine([self.rect.centerx, self.rect.centery],
                              self._angle, spin=random.uniform(-2, 2))
                GAME.environment.add(shine)
                GAME.all.add(shine)
            caught.hit(self._damage)
        Game_Object.update(self)


class Surface(Game_Object):
    """Simple game surface.
    
        Arguments:
            position {array: float} -- [x, y] start position
            dimension {array: float} -- [x, y] polygon dimension
            color {tuple} -- (R, G, B) color standard
            need_max_rect {bool} -- True to permit collisions TODO
            camera_mode {string} -- same as Game_Object
            spin {float} -- default is 0
            speed {array: float} -- default is [0, 0]
            life {float} -- default is immortal object"""

    def __init__(self, position, dimension, color, need_max_rect,
                 camera_mode="normal", spin=0, speed=[0, 0],
                 life="immortal"):
        super().__init__(position, pygame.Surface(dimension, pygame.SRCALPHA).convert_alpha(),
                         need_max_rect=need_max_rect, camera_mode=camera_mode)
        self._color = color
        self._image.fill(color)
        self._spin = spin
        self._speed = speed
        self._life = life

    def update(self):
        self.spin(self._spin / DELTA_TIME)
        Game_Object.update(self)


class Debris(Game_Object):
    pass #TODO


class Edge(Surface):
    """Map Edge surface"""

    def __init__(self, position, dimension, color):
        super().__init__(position, dimension, color, False)
        self.rect = self._image.get_rect(topleft=position)
        self._need_update = False

    def update(self):
        self.label_position = ((SCREEN_SIZE[0] / 2) - ((CAMERA_X - self.rect.x)),
                               (SCREEN_SIZE[1] / 2) - ((CAMERA_Y - self.rect.y)) - 30)
        GAME.screen.blit(self._image, ((SCREEN_SIZE[0] / 2) - ((CAMERA_X - self.rect.x)),
                                       (SCREEN_SIZE[1] / 2) - ((CAMERA_Y - self.rect.y))))


class Shine(Surface):
    """lights and shines"""

    def __init__(self, position, angle, spin=0, dimension=[5, 2], color=(155, 155, 0)):
        super().__init__(position, dimension, color, False)
        self._angle = random.randint(0, 360)
        self._speed = [(-math.cos(math.radians(angle))) * random.randint(0, 7) + random.uniform(-1, 1),
                       (math.sin(math.radians(angle))) * random.randint(0, 7) + random.uniform(-1, 1)] 
        self._time2live = random.randint(5, 100)
        self._spin = spin
    
    def update(self):
        self._time2live -= 1 / DELTA_TIME
        if self._time2live < 0:
            self.kill()
        Game_Object.update(self) # no spin for shines due to performance issue TODO


class Stars(Surface):
    """background stars"""

    def __init__(self, position, color=(255, 255, 255)):
        super().__init__(position, [1, 1], color, False)
    
    def update(self):
        Game_Object.update(self)


class Test_game:
    """Test game with some sprites and basic settings"""

    def __init__(self, map_size):
        global SCREEN_SIZE, CAMERA_X, CAMERA_Y
        self.map_size = map_size

        # Setting up the screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        SCREEN_SIZE = self.screen.get_size()

        # Game clock setting
        self.clock = pygame.time.Clock()

        # Groups
        self.ships = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.edge = pygame.sprite.Group()
        self.rectangles = pygame.sprite.Group()
        self.environment = pygame.sprite.Group()
        self.starry_sky = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.all = pygame.sprite.Group()

        # User
        self.user = Ship([100, 200], 'Images/ship.png', 0.7, 0.4, 10, 10.0, 10.0, 7,
                         camera_mode='scrolling', controlled=True)
        CAMERA_X = 100
        CAMERA_Y = 200
        self.ships.add(self.user)

        # Finalize screen
        pygame.display.set_caption("Shooter")

        # edge objects [[position], [dimension]]
        boundaries = [[[0, 0], [map_size[0], 20]],
                      [[0, map_size[1]], [map_size[0], 20]],
                      [[0, 0], [20, map_size[1]]],
                      [[map_size[0], 0], [20, map_size[1] + 20]]]
        for obj in boundaries:
            item = Edge(obj[0], obj[1], (255, 0, 0))
            self.edge.add(item)
            self.environment.add(item)
            self.targets.add(item)
            self.all.add(item)

        # test objects
        for x in range(100):
            test = Surface([random.randint(1, map_size[0]),
                            random.randint(1, map_size[1])],
                           [60, 60], (0, 0, 255), True, spin=1,
                           speed=[0, 0], life=5)
            self.rectangles.add(test)
            self.environment.add(test)
            self.targets.add(test)
            self.all.add(test)

        # Starry sky
        if not DEBUG:
            for x in range(1000):
                star = Stars((random.randint(0, self.map_size[0]),
                              random.randint(0, self.map_size[1])))
                self.starry_sky.add(star)
                self.all.add(star)

    def main(self):
        global DELTA_TIME
        done = False

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # delta time, game is frame rate indipendent
            DELTA_TIME = 30 / self.clock.tick_busy_loop(60)

            # Refresh screen and update sprites
            self.screen.fill((0, 0, 0))
            self.starry_sky.update()
            self.bullets.update()
            self.ships.update(pygame.key.get_pressed())
            self.environment.update()
            display_label = DB_FONT.render(" Sprites in game:" +
                                           str(self.all.sprites) +
                                           ", fps: " + str(self.clock.get_fps()),
                                           1, (255, 255, 0))
            GAME.screen.blit(display_label, (0, 0))
            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    GAME = Test_game((1500, 1500))
    GAME.main()
