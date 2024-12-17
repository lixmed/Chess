class MoveGenerator:
    
    def getPawnMoves(self, r, c, moves, board, whiteToMove):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if whiteToMove:
            if board[r - 1][c] == "--":  # 1 square move
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), board))
                    if r == 6 and board[r-2][c] == "--":  # 2 square move
                        moves.append(Move((r, c), (r - 2, c), board))
            if c - 1 >= 0:  # Capture to the left
                if board[r - 1][c - 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), board, isEnpassantMove=True))
            if c + 1 < len(board):  # Capture to the right
                if board[r - 1][c + 1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), board, isEnpassantMove=True))        
                
        else:
            if board[r + 1][c] == "--":  # 1 square move
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), board))
                    if r == 1 and board[r+2][c] == "--":  # 2 square move
                        moves.append(Move((r, c), (r + 2, c), board))
            if c - 1 >= 0:  # Capture to the left
                if board[r + 1][c - 1][0] == "w":
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), board, isEnpassantMove=True))
            if c + 1 < len(board):  # Capture to the right
                if board[r + 1][c + 1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), board, isEnpassantMove=True))
              
    def getRookMoves(self, r, c, moves, board, whiteToMove):
        """Gets all rook moves for the rook located at (r, c) and adds moves to move log"""
        opponent = 'b' if whiteToMove else 'w'

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if board[r][c][1] != 'Q':  # Can't remove queen from pin on rook moves (only bishop moves)
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Tuples indicate (row, column) movements possible
        for d in directions:
            for i in range(1, len(board)):
                endRow = r + d[0] * i  # Potentially moves up/down to 7 rows
                endCol = c + d[1] * i  # Potentially moves up/down to 7 columns
                if 0 <= endRow < len(board) and 0 <= endCol < len(board[0]):  # Makes sure on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = board[endRow][endCol]
                        if endPiece == '--':  # Valid move to empty space
                            moves.append(Move((r, c), (endRow, endCol), board))
                        elif endPiece[0] == opponent:  # Valid move to capture
                            moves.append(Move((r, c), (endRow, endCol), board))
                            break
                        else:  # Cannot take friendly piece
                            break
                else:  # Cannot move off board
                    break

    def getKnightMoves(self, r, c, moves, board, whiteToMove):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))  # L-shaped moves
        allyColor = "w" if whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < len(board) and 0 <= endCol < len(board[0]):
                if not piecePinned or pinDirection == (m[0], m[1]) or pinDirection == (-m[0], -m[1]):
                    endPiece = board[endRow][endCol]
                    if endPiece == "--" or endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), board))
        
    def getBishopMoves(self, r, c, moves, board, whiteToMove):
        """Gets all bishop moves for the bishop located at (r, c) and adds moves to move log"""
        opponent = 'b' if whiteToMove else 'w'

        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]  # Tuples indicate (row, column) movements possible
        for d in directions:
            for i in range(1, len(board)):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < len(board) and 0 <= endCol < len(board[0]):  # Makes sure on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = board[endRow][endCol]
                        if endPiece == '--':  # Valid move to empty space
                            moves.append(Move((r, c), (endRow, endCol), board))
                        elif endPiece[0] == opponent:  # Valid move to capture
                            moves.append(Move((r, c), (endRow, endCol), board))
                            break
                        else:  # Cannot take friendly piece
                            break
                else:  # Cannot move off board
                    break
        
    def getQueenMoves(self, r, c, moves, board, whiteToMove):
        self.getRookMoves(r, c, moves, board, whiteToMove)
        self.getBishopMoves(r, c, moves, board, whiteToMove)

    def getKingMoves(self, r, c, moves, board, whiteToMove):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))  # All possible king moves
        allyColor = "w" if whiteToMove else "b"
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                self.pins.remove(self.pins[i])
                break
        for m in kingMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < len(board) and 0 <= endCol < len(board[0]):
                endPiece = board[endRow][endCol]
                if endPiece == "--" or endPiece[0] != allyColor:
                    # Place king on end square and check for checks
                    if whiteToMove:
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), board))
                    # Place king back on original location
                    if whiteToMove:
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
    
    def getCastleMoves(self, r, c, moves, board, whiteToMove):
        if self.squareUnderAttack(r, c):
            return # Can't castle while in check
        if (self.whiteToMove and self.currentCastleRights.wks) or (not self.whiteToMove and self.currentCastleRights.bks):
            self.getKingsideCastleMoves(r, c, moves, board, whiteToMove)
        if (self.whiteToMove and self.currentCastleRights.wqs) or (not self.whiteToMove and self.currentCastleRights.bqs):
            self.getQueensideCastleMoves(r, c, moves, board, whiteToMove)
    
    def getKingsideCastleMoves(self, r, c, moves, board, whiteToMove):
        if board[r][c+1] == "--" and board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), board, isCastleMove=True))
    
    def getQueensideCastleMoves(self, r, c, moves, board, whiteToMove):
        if board[r][c-1] == "--" and board[r][c-2] == "--" and board[r][c-3] == "--":
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), board, isCastleMove=True))
                
    
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks, self.bks, self.wqs, self.bqs = wks, bks, wqs, bqs 

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        # Castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)