import random
import numpy as np

ROWS = 6
COLS = 7

def get_move(board):
    """
    Level 2: Greedy Heuristic AI (1-ply lookahead)
    """
    # Finding all valid columns
    available_cols = [c for c in range(COLS) if board[0][c] == 0]
    
    if not available_cols:
        return None

    best_score = -float("inf")
    chosen_col = random.choice(available_cols)

    for col in available_cols:
        # Simulate the AI's move
        sim_board = dropping(board, col, 2) # Assuming AI is player 2
        # Evaluate the board
        score = score_board(sim_board, ai=2)

        # Finding the most optimal move
        if score > best_score:
            best_score = score
            chosen_col = col
            
    return chosen_col

def dropping(board, col, player):
    temp_board = board.copy()
    # Loop from bottom row -> up
    for r in reversed(range(ROWS)):
        if temp_board[r][col] == 0:
            temp_board[r][col] = player
            return temp_board
    return temp_board

def Simple_Heuristic(window, ai):
    # Opponent identity
    if ai == 2:
        opponent = 1
    else:
        opponent = 2

    score = 0
    
    # Count pieces
    ai_count = np.count_nonzero(window == ai)
    op_count = np.count_nonzero(window == opponent)
    empty_count = np.count_nonzero(window == 0)

    # Reward patterns
    if ai_count == 4:
        score += 500
    elif ai_count == 3 and empty_count == 1:
        score += 6
    elif ai_count == 2 and empty_count == 2:
        score += 1
    
    # Block opponent
    if op_count == 3 and empty_count == 1:
        score -= 10

    return score

def score_board(b, ai=2):
    score = 0
    
    # Center column preference
    center_array = [i for i in list(b[:, COLS//2])]
    center_count = center_array.count(ai)
    score += center_count * 3

    # Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(b[r,:])]
        for c in range(COLS-3):
            window = np.array(row_array[c:c+4])
            score += Simple_Heuristic(window, ai)

    # Vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(b[:,c])]
        for r in range(ROWS-3):
            window = np.array(col_array[r:r+4])
            score += Simple_Heuristic(window, ai)

    # Positive Diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = np.array([b[r+i][c+i] for i in range(4)])
            score += Simple_Heuristic(window, ai)

    # Negative Diagonal
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = np.array([b[r+3-i][c+i] for i in range(4)])
            score += Simple_Heuristic(window, ai)

    return score
