import unittest

import pygame

from src.levelTools import EnemyArmy


class TestLevelTools(unittest.TestCase):

    def test_enemies_army(self):
        try:
            assert_res = True
            army_class = EnemyArmy(level=1, pattern=[
                ["basic", "basic", "basic"]
            ])
            if army_class.level != 1:
                assert_res = False
            if len(army_class.enemiesGroup) < 3:
                assert_res = False
            self.assertTrue(assert_res)
        except Exception as err:
            self.assertTrue(False, err)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
