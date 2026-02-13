from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from app.models.models import Case, Alert, Transaction, CaseNote, SAR
from app.schemas.schemas import Case as CaseSchema

router = APIRouter()

class CaseUpdate(BaseModel):
    status: Optional[str] = None
    analyst_id: Optional[int] = None

class CaseNoteCreate(BaseModel):
    case_id: str
    note: str
    analyst_id: int

@router.get("", response_model=List[CaseSchema])
async def get_cases(
    status: Optional[str] = None,
    analyst_id: Optional[int] = None,
    search: Optional[str] = None
):
    """Get all cases with optional filtering"""
    query = {}
    if status:
        query["status"] = status
    if analyst_id:
        query["analyst_id"] = analyst_id
    
    cases = await Case.find(query).to_list()
    
    if not cases:
        return []

    # Bulk fetch alerts
    alert_ids = [c.alert.ref.id for c in cases if c.alert]
    alerts = await Alert.find({"_id": {"$in": alert_ids}}).to_list()
    alert_map = {a.id: a for a in alerts}
    
    # Bulk fetch transactions for those alerts
    transaction_ids = [a.transaction.ref.id for a in alerts if a.transaction]
    transactions = await Transaction.find({"_id": {"$in": transaction_ids}}).to_list()
    trans_map = {t.id: t for t in transactions}
    
    # Fetch notes in bulk if needed, but notes are usually few
    # For now, let's just assemble cases
    for case in cases:
        if case.alert:
            alert = alert_map.get(case.alert.ref.id)
            if alert:
                if alert.transaction:
                    alert.transaction = trans_map.get(alert.transaction.ref.id)
                case.alert = alert
        
        # Notes are still fetched per case because they are unique to the case
        if case.notes:
            case.notes = [await CaseNote.get(note.ref.id) for note in case.notes if note.ref]
    
    # Apply search filter if provided
    if search:
        search_lower = search.lower()
        cases = [
            c for c in cases
            if search_lower in str(c.id).lower() or
               (c.alert and c.alert.transaction and search_lower in str(c.alert.transaction.transaction_id).lower())
        ]
    
    return [CaseSchema.model_validate(c) for c in cases]

@router.get("/{case_id}", response_model=CaseSchema)
async def get_case(case_id: str):
    """Get a specific case by ID"""
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Manually fetch links instead of using fetch_all_links
    if case.alert:
        alert = await Alert.get(case.alert.ref.id)
        if alert:
            # Fetch transaction if it exists (check if it's a Link object)
            if alert.transaction:
                try:
                    if hasattr(alert.transaction, 'ref'):
                        transaction = await Transaction.get(alert.transaction.ref.id)
                    else:
                        transaction = alert.transaction
                    if transaction:
                        alert.transaction = transaction
                    else:
                        alert.transaction = None
                except Exception:
                    alert.transaction = None
            case.alert = alert
    
    # Fetch all notes
    if case.notes:
        case.notes = [await CaseNote.get(note.ref.id) for note in case.notes if note.ref]
    
    return CaseSchema.model_validate(case)

@router.put("/{case_id}", response_model=CaseSchema)
async def update_case(case_id: str, update: CaseUpdate):
    """Update case status or analyst assignment"""
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if update.status:
        case.status = update.status
    if update.analyst_id is not None:
        case.analyst_id = update.analyst_id
    
    case.updated_at = datetime.now(timezone.utc)
    await case.save()
    
    # Manually fetch links instead of using fetch_all_links (which has issues)
    if case.alert:
        alert = await Alert.get(case.alert.ref.id)
        if alert:
            # Fetch transaction if it exists (check if it's a Link object)
            if alert.transaction:
                try:
                    # Check if it's a Link object (has 'ref' attribute)
                    if hasattr(alert.transaction, 'ref'):
                        transaction = await Transaction.get(alert.transaction.ref.id)
                    else:
                        # Already a Transaction object
                        transaction = alert.transaction
                    
                    if transaction:
                        alert.transaction = transaction
                    else:
                        alert.transaction = None
                except Exception as e:
                    # If transaction fetch fails, set to None
                    print(f"Error fetching transaction: {e}")
                    alert.transaction = None
            case.alert = alert
    
    # Fetch notes if any
    if case.notes:
        fetched_notes = []
        for note in case.notes:
            if note.ref:
                try:
                    fetched_note = await CaseNote.get(note.ref.id)
                    if fetched_note:
                        fetched_notes.append(fetched_note)
                except Exception:
                    continue
        case.notes = fetched_notes
    
    return CaseSchema.model_validate(case)

@router.post("/notes", response_model=dict)
async def add_note(note_data: CaseNoteCreate):
    """Add a note to a case"""
    case = await Case.get(note_data.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Create note
    note = CaseNote(
        note=note_data.note,
        analyst_id=note_data.analyst_id,
        created_at=datetime.now(timezone.utc)
    )
    await note.insert()
    
    # Add note to case
    if not case.notes:
        case.notes = []
    case.notes.append(note)
    case.updated_at = datetime.now(timezone.utc)
    await case.save()
    
    return {"message": "Note added successfully", "note_id": str(note.id)}

@router.post("/{case_id}/assign", response_model=CaseSchema)
async def assign_analyst(case_id: str, analyst_id: int = Body(...)):
    """Assign an analyst to a case"""
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.analyst_id = analyst_id
    case.updated_at = datetime.now(timezone.utc)
    await case.save()
    
    # Manually fetch links
    if case.alert:
        alert = await Alert.get(case.alert.ref.id)
        if alert:
            # Fetch transaction if it exists (check if it's a Link object)
            if alert.transaction:
                try:
                    if hasattr(alert.transaction, 'ref'):
                        transaction = await Transaction.get(alert.transaction.ref.id)
                    else:
                        transaction = alert.transaction
                    if transaction:
                        alert.transaction = transaction
                    else:
                        alert.transaction = None
                except Exception:
                    alert.transaction = None
            case.alert = alert
    
    return CaseSchema.model_validate(case)
