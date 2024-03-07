import unittest

from src.globals import GameVariables
import pygame

# TODO: put this in a common file for testing, for some reason windows version
#  requires to load pygame init and other kind of things
# pygame setup
pygame.init()
# set caption
pygame.display.set_caption("Da2 Space invaders")
pygame.display.set_mode((600, 600))

GLOBALS = GameVariables()
pygame.mixer.init()

if __name__ == '__main__':
    # Discover and run all tests in the 'tests' directory and
    # its subdirectories
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('src', pattern='test_*.py')

    # Run the tests
    runner = unittest.TextTestRunner()
    result = runner.run(test_suite)
