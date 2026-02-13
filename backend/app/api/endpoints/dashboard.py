from fastapi import APIRouter
from app.models.models import Transaction, Alert, Case
from app.schemas.schemas import DashboardKPIs
from datetime import datetime, timedelta
from app.core.cache import cached

router = APIRouter()

@router.get("/kpis", response_model=DashboardKPIs)
@cached(ttl=30) # Cache for 30 seconds
async def get_dashboard_kpis():
    # Use aggregation for total amount and count
    trans_stats = await Transaction.aggregate([
        {"$group": {"_id": None, "total_amount": {"$sum": "$amount"}, "count": {"$sum": 1}}}
    ]).to_list()
    
    total_trans = trans_stats[0]["count"] if trans_stats else 0
    total_amount = trans_stats[0]["total_amount"] if trans_stats else 0
    
    # Use aggregation for fraud alerts stats
    # We need to join with Transaction to get the amount of flagged transactions
    alert_stats = await Alert.aggregate([
        {"$match": {"risk_score": {"$gt": 70}}},
        {"$lookup": {
            "from": "transactions",
            "localField": "transaction.$id",
            "foreignField": "_id",
            "as": "trans_data"
        }},
        {"$unwind": "$trans_data"},
        {"$group": {
            "_id": None, 
            "fraud_alerts": {"$sum": 1}, 
            "fraud_amount": {"$sum": "$trans_data.amount"}
        }}
    ]).to_list()
    
    fraud_alerts = alert_stats[0]["fraud_alerts"] if alert_stats else 0
    fraud_amount = alert_stats[0]["fraud_amount"] if alert_stats else 0
    
    total_cases = await Case.count()
    closed_cases = await Case.find(Case.status == "Closed").count()
    
    # Rates
    fraud_rate = (fraud_alerts / total_trans * 100) if total_trans > 0 else 0
    detection_rate = fraud_rate # Simplified for now
    review_rate = (total_cases / fraud_alerts * 100) if fraud_alerts > 0 else 0
    approval_rate = (closed_cases / total_cases * 100) if total_cases > 0 else 0
    
    return DashboardKPIs(
        fraud_rate=round(min(fraud_rate, 100), 2),
        fraud_sum=round(fraud_amount, 2),
        detection_rate=round(min(detection_rate, 100), 2),
        review_rate=round(min(review_rate, 100), 2),
        approval_rate=round(min(approval_rate, 100), 2),
        false_negative_rate=1.2
    )

@router.get("/alerts-over-time")
@cached(ttl=60)
async def get_alerts_over_time():
    # Use aggregation to group by date directly in MongoDB
    # This is MUCH faster than fetching all records
    
    # 1. Transaction counts per day
    trans_trend = await Transaction.aggregate([
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "total_transactions": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]).to_list()
    
    # 2. Alert counts per day
    alert_trend = await Alert.aggregate([
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "alerts": {"$sum": 1},
                "fraud": {"$sum": {"$cond": [{"$gte": ["$risk_score", 90]}, 1, 0]}}
            }
        },
        {"$sort": {"_id": 1}}
    ]).to_list()
    
    # Merge results
    trends = {}
    for item in trans_trend:
        date = item["_id"]
        if date:
            trends[date] = {"alerts": 0, "fraud": 0, "total_transactions": item["total_transactions"]}
            
    for item in alert_trend:
        date = item["_id"]
        if date:
            if date not in trends:
                trends[date] = {"alerts": 0, "fraud": 0, "total_transactions": 0}
            trends[date]["alerts"] = item["alerts"]
            trends[date]["fraud"] = item["fraud"]
            
    # Format for Recharts
    chart_data = []
    for date in sorted(trends.keys()):
        chart_data.append({
            "name": date,
            "alerts": trends[date]["alerts"],
            "fraud": trends[date]["fraud"],
            "total": trends[date]["total_transactions"]
        })
        
    # If no data, provide a small mock set to avoid empty charts
    if not chart_data:
        today = datetime.now()
        for i in range(7):
            date = (today - timedelta(days=6-i)).strftime("%Y-%m-%d")
            chart_data.append({"name": date, "alerts": 0, "fraud": 0, "total": 0})
            
    return chart_data
