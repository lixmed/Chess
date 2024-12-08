from Utils.constants import *
from Chess_engine.board import Board
from Utils.utils import generate_moves

class Game:
    def __init__(self):
        self.board = Board()
        self.current_player = WHITE

    