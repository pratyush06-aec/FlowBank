from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.simulator import simulate_scenario

router = APIRouter(prefix="/simulate", tags=["simulate"])

@router.post("/{user_id}")
def run_simulation(user_id: str, scenario_params: dict = Body(...), db: Session = Depends(get_db)):
    result = simulate_scenario(user_id, db, scenario_params)
    return result
