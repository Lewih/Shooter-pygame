import random
import sys
import pygame
from PIL import Image
from threading import Condition, Thread
import game_object
import player_object
import multiplayer


class SharedHashTable:
    
    def __init__(self):
        self._condition = Condition()
        self._writable = True
        self._hashmap = {} # hashmap containing all relevant game objects {id: object}
    
    def setter(self, key, data):
        self._condition.acquire()
        self._hashmap[key] = data
        self._condition.notify()
        self._condition.release()
    
    def getter(self, key):
        self._condition.acquire()
        value = self._hashmap.get(key)
        self._condition.notify()
        self._condition.release()
        return value
    
    def remove(self, key):
        self._condition.acquire()
        self._hashmap.pop(key)
        self._condition.notify()
        self._condition.release()


class Game(Thread):
    """Generic Game, initialize important attributes and contains mainloop
    """
    def __init__(self, map_size, screen_size, debug):
        super().__init__()
        # Initialize pygame
        pygame.init()

        self.map_size = map_size
        self.screen_size = screen_size
        self.debug_font = pygame.font.SysFont("monospace", 15)
        self.debug = debug
        self.hashmap = SharedHashTable()

        # Setting up the screen
        self.screen = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF)

        # Game clock setting
        self.clock = pygame.time.Clock()

        # Groups
        self.ships = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.edge = pygame.sprite.Group()
        self.allies = pygame.sprite.Group()
        self.environment = pygame.sprite.Group()
        self.starry_sky = pygame.sprite.Group()
        self.targets = pygame.sprite.Group()
        self.all = pygame.sprite.Group()

        # default shines, theoretic performance boost
        self.standard_shine = pygame.Surface([5, 2], pygame.SRCALPHA).convert_alpha()
        self.standard_shine.fill((155, 155, 0))
        self.white_shine = pygame.Surface([2, 2], pygame.SRCALPHA).convert_alpha()
        self.white_shine.fill((255, 255, 255))
        self.lightred_shine = pygame.Surface([2, 2], pygame.SRCALPHA).convert_alpha()
        self.lightred_shine.fill((255, 150, 150))



