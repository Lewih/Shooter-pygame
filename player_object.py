import math
import random
import pygame
import game_object


class Ship(game_object.Game_Object):
    """Ship game object. It is verbose in debug mode.

    Arguments:
        game {object} -- game instance
        image {str} -- pygame surface object
        start_pos {float: array} -- [x, y] spawn point
        acceleration {float} -- Ship acceleration
        h_acceleration {float} -- horizontal acceleration
        spin {float} -- Ship spin
        max_speed {float} -- nominal max vertical speed
        bullet_speed {float} -- Ship bullet speed
        fire_rate {float} -- fire sleep in game tick / self._game.delta_time
        camera_mode {string} -- normal = not player object
                               scrolling = locked camera on player ship
        controlled {bool}  -- ship is controlled by user
        need_max_rect {bool} -- rect size is the first diagonal"""
    
    def __init__(self, game, image, start_pos, acceleration,
                 h_acceleration, spin, max_speed, bullet_speed,
                 fire_rate, camera_mode='normal', controlled=False,
                 need_max_rect=True):
        super().__init__(game, start_pos, image, True,
                         need_max_rect=need_max_rect,
                         camera_mode=camera_mode)
        self._life = 100.0
        self._acceleration = acceleration
        self._original_spin = spin
        self._spin = spin
        self._max_speed = max_speed
        self._h_acceleration = h_acceleration
        self._bullet_speed = bullet_speed
        self._fire_rate = fire_rate
        self._bullet_timer = 0
        self._bullet_image = pygame.image.load("Images/bullet.png").convert_alpha()
        self._missile_image = pygame.image.load("Images/missile.png").convert_alpha()
        self._controlled = controlled

    def __str__(self):
        return("""Ship = {
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
                               self._image, self._camera_mode, self._controlled))

    def controls(self, pressedKeys):
        """keyboard handling"""

        cos = math.cos(math.radians(self._angle))
        sin = math.sin(math.radians(self._angle))
        cos90 = math.cos(math.radians(self._angle + 90))
        sin90 = math.sin(math.radians(self._angle + 90))

        rel_max_speed = [self._max_speed * cos, 
                              self._max_speed * -sin]

        rel_max_h_speed = [self._max_speed * cos90, 
                                self._max_speed * -sin90]

        if pressedKeys[pygame.K_UP]:
            shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                      self._angle, image=self._game.white_shine)
            self._game.environment.add(shine)
            self._game.all.add(shine)

            if rel_max_speed[0] > 0:
                if self._speed[0] <= rel_max_speed[0]:
                    self._speed[0] += self._acceleration * cos / self._game.delta_time
            else:
                if self._speed[0] >= rel_max_speed[0]:
                    self._speed[0] += self._acceleration * cos / self._game.delta_time

            if rel_max_speed[1] > 0:
                if self._speed[1] <= rel_max_speed[1]:
                    self._speed[1] += self._acceleration * -sin / self._game.delta_time
            else:
                if self._speed[1] >= rel_max_speed[1]:
                    self._speed[1] += self._acceleration * -sin / self._game.delta_time

        elif pressedKeys[pygame.K_DOWN]:
            shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                      self._angle + 180, image=self._game.white_shine)
            self._game.environment.add(shine)
            self._game.all.add(shine)

            if rel_max_speed[0] > 0:
                if self._speed[0] >= -rel_max_speed[0]:
                    self._speed[0] -= self._acceleration * cos / self._game.delta_time
            else:
                if self._speed[0] <= -rel_max_speed[0]:
                    self._speed[0] -= self._acceleration * cos / self._game.delta_time

            if rel_max_speed[1] > 0:
                if self._speed[1] >= -rel_max_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / self._game.delta_time
            else:
                if self._speed[1] <= -rel_max_speed[1]:
                    self._speed[1] -= self._acceleration * -sin / self._game.delta_time

        if pressedKeys[pygame.K_q]:
            if rel_max_h_speed[0] > 0:
                if self._speed[0] <= rel_max_h_speed[0]:
                    self._speed[0] += self._h_acceleration * cos90 / self._game.delta_time
            else:
                if self._speed[0] >= rel_max_h_speed[0]:
                    self._speed[0] += self._h_acceleration * cos90 / self._game.delta_time

            if rel_max_h_speed[1] > 0:
                if self._speed[1] <= rel_max_h_speed[1]:
                    self._speed[1] += self._h_acceleration * -sin90 / self._game.delta_time
            else:
                if self._speed[1] >= rel_max_h_speed[1]:
                    self._speed[1] += self._h_acceleration * -sin90 / self._game.delta_time

        elif pressedKeys[pygame.K_e]:
            if rel_max_h_speed[0] > 0:
                if self._speed[0] >= -rel_max_h_speed[0]:
                    self._speed[0] -= self._h_acceleration * cos90 / self._game.delta_time
            else:
                if self._speed[0] <= -rel_max_h_speed[0]:
                    self._speed[0] -= self._h_acceleration * cos90 / self._game.delta_time

            if rel_max_h_speed[1] > 0:
                if self._speed[1] >= -rel_max_h_speed[1]:
                    self._speed[1] -= self._h_acceleration * -sin90 / self._game.delta_time
            else:
                if self._speed[1] <= -rel_max_h_speed[1]:
                    self._speed[1] -= self._h_acceleration * -sin90 / self._game.delta_time

        if pressedKeys[pygame.K_w]:
            self._spin = self._original_spin / 2
        
        elif not pressedKeys[pygame.K_w]:
            self._spin = self._original_spin

        if pressedKeys[pygame.K_LEFT]:
            self.spin(self._spin / self._game.delta_time)

        if pressedKeys[pygame.K_RIGHT]:
            self.spin(-self._spin / self._game.delta_time)

        if pressedKeys[pygame.K_s]:
            self._speed = [0, 0]

        if pressedKeys[pygame.K_SPACE] and self._bullet_timer <= 0:
            self._bullet_timer = self._fire_rate
            new_bullet = Bullet(self._game, self._bullet_image,
                                self._position, self._angle, self._bullet_speed,
                                self)
            self._game.bullets.add(new_bullet)
            self._game.all.add(new_bullet)
        
        if pressedKeys[pygame.K_LSHIFT] and self._bullet_timer <= 0:
            self._bullet_timer = self._fire_rate
            new_missile = Missile(self._game, self._missile_image,
                                  self._position, self._angle, self)
            self._game.bullets.add(new_missile)
            self._game.all.add(new_missile)

    def update(self, pressedKeys):
        """Overriden pygame.sprite.sprite method.
        Acceleration is applied according to its vectorial component and in-game events.
        
        Arguments:
            pressedKeys {Tuple} -- collection of events generated by pygame.key"""

        if self._bullet_timer > 0:
            self._bullet_timer -= 1 / self._game.delta_time

        if self._controlled:
            self.controls(pressedKeys)

        game_object.Game_Object.update(self)


class Bullet(game_object.Game_Object):
    """Bullet game object shot by sprites according to their angle.
       It is verbose in debug mode.
        
        Arguments:
            game {object} -- game instance
            image {string} -- default is standard bullet
            start_pos {array: float} -- [x, y] start position
            angle {float} -- angle of the vector in degrees
            bullet_speed {float} -- bullet speed
            owner {object} -- object whose event generated the sprite
            """

    def __init__(self, game, image, start_pos,
                 angle, bullet_speed, owner, damage=1):
        super().__init__(game, start_pos, image, True, need_max_rect=True)
        self._angle = angle
        self._spin = 0
        self._bullet_speed = bullet_speed
        self._speed = [self._bullet_speed * math.cos(math.radians(self._angle)), 
                       self._bullet_speed * -math.sin(math.radians(self._angle))]
        self._damage = damage
        self._owner = owner

    def explode(self):
        self.kill()
        for x in range(20):
            shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                      self._angle, spin=random.uniform(-2, 2),
                                      image=self._game.standard_shine)
            self._game.environment.add(shine)
            self._game.all.add(shine)

    def update(self):
        for caught in pygame.sprite.spritecollide(self, self._game.targets, False):
            if caught is not self._owner:
                self.explode()
                caught.hit(self._damage)
        game_object.Game_Object.update(self)


class Missile(game_object.Game_Object):
    """Seeking missile game object. Seeks the closest target.
       It is verbose in debug mode.
        
        Arguments:
            game {object} -- game instance
            image {string} -- default is standard bullet
            start_pos {array: float} -- [x, y] start position
            angle {float} -- initial angle of the vector in degrees
            owner {object} -- object whose event generated the sprite
            spin {float} -- missile spin
            speed {float} -- nominal speed
            radius {int} -- targets in radius are hit. Radius in pixel.
            damage {int} -- damage inflicted to targets
            """

    def __init__(self, game, image, start_pos,
                 angle, owner, spin=1.0, speed=15.0,
                 radius=100.0, damage=10):
        super().__init__(game, start_pos, image, True, True)
        self._owner = owner
        self._angle = angle
        self._missile_speed = speed
        self._speed = [speed * math.cos(math.radians(self._angle)), 
                       speed * -math.sin(math.radians(self._angle))]
        self._spin = spin
        self._exp_radius = radius
        self._damage = damage
        self._target = self.find_target()

    def explode(self):
        """Custom missile explosion"""

        self.kill()
        counter = 0
        for x in range(59):
            shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                      counter, speed=[-math.cos(math.radians(counter)) * 4,
                                                      math.sin(math.radians(counter)) * 4],
                                      image=self._game.standard_shine)
            self._game.environment.add(shine)
            self._game.all.add(shine)
            counter += 6

    def find_target(self):
        """Find the closest target"""

        target = None
        for obj in self._game.targets.sprites():
            if not target:
                target = obj
            elif self.distance_from(obj._position) < self.distance_from(target._position):
                target = obj
        return target

    def seek(self):
        """Seek the chosen target if alive"""

        if self._target and self._target.alive():
            new_angle = math.degrees(math.atan2(self._position[1] - self._target._position[1],
                                     -self._position[0] + self._target._position[0]))
            angle = self._angle % 360
            if angle <= -180 :
                angle += 360
            elif angle > 180:
                angle -= 360
            
            if - new_angle + angle <= 180 and - new_angle + angle >= 0:
                self.spin(-self._spin)
            else:
                self.spin(self._spin) 

            self._speed = [self._missile_speed * math.cos(math.radians(self._angle)), 
                           self._missile_speed * -math.sin(math.radians(self._angle))]

    def update(self):
        shine = game_object.Shine(self._game, [self.rect.centerx, self.rect.centery],
                                  self._angle, image=self._game.lightred_shine)
        self._game.environment.add(shine)
        self._game.all.add(shine)
        self.seek()
        if pygame.sprite.spritecollide(self, self._game.targets, False):
            self.explode()
            for obj in self._game.targets.sprites():
                if self.distance_from(obj._position) <= self._exp_radius:
                    obj.hit(self._damage)
        super().update()

