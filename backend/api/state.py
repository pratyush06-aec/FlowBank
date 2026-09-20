from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.digital_twin import calculate_financial_state

router = APIRouter(prefix="/financial-state", tags=["state"])

@router.get("/{user_id}")
def get_financial_state(user_id: str, db: Session = Depends(get_db)):
    state = calculate_financial_state(user_id, db)
    return state
