import pygame
import random
import math
import threading
import socket

# Initialize pygame
pygame.init()

# Constants
SCREEN_SIZE = (1100, 800)
CAMERA_X = 0
CAMERA_Y = 0
DB_FONT = pygame.font.SysFont("monospace", 15)
DEBUG = True

class Server(threading.Thread):
	PORT = 50000

	def __init__(self):
		super().__init__()
		self.text = ''
		self.client = None
		self.address = None

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind(('localhost', self.PORT))
		self.server.listen(1)

	def send(self, message):
		try:
			self.server.sendall(bytes(str(message), 'ascii'))
		except Exception as err:
			print(err)
			exit(1)

	def reading(self):
		if self.text=='exit':
			self.send('shutdown()')
			self.server.shutdown(socket.SHUT_RDWR)
			self.server.close()

		else:
			self.send(interface.user.str)

	def run(self):
		print('\nwaiting for new connection...')
		self.client, self.address = self.server.accept()
		print('\nConnected to ',self.address + '\n')
		self.client.send(bytes("Connected!\n", 'ascii'))
		while True:
			try:
				self.text = str(self.client.recv(4096), 'ascii')
				self.reading()
			except Exception as err:
				self.send(err)


class Client(threading.Thread):
    pass


class Game_Object(pygame.sprite.Sprite):
    """Generic game object. 
    Implements sprites rotation and movement.
    _image and _size must be defined in child class.
    """

    def __init__(self, position, camera_mode = "normal"):
        super().__init__()
        self._speed      = [0, 0] # [x, y]
        self._angle      = 0
        self._spin       = 0
        self.rect        = self._image.get_rect()
        self.rect.x      = position[0]
        self.rect.y      = position[1]
        self._position   = [position[0], position[1]]
        self._camera_mode = camera_mode

    def __str__(self):
        return """
        _position: [%f, %f]
        _speed: [%f, %f]
        _spin: %f
        _angle: %f
        _camera: %s""" % (self.rect.x, self.rect.y, self._speed[0], self._speed[1],
                        self._spin, self._angle, self._camera_mode)

    def display_label(self):
        """Display object __str__ as a label in game"""

        values = self.__str__()
        values = values.split("\n")
        offset = 0
	
        for string in values:
            offset += 15
            display_label = DB_FONT.render(string ,1, (255, 255, 0))
            interface.screen.blit(display_label, (self._display_label_position[0], 
                                          self._display_label_position[1] + offset))

    def update(self):
        global CAMERA_X, CAMERA_Y
        self._position[0] += self._speed[0] / DELTA_TIME
        self._position[1] += self._speed[1] / DELTA_TIME
        self.rect.x        = int(self._position[0])
        self.rect.y        = int(self._position[1])

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

        # control whether it is an edge element
        if interface.edge.has(self): 
            origin = (self.rect.x , self.rect.y)

        self.rotated_image = pygame.transform.rotate(self._image, self._angle)
        w, h = self.rotated_image.get_size()

        if self._camera_mode == 'scrolling':
            CAMERA_X = self.rect.x
            CAMERA_Y = self.rect.y
            self._display_label_position = ((SCREEN_SIZE[0] / 2.0) - w / 2 + 45, 10 + (SCREEN_SIZE[1] / 2.0) - h / 2 )
            interface.screen.blit(self.rotated_image, ((SCREEN_SIZE[0] / 2.0) - w / 2, (SCREEN_SIZE[1] / 2.0) - h / 2))
        
        elif self._camera_mode == "normal":
            self._display_label_position = ((SCREEN_SIZE[0] / 2) - ((CAMERA_X - origin[0])),
                                                       (SCREEN_SIZE[1] / 2) - ((CAMERA_Y - origin[1])) - 30)
            interface.screen.blit(self.rotated_image, ((SCREEN_SIZE[0] / 2) - ((CAMERA_X - origin[0])),
                                                       (SCREEN_SIZE[1] / 2) - ((CAMERA_Y - origin[1]))))
        if DEBUG:
            self.display_label()


