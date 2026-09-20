from datetime import date, timedelta
from sqlalchemy.orm import Session
from ..models.domain import FinancialProfile, Asset, IncomeEvent, ExpenseEvent, DeFiPosition

def generate_forecast(user_id: str, db: Session) -> list[dict]:
    # Base state
    liquid_assets = db.query(Asset).filter(Asset.user_id == user_id).all()
    current_liquid = sum(asset.value_usd for asset in liquid_assets)
    
    incomes = db.query(IncomeEvent).filter(IncomeEvent.user_id == user_id).all()
    expenses = db.query(ExpenseEvent).filter(ExpenseEvent.user_id == user_id).all()
    
    # Calculate simple daily rates for MVP based on monthly inputs
    monthly_income = sum(inc.amount for inc in incomes if inc.recurring)
    monthly_expense = sum(exp.amount for exp in expenses if exp.recurring)
    
    daily_net = (monthly_income - monthly_expense) / 30.0
    
    intervals = [7, 14, 30, 60, 90]
    forecasts = []
    
    today = date.today()
    
    for days in intervals:
        projected = current_liquid + (daily_net * days)
        # Process non-recurring events falling within the interval
        target_date = today + timedelta(days=days)
        
        for inc in incomes:
            if not inc.recurring and inc.expected_date and today <= inc.expected_date <= target_date:
                projected += inc.amount
                
        for exp in expenses:
            if not exp.recurring and exp.expected_date and today <= exp.expected_date <= target_date:
                projected -= exp.amount
                
        forecasts.append({
            "days": days,
            "target_date": target_date.isoformat(),
            "projected_liquidity": projected
        })
        
    return forecasts
