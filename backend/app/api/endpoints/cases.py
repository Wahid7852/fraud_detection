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

@router.get("/", response_model=List[CaseSchema])
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
    
    # Fetch related data
    for case in cases:
        if case.alert:
            alert = await Alert.get(case.alert.ref.id)
            if alert:
                if alert.transaction:
                    alert.transaction = await Transaction.get(alert.transaction.ref.id)
                case.alert = alert
        
        # Fetch notes
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
            case.alert = alert
            if alert.transaction:
                transaction = await Transaction.get(alert.transaction.ref.id)
                if transaction:
                    alert.transaction = transaction
    
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
            case.alert = alert
            if alert.transaction:
                transaction = await Transaction.get(alert.transaction.ref.id)
                if transaction:
                    alert.transaction = transaction
    
    # Fetch notes if any
    if case.notes:
        case.notes = [await CaseNote.get(note.ref.id) for note in case.notes if note.ref]
    
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
            case.alert = alert
            if alert.transaction:
                transaction = await Transaction.get(alert.transaction.ref.id)
                if transaction:
                    alert.transaction = transaction
    
    return CaseSchema.model_validate(case)
