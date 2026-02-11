from fastapi import APIRouter
from app.models.models import Transaction, Alert
from app.schemas.schemas import DashboardKPIs

router = APIRouter()

@router.get("/kpis", response_model=DashboardKPIs)
async def get_dashboard_kpis():
    total_trans = await Transaction.count()
    fraud_alerts = await Alert.find(Alert.risk_score > 70).count()
    
    # Calculate total amount
    total_amount = 0
    async for trans in Transaction.find_all():
        total_amount += trans.amount
    
    # In MongoDB/Beanie, joining is done via lookups or separate queries.
    # For now, let's keep it simple or use a manual join if needed.
    # Since we have links, we can find alerts and then get their transaction amounts.
    fraud_amount = 0
    alerts = await Alert.find(Alert.risk_score > 70).to_list()
    for alert in alerts:
        await alert.fetch_links()
    for alert in alerts:
        if alert.transaction:
            fraud_amount += alert.transaction.amount
    
    return DashboardKPIs(
        fraud_rate=(fraud_alerts / total_trans * 100) if total_trans > 0 else 0,
        fraud_sum=fraud_amount,
        detection_rate=95.5,
        review_rate=12.3,
        approval_rate=85.0,
        false_negative_rate=1.2
    )

@router.get("/alerts-over-time")
async def get_alerts_over_time():
    # Return mock trend data
    return [
        {"date": "2024-02-01", "alerts": 10, "fraud": 2},
        {"date": "2024-02-02", "alerts": 15, "fraud": 5},
        {"date": "2024-02-03", "alerts": 8, "fraud": 1},
        {"date": "2024-02-04", "alerts": 12, "fraud": 4},
        {"date": "2024-02-05", "alerts": 20, "fraud": 8},
        {"date": "2024-02-06", "alerts": 14, "fraud": 3},
        {"date": "2024-02-07", "alerts": 18, "fraud": 6},
    ]
