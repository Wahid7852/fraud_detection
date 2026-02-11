from fastapi import APIRouter, HTTPException
from typing import List
from app.models.models import Alert
from app.schemas.schemas import Alert as AlertSchema

router = APIRouter()

@router.get("/", response_model=List[AlertSchema])
async def get_alerts(skip: int = 0, limit: int = 100):
    # Use fetch_links() to include linked Transaction data
    alerts = await Alert.find_all().skip(skip).limit(limit).fetch_links().to_list()
    return alerts

@router.get("/{alert_id}", response_model=AlertSchema)
async def get_alert(alert_id: str):
    alert = await Alert.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await alert.fetch_links()
    return alert

@router.post("/{alert_id}/action")
async def alert_action(alert_id: str, action: str):
    alert = await Alert.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = action
    await alert.save()
    return {"message": f"Alert {alert_id} {action}ed successfully"}
