from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.db.session import init_db
from app.api.api import api_router

app = FastAPI(
    title="Fraud Detection & Case Management API",
    redirect_slashes=False
)

# Initialize MongoDB with Beanie
@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
        print("MongoDB initialized successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Fraud Detection Platform API",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Backend API is running"}

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
