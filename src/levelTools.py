from abc import ABC, abstractmethod
from src.characters.enemy import EnemyBasic, EnemiesController
from src.characters.player import Player, PlayerController


class GameLevel(ABC):
    """Level Marker representation"""

    def build_level(self):
        """Creates the level structure"""

    def render(self):
        """Render the level with all characters on it"""


class EnemyArmy:
    pass


class LevelFactory:
    pass
