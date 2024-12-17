import pygame as p
import computer
from engine import GameState
from moves import MoveGenerator, Move

WIDTH = HEIGHT = 480
SIDEBAR_WIDTH = 200
DIMENSION = 8  # Chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60  # For animations later on
IMAGES = {}
BACKGROUND_IMAGE = p.image.load('background.jpg')
BACKGROUND_IMAGE = p.transform.scale(BACKGROUND_IMAGE, (WIDTH, HEIGHT))

class ChessGame:
    def __init__(self):
        self.boardColors = {
            "light": p.Color(240, 217, 181),  # light square color
            "dark": p.Color(181, 136, 99),    # dark square color
            "highlight": p.Color("#D1A15B"),  # highlight selected square color
            "validMove": p.Color("#00CED1")  # valid move square color
        }
        self.pieceColors = {
            "white": p.Color(255, 255, 255),  # White pieces (used for highlights)
            "black": p.Color(0, 0, 0)  # Black pieces (used for highlights)
        }

        self.textColor = p.Color("#333333")  # Default text color (can be modified per theme)
        self.screen = None
        self.clock = None
        self.gs = GameState()
        self.validMoves = self.gs.getValidMoves()
        self.moveMade = False
        self.sqSelected = None  # tuple: (row, col)
        self.playerClicks = []  # Keep track of player clicks (two tuples: [(6, 4), (4, 4)])
        self.selectedPieceMoves = []  # Store valid moves for the selected piece
        self.capturedPieces = {"w": [], "b": []}  # Store captured pieces
        self.playerOne, self.playerTwo = None, None

    def loadImages(self):
        pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
        for piece in pieces:
            IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

    def initializeGame(self):
        p.init()
        p.display.set_caption("Chess Game")
        self.screen = p.display.set_mode((WIDTH + SIDEBAR_WIDTH, HEIGHT))
        self.clock = p.time.Clock()
        self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        self.sidebarImage = p.image.load("sidebarImage.jpg")  # Load the sidebar image
        self.sidebarImage = p.transform.scale(self.sidebarImage, (SIDEBAR_WIDTH, HEIGHT))
        self.loadImages()
        

    # Get player mode, color, and difficulty level
        self.playerOneIsHuman, self.playerTwoIsHuman, self.color, self.difficulty = self.showStartWindow()

    # Assign players based on color choice
        if self.color == "white":
            self.playerOne = self.playerTwoIsHuman  # White player
            self.playerTwo = self.playerOneIsHuman  # Black player
        else:  # User chose black
            self.playerOne = self.playerOneIsHuman  # White (computer or human)
            self.playerTwo = self.playerTwoIsHuman  # Black (user)

        print(f"Player 1 is {'Human' if self.playerOne else 'Computer'} playing White")
        print(f"Player 2 is {'Human' if self.playerTwo else 'Computer'} playing Black")

    def mainLoop(self):
        running = True
        while running:
            humanTurn = (self.gs.whiteToMove and self.playerOne) or (not self.gs.whiteToMove and self.playerTwo)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    if humanTurn:
                        self.handleMouseClick(e)
                elif e.type == p.KEYDOWN:
                    self.handleKeyPress(e)
            if not humanTurn:
                self.handleAIMove()
            if self.moveMade:
                self.validMoves = self.gs.getValidMoves()
                self.moveMade = False
            self.drawGameState()
            if self.gs.checkmate or self.gs.stalemate:
                self.showEndGameMessage("Checkmate" if self.gs.checkmate else "Stalemate", "Black" if self.gs.whiteToMove else "White")
                running = False
            self.clock.tick(MAX_FPS)
            p.display.flip()

    def handleMouseClick(self, event):
        location = p.mouse.get_pos()  # location of the mouse (x, y)
        if location[0] < WIDTH:  # Click on the board
            col, row = (location[0] // SQ_SIZE), (location[1] // SQ_SIZE)
            if self.sqSelected == (row, col):  # The user clicked the same square twice
                self.sqSelected = None  # Deselect
                self.playerClicks = []  # Clear player clicks
                self.selectedPieceMoves = []  # Clear valid moves for the selected piece
            else:
                self.sqSelected = (row, col)
                self.playerClicks.append(self.sqSelected)  # Append for both 1st and 2nd clicks
                self.selectedPieceMoves = [move for move in self.validMoves if move.startRow == row and move.startCol == col]
            if len(self.playerClicks) == 2:  # After the 2nd click
                move = Move(self.playerClicks[0], self.playerClicks[1], self.gs.board)
                print(move.getChessNotation())
                for i in range(len(self.validMoves)):
                    if move == self.validMoves[i]:
                        if move.isPawnPromotion:
                            choice = self.showPromotionChoices(self.gs.whiteToMove)
                            self.gs.makeMove(self.validMoves[i], choice)
                        else:
                            self.gs.makeMove(self.validMoves[i])

                    # Update captured pieces before animating
                        if move.pieceCaptured != "--":
                            self.capturedPieces[move.pieceCaptured[0]].append(move.pieceCaptured)

                    # Call the animateMove function to animate the move
                        self.animateMove(self.playerClicks[0], self.playerClicks[1], move.pieceMoved)

                        self.moveMade = True
                        self.sqSelected = None  # Reset user clicks
                        self.playerClicks = []
                        self.selectedPieceMoves = []  # Clear valid moves for the selected piece

                    # Play sounds after move
                        if move.pieceCaptured != "--":
                            p.mixer.Sound('sounds_capture.mp3').play()
                        else:
                            p.mixer.Sound('sounds_move-self.mp3').play()
                        break  # Exit loop once the move is made
                if not self.moveMade:
                    self.playerClicks = [self.sqSelected]

    def handleKeyPress(self, event):
        if event.key == p.K_z:
            self.gs.undoMove()
            self.moveMade = True
        if event.key == p.K_r:
            self.resetGame()

    def drawButton(self, text, buttonRect, buttonColor, textColor, outlineColor):
        font = p.font.SysFont("Helvetica", buttonRect.height // 2, True, False)

        # Create background and outline rectangles for the button
        paddingX, paddingY = 8, 4
        textSurface = font.render(text, True, textColor)
        textRect = textSurface.get_rect(center=buttonRect.center)

        # Create background and outline rectangles
        backgroundRect = buttonRect.inflate(paddingX * 2, paddingY * 2)
        outlineRect = backgroundRect.inflate(4, 4)

        # Draw the button outline and background
        p.draw.rect(self.screen, outlineColor, outlineRect, border_radius=8)
        p.draw.rect(self.screen, buttonColor, backgroundRect, border_radius=6)

        # Blit the text onto the button
        self.screen.blit(textSurface, textRect)

    def showDifficultyChoiceWindow(self):
        # Colors
        textColor = p.Color("#4B3621")  # Dark brown text
        backgroundColor = p.Color("#F5F5DC")  # Beige background
        outlineColor = p.Color("#4B3621")  # Dark brown outline
        buttonColor = p.Color("#F5F5DC")  # Button background
        buttonTextColor = p.Color("#4B3621")  # Button text

        # Load background image
        self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        self.screen.blit(self.sidebarImage, (WIDTH, 0))

        # Draw the title box
        titleRect = p.Rect(WIDTH // 2 - 150, HEIGHT // 4 - 40, 230, 50)
        self.drawButton("Select Difficulty", titleRect, backgroundColor, textColor, outlineColor)

        # Define buttons for difficulty levels
        buttonWidth, buttonHeight = 200, 60

        easyButton = p.Rect(WIDTH // 2 - buttonWidth // 2, HEIGHT // 2 - 80, buttonWidth, buttonHeight)
        mediumButton = p.Rect(WIDTH // 2 - buttonWidth // 2, HEIGHT // 2, buttonWidth, buttonHeight)
        hardButton = p.Rect(WIDTH // 2 - buttonWidth // 2, HEIGHT // 2 + 80, buttonWidth, buttonHeight)

        # Draw difficulty buttons
        self.drawButton("Easy", easyButton, buttonColor, buttonTextColor, outlineColor)
        self.drawButton("Medium", mediumButton, buttonColor, buttonTextColor, outlineColor)
        self.drawButton("Hard", hardButton, buttonColor, buttonTextColor, outlineColor)

        # Update the display
        p.display.flip()

        # Wait for user input
        waiting = True
        while waiting:
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    exit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if easyButton.collidepoint(location):
                        return "easy"
                    elif mediumButton.collidepoint(location):
                        return "medium"
                    elif hardButton.collidepoint(location):
                        return "hard"

    def handleAIMove(self):
        # Select AI move based on the difficulty level
        if self.difficulty == "easy":
            AIMove = computer.findRandomMove(self.validMoves)
        elif self.difficulty == "medium":
            AIMove = computer.findBestMove(self.gs, self.validMoves)
        else:  # Hard
            AIMove = computer.findBestMoveAlphaBeta(self.gs, self.validMoves)

    # Fallback to a random move if no move was found
        if AIMove is None:
            AIMove = computer.findRandomMove(self.validMoves)
    
    # Make the AI move and update game state
        self.gs.makeMove(AIMove)
        self.moveMade = True

    # Update captured pieces and play the appropriate sound
        if AIMove.pieceCaptured != "--":
            self.capturedPieces[AIMove.pieceCaptured[0]].append(AIMove.pieceCaptured)
            p.mixer.Sound('sounds_capture.mp3').play()
        else:
            p.mixer.Sound('sounds_move-self.mp3').play()

    def resetGame(self):
        self.gs = GameState()
        self.validMoves = self.gs.getValidMoves()
        self.sqSelected = None
        self.playerClicks = []
        self.selectedPieceMoves = []
        self.capturedPieces = {"w": [], "b": []}
        self.moveMade = False

    def drawGameState(self):
        self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        self.drawBoard()
        self.drawPieces()
        self.drawSidebar()
        p.display.flip()

    def drawBoard(self):
    # Define colors
        colors = [p.Color(240, 217, 181), p.Color(181, 136, 99)]  # Light wood and dark wood
        selectedColor = p.Color(106, 90, 205)  # Cornflower blue for selected square
        moveColor = p.Color(72, 209, 204, 150)  # Light cyan with transparency for valid moves
        checkColor = p.Color(255, 99, 71)  # Tomato red for the king in check

    # Draw the squares
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                color = colors[(r + c) % 2]  # Default square color

            # Highlight selected square
                if self.sqSelected == (r, c):
                    color = selectedColor
            
            # Highlight valid moves
                if (r, c) in [(move.endRow, move.endCol) for move in self.selectedPieceMoves]:
                    color = moveColor

            # Highlight the king in check
                if self.gs.inCheck and ((self.gs.whiteToMove and (r, c) == self.gs.whiteKingLocation) or
                                        (not self.gs.whiteToMove and (r, c) == self.gs.blackKingLocation)):
                    color = checkColor

            # Draw the square
                p.draw.rect(self.screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    # Handle sounds for check and checkmate (outside the loop)
        if self.gs.inCheck and not hasattr(self.gs, 'checkSoundPlayed'):
            p.mixer.Sound('sounds_move-check.mp3').play()
            self.gs.checkSoundPlayed = True
        elif not self.gs.inCheck and hasattr(self.gs, 'checkSoundPlayed'):
            del self.gs.checkSoundPlayed

        if self.gs.checkmate and not hasattr(self.gs, 'checkmateSoundPlayed'):
            p.mixer.Sound('sounds_chess_com_checkmate.mp3').play()
            self.gs.checkmateSoundPlayed = True
        elif not self.gs.checkmate and hasattr(self.gs, 'checkmateSoundPlayed'):
            del self.gs.checkmateSoundPlayed

    def drawPieces(self):
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = self.gs.board[r][c]
                if piece != "--":
                    self.screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    def drawSidebar(self):
        # Sidebar background with gradient
        gradient = p.Surface((SIDEBAR_WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color = ("#3C2F2A")  
            p.draw.line(gradient, color, (0, y), (SIDEBAR_WIDTH, y))
        self.screen.blit(gradient, (WIDTH, 0))

    # Set up font
        font = p.font.SysFont("Helvetica", 20, True, False)

    # Display turn information (centered)
        turnText = "White to Move" if self.gs.whiteToMove else "Black to Move"
        turnLabel = font.render(turnText, True, p.Color("#F1E6D1") if not self.gs.whiteToMove else p.Color("#F1E6D1"))
        turnLabelRect = turnLabel.get_rect(center=(WIDTH + SIDEBAR_WIDTH // 2, 25))  # Centered at the top
        self.screen.blit(turnLabel, turnLabelRect)

    # Display captured pieces
        yOffset = 60
        pieceSize = SIDEBAR_WIDTH // 5  # Dynamically size the pieces to fit the sidebar
        for color, pieces in self.capturedPieces.items():
            labelText = "White captured:" if color == "w" else "Black captured:"
            label = font.render(labelText, True, p.Color("#F1E6D1"))
            labelRect = label.get_rect(topleft=(WIDTH + 10, yOffset))
            self.screen.blit(label, labelRect)

            yOffset += 30  # Space below label
            xOffset = WIDTH + 10
            for i, piece in enumerate(pieces):
                pieceImage = p.transform.scale(IMAGES[piece], (pieceSize, pieceSize))  # Dynamically resize
                self.screen.blit(pieceImage, (xOffset, yOffset))
                xOffset += pieceSize + 5  # Space between icons
                if (i + 1) % 4 == 0:  # Move to the next row after 4 icons
                    xOffset = WIDTH + 10
                    yOffset += pieceSize + 5
            if color == "w":
                yOffset += 40  # Space between white and black sections
   
    def animateMove(self, startSq, endSq, piece):
        startX, startY = startSq[1] * SQ_SIZE, startSq[0] * SQ_SIZE
        endX, endY = endSq[1] * SQ_SIZE, endSq[0] * SQ_SIZE
        frames = 10
        for frame in range(frames + 1):
            x = startX + (endX - startX) * frame / frames
            y = startY + (endY - startY) * frame / frames
            self.drawGameState()  # This will draw the board, pieces, and sidebar
            self.screen.blit(IMAGES[piece], (x, y))
            p.display.flip()
            self.clock.tick(60)

        
        # Set up font
        font = p.font.SysFont("Helvetica", 24, True, False)
        
        # Display whose turn it is using color
        turnColor = p.Color("white") if self.gs.whiteToMove else p.Color("black")
        turnRect = p.Rect(WIDTH + 10, 10, 30, 30)
        p.draw.rect(self.screen, turnColor, turnRect)
        
        # Display captured pieces
        yOffset = 60
        pieceSize = SQ_SIZE // 2  # Smaller size for captured pieces
        for color, pieces in self.capturedPieces.items():
            colorText = "White captured:" if color == "w" else "Black captured:"
            colorObject = font.render(colorText, 0, p.Color("Black"))
            self.screen.blit(colorObject, (WIDTH + 10, yOffset))
            yOffset += 30
            xOffset = WIDTH + 10
            for i, piece in enumerate(pieces):
                pieceImage = p.transform.scale(IMAGES[piece], (pieceSize, pieceSize))
                self.screen.blit(pieceImage, (xOffset, yOffset))
                xOffset += pieceSize + 5  # Move to the right for the next piece
                if (i + 1) % 4 == 0:  # Move to the next row after 4 pieces
                    xOffset = WIDTH + 10
                    yOffset += pieceSize + 5  # Add some space between rows
            yOffset += pieceSize + 10  # Add some space between different color sections

    def showEndGameMessage(self, message, winner):
        font = p.font.SysFont("Helvetica", 32, True, False)

    # Update the message text based on game state
        if winner:
            if message == "Checkmate":
                message = f"{winner} wins by checkmate!"
            else:   
                message = "It's a stalemate!"

    # Render the message text
        messageTextColor = p.Color(241, 230, 209)  # Light Cream Text
        textObject = font.render(message, True, messageTextColor)

    # Calculate message box size with padding
        paddingX, paddingY = 40, 20  # Padding around the message
        messageBoxWidth = textObject.get_width() + paddingX * 2
        messageBoxHeight = textObject.get_height() + paddingY * 2

    # Define the message box centered on the screen
        messageBoxColor = p.Color(106, 78, 58)  # Muted Brown Background
        messageBox = p.Rect(
            WIDTH // 2 - messageBoxWidth // 2,
            HEIGHT // 2 - messageBoxHeight // 2 - 80,
            messageBoxWidth, messageBoxHeight
        )
        p.draw.rect(self.screen, messageBoxColor, messageBox, border_radius=15)

    # Center the message text inside the message box
        textLocation = textObject.get_rect(center=messageBox.center)
        self.screen.blit(textObject, textLocation)

    # Button Settings
        buttonFont = p.font.SysFont("Helvetica", 28, True, False)
        buttonWidth, buttonHeight = messageBoxWidth // 2 - 20, 50

    # Define buttons below the message box
        playAgainButton = p.Rect(
            WIDTH // 2 - buttonWidth - 10, HEIGHT // 2 + messageBoxHeight // 2, buttonWidth, buttonHeight
        )
        quitButton = p.Rect(
            WIDTH // 2 + 10, HEIGHT // 2 + messageBoxHeight // 2, buttonWidth, buttonHeight
        )

    # Draw buttons
        playAgainColor = p.Color(79, 111, 43)  # Dark Olive Green
        quitButtonColor = p.Color(111, 38, 38)  # Dark Red

        p.draw.rect(self.screen, playAgainColor, playAgainButton, border_radius=10)
        p.draw.rect(self.screen, quitButtonColor, quitButton, border_radius=10)

    # Render button texts
        playAgainText = buttonFont.render("Play Again", True, messageTextColor)
        quitText = buttonFont.render("Exit", True, messageTextColor)

    # Center text inside buttons
        self.screen.blit(playAgainText, playAgainText.get_rect(center=playAgainButton.center))
        self.screen.blit(quitText, quitText.get_rect(center=quitButton.center))

    # Update the display
        p.display.flip()

    # Wait for user input
        waiting = True
        while waiting:
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    exit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if playAgainButton.collidepoint(location):
                        self.resetGame()
                        self.mainLoop()
                        waiting = False
                    elif quitButton.collidepoint(location):
                        p.quit()
                        exit()

    def drawTitle(self):
        font = p.font.SysFont("Helvetica", 32, True, False)

        # Define colors
        titleColor = p.Color("#4B3621")  # Dark brown text
        backgroundColor = p.Color("#F5F5DC")  # Beige background
        outlineColor = p.Color("#4B3621")  # Dark brown outline

        # Render the text
        titleText = font.render("Welcome to Chess Game !!", True, titleColor)

        # Get text size and center
        titleRect = titleText.get_rect(center=(WIDTH // 2, HEIGHT // 5))

        # Minimal padding for the background box
        paddingX, paddingY = 6, 3  # Small padding

        # Create the background box tightly around the text
        backgroundRect = titleRect.inflate(paddingX * 2, paddingY * 2)

        # Draw the outline (slightly larger than the background)
        outlineThickness = 2  # Small outline
        outlineRect = backgroundRect.inflate(outlineThickness * 2, outlineThickness * 2)
        p.draw.rect(self.screen, outlineColor, outlineRect, border_radius=8)

        # Draw the background box
        p.draw.rect(self.screen, backgroundColor, backgroundRect, border_radius=6)

        # Blit the text onto the screen
        self.screen.blit(titleText, titleRect)

    def showStartWindow(self):
        font = p.font.SysFont("Helvetica", 32, True, False)
        buttonFont = p.font.SysFont("Helvetica", 26, True, False)
        
        
    # Create gradient background
        gradient = p.Surface((WIDTH + SIDEBAR_WIDTH, HEIGHT))
        for y in range(HEIGHT):
            color = ("#F5F5DC")  # Dark blue gradient
            p.draw.line(gradient, color, (0, y), (WIDTH + SIDEBAR_WIDTH, y))
        self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        self.screen.blit(self.sidebarImage, (WIDTH, 0))

        self.drawTitle()

    # Define button rectangles with proper spacing
        buttonWidth, buttonHeight = 270, 60  # Fixed button sizes
        vsPlayerButton = p.Rect(WIDTH // 2 - buttonWidth // 2, HEIGHT // 2 - 80, buttonWidth, buttonHeight)
        vsComputerButton = p.Rect(WIDTH // 2 - buttonWidth // 2, HEIGHT // 2 + 10, buttonWidth, buttonHeight)

    # Draw buttons with borders and frames
        p.draw.rect(self.screen, p.Color("#C9B79C"), vsPlayerButton, border_radius=10)
        p.draw.rect(self.screen, p.Color("#A88C6B"), vsPlayerButton, 3, border_radius=10)  # White border

        p.draw.rect(self.screen, p.Color("#C9B79C"), vsComputerButton, border_radius=10)
        p.draw.rect(self.screen, p.Color("#A88C6B"), vsComputerButton, 3, border_radius=10)  # White border

    # Button Text (centered inside buttons)
        vsPlayerText = buttonFont.render("Player vs Player", True, p.Color("#4B3621"))
        vsComputerText = buttonFont.render("Player vs Computer", True, p.Color("#4B3621"))

        self.screen.blit(vsPlayerText, vsPlayerText.get_rect(center=vsPlayerButton.center))
        self.screen.blit(vsComputerText, vsComputerText.get_rect(center=vsComputerButton.center))

    # Update display
        p.display.flip()

    # Handle user input for button clicks
        waiting = True
        while waiting:
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    exit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if vsPlayerButton.collidepoint(location):
                        color = self.showColorChoiceWindow()  # Correctly get color as string
                        return True, True, color, None
                    elif vsComputerButton.collidepoint(location):
                        color = self.showColorChoiceWindow()  # Correctly get color as string
                        difficulty = self.showDifficultyChoiceWindow()
                        return False, True, color, difficulty

    def showColorChoiceWindow(self):
        # Colors
        textColor = p.Color("#4B3621")  # Dark brown text
        backgroundColor = p.Color("#F5F5DC")  # Beige background
        outlineColor = p.Color("#4B3621")  # Dark brown outline
        buttonColor = p.Color("#4F3926")  # Button background
        buttonTextColor = p.Color("#F1E6D1")  # Button text

        # Load background image
        self.screen.blit(BACKGROUND_IMAGE, (0, 0))
        self.screen.blit(self.sidebarImage, (WIDTH, 0))

        # Render title text
        font = p.font.SysFont("Helvetica", 36, True, False)
        titleText = font.render("Choose Your Color!", True, textColor)

        # Calculate centered text rect
        titleRect = titleText.get_rect(center=(WIDTH // 2, HEIGHT // 4))

        # Create background and outline rectangles for the text
        paddingX, paddingY = 10, 6  # Small padding for the background box
        backgroundRect = titleRect.inflate(paddingX * 2, paddingY * 2)
        outlineRect = backgroundRect.inflate(4, 4)

        # Draw the outline and background
        p.draw.rect(self.screen, outlineColor, outlineRect, border_radius=8)
        p.draw.rect(self.screen, backgroundColor, backgroundRect, border_radius=6)

        # Blit the text
        self.screen.blit(titleText, titleRect)

        # Draw the color selection buttons
        whiteButton = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        blackButton = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

        p.draw.rect(self.screen, buttonColor, whiteButton, border_radius=10)
        p.draw.rect(self.screen, buttonColor, blackButton, border_radius=10)

        # Render and draw button texts
        whiteText = font.render("White", True, buttonTextColor)
        blackText = font.render("Black", True, buttonTextColor)
        self.screen.blit(whiteText, whiteButton.move(50, 7))
        self.screen.blit(blackText, blackButton.move(50, 7))

        # Update the display
        p.display.flip()

        # Wait for user input
        waiting = True
        while waiting:
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    exit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if whiteButton.collidepoint(location):
                        return "white"  # Return color as a string
                    elif blackButton.collidepoint(location):
                        return "black"  # Return color as a string

    def showPromotionChoices(self, isWhite):
        font = p.font.SysFont("Helvetica", 24, True, False)
        promotionRect = p.Rect(WIDTH + 10, HEIGHT // 2 - 100, 180, 200)
        p.draw.rect(self.screen, p.Color("#F5F5DC"), promotionRect)
        
        titleText = font.render("Promote to:", 0, p.Color("Black"))
        self.screen.blit(titleText, promotionRect.move(10, 10))
        
        pieces = ["Q", "R", "N", "B"]
        pieceImages = ["wQ", "wR", "wN", "wB"] if isWhite else ["bQ", "bR", "bN", "bB"]
        buttons = []
        for i, piece in enumerate(pieces):
            button = p.Rect(WIDTH + 20, HEIGHT // 2 - 50 + i * 40, 160, 30)
            p.draw.rect(self.screen, p.Color("#F5F5DC"), button, border_radius=5)
            pieceImage = p.transform.scale(IMAGES[pieceImages[i]], (30, 30))
            self.screen.blit(pieceImage, button.move(10, 0))
            pieceText = font.render(piece, 0, p.Color("black"))
            self.screen.blit(pieceText, button.move(50, 0))
            buttons.append((button, piece))
        
        p.display.flip()
        
        waiting = True
        while waiting:
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    exit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    for button, piece in buttons:
                        if button.collidepoint(location):
                            return piece

if __name__ == "__main__":
    game = ChessGame()
    game.initializeGame()
    game.mainLoop()