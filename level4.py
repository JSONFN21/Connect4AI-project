"""
connect 4 level 4 ai using minimax with alpha-beta and tunable weights. very similar to level 3 but with a key differences.
   - genetic algorithm to evolve weights which are saved to a json file and used in the ai
"""

import numpy as np
import json
import math
import os

ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

# default weights if nothing evolved yet
DEFAULT_WEIGHTS = [1000, 10, 3, 1.2]

# try to load evolved weights, otherwise fall back to defaults
if os.path.exists("evolved_weights.json"):
    try:
        with open("evolved_weights.json", "r") as f:
            WEIGHTS = json.load(f)
    except:
        WEIGHTS = DEFAULT_WEIGHTS
else:
    WEIGHTS = DEFAULT_WEIGHTS

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def remove_piece(board, row, col):
    board[row][col] = EMPTY

def is_valid_location(board, col):
    return board[0][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None

def winning_move(board, piece):
    # check all directions for 4 in a row for a given piece
    for c in range(COLS - 3):
        for r in range(ROWS):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    for c in range(COLS):
        for r in range(ROWS - 3):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if all(board[r-i][c+i] == piece for i in range(4)):
                return True
    return False

def evaluate_window(window, piece, weights):
    # score a 4-cell window for one side vs the other
    window = np.array(window)
    ai_count = np.sum(window == piece)
    opp_count = np.sum(window == (PLAYER_PIECE if piece == AI_PIECE else AI_PIECE))
    empty_count = np.sum(window == EMPTY)
    
    SCORE_4 = 1000000
    SCORE_3 = weights[0]
    SCORE_2 = weights[1]
    BLOCKING_MULT = weights[3]
    
    if ai_count == 4:
        return SCORE_4
    if opp_count == 4:
        return -SCORE_4
    if ai_count == 3 and empty_count == 1:
        return SCORE_3
    if opp_count == 3 and empty_count == 1:
        return -SCORE_3 * BLOCKING_MULT
    if ai_count == 2 and empty_count == 2:
        return SCORE_2
    if opp_count == 2 and empty_count == 2:
        return -SCORE_2
    return 0

def score_position(board, piece, weights):
    # evaluate how good the full board is for a given piece
    score = 0
    opp = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    
    # small bonus for controlling the center column
    center = board[:, COLS // 2]
    CENTER_BONUS = weights[2]
    score += (np.sum(center == piece) - np.sum(center == opp)) * CENTER_BONUS
    
    # scan all possible 4-cell windows
    for r in range(ROWS):
        for c in range(COLS - 3):
            score += evaluate_window(board[r, c:c+4], piece, weights)
    for r in range(ROWS - 3):
        for c in range(COLS):
            score += evaluate_window(board[r:r+4, c], piece, weights)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            score += evaluate_window([board[r+i][c+i] for i in range(4)], piece, weights)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            score += evaluate_window([board[r-i][c+i] for i in range(4)], piece, weights)
    
    return score

def is_terminal_node(board):
    # game is over if someone wins or there are no valid moves
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    return [c for c in range(COLS) if is_valid_location(board, c)]

def minimax(board, depth, alpha, beta, maximizingPlayer, weights):
    # core minimax search with alpha-beta pruning
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 1000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -1000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE, weights))

    # try center-ish columns first (helps pruning)
    center = COLS // 2
    valid_locations.sort(key=lambda x: abs(x - center))

    if maximizingPlayer:
        value = -math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            new_score = minimax(board, depth - 1, alpha, beta, False, weights)[1]
            remove_piece(board, row, col)
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return (column, value)
    else:
        value = math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, PLAYER_PIECE)
            new_score = minimax(board, depth - 1, alpha, beta, True, weights)[1]
            remove_piece(board, row, col)
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return (column, value)

def get_move(board, depth=5):
    # main entry: pick the best column for the ai
    col, score = minimax(board, depth, -math.inf, math.inf, True, WEIGHTS)
    if col is None:
        valid = get_valid_locations(board)
        if valid:
            return valid[0]
    return col
