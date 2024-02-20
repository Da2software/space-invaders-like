from typing import List

from src.globals import GameVariables
from src.characters import enemy
from src.characters.player import Player, PlayerController
import pygame
import json
import random

GLOBALS = GameVariables()


class EnemyArmy:
    """Factory class to generate a Enemies group placed over the level"""

    def __init__(self, level=1, pattern=[[]]):
        self.level = level
        self.pattern = pattern
        self.enemiesGroup: pygame.sprite.Group = None
        self.__create()

    def __create(self, w_margin=45, h_margin=45, gap=25,
                 enemy_size=40) -> None:
        """
        Build the enemies collection based on the screen size (600x600)
        we will take 20 and 20 px from left to right and then each enemy takes
        56px per col and row, each enemy has a 8px margin/gap
        """
        self.enemiesGroup = pygame.sprite.Group()  # restart the group
        x_delta = w_margin
        y_delta = h_margin
        gap = gap
        enemy_size = enemy_size
        for row in self.pattern:
            for e_type in row:
                # add enemy position with the gap to the left
                new_enemy = self.build_enemy(e_type, x_delta + gap,
                                             y_delta + gap)
                self.enemiesGroup.add(new_enemy)
                # add the gap to the right
                x_delta += enemy_size + gap
            y_delta += enemy_size + gap
            x_delta = w_margin

    @staticmethod
    def build_enemy(enemy_type: str, x: int, y: int) -> enemy.Enemy:
        """
        Creates an enemy based on the type, it takes the object where
        the Enemies classes are referred
        :param y: start vertical position
        :param x: start horizontal position
        :param enemy_type: enemy type identifier, this is unique
        :return: a {Enemy} class type with all the properties
        """
        enemies_map = {
            "basic": enemy.EnemyBasic,
            "shooter": enemy.EnemyShooter
        }
        if enemy_type not in enemies_map:
            return enemy.EnemyBasic(x, y)
        enemy_class = enemies_map[enemy_type.lower()]
        return enemy_class(x, y)


class HiveMind:
    """ Use to control all action over an Enemy Army"""

    def __init__(self, army: EnemyArmy, level=1):
        self.army = army
        self.level = level
        # validations
        if not army:
            raise Exception("HiveMind: class require EnemyArmy parameter")
        self.enemy_list: List[enemy.Enemy] = []
        self.get_enemy_list()
        if len(self.enemy_list) == 0:
            raise Exception("HiveMind: EnemyArmy list is empty")
        # take idle duration
        self.__idle_duration = self.enemy_list[0].animations.get_animation(
            "idle").get_duration()
        self.__global_idle_timer = 0
        self.frequency = 1000
        self.frequency_timer = 0
        self.limit_on_attack = 2
        self.on_attack_count = 0
        self.setup()

    def setup(self):
        """ Analyze the current army and creates a patter attack """

        if 2 < self.level <= 4:
            self.frequency = 1500
            self.limit_on_attack = 2

        for enemy_ref in self.enemy_list:
            enemy_ref.run_animation("idle", True)
            enemy_ref.restore_pos_callback = self.restore_pos_ends
            enemy_ref.attack_end_callback = self.attack_ends
            enemy_ref.on_die_callback = self.on_enemy_dies
            enemy_ref.on_shoot_callback = self.on_shoot

    def get_enemy_list(self):
        """ update enemy list, this variable is used over multiple processes"""
        base_list = self.army.enemiesGroup.sprites()
        self.enemy_list = []
        for item in base_list:
            # ignore bullets
            if item.tag == "enemy_bullet":
                continue
            self.enemy_list.append(item)

    def idle_timer(self):
        """
        used to sync all the enemies timers on idle mode
        :return:
        """
        self.__global_idle_timer += GLOBALS.ms_fps
        if self.__global_idle_timer > self.__idle_duration:
            self.__global_idle_timer = 0
        for enemy_ref in self.enemy_list:
            if enemy_ref.idle:
                enemy_ref.timer = self.__global_idle_timer

    def on_shoot(self, enemy_ref: enemy.Enemy):
        # TODO: add a mechanic to use different bullets base on the enemy type
        bullet: enemy.Enemy = (
            enemy.Bullet(enemy_ref.rect.centerx,
                         enemy_ref.rect.y + enemy_ref.rect.height + 10))
        self.army.enemiesGroup.add(bullet)

    def attack_ends(self, enemy_ref):
        # we are not using this yet
        pass

    def restore_pos_ends(self, enemy_ref: enemy.Enemy):
        # set the idle animation again
        enemy_ref.run_animation("idle", True)
        # to sync animation with the rest we need to do a
        # remaining time calculation to wait and start the idle at
        # the same time
        enemy_ref.animation_delay = self.__idle_duration - self.__global_idle_timer

    def on_enemy_dies(self, enemy_ref: enemy.Enemy):
        # we need to update the list again
        self.get_enemy_list()

    def execute_attack(self, chosen_one: enemy.Enemy):
        """ Takes an enemy to trigger one of its attack actions """
        if self.on_attack_count >= self.limit_on_attack:
            return
        chosen_one.attack()

    def update(self):
        self.idle_timer()
        # check attacking enemies
        self.on_attack_count = 0
        for an_enemy in self.army.enemiesGroup.sprites():
            if an_enemy.on_attack:
                self.on_attack_count += 1
        # check if we can attack or not
        if self.frequency_timer > self.frequency:
            # check if last one is dead or not to avoid complete this task
            if len(self.enemy_list) == 1 and self.enemy_list[0].is_dead:
                return
            chosen_one = random.randint(0, len(self.enemy_list) - 1)
            if self.enemy_list[chosen_one].on_attack:
                return
            if (not self.enemy_list[chosen_one].on_attack
                    and self.enemy_list[chosen_one].restart_pos):
                return
            self.execute_attack(self.enemy_list[chosen_one])
            # restore frequency if we reach the limit
            if self.on_attack_count >= self.limit_on_attack:
                self.frequency_timer = 0
        self.frequency_timer += GLOBALS.ms_fps


