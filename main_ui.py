import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QSizePolicy
from PyQt6.QtCore import Qt, QTimer

import level1
import level2
import level3
import level4

ROWS = 6
COLS = 7
disks_size = 60

class Connect4Game(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect 4")
        self.setGeometry(100, 100, 600, 850)
        
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("background-color: #2c3e50; font-family: 'Segoe UI', sans-serif;")
        self.setCentralWidget(self.main_widget)
        
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.status_label = QLabel("Welcome to Connect 4")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; padding: 20px; background-color: #34495e; border-radius: 10px; margin-bottom: 10px;")
        self.layout.addWidget(self.status_label)

        control_panel = QWidget()
        control_panel.setStyleSheet("background-color: #34495e; border-radius: 10px; padding: 10px;")
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)

        mode_layout = QHBoxLayout()
        mode_label = QLabel("Game Mode:")
        mode_label.setStyleSheet("color: #ecf0f1; font-weight: bold; font-size: 16px;")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Human vs AI", "Human vs Human", "AI vs AI"])
        self.mode_combo.setStyleSheet("QComboBox { background-color: white; color: #2c3e50; padding: 5px; border-radius: 5px; font-size: 14px; } QComboBox::drop-down { border: 0px; }")
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        control_layout.addLayout(mode_layout)

        self.diff_widget = QWidget()
        self.diff_layout = QVBoxLayout(self.diff_widget)
        self.diff_layout.setContentsMargins(0, 0, 0, 0)
        
        self.pve_diff_combo = QComboBox()
        self.pve_diff_combo.addItems(["Level 1: Random", "Level 2: Greedy", "Level 3: Minimax", "Level 4: Impossible"])
        self.pve_diff_combo.setStyleSheet(self.mode_combo.styleSheet())
        self.pve_label = QLabel("AI Difficulty:")
        self.pve_label.setStyleSheet(mode_label.styleSheet())
        
        self.ai1_combo = QComboBox()
        self.ai1_combo.addItems(["Level 1: Random", "Level 2: Greedy", "Level 3: Minimax", "Level 4: Impossible"])
        self.ai1_combo.setStyleSheet(self.mode_combo.styleSheet())
        self.ai2_combo = QComboBox()
        self.ai2_combo.addItems(["Level 1: Random", "Level 2: Greedy", "Level 3: Minimax", "Level 4: Impossible"])
        self.ai2_combo.setStyleSheet(self.mode_combo.styleSheet())
        
        self.ai1_label = QLabel("Red AI (P1):")
        self.ai1_label.setStyleSheet(mode_label.styleSheet())
        self.ai2_label = QLabel("Yellow AI (P2):")
        self.ai2_label.setStyleSheet(mode_label.styleSheet())

        control_layout.addWidget(self.diff_widget)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Game")
        self.start_btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px; font-weight: bold; border-radius: 5px; font-size: 16px;")
        self.start_btn.clicked.connect(self.start_game)
        
        self.stop_btn = QPushButton("Stop Game")
        self.stop_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; font-weight: bold; border-radius: 5px; font-size: 16px;")
        self.stop_btn.clicked.connect(self.stop_game)
        self.stop_btn.setVisible(False)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        control_layout.addLayout(btn_layout)

        action_layout = QHBoxLayout()
        self.undo_btn = QPushButton("Undo Move")
        self.undo_btn.setStyleSheet("background-color: #f39c12; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.undo_btn.clicked.connect(self.undo_move)
        self.undo_btn.setEnabled(False)
        
        self.hint_level_combo = QComboBox()
        self.hint_level_combo.addItems(["Level 1", "Level 2", "Level 3", "Level 4"])
        self.hint_level_combo.setStyleSheet(self.mode_combo.styleSheet())
        
        self.hint_btn = QPushButton("Get Hint")
        self.hint_btn.setStyleSheet("background-color: #9b59b6; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.hint_btn.clicked.connect(self.show_hint)
        self.hint_btn.setEnabled(False)
        
        action_layout.addWidget(self.undo_btn)
        action_layout.addWidget(self.hint_btn)
        action_layout.addWidget(self.hint_level_combo)
        
        self.hint_level_combo.setFixedWidth(80)
        
        control_layout.addLayout(action_layout)

        self.layout.addWidget(control_panel)

        self.board_container = QWidget()
        self.board_container.setStyleSheet("background-color: #2980b9; border-radius: 15px; margin-top: 10px;")
        self.board_layout = QGridLayout()
        self.board_layout.setContentsMargins(20, 20, 20, 20)
        self.board_layout.setSpacing(10)
        self.board_container.setLayout(self.board_layout)
        self.layout.addWidget(self.board_container)

        self.buttons = []
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.game_active = False
        self.game_over = False
        self.current_player = 1
        self.history = []
        
        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.ai_move_step)
        
        self.init_GUI()
        self.mode_combo.currentIndexChanged.connect(self.update_controls)
        self.update_controls()

        self.level3_ai = level3.Level3(player_piece=2)

    def resizeEvent(self, event):
        if hasattr(self, 'overlay') and hasattr(self, 'board_container'):
            self.overlay.resize(self.board_container.size())
        super().resizeEvent(event)

    def init_GUI(self):
        for r in range(ROWS):
            row_btns = []
            for c in range(COLS):
                btn = QPushButton()
                btn.setFixedSize(disks_size, disks_size)
                btn.setStyleSheet(f"QPushButton {{ background-color: white; border: 2px solid #1abc9c; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")
                # each button represents a cell, when clicked we figure out which column it belongs to
                btn.clicked.connect(lambda _, r=r, c=c: self.handle_click(r, c))
                self.board_layout.addWidget(btn, r, c)
                row_btns.append(btn)
            self.buttons.append(row_btns)

    def update_controls(self):
        for i in reversed(range(self.diff_layout.count())): 
            self.diff_layout.itemAt(i).widget().setParent(None)
            
        mode = self.mode_combo.currentIndex()
        if mode == 0:
            self.diff_layout.addWidget(self.pve_label)
            self.diff_layout.addWidget(self.pve_diff_combo)
        elif mode == 2:
            self.diff_layout.addWidget(self.ai1_label)
            self.diff_layout.addWidget(self.ai1_combo)
            self.diff_layout.addWidget(self.ai2_label)
            self.diff_layout.addWidget(self.ai2_combo)

    def start_game(self):
        # reset board and state when a new game starts
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.game_active = True
        self.game_over = False
        self.current_player = 1
        self.history = []
        self.reset_visuals()
        
        self.start_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.mode_combo.setEnabled(False)
        
        mode = self.mode_combo.currentIndex()
        if mode == 2:
            # ai vs ai mode: user can't undo or ask for hints, timer drives the game
            self.undo_btn.setEnabled(False)
            self.hint_btn.setEnabled(False)
            self.hint_level_combo.setEnabled(False)
            self.ai_timer.start(1000)
        else:
            self.undo_btn.setEnabled(True)
            self.hint_btn.setEnabled(True)
            self.hint_level_combo.setEnabled(True)
        
        self.update_status("Game Started! Red's Turn")

    def stop_game(self):
        # stop game and let user configure a new one
        self.game_active = False
        self.ai_timer.stop()
        self.start_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.mode_combo.setEnabled(True)
        self.undo_btn.setEnabled(False)
        self.hint_btn.setEnabled(False)
        self.hint_level_combo.setEnabled(True)
        self.update_status("Game Stopped")

    def reset_visuals(self):
        # put all discs back to empty white circles
        for r in range(ROWS):
            for c in range(COLS):
                self.buttons[r][c].setStyleSheet(f"QPushButton {{ background-color: white; border: 2px solid #1abc9c; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")

    def update_status(self, text):
        self.status_label.setText(text)

    def handle_click(self, r, c):
        # user clicked somewhere on the board, we mainly care about the column
        if not self.game_active or self.game_over:
            return
        
        mode = self.mode_combo.currentIndex()
        # ignore clicks during ai vs ai
        if mode == 2:
            return
        # in human vs ai, ignore clicks when it's ai's turn
        if mode == 0 and self.current_player == 2:
            return

        self.attempt_move(c)

    def attempt_move(self, col):
        # if top cell is not empty, column is full
        if self.board[0][col] != 0:
            return

        # find the lowest empty cell in this column
        row = -1
        for r in reversed(range(ROWS)):
            if self.board[r][col] == 0:
                row = r
                break
        
        self.make_move(row, col, self.current_player)

    def make_move(self, row, col, player):
        # core "drop disc" logic: update board state and ui, then check for win/draw and switch turn
        self.board[row][col] = player
        self.history.append((row, col, player))
        
        color = "red" if player == 1 else "yellow"
        self.buttons[row][col].setStyleSheet(f"QPushButton {{ background-color: {color}; border: 2px solid #2c3e50; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")
        
        # check if this move ended the game
        if level4.winning_move(self.board, player):
            # highlight the exact 4-in-a-row that won
            winning_positions = self.get_winning_positions(player)
            if winning_positions:
                for (r, c) in winning_positions:
                    self.buttons[r][c].setStyleSheet(f"QPushButton {{ background-color: #2ecc71; border: 4px solid #27ae60; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")
            
            self.game_over = True
            self.game_active = False
            self.ai_timer.stop()
            winner = "Red" if player == 1 else "Yellow"
            self.update_status(f"Game Over: {winner} Wins!")
            QMessageBox.information(self, "Game Over", f"{winner} Wins!")
            self.stop_game()
            return
        
        # if no empty cells left and nobody won, it's a draw
        if not (self.board == 0).any():
            self.game_over = True
            self.game_active = False
            self.ai_timer.stop()
            self.update_status("Game Over: Draw!")
            QMessageBox.information(self, "Game Over", "It's a Draw!")
            self.stop_game()
            return

        # switch current player (1 -> 2, 2 -> 1)
        self.current_player = 3 - self.current_player
        p_name = "Red" if self.current_player == 1 else "Yellow"
        self.update_status(f"{p_name}'s Turn")

        # if human vs ai and it's now ai's turn, schedule ai move
        mode = self.mode_combo.currentIndex()
        if mode == 0 and self.current_player == 2:
            QTimer.singleShot(500, self.ai_move_step)

    def get_winning_positions(self, piece):
        # scan horizontally for 4 in a row
        for c in range(COLS - 3):
            for r in range(ROWS):
                if (self.board[r][c] == piece and self.board[r][c + 1] == piece and self.board[r][c + 2] == piece and self.board[r][c + 3] == piece):
                    return [(r, c), (r, c+1), (r, c+2), (r, c+3)]
        # scan vertically for 4 in a row
        for c in range(COLS):
            for r in range(ROWS - 3):
                if (self.board[r][c] == piece and self.board[r + 1][c] == piece and self.board[r + 2][c] == piece and self.board[r + 3][c] == piece):
                    return [(r, c), (r+1, c), (r+2, c), (r+3, c)]
        # scan positive diagonals (\ direction)
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if (self.board[r][c] == piece and self.board[r + 1][c + 1] == piece and self.board[r + 2][c + 2] == piece and self.board[r + 3][c + 3] == piece):
                    return [(r, c), (r+1, c+1), (r+2, c+2), (r+3, c+3)]
        # scan negative diagonals (/ direction)
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if (self.board[r][c] == piece and self.board[r - 1][c + 1] == piece and self.board[r - 2][c + 2] == piece and self.board[r - 3][c + 3] == piece):
                    return [(r, c), (r-1, c+1), (r-2, c+2), (r-3, c+3)]
        
        return None

    def ai_move_step(self):
        # called either by the timer (ai vs ai) or singleShot (human vs ai)
        if not self.game_active or self.game_over:
            return

        mode = self.mode_combo.currentIndex()
        
        # decide which difficulty to use based on mode and current player
        level_idx = 0
        if mode == 0:
            level_idx = self.pve_diff_combo.currentIndex()
        elif mode == 2:
            if self.current_player == 1:
                level_idx = self.ai1_combo.currentIndex()
            else:
                level_idx = self.ai2_combo.currentIndex()

        col = self.get_ai_move(level_idx, self.current_player)
        
        if col is not None:
            self.attempt_move(col)
        else:
            print("AI returned None move!")

    def get_ai_move(self, level_idx, player):
        # route ai decision to the appropriate "level" implementation
        try:
            if level_idx == 0:
                # level 1: random
                return level1.get_move(self.board)
            elif level_idx == 1:
                # level 2: greedy (hard-coded for piece 2, so flip if needed)
                if player == 1:
                    flipped_board = self.board.copy()
                    flipped_board[self.board == 1] = 2
                    flipped_board[self.board == 2] = 1
                    return level2.get_move(flipped_board)
                else:
                    return level2.get_move(self.board)
            elif level_idx == 2:
                # level 3: minimax with weights
                self.level3_ai.player_piece = player
                self.level3_ai.opponent_piece = 3 - player
                return self.level3_ai.get_move(self.board)
            elif level_idx == 3:
                # level 4: "impossible" mode (also assumes ai is 2, so flip if needed)
                if player == 1:
                    flipped_board = self.board.copy()
                    flipped_board[self.board == 1] = 2
                    flipped_board[self.board == 2] = 1
                    return level4.get_move(flipped_board)
                else:
                    return level4.get_move(self.board)
            return None
        except Exception as e:
            print(f"Error in get_ai_move: {e}")
            return None

    def undo_move(self):
        # undo last move(s) from history
        if not self.history or not self.game_active:
            return
            
        mode = self.mode_combo.currentIndex()
        steps = 1
        # in human vs ai, when it's human's turn we undo both human and ai moves
        if mode == 0 and self.current_player == 1:
            steps = 2
            
        for _ in range(steps):
            if not self.history:
                break
            r, c, p = self.history.pop()
            self.board[r][c] = 0
            self.buttons[r][c].setStyleSheet(f"QPushButton {{ background-color: white; border: 2px solid #1abc9c; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")
            # restore current player to whoever made the undone move
            self.current_player = p
            
        self.update_status(f"Undo! Player {self.current_player}'s Turn")

    def show_hint(self):
        # ask one of the ai levels for a suggested move and temporarily highlight that spot
        if not self.game_active:
            return
        
        self.hint_btn.setText("Thinking...")
        self.hint_btn.setEnabled(False)
        self.hint_level_combo.setEnabled(False)
        QApplication.processEvents()
        
        try:
            level_idx = self.hint_level_combo.currentIndex()
            col = self.get_ai_move(level_idx, self.current_player)
            
            if col is not None:
                # find where the disc would actually land in that column
                row = -1
                for r in reversed(range(ROWS)):
                    if self.board[r][col] == 0:
                        row = r
                        break

                if row != -1:
                    # temporarily paint that cell as a "hint" disc
                    self.buttons[row][col].setStyleSheet(f"QPushButton {{ background-color: #f1c40f; border: 3px dashed black; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")
                    QTimer.singleShot(1000, self.restore_hint_visuals)
            else:
                print("Hint returned None")
                
        except Exception as e:
            print(f"Error showing hint: {e}")
        
        self.hint_btn.setText("Get Hint")
        self.hint_btn.setEnabled(True)
        self.hint_level_combo.setEnabled(True)

    def restore_hint_visuals(self):
        # after hint fades, repaint the board so only real discs remain colored
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == 0:
                    self.buttons[r][c].setStyleSheet(f"QPushButton {{ background-color: white; border: 2px solid #1abc9c; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")
                else:
                    color = "red" if self.board[r][c] == 1 else "yellow"
                    self.buttons[r][c].setStyleSheet(f"QPushButton {{ background-color: {color}; border: 2px solid #2c3e50; border-radius: {disks_size//2}px; min-width: {disks_size}px; max-width: {disks_size}px; min-height: {disks_size}px; max-height: {disks_size}px; padding: 0px; margin: 0px; }}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = Connect4Game()
    game.show()
    sys.exit(app.exec())
