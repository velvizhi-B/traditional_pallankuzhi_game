from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum


# ===========================================================
# ENUMS
# ===========================================================
class GameStatus(str, enum.Enum):
    """Enum for tracking game status."""
    ongoing = "ongoing"
    completed = "completed"


# ===========================================================
# PLAYER MODEL
# ===========================================================
class Player(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    games_as_player1 = relationship(
        "Game",
        foreign_keys="[Game.player1_id]",
        back_populates="player1",
    )
    games_as_player2 = relationship(
        "Game",
        foreign_keys="[Game.player2_id]",
        back_populates="player2",
    )
    games_won = relationship(
        "Game",
        foreign_keys="[Game.winner]",
        back_populates="winner_player",
    )


# ===========================================================
# GAME MODEL
# ===========================================================
class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    current_turn = Column(Integer, nullable=False, default=1)
    status = Column(Enum(GameStatus), default=GameStatus.ongoing, nullable=False)
    winner = Column(Integer, ForeignKey("players.player_id"), nullable=True)
    scores = Column(JSON, nullable=False, default=dict)

    # Stores full game board state:
    # Example: {"pits": [5,5,5,...,5], "scores": {"1": 0, "2": 0}}
    board_state = Column(JSON, nullable=False, default={"pits": [5] * 14, "scores": {"1": 0, "2": 0}})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    player1 = relationship(
        "Player",
        foreign_keys=[player1_id],
        back_populates="games_as_player1",
    )
    player2 = relationship(
        "Player",
        foreign_keys=[player2_id],
        back_populates="games_as_player2",
    )
    winner_player = relationship(
        "Player",
        foreign_keys=[winner],
        back_populates="games_won",
    )

    pits = relationship("Pit", back_populates="game", cascade="all, delete-orphan")
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")


# ===========================================================
# PIT MODEL
# ===========================================================
class Pit(Base):
    __tablename__ = "pits"

    pit_id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    pit_position = Column(Integer, nullable=False)  # Range: 0–13
    seed_count = Column(Integer, nullable=False, default=5)

    game = relationship("Game", back_populates="pits")


# ===========================================================
# MOVE MODEL
# ===========================================================
class Move(Base):
    __tablename__ = "moves"

    move_id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.player_id"), nullable=False)
    pit_choosen = Column(Integer, nullable=False)
    resulting_board = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    game = relationship("Game", back_populates="moves")
