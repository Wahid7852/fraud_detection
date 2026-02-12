
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.models import Transaction, Alert, Case, Rule, CaseNote
from app.core.config import MONGODB_URI, DATABASE_NAME

async def check_methods():
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[Transaction, Alert, Case, Rule, CaseNote]
    )
    
    alert = await Alert.find_one()
    if alert:
        print(f"Methods on Alert: {dir(alert)}")
    else:
        print("No alerts found")

if __name__ == "__main__":
    asyncio.run(check_methods())
