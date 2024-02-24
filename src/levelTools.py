import math
from typing import List

from src.globals import GameVariables
from src.characters import enemy
from src.characters.player import Player, PlayerController, Bullet
import pygame
import json
import random

from src.hit_particles import HitExplosionController

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
            if len(row) == 0 or len(row) > 8:
                raise Exception(
                    "Enemy rows need to be min 1 or max 8 elements")
            for e_type in row:
                if e_type:
                    # add enemy position with the gap to the left
                    new_enemy = self.build_enemy(e_type, x_delta + gap,
                                                 y_delta + gap)
                    new_enemy.life += round(
                        GLOBALS.level * 0.1) * new_enemy.life
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
            "shooter": enemy.EnemyShooter,
            "sniper": enemy.EnemySniper
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

        if 2 < self.level < 5:
            self.frequency = 1750
            self.limit_on_attack = 2

        if 4 < self.level < 7:
            self.frequency = 1500
            self.limit_on_attack = 4

        if 6 < self.level <= 10:
            self.frequency = 1000
            self.limit_on_attack = 6

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
        bullet: enemy.Enemy | None = None
        match enemy_ref.type:
            case 2:
                bullet = enemy.Bullet(enemy_ref.rect.centerx,
                                      enemy_ref.rect.y + enemy_ref.rect.height + 10)
            case 3:
                bullet = enemy.SniperBullet(enemy_ref.rect.centerx,
                                            enemy_ref.rect.y + enemy_ref.rect.height + 10)
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


class UIController:
    def __init__(self):
        self.txt_score: str = "Score: "
        self.txt_player_life: str = "Life: "
        self.txt_level: str = "Leve: "
        self.txt_game_over: str = "GAME OVER"
        self.txt_restart: str = "press SPACE to restart"
        self.__blink_restart = False
        self.__blink_timer = 500

    def in_game(self, player):
        # Level text
        GLOBALS.game_fonts.base.render_to(GLOBALS.screen, (10, 10),
                                          self.txt_level + str(GLOBALS.level),
                                          (255, 255, 255))
        # score text
        score, score_rect = GLOBALS.game_fonts.base.render(
            self.txt_score + str(GLOBALS.score), (255, 255, 255), (0, 0, 0, 0))
        score_rect.centerx = GLOBALS.screen.get_rect().centerx
        GLOBALS.screen.blit(score, score_rect)
        # life text
        GLOBALS.game_fonts.base.render_to(GLOBALS.screen, (520, 10),
                                          self.txt_player_life + str(
                                              GLOBALS.life),
                                          (255, 255, 255))

    def game_over(self):
        screen_center = GLOBALS.screen.get_rect().center
        # GAME OVER text
        game_over, game_over_rect = GLOBALS.game_fonts.title.render(
            self.txt_game_over, (255, 100, 100), (0, 0, 0, 0))
        game_over_rect.center = screen_center
        game_over_rect.centery -= 10
        GLOBALS.screen.blit(game_over, game_over_rect)
        # score text, in this case we add the life as score
        score, score_rect = GLOBALS.game_fonts.base.render(
            self.txt_score + str(GLOBALS.score + GLOBALS.life),
            (200, 200, 190), (0, 0, 0, 0))
        score_rect.center = screen_center
        score_rect.centery += 10
        GLOBALS.screen.blit(score, score_rect)
        # restart label
        restart, restart_rect = GLOBALS.game_fonts.base.render(
            self.txt_restart,
            (255, 255, 255, 255 if self.__blink_restart else 200),
            (0, 0, 0, 0))
        restart_rect.center = screen_center
        restart_rect.centery += 100
        GLOBALS.screen.blit(restart, restart_rect)
        self.__blink_timer -= GLOBALS.ms_fps
        if self.__blink_timer <= 0:
            self.__blink_restart = not self.__blink_restart
            self.__blink_timer = 500

        # Enter Key press detector
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            GLOBALS.restart = True

    def render(self, player_controller: PlayerController):
        # if level is complete then we can create the new level
        if player_controller.player.is_dead:
            self.game_over()
        else:
            self.in_game(player_controller.player)


