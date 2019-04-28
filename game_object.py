import math
import random
import pygame


class Game_Object(pygame.sprite.Sprite):
    """Generic game object. Implements sprites rotation and movement.

    Arguments:
        game {object} -- game instance
        position {float: array} -- [x, y] spawn position
        image {object} -- pygame image object
        need_max_rect {bool} -- generate static rect that fits the image indipendently of its angle
        camera_mode{string} -- normal = not player object
                               scrolling = locked camera on player ship
    """

    def __init__(self, game, position, image, need_max_rect=False, camera_mode="normal"):
        super().__init__()
        self._game = game
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
        origin: %s,
        _position: %s,
        _speed: [%f, %f],
        _spin: %f,
        _angle: %f,
        _camera: %s}""" % (self._life, self.rect, self.origin, self._position,
                           self._speed[0], self._speed[1],
                           self._spin, self._angle, self._camera_mode)

    def hit(self, damage):
        """hit the object, life drops according to damage {int}"""

        if self._life != "immortal":
            self._life -= damage
            if self._life <= 0:
                self.kill()

    def spin(self, value):
        """spin the object by value {float} deegree"""

        if value != 0:
            self._angle += value
            self._need_update = True

    def is_in_screen(self):
        """return True if the object is in sight
        
        Returns:
            Bool"""

        if (abs(self._game.cameraX - self._position[0]) < (self._game.screen_size[0] / 2) and
            abs(self._game.cameraY - self._position[1]) < (self._game.screen_size[1] / 2)):
            return True
        return False

    def distance_from(self, obj):
        pass #TODO

    def get_max_rect(self):
        """side lenght of the square which contains the image independently of the its angle.
        
        Returns:
            float"""

        self.image_handler()
        rect = self.rotated_image.get_rect()
        return (rect.width**2 + rect.height**2)**0.5

    def display_label(self):
        """Display object __str__ as a label in game"""

        values = self.__str__()
        values = values.split("\n")
        offset = -15

        for string in values:
            offset += 15
            display_label = self.game.debug_font.render(string, 1, (255, 255, 0))
            self._game.screen.blit(display_label, (self.label_position[0], 
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
        """Updates sprite position and image"""

        # redefine position and rotate sprite image 
        self._position[0] += self._speed[0] / self._game.deltaTime
        self._position[1] += self._speed[1] / self._game.deltaTime
        self.rect.centerx = int(self._position[0])
        self.rect.centery = int(self._position[1])

        if self._need_update and self.is_in_screen():
            self.image_handler()
            self._need_update = False

        if self._camera_mode == 'scrolling':
            self._game.cameraX = int(self._position[0])
            self._game.cameraY = int(self._position[1])
            w, h = self.rotated_image.get_size()
            x = (self._game.screen_size[0] / 2.0) - w / 2
            y = (self._game.screen_size[1] / 2.0) - h / 2
            self.label_position = (x + 45, y)

            self._game.screen.blit(self.rotated_image, (x, y))

        elif self._camera_mode == "normal" and self.is_in_screen():
             # calculate the upper left origin of the rotated image
            self.origin = (self._position[0] - self._size[0] / 2 + self.min_box[0] - self.pivot_move[0],
                           self._position[1] - self._size[1] / 2 - self.max_box[1] + self.pivot_move[1])
            self.label_position = ((self._game.screen_size[0] / 2) - ((self._game.cameraX - self.origin[0])),
                                   (self._game.screen_size[1] / 2) - ((self._game.cameraY - self.origin[1])) - 30)

            self._game.screen.blit(self.rotated_image, 
                                   ((self._game.screen_size[0] / 2) - ((self._game.cameraX - self.origin[0])),
                                    (self._game.screen_size[1] / 2) - ((self._game.cameraY - self.origin[1]))))
        if self._game.debug:
            self.display_label()
            self.display_rect()


class Surface(Game_Object):
    """Simple game surface.
    
    Arguments:
        game {object} -- game instance
        position {array: float} -- [x, y] spawn position
        dimension {array: float} -- [x, y] polygon dimension
        color {tuple} -- (R, G, B) color standard
        need_max_rect {bool} -- True to have fixed rect size 
        camera_mode {string} -- same as Game_Object
        spin {float} -- default is 0
        speed {array: float} -- default is [0, 0]
        life {float} -- default is immortal object"""

    def __init__(self, game, position, dimension, color, need_max_rect,
                 camera_mode="normal", spin=0, speed=[0, 0],
                 life="immortal"):
        super().__init__(game, position, pygame.Surface(dimension, pygame.SRCALPHA).convert_alpha(),
                         need_max_rect=need_max_rect, camera_mode=camera_mode)
        self._color = color
        self._image.fill(color)
        self._spin = spin
        self._speed = speed
        self._life = life

    def update(self):
        self.spin(self._spin / self._game.deltaTime)
        Game_Object.update(self)


class Debris(Game_Object):
    pass #TODO


class Edge(Surface):
    """Map Edge surface, child of Surface"""

    def __init__(self, game, position, dimension, color):
        super().__init__(game, position, dimension, color, False)
        self.rect = self._image.get_rect(topleft=position)
        self._need_update = False

    def update(self):
        self.label_position = ((self._game.screen_size[0] / 2) - ((self._game.cameraX - self.rect.x)),
                               (self._game.screen_size[1] / 2) - ((self._game.cameraY - self.rect.y)) - 30)
        self._game.screen.blit(self._image, 
                               ((self._game.screen_size[0] / 2) - ((self._game.cameraX - self.rect.x)),
                                (self._game.screen_size[1] / 2) - ((self._game.cameraY - self.rect.y))))


class Shine(Surface):
    """lights and shines, child of Surface"""

    def __init__(self, game, position, angle, spin=0, dimension=[5, 2], color=(155, 155, 0)):
        super().__init__(game, position, dimension, color, False)
        self._angle = random.randint(0, 360)
        self._speed = [(-math.cos(math.radians(angle))) * random.randint(0, 7) + random.uniform(-1, 1),
                       (math.sin(math.radians(angle))) * random.randint(0, 7) + random.uniform(-1, 1)] 
        self._time2live = random.randint(5, 100)
        self._spin = spin
    
    def update(self):
        self._time2live -= 1 / self._game.deltaTime
        if self._time2live < 0:
            self.kill()
        Game_Object.update(self) # no spin for shines due to performance issue TODO


class Stars(Surface):
    """background stars, child of Surface"""

    def __init__(self, game, position, color=(255, 255, 255)):
        super().__init__(game, position, [1, 1], color, False)
    
    def update(self):
        Game_Object.update(self)
