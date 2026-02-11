
import os
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal, engine
from backend.app.models.models import Base, Transaction, Alert, Case, Rule
import datetime

# Absolute path to the data folder
DATA_PATH = r"c:\Users\Wahid Khan\Desktop\g_project\New folder\Data"

def ingest_data():
    db = SessionLocal()
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Alert).delete()
        db.query(Transaction).delete()
        db.query(Case).delete()
        db.query(Rule).delete()
        db.commit()

        print(f"Loading data from {DATA_PATH}...")

        # Load CSVs
        tx_records = pd.read_csv(os.path.join(DATA_PATH, "Transaction Data", "transaction_records.csv"))
        tx_metadata = pd.read_csv(os.path.join(DATA_PATH, "Transaction Data", "transaction_metadata.csv"))
        tx_categories = pd.read_csv(os.path.join(DATA_PATH, "Merchant Information", "transaction_category_labels.csv"))
        fraud_inds = pd.read_csv(os.path.join(DATA_PATH, "Fraudulent Patterns", "fraud_indicators.csv"))
        customer_accounts = pd.read_csv(os.path.join(DATA_PATH, "Customer Profiles", "account_activity.csv"))

        # Merge transaction data
        df = tx_records.merge(tx_metadata, on="TransactionID")
        df = df.merge(tx_categories, on="TransactionID")
        df = df.merge(fraud_inds, on="TransactionID")
        
        # Merge customer data for balance
        df = df.merge(customer_accounts, on="CustomerID", how="left")

        print(f"Ingesting {len(df)} transactions...")

        for _, row in df.iterrows():
            # Create transaction
            tx = Transaction(
                transaction_id=str(row['TransactionID']),
                amount=float(row['Amount']),
                customer_id=int(row['CustomerID']),
                timestamp=pd.to_datetime(row['Timestamp']),
                merchant_id=int(row['MerchantID']),
                category=row['Category'],
                transaction_type="PAYMENT", # Defaulting as not in CSV
                old_balance_orig=float(row['AccountBalance']) if not pd.isna(row['AccountBalance']) else 0.0,
                new_balance_orig=(float(row['AccountBalance']) - float(row['Amount'])) if not pd.isna(row['AccountBalance']) else 0.0,
            )
            db.add(tx)
            db.flush() # Get the ID

            # If it's flagged as fraud in the dataset, create an alert
            if row['FraudIndicator'] == 1:
                risk_score = np.random.randint(75, 100)
                alert = Alert(
                    transaction_id=tx.id,
                    risk_score=risk_score,
                    risk_level="High" if risk_score < 90 else "Very High",
                    status="Pending",
                    assigned_queue="Fraud Queue",
                )
                db.add(alert)
                db.flush()

                # Also create a case for high risk
                if risk_score > 85:
                    case = Case(
                        alert_id=alert.id,
                        status="Open",
                        analyst_id=None
                    )
                    db.add(case)

        # Add some default rules
        default_rules = [
            Rule(name="High Amount Transaction", description="Transactions over $500", score_impact=40, action="Review", conditions={"field": "amount", "operator": ">", "value": 500}),
            Rule(name="New Merchant", description="First time transaction with merchant", score_impact=20, action="Review", conditions={"field": "merchant_id", "operator": "new", "value": True}),
            Rule(name="Unusual Category", description="Transaction in high-risk category", score_impact=30, action="Review", conditions={"field": "category", "operator": "in", "value": ["Gaming", "Crypto"]})
        ]
        db.add_all(default_rules)

        db.commit()
        print("Data ingestion completed successfully!")

    except Exception as e:
        print(f"Error during ingestion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_data()
