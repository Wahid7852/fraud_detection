from fastapi import APIRouter
from app.api.endpoints import dashboard, alerts, cases, rules, transactions, analysis, reports, sars

api_router = APIRouter(redirect_slashes=False)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(sars.router, prefix="/sars", tags=["sars"])
