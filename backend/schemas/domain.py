from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class FinancialProfileBase(BaseModel):
    monthly_income: float
    risk_profile: str
    minimum_liquidity: float
    emergency_reserve: float
    max_defi_exposure: float
    max_autonomous_transaction: float

class FinancialProfileCreate(FinancialProfileBase):
    pass

class FinancialProfileResponse(FinancialProfileBase):
    user_id: str
    
    class Config:
        from_attributes = True

class IncomeEventBase(BaseModel):
    amount: float
    category: str
    expected_date: date
    recurring: bool

class IncomeEventCreate(IncomeEventBase):
    pass

class IncomeEventResponse(IncomeEventBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True

class ExpenseEventBase(BaseModel):
    amount: float
    category: str
    expected_date: date
    recurring: bool

class ExpenseEventCreate(ExpenseEventBase):
    pass

class ExpenseEventResponse(ExpenseEventBase):
    id: str
    user_id: str

    class Config:
        from_attributes = True
