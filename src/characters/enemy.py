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
        self.animation_time = 0  # 1 second delay
        self.move_dir: Position2D = Position2D()
        self.x_dir = 0
        self.player_pos: Position2D = None
        self.idle = True
        self.action_time = random.randint(2000, 8000)
        self.action_timer = 0
        self.initial_pos = {"x": x, "y": y}
        self.run_animation("idle", True)

    def update(self, player) -> None:
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
        self.action_timer += GLOBALS.ms_fps if (
                self.action_timer < self.action_time) else 0
