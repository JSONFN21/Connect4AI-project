import numpy as np
import math
import random

class Level3:
    """
    Level 3 AI: Minimax with alpha-beta pruning
    """

    def __init__(self, player_piece=2, max_depth=5):
        # Player pieces
        self.player_piece = player_piece
        self.opponent_piece = 1 if player_piece == 2 else 2

        # Search depth: how far ahead the AI looks in the minimax tree
        self.max_depth = max_depth

        # Board size
        self.ROWS = 6
        self.COLS = 7

        # Scoring weights: Win > (3 in row) > (2 in row) > (center pieces)
        self.SCORE_4 = 1000000
        self.SCORE_3 = 1000
        self.SCORE_2 = 10
        self.CENTER_BONUS = 3

    # ----------------------------------------------------------
    # PUBLIC METHOD CALLED BY GAME
    # ----------------------------------------------------------
    def get_move(self, board):
        """Return the best column using minimax."""

        # gets columns that don't already contain a token
        valid_cols = self.get_valid_columns(board)
        if not valid_cols:
            return None

        # start score at infinity 
        best_score = -math.inf
        # best column starts at the first vaild column
        best_col = valid_cols[0]

        # loop through all valid columns   
        for col in valid_cols:
            # test dropping a token 
            temp = board.copy()
            row = self.get_next_open_row(temp, col)
            temp[row][col] = self.player_piece

            score = self.minimax(
                temp,                          # current simluated board 
                depth=self.max_depth - 1,      
                is_maximizing=False,           # ai already dropped a token, human is now the minimizing player
                alpha=-math.inf,               # alpha = -∞ , beta = ∞
                beta=math.inf
            )

            if score > best_score:             # return the best move (highest score)
                best_score = score
                best_col = col

        return best_col

    # ----------------------------------------------------------
    # MINIMAX + ALPHA-BETA
    # ----------------------------------------------------------
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        # columns that do not contain tokens
        valid_cols = self.get_valid_columns(board)
        # true if game is over, false otherwise
        terminal = self.is_terminal_node(board)

        # stop search if reached max depth or game is over 
        if depth == 0 or terminal:
            if terminal:
                if self.check_win(board, self.player_piece):
                    return self.SCORE_4 # ai wins
                if self.check_win(board, self.opponent_piece):
                    return -self.SCORE_4 # human wins 
                return 0  # draw
            return self.evaluate_board(board) # no one wins, use heuristic

        # AI turn
        if is_maximizing:
            max_eval = -math.inf
            # drop token in open spots
            for col in valid_cols:
                child = board.copy()
                r = self.get_next_open_row(child, col)
                child[r][col] = self.player_piece
                # get maximum score
                eval_score = self.minimax(child, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval_score)
                # update alpha, prune if needed 
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval

        # Human turn
        else:
            min_eval = math.inf
            for col in valid_cols:
                child = board.copy()
                r = self.get_next_open_row(child, col)
                child[r][col] = self.opponent_piece
                # human wants to minimize
                eval_score = self.minimax(child, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval_score)

                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    # ----------------------------------------------------------
    # BOARD EVALUATION: USE WHEN MINIMAX REACHES DEPTH LIMIT 
    # ----------------------------------------------------------
    def evaluate_board(self, board):
        score = 0

        # adds center bonus to score 
        center = board[:, self.COLS // 2]
        score += (np.sum(center == self.player_piece) -
                  np.sum(center == self.opponent_piece)) * self.CENTER_BONUS

        # window = group of 4 tokens, AI examines every possible window
        score += self.evaluate_all_windows(board)
        return score

    def evaluate_all_windows(self, board):
        total = 0

        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                total += self.evaluate_window(board[r, c:c+4])

        # Vertical
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                total += self.evaluate_window(board[r:r+4, c])

        # Positive diagonals
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                total += self.evaluate_window([board[r+i][c+i] for i in range(4)])

        # Negative diagonals
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                total += self.evaluate_window([board[r-i][c+i] for i in range(4)])

        return total



    def evaluate_window(self, window):
        # counts how many tokens are present in a group of 4 : ex: [2,0,2,2] = 3
        window = np.array(window)
        ai = np.sum(window == self.player_piece)
        op = np.sum(window == self.opponent_piece)
        empty = np.sum(window == 0)

        # four tokens in a row
        if ai == 4:
            return self.SCORE_4
        if op == 4:
            return -self.SCORE_4

        # three tokens in a row 
        if ai == 3 and empty == 1:
            return self.SCORE_3
        if op == 3 and empty == 1:
            return -self.SCORE_3 * 1.1

        # two tokens in a row 
        if ai == 2 and empty == 2:
            return self.SCORE_2
        if op == 2 and empty == 2:
            return -self.SCORE_2

        return 0


    # ----------------------------------------------------------
    # BOARD UTILITIES
    # ----------------------------------------------------------
    def get_valid_columns(self, board):
        # if the top cell of that column is empty, it's valid 
        return [c for c in range(self.COLS) if board[0][c] == 0]

    def get_next_open_row(self, board, col):
        # token falls to the lowest empty space 
        for r in range(self.ROWS - 1, -1, -1):
            if board[r][col] == 0:
                return r
        return -1

    def check_win(self, board, piece):
        ROWS = self.ROWS
        COLS = self.COLS

        # ----- Horizontal -----
        for r in range(ROWS):
            for c in range(COLS - 3):
                if (board[r][c]     == piece and
                    board[r][c+1]   == piece and
                    board[r][c+2]   == piece and
                    board[r][c+3]   == piece):
                    return True

        # ----- Vertical -----
        for r in range(ROWS - 3):
            for c in range(COLS):
                if (board[r][c]     == piece and
                    board[r+1][c]   == piece and
                    board[r+2][c]   == piece and
                    board[r+3][c]   == piece):
                    return True

        # ----- Diagonal Down-Right (/ shape) -----
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if (board[r][c]       == piece and
                    board[r+1][c+1]   == piece and
                    board[r+2][c+2]   == piece and
                    board[r+3][c+3]   == piece):
                    return True

        # ----- Diagonal Up-Right (\ shape) -----
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if (board[r][c]       == piece and
                    board[r-1][c+1]   == piece and
                    board[r-2][c+2]   == piece and
                    board[r-3][c+3]   == piece):
                    return True

        return False


    def is_terminal_node(self, board):
        # win, lose, or draw 
        return (
            self.check_win(board, self.player_piece) or
            self.check_win(board, self.opponent_piece) or
            len(self.get_valid_columns(board)) == 0
        )
