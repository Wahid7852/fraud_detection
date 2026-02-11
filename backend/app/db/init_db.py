import pandas as pd
import os
from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.models.models import Transaction, Alert, Rule
import datetime

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        if db.query(Transaction).first() is None:
            print("Seeding database...")
            seed_data(db)
        else:
            print("Database already seeded.")
    finally:
        db.close()

def seed_data(db: Session):
    # Paths to data
    data_dir = "New folder/Data"
    
    # Load Transaction Data
    trans_records = pd.read_csv(os.path.join(data_dir, "Transaction Data/transaction_records.csv"))
    trans_meta = pd.read_csv(os.path.join(data_dir, "Transaction Data/transaction_metadata.csv"))
    fraud_inds = pd.read_csv(os.path.join(data_dir, "Fraudulent Patterns/fraud_indicators.csv"))
    categories = pd.read_csv(os.path.join(data_dir, "Merchant Information/transaction_category_labels.csv"))
    
    # Merge data
    df = trans_records.merge(trans_meta, on="TransactionID")
    df = df.merge(fraud_inds, on="TransactionID")
    df = df.merge(categories, on="TransactionID")
    
    # Limit to 100 records for initial seed to keep it fast
    df = df.head(100)
    
    for _, row in df.iterrows():
        # Create Transaction
        trans = Transaction(
            transaction_id=str(row['TransactionID']),
            amount=float(row['Amount']),
            customer_id=int(row['CustomerID']),
            timestamp=pd.to_datetime(row['Timestamp']),
            merchant_id=int(row['MerchantID']),
            category=row['Category'],
            transaction_type="Transfer" # Default for now
        )
        db.add(trans)
        db.flush() # Get the ID
        
        # If fraud indicator is 1, create an Alert
        if row['FraudIndicator'] == 1:
            alert = Alert(
                transaction_id=trans.id,
                risk_score=95, # High score for seed
                risk_level="Very High",
                status="Pending",
                assigned_queue="High Profile Queue"
            )
            db.add(alert)
            
    # Add some initial rules
    rules = [
        Rule(
            name="Large Transaction Rule",
            description="Alerts for transactions over $1000",
            score_impact=50,
            action="Review",
            is_active=True,
            conditions={"amount": {">": 1000}},
            priority=1
        ),
        Rule(
            name="Suspicious Category Rule",
            description="Alerts for transactions in 'Other' category",
            score_impact=20,
            action="Review",
            is_active=True,
            conditions={"category": {"==": "Other"}},
            priority=2
        )
    ]
    for rule in rules:
        db.add(rule)
        
    db.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    init_db()
