import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.core.database import SessionLocal, engine
from backend.models import domain
from datetime import date, timedelta
import uuid

def seed():
    # Setup tables
    domain.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--wallet", help="Your connected MetaMask wallet address")
    args = parser.parse_args()

    user_id = args.wallet or os.getenv("BANK_OS_ACCOUNT_ADDRESS")
    if not user_id:
        user_id = input("Enter your MetaMask wallet address to seed (e.g., 0x...): ").strip()
        
    if not user_id:
        print("No wallet address provided. Exiting.")
        return

    # Clear old data to force a refresh
    user = db.query(domain.User).filter(domain.User.id == user_id).first()
    if user:
        print(f"Refreshing data for {user_id}...")
        db.query(domain.Asset).filter(domain.Asset.user_id == user_id).delete()
        db.query(domain.DeFiPosition).filter(domain.DeFiPosition.user_id == user_id).delete()
        db.query(domain.ExpenseEvent).filter(domain.ExpenseEvent.user_id == user_id).delete()
        db.query(domain.IncomeEvent).filter(domain.IncomeEvent.user_id == user_id).delete()
        db.query(domain.Policy).filter(domain.Policy.user_id == user_id).delete()
        db.query(domain.FinancialProfile).filter(domain.FinancialProfile.user_id == user_id).delete()
        db.delete(user)
        db.commit()
        
    print(f"Seeding database for {user_id}...")
    user = domain.User(id=user_id)
    db.add(user)
    
    profile = domain.FinancialProfile(
        user_id=user_id,
        monthly_income=120000,
        risk_profile="moderate",
        minimum_liquidity=40000,
        emergency_reserve=20000,
        max_defi_exposure=75.0,
        max_autonomous_transaction=10000
    )
    db.add(profile)
    
    liquid = domain.Asset(id=str(uuid.uuid4()), user_id=user_id, asset_symbol="USDC", amount=50000, value_usd=50000, source="wallet")
    db.add(liquid)
    
    defi = domain.DeFiPosition(id=str(uuid.uuid4()), user_id=user_id, protocol="AAVE", asset_symbol="USDC", amount=45000, value_usd=45000, apy=5.2)
    db.add(defi)
    
    # Income (recurring)
    income = domain.IncomeEvent(id=str(uuid.uuid4()), user_id=user_id, amount=120000, category="Salary", expected_date=date.today() + timedelta(days=5), recurring=True)
    db.add(income)
    
    # Expense
    expense = domain.ExpenseEvent(id=str(uuid.uuid4()), user_id=user_id, amount=30000, category="Rent", expected_date=date.today() + timedelta(days=2), recurring=True)
    db.add(expense)
    
    # Allowed Policy
    policy = domain.Policy(id=str(uuid.uuid4()), user_id=user_id, policy_type="ALLOWED_PROTOCOL", value="AAVE", enabled=True)
    db.add(policy)
    
    db.commit()
    db.close()
    print("Seed complete.")

if __name__ == "__main__":
    seed()
