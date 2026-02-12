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
        if alert.transaction:
            transaction = await Transaction.get(alert.transaction.ref.id)
            if transaction:
                fraud_amount += transaction.amount
    
    # Calculate detection rate (alerts / transactions)
    detection_rate = (fraud_alerts / total_trans * 100) if total_trans > 0 else 0
    
    # Calculate review rate (cases / alerts)
    from app.models.models import Case
    total_cases = await Case.count()
    review_rate = (total_cases / fraud_alerts * 100) if fraud_alerts > 0 else 0
    
    # Calculate approval rate (closed cases without SAR / total cases)
    closed_cases = await Case.find(Case.status == "Closed").count()
    sar_cases = await Case.find(Case.status == "SAR Filed").count()
    approval_rate = (closed_cases / total_cases * 100) if total_cases > 0 else 0
    
    # Round and limit values to reasonable ranges
    fraud_rate = min((fraud_alerts / total_trans * 100) if total_trans > 0 else 0, 100)
    detection_rate = min(detection_rate, 100)
    review_rate = min(review_rate, 100)
    approval_rate = min(approval_rate, 100)
    
    return DashboardKPIs(
        fraud_rate=round(fraud_rate, 2),
        fraud_sum=round(fraud_amount, 2),
        detection_rate=round(detection_rate, 2),
        review_rate=round(review_rate, 2),
        approval_rate=round(approval_rate, 2),
        false_negative_rate=round(1.2, 2)  # Placeholder - would need historical data
    )

@router.get("/alerts-over-time")
async def get_alerts_over_time():
    """Get real alerts trend data from database"""
    from datetime import datetime, timedelta
    
    # Get alerts from last 7 days
    alerts = await Alert.find_all().to_list()
    
    # Group by date
    trends = {}
    for alert in alerts:
        date_key = alert.created_at.date().isoformat()
        if date_key not in trends:
            trends[date_key] = {"alerts": 0, "fraud": 0}
        trends[date_key]["alerts"] += 1
        if alert.risk_score >= 70:
            trends[date_key]["fraud"] += 1
    
    # Convert to list and sort by date
    result = [
        {"date": date, "alerts": data["alerts"], "fraud": data["fraud"]}
        for date, data in sorted(trends.items())
    ]
    
    # If no data, return empty list
    return result if result else [
        {"date": (datetime.now() - timedelta(days=i)).date().isoformat(), "alerts": 0, "fraud": 0}
        for i in range(6, -1, -1)
    ]