class Ship(Game_Object):
    """Ship game object.
    
    Arguments:
        start_pos {float: array} -- [x, y]
        image {str} -- Ship Image directory
        acceleration {float} -- Ship acceleration
        spin {float} -- Ship spin
        max_v_speed {float} -- nominal max vertical speed
        max_h_speed {float} -- nominal max horizontal speed
        bullet_speed {float} -- Ship bullet speed
        fire_rate {float} -- fire sleep in game tick / DELTA_TIME
        camera_mode{string} -- normal = not player object
                               scrolling = locked camera on player ship
        controlled{bool}  -- ship is controlled by user"""
    
    def __init__(self, start_pos, image, acceleration,
                 spin, max_v_speed, max_h_speed, bullet_speed,
                 fire_rate, camera_mode = 'normal', controlled = False):
        self._image_dir    = image
        self._image        = pygame.image.load(image).convert_alpha()
        super().__init__(start_pos, camera_mode = camera_mode)
        self._size         = self._image.get_size()
        self._acceleration = acceleration
        self._spin         = spin
        self._max_v_speed  = max_v_speed
        self._max_h_speed  = max_h_speed
        self._bullet_speed = bullet_speed
        self._fire_rate    = fire_rate
        self._bullet_timer = 0
        self._controlled = controlled
    
    def __str__(self):
        return("""Ship = {
        _position: [%f, %f],
        _speed: [%f, %f],
        _acceleration: %f,
        _max_v_speed: %f,
        _max_h_speed: %f,
        _spin: %f,
        _bullet_speed: %f
        _fire_rate: %f,
        _bullet_timer: %f,
        _image: %s
        _camera_mode: %s
        _controlled: %d}""" % (self.rect.x, self.rect.y, self._speed[0], self._speed[1],
                        self._acceleration, self._max_v_speed, self._max_h_speed,
                        self._spin, self._bullet_speed, self._fire_rate, self._bullet_timer,
                        self._image_dir, self._camera_mode, self._controlled))

    def controls(self, pressedKeys):
        """keyboard handling"""

        cos = math.cos(math.radians(self._angle))
        sin = math.sin(math.radians(self._angle))
        cos90 = math.cos(math.radians(self._angle + 90))
        sin90 = math.sin(math.radians(self._angle + 90))

        self._rel_max_v_speed = [self._max_v_speed * cos, 
                                 self._max_v_speed * -sin]
        
        self._rel_max_h_speed = [self._max_v_speed * cos90, 
                                 self._max_v_speed * -sin90]
        
        if pressedKeys[pygame.K_UP]:
            if self._rel_max_v_speed[0] > 0:
                if self._speed[0] <= self._rel_max_v_speed[0]:
                    self._speed[0] += self._acceleration * cos / DELTA_TIME
            else:
                if self._speed[0] >= self._rel_max_v_speed[0]:
                    self._speed[0] += self._acceleration * cos / DELTA_TIME

            if self._rel_max_v_speed[1] > 0:
                if self._speed[1] <= self._rel_max_v_speed[1]:
                    self._speed[1] += self._acceleration * -sin / DELTA_TIME
            else:
                if self._speed[1] >= self._rel_max_v_speed[1]:
                    self._speed[1] += self._acceleration * -sin / DELTA_TIME
            
        elif pressedKeys[pygame.K_DOWN]:
            if self._rel_max_v_speed[0] > 0:
                if self._speed[0] >= -self._rel_max_v_speed[0]:
                    self._speed[0] -= self._acceleration * cos / DELTA_TIME
            else:
                if self._speed[0] <= -self._rel_max_v_speed[0]:
                    self._speed[0] -= self._acceleration * cos / DELTA_TIME

            if self._rel_max_v_speed[1] > 0:
                if self._speed[1] >= -self._rel_max_v_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / DELTA_TIME
            else:
                if self._speed[1] <= -self._rel_max_v_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / DELTA_TIME
        
        if pressedKeys[pygame.K_q]:
            if self._rel_max_h_speed[0] > 0:
                if self._speed[0] <= self._rel_max_h_speed[0]:
                    self._speed[0] += self._max_h_speed * cos90 / DELTA_TIME
            else:
                if self._speed[0] >= self._rel_max_h_speed[0]:
                    self._speed[0] += self._max_h_speed * cos90 / DELTA_TIME

            if self._rel_max_h_speed[1] > 0:
                if self._speed[1] <= self._rel_max_h_speed[1]:
                    self._speed[1] += self._max_h_speed * -sin90 / DELTA_TIME
            else:
                if self._speed[1] >= self._rel_max_h_speed[1]:
                    self._speed[1] += self._max_h_speed * -sin90 / DELTA_TIME
        
        elif pressedKeys[pygame.K_e]:
            if self._rel_max_h_speed[0] > 0:
                if self._speed[0] >= -self._rel_max_h_speed[0]:
                    self._speed[0] -= self._max_h_speed * cos90 / DELTA_TIME
            else:
                if self._speed[0] <= -self._rel_max_h_speed[0]:
                    self._speed[0] -= self._max_h_speed * cos90 / DELTA_TIME

            if self._rel_max_h_speed[1] > 0:
                if self._speed[1] >= -self._rel_max_h_speed[1]:
                    self._speed[1] -= self._max_h_speed * -sin90 / DELTA_TIME
            else:
                if self._speed[1] <= -self._rel_max_h_speed[1]:
                    self._speed[1] -= self._max_h_speed * -sin90 / DELTA_TIME

        if pressedKeys[pygame.K_LEFT]:
            self._angle += self._spin / DELTA_TIME

        if pressedKeys[pygame.K_RIGHT]:
            self._angle -= self._spin / DELTA_TIME
        
        if pressedKeys[pygame.K_w]:
            self._speed = [0, 0]

        if pressedKeys[pygame.K_SPACE] and self._bullet_timer <= 0:
            self._bullet_timer = self._fire_rate
            new_bullet = Bullet((self.rect.x, self.rect.y), self._angle, self._bullet_speed)
            interface.bullets.add(new_bullet)

    def update(self, pressedKeys):
        """Overriden pygame.sprite.sprite method.
        Acceleration is applied according to its vectorial component and in-game events.
        
        Arguments:
            pressedKeys {Tuple} -- collection of events generated by pygame.key"""

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
            bullet_speed {float} -- bullet speed"""

    def __init__(self, start_pos, angle, bullet_speed):
        self._image = pygame.image.load('Images/bullet.png').convert_alpha()
        super().__init__(start_pos)
        self._angle = angle
        self._spin  = 0
        self._bullet_speed = bullet_speed
        self._size  = self._image.get_size( )
        self._speed = [self._bullet_speed * math.cos(math.radians(self._angle)), 
                       self._bullet_speed * -math.sin(math.radians(self._angle))]


class Surface(Game_Object):
    """Simple game surface.
    
        Arguments:
            position {array: float} -- [x, y] start position
            dimension {array: float} -- [x, y] polygon dimension
            color {tuple} -- (R, G, B) color standard"""

    def __init__(self, position, dimension, color, camera_mode = "normal", spin = 0, speed = [0, 0]):
        self._image = pygame.Surface(dimension, pygame.SRCALPHA)
        super().__init__(position, camera_mode = camera_mode)
        self._image.fill(color)
        self._size = self._image.get_size()
        self._spin = spin
        self._speed = speed
    
    def update(self):
        self._angle += self._spin / DELTA_TIME
        Game_Object.update(self)
        self.value = pygame.sprite.groupcollide(interface.bullets, interface.edge, True, False)


class Test_game:

    def __init__(self, map_size):
        global SCREEN_SIZE, CAMERA_X, CAMERA_Y
        self.map_size = map_size

        # Setting up the screen
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        SCREEN_SIZE = self.screen.get_size()

        # Game clock setting
        self.clock = pygame.time.Clock()

        # Groups
        self.ships   = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.edge = pygame.sprite.Group()
        self.rectangles = pygame.sprite.Group()

        # User
        self.user = Ship([100, 200], 'Images/ship.png', 0.7, 10, 10.0, 0.4, 10.0, 10, camera_mode='scrolling', controlled=True)
        CAMERA_X = 100
        CAMERA_Y = 200
        self.ships.add(self.user)

        # Finalize screen
        pygame.display.set_caption("Shooter")

        boundaries = [[[0, 0], [map_size[0], 20]], [[0, map_size[1]], [map_size[0], 20]], # [position], [dimension]
                      [[0, 0], [20, map_size[1]]], [[map_size[0], 0], [20, map_size[1]]]]
        for obj in boundaries:
            item = Surface(obj[0], obj[1], (255, 0, 0))
            self.edge.add(item)

        test = Surface([300, 300], [100,100], (0, 0, 255), spin = 0.5, speed=[1, 1])
        test1 = Surface([300, 300], [100,100], (0, 0, 255), spin = 0.5)
        self.rectangles.add(test)
        self.rectangles.add(test1)
        #self.centre = Surface([0, 0], [4,4], (255, 255, 255), spin = 0, camera_mode="scrolling")

    def main(self):
        global DELTA_TIME
        done = False

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            DELTA_TIME = 30 / self.clock.tick_busy_loop(60) # delta time, game is fp indipendent

            # Refresh screen and update sprites
            self.screen.fill((0, 0, 0))
            self.bullets.update()
            self.ships.update(pygame.key.get_pressed())
            self.edge.update()
            self.rectangles.update()
            #self.centre.update()
            pygame.display.update()
            print(self.clock.get_fps(), len(self.bullets.sprites()), DELTA_TIME)

        pygame.quit()


if __name__ == "__main__":
    interface = Test_game((3000, 3000))
    interface.main()
