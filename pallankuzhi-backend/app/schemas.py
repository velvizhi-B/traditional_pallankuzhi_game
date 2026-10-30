from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


# ===========================================================
# ENUMS
# ===========================================================
class GameStatus(str, Enum):
    """Enum for tracking game status."""
    ongoing = "ongoing"
    completed = "completed"


# ===========================================================
# PLAYER SCHEMAS
# ===========================================================
class PlayerBase(BaseModel):
    player_name: str
    email: EmailStr


class PlayerCreate(PlayerBase):
    """Used when creating a new player."""
    pass


class PlayerResponse(PlayerBase):
    player_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================================================
# PIT SCHEMAS
# ===========================================================
class PitBase(BaseModel):
    pit_position: int
    seed_count: int


class PitResponse(PitBase):
    pit_id: int

    class Config:
        from_attributes = True


# ===========================================================
# MOVE SCHEMAS
# ===========================================================
class MoveBase(BaseModel):
    """Used when a player makes a move."""
    player_id: int
    pit_choosen: int


class MoveCreate(MoveBase):
    """Used when creating a move (before storing result)."""
    pass


class MoveResponse(MoveBase):
    """Response schema for moves with full details."""
    move_id: int
    resulting_board: Dict
    created_at: datetime

    class Config:
        from_attributes = True


# ===========================================================
# GAME SCHEMAS
# ===========================================================
class GameCreate(BaseModel):
    """Used to start a new game."""
    player1_id: int
    player2_id: int


class GameResponse(BaseModel):
    """Full response for a game, including related data."""
    id: int
    player1_id: int
    player2_id: int
    current_turn: int
    status: GameStatus
    winner: Optional[int] = None
    board_state: Dict
    created_at: datetime

    # Related tables
    pits: List[PitResponse] = []
    moves: List[MoveResponse] = []
    scores: Optional[Dict[str, int]] = None  # e.g., {"1": 12, "2": 8}

    class Config:
        from_attributes = True
