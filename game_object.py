import math
import random
import pygame


class Game_Object(pygame.sprite.Sprite):
    """Generic game object. Implements sprites rotation and movement.

    Arguments:
        game {object} -- game instance
        position {float: array} -- [x, y] spawn position
        image {object} -- pygame surface
        debuggable {bool} -- object shows rect and label if game runs in debug mode 
        need_max_rect {bool} -- generate static rect that fits the image indipendently of its angle
        camera_mode {string} -- normal = not player object
                               scrolling = locked camera on player ship
    """

    def __init__(self, game, position, image, debuggable, need_max_rect=False, camera_mode="normal"):
        super().__init__()
        self._game = game
        self._image = image
        if image:
            self._size = self._image.get_size()
        self._life = "immortal"
        self._speed = [0, 0] # [x, y]
        self._angle = 0
        self._spin = 0
        self._debuggable = debuggable
        self.image_handler() # initialize image attributes
        if need_max_rect:
            max_rect = self.get_max_rect()
            self.rect = pygame.Rect((0, 0),
                                    (max_rect,
                                     max_rect))
            self.rect.center = position
        else:
            self.rect = self._image.get_rect(center=position)
        self._position = [position[0], position[1]]
        self._origin = self._position
        self._label_position = self._position # required in debug
        self._camera_mode = camera_mode
        self._need_update = True

    def __str__(self):
        return """
        game_object = {
        _life: %s,
        _rect: %s,
        origin: %s,
        _position: %s,
        _speed: [%f, %f],
        _spin: %f,
        _angle: %f,
        _camera: %s,
        _distance_from_base: %s}""" % (self._life, self.rect, self._origin, self._position,
                           self._speed[0], self._speed[1],
                           self._spin, self._angle, self._camera_mode, self.distance_from(self._game.base._position))

    def explode(self, color=None):
        """kill the sprite and make fireworks"""

        self.kill()
        if color: # reduntant code due to performance issue TODO
            for x in range(50):
                shine = Shine(self._game, [self.rect.centerx, self.rect.centery],
                              random.randint(1, 360), spin=random.uniform(-2, 2),
                              color=color)
                self._game.environment.add(shine)
                self._game.all.add(shine)
        else:
            for x in range(50):
                shine = Shine(self._game, [self.rect.centerx, self.rect.centery],
                              random.randint(1, 360), spin=random.uniform(-2, 2),
                              color=(random.randint(1, 255),
                                     random.randint(1, 255),
                                     random.randint(1, 255)))
                self._game.environment.add(shine)
                self._game.all.add(shine)

    def hit(self, damage):
        """hit the object, life drops according to damage {int}"""

        if self._life != "immortal":
            self._life -= damage
            if self._life <= 0:
                self.explode()

    def spin(self, value):
        """spin the object by value {float} degree"""

        if value != 0:
            self._angle += value
            self._need_update = True

    def is_in_screen(self):
        """Object is in screen
        
        Returns:
            Bool -- True if the object is in sight"""

        if (abs(self._game.camera_x - self._position[0]) < (self._game.screen_size[0] / 2) + self.rect.width / 2 and
            abs(self._game.camera_y - self._position[1]) < (self._game.screen_size[1] / 2) + self.rect.height / 2):
            return True
        return False

    def distance_from(self, point):
        """Euclidean distance between point and self calculated according to its _position attribute.
        Arguments:
            point {tuple: float}

        Returns:
            float -- absolute distance"""

        return ((self._position[0] - point[0])**2 +
                (self._position[1] - point[1])**2)**0.5 

    def get_speed_vector_angle(self):
        """Calculate angle of the speed vector using atan2
        
        Returns:
            float -- angle in degrees, None if speed vector is [0, 0]"""

        if self._speed == [0, 0]:
            return None
        return math.degrees(math.atan2(self._speed[1], self._speed[0]))

    def get_max_rect(self):
        """side lenght of the square which contains the image independently of the its angle.
        
        Returns:
            float"""

        self.image_handler()
        rect = self.rotated_image.get_rect()
        return (rect.width**2 + rect.height**2)**0.5

    def display_label(self):
        """Debug mode.Display object __str__ as a label in game"""

        values = self.__str__()
        values = values.split("\n")
        offset = -15

        for string in values:
            offset += 15
            display_label = self._game.debug_font.render(string, 1, (255, 255, 0))
            self._game.screen.blit(display_label, (self._label_position[0], 
                                                   self._label_position[1] + offset))

    def display_rect(self):
        """Debug mode.Display sprite rect on screen"""

        new_rect = self.rect.copy()
        new_rect.topleft = self._label_position
        pygame.draw.rect(self._game.screen, (255, 0, 0),
                         new_rect, 1)

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
        """Updates sprite position and image"""

        # redefine position and rotate sprite image 
        self._position[0] += self._speed[0] / self._game.delta_time
        self._position[1] += self._speed[1] / self._game.delta_time
        self.rect.centerx = int(self._position[0])
        self.rect.centery = int(self._position[1])

        if self._need_update and self.is_in_screen():
            self.image_handler()
            self._need_update = False

        if self._camera_mode == 'scrolling':
            # user ship handling with camera position
            self._game.camera_x = int(self._position[0])
            self._game.camera_y = int(self._position[1])
            w, h = self.rotated_image.get_size()
            x = (self._game.screen_size[0] / 2.0) - w / 2
            y = (self._game.screen_size[1] / 2.0) - h / 2
            self._label_position = ((self._game.screen_size[0] / 2.0) - self.rect.width / 2,
                                    (self._game.screen_size[1] / 2.0) - self.rect.height / 2)
            # blitting
            self._game.screen.blit(self.rotated_image, (x, y))

        elif self._camera_mode == "normal" and self.is_in_screen():
            # calculate the center origin of the rotated image
            self._origin = (self._position[0] - self._size[0] / 2 + self.min_box[0] - self.pivot_move[0],
                            self._position[1] - self._size[1] / 2 - self.max_box[1] + self.pivot_move[1])
            # calculate the debug info position
            self._label_position = ((self._game.screen_size[0] / 2) - (self._game.camera_x - self.rect.x),
                                    (self._game.screen_size[1] / 2) - (self._game.camera_y - self.rect.y))
            # blitting
            self._game.screen.blit(self.rotated_image, 
                                   ((self._game.screen_size[0] / 2) - ((self._game.camera_x - self._origin[0])),
                                    (self._game.screen_size[1] / 2) - ((self._game.camera_y - self._origin[1]))))

        if self._game.debug and self.is_in_screen() and self._debuggable:
            self.display_label()
            self.display_rect()


