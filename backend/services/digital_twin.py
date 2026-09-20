from sqlalchemy.orm import Session
from ..models.domain import User, FinancialProfile, Asset, DeFiPosition, IncomeEvent, ExpenseEvent

def calculate_financial_state(user_id: str, db: Session) -> dict:
    profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()
    
    if not profile:
        import uuid
        from datetime import date, timedelta
        from ..models.domain import Policy
        
        user = User(id=user_id)
        db.add(user)
        
        profile = FinancialProfile(
            user_id=user_id,
            monthly_income=120000,
            risk_profile="moderate",
            minimum_liquidity=40000,
            emergency_reserve=20000,
            max_defi_exposure=75.0,
            max_autonomous_transaction=10000
        )
        db.add(profile)
        
        liquid = Asset(id=str(uuid.uuid4()), user_id=user_id, asset_symbol="USDC", amount=50000.0, value_usd=50000.0, source="wallet")
        db.add(liquid)
        
        defi = DeFiPosition(id=str(uuid.uuid4()), user_id=user_id, protocol="AAVE", asset_symbol="USDC", amount=45000.0, value_usd=45000.0, apy=5.2)
        db.add(defi)
        
        income = IncomeEvent(id=str(uuid.uuid4()), user_id=user_id, amount=120000.0, category="Salary", expected_date=date.today() + timedelta(days=5), recurring=True)
        db.add(income)
        
        expense = ExpenseEvent(id=str(uuid.uuid4()), user_id=user_id, amount=30000.0, category="Rent", expected_date=date.today() + timedelta(days=2), recurring=True)
        db.add(expense)
        
        policy = Policy(id=str(uuid.uuid4()), user_id=user_id, policy_type="ALLOWED_PROTOCOL", value="AAVE", enabled=True)
        db.add(policy)
        
        db.commit()
    
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