class GameLevel:
    """ Creates the level structure according to the level """

    def __init__(self):
        self.level = None
        self.enemy_army: EnemyArmy = None
        self.player_controller: PlayerController = None
        self.enemy_controller: HiveMind = None

    def build_level(self, level, enemies):
        """Creates the level structure"""
        self.level = level
        self.enemy_army = EnemyArmy(level=level, pattern=enemies)
        self.player_controller = PlayerController()
        self.enemy_controller = HiveMind(self.enemy_army, level)

    def is_level_completed(self) -> bool:
        """Check if level is complete
        :returns: boolean"""
        if len(self.enemy_army.enemiesGroup) == 0:
            return True
        return False

    def is_game_over(self) -> bool:
        """Check if player is dead
               :returns: boolean"""
        if self.player_controller.player.life == 0:
            return True
        return False

    def check_bullet_hit(self):
        for enemy_item in self.enemy_army.enemiesGroup.spritedict:
            for bullet in self.player_controller.playerGroup.spritedict:
                if bullet.tag == "bullet":
                    if bullet.rect.colliderect(enemy_item.rect):
                        enemy_item.take_damage(bullet.damage)
                        bullet.hit()

    def render_level_frame(self):
        self.player_controller.render()
        self.check_bullet_hit()
        self.enemy_army.enemiesGroup.update(self.player_controller.player)
        self.enemy_controller.update()
        self.enemy_army.enemiesGroup.draw(GLOBALS.screen)

    def __str__(self):
        return (f"(level: {self.level}, enemies: {self.enemy_army}, "
                f"player: {self.player_controller.player})")


class LevelController:
    def __init__(self):
        self.__game_level = GameLevel()
        self.__curr_level = 1
        self.__level_list = self.__load_levels_file()
        self.__create_level(1)

    def __create_level(self, level):
        self.__curr_level = level
        next_level = f"level_{self.__curr_level}"
        if next_level not in self.__level_list:
            return
        enemy_set = self.__level_list[next_level]
        self.__game_level.build_level(level=1, enemies=enemy_set)

    def execute(self) -> None:
        # if level is complete then we can create the new level
        if self.__game_level.is_level_completed():
            self.__curr_level += 1
            self.__create_level(self.__curr_level)
            return
        if self.__game_level.is_game_over():
            # do something
            return

        # render level frame
        self.__game_level.render_level_frame()

    @staticmethod
    def __load_levels_file():
        data_levels = []
        with open('src/assets/levels.json') as f:
            data_levels = json.load(f)
        return data_levels
