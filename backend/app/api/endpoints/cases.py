from fastapi import APIRouter, HTTPException
from typing import List
from beanie import PydanticObjectId
from app.models.models import Case, Alert, Transaction
from app.schemas.schemas import Case as CaseSchema

router = APIRouter()

@router.get("/", response_model=List[CaseSchema])
async def get_cases():
    cases = await Case.find_all().to_list()
    for case in cases:
        if case.alert:
            # Manually fetch the alert link
            alert = await Alert.get(case.alert.ref.id)
            if alert:
                # Also fetch the transaction for the alert if needed
                if alert.transaction:
                    alert.transaction = await Transaction.get(alert.transaction.ref.id)
                case.alert = alert
    return [CaseSchema.model_validate(c) for c in cases]

@router.get("/{case_id}", response_model=CaseSchema)
async def get_case(case_id: str):
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    await case.fetch_all_links()
    return CaseSchema.model_validate(case)

@router.post("/{case_id}/status")
async def update_case_status(case_id: str, status: str):
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = status
    await case.save()
    return {"message": f"Case {case_id} status updated to {status}"}
