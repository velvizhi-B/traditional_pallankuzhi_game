# ===========================================================
# Pallankuzhi Game Rules and Constants
# ===========================================================

"""
This file defines the core constants, player pit mappings, 
and reference rules for Pallankuzhi gameplay.
It serves as a readable guide and utility reference 
for game logic, validation, and testing.
"""

# -------------------------------
# BASIC CONSTANTS
# -------------------------------

TOTAL_PITS = 14          # 7 per player (Player 1 → 0–6, Player 2 → 7–13)
INITIAL_SEEDS = 5        # Each pit starts with 5 seeds

PLAYER_1_SIDE = list(range(0, 7))
PLAYER_2_SIDE = list(range(7, 14))

# -------------------------------
# BONUS RULE CONFIGURATION
# -------------------------------

# Enable / Disable 4-seed capture rule
ENABLE_FOUR_SEED_BONUS = True

# Target seed count for bonus capture
FOUR_SEED_TARGET = 4


# -------------------------------
# GAME STATUS ENUMS (for database)
# -------------------------------
GAME_STATUS_ONGOING = "ongoing"
GAME_STATUS_COMPLETED = "completed"

# -------------------------------
# DEFAULT INITIAL STATE
# -------------------------------
DEFAULT_BOARD_STATE = {"pits": [INITIAL_SEEDS] * TOTAL_PITS}
DEFAULT_SCORES = {"1": 0, "2": 0}


# -------------------------------
# RULES REFERENCE (for documentation or UI)
# -------------------------------
GAME_RULES_TEXT = """
Pallankuzhi Gameplay Rules:

1️⃣ Board Setup:
   - The board has 14 pits (7 on each side).
   - Each pit starts with 5 seeds.

2️⃣ Turns:
   - Player 1 starts from their own side (pits 0–6).
   - Player 2 plays from their side (pits 7–13).

3️⃣ Movement:
   - A player picks all seeds from a pit on their side.
   - Seeds are sown counter-clockwise, one per pit.

4️⃣ Empty Pit Handling:
   - If a chosen pit is empty → take seeds from the next pit to the last-seed-drawn pit and continue.
   - If the hand becomes empty and the next pit is also empty → 
     take seeds from the next-to-empty pit as captured points.
   - If two consecutive pits are empty → player scores 0 and the turn ends.

5️⃣ Capture Rule (Configurable):
   - If ENABLE_FOUR_SEED_BONUS is True:
       If a pit reaches exactly FOUR_SEED_TARGET seeds,
       the owner of that side captures those seeds.
   - If it reaches more than the target, no capture occurs.

6️⃣ End of Game:
   - When all pits on one player’s side are empty, 
     the opponent collects all remaining seeds on their side.
   - The player with the most total seeds wins the game.
"""


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------

def is_valid_pit_for_player(pit_index: int, player_turn: int) -> bool:
    """Checks if a given pit belongs to the current player."""
    return is_valid_pit_for_player_with_pit_count(pit_index, player_turn, 7)


def is_valid_pit_for_player_with_pit_count(pit_index: int, player_turn: int, pits_per_side: int) -> bool:
    """Checks pit ownership for a board with a variable number of pits per side."""
    if player_turn == 1:
        return 0 <= pit_index < pits_per_side
    if player_turn == 2:
        return pits_per_side <= pit_index < pits_per_side * 2
    return False


def get_opponent(player_turn: int) -> int:
    """Returns the opponent player's number."""
    return 2 if player_turn == 1 else 1


def is_bonus_pit(pit_index: int, seed_count: int) -> bool:
    """
    Determines if a pit qualifies for bonus capture 
    based on configuration.
    """
    return ENABLE_FOUR_SEED_BONUS and seed_count == FOUR_SEED_TARGET


def get_pit_owner(pit_index: int) -> str:
    """
    Returns the owner of the pit:
    '1' for Player 1 side
    '2' for Player 2 side
    """
    if pit_index in PLAYER_1_SIDE:
        return "1"
    elif pit_index in PLAYER_2_SIDE:
        return "2"
    return None