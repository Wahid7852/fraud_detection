from typing import Optional, List, Any
from datetime import datetime, timezone
from beanie import Document, Link
from pydantic import Field

class Transaction(Document):
    transaction_id: str = Field(unique=True)
    amount: float
    customer_id: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    risk_score: int = Field(default=0) # 0-99
    risk_level: str = Field(default="Low") # Very Low -> Very High
    status: str = Field(default="Pending") # Pending, Reviewed, Dismissed
    assigned_queue: str = Field(default="General")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "alerts"

class CaseNote(Document):
    note: str
    analyst_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "case_notes"

class Case(Document):
    alert: Link[Alert]
    status: str = Field(default="Open") # Open, In Progress, Closed, SAR Filed
    analyst_id: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: List[Link[CaseNote]] = Field(default_factory=list)

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "rules"

class SAR(Document):
    sar_id: str = Field(unique=True)
    case: Link[Case]
    customer_name: Optional[str] = None
    amount: float
    status: str = Field(default="Draft") # Draft, Pending, Filed
    filing_date: Optional[datetime] = None
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "sars"
