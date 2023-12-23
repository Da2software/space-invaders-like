# Example file showing a circle moving on screen
import pygame
from src.characters.player import PlayerController
from src.globals import GameVariables

# pygame setup
pygame.init()
GLOBALS = GameVariables()
GLOBALS.screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True

# Create player controller
playerController = PlayerController()

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    GLOBALS.screen.fill("black")

    # render player actions
    playerController.render()

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    # set delta time that player use to move itself
    GLOBALS.delta_time = dt

pygame.quit()
