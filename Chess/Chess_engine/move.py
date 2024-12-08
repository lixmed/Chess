from Chess_engine.board import Board
from Utils.utils import is_square_attacked



def generate_pawn_moves(board, row, col, color):
    moves = []
    direction = 1 if color == 'white' else -1
    
    # Forward move
    new_row = row + direction
    if 0 <= new_row < 8 and board.is_empty(new_row, col):
        moves.append((new_row, col))
        
        # Initial two-square move
        if (row == 1 and color == 'white') or (row == 6 and color == 'black'):
            new_row += direction
            if board.is_empty(new_row, col):
                moves.append((new_row, col))
    
    # Capture moves
    for offset in (-1, 1):
        new_row = row + direction
        new_col = col + offset
        if 0 <= new_row < 8 and 0 <= new_col < 8 and not board.is_empty(new_row, new_col) and board.get_piece(new_row, new_col).color != color:
            moves.append((new_row, new_col))
    
    return moves

def generate_bishop_moves(board, row, col, color):
    moves = []
    directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in directions:
        new_row, new_col = row + dx, col + dy
        while 0 <= new_row < 8 and 0 <= new_col < 8 and board.is_empty(new_row, new_col):
            moves.append((new_row, new_col))
            new_row += dx
            new_col += dy
        if 0 <= new_row < 8 and 0 <= new_col < 8 and board.get_piece(new_row, new_col).color != color:
            moves.append((new_row, new_col))
    return moves

def generate_knight_moves(board, row, col, color):
    moves = []
    deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    for dx, dy in deltas:
        new_row, new_col = row + dx, col + dy
        if 0 <= new_row < 8 and 0 <= new_col < 8 and (board.is_empty(new_row, new_col) or board.get_piece(new_row, new_col).color != color):
            moves.append((new_row, new_col))
    return moves

def generate_rook_moves(board, row, col, color):
    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dx, dy in directions:
        new_row, new_col = row + dx, col + dy
        while 0 <= new_row < 8 and 0 <= new_col < 8 and board.is_empty(new_row, new_col):
            moves.append((new_row, new_col))
            new_row += dx
            new_col += dy
        if 0 <= new_row < 8 and 0 <= new_col < 8 and board.get_piece(new_row, new_col).color != color:
            moves.append((new_row, new_col))
    return moves

def generate_king_moves(board, row, col, color):
    moves = []
    deltas = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in deltas:
        new_row, new_col = row + dx, col + dy
        if 0 <= new_row < 8 and 0 <= new_col < 8 and (board.is_empty(new_row, new_col) or board.get_piece(new_row, new_col).color != color):
            moves.append((new_row, new_col))

    # Castling
    if not board.get_piece(row, col).has_moved:
        if color == 'white':
            # Kingside castling
            if board.is_empty(row, col + 1) and board.is_empty(row, col + 2) and not board.get_piece(row, col + 3).has_moved:
                if not is_square_attacked(board, row, col + 1, 'black') and not is_square_attacked(board, row, col + 2, 'black'):
                    moves.append((row, col + 2))
            # Queenside castling
            if board.is_empty(row, col - 1) and board.is_empty(row, col - 2) and board.is_empty(row, col - 3) and not board.get_piece(row, col - 4).has_moved:
                if not is_square_attacked(board, row, col - 1, 'black') and not is_square_attacked(board, row, col - 2, 'black'):
                    moves.append((row, col - 2))
        else:
            # Kingside castling
            if board.is_empty(row, col + 1) and board.is_empty(row, col + 2) and not board.get_piece(row, col + 3).has_moved:
                if not is_square_attacked(board, row, col + 1, 'white') and not is_square_attacked(board, row, col + 2, 'white'):
                    moves.append((row, col + 2))
            # Queenside castling
            if board.is_empty(row, col - 1) and board.is_empty(row, col - 2) and board.is_empty(row, col - 3) and not board.get_piece(row, col - 4).has_moved:
                if not is_square_attacked(board, row, col - 1, 'white') and not is_square_attacked(board, row, col - 2, 'white'):
                    moves.append((row, col - 2))
    return moves

def generate_queen_moves(board, row, col, color):
    return generate_bishop_moves(board, row, col, color) + generate_rook_moves(board, row, col, color)