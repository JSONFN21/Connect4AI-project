"""
tiny ga trainer for the connect 4 ai.

idea:
- we keep a bunch of weight sets (population).
- they play games against each other and sometimes against level 3.
- we score them, keep the good ones, mix/mutate them, and repeat.
- every now and then, if one looks strong enough, we save it to evolved_weights.json.
"""

import random
import numpy as np
import json
import math
import multiprocessing
import os
from level3 import Level3
from level4 import ( minimax, winning_move, get_valid_locations, drop_piece, remove_piece, is_valid_location, get_next_open_row, ROWS, COLS, EMPTY, PLAYER_PIECE, AI_PIECE)

# basic ga + search settings
POPULATION_SIZE = 20
GENERATIONS = 30
TRAINING_DEPTH = 5
VALIDATION_DEPTH = 5
GAMES_PER_GENOME = 3
ELITE_COUNT = 6

def choose_move_with_weights(board, current_player, depth, weights):
    """
    ask level4.minimax what move to play using a specific weight set.
    if it's player 2's turn, we just call minimax normally.
    if it's player 1's turn, we flip the board so minimax thinks player 1 is "the ai".
    """
    if current_player == AI_PIECE:
        col, _ = minimax(board, depth, -math.inf, math.inf, True, weights)
        return col

    # flip 1 and 2 so "2" is always the side to move from minimax's point of view
    mapped = board.copy()
    temp = 3
    mapped[mapped == PLAYER_PIECE] = temp
    mapped[mapped == AI_PIECE] = PLAYER_PIECE
    mapped[mapped == temp] = AI_PIECE

    col, _ = minimax(mapped, depth, -math.inf, math.inf, True, weights)
    return col

def play_game(w1, w2, w2_is_level3=False, depth=TRAINING_DEPTH, fixed_start=None):
    """
    play a single game of connect 4.
    
    returns:
    - 1  if w1 wins
    - 0  if draw / error
    - -1 if w1 loses
    """
    board = np.zeros((ROWS, COLS), dtype=int)
    # who starts
    turn = random.randint(0, 1) if fixed_start is None else fixed_start
    level3_ai = None
    
    for _ in range(ROWS * COLS):
        current_player = PLAYER_PIECE if turn == 0 else AI_PIECE
        is_w1 = (turn == 0)
        
        # decide move for the current player
        if not is_w1 and w2_is_level3:
            # let level 3 pick the move (only initialize once)
            if level3_ai is None:
                level3_ai = Level3(player_piece=current_player, max_depth=5)
            col = level3_ai.get_move(board)
        else:
            # use ga weights (w1 or w2)
            active_weights = w1 if is_w1 else w2
            col = choose_move_with_weights(board, current_player, depth, active_weights)
            
        # no valid move: treat as draw / weird situation
        if col is None or not is_valid_location(board, col):
            return 0
        
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, current_player)
        
        # someone just won
        if winning_move(board, current_player):
            return 1 if is_w1 else -1
        
        # board is full = draw
        if not any(is_valid_location(board, c) for c in range(COLS)):
            return 0
        
        # swap turns
        turn = 1 - turn
    
    return 0

def play_self_task(args):
    w1, w2, idx, start = args
    return idx, play_game(w1, w2, False, TRAINING_DEPTH, fixed_start=start)

def play_level3_bonus_task(args):
    w, idx, start = args
    res = play_game(w, None, True, TRAINING_DEPTH, fixed_start=start)
    return idx, res

def verify_champion_task(args):
    """
    run a validation game for a candidate:
    - either vs level 3
    - or vs some old champion weights.
    just returns the result of that game.
    """ 
    cand, opp_type, opp_w = args
    if opp_type == 'LEVEL3':
        res = play_game(cand, None, True, VALIDATION_DEPTH)
    else:
        res = play_game(cand, opp_w, False, VALIDATION_DEPTH)
    return res

def mutate(w):
    """
    slightly shake the weights.
    - for the blocking multiplier (index 3) we scale within a tighter range.
    - for the others we randomly scale and cast back to int.
    """
    new_w = []
    for i, g in enumerate(w):
        if i == 3:
            new_val = g * random.uniform(0.9, 1.1)
            new_w.append(max(0.8, min(2.5, new_val)))
        else:
            new_w.append(int(g * random.uniform(0.7, 1.3)))
    return new_w

