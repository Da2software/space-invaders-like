import pygame.display
from pygame.freetype import Font


class SingletonMeta(type):
    """
    Base singleton Class to be used to create the business logic
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GameFonts:
    def __init__(self):
        self.base: Font = None
        self.title: Font = None


class GameVariables(metaclass=SingletonMeta):
    """
    Global variables to be able to access to this any place we need it
    """

    def __init__(self):
        self.screen: pygame.Surface = None
        self.game_fonts = GameFonts()
        self.sprite_dir = "src/assets/sprites/"
        self.delta_time = 0
        self.ms_fps = 16.666666667  # milliseconds peer frame (60 fps)
        self.score = 0
        self.level = 1
        # life do not reset after changing levels, more difficulty added XD
        self.life = 100
