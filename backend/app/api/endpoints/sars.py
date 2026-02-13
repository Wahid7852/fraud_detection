from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from app.models.models import Case, Alert, Transaction, SAR

router = APIRouter()

class SARCreate(BaseModel):
    case_id: str
    filing_date: Optional[datetime] = None
    amount: float
    customer_name: Optional[str] = None
    description: str

class SARUpdate(BaseModel):
    status: Optional[str] = None
    filing_date: Optional[datetime] = None

@router.get("")
async def get_sars(
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get all SARs with optional filtering"""
    query = {}
    if status:
        query["status"] = status
    
    sars = await SAR.find(query).skip(skip).limit(limit).to_list()
    
    if not sars:
        return []

    # Bulk fetch cases
    case_ids = [s.case.ref.id for s in sars if s.case]
    cases = await Case.find({"_id": {"$in": case_ids}}).to_list()
    case_map = {c.id: c for c in cases}
    
    # Bulk fetch alerts for these cases
    alert_ids = [c.alert.ref.id for c in cases if c.alert]
    alerts = await Alert.find({"_id": {"$in": alert_ids}}).to_list()
    alert_map = {a.id: a for a in alerts}
    
    # Bulk fetch transactions for these alerts
    transaction_ids = [a.transaction.ref.id for a in alerts if a.transaction]
    transactions = await Transaction.find({"_id": {"$in": transaction_ids}}).to_list()
    trans_map = {t.id: t for t in transactions}
    
    # Assemble
    for sar in sars:
        if sar.case:
            case = case_map.get(sar.case.ref.id)
            if case:
                if case.alert:
                    alert = alert_map.get(case.alert.ref.id)
                    if alert:
                        if alert.transaction:
                            alert.transaction = trans_map.get(alert.transaction.ref.id)
                        case.alert = alert
                sar.case = case
    if search:
        search_lower = search.lower()
        sars = [
            s for s in sars
            if search_lower in (s.sar_id or '').lower() or
               (s.case and search_lower in str(s.case.id).lower())
        ]
    
    # Sort by created_at descending
    sars.sort(key=lambda x: x.created_at, reverse=True)
    
    return [
        {
            "id": str(s.id),
            "sar_id": s.sar_id,
            "case_id": str(s.case.id) if s.case else None,
            "customer_name": s.customer_name,
            "amount": s.amount,
            "status": s.status,
            "filing_date": s.filing_date.isoformat() if s.filing_date else None,
            "created_at": s.created_at.isoformat()
        }
        for s in sars
    ]

@router.get("/stats")
async def get_sar_stats():
    """Get SAR statistics"""
    total = await SAR.count()
    pending = await SAR.find(SAR.status == "Pending").count()
    filed = await SAR.find(SAR.status == "Filed").count()
    drafts = await SAR.find(SAR.status == "Draft").count()
    
    return {
        "pending_filings": pending,
        "successfully_filed": filed,
        "drafts": drafts,
        "total": total
    }

@router.post("/")
async def create_sar(sar_data: SARCreate):
    """Create a new SAR filing"""
    # Get case
    case = await Case.get(sar_data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Fetch alert and transaction to get amount
    amount = sar_data.amount
    customer_name = sar_data.customer_name
    
    if case.alert:
        alert = await Alert.get(case.alert.ref.id)
        if alert and alert.transaction:
            transaction = await Transaction.get(alert.transaction.ref.id)
            if transaction:
                # Use transaction amount if not provided or if provided amount is 0
                if amount <= 0:
                    amount = transaction.amount
                # Use customer ID for name if not provided
                if not customer_name:
                    customer_name = f"Customer-{transaction.customer_id}"
    
    # Generate SAR ID
    sar_count = await SAR.count()
    sar_id = f"SAR-{datetime.now().year}-{str(sar_count + 1).zfill(3)}"
    
    # Create SAR
    sar = SAR(
        sar_id=sar_id,
        case=case,
        customer_name=customer_name,
        amount=amount,
        status="Draft",
        filing_date=sar_data.filing_date,
        description=sar_data.description,
        created_at=datetime.now(timezone.utc)
    )
    
    await sar.insert()
    
    return {
        "id": str(sar.id),
        "sar_id": sar.sar_id,
        "message": "SAR created successfully"
    }

@router.get("/{sar_id}")
async def get_sar(sar_id: str):
    """Get a specific SAR by ID"""
    sar = await SAR.find_one(SAR.sar_id == sar_id)
    if not sar:
        # Try by MongoDB ID
        try:
            sar = await SAR.get(sar_id)
        except:
            raise HTTPException(status_code=404, detail="SAR not found")
    
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    
    # Fetch case
    if sar.case:
        sar.case = await Case.get(sar.case.ref.id)
    
    return {
        "id": str(sar.id),
        "sar_id": sar.sar_id,
        "case_id": str(sar.case.id) if sar.case else None,
        "customer_name": sar.customer_name,
        "amount": sar.amount,
        "status": sar.status,
        "filing_date": sar.filing_date.isoformat() if sar.filing_date else None,
        "description": sar.description,
        "created_at": sar.created_at.isoformat()
    }

@router.put("/{sar_id}")
async def update_sar(sar_id: str, update: SARUpdate):
    """Update SAR status or filing date"""
    sar = await SAR.find_one(SAR.sar_id == sar_id)
    if not sar:
        try:
            sar = await SAR.get(sar_id)
        except:
            raise HTTPException(status_code=404, detail="SAR not found")
    
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    
    if update.status:
        sar.status = update.status
    if update.filing_date:
        sar.filing_date = update.filing_date
    
    await sar.save()
    
    return {
        "id": str(sar.id),
        "sar_id": sar.sar_id,
        "status": sar.status,
        "message": "SAR updated successfully"
    }

@router.post("/{sar_id}/file")
async def file_sar(sar_id: str):
    """File a SAR (change status to Filed)"""
    sar = await SAR.find_one(SAR.sar_id == sar_id)
    if not sar:
        try:
            sar = await SAR.get(sar_id)
        except:
            raise HTTPException(status_code=404, detail="SAR not found")
    
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    
    sar.status = "Filed"
    sar.filing_date = datetime.now(timezone.utc)
    
    # Update case status
    if sar.case:
        case = await Case.get(sar.case.ref.id)
        if case:
            case.status = "SAR Filed"
            await case.save()
    
    await sar.save()
    
    return {
        "id": str(sar.id),
        "sar_id": sar.sar_id,
        "status": sar.status,
        "filing_date": sar.filing_date.isoformat(),
        "message": "SAR filed successfully"
    }

@router.get("/export/batch")
async def export_batch_sars(
    status: Optional[str] = None,
    format: str = Query("csv", description="Export format: csv, json")
):
    """Export SARs in batch"""
    query = {}
    if status:
        query["status"] = status
    
    sars = await SAR.find(query).to_list()
    
    export_data = []
    for s in sars:
        case_id = None
        if s.case:
            if hasattr(s.case, 'id'):
                case_id = str(s.case.id)
            elif hasattr(s.case, 'ref'):
                case_id = str(s.case.ref.id)
        export_data.append({
            "sar_id": s.sar_id,
            "case_id": case_id,
            "customer_name": s.customer_name,
            "amount": s.amount,
            "status": s.status,
            "filing_date": s.filing_date.isoformat() if s.filing_date else None,
            "created_at": s.created_at.isoformat()
        })
    
    if format == "json":
        return {"data": export_data}
    else:  # CSV
        import io
        import csv
        output = io.StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        return {"csv": output.getvalue()}
