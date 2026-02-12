import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
import random

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import init_db
from app.models.models import Transaction, Alert

async def seed_alerts():
    await init_db()
    
    # Check if we already have alerts
    count = await Alert.count()
    if count > 0:
        print(f"Found {count} alerts already. Skipping seeding.")
        return

    print("Seeding sample transactions and alerts...")
    
    # Sample categories and merchants
    categories = ["Retail", "Food", "Entertainment", "Travel", "Electronics"]
    merchants = [101, 102, 103, 104, 105]
    
    # Create some transactions
    for i in range(10):
        tx_id = f"TXN-{random.randint(100000, 999999)}"
        amount = round(random.uniform(10.0, 6000.0), 2)
        customer_id = random.randint(1000, 2000)
        
        tx = Transaction(
            transaction_id=tx_id,
            amount=amount,
            customer_id=customer_id,
            merchant_id=random.choice(merchants),
            category=random.choice(categories),
            transaction_type="PAYMENT",
            timestamp=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48))
        )
        await tx.insert()
        
        # Create alert for high value or random ones
        if amount > 1000 or random.random() > 0.7:
            risk_score = int((amount / 6000) * 100) if amount > 1000 else random.randint(30, 70)
            risk_level = "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low"
            
            alert = Alert(
                transaction=tx,
                risk_score=risk_score,
                risk_level=risk_level,
                status="Pending",
                assigned_queue="Fraud Queue" if risk_score > 60 else "General"
            )
            await alert.insert()
            print(f"Created alert for transaction {tx_id} with risk score {risk_score}")

    print("Seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_alerts())
