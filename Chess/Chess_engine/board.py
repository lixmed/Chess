class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.piece_type = piece_type
        self.row = None
        self.col = None

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_position(self):
        return self.row, self.col

class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]

    def place_piece(self, piece, row, col):
        self.board[row][col] = piece
        piece.set_position(row, col)

    def remove_piece(self, row, col):
        self.board[row][col] = None

    def is_empty(self, row, col):
        return self.board[row][col] is None

    def get_piece(self, row, col):
        return self.board[row][col]

    def print_board(self):
        for row in self.board:
            print(row)