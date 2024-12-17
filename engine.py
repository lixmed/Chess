from moves import MoveGenerator, Move, CastleRights

class GameState(MoveGenerator):

    def __init__(self):
        super().__init__()
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"], 
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation , self.blackKingLocation = (7, 4), (0, 4)
        self.inCheck = False
        self.checkmate, self.stalemate = False, False
        self.pins, self.checks = [], []
        self.enpassantPossible = ()  # Coordinates for the square where en passant capture is possible
        self.currentCastleRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                             self.currentCastleRights.wqs, self.currentCastleRights.bqs)]
        self.fiftyMoveCounter = 0
        self.positionLog = {}

    def makeMove(self, move, choice='Q'):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append((move, self.enpassantPossible))
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        if move.isPawnPromotion:
            promote = ''
            if choice == 'B':
                promote = move.pieceMoved[0] + 'B'
            elif choice == 'N':
                promote = move.pieceMoved[0] + 'N'
            elif choice == 'R':
                promote = move.pieceMoved[0] + 'R'
            else:
                promote = move.pieceMoved[0] + 'Q'
            
            self.board[move.endRow][move.endCol] = promote
            
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" # Capturing the pawn
        
        # Update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:# Only on 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # King side castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else: # Queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'
        
        # Update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                                 self.currentCastleRights.wqs, self.currentCastleRights.bqs))

        # Update fifty-move rule counter
        if move.pieceCaptured == "--" and move.pieceMoved[1] != 'p':
            self.fiftyMoveCounter += 1
        else:
            self.fiftyMoveCounter = 0

        # Update position log for threefold repetition
        board_tuple = tuple(tuple(row) for row in self.board)
        if board_tuple in self.positionLog:
            self.positionLog[board_tuple] += 1
        else:
            self.positionLog[board_tuple] = 1

    def undoMove(self):
        if len(self.moveLog) != 0:
            move, self.enpassantPossible = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # Undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # Undo 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # Undo castling rights
            self.castleRightsLog.pop() # Get rid of new castle rights from the move we are undoing
            castleRights = self.castleRightsLog[-1] # Set the current castle rights to the last one in the list
            self.currentCastleRights = CastleRights(castleRights.wks, castleRights.bks, castleRights.wqs, castleRights.bqs)
            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            self.checkmate, self.stalemate = False, False

            # Update fifty-move rule counter
            if move.pieceCaptured == "--" and move.pieceMoved[1] != 'p':
                self.fiftyMoveCounter -= 1
            else:
                self.fiftyMoveCounter = 0

            # Update position log for threefold repetition
            board_tuple = tuple(tuple(row) for row in self.board)
            if board_tuple in self.positionLog:
                self.positionLog[board_tuple] -= 1

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastleRights.wks = self.currentCastleRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastleRights.bks = self.currentCastleRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastleRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastleRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastleRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastleRights.bks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                        self.currentCastleRights.wqs, self.currentCastleRights.bqs)
        """Gets all moves considering checks"""
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        # Updates king locations
        if self.whiteToMove:
            king_row, king_column = self.whiteKingLocation[0], self.whiteKingLocation[1]
        else:
            king_row, king_column = self.blackKingLocation[0], self.blackKingLocation[1]

        if self.inCheck:
            if len(self.checks) == 1:  # Only 1 check: block check or move king
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                check_row, check_column = check[0], check[1]
                piece_checking = self.board[check_row][check_column]  # Enemy piece causing check
                valid_squares = []
                if piece_checking[1] == 'N':# If knight, must capture knight or move king
                    valid_squares = [(check_row, check_column)]
                else:# If rook, bishop, or queen, block check or move king
                    for i in range(1, len(self.board)):
                        valid_square = (king_row + check[2] * i, king_column + check[3] * i)  # 2 & 3 = check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_column:# Once you reach piece and check
                            break
                for i in range(len(moves) - 1, -1, -1):  # Gets rid of move not blocking, checking, or moving king
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in valid_squares:
                            moves.remove(moves[i])
            else:  # Double check, king must move
                self.getKingMoves(king_row, king_column, moves, self.board, self.whiteToMove)
        else:  # Not in check
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:  # Either checkmate or stalemate
            self.checkmate, self.stalemate = self.inCheck, not self.inCheck
        else:
            self.checkmate, self.stalemate = False, False
            
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves, self.board, self.whiteToMove)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves, self.board, self.whiteToMove)
        
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastleRights = tempCastleRights 

        # Check for fifty-move rule
        if self.fiftyMoveCounter >= 50:
            self.stalemate = True

        # Check for threefold repetition
        board_tuple = tuple(tuple(row) for row in self.board)
        if self.positionLog.get(board_tuple, 0) >= 3:
            self.stalemate = True

        # Check for insufficient material
        if self.insufficientMaterial():
            self.stalemate = True

        return moves

    def getAllPossibleMoves(self):
        """Gets all moves without considering checks"""
        moves = []
        for row in range(len(self.board)):  # Number of rows
            for column in range(len(self.board[row])):  # Number of columns in each row
                turn = self.board[row][column][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][column][1]
                    self.moveFunctions[piece](row, column, moves, self.board, self.whiteToMove)  # Calls move function based on piece type
        return moves

    def checkForPinsAndChecks(self):
        """Returns if the player is in check, a list of pins, and a list of checks"""
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            opponent, ally = 'b', 'w'
            startRow, startCol = self.whiteKingLocation
        else:
            opponent, ally = 'w', 'b'
            startRow, startCol = self.blackKingLocation

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # Resets possible pins
            for i in range(1, len(self.board)):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board):
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == ally and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st ally piece can be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd ally piece, so no pin or check possible
                            break
                    elif endPiece[0] == opponent:
                        pieceType = endPiece[1]
                        if (0 <= j <= 3 and pieceType == 'R') or (4 <= j <= 7 and pieceType == 'B') or \
                                (i == 1 and pieceType == 'p' and ((opponent == 'w' and 6 <= j <= 7)
                                                                   or (opponent == 'b' and 4 <= j <= 5))) or \
                                (pieceType == 'Q') or (i == 1 and pieceType == 'K'):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # Piece blocking, so pin
                                pins.append(possiblePin)
                                break
                        else:  # Enemy piece but not applying check
                            break
                else:  # Off board
                    break

        # Check for knight checks cause they are a bit different
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow < len(self.board) and 0 <= endCol < len(self.board):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == opponent and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))

        return inCheck, pins, checks

    def squareUnderAttack(self, row, col):
        """Determine if a square is under attack by any of the opponent's pieces"""
        self.whiteToMove = not self.whiteToMove  # Switch to opponent's turn
        opponent_moves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # Switch turns back
        for move in opponent_moves:
            if move.endRow == row and move.endCol == col:
                return True
        return False

    def insufficientMaterial(self):
        """Check for insufficient material to checkmate"""
        pieces = [piece for row in self.board for piece in row if piece != "--"]
        if len(pieces) == 2:
            return True  # Only kings left
        if len(pieces) == 3:
            if pieces.count("wK") == 1 and pieces.count("bK") == 1:
                if pieces.count("wB") == 1 or pieces.count("wN") == 1 or pieces.count("bB") == 1 or pieces.count("bN") == 1:
                    return True  # One side has only king and bishop/knight
        return False