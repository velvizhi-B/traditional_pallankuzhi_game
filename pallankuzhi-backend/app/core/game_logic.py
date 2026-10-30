# ===========================================================
# Pallankuzhi Game Logic Utilities
# ===========================================================
from typing import List, Tuple, Dict


def sow_and_capture(
    board: List[int],
    start_index: int,
    player_turn: int,
    scores: Dict[str, int]
) -> Tuple[List[int], Dict[str, int], bool]:
    """
    Executes a player's move according to Pallankuzhi rules.

    Args:
        board (List[int]): Current state of 14 pits.
        start_index (int): Selected pit index (0–13).
        player_turn (int): 1 or 2, representing current player.
        scores (Dict[str, int]): Current scores {'1': x, '2': y}.

    Returns:
        Tuple[List[int], Dict[str, int], bool]:
            updated_board, updated_scores, game_continues
    """

    # -------------------------------
    # Move validation
    # -------------------------------
    if board[start_index] == 0:
        raise ValueError("Selected pit is empty. Choose a pit with seeds.")

    pits_per_side = len(board) // 2
    if player_turn == 1 and not (0 <= start_index < pits_per_side):
        raise ValueError("Player 1 can only select pits 0–6.")
    if player_turn == 2 and not (pits_per_side <= start_index < len(board)):
        raise ValueError("Player 2 can only select pits 7–13.")

    # -------------------------------
    # Initial sowing setup
    # -------------------------------
    seeds_in_hand = board[start_index]
    board[start_index] = 0
    index = start_index

    # -------------------------------
    # Main sowing loop
    # -------------------------------
    while True:
        # Sow seeds counter-clockwise
        while seeds_in_hand > 0:
            index = (index + 1) % len(board)
            board[index] += 1
            seeds_in_hand -= 1

            # ==========================================
            # NEW RULE: Bonus capture if pit reaches 4
            # ==========================================
            if board[index] == 4:
                if index < len(board) // 2:
                    scores["1"] += 4
                else:
                    scores["2"] += 4

                board[index] = 0  # Empty the pit after capture

        # Determine next pits for checking
        next_index = (index + 1) % len(board)
        next_next_index = (index + 2) % len(board)

        # -------------------------------
        # Rule 1: Two consecutive empty pits → turn ends, no points
        # -------------------------------
        if board[next_index] == 0 and board[next_next_index] == 0:
            return board, scores, False

        # -------------------------------
        # Rule 2: Next pit empty → capture next-to-empty pit seeds
        # -------------------------------
        elif board[next_index] == 0:
            score_gain = board[next_next_index]
            board[next_next_index] = 0
            scores[str(player_turn)] += score_gain
            return board, scores, False

        # -------------------------------
        # Rule 3: Continue sowing from next pit
        # -------------------------------
        else:
            seeds_in_hand = board[next_index]
            board[next_index] = 0
            index = next_index


def check_game_over(board: List[int], scores: Dict[str, int]) -> Tuple[bool, Dict[str, int]]:
    """
    Checks if one side is empty and assigns remaining seeds
    to the opponent as per Pallankuzhi end-game rules.
    """
    pits_per_side = len(board) // 2
    side1_empty = all(seed_count == 0 for seed_count in board[:pits_per_side])
    side2_empty = all(seed_count == 0 for seed_count in board[pits_per_side:])

    if side1_empty or side2_empty:
        if side1_empty:
            scores["2"] += sum(board[pits_per_side:])
        if side2_empty:
            scores["1"] += sum(board[:pits_per_side])
        board[:] = [0] * len(board)
        return True, scores

    return False, scores


def get_winner(scores: Dict[str, int]) -> str:
    """
    Determines the winner based on final scores.
    """
    if scores["1"] > scores["2"]:
        return "1"
    elif scores["2"] > scores["1"]:
        return "2"
    else:
        return "Draw"