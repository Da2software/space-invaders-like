import pygame
from src.globals import GameVariables
from src.utils import Position2D
from src.kinematics import kinematics
import random
import uuid
from typing import final

GLOBALS = GameVariables()


@final
def on_attack(function):
    """ Execute a callback when enemy attacks, this one works as
     trigger event and decorator"""

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
        self.move_speed = 2
        self.is_dead = False
        self.die_animation = 0
        self.attack_delay = 0

        # Rendering Variables
        self.image = pygame.Surface((size, size))
        self.image.fill("red")
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

    def take_damage(self, damage: int) -> None:
        self.life -= damage
        if self.life <= 0:
            self.__on_die()

    def get_pos(self) -> Position2D:
        return Position2D(self.rect.x, self.rect.y)

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
        dx = self.initial_pos[0] - self.rect.x
        dy = self.initial_pos[1] - self.rect.y
        distance = pygame.math.Vector2(dx, dy).length()

        # if distance is greater than the speed, move to start position
        if distance > 1:
            self.rect.centerx += dx * 0.1
            self.rect.centery += dy * 0.1
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


class EnemyBasic(Enemy):

    def __init__(self, x: int, y: int, size=40):
        super().__init__(x, y, size)
        self.define_animations("basic")
        self.run_animation("idle", True)

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
