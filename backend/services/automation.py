import threading
import time
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..core.strategy_engine import StrategyEngine
from ..core.copilot import AICopilot
from ..models.domain import User

def run_automation_loop():
    while True:
        db = SessionLocal()
        try:
            users = db.query(User).all()
            for user in users:
                # 1. Run Strategy
                strategy_engine = StrategyEngine(db, user.id)
                strategy = strategy_engine.determine_strategy()
                
                # 2. If high urgency action needed, pass to Copilot
                for action in strategy.get("strategies", []):
                    if action.get("urgency") == "HIGH":
                        print(f"[Automation] Urgent action required for {user.id}: {action}")
                        # In production, this would trigger an intent execution or push notification for approval
                        
        except Exception as e:
            print(f"[Automation Error] {e}")
        finally:
            db.close()
            
        time.sleep(3600) # Run every hour

def start_automation_daemon():
    thread = threading.Thread(target=run_automation_loop, daemon=True)
    thread.start()
