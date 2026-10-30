# ===========================================================
# Games Router — Create and Manage Game Instances
# ===========================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
from app import models, schemas, database
from app.core import game_rules

router = APIRouter(prefix="/games", tags=["Games"])


# ===========================================================
# START A NEW GAME
# ===========================================================
@router.post("/", response_model=schemas.GameResponse)
def start_game(game: schemas.GameCreate, db: Session = Depends(database.get_db)):
    """
    Starts a new Pallankuzhi game with 14 pits (5 seeds each) and initializes both players.
    """

    # ✅ Validate players
    p1 = db.query(models.Player).filter(models.Player.player_id == game.player1_id).first()
    p2 = db.query(models.Player).filter(models.Player.player_id == game.player2_id).first()

    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="One or both players not found")

    # ✅ Create game entry with default state
    starting_player = random.choice([1, 2])
    new_game = models.Game(
        player1_id=game.player1_id,
        player2_id=game.player2_id,
        current_turn=starting_player,
        status=models.GameStatus.ongoing,
        board_state={
            "pits": [game_rules.INITIAL_SEEDS] * game_rules.TOTAL_PITS,
            "starting_player": starting_player,
        },
        scores={"1": 0, "2": 0},
    )

    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    # ✅ Initialize pits (14 total)
    for i in range(game_rules.TOTAL_PITS):
        pit = models.Pit(game_id=new_game.id, pit_position=i, seed_count=game_rules.INITIAL_SEEDS)
        db.add(pit)
    db.commit()

    db.refresh(new_game)
    return new_game


@router.post("/{game_id}/rematch", response_model=schemas.GameResponse)
def start_rematch(game_id: int, db: Session = Depends(database.get_db)):
    """Start the next level using the completed game's scores and board size rules."""
    previous_game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not previous_game:
        raise HTTPException(status_code=404, detail="Game not found")
    if previous_game.status != models.GameStatus.completed:
        raise HTTPException(status_code=400, detail="Rematch is available after the game is completed")

    previous_scores = previous_game.scores or {"1": 0, "2": 0}
    least_score = min(previous_scores.get("1", 0), previous_scores.get("2", 0))
    pits_per_side = least_score // game_rules.INITIAL_SEEDS
    if pits_per_side < 1:
        raise HTTPException(
            status_code=400,
            detail="The match series is finished because a player has fewer than 5 points",
        )
    total_pits = pits_per_side * 2
    seeds_used_per_player = pits_per_side * game_rules.INITIAL_SEEDS
    carried_scores = {
        "1": max(0, previous_scores.get("1", 0) - seeds_used_per_player),
        "2": max(0, previous_scores.get("2", 0) - seeds_used_per_player),
    }
    previous_starting_player = previous_game.board_state.get("starting_player", previous_game.current_turn)
    starting_player = game_rules.get_opponent(previous_starting_player)
    board = [game_rules.INITIAL_SEEDS] * total_pits

    new_game = models.Game(
        player1_id=previous_game.player1_id,
        player2_id=previous_game.player2_id,
        current_turn=starting_player,
        status=models.GameStatus.ongoing,
        board_state={"pits": board, "starting_player": starting_player},
        scores=carried_scores,
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    for pit_position in range(total_pits):
        db.add(models.Pit(
            game_id=new_game.id,
            pit_position=pit_position,
            seed_count=game_rules.INITIAL_SEEDS,
        ))
    db.commit()
    db.refresh(new_game)
    return new_game


# ===========================================================
# GET GAME DETAILS
# ===========================================================
@router.get("/{game_id}", response_model=schemas.GameResponse)
def get_game(game_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves full game state, including pits and scores.
    """
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game
