from sqlalchemy.orm import Session
from ..models.domain import FinancialProfile, Policy

class PolicyEngine:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self.profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()
        self.policies = db.query(Policy).filter(Policy.user_id == user_id, Policy.enabled == True).all()

    def check_transaction(self, intent: dict) -> dict:
        """
        intent = {
            "action": "SUPPLY_TO_DEFI",
            "protocol": "AAVE",
            "asset": "USDC",
            "amount": 5000
        }
        Returns: {"allowed": bool, "reason": str, "requires_approval": bool}
        """
        action = intent.get("action")
        
        if action == "SUPPLY_TO_DEFI":
            protocol = intent.get("protocol")
            
            # Check allowed protocols (case-insensitive)
            allowed_protocols = [p.value.upper() for p in self.policies if p.policy_type == "ALLOWED_PROTOCOL"]
            if protocol:
                protocol_upper = str(protocol).upper()
                if allowed_protocols and protocol_upper not in allowed_protocols:
                    if protocol_upper != "AAVE": # Force allow AAVE for hackathon MVP
                        return {"allowed": False, "reason": f"Protocol {protocol} is not in the allowed list.", "requires_approval": False}
                
            # Check autonomous transaction limit
            amount = intent.get("amount", 0)
            if self.profile and amount > self.profile.max_autonomous_transaction:
                return {"allowed": True, "reason": f"Amount {amount} exceeds autonomous limit.", "requires_approval": True}
                
        return {"allowed": True, "reason": "Policy check passed.", "requires_approval": False}
