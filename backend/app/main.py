from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app.db.session import engine, Base, get_db
from app.models import models
from app.schemas import schemas # Need to create this
from app.api.api import api_router

app = FastAPI(title="Fraud Detection & Case Management API")

# Create tables (moved to startup event for better reliability)
@app.on_event("startup")
def startup_event():
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error during database initialization: {e}")
        # We don't raise here so the app can at least start, 
        # but subsequent DB calls will fail with descriptive errors.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fraud Detection Platform API"}

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
