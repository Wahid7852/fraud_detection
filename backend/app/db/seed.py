from app.models.models import Transaction, Alert, Case, Rule
from datetime import datetime, timedelta, timezone
import random

async def seed_data():
    # 1. Seed Transactions if empty
    trans_count = await Transaction.count()
    if trans_count == 0:
        print("Seeding sample transactions...")
        categories = ["W", "H", "R", "S", "O"]
        types = ["debit", "credit"]
        for i in range(20):
            amount = round(random.uniform(50.0, 6000.0), 2)  # Ensure minimum amount of 50
            trans = Transaction(
                transaction_id=f"TX{1000+i}",
                amount=amount,
                customer_id=random.randint(10000, 99999),
                merchant_id=random.randint(1000, 9999),
                category=random.choice(categories),
                transaction_type=random.choice(types),
                timestamp=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7))
            )
            await trans.insert()

    # 2. Seed Alerts if empty
    alert_count = await Alert.count()
    if alert_count == 0:
        print("Seeding sample alerts...")
        transactions = await Transaction.find_all().to_list()
        for i in range(5):
            trans = transactions[i]
            risk_score = random.randint(75, 99)
            risk_level = "High" if risk_score > 85 else "Medium"
            alert = Alert(
                transaction=trans,
                risk_score=risk_score,
                risk_level=risk_level,
                status="Pending",
                assigned_queue=random.choice(["High Profile", "High Velocity", "New Accounts"]),
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24))
            )
            await alert.insert()

    # 3. Seed Cases if empty
    case_count = await Case.count()
    if case_count == 0:
        print("Seeding sample cases...")
        alerts = await Alert.find_all().to_list()
        for i in range(min(3, len(alerts))):
            alert = alerts[i]
            case = Case(
                alert=alert,
                status=random.choice(["Open", "In Progress"]),
                analyst_id=random.randint(1, 5),
                created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 12)),
                updated_at=datetime.now(timezone.utc)
            )
            await case.insert()
            # Update alert status if it's in a case
            alert.status = "Reviewed"
            await alert.save()

    print("Data seeding completed successfully.")
