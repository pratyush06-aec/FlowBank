from sqlalchemy.orm import Session
from ..models.domain import User, FinancialProfile, Asset, DeFiPosition, IncomeEvent, ExpenseEvent

def calculate_financial_state(user_id: str, db: Session) -> dict:
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()
    
    liquid_assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    total_liquid = sum(asset.value_usd for asset in liquid_assets)
    
    defi_positions = db.query(DeFiPosition).filter(DeFiPosition.user_id == user_id).all()
    total_defi = sum(pos.value_usd for pos in defi_positions)
    
    # Simple upcoming obligations for the month (simplified for MVP)
    expenses = db.query(ExpenseEvent).filter(ExpenseEvent.user_id == user_id).all()
    upcoming_obligations = sum(exp.amount for exp in expenses)
    
    total_debt = 0.0 # Placeholder if no liability model
    net_position = total_liquid + total_defi - total_debt
    
    return {
        "total_liquid_cash": total_liquid,
        "total_defi_assets": total_defi,
        "emergency_reserve": profile.emergency_reserve if profile else 0.0,
        "upcoming_obligations": upcoming_obligations,
        "total_debt": total_debt,
        "net_position": net_position,
        "minimum_liquidity": profile.minimum_liquidity if profile else 0.0,
    }
