import math

import pygame


class Position2D:
    """
    CLass to be used to save position states, to avoid create multiple x and y
    variables each time we need a position
    """

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def clear(self):
        self.x = 0
        self.y = 0

    def __str__(self):
        return f"x_axis = {self.x} | y_axis = {self.y}"


def calculate_distance(target_pos: tuple, current_pos: tuple):
    # Calculate the distance to move in each frame
    dx = target_pos[0] - current_pos[0]
    dy = target_pos[1] - current_pos[1]
    distance = pygame.math.Vector2(dx, dy).length()
    return dx, dy, distance


def get_direction_angle(vector1: tuple, vector2: tuple):
    """ get the angle between two vectors"""
    # get distances
    return math.atan2(vector2[1] - vector1[1],  # y2 - y1
                      vector2[0] - vector1[0])  # x2 - x2


def move_to_direction(rect: pygame.Rect,
                      angle: float = 0, speed=10):
    # move rect
    rect.centerx += speed * math.cos(angle)
    rect.centery += speed * math.sin(angle)
