from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.domain import FinancialProfile, User
from ..schemas.domain import FinancialProfileCreate, FinancialProfileResponse
import uuid

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/{user_id}", response_model=FinancialProfileResponse)
def get_profile(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/{user_id}", response_model=FinancialProfileResponse)
def update_profile(user_id: str, profile_in: FinancialProfileCreate, db: Session = Depends(get_db)):
    # Ensure user exists for MVP simplicity
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        db.add(user)
        db.commit()

    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()
    if profile:
        for key, value in profile_in.model_dump().items():
            setattr(profile, key, value)
    else:
        profile = FinancialProfile(user_id=user_id, **profile_in.model_dump())
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile
