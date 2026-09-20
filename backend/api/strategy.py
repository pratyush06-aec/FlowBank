from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.strategy_engine import StrategyEngine

router = APIRouter(prefix="/strategy", tags=["strategy"])

@router.get("/{user_id}")
def get_strategy(user_id: str, db: Session = Depends(get_db)):
    engine = StrategyEngine(db, user_id)
    return engine.determine_strategy()