class TestGame(Game):
    """Test game with some sprites and basic settings"""

    def __init__(self, map_size, screen_size, debug):
        super().__init__(map_size, screen_size, debug)

        self.asteroids = pygame.sprite.Group()

        # Finalize screen caption
        pygame.display.set_caption("Shooter")

        # User
        self.user = player_object.Ship(self, pygame.image.load('Images/ship.png').convert_alpha(), 
                                       [self.map_size[0] / 2, self.map_size[1] / 2 + 100],
                                       0.7, 0.4, 10, 10.0, 12.0, 8, need_max_rect=False,
                                       camera_mode='scrolling', controlled=True)
        self.camera_x = 100
        self.camera_y = 200
        self.ships.add(self.user)
        # self.targets.add(self.user)
        self.allies.add(self.user)
        self.all.add(self.user)

        # Edge objects [[position], [dimension]]
        boundaries = [[[0, 0], [map_size[0], 20]],
                      [[0, map_size[1]], [map_size[0], 20]],
                      [[0, 0], [20, map_size[1]]],
                      [[map_size[0], 0], [20, map_size[1] + 20]]]
        for obj in boundaries:
            item = game_object.Edge(self, obj[0], obj[1], (255, 0, 0))
            self.edge.add(item)
            self.environment.add(item)
            self.all.add(item)

        # Starry sky, randomly generated
        img = Image.new('RGB', map_size)
        pixel_map = img.load()
        for x in range(1000):
            pixel_map[random.randint(0, self.map_size[0] - 1),
                      random.randint(0, self.map_size[1] - 1)] = (255, 255, 255, 0)
        stars = game_object.Background(self, pygame.image.frombuffer(img.tobytes("raw", "RGB"), map_size, "RGB").convert())
        self.starry_sky.add(stars)
        img.close()
        
        # Base
        self.base = game_object.Surface(self, pygame.image.load("Images/base.png").convert_alpha(),
                                        [self.map_size[0] / 2, self.map_size[1] / 2],
                                        False, 0, spin=0.5, life=200)
        self.environment.add(self.base)
        self.allies.add(self.base)

         # Asteroids
        self.asteroid_image1 = pygame.image.load("Images/asteroid.png").convert_alpha()
        for x in range(20):
            position = [random.randint(1, self.map_size[0]),
                        random.randint(1, self.map_size[1])]
            while self.base.distance_from(position) < 700:
                position = [random.randint(1, self.map_size[0]),
                            random.randint(1, self.map_size[1])]
            test = game_object.Surface(self, self.asteroid_image1,
                                       position, False, 8,
                                       spin=random.uniform(-2, 2),
                                       speed=[random.uniform(-4, 4), random.uniform(-4, 4)], life=5)
            self.environment.add(test)
            self.asteroids.add(test)
            self.targets.add(test)
            self.all.add(test)

    def run(self):
        """game mainloop
        """
        done = False
        counter = 0

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # delta time, game is frame rate indipendent
            self.delta_time = 30 / self.clock.tick_busy_loop(60)

            # asteroids spawn
            counter += 1 / self.delta_time
            if counter / 60 > 1: # TODO optimize position
                counter = 0
                position = [random.randint(1, self.map_size[0]),
                            random.randint(1, self.map_size[1])]
                while self.user.distance_from(position) < 450 or self.base.distance_from(position) < 800:
                    position = [random.randint(1, self.map_size[0]),
                                random.randint(1, self.map_size[1])]

                test = game_object.Surface(self, self.asteroid_image1,
                                           position,
                                           False, 8, spin=random.uniform(-2, 2),
                                           speed=[random.uniform(-3, 3), random.uniform(-3, 3)], life=5)
                self.environment.add(test)
                self.asteroids.add(test)
                self.targets.add(test)
                self.all.add(test)

            # keys events
            keys = pygame.key.get_pressed()

            # asteroids collision
            for ally, asteroids in pygame.sprite.groupcollide(self.allies, self.asteroids, False, False).items():
                for obj in asteroids:
                    ally.hit(obj._damage)
                    obj.explode(color=(255, 0, 0))

            # pause the game
            if not keys[pygame.K_a]:
                # Refresh screen and update sprites
                self.screen.fill((0, 0, 0))
                self.starry_sky.update()
                self.bullets.update()
                self.ships.update(keys)
                self.environment.update()
                display_label = self.debug_font.render(" Sprites in game:" +
                                                        str(len(self.all.sprites())) +
                                                        ", fps: " + str(self.clock.get_fps()),
                                                        1, (255, 255, 0))
                self.screen.blit(display_label, (0, 0))
                pygame.display.update()

        pygame.quit()


class Multi1v1(Game):
    
    def __init__(self, map_size, screensize, role, debug_enable, ip='localhost'):
        super().__init__()
        if role == 'server':
            self._role = True
            self.connection = multiplayer.Server(self)
        else:
            self._role = False
            self.connection = multiplayer.Client(self)
        
    def update_server(self):
        pass

    def update_client(self):
        pass

    def run(self):
        done = False
        counter = 0

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # Update hashmap
            if self._role:
                self.update_server()
            else:
                self.update_client()

            # Refresh screen and update sprites
            self.screen.fill((0, 0, 0))
            self.starry_sky.update()
            self.bullets.update()
            self.ships.update(keys)
            self.environment.update()
            display_label = self.debug_font.render(" Sprites in game:" +
                                                    str(len(self.all.sprites())) +
                                                    ", fps: " + str(self.clock.get_fps()),
                                                    1, (255, 255, 0))
            self.screen.blit(display_label, (0, 0))
            pygame.display.update()
