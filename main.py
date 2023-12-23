# Example file showing a circle moving on screen
import pygame
from src.characters.player import PlayerController
from src.characters.enemy import EnemiesController
from src.globals import GameVariables

# pygame setup
pygame.init()
# set caption
pygame.display.set_caption("Da2 Space invaders")
# load the image
gameIcon = pygame.image.load("src/assets/base.png")
# set icon
pygame.display.set_icon(gameIcon)

GLOBALS = GameVariables()
GLOBALS.screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True

# Create player controller
playerController = PlayerController()
# Create enemy controller
enemiesController = EnemiesController()

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
    # render enemies actions
    enemiesController.render(playerController.playerGroup)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000
    # set delta time that player use to move itself
    GLOBALS.delta_time = dt

pygame.quit()
