import pygame
from src.globals import GameVariables
from src.utils import Position2D
from src.kinematics import kinematics
import random

GLOBALS = GameVariables()


class Enemy(pygame.sprite.Sprite, kinematics.Animator):
    def __init__(self, x: int, y: int, size=40):
        pygame.sprite.Sprite.__init__(self)
        kinematics.Animator.__init__(self)
        self.tag = "enemy"
        self.type = 1
        self.life = 10
        self.points = 5
        self.move_speed = 2
        self.is_dead = False
        self.die_animation = 0

        # Rendering Variables
        self.image = pygame.Surface((size, size))
        self.image.fill("red")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.initial_pos = (x, y)
        self.restart_pos = False

    def take_damage(self, damage: int) -> None:
        self.life -= damage
        if self.life <= 0:
            self.is_dead = True
            GLOBALS.score += self.points

    def get_pos(self) -> Position2D:
        return Position2D(self.rect.x, self.rect.y)

    def __str__(self):
        return f"({self.tag}, {self.life}, {self.type})"


class EnemyBasic(Enemy):

    def __init__(self, x: int, y: int, size=40):
        super().__init__(x, y, size)
        self.idle = True
        self.action_time = random.randint(2000, 8000)
        self.action_timer = 0
        self.run_animation("idle", True)

    def update(self, player) -> None:
        if self.idle:
            self.run_animation("idle", True)
        # after around 2 or  seconds we start running the random actions
        if (self.action_timer > self.action_time and
                random.randint(0, 200) == 0 and self.idle):
            self.stop_animation()
            self.idle = False
            attack_anims = ["zigzag", "zigzag",
                            "kamikaze-left", "kamikaze-right"]
            animation_id = attack_anims[random.randint(0, 3)]
            self.run_animation(animation_id, True)
        # check if enemy is dead
        if self.is_dead:
            self.kill()
            return
        self.render_animation(self.rect)
        # other actions/events
        self.check_limit()
        self.repositioning()
        self.action_timer += GLOBALS.ms_fps if (
                self.action_timer < self.action_time) else 0

    def reset_action_timers(self):
        self.action_time = random.randint(2000, 8000)
        self.action_timer = 0

    def repositioning(self):
        if not self.restart_pos:
            return
        # Calculate the distance to move in each frame
        dx = self.initial_pos[0] - self.rect.x
        dy = self.initial_pos[1] - self.rect.y
        distance = pygame.math.Vector2(dx, dy).length()

        # If the distance is greater than the speed, move the sprite
        if distance > 1:
            self.rect.centerx += dx * 0.1
            self.rect.centery += dy * 0.1
        if (self.initial_pos[0] - 10 <= self.rect.x <= self.initial_pos[0] + 10
                and self.initial_pos[1] - 10 <= self.rect.y <=
                self.initial_pos[1] + 10):
            self.rect.center = (self.initial_pos[0], self.initial_pos[1])
            self.restart_pos = False
            self.idle = True
            self.reset_action_timers()

    def check_limit(self):
        if self.rect.y > GLOBALS.screen.get_height():
            self.rect.y = -self.rect.height
            # reposition for the enemy
            self.stop_animation()
            self.restart_pos = True
        if self.rect.x > GLOBALS.screen.get_width() + self.rect.width + 20:
            self.rect.x = -self.rect.width
        if self.rect.x < -(self.rect.width + 20):
            self.rect.x = GLOBALS.screen.get_width() + self.rect.width
