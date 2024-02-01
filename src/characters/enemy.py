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

    def define_animations(self):
        idle = kinematics.Animation(
            animation_id="idle", duration=1000, frames=5)
        idle.set_key_frame('0', kinematics.KeyFrame(
            kinematics.AnimationTransform(),  kinematics.Curve.smooth))
        idle.set_key_frame('1', kinematics.KeyFrame(
            kinematics.AnimationTransform(x=2, y=2),  kinematics.Curve.smooth))
        idle.set_key_frame('2', kinematics.KeyFrame(
            kinematics.AnimationTransform(x=2, y=2), kinematics.Curve.smooth))
        idle.set_key_frame('3', kinematics.KeyFrame(
            kinematics.AnimationTransform(x=-4, y=-4), kinematics.Curve.smooth))
        self.animations.append(idle)
        self.run_animation("idle")

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
            return
        self.render_animation(self.rect)
        return
        # set player position
        self.player_pos = player.get_pos()

        # start moving towards the player after 1 second
        if self.animation_time > 1:
            # moving direction according player position (x-axis)
            self.move_dir.y = self.move_speed
            # random change move direction each 2 seconds
            if random.randrange(0, 80) == 0:
                self.x_dir = -self.x_dir
            # 3 seconds after enemy spawn we can do the animation
            if self.animation_time < 3:
                self.move_dir.x = self.move_speed * self.x_dir
            self.rect.move_ip(self.move_dir.x, self.move_dir.y + 2)
        # Then, if the enemy reaches the end of the window screen, it will be
        # respawned.
        if self.rect.top > GLOBALS.screen.get_height():
            # reset timer to 1 second
            self.animation_time = 1
            # reset y position to top
            self.rect.y = -self.rect.height
            # reset x according to last position
            if self.rect.x < 0:
                self.rect.x = 0
            elif self.rect.x > GLOBALS.screen.get_width():
                self.rect.x = GLOBALS.screen.get_width()
            self.x_dir = 1 if self.player_pos.x > self.rect.left else -1

        # update animation time
        self.animation_time += GLOBALS.delta_time


# todo: remove this later and move it to the level maker/controller
class EnemiesController:
    def __init__(self):
        self.timers = {}
        self.enemiesGroup = pygame.sprite.Group()
        self.spawn = False

    @staticmethod
    def get_player_from_group(player_group: pygame.sprite.Group):
        player = None
        for items in player_group.spritedict:
            if items.tag == "player":
                player = items
                break
        return player

    @staticmethod
    def check_hit(player_group: pygame.sprite.Group,
                  enemies_group: pygame.sprite.Group):
        for enemy in enemies_group.spritedict:
            for bullet in player_group.spritedict:
                if bullet.tag == "bullet":
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.take_damage(bullet.damage)
                        bullet.hit()

    def render(self, player_group: pygame.sprite.Group):
        """
        :param player_group: playerGroup to be as a target, also to be
         used as a collider
        :return:
        """
        if not self.spawn:
            self.spawn = True
            enemy = EnemyBasic(
                random.randrange(0, GLOBALS.screen.get_width() - 30), 0)
            self.enemiesGroup.add(enemy)
        # get player instance
        player = self.get_player_from_group(player_group)

        # check enemies gets a bullet hit
        self.check_hit(player_group, self.enemiesGroup)

        # render enemies
        self.enemiesGroup.update(player)
        self.enemiesGroup.draw(GLOBALS.screen)
