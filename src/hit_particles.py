import math
from src.globals import GameVariables
import pygame

GLOBALS = GameVariables()


class HitParticle(pygame.sprite.Sprite):
    """ this creates a explosion hit animation """

    def __init__(self, x: int = 0, y: int = 0, duration=250,
                 sound_effect=True):
        pygame.sprite.Sprite.__init__(self)
        # Load sprite sheet
        self.sprite_sheet = pygame.image.load(
            GLOBALS.sprite_dir + "/hit-particle.png").convert_alpha()
        # scale to 48 (3 times original size)
        self.sprite_sheet = pygame.transform.scale(self.sprite_sheet,
                                                   (48, 240))
        self.frames = []  # we're going to save each title here
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
        if sound_effect:
            # same as bullets, play a sound effect each instance
            GLOBALS.sound_controller.play("exp")

    def load_frames(self):
        # hit-particle image is a sheet grid of (16x16)x3 because the rescale
        for y in range(0, 240, 48):
            # we take the tile and add this into the frames list
            frame = self.sprite_sheet.subsurface(pygame.Rect(0, y, 48, 48))
            self.frames.append(frame)

    def update(self):
        if self.frame_idx >= len(self.frames) - 1:
            self.kill()
            return
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
            self.image = self.frames[self.frame_idx]


class HitExplosionController:
    def __init__(self):
        # create the hit explosion group
        self.explosion_group = pygame.sprite.Group()

    def add_hit_explosion(self, pos: tuple = (0, 0), sound_effect=True):
        new_explosion = HitParticle(pos[0], pos[1], sound_effect=sound_effect)
        self.explosion_group.add(new_explosion)

    def render(self):
        self.explosion_group.update()
        self.explosion_group.draw(GLOBALS.screen)
