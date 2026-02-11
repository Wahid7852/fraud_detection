from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.models import Transaction, Alert, Case
from app.schemas.schemas import Transaction as TransactionSchema, TransactionCreate
from app.fraud_engine.scoring.scorer import Scorer

router = APIRouter()

@router.post("/", response_model=TransactionSchema)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    # 1. Save transaction
    db_trans = Transaction(**transaction.dict())
    db.add(db_trans)
    db.commit()
    db.refresh(db_trans)
    
    # 2. Run fraud engine
    scorer = Scorer(db)
    result = scorer.calculate_score(db_trans)
    
    # 3. Create alert if score is high
    if result["risk_score"] > 50: # Threshold for alert
        alert = Alert(
            transaction_id=db_trans.id,
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            status="Pending",
            assigned_queue="General Queue"
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # 4. Auto-create case for very high risk
        if result["risk_score"] > 90:
            case = Case(
                alert_id=alert.id,
                status="Open"
            )
            db.add(case)
            db.commit()
            
    return db_trans

@router.get("/{trans_id}", response_model=TransactionSchema)
def get_transaction(trans_id: int, db: Session = Depends(get_db)):
    trans = db.query(Transaction).filter(Transaction.id == trans_id).first()
    if not trans:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return trans
