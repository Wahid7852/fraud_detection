# MongoDB Setup Guide

## Option 1: Local MongoDB Installation

### Windows:
1. **Download MongoDB Community Server**
   - Visit: https://www.mongodb.com/try/download/community
   - Select: Windows, MSI package
   - Install with default settings

2. **Start MongoDB Service**
   - Open Services (Win + R, type `services.msc`)
   - Find "MongoDB" service
   - Right-click → Start
   - Or set it to "Automatic" startup

3. **Verify Installation**
   ```bash
   mongod --version
   ```

4. **Manual Start (if service doesn't work)**
   ```bash
   # Create data directory
   mkdir C:\data\db
   
   # Start MongoDB
   mongod --dbpath C:\data\db
   ```

### macOS:
```bash
# Install via Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community
```

### Linux:
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

## Option 2: MongoDB Atlas (Cloud - Recommended)

1. **Create Free Account**
   - Visit: https://www.mongodb.com/cloud/atlas
   - Sign up for free tier (512MB storage)

2. **Create Cluster**
   - Click "Build a Database"
   - Choose free tier (M0)
   - Select region closest to you

3. **Create Database User**
   - Go to "Database Access"
   - Add new user with username/password
   - Save credentials

4. **Whitelist IP**
   - Go to "Network Access"
   - Add IP: `0.0.0.0/0` (for development) or your IP

5. **Get Connection String**
   - Go to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy connection string
   - Format: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/`

6. **Set Environment Variable**
   ```bash
   # Windows PowerShell
   $env:MONGODB_URL="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/fraud_detection"
   
   # Windows CMD
   set MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/fraud_detection
   
   # Linux/macOS
   export MONGODB_URL="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/fraud_detection"
   ```

## Option 3: Docker (Quick Start)

```bash
# Run MongoDB in Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify it's running
docker ps
```

## Verify Connection

After setting up MongoDB, test the connection:

```python
# Test script
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        await client.admin.command('ping')
        print("✓ MongoDB is running!")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")

asyncio.run(test_connection())
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONGODB_URL=mongodb://localhost:27017
# OR for Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/fraud_detection

DB_NAME=fraud_detection
```

## Troubleshooting

### "Connection refused" error:
- MongoDB service is not running
- Check: `mongod --version` or `brew services list` (macOS)
- Start the service manually

### "Authentication failed":
- Check username/password in connection string
- Verify database user has proper permissions

### Port 27017 already in use:
- Another MongoDB instance is running
- Change port: `mongod --port 27018`
- Update MONGODB_URL accordingly

