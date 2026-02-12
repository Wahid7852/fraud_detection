from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.models import Transaction, Alert, Case
import pandas as pd
import json

router = APIRouter()

class ReportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    report_type: str = "summary"  # summary, detailed, trends

@router.get("/templates")
async def get_report_templates():
    """Get available report templates"""
    return [
        {
            "id": "monthly_summary",
            "title": "Monthly Fraud Summary",
            "description": "Comprehensive overview of fraud trends and metrics for the current month",
            "format": ["PDF", "CSV", "XLSX"]
        },
        {
            "id": "analyst_performance",
            "title": "Analyst Performance",
            "description": "Metrics on case resolution time and accuracy across the investigation team",
            "format": ["PDF", "CSV", "XLSX"]
        },
        {
            "id": "rule_effectiveness",
            "title": "Rule Effectiveness",
            "description": "Analysis of false positive and true positive rates for all active detection rules",
            "format": ["PDF", "CSV", "XLSX"]
        },
        {
            "id": "regional_risk",
            "title": "Regional Risk Heatmap",
            "description": "Geographical distribution of fraud attempts and successful preventions",
            "format": ["PDF", "CSV", "JSON"]
        }
    ]

@router.post("/generate")
async def generate_report(request: ReportRequest):
    """Generate a custom report"""
    # Set default date range if not provided
    end_date = request.end_date or datetime.now()
    start_date = request.start_date or (end_date - timedelta(days=30))
    
    # Fetch data based on date range
    transactions = await Transaction.find(
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    ).to_list()
    
    alerts = await Alert.find_all().to_list()
    cases = await Case.find_all().to_list()
    
    # Filter alerts and cases by transaction dates
    alert_ids = {str(a.transaction.ref.id) for a in alerts if a.transaction}
    relevant_transactions = [t for t in transactions if str(t.id) in alert_ids]
    
    # Calculate metrics
    total_transactions = len(transactions)
    total_alerts = len(alerts)
    total_cases = len(cases)
    fraud_amount = sum(t.amount for t in relevant_transactions)
    
    # Calculate fraud rate
    fraud_rate = (total_alerts / total_transactions * 100) if total_transactions > 0 else 0
    
    # Case status breakdown
    case_statuses = {}
    for case in cases:
        status = case.status
        case_statuses[status] = case_statuses.get(status, 0) + 1
    
    # Alert risk level breakdown
    risk_levels = {}
    for alert in alerts:
        level = alert.risk_level
        risk_levels[level] = risk_levels.get(level, 0) + 1
    
    # Generate report data
    report_data = {
        "report_type": request.report_type,
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "summary": {
            "total_transactions": total_transactions,
            "total_alerts": total_alerts,
            "total_cases": total_cases,
            "fraud_rate": round(fraud_rate, 2),
            "fraud_amount": round(fraud_amount, 2)
        },
        "case_status_breakdown": case_statuses,
        "risk_level_breakdown": risk_levels,
        "generated_at": datetime.now().isoformat()
    }
    
    return report_data

@router.get("/trends")
async def get_trends(
    days: int = Query(30, description="Number of days to analyze"),
    group_by: str = Query("day", description="Group by: day, week, month")
):
    """Get fraud trends over time"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Fetch transactions and alerts
    transactions = await Transaction.find(
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    ).to_list()
    
    alerts = await Alert.find_all().to_list()
    
    # Create a set of transaction IDs that have alerts (for faster lookup)
    alert_transaction_ids = set()
    for alert in alerts:
        if alert.transaction:
            try:
                # Get transaction ID from the link
                if hasattr(alert.transaction, 'ref'):
                    alert_transaction_ids.add(str(alert.transaction.ref.id))
                elif hasattr(alert.transaction, 'id'):
                    alert_transaction_ids.add(str(alert.transaction.id))
            except:
                pass
    
    # Group by time period
    trends = {}
    for transaction in transactions:
        if group_by == "day":
            key = transaction.timestamp.date().isoformat()
        elif group_by == "week":
            week_start = transaction.timestamp - timedelta(days=transaction.timestamp.weekday())
            key = week_start.date().isoformat()
        else:  # month
            key = transaction.timestamp.strftime("%Y-%m")
        
        if key not in trends:
            trends[key] = {"total": 0, "fraud": 0, "amount": 0.0}
        
        trends[key]["total"] += 1
        trends[key]["amount"] += transaction.amount
        
        # Check if this transaction has an alert (using set for O(1) lookup)
        if str(transaction.id) in alert_transaction_ids:
            trends[key]["fraud"] += 1
    
    # Convert to list format
    trend_list = [
        {
            "date": key,
            "total": val["total"],
            "fraud": val["fraud"],
            "legit": val["total"] - val["fraud"],
            "amount": round(val["amount"], 2)
        }
        for key, val in sorted(trends.items())
    ]
    
    return trend_list

@router.get("/stats")
async def get_report_stats():
    """Get current statistics for dashboard"""
    total_transactions = await Transaction.count()
    total_alerts = await Alert.count()
    total_cases = await Case.count()
    
    # Calculate fraud rate
    fraud_rate = (total_alerts / total_transactions * 100) if total_transactions > 0 else 0
    
    # Calculate average fraud score
    alerts = await Alert.find_all().to_list()
    avg_risk_score = sum(a.risk_score for a in alerts) / len(alerts) if alerts else 0
    
    # Calculate false positive rate (simplified - cases closed without SAR)
    closed_cases = await Case.find(Case.status == "Closed").to_list()
    sar_cases = await Case.find(Case.status == "SAR Filed").to_list()
    false_positive_rate = (len(closed_cases) / total_cases * 100) if total_cases > 0 else 0
    
    # Calculate detection rate
    detection_rate = (total_alerts / total_transactions * 100) if total_transactions > 0 else 0
    
    return {
        "avg_fraud_score": round(avg_risk_score, 2),
        "false_positive_rate": round(false_positive_rate, 2),
        "detection_rate": round(detection_rate, 2),
        "approval_rate": round(100 - false_positive_rate, 2),
        "false_negative_rate": round(1.2, 2)  # Placeholder
    }

@router.get("/export")
async def export_report(
    format: str = Query("csv", description="Export format: csv, json"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Export report data"""
    end_date = end_date or datetime.now()
    start_date = start_date or (end_date - timedelta(days=30))
    
    # Fetch data
    transactions = await Transaction.find(
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    ).to_list()
    
    alerts = await Alert.find_all().to_list()
    
    # Prepare export data
    export_data = []
    for transaction in transactions:
        # Find associated alert
        alert = None
        for a in alerts:
            if a.transaction and str(a.transaction.ref.id) == str(transaction.id):
                alert = a
                break
        
        export_data.append({
            "transaction_id": transaction.transaction_id,
            "amount": transaction.amount,
            "customer_id": transaction.customer_id,
            "timestamp": transaction.timestamp.isoformat(),
            "category": transaction.category,
            "risk_score": alert.risk_score if alert else 0,
            "risk_level": alert.risk_level if alert else "Low",
            "status": alert.status if alert else "None"
        })
    
    if format == "json":
        return {"data": export_data}
    else:  # CSV
        # Convert to CSV string
        import io
        output = io.StringIO()
        if export_data:
            df = pd.DataFrame(export_data)
            df.to_csv(output, index=False)
        return {"csv": output.getvalue()}

