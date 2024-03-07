from typing import List

import pygame.sprite
from src.globals import GameVariables

GLOBALS = GameVariables()


class RkAndMrShip(pygame.sprite.Sprite):
    """
      Cameo Character that gives extra life points to the player
      """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.tag = "cameo"
        # we need a drop area base on the screen size, also with a gap
        screen_width = GLOBALS.screen.get_width()
        self.movex_speed = 10
        # ship rendering
        self.image = pygame.image.load(
            GLOBALS.sprite_dir + "rkShip.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        # self.image.fill(col)
        self.rect = self.image.get_rect()
        self.life = 25
        self.init_life = 25

    def draw_health_bar(self) -> None:
        life_color = (128, 255, 0)
        life_bar_length = self.rect.width - 8  # with padding
        remaining_life = self.life / self.init_life
        # set the color of the life base
        if remaining_life > 0.75:
            life_color = (128, 255, 0)  # green color
        elif 0.5 < remaining_life <= 0.75:
            life_color = (255, 220, 0)  # yellow color
        elif 0.25 < remaining_life <= 0.5:
            life_color = (255, 128, 0)  # orange
        elif remaining_life <= 0.25:
            life_color = (255, 0, 0)  # red
        pygame.draw.rect(GLOBALS.screen, (255, 255, 255), (
            self.rect.x + 2, self.rect.y - 11, life_bar_length + 2, 6))
        pygame.draw.rect(GLOBALS.screen, life_color, (
            self.rect.x + 4, self.rect.y - 10,
            life_bar_length * remaining_life,
            4))

    def take_damage(self, damage: int) -> None:
        if self.life <= 0:
            self.life = 0
            return
            # then subtract the damage
        self.life -= damage

    def update(self) -> None:
        self.rect.centerx += self.movex_speed


class RkPortal(pygame.sprite.Sprite):
    """
      Portal Sprite
      """

    def __init__(self, x: int = 0, y: int = 0, duration=250):
        pygame.sprite.Sprite.__init__(self)
        self.tag = "portal"
        self.end = False
        # Load sprite sheet
        self.sprite_sheet = pygame.image.load(
            GLOBALS.sprite_dir + "/rkPortal.png").convert_alpha()
        # scale to 48 (3 times original size)
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet,
                                                   (48, 240))
        self.frames: List[
            pygame.Surface] = []  # we're going to save each title here
        self.frame_idx = 0
        self.load_frames()

        # Set the image and rect attributes for sprite
        self.image = self.frames[self.frame_idx]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        # Timer variables
        self.last_update = pygame.time.get_ticks()
        # duration dive frames result in the milliseconds frame rate
        self.frame_rate = duration / len(self.frames)
        # if sound_effect:
        #     # same as bullets, play a sound effect each instance
        #     GLOBALS.sound_controller.play("exp")

    def load_frames(self):
        # hit-particle image is a sheet grid of (16x16)x3 because the rescale
        for y in range(0, 240, 48):
            # we take the tile and add this into the frames list
            frame = self.sprite_sheet.subsurface(pygame.Rect(0, y, 48, 48))
            self.frames.append(frame)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            self.image = self.frames[self.frame_idx]


class RkLieUp(pygame.sprite.Sprite):
    """
      Item that increase life of player
      """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.tag = "cameo"
        # we need a drop area base on the screen size, also with a gap
        screen_width = GLOBALS.screen.get_width()
        self.fall_speed = 10
        # ship rendering
        self.image = pygame.image.load(
            GLOBALS.sprite_dir + "lifeUp.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.lifeUp = 20

    def update(self) -> None:
        self.rect.centery += self.fall_speed


class RkAndMrController:
    def __init__(self):
        self.__ship = RkAndMrShip()
        self.__rk_portal_start: RkPortal = RkPortal()
        self.__rk_portal_end: RkPortal = RkPortal()
        self.__rk_portal_end.end = True
        self.__renders = pygame.sprite.Group()
        self.__renders.add(self.__rk_portal_start)
        self.__renders.add(self.__rk_portal_end)

    def open_start_portal(self):
        self.__rk_portal_start.rect.centerx = (
            10, GLOBALS.screen.get_height() / 2)

    def render(self):
        pass
