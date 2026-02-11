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
    id: int

    class Config:
        from_attributes = True

class RuleBase(BaseModel):
    name: str
    description: str
    score_impact: int
    action: str
    is_active: bool = True
    conditions: Dict[str, Any]
    priority: int = 0

class Rule(RuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    transaction_id: int
    risk_score: int
    risk_level: str
    status: str = "Pending"
    assigned_queue: Optional[str] = None

class Alert(AlertBase):
    id: int
    created_at: datetime
    transaction: Transaction

    class Config:
        from_attributes = True

class CaseBase(BaseModel):
    alert_id: int
    status: str = "Open"
    analyst_id: Optional[int] = None

class Case(CaseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    alert: Alert

    class Config:
        from_attributes = True

class DashboardKPIs(BaseModel):
    fraud_rate: float
    fraud_sum: float
    detection_rate: float
    review_rate: float
    approval_rate: float
    false_negative_rate: float