def crossover(w1, w2):
    """
    simple mix: for each gene, flip a coin to take from parent 1 or parent 2.
    """
    return [w1[i] if random.random() < 0.5 else w2[i] for i in range(len(w1))]

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("AI training...")

    # start population around level 3's weights
    DEFAULT = [1000, 10, 3, 1.1]
    pop = [DEFAULT] + [[int(g * random.uniform(0.5, 2.0)) if i < 3 else g * random.uniform(0.8, 1.5)
                        for i, g in enumerate(DEFAULT)] for _ in range(POPULATION_SIZE - 1)]
    
    # keep a small "hall of fame" list of champions we saved
    champion_history = []
    if os.path.exists("evolved_weights.json"):
        try:
            with open("evolved_weights.json", "r") as f:
                past_champion = json.load(f)
                champion_history.append(past_champion)
        except:
            pass

    for gen in range(GENERATIONS):
        # self-play phase ==================
        tasks = []
        task_map = {}
        idx = 0
        for i in range(POPULATION_SIZE):
            # pick some random opponents for genome i
            opponents = random.sample(range(POPULATION_SIZE), min(GAMES_PER_GENOME, POPULATION_SIZE - 1))
            for opp in opponents:
                if opp == i:
                    continue
                # two games: one where i starts, one where opponent starts
                tasks.append((pop[i], pop[opp], idx, 0))
                task_map[idx] = i
                idx += 1
                tasks.append((pop[i], pop[opp], idx, 1))
                task_map[idx] = i
                idx += 1
        fitness = [0] * POPULATION_SIZE
        
        # run all self-play games in parallel
        with multiprocessing.Pool() as pool:
            for idx, result in pool.imap_unordered(play_self_task, tasks):
                g_idx = task_map[idx]
                # win = +3, draw = +1, loss = -1 (very simple scoring)
                fitness[g_idx] += (3 if result == 1 else 1 if result == 0 else -1)
                
        # level 3 bonus phase ==================
        # take top elite genomes and let them fight level 3
        top_indices = sorted(range(POPULATION_SIZE), key=lambda i: fitness[i], reverse=True)[:ELITE_COUNT]
        l3_tasks = []
        l3_map = {}
        t_idx = 0
        for i in top_indices:
            # two games vs level 3: one starting first, one second
            l3_tasks.append((pop[i], t_idx, 0))
            l3_map[t_idx] = i
            t_idx += 1
            l3_tasks.append((pop[i], t_idx, 1))
            l3_map[t_idx] = i
            t_idx += 1
                
        if l3_tasks:
            with multiprocessing.Pool() as pool:
                for idx, result in pool.imap_unordered(play_level3_bonus_task, l3_tasks):
                    g_idx = l3_map[idx]
                    if result == 1:
                        fitness[g_idx] += 8   # big reward for beating level 3
                    elif result == 0:
                        fitness[g_idx] += 3   # smaller reward for drawing
                    else:
                        fitness[g_idx] -= 12  # heavy penalty for losing
        
        # best genome this generation based on fitness
        best_idx = max(range(POPULATION_SIZE), key=lambda i: fitness[i])
        gen_best = pop[best_idx]

        # gauntlet check ==================
        if gen == GENERATIONS - 1 or gen % 5 == 0:
            challenges = []
            # 4 games vs level 3
            for _ in range(4):
                challenges.append((gen_best, 'LEVEL3', None))
            # a few games vs random past champions (if we have any)
            if champion_history:
                num_to_test = min(3, len(champion_history))
                sampled = random.sample(champion_history, num_to_test)
                for champ in sampled:
                    for _ in range(2):
                        challenges.append((gen_best, 'WEIGHTS', champ))
            
            if challenges:
                with multiprocessing.Pool() as pool:
                    results = pool.map(verify_champion_task, challenges)
                    wins = results.count(1)
                    l3_wins = results[:4].count(1)  # first 4 are vs level 3
                
                win_rate = wins / len(challenges)
                l3_win_rate = l3_wins / 4
                
                # only accept as a new champion if it clearly handles level 3
                if l3_win_rate >= 0.75 and win_rate >= 0.5:
                    with open("evolved_weights.json", "w") as f:
                        json.dump(gen_best, f)
                    
                    if gen_best not in champion_history:
                        champion_history.append(gen_best)

        # evolution step ==================
        # sort population by fitness 
        sorted_pop = [pop[i] for i in sorted(range(POPULATION_SIZE), key=lambda i: fitness[i], reverse=True)]
        new_pop = sorted_pop[:4]  # keep top 4 as is 
        while len(new_pop) < POPULATION_SIZE:
            # pick two decent parents from the better half
            p1 = sorted_pop[random.randint(0, len(sorted_pop) // 2)]
            p2 = sorted_pop[random.randint(0, len(sorted_pop) // 2)]
            child = mutate(crossover(p1, p2))
            new_pop.append(child)
        pop = new_pop
        
    print("Done.")
