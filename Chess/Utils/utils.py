from Chess_engine.move import *

def generate_moves(board, row, col, color):
    piece = board.get_piece(row, col)
    moves = []

    if piece.piece_type == 'pawn':
        moves.extend(generate_pawn_moves(board, row, col, color))
    elif piece.piece_type == 'knight':
        moves.extend(generate_knight_moves(board, row, col, color))
    elif piece.piece_type == 'bishop':
        moves.extend(generate_bishop_moves(board, row, col, color))
    elif piece.piece_type == 'rook':
        moves.extend(generate_rook_moves(board, row, col, color))
    elif piece.piece_type == 'queen':
        moves.extend(generate_queen_moves(board, row, col, color))
    elif piece.piece_type == 'king':
        moves.extend(generate_king_moves(board, row, col, color))

    return moves

def is_square_attacked(board, row, col, color):
    opponent_color = 'white' if color == 'black' else 'black'
    for i in range(8):
        for j in range(8):
            piece = board.get_piece(i, j)
            if piece and piece.color == opponent_color:
                if piece.piece_type == 'pawn':
                    # Check pawn's capture moves
                    if (i, j) in generate_pawn_moves(board, i, j, opponent_color):
                        return True
                else:
                    # Check other pieces' moves
                    for move in generate_moves(board, i, j, opponent_color):
                        if move == (row, col):
                            return True
    return False