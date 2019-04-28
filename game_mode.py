import random
import pygame
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
        self.screen = pygame.display.set_mode(self.screen_size)

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

    def mainloop(self):
        """Main game loop
        """
        done = False

        # check for exit
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            # delta time, game is frame rate indipendent
            self.delta_time = 30 / self.clock.tick_busy_loop(60)

            # Refresh screen and update sprites
            self.screen.fill((0, 0, 0))
            self.starry_sky.update()
            self.bullets.update()
            self.ships.update(pygame.key.get_pressed())
            self.environment.update()
            display_label = self.debug_font.render(" Sprites in game:" +
                                                   str(self.all.sprites) +
                                                   ", fps: " + str(self.clock.get_fps()),
                                                   1, (255, 255, 0))
            GAME.screen.blit(display_label, (0, 0))
            pygame.display.update()

        pygame.quit()


class TestGame(Game):
    """Test game with some sprites and basic settings"""

    def __init__(self, map_size, screen_size, debug):
        super().__init__(map_size, screen_size, debug)

        # User
        self.user = player_object.Ship(self, [100, 200], 'Images/ship.png',
                                       0.7, 0.4, 10, 10.0, 10.0, 7,
                                       camera_mode='scrolling', controlled=True)
        self.camera_x = 100
        self.camera_y = 200
        self.ships.add(self.user)

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
            self.all.add(item)

        # test objects
        for x in range(100):
            test = game_object.Surface(self, [random.randint(1, map_size[0]),
                                              random.randint(1, map_size[1])],
                                       [60, 60], (0, 0, 255), True, spin=1,
                                       speed=[0, 0], life=5)
            self.rectangles.add(test)
            self.environment.add(test)
            self.targets.add(test)
            self.all.add(test)

        # Starry sky
        if not self.debug:
            for x in range(1000):
                star = game_object.Stars(self,
                                         (random.randint(0, self.map_size[0]),
                                          random.randint(0, self.map_size[1])))
                self.starry_sky.add(star)
                self.all.add(star)


if __name__ == "__main__":
    # Initialize pygame
    pygame.init()

    GAME = TestGame((1500, 1500), (1300, 800), False)
    GAME.mainloop()
