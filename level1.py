import random

def get_move(board):
    """
    Level 1: Random AI
    Returns a random valid column.
    """
    ROWS = len(board)
    COLS = len(board[0])
    
    # Get all valid columns (where the top row is empty)
    valid_cols = [c for c in range(COLS) if board[0][c] == 0]
    
    if valid_cols:
        return random.choice(valid_cols)
    return None
