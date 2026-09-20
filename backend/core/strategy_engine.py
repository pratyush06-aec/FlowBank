from sqlalchemy.orm import Session
from ..services.digital_twin import calculate_financial_state
from ..services.forecast import generate_forecast

class StrategyEngine:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        
    def determine_strategy(self) -> dict:
        """
        Determines what actions should be taken based on current state and 30-day forecast.
        """
        current_state = calculate_financial_state(self.user_id, self.db)
        forecasts = generate_forecast(self.user_id, self.db)
        
        # Look at the 30-day forecast
        forecast_30 = next((f for f in forecasts if f["days"] == 30), None)
        
        min_liquidity = current_state.get("minimum_liquidity", 0.0)
        current_liquid = current_state.get("total_liquid_cash", 0.0)
        
        strategies = []
        
        # Immediate Shortfall
        if current_liquid < min_liquidity:
            shortfall = min_liquidity - current_liquid
            strategies.append({
                "action": "WITHDRAW_FROM_DEFI",
                "amount": shortfall,
                "reason": "Immediate liquidity shortfall.",
                "urgency": "HIGH"
            })
            
        # 30-Day Forecast Shortfall
        elif forecast_30 and forecast_30["projected_liquidity"] < min_liquidity:
            shortfall = min_liquidity - forecast_30["projected_liquidity"]
            strategies.append({
                "action": "PREPARE_WITHDRAWAL",
                "amount": shortfall,
                "reason": "Projected liquidity shortfall in next 30 days.",
                "urgency": "MEDIUM"
            })
            
        # Idle Surplus
        elif forecast_30 and forecast_30["projected_liquidity"] > (min_liquidity * 1.5):
            surplus = forecast_30["projected_liquidity"] - (min_liquidity * 1.2) # Keep some buffer
            strategies.append({
                "action": "SUPPLY_TO_DEFI",
                "amount": surplus,
                "reason": "Idle surplus projected for next 30 days. Optimize yield.",
                "urgency": "LOW"
            })
            
        return {
            "current_liquid": current_liquid,
            "min_liquidity": min_liquidity,
            "strategies": strategies
        }
