import pygame
from src.globals import GameVariables
from src.utils import Position2D
import random
import math

GLOBALS = GameVariables()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.tag = "enemy"
        self.type = 1
        self.life = 10
        self.points = 5
        self.move_speed = 2
        self.is_dead = False
        self.die_animation = 0

    def take_damage(self, damage: int) -> None:
        self.life -= damage
        if self.life <= 0:
            self.is_dead = True
            GLOBALS.score += self.points
            print(GLOBALS.score)


class EnemyBasic(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.animation_time = 0  # 1 second delay
        # Rendering Variables
        self.image = pygame.Surface((30, 30))
        self.image.fill("red")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_dir: Position2D = Position2D()
        self.x_dir = 0
        self.player_pos: Position2D | None = None

    def update(self, player) -> None:
        # check if enemy is dead
        if self.is_dead:
            self.kill()
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
        :param player_group: playerGrop to be as a target, also to be
         used as a collider
        :return:
        """
        # todo: remove this later and add the level maker here
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
