from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.models.models import Transaction, Alert, Case, Report
from app.services.llm_service import llm_service
from app.core.cache import cached
import pandas as pd
import json

router = APIRouter()

class ReportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    report_type: str = "summary"  # summary, detailed, trends

@router.get("/list", response_model=List[Report])
async def list_reports(
    limit: int = Query(10, description="Number of reports to fetch"),
    report_type: Optional[str] = None
):
    """List recently generated reports"""
    query = Report.find_all()
    if report_type:
        query = query.find(Report.report_type == report_type)
    
    return await query.sort(-Report.generated_at).limit(limit).to_list()

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
    """Generate a custom report or fetch from DB if recent"""
    # Set default date range if not provided
    end_date = request.end_date or datetime.now()
    start_date = request.start_date or (end_date - timedelta(days=30))
    
    # Normalize dates for lookup
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Check for recent pre-generated report (last 24 hours)
    one_day_ago = datetime.now() - timedelta(hours=24)
    existing_report = await Report.find_one(
        Report.report_type == request.report_type,
        Report.period_start == start_date,
        Report.period_end == end_date,
        Report.generated_at >= one_day_ago
    )
    
    if existing_report:
        print(f"Fetching pre-generated {request.report_type} report from DB")
        return existing_report

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
    
    summary_data = {
        "total_transactions": total_transactions,
        "total_alerts": total_alerts,
        "total_cases": total_cases,
        "fraud_rate": round(fraud_rate, 2),
        "fraud_amount": round(fraud_amount, 2)
    }

    # Generate AI Executive Summary using free model
    print("Generating AI Executive Summary for new report...")
    prompt = f"""
    As a fraud management expert, provide a concise executive summary (3-4 sentences) for the following fraud report metrics:
    Metrics: {json.dumps(summary_data)}
    Case Breakdown: {json.dumps(case_statuses)}
    Risk Breakdown: {json.dumps(risk_levels)}
    
    Focus on the fraud rate, total amount at risk, and case resolution efficiency.
    """
    
    messages = [
        {"role": "system", "content": "You are a professional fraud detection consultant. Provide clear, data-driven summaries."},
        {"role": "user", "content": prompt}
    ]
    
    executive_summary = await llm_service.get_completion(messages)
    
    # Store the report in DB for future instant fetching
    new_report = Report(
        report_type=request.report_type,
        period_start=start_date,
        period_end=end_date,
        summary=summary_data,
        case_status_breakdown=case_statuses,
        risk_level_breakdown=risk_levels,
        executive_summary=executive_summary,
        generated_at=datetime.now()
    )
    await new_report.insert()
    
    return new_report

@router.get("/trends")
@cached(ttl=60)
async def get_trends(
    days: int = Query(30, description="Number of days to analyze"),
    group_by: str = Query("day", description="Group by: day, week, month")
):
    """Get fraud trends over time"""
    try:
        # Get all transactions and alerts (don't filter by date to show all data)
        all_transactions = await Transaction.find_all().to_list()
        all_alerts = await Alert.find_all().to_list()
        
        # Build a set of transaction IDs that have alerts
        alert_transaction_ids = set()
        for alert in all_alerts:
            if alert.transaction:
                try:
                    if hasattr(alert.transaction, 'ref'):
                        transaction_id = str(alert.transaction.ref.id)
                        alert_transaction_ids.add(transaction_id)
                    elif hasattr(alert.transaction, 'id'):
                        transaction_id = str(alert.transaction.id)
                        alert_transaction_ids.add(transaction_id)
                except:
                    continue
        
        # Group by time period - process all transactions to get actual dates
        trends = {}
        
        # Process all transactions to build trends from actual data
        for transaction in all_transactions:
            if not transaction.timestamp:
                continue
                
            try:
                trans_date = transaction.timestamp.date()
                
                if group_by == "day":
                    key = trans_date.isoformat()
                elif group_by == "week":
                    week_start = trans_date - timedelta(days=trans_date.weekday())
                    key = week_start.isoformat()
                else:  # month
                    key = transaction.timestamp.strftime("%Y-%m")
                
                if key not in trends:
                    trends[key] = {"total": 0, "fraud": 0, "amount": 0.0}
                
                trends[key]["total"] += 1
                trends[key]["amount"] += transaction.amount or 0.0
                
                # Check if this transaction has an alert
                if str(transaction.id) in alert_transaction_ids:
                    trends[key]["fraud"] += 1
            except Exception as e:
                continue
        
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
        
        # If no data, return empty structure for last 7 days
        if not trend_list:
            today = datetime.now().date()
            trend_list = [
                {
                    "date": (today - timedelta(days=i)).isoformat(),
                    "total": 0,
                    "fraud": 0,
                    "legit": 0,
                    "amount": 0.0
                }
                for i in range(6, -1, -1)
            ]
        
        return trend_list
    except Exception as e:
        # Return empty data on error instead of crashing
        import traceback
        print(f"Error in get_trends: {e}")
        print(traceback.format_exc())
        today = datetime.now().date()
        return [
            {
                "date": (today - timedelta(days=i)).isoformat(),
                "total": 0,
                "fraud": 0,
                "legit": 0,
                "amount": 0.0
            }
            for i in range(6, -1, -1)
        ]

@router.get("/stats")
@cached(ttl=60)
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

