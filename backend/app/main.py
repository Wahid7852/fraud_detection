from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import List

from app.db.session import init_db
from app.api.api import api_router
from app.models.models import Rule
from app.db.seed import seed_data
from datetime import datetime

async def seed_rules():
    # Check if rules already exist
    count = await Rule.count()
    if count == 0:
        print("Seeding baseline fraud detection rules...")
        baseline_rules = [
            Rule(
                name="High Value Transaction",
                description="Flags transactions over $5,000 as high risk",
                score_impact=50,
                action="Review",
                conditions={"amount": {">": 5000}},
                priority=1
            ),
            Rule(
                name="Velocity Check",
                description="Flags rapid successive transactions from the same card",
                score_impact=70,
                action="Review",
                conditions={"velocity": {">": 3, "window": "10m"}},
                priority=2
            ),
            Rule(
                name="Category Mismatch",
                description="Flags mismatch between purchaser and receiver email domains",
                score_impact=40,
                action="Review",
                conditions={"email_mismatch": True},
                priority=3
            )
        ]
        for rule in baseline_rules:
            await rule.insert()

app = FastAPI(title="Fraud Detection & Case Management API")

# Initialize MongoDB with Beanie
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
        print("MongoDB initialized successfully")
        await seed_rules()
        await seed_data()
    except Exception as e:
        print(f"Error during database initialization: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend API is running"}

@app.get("/api/docs", include_in_schema=False)
async def api_docs_redirect():
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return {"message": "Not found"}

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
