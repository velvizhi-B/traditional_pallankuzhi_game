# ===========================================================
# Moves Router — Handles Player Moves and Turn Logic
# ===========================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.core import game_logic, game_rules

router = APIRouter(prefix="/moves", tags=["Moves"])


# ===========================================================
# MAKE A MOVE
# ===========================================================
@router.post("/{game_id}", response_model=schemas.GameResponse)
def make_move(game_id: int, move: schemas.MoveBase, db: Session = Depends(database.get_db)):
    """
    Player makes a move according to Pallankuzhi rules.
    Handles sowing, capture, continuation, scoring, and turn switching.
    """

    # 1️⃣ Fetch the game
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.status != game_rules.GAME_STATUS_ONGOING:
        raise HTTPException(status_code=400, detail="Game is already completed")

    # 2️⃣ Determine current player
    current_player_id = game.player1_id if game.current_turn == 1 else game.player2_id
    if move.player_id != current_player_id:
        raise HTTPException(status_code=403, detail="Not your turn")

    # 3️⃣ Load board state & scores
    board_state = game.board_state or {}
    board = list(board_state.get("pits", []))
    if not board or len(board) < 2 or len(board) % 2 != 0:
        raise HTTPException(status_code=400, detail="Invalid board state")

    scores = {"1": game.scores.get("1", 0), "2": game.scores.get("2", 0)} if game.scores else {"1": 0, "2": 0}

    # 4️⃣ Validate chosen pit
    pits_per_side = len(board) // 2
    if not game_rules.is_valid_pit_for_player_with_pit_count(move.pit_choosen, game.current_turn, pits_per_side):
        raise HTTPException(status_code=400, detail="You can only play from your side pits")

    if board[move.pit_choosen] == 0:
        raise HTTPException(status_code=400, detail="Selected pit is empty")

    # 5️⃣ Apply main sow-and-capture logic
    updated_board, updated_scores, game_continues = game_logic.sow_and_capture(
        board=board,
        start_index=move.pit_choosen,
        player_turn=game.current_turn,
        scores=scores,
    )

    # 6️⃣ Check for end of game
    game_over, final_scores = game_logic.check_game_over(updated_board, updated_scores)
    game.board_state = {
        "pits": updated_board,
        "starting_player": board_state.get("starting_player", game.current_turn),
    }
    game.scores = final_scores

    if game_over:
        game.status = game_rules.GAME_STATUS_COMPLETED
        winner = None
        if final_scores["1"] > final_scores["2"]:
            winner = game.player1_id
        elif final_scores["2"] > final_scores["1"]:
            winner = game.player2_id
        game.winner = winner

    else:
        # Switch turns only if game continues
        if not game_continues:
            game.current_turn = game_rules.get_opponent(game.current_turn)

    # 7️⃣ Log the move
    new_move = models.Move(
        game_id=game.id,
        player_id=move.player_id,
        pit_choosen=move.pit_choosen,
        resulting_board={"pits": updated_board},
    )
    db.add(new_move)

    db.commit()
    db.refresh(game)

    return game
