import os

import pygame
from states.state import State


class Game_World(State):
    def __init__(self, game):
        State.__init__(self, game)