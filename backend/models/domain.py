from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True) # e.g. wallet address or UUID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("FinancialProfile", back_populates="user", uselist=False)
    incomes = relationship("IncomeEvent", back_populates="user")
    expenses = relationship("ExpenseEvent", back_populates="user")
    assets = relationship("Asset", back_populates="user")
    defi_positions = relationship("DeFiPosition", back_populates="user")
    policies = relationship("Policy", back_populates="user")

class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    monthly_income = Column(Float, default=0.0)
    risk_profile = Column(String, default="moderate") # conservative, moderate, aggressive
    minimum_liquidity = Column(Float, default=0.0)
    emergency_reserve = Column(Float, default=0.0)
    max_defi_exposure = Column(Float, default=0.0) # percentage 0-100
    max_autonomous_transaction = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="profile")

class IncomeEvent(Base):
    __tablename__ = "income_events"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Float)
    category = Column(String)
    expected_date = Column(Date)
    recurring = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="incomes")

class ExpenseEvent(Base):
    __tablename__ = "expense_events"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    amount = Column(Float)
    category = Column(String)
    expected_date = Column(Date)
    recurring = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="expenses")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    asset_symbol = Column(String)
    amount = Column(Float)
    value_usd = Column(Float)
    source = Column(String) # e.g., 'wallet'
    
    user = relationship("User", back_populates="assets")

class DeFiPosition(Base):
    __tablename__ = "defi_positions"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    protocol = Column(String) # e.g., 'AAVE'
    asset_symbol = Column(String)
    amount = Column(Float)
    value_usd = Column(Float)
    apy = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="defi_positions")

class Policy(Base):
    __tablename__ = "policies"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    policy_type = Column(String) # e.g., 'ALLOWED_PROTOCOL'
    value = Column(String) # e.g., 'AAVE'
    enabled = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="policies")
