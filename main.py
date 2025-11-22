import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout, QVBoxLayout, QSizePolicy

# Used for AI (Random Move)
import random
# Used for AI (More Advanced Levels)
import utils


ROWS = 6 # of rows
COLS = 7 # of columns
disks_size = 60 # Size of the disks/buttons

class Connect4Game(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect 4")
        self.setGeometry(200, 200, 400, 200) # x, y, width, height

        # ==================== Start Screen ====================
        self.start_frame = QWidget()
        self.setCentralWidget(self.start_frame)

        self.start_layout = QVBoxLayout()
        self.start_frame.setLayout(self.start_layout)

        self.start_label = QLabel("Welcome to Connect 4!", self)
        self.start_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.start_label.setStyleSheet("font-size: 24px;")
        self.start_layout.addWidget(self.start_label)

        # ==================== Mode Selection Buttons ====================
        # Player vs Player Button
        self.pvp_button = QPushButton("PvP", self)
        self.pvp_button.clicked.connect(lambda: self.select_mode("PVP"))
        self.start_layout.addWidget(self.pvp_button)

        # Player vs Environment Button
        self.pve_button = QPushButton("PvE", self)
        self.pve_button.clicked.connect(lambda: self.select_mode("PVE"))
        self.start_layout.addWidget(self.pve_button)

    # ==================== Mode Selection ====================
    def select_mode(self, selected_mode):
        self.mode = selected_mode
        if self.mode == "PVP":
            self.show_game_screen()
        elif self.mode == "PVE":
            self.select_difficulty()

    # ==================== Difficulty Selection ====================
    def select_difficulty(self):
        # Clear previous layout
        for i in reversed(range(self.start_layout.count())): 
            self.start_layout.itemAt(i).widget().setParent(None)

        self.difficulty_label = QLabel("Select Difficulty Level:", self)
        self.difficulty_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.difficulty_label.setStyleSheet("font-size: 24px;")
        self.start_layout.addWidget(self.difficulty_label)

        # Difficulty Buttons
        difficulty_levels = ["Easy", "Medium", "Hard", "Impossible"]
        for level in difficulty_levels:
            button = QPushButton(level, self)
            button.clicked.connect(lambda _, l=level: self.set_difficulty(l))
            self.start_layout.addWidget(button)

    # ==================== Set Difficulty ====================
    def set_difficulty(self, level):
        print("Selected Difficulty:", level)
        self.level = level
        self.show_game_screen()

    # ==================== Game Screen ====================
    def show_game_screen(self):
        self.start_frame.hide()  # Hide start screen
        # ==================== Main Widget ====================
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: blue")
        self.setCentralWidget(main_widget)

        # ==================== Grid Layout (The Board) ====================
        self.main_layout = QGridLayout()
        main_widget.setLayout(self.main_layout)

        # Initial Board Setup
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

    # ==================== Check Button Clicks ====================
    def handle_click(self, row, col):
        # Checks "Game End Condition" before the next player can move
        if self.game_over:
            return
        
        # Checks in reverse, so lasts row first (e.g. 6 5 4 3 2 1)
        for r in reversed(range(ROWS)):
            # If a tile is already occupied, when clicked, it will skip to the next row
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

                # After the player finishes the turn, check for win or draw
                if self.check_win():
                    self.game_over = True
                    print(f"Player {self.current_player} wins!")
                    return
                if self.check_draw():
                    self.game_over = True
                    print("It's a draw!")
                    return
                
                # Switch current player in play to another
                if self.current_player == 1:
                    # Player vs Player
                    if self.mode == "PVP":
                        self.current_player = 2

                    # Player vs Environment (AI)
                    elif self.mode == "PVE":
                        print("AI's Turn")
                        self.current_player = 2
                        match self.level:
                            case "Easy":
                                self.level_easy()
                            case "Medium":
                                self.level_medium()
                            case "Hard":
                                self.level_hard()
                            case "Impossible":
                                self.level_impossible()

                else:
                    self.current_player = 1                    
                break
        return

    # ==================== Game End Condition ====================
    # After the player finishes the turn, check if there is a connect 4
    # If there is, self.game_over = True and the game ends

    # ==================== Check Win Condition (Goal Test) ====================
    def check_win(self):
        # Needs to check all win conditions (horizontal, vertical, diagonal)
        board = self.board

        # Horizontal Check
        for r in range(ROWS):
            for c in range(COLS - 3):
                if board[r][c] != 0 and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                    return True
        
        # Vertical Check
        for r in range(ROWS - 3):
            for c in range(COLS):
                if board[r][c] != 0 and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                    return True
  
        # Diagonal Check (/)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if board[r][c] != 0 and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                    return True
        
        # Diagonal Check (\)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if board[r][c] != 0 and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                    return True

    # ==================== Check Draw Condition ====================
    def check_draw(self):
        # Needs to check if board is full (without any connect 4)
        if not (self.board == 0).any():
            return True
        return False

    # ==================== Artificial Intelligence ====================
    # Random Move
    def level_easy(self):
        # AI selects a random available column
        available_cols = [c for c in range(COLS) if self.board[0][c] == 0]
        # If there are available columns, choose one randomly
        if available_cols:
            # Choose a random column from available columns for AI move
            chosen_col = random.choice(available_cols)
            # Place the disk in the chosen column
            for r in reversed(range(ROWS)):
                if self.board[r][chosen_col] == 0:
                    color = "yellow"
                    self.buttons[r][chosen_col].setStyleSheet(f"background-color: {color}; border-radius: {disks_size/2}px;")
                    self.board[r][chosen_col] = self.current_player

                    # After AI finishes the turn, check for win or draw
                    if self.check_win():
                        self.game_over = True
                        print(f"Player {self.current_player} wins!")
                        return
                    if self.check_draw():
                        self.game_over = True
                        print("It's a draw!")
                        return
                    
                    # Switch back to player 1
                    self.current_player = 1
                    break
    
    # TODO: Implement more advanced AI levels
    def level_medium(self):
        pass

    def level_hard(self):
        pass

    def level_impossible(self):
        pass

    def prune(self):
        pass

    def heuristic(self):
        pass


# ==================== Runs the Game ====================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Connect4Game()
    game.show()
    sys.exit(app.exec())