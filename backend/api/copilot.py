from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.copilot import AICopilot

router = APIRouter(prefix="/copilot", tags=["copilot"])

@router.post("/{user_id}")
def process_prompt(user_id: str, prompt: str = Body(..., embed=True), db: Session = Depends(get_db)):
    copilot = AICopilot(db, user_id)
    result = copilot.process_prompt(prompt)
    return result
