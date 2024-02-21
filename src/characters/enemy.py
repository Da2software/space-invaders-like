import math

import pygame
from src.globals import GameVariables
from src.kinematics.kinematics import Animation
from src.utils import *
from src.kinematics import kinematics
import random
import uuid
from typing import final

GLOBALS = GameVariables()


@final
def on_attack(function):
    """ Execute a callback when enemy attacks, this one works as
     trigger event and decorator """

    def _decorator(self, *args, **kwargs):
        self.on_attack = True
        if self.attack_callback:
            self.attack_callback(self)
        function(self, *args, **kwargs)

    return _decorator


class Enemy(pygame.sprite.Sprite, kinematics.Animator):
    def __init__(self, x: int, y: int, size=40):
        pygame.sprite.Sprite.__init__(self)
        kinematics.Animator.__init__(self)
        self.tag = "enemy"
        self.army_id = uuid.uuid4()
        self.type = 1
        self.life = 10
        self.points = 5
        self.damage = 10
        self.move_speed = 2
        self.is_dead = False
        self.die_animation = 0
        self.attack_delay = 0

        # Rendering Variables
        self.image = pygame.image.load(
            GLOBALS.sprite_dir + "EnemyBasic.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.initial_pos = (x, y)
        self.restart_pos = False
        self.idle = True
        self.on_attack = False
        # callbacks
        self.attack_callback = None
        self.attack_end_callback = None
        self.restore_pos_callback = None
        self.on_die_callback = None
        self.on_shoot_callback = None

    def take_damage(self, damage: int) -> None:
        self.life -= damage
        if self.life <= 0:
            self.__on_die()

    def get_pos(self) -> Position2D:
        return Position2D(self.rect.x, self.rect.y)

    @final
    def press_trigger(self):
        """
        if a child class is using a shoot system we can trigger that using this
        call, then the HiveMind class can get notified and let this class,
        creates the shoot
        """
        self.__on_shoot()

    @final
    def __on_shoot(self):
        """ Execute a callback after shooting a bullet ends"""
        if self.on_shoot_callback:
            self.on_shoot_callback(self)

    @final
    def __attack_end(self):
        """ Execute a callback after an attack ends"""
        self.on_attack = False
        if self.attack_end_callback:
            self.attack_end_callback(self)

    @final
    def __on_die(self):
        """ Execute a callback when an enemy dies"""
        self.is_dead = True
        GLOBALS.score += self.points
        if self.on_die_callback:
            self.on_die_callback(self)

    @final
    def __restore_pos_end(self):
        """ Execute a callback after restores position ends"""
        self.restart_pos = False
        self.idle = True
        if self.restore_pos_callback:
            self.restore_pos_callback(self)

    @on_attack
    def attack(self):
        """ method that can be overridden to create an attack functionality,
         it also runs the on_attack event. \n
        if you override this method don't forget to add the
        @enemy_ref.on_attack decorator """
        pass

    def check_limit(self):
        if self.rect.y > GLOBALS.screen.get_height():
            self.rect.y = -self.rect.height
            # reposition for the enemy
            self.stop_animation()
            self.restart_pos = True
            self.__attack_end()
        if self.rect.x > GLOBALS.screen.get_width() + self.rect.width + 20:
            self.rect.x = -self.rect.width
        if self.rect.x < -(self.rect.width + 20):
            self.rect.x = GLOBALS.screen.get_width() + self.rect.width

    def repositioning(self):
        if not self.restart_pos:
            return
        # Calculate the distance to move in each frame
        dx, dy, distance = calculate_distance(self.initial_pos,
                                              (self.rect.x, self.rect.y))

        # if distance is greater than the speed, move to start position
        if distance > 1:
            self.rect.centerx += dx * 0.05
            self.rect.centery += dy * 0.05
        # if we get the start position then we can restore the idle state
        gapx = self.rect.width / 2
        gapy = self.rect.height / 2
        if (self.initial_pos[0] - gapx <= self.rect.x <= self.initial_pos[
            0] + gapx and self.initial_pos[1] - gapy <= self.rect.y <=
                self.initial_pos[1] + gapy):
            # just to make sure we get the exactly same start position
            self.rect.center = (self.initial_pos[0], self.initial_pos[1])
            self.__restore_pos_end()

    def __str__(self):
        return f"({self.tag}, {self.life}, {self.type})"


# BULLETS TYPE
class Bullet(Enemy):
    def __init__(self, x: int, y: int, size=5):
        super().__init__(x, y, size)
        self.speed = 5
        self.tag = "enemy_bullet"
        self.type = 0
        self.damage = 10

        # set rendering
        self.image = pygame.Surface((5, 8))
        self.image.fill("green")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def repositioning(self):
        # avoid inherit process
        return

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
        self.rect.move_ip(0, + self.speed)
        # delete if we get the end of the height screen
        if self.rect.top > GLOBALS.screen.get_height():
            self.is_dead = True


class SniperBullet(Enemy):
    def __init__(self, x: int, y: int, size=5):
        super().__init__(x, y, size)
        self.speed = 5
        self.tag = "enemy_bullet"
        self.damage = 20
        self.type = 0

        # set rendering
        self.image = pygame.Surface((8, 8))
        self.image.fill("green")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.target_on_place = False
        self.direction_angle = None

    def repositioning(self):
        # avoid inherit process
        return

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
        if not self.target_on_place:  # run once
            self.direction_angle = get_direction_angle(self.rect.center,
                                                       player.rect.center)
            self.target_on_place = True
        if self.direction_angle is not None:
            move_to_direction(self.rect, self.direction_angle, self.speed)
        # delete if we get the end of the height screen
        if self.rect.top > GLOBALS.screen.get_height():
            self.is_dead = True


# ENEMIES TYPE
class EnemyBasic(Enemy):

    def __init__(self, x: int, y: int, size=40):
        super().__init__(x, y, size)
        self.type = 1
        self.define_animations("basic")
        self.run_animation("idle", True)
        self.damage = 10

    @on_attack
    def attack(self):
        self.stop_animation()
        attack_anims = ["zigzag", "zigzag",
                        "kamikaze-left", "kamikaze-right"]
        animation_id = attack_anims[random.randint(0, 3)]
        self.run_animation(animation_id, True)
        self.idle = False
        self.on_attack = True

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
            return
        # attack delay
        if self.on_attack and self.attack_delay > 0:
            self.attack_delay -= GLOBALS.ms_fps
            return
        self.render_animation(self.rect)
        # other actions/events
        self.check_limit()
        if not self.on_attack:
            self.repositioning()


class EnemyShooter(Enemy):
    """ This enemy can move down to attack player and shoot a the same time"""

    def __init__(self, x: int, y: int, size=40):
        super().__init__(x, y, size)
        self.define_animations("shooter")
        self.run_animation("idle", True)
        self.type = 2
        self.idle = False
        self.on_shoot = False
        self.attack_direction = "left"
        self.delay_attack = False
        self.shoot_time = 0
        self.shoot_already = True
        self.damage = 20

        # Rendering Variables
        self.image = pygame.image.load(
            GLOBALS.sprite_dir + "Shooter.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    @on_attack
    def attack(self):
        self.stop_animation()
        attack_type = ["left", "right"]
        self.attack_direction = attack_type[random.randint(0, 1)]
        self.run_animation(f"jump-{self.attack_direction}")
        self.idle = False

    def on_animation_ends(self, anim_id: str):
        if anim_id == f"jump-{self.attack_direction}":
            self.delay_attack = True

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
            return
        # prepare attack
        if self.delay_attack and self.shoot_already:  # Run once
            self.delay_attack = False
            self.run_animation(f"attack-{self.attack_direction}", True)
            self.on_attack = True
            self.shoot_already = False
            self.shoot_time = random.randint(200, 1500)

        if self.shoot_time > 0:
            self.shoot_time -= GLOBALS.ms_fps
        elif (self.shoot_time <= 0 and self.on_attack
              and not self.shoot_already):
            # shot a bullet
            self.shoot_already = True
            self.press_trigger()

        if self.on_attack and self.attack_delay > 0:
            self.attack_delay -= GLOBALS.ms_fps
            return
        self.render_animation(self.rect)
        # other actions/events
        self.check_limit()
        if not self.on_attack:
            self.repositioning()


class EnemySniper(Enemy):
    """ This enemy can shoot a bullet that gets close to the player having more
    change to do dame but this enemy can not move """

    def __init__(self, x: int, y: int, size=40):
        super().__init__(x, y, size)
        self.type = 3
        self.define_animations("basic")
        self.run_animation("idle", True)
        self.idle = True
        self.shoot_rate = 0
        self.damage = 25

        # Rendering Variables
        self.image = pygame.image.load(
            GLOBALS.sprite_dir + "Sniper.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def set_shoot_rate(self):
        self.shoot_rate = random.randint(1500, 3000)

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
            return
        self.shoot_rate -= GLOBALS.ms_fps
        if self.shoot_rate <= 0:
            self.press_trigger()
            self.set_shoot_rate()
        self.render_animation(self.rect)
