import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fraud_detection")

async def init_db():
    if not MONGODB_URI:
        print("MONGODB_URI not set. Skipping database initialization.")
        return

    # Create Motor client
    client = AsyncIOMotorClient(MONGODB_URI)
    
    # Import models here to avoid circular imports
    from app.models.models import Transaction, Alert, Case, CaseNote, Rule
    
    # Initialize beanie with document models in dependency order
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            Transaction,
            CaseNote,
            Alert,
            Case,
            Rule
        ]
    )
