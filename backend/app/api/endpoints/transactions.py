from fastapi import APIRouter, HTTPException
from typing import List
from app.models.models import Transaction, Alert, Case
from app.schemas.schemas import Transaction as TransactionSchema, TransactionCreate
from app.fraud_engine.scoring.scorer import Scorer

router = APIRouter()

@router.post("/", response_model=TransactionSchema)
async def create_transaction(transaction: TransactionCreate):
    # 1. Save transaction
    db_trans = Transaction(**transaction.dict())
    await db_trans.insert()
    
    # 2. Run fraud engine
    scorer = Scorer()
    result = await scorer.calculate_score(db_trans)
    
    # 3. Create alert if score is high
    if result["risk_score"] > 50: # Threshold for alert
        alert = Alert(
            transaction=db_trans,
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            status="Pending",
            assigned_queue="General Queue"
        )
        await alert.insert()
        
        # 4. Auto-create case for very high risk
        if result["risk_score"] > 90:
            case = Case(
                alert=alert,
                status="Open"
            )
            await case.insert()
            
    return TransactionSchema.model_validate(db_trans)

@router.get("/", response_model=List[TransactionSchema])
async def get_transactions():
    transactions = await Transaction.find_all().to_list()
    return [TransactionSchema.model_validate(t) for t in transactions]

@router.get("/{trans_id}", response_model=TransactionSchema)
async def get_transaction(trans_id: str):
    trans = await Transaction.get(trans_id)
    if not trans:
        # Also try finding by transaction_id string
        trans = await Transaction.find_one(Transaction.transaction_id == trans_id)
        if not trans:
            raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionSchema.model_validate(trans)
