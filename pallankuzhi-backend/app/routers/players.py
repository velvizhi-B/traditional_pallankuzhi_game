from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, database


router = APIRouter(prefix="/players", tags=["Players"])


@router.post("/", response_model=schemas.PlayerResponse)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(database.get_db)):
    db_player = models.Player(player_name=player.player_name, email=player.email)

    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player



@router.get("/", response_model=list[schemas.PlayerResponse])
def list_players(db: Session = Depends(database.get_db)):
    return db.query(models.Player).all()