class SpaceBackground:
    """ this creates a background animated with start and planets """

    def __init__(self, speed=1):
        self.img_height = 1200
        self.bg = pygame.image.load(GLOBALS.sprite_dir + "bg.png").convert()
        self.bg.set_alpha(180)
        self.tiles = math.ceil(self.img_height / self.bg.get_height()) + 1
        self.scroll = 0
        self.speed = speed

    def render(self):
        for i in range(0, self.tiles):
            GLOBALS.screen.blit(self.bg, (0, self.bg.get_height() * i
                                          + self.scroll))
        self.scroll -= self.speed
        if abs(self.scroll) > self.img_height:
            self.scroll = 0


class GameLevel:
    """ Creates the level structure according to the level """

    def __init__(self):
        self.level = None
        self.enemy_army: EnemyArmy = None
        self.player_controller: PlayerController = None
        self.enemy_controller: HiveMind = None
        self.background = SpaceBackground()
        self.hit_controller = HitExplosionController()

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
            GLOBALS.sound_controller.stop()
            return True
        return False

    def is_game_over(self) -> bool:
        """Check if player is dead
               :returns: boolean"""
        if GLOBALS.life <= 0:
            GLOBALS.sound_controller.stop()
            return True
        return False

    def check_collisions(self):
        for enemy_ref in self.enemy_army.enemiesGroup.spritedict:
            enemy_item: enemy.Enemy = enemy_ref
            for player_ref in self.player_controller.playerGroup.spritedict:
                player_or_bullet: Player | Bullet = player_ref
                # check player got hit
                if player_or_bullet.tag == "player":
                    if player_or_bullet.rect.colliderect(enemy_item.rect):
                        # check invulnerability
                        if not player_or_bullet.invulnerable:
                            player_or_bullet.take_damage(enemy_item.damage)
                            player_or_bullet.active_invulnerability()
                            # render hit
                            self.hit_controller.add_hit_explosion(
                                player_or_bullet.rect.center,
                                sound_effect=False)
                            # if hit is enemy_bullet then we need to remove it
                            if enemy_item.type == 0:
                                enemy_item.is_dead = True
                # enemy bullets are type 0, that's why type > 0
                if player_or_bullet.tag == "bullet" and enemy_item.type > 0:
                    if player_or_bullet.rect.colliderect(enemy_item.rect):
                        # render hit
                        self.hit_controller.add_hit_explosion(
                            enemy_item.rect.center)

                        enemy_item.take_damage(player_or_bullet.damage)
                        player_or_bullet.hit()

    def render_level_frame(self):
        self.background.render()
        self.player_controller.render()
        self.check_collisions()
        self.enemy_army.enemiesGroup.update(self.player_controller.player)
        self.enemy_controller.update()
        self.enemy_army.enemiesGroup.draw(GLOBALS.screen)
        self.hit_controller.render()

    def __str__(self):
        return (f"(level: {self.level}, enemies: {self.enemy_army}, "
                f"player: {self.player_controller.player})")


class LevelController:
    def __init__(self):
        self.__game_level = GameLevel()
        self.__curr_level = 1
        self.__level_list = self.__load_levels_file()
        self.__create_level(self.__curr_level)
        self.__ui = UIController()

    def __restart(self):
        GLOBALS.restart = False
        GLOBALS.level = 1
        GLOBALS.life = 100
        GLOBALS.score = 0
        self.__init__()

    def __create_level(self, level):
        self.__curr_level = level
        next_level = f"level_{self.__curr_level}"
        if next_level not in self.__level_list:
            return
        enemy_set = self.__level_list[next_level]
        self.__game_level.build_level(level=self.__curr_level,
                                      enemies=enemy_set)

    def execute(self) -> None:
        if GLOBALS.restart:
            self.__restart()
            return
        if not self.__game_level.is_game_over():
            if self.__game_level.is_level_completed():
                self.__curr_level += 1
                GLOBALS.level = self.__curr_level
                self.__create_level(self.__curr_level)
                return
            # render level frame
            self.__game_level.render_level_frame()
        # render ui
        self.__ui.render(self.__game_level.player_controller)

    @staticmethod
    def __load_levels_file():
        data_levels = []
        with open('src/assets/levels.json') as f:
            data_levels = json.load(f)
        return data_levels
