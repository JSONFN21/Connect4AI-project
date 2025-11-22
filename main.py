import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout, QVBoxLayout, QSizePolicy

# Used for AI (From Class)
import utils
# testing purposes
import random

ROWS = 6
COLS = 7
disks_size = 60

class Connect4Game(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect 4")
        self.setGeometry(100, 100, 400, 200) # x, y, width, height
        
        # ==================== Main Widget ====================
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: blue")
        self.setCentralWidget(main_widget)

        # ==================== Grid Layout (The Board) ====================
        self.main_layout = QGridLayout()
        main_widget.setLayout(self.main_layout)

        # Initial
        self.board = np.zeros((ROWS, COLS), dtype=int) # Makes a 2D array of the board
        self.buttons = []
        self.current_player = 1
        self.game_over = False

        self.init_GUI()

    # ==================== Initiate The Game Board ====================
    def init_GUI(self):
        for row in range(ROWS):
            row_buttons = []
            for col in range(COLS):
                button = QPushButton(f"")
                button.setFixedSize(disks_size, disks_size) # Fixed disk/button size
                button.setStyleSheet(F"background-color: white; border-radius: {disks_size/2}px;") # Styles the button
                button.clicked.connect(lambda _, r=row, c=col: self.handle_click(r, c)) # Button clicks are processed through handle_click
                
                self.main_layout.addWidget(button, row, col) # Adds the button to board
                row_buttons.append(button)
            self.buttons.append(row_buttons)

    # ==================== Checks Button Clicks ====================
    def handle_click(self, row, col):
        # Checks "Game End Condition" before the next player can move
        if self.game_over:
            return
        
        # Checks the last row first (e.g. 6 5 4 3 2 1)
        for r in reversed(range(ROWS)):
            if self.board[r][col] == 0:
                # Checks current player in play and switches color of tile
                if self.current_player == 1:
                    color = "red"
                else:
                    color = "yellow"

                # Updates the tile color to that of the player (GUI part)
                self.buttons[r][col].setStyleSheet(f"background-color: {color}; border-radius: {disks_size/2}px;")
                # Updates the board on who got the tile
                self.board[r][col] = self.current_player
                

                # Switch current player in play to another
                if self.current_player == 1:
                    self.current_player = 2
                    # self.against_AI(row, col) # Used to play with AI
                else:
                    self.current_player = 1                    

                break
        return


    # ==================== Game End Condition ====================
    # After the player finishes the turn, check if there is a connect 4
    # If there is, self.game_over = True and the game ends
    def check_win(self):


        # self.game_over = True
        pass

    def check_draw(self):
        # Needs to check if board is full and that there is not connect 4
        if (self.board == 0).any():
            print("test")

            # set self.game_over = True

    # ==================== Artificial Intelligence ====================
    def against_AI(self, row, col):
        pass


# ==================== Runs the Game ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Connect4Game()
    game.show()
    sys.exit(app.exec())