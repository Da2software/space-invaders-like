import unittest
from src.characters.player import *
from src.characters.enemy import *


class TestCharacters(unittest.TestCase):
    def test_player(self):
        player_test = Player("blue", 50, 50)
        self.assertEqual(player_test.rect.center, (50, 50))
        self.assertEqual(player_test.is_dead, False)
        player_test.take_damage(101)
        self.assertEqual(player_test.is_dead, True)

    def test_enemy(self):
        enemy_test = Enemy(50, 50)
        self.assertEqual(enemy_test.rect.center, (50, 50))
        self.assertEqual(enemy_test.rect.width, 48)
        self.assertEqual(enemy_test.rect.height, 48)
        self.assertEqual(enemy_test.is_dead, False)
        enemy_test.take_damage(101)
        self.assertEqual(enemy_test.is_dead, True)
