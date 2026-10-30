# ===========================================================
# CRUD Operations for Pallankuzhi Game
# ===========================================================
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from app import models, schemas
import app
from app.database import get_db


# ===========================================================
# PLAYER CRUD
# ===========================================================
def create_player(db: Session, player: schemas.PlayerCreate):
    """Create a new player."""
    existing_player = db.query(models.Player).filter(models.Player.email == player.email).first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player with this email already exists",
        )

    new_player = models.Player(player_name=player.player_name, email=player.email)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


def get_player(db: Session, player_id: int):
    """Retrieve a player by ID."""
    player = db.query(models.Player).filter(models.Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return player


def get_all_players(db: Session):
    """Get all registered players."""
    return db.query(models.Player).order_by(models.Player.player_id).all()


# ===========================================================
# GAME CRUD
# ===========================================================
def create_game(db: Session, game_data: schemas.GameCreate):
    """Create and initialize a new game."""
    p1 = db.query(models.Player).filter(models.Player.player_id == game_data.player1_id).first()
    p2 = db.query(models.Player).filter(models.Player.player_id == game_data.player2_id).first()

    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="One or both players not found")

    new_game = models.Game(
        player1_id=game_data.player1_id,
        player2_id=game_data.player2_id,
        current_turn=1,
        status=models.GameStatus.ongoing,
        board_state={"pits": [5] * 14, "scores": {"1": 0, "2": 0}},
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    # Create 14 pits
    for i in range(14):
        pit = models.Pit(game_id=new_game.id, pit_position=i, seed_count=5)
        db.add(pit)
    db.commit()
    return new_game


def get_game_by_id(db: Session, game_id: int):
    """Retrieve a game with all its pits and moves."""
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


def get_all_games(db: Session):
    """Get all existing games."""
    return db.query(models.Game).order_by(models.Game.id.desc()).all()


# ===========================================================
# MOVE CRUD
# ===========================================================
def create_move(db: Session, move_data: schemas.MoveBase, game: models.Game):
    """Store a move made by a player."""
    move = models.Move(
        game_id=game.id,
        player_id=move_data.player_id,
        pit_choosen=move_data.pit_choosen,
        resulting_board=game.board_state,
    )
    db.add(move)
    db.commit()
    db.refresh(move)
    return move


def get_moves_for_game(db: Session, game_id: int):
    """Get all moves for a given game."""
    return db.query(models.Move).filter(models.Move.game_id == game_id).order_by(models.Move.move_id).all()

@app.get("/games/{game_id}", response_model=schemas.GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Example score calculation logic (customize as needed)
    scores = {
        "1": sum(p.seed_count for p in game.pits if p.pit_position in range(0, 7)),
        "2": sum(p.seed_count for p in game.pits if p.pit_position in range(7, 14)),
    }

    response = schemas.GameResponse(
        **game.__dict__,
        pits=game.pits,
        moves=game.moves,
        scores=scores
    )
    return response
