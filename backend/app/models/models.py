from typing import Optional, List, Any
from datetime import datetime
from beanie import Document, Link
from pydantic import Field

class Transaction(Document):
    transaction_id: str = Field(unique=True)
    amount: float
    customer_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    merchant_id: int
    category: str
    transaction_type: str
    
    # ML features
    old_balance_orig: Optional[float] = None
    new_balance_orig: Optional[float] = None
    old_balance_dest: Optional[float] = None
    new_balance_dest: Optional[float] = None

    class Settings:
        name = "transactions"

class Alert(Document):
    transaction: Link[Transaction]
    risk_score: int # 0-99
    risk_level: str # Very Low -> Very High
    status: str = "Pending" # Pending, Reviewed, Dismissed
    assigned_queue: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "alerts"

class CaseNote(Document):
    note: str
    analyst_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "case_notes"

class Case(Document):
    alert: Link[Alert]
    status: str = "Open" # Open, In Progress, Closed, SAR Filed
    analyst_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: List[Link[CaseNote]] = []

    class Settings:
        name = "cases"

class Rule(Document):
    name: str
    description: str
    score_impact: int
    action: str # Approve, Deny, Review
    is_active: bool = True
    conditions: Any # JSON object representing the rule logic
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rules"
