from fastapi import APIRouter
from .endpoints import dashboard, alerts, cases, rules, transactions

api_router = APIRouter()
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
