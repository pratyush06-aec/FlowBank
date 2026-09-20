from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.forecast import generate_forecast

router = APIRouter(prefix="/forecast", tags=["forecast"])

@router.get("/{user_id}")
def get_forecast(user_id: str, db: Session = Depends(get_db)):
    forecasts = generate_forecast(user_id, db)
    return {"forecasts": forecasts}
