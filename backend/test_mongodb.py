"""
Quick script to test MongoDB connection
Run this before running the ingestion script
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017"

async def test_connection():
    print("Testing MongoDB connection...")
    print(f"Connection URL: {MONGODB_URL.replace('://', '://***:***@') if '@' in MONGODB_URL else MONGODB_URL}")
    print()
    
    try:
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("✓ SUCCESS: MongoDB is running and accessible!")
        print(f"✓ Connected to: {MONGODB_URL}")
        
        # List databases
        db_list = await client.list_database_names()
        print(f"✓ Available databases: {', '.join(db_list) if db_list else 'None'}")
        
        return True
    except Exception as e:
        print("✗ FAILED: MongoDB connection error!")
        print(f"  Error: {e}")
        print()
        print("="*60)
        print("SOLUTIONS:")
        print("="*60)
        print()
        print("Option 1: Start Local MongoDB")
        print("  - Windows: Open Services → Start 'MongoDB' service")
        print("  - Or run: mongod --dbpath C:\\data\\db")
        print()
        print("Option 2: Use MongoDB Atlas (Cloud)")
        print("  - Sign up: https://www.mongodb.com/cloud/atlas")
        print("  - Get connection string")
        print("  - Set: export MONGODB_URL='your-connection-string'")
        print()
        print("Option 3: Use Docker")
        print("  - docker run -d -p 27017:27017 --name mongodb mongo:latest")
        print()
        print("See backend/SETUP_MONGODB.md for detailed instructions")
        print("="*60)
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)

