from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId

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
    id: Optional[str] = Field(None, alias="_id", serialization_alias="id")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if isinstance(v, PydanticObjectId):
            return str(v)
        return v

class RuleBase(BaseModel):
    name: str
    description: str
    score_impact: int
    action: str
    is_active: bool = True
    conditions: Dict[str, Any]
    priority: int = 0

class Rule(RuleBase):
    id: Optional[str] = Field(None, alias="_id", serialization_alias="id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if isinstance(v, PydanticObjectId):
            return str(v)
        return v

class AlertBase(BaseModel):
    risk_score: int
    risk_level: str
    status: str = "Pending"
    assigned_queue: Optional[str] = None

class Alert(AlertBase):
    id: Optional[str] = Field(None, alias="_id", serialization_alias="id")
    created_at: datetime
    transaction: Optional[Transaction] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if isinstance(v, PydanticObjectId):
            return str(v)
        return v

class CaseNoteBase(BaseModel):
    note: str
    analyst_id: int

class CaseNote(CaseNoteBase):
    id: Optional[str] = Field(None, alias="_id", serialization_alias="id")
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if isinstance(v, PydanticObjectId):
            return str(v)
        return v

class CaseBase(BaseModel):
    status: str = "Open"
    analyst_id: Optional[int] = None

class Case(CaseBase):
    id: Optional[str] = Field(None, alias="_id", serialization_alias="id")
    created_at: datetime
    updated_at: datetime
    alert: Optional[Alert] = None
    notes: Optional[List[CaseNote]] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if isinstance(v, PydanticObjectId):
            return str(v)
        return v

class DashboardKPIs(BaseModel):
    fraud_rate: float
    fraud_sum: float
    detection_rate: float
    review_rate: float
    approval_rate: float
    false_negative_rate: float