class Background(pygame.sprite.Sprite):
    """background stars
    
    Arguments:
        game {object} -- game instance
        image {object} -- pygame surface"""

    def __init__(self, game, image):
        super().__init__()
        self._game = game
        self._image = image
        self.rect = self._image.get_rect(topleft=(0, 0))
    
    def update(self):
        # blitting
        self._game.screen.blit(self._image, 
                               ((self._game.screen_size[0] / 2) - ((self._game.camera_x)),
                                (self._game.screen_size[1] / 2) - ((self._game.camera_y))))


class Surface(Game_Object):
    """Generic game surface.
    
    Arguments:
        game {object} -- game instance
        image {object} -- pygame surface
        position {array: float} -- [x, y] spawn position
        need_max_rect {bool} -- True to have fixed rect size
        debuggable {bool} -- object shows rect and label if game runs in debug mode  
        camera_mode {string} -- same as Game_Object
        spin {float} -- default is 0
        speed {array: float} -- default is [0, 0]
        life {float} -- default is immortal object"""

    def __init__(self, game, image, position, need_max_rect=False, damage=5,
                 debuggable=True, camera_mode="normal", spin=0, speed=[0, 0],
                 life="immortal"):
        super().__init__(game, position, image,
                         debuggable, need_max_rect=need_max_rect,
                         camera_mode=camera_mode)
        self._spin = spin
        self._speed = speed
        self._life = life
        self._damage = damage

    def update(self):
        self.spin(self._spin / self._game.delta_time)
        Game_Object.update(self)


class Edge(Surface):
    """Map Edge surface, child of Surface"""

    def __init__(self, game, position, dimension, color):
        super().__init__(game, pygame.Surface(dimension, pygame.SRCALPHA).convert_alpha(),
                         position, False)
        self._color = color
        self._image.fill(color)
        self.rect = self._image.get_rect(topleft=position)
        self._need_update = False

    def update(self):
        self._label_position = ((self._game.screen_size[0] / 2) - ((self._game.camera_x - self.rect.x)),
                                (self._game.screen_size[1] / 2) - ((self._game.camera_y - self.rect.y)))
        self._game.screen.blit(self._image, 
                               ((self._game.screen_size[0] / 2) - ((self._game.camera_x - self.rect.x)),
                                (self._game.screen_size[1] / 2) - ((self._game.camera_y - self.rect.y))))

        # everything which touch an edge explodes
        for caught in pygame.sprite.spritecollide(self, self._game.all, False):
            if not self._game.edge.has(caught):
                caught.explode()


class Shine(Surface): # should be child of pygame.sprite due to performance issue
    """lights and shines, child of Surface"""

    def __init__(self, game, position, angle, image=None,
                 spin=0, dimension=[5, 2], color=(155, 155, 0),
                 speed=None):
        if image:
            super().__init__(game, image, position, False,  debuggable=False)
        else:
            super().__init__(game, pygame.Surface(dimension, pygame.SRCALPHA).convert_alpha(),
                            position, False,  debuggable=False)
            self._image.fill(color)
            self._color = color

        self._angle = random.randint(0, 360)
        if speed is None:
            self._speed = [(-math.cos(math.radians(angle))) * random.randint(0, 7) + random.uniform(-1, 1),
                           (math.sin(math.radians(angle))) * random.randint(0, 7) + random.uniform(-1, 1)] 
        else:
            self._speed = speed
        self._time2live = random.randint(5, 100)
        self._spin = spin

    def explode(self):
        self.kill()

    def update(self):
        self._time2live -= 1 / self._game.delta_time
        if self._time2live < 0:
            self.kill()
        Game_Object.update(self) # no spin for shines due to performance issue TODO
