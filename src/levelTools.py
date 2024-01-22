from src.globals import GameVariables
from src.characters import enemy
from src.characters.player import Player, PlayerController
import pygame
import json

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
            "basic": enemy.EnemyBasic
        }
        if enemy_type not in enemies_map:
            return enemy.EnemyBasic(x, y)
        enemy_class = enemies_map[enemy_type.lower()]
        return enemy_class(x, y)


class GameLevel:
    """ Creates the level structure according to the level """

    def __init__(self):
        self.level = None
        self.enemy_army: EnemyArmy = None
        self.player_controller: PlayerController = None

    def build_level(self, level, enemies):
        """Creates the level structure"""
        self.level = level
        self.enemy_army = EnemyArmy(level=level, pattern=enemies)
        self.player_controller = PlayerController()

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



