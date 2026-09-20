from sqlalchemy.orm import Session
from ..models.domain import FinancialProfile, Asset, IncomeEvent, ExpenseEvent, DeFiPosition
from .digital_twin import calculate_financial_state

def simulate_scenario(user_id: str, db: Session, scenario_params: dict) -> dict:
    """
    scenario_params could include:
    {
        "type": "LARGE_PURCHASE",
        "amount": 25000,
        "date_offset_days": 10
    }
    """
    # 1. Get base state
    current_state = calculate_financial_state(user_id, db)
    
    # 2. Apply scenario (without committing to DB)
    projected_state = current_state.copy()
    
    scenario_type = scenario_params.get("type")
    
    if scenario_type == "LARGE_PURCHASE":
        amount = scenario_params.get("amount", 0)
        projected_state["total_liquid_cash"] -= amount
        
    elif scenario_type == "INCOME_DELAY":
        # Simulating delay reduces liquid cash by the income amount if it was expected
        amount = scenario_params.get("amount", 0)
        projected_state["total_liquid_cash"] -= amount
        
    elif scenario_type == "DEFI_DROP":
        percent = scenario_params.get("percentage_drop", 0)
        drop_value = projected_state["total_defi_assets"] * (percent / 100.0)
        projected_state["total_defi_assets"] -= drop_value
    
    # Recalculate net position
    projected_state["net_position"] = projected_state["total_liquid_cash"] + projected_state["total_defi_assets"] - projected_state["total_debt"]
    
    # 3. Calculate Risk and Liquidity Impact
    min_liquidity = projected_state.get("minimum_liquidity", 0.0)
    new_liquid = projected_state.get("total_liquid_cash", 0.0)
    
    impact = current_state["total_liquid_cash"] - new_liquid
    
    status = "SAFE"
    recommended_action = "No action needed."
    
    if new_liquid < min_liquidity:
        status = "LIQUIDITY RISK"
        shortfall = min_liquidity - new_liquid
        if projected_state["total_defi_assets"] >= shortfall:
            recommended_action = f"Withdraw ₹{shortfall:,.2f} from DeFi position to cover the shortfall."
        else:
            recommended_action = f"Warning: Shortfall of ₹{shortfall:,.2f} exceeds available DeFi liquidity."
            
    return {
        "current_state": current_state,
        "scenario_assumptions": scenario_params,
        "projected_state": projected_state,
        "liquidity_impact": f"₹{impact:,.2f} reduction" if impact > 0 else "None",
        "risk_impact": status,
        "recommended_action": recommended_action,
        "execution_status": "Simulation only — no transaction executed."
    }
