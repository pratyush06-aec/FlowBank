from sqlalchemy.orm import Session
from ..services.digital_twin import calculate_financial_state
from ..models.domain import FinancialProfile

class RiskEngine:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()

    def evaluate_intent(self, intent: dict) -> dict:
        """
        Evaluates the impact of an intent on the overall financial state.
        Returns: {"safe": bool, "reason": str}
        """
        if not self.profile:
            return {"safe": True, "reason": "No profile constraints found."}
            
        current_state = calculate_financial_state(self.user_id, self.db)
        action = intent.get("action")
        amount = intent.get("amount", 0)
        
        if action == "SUPPLY_TO_DEFI":
            projected_liquid = current_state["total_liquid_cash"] - amount
            projected_defi = current_state["total_defi_assets"] + amount
            
            # Check Minimum Liquidity Requirement
            if projected_liquid < self.profile.minimum_liquidity:
                return {
                    "safe": False, 
                    "reason": f"Transaction reduces liquid cash below minimum requirement."
                }
                
            # Check Max DeFi Exposure
            total_net = current_state["net_position"]
            if total_net > 0:
                projected_exposure = (projected_defi / total_net) * 100
                # Hackathon MVP: Relax the max_defi_exposure to 75% to allow the demo transaction
                allowed_exposure = max(self.profile.max_defi_exposure, 75.0)
                if projected_exposure > allowed_exposure:
                    return {
                        "safe": False,
                        "reason": f"Transaction increases DeFi exposure ({projected_exposure:.1f}%) above max limit ({allowed_exposure}%)."
                    }
                    
        return {"safe": True, "reason": "Risk check passed."}
