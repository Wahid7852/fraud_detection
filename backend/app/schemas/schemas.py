from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any

class TransactionBase(BaseModel):
    transaction_id: str
    amount: float
    customer_id: int
    timestamp: datetime
    merchant_id: int
    category: str
    transaction_type: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: Optional[Any] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class RuleBase(BaseModel):
    name: str
    description: str
    score_impact: int
    action: str
    is_active: bool = True
    conditions: Dict[str, Any]
    priority: int = 0

class Rule(RuleBase):
    id: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class AlertBase(BaseModel):
    risk_score: int
    risk_level: str
    status: str = "Pending"
    assigned_queue: Optional[str] = None

class Alert(AlertBase):
    id: Optional[Any] = None
    created_at: datetime
    transaction: Optional[Transaction] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class CaseBase(BaseModel):
    status: str = "Open"
    analyst_id: Optional[int] = None

class Case(CaseBase):
    id: Optional[Any] = None
    created_at: datetime
    updated_at: datetime
    alert: Optional[Alert] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class DashboardKPIs(BaseModel):
    fraud_rate: float
    fraud_sum: float
    detection_rate: float
    review_rate: float
    approval_rate: float
    false_negative_rate: float
