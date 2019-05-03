import random
import pygame
from PIL import Image
import game_object
import player_object


class Game:
    """Generic Game, initialize important attributes and contains mainloop
    """
    def __init__(self, map_size, screen_size, debug):
        self.map_size = map_size
        self.screen_size = screen_size
        self.debug_font = pygame.font.SysFont("monospace", 15)
        self.debug = debug
        # self.delta_time = 0

        # Setting up the screen
        self.screen = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF)
        #self.screen.set_alpha(None) # disable to use collide mask TODO

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


class TestGame(Game):
    """Test game with some sprites and basic settings"""

    def __init__(self, map_size, screen_size, debug):
        super().__init__(map_size, screen_size, debug)

        # User
        self.user = player_object.Ship(self, pygame.image.load('Images/ship.png').convert_alpha(), 
                                       [self.map_size[0] / 2, self.map_size[1] / 2 + 100],
                                       0.7, 0.4, 10, 10.0, 10.0, 7, need_max_rect=False,
                                       camera_mode='scrolling', controlled=True)
        self.camera_x = 100
        self.camera_y = 200
        self.ships.add(self.user)
        self.allies.add(self.user)
        self.all.add(self.user)

        # Finalize screen caption
        pygame.display.set_caption("Shooter")

        # edge objects [[position], [dimension]]
        boundaries = [[[0, 0], [map_size[0], 20]],
                      [[0, map_size[1]], [map_size[0], 20]],
                      [[0, 0], [20, map_size[1]]],
                      [[map_size[0], 0], [20, map_size[1] + 20]]]
        for obj in boundaries:
            item = game_object.Edge(self, obj[0], obj[1], (255, 0, 0))
            self.edge.add(item)
            self.environment.add(item)
            self.targets.add(item)
            self.allies.add(item)
            self.all.add(item)

        # test objects
        for x in range(20):
            test = game_object.Surface(self, pygame.image.load("Images/asteroid.png").convert_alpha(),
                                       [random.randint(1, map_size[0]),
                                        random.randint(1, map_size[1])],
                                       False, 8, spin=random.uniform(-2, 2),
                                       speed=[random.uniform(-3, 3), random.uniform(-3, 3)], life=5)
            self.environment.add(test)
            self.targets.add(test)
            self.all.add(test)

        # Starry sky, randomly generated
        img = Image.new('RGB', map_size)
        pixel_map = img.load()
        for x in range(1000):
            pixel_map[random.randint(0, self.map_size[0] - 1),
                      random.randint(0, self.map_size[1] - 1)] = (255, 255, 255, 0)
        stars = game_object.Background(self, pygame.image.frombuffer(img.tobytes("raw", "RGB"), map_size, "RGB").convert())
        self.starry_sky.add(stars)
        self.all.add(stars)
        img.close()
        
        # base
        self.base = game_object.Surface(self, pygame.image.load("Images/base.png").convert_alpha(),
                                        [self.map_size[0] / 2, self.map_size[1] / 2],
                                        False, 0, spin=0.5, life=200)
        self.environment.add(self.base)
        self.allies.add(self.base)

    def mainloop(self):
        """Main game loop
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

                test = game_object.Surface(self, pygame.image.load("Images/asteroid.png").convert_alpha(),
                                           position,
                                           False, 8, spin=random.uniform(-2, 2),
                                           speed=[random.uniform(-3, 3), random.uniform(-3, 3)], life=5)
                self.environment.add(test)
                self.targets.add(test)
                self.all.add(test)

            # keys events
            keys = pygame.key.get_pressed()

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
                GAME.screen.blit(display_label, (0, 0))
                pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()

    GAME = TestGame((2500, 2500), (1300, 800), False) # mapsize, screensize, debug_enable
    GAME.mainloop()
