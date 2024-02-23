from typing import List

import pygame


class SoundItem:
    def __init__(self, name: str, file: str):
        self.name: str = name
        self.file = file
        self.sound = pygame.mixer.Sound(file)

    def __str__(self):
        return f"({self.name}, {self.file})"


class SoundController:
    """ we need to save this into GLOBALS """

    def __init__(self):
        self.sounds_dir = "src/assets/sounds/"
        self.library: List[SoundItem] = []

    def add_sound(self, name: str, file: str):
        new_sound = SoundItem(name, self.sounds_dir + file)
        self.library.append(new_sound)

    def play(self, name):
        for item in self.library:
            if item.name == name:
                item.sound.play()
                break

    def stop(self):
        pygame.mixer.stop()
