from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...db.session import get_db
from ...models.models import Transaction, Alert
from ...schemas.schemas import DashboardKPIs

router = APIRouter()

@router.get("/kpis", response_model=DashboardKPIs)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    total_trans = db.query(Transaction).count()
    fraud_alerts = db.query(Alert).filter(Alert.risk_score > 70).count()
    total_amount = db.query(func.sum(Transaction.amount)).scalar() or 0
    fraud_amount = db.query(func.sum(Transaction.amount)).join(Alert).filter(Alert.risk_score > 70).scalar() or 0
    
    # Mock data for demonstration, in a real app these would be calculated
    return DashboardKPIs(
        fraud_rate=(fraud_alerts / total_trans * 100) if total_trans > 0 else 0,
        fraud_sum=fraud_amount,
        detection_rate=95.5,
        review_rate=12.3,
        approval_rate=85.0,
        false_negative_rate=1.2
    )

@router.get("/alerts-over-time")
def get_alerts_over_time(db: Session = Depends(get_db)):
    # Group by date and count alerts
    # For now, return mock trend data
    return [
        {"date": "2024-02-01", "alerts": 10, "fraud": 2},
        {"date": "2024-02-02", "alerts": 15, "fraud": 5},
        {"date": "2024-02-03", "alerts": 8, "fraud": 1},
        {"date": "2024-02-04", "alerts": 12, "fraud": 4},
        {"date": "2024-02-05", "alerts": 20, "fraud": 8},
        {"date": "2024-02-06", "alerts": 14, "fraud": 3},
        {"date": "2024-02-07", "alerts": 18, "fraud": 6},
    ]
