import math
import random
import pygame
import game_object


class Ship(game_object.Game_Object):
    """Ship game object.

    Arguments:
        start_pos {float: array} -- [x, y]
        image {str} -- Ship Image directory
        acceleration {float} -- Ship acceleration
        h_acceleration {float} -- horizontal acceleration
        spin {float} -- Ship spin
        max_speed {float} -- nominal max vertical speed
        bullet_speed {float} -- Ship bullet speed
        fire_rate {float} -- fire sleep in game tick / self._game.deltaTime
        camera_mode{string} -- normal = not player object
                               scrolling = locked camera on player ship
        controlled{bool}  -- ship is controlled by user"""
    
    def __init__(self, game, start_pos, image, acceleration,
                 h_acceleration, spin, max_speed, bullet_speed,
                 fire_rate, camera_mode='normal', controlled=False):
        super().__init__(game, start_pos, pygame.image.load(image).convert_alpha(),
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
            shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                      self._angle, dimension=[2, 2], color=(255, 255, 255))
            self._game.environment.add(shine)
            self._game.all.add(shine)

            if self.rel_max_speed[0] > 0:
                if self._speed[0] <= self.rel_max_speed[0]:
                    self._speed[0] += self._acceleration * cos / self._game.deltaTime
            else:
                if self._speed[0] >= self.rel_max_speed[0]:
                    self._speed[0] += self._acceleration * cos / self._game.deltaTime

            if self.rel_max_speed[1] > 0:
                if self._speed[1] <= self.rel_max_speed[1]:
                    self._speed[1] += self._acceleration * -sin / self._game.deltaTime
            else:
                if self._speed[1] >= self.rel_max_speed[1]:
                    self._speed[1] += self._acceleration * -sin / self._game.deltaTime

        elif pressedKeys[pygame.K_DOWN]:
            if self.rel_max_speed[0] > 0:
                if self._speed[0] >= -self.rel_max_speed[0]:
                    self._speed[0] -= self._acceleration * cos / self._game.deltaTime
            else:
                if self._speed[0] <= -self.rel_max_speed[0]:
                    self._speed[0] -= self._acceleration * cos / self._game.deltaTime

            if self.rel_max_speed[1] > 0:
                if self._speed[1] >= -self.rel_max_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / self._game.deltaTime
            else:
                if self._speed[1] <= -self.rel_max_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / self._game.deltaTime

        if pressedKeys[pygame.K_q]:
            if self.rel_max_h_speed[0] > 0:
                if self._speed[0] <= self.rel_max_h_speed[0]:
                    self._speed[0] += self._h_acceleration * cos90 / self._game.deltaTime
            else:
                if self._speed[0] >= self.rel_max_h_speed[0]:
                    self._speed[0] += self._h_acceleration * cos90 / self._game.deltaTime

            if self.rel_max_h_speed[1] > 0:
                if self._speed[1] <= self.rel_max_h_speed[1]:
                    self._speed[1] += self._h_acceleration * -sin90 / self._game.deltaTime
            else:
                if self._speed[1] >= self.rel_max_h_speed[1]:
                    self._speed[1] += self._h_acceleration * -sin90 / self._game.deltaTime

        elif pressedKeys[pygame.K_e]:
            if self.rel_max_h_speed[0] > 0:
                if self._speed[0] >= -self.rel_max_h_speed[0]:
                    self._speed[0] -= self._h_acceleration * cos90 / self._game.deltaTime
            else:
                if self._speed[0] <= -self.rel_max_h_speed[0]:
                    self._speed[0] -= self._h_acceleration * cos90 / self._game.deltaTime

            if self.rel_max_h_speed[1] > 0:
                if self._speed[1] >= -self.rel_max_h_speed[1]:
                    self._speed[1] -= self._h_acceleration * -sin90 / self._game.deltaTime
            else:
                if self._speed[1] <= -self.rel_max_h_speed[1]:
                    self._speed[1] -= self._h_acceleration * -sin90 / self._game.deltaTime

        if pressedKeys[pygame.K_LEFT]:
            self.spin(self._spin / self._game.deltaTime)

        if pressedKeys[pygame.K_RIGHT]:
            self.spin(-self._spin / self._game.deltaTime)

        if pressedKeys[pygame.K_w]:
            self._speed = [0, 0]

        if pressedKeys[pygame.K_SPACE] and self._bullet_timer <= 0:
            self._bullet_timer = self._fire_rate
            new_bullet = Bullet(self._game, self._position, self._angle, self._bullet_speed)
            self._game.bullets.add(new_bullet)

    def update(self, pressedKeys):
        """Overriden pygame.sprite.sprite method.
        Acceleration is applied according to its vectorial component and in-game events.
        
        Arguments:
            pressedKeys {Tuple} -- collection of events generated by pygame.key"""

        for caught in pygame.sprite.spritecollide(self, self._game.edge, False):
            self.kill()
            for x in range(20):
                shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery], self._angle)
                self._game.environment.add(shine)
                self._game.all.add(shine)

        if self._bullet_timer > 0:
            self._bullet_timer -= 1 / self._game.deltaTime

        if self._controlled:
            self.controls(pressedKeys)

        game_object.Game_Object.update(self)


class Bullet(game_object.Game_Object):
    """Bullet game object shot by sprites according to their angle.
        
        Arguments:
            start_pos {array: float} -- [x, y] start position
            angle {float} -- angle of the vector in degrees
            bullet_speed {float} -- bullet speed
            image {string} -- default is standard bullet"""

    def __init__(self, game, start_pos, angle, bullet_speed,
                 image='Images/bullet.png'):
        super().__init__(game, start_pos, pygame.image.load(image).convert_alpha())
        self._angle = angle
        self._spin = 0
        self._bullet_speed = bullet_speed
        self._speed = [self._bullet_speed * math.cos(math.radians(self._angle)), 
                       self._bullet_speed * -math.sin(math.radians(self._angle))]
        self._damage = 1

    def update(self):
        for caught in pygame.sprite.spritecollide(self, self._game.targets, False):
            self.kill()
            for x in range(20):
                shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                          self._angle, spin=random.uniform(-2, 2))
                self._game.environment.add(shine)
                self._game.all.add(shine)
            caught.hit(self._damage)
        game_object.Game_Object.update(self)
