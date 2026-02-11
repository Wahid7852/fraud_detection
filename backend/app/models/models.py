from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    customer_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    merchant_id = Column(Integer)
    category = Column(String)
    transaction_type = Column(String)
    
    # ML features
    old_balance_orig = Column(Float, nullable=True)
    new_balance_orig = Column(Float, nullable=True)
    old_balance_dest = Column(Float, nullable=True)
    new_balance_dest = Column(Float, nullable=True)

    alert = relationship("Alert", back_populates="transaction", uselist=False)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    risk_score = Column(Integer) # 0-99
    risk_level = Column(String) # Very Low -> Very High
    status = Column(String, default="Pending") # Pending, Reviewed, Dismissed
    assigned_queue = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    transaction = relationship("Transaction", back_populates="alert")
    case = relationship("Case", back_populates="alert", uselist=False)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    status = Column(String, default="Open") # Open, In Progress, Closed, SAR Filed
    analyst_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    alert = relationship("Alert", back_populates="case")
    notes = relationship("CaseNote", back_populates="case")

class CaseNote(Base):
    __tablename__ = "case_notes"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    note = Column(String)
    analyst_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("Case", back_populates="notes")

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    score_impact = Column(Integer)
    action = Column(String) # Approve, Deny, Review
    is_active = Column(Boolean, default=True)
    conditions = Column(JSON) # JSON object representing the rule logic
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
