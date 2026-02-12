"""
Ingest Kaggle IEEE-CIS Fraud Detection dataset into MongoDB
Processes train_transaction.csv and train_identity.csv
Optimized with progress bar and batch processing
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.models import Transaction, Alert, Case, Rule, CaseNote, SAR
from app.fraud_engine.scoring.scorer import Scorer

# Try to import tqdm for progress bar, fallback to simple progress if not available
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Note: Install 'tqdm' for better progress bars: pip install tqdm")

# Configuration
SOURCES_DIR = r'c:\Users\Wahid Khan\Desktop\g_project\sources'
MONGODB_URL = os.getenv("MONGODB_URL") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME", "fraud_detection")

# Print configuration for debugging
print(f"MongoDB URL: {MONGODB_URL.replace('://', '://***:***@') if '@' in MONGODB_URL else MONGODB_URL}")
print(f"Database: {DB_NAME}")

# Key features to extract from transaction data
TRANSACTION_FEATURES = [
    'TransactionID', 'isFraud', 'TransactionDT', 'TransactionAmt',
    'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6',
    'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14',
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15',
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9'
]

IDENTITY_FEATURES = [
    'TransactionID', 'id_01', 'id_02', 'id_03', 'id_04', 'id_05', 'id_06', 'id_07', 'id_08', 'id_09', 'id_10',
    'id_11', 'id_12', 'id_13', 'id_14', 'id_15', 'id_16', 'id_17', 'id_18', 'id_19', 'id_20',
    'DeviceType', 'DeviceInfo'
]

async def init_database():
    """Initialize MongoDB connection and Beanie"""
    try:
        # Test connection first
        client = AsyncIOMotorClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print(f"✓ MongoDB connection successful")
    except Exception as e:
        print("\n" + "="*60)
        print("ERROR: MongoDB is not running or not accessible!")
        print("="*60)
        print(f"\nConnection error: {e}")
        print("\nTo fix this, you need to:")
        print("1. Install MongoDB (if not installed):")
        print("   - Download from: https://www.mongodb.com/try/download/community")
        print("   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas")
        print("\n2. Start MongoDB locally:")
        print("   - Windows: Open Services and start 'MongoDB' service")
        print("   - Or run: mongod --dbpath <your-data-path>")
        print("\n3. Or set MONGODB_URL environment variable to a cloud MongoDB:")
        print("   - MongoDB Atlas: mongodb+srv://user:pass@cluster.mongodb.net/")
        print("   - Set: export MONGODB_URL='your-connection-string'")
        print("\n4. Current MONGODB_URL:", MONGODB_URL)
        print("="*60)
        raise
    
    await init_beanie(database=client[DB_NAME], document_models=[Transaction, Alert, Case, Rule, CaseNote, SAR])
    print(f"✓ Connected to database: {DB_NAME}")

def convert_transaction_dt(dt_value):
    """Convert TransactionDT (seconds from reference) to datetime"""
    # Reference date is 2017-12-01 00:00:00
    reference = pd.Timestamp('2017-12-01 00:00:00')
    return reference + pd.Timedelta(seconds=int(dt_value))

def map_product_cd_to_category(product_cd):
    """Map ProductCD to category"""
    mapping = {
        'W': 'Web',
        'C': 'Credit',
        'R': 'Retail',
        'S': 'Service',
        'H': 'Home'
    }
    return mapping.get(product_cd, 'Other')

def print_progress(current, total, prefix="Progress", start_time=None):
    """Print progress information"""
    percent = (current / total * 100) if total > 0 else 0
    bar_length = 50
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = '█' * filled + '░' * (bar_length - filled)
    
    elapsed = time.time() - start_time if start_time else 0
    rate = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / rate if rate > 0 else 0
    
    print(f"\r{prefix}: |{bar}| {current}/{total} ({percent:.1f}%) | "
          f"Rate: {rate:.0f}/s | ETA: {eta:.0f}s", end='', flush=True)

async def clear_all_data():
    """Clear ALL existing data from database"""
    print("\n" + "="*60)
    print("CLEARING ALL EXISTING DATA")
    print("="*60)
    
    collections = [
        ("SARs", SAR),
        ("Cases", Case),
        ("Case Notes", CaseNote),
        ("Alerts", Alert),
        ("Transactions", Transaction),
    ]
    
    # Keep Rules - they're configuration, not data
    # If you want to clear rules too, uncomment:
    # collections.append(("Rules", Rule))
    
    total_deleted = 0
    for name, model in collections:
        try:
            count = await model.count()
            if count > 0:
                await model.delete_all()
                print(f"  ✓ Deleted {count:,} {name}")
                total_deleted += count
            else:
                print(f"  - No {name} to delete")
        except Exception as e:
            print(f"  ✗ Error deleting {name}: {e}")
    
    print(f"\n✓ Total records deleted: {total_deleted:,}")
    print("="*60)

async def ingest_data(nrows=None, sample_fraud_rate=0.035, batch_size=2000):
    """
    Ingest Kaggle data into MongoDB
    nrows: Limit number of rows (None for all)
    sample_fraud_rate: Target fraud rate for sampling (to balance dataset)
    batch_size: Number of records to process in each batch (larger = faster but more memory)
    """
    start_time = time.time()
    await init_database()
    
    print("\n" + "=" * 60)
    print("Starting Kaggle Data Ingestion")
    print("=" * 60)
    
    # Clear ALL existing data first
    await clear_all_data()
    
    # Load transaction data
    print(f"\n📂 Loading transaction data from {SOURCES_DIR}/train_transaction.csv...")
    load_start = time.time()
    train_trans = pd.read_csv(
        os.path.join(SOURCES_DIR, 'train_transaction.csv'),
        nrows=nrows,
        usecols=TRANSACTION_FEATURES if nrows else None
    )
    print(f"✓ Loaded {len(train_trans):,} transaction records in {time.time() - load_start:.1f}s")
    
    # Load identity data
    print(f"📂 Loading identity data from {SOURCES_DIR}/train_identity.csv...")
    load_start = time.time()
    try:
        train_identity = pd.read_csv(
            os.path.join(SOURCES_DIR, 'train_identity.csv'),
            nrows=nrows,
            usecols=IDENTITY_FEATURES if nrows else None
        )
        print(f"✓ Loaded {len(train_identity):,} identity records in {time.time() - load_start:.1f}s")
        # Merge identity data
        df = train_trans.merge(train_identity, on='TransactionID', how='left')
    except Exception as e:
        print(f"⚠ Warning: Could not load identity data: {e}")
        df = train_trans.copy()
    
    # Sample data to balance fraud rate if needed
    fraud_count = df['isFraud'].sum()
    fraud_rate = fraud_count / len(df)
    print(f"\n📊 Original fraud rate: {fraud_rate:.4f} ({fraud_count:,} fraud cases)")
    
    if sample_fraud_rate and fraud_rate < sample_fraud_rate:
        # Upsample fraud cases
        fraud_df = df[df['isFraud'] == 1]
        non_fraud_df = df[df['isFraud'] == 0]
        target_fraud_count = int(len(non_fraud_df) * sample_fraud_rate / (1 - sample_fraud_rate))
        if target_fraud_count > len(fraud_df):
            fraud_df = fraud_df.sample(n=target_fraud_count, replace=True, random_state=42)
        df = pd.concat([non_fraud_df, fraud_df]).sample(frac=1, random_state=42).reset_index(drop=True)
        print(f"📊 After sampling: {df['isFraud'].sum():,} fraud cases ({df['isFraud'].sum()/len(df):.4f} rate)")
    
    # Process and insert transactions
    print(f"\n🔄 Processing and inserting {len(df):,} transactions...")
    print(f"   Batch size: {batch_size:,} records")
    print(f"   Note: Using fast heuristic scoring (ML models will be used in real-time)")
    
    # Don't initialize Scorer here - it loads ML models which is slow
    # Use fast heuristic scoring instead for bulk ingestion
    inserted_count = 0
    alert_count = 0
    case_count = 0
    error_count = 0
    
    # Use tqdm if available, otherwise use simple progress
    if HAS_TQDM:
        pbar = tqdm(total=len(df), desc="Ingesting", unit="records", ncols=100, mininterval=0.5)
    else:
        print_progress(0, len(df), "Ingesting", start_time)
    
    def calculate_risk_score_fast(transaction, is_fraud, row):
        """Fast heuristic risk scoring for bulk ingestion (no ML model loading)"""
        if is_fraud:
            # Use actual fraud label - calculate high risk score
            return np.random.randint(75, 100)
        
        # Fast heuristic scoring (no ML model needed)
        base_risk = 0
        
        # Amount-based risk
        if transaction.amount > 5000:
            base_risk += 40
        elif transaction.amount > 1000:
            base_risk += 20
        elif transaction.amount > 500:
            base_risk += 10
        
        # Category-based risk
        high_risk_cats = ['Service', 'Other']
        if transaction.category in high_risk_cats:
            base_risk += 15
        
        # ProductCD risk (from original data)
        product_cd = row.get('ProductCD', 'W')
        if product_cd in ['S', 'H']:  # Service, Home categories
            base_risk += 10
        
        # Card type risk
        card4 = row.get('card4', '')
        if pd.notna(card4) and str(card4).lower() in ['discover', 'american express']:
            base_risk += 5
        
        # Email domain risk
        p_email = row.get('P_emaildomain', '')
        if pd.notna(p_email) and 'temp' in str(p_email).lower():
            base_risk += 15
        
        return min(int(base_risk), 99)
    
    # Process in batches
    for idx in range(0, len(df), batch_size):
        batch = df.iloc[idx:idx+batch_size]
        transactions_to_insert = []
        
        # Prepare transactions
        for _, row in batch.iterrows():
            try:
                # Convert TransactionDT to datetime
                timestamp = convert_transaction_dt(row['TransactionDT'])
                
                # Extract customer_id from TransactionID (use last 6 digits)
                customer_id = int(str(row['TransactionID'])[-6:]) % 1000000
                
                # Extract merchant_id from card1 (or use addr1)
                merchant_id = int(row.get('card1', row.get('addr1', 0))) % 10000
                
                # Map ProductCD to category
                category = map_product_cd_to_category(row.get('ProductCD', 'W'))
                
                # Ensure amount is valid (minimum $0.01)
                amount = max(float(row['TransactionAmt']), 0.01)
                
                # Create transaction
                transaction = Transaction(
                    transaction_id=str(row['TransactionID']),
                    amount=amount,
                    customer_id=customer_id,
                    timestamp=timestamp,
                    merchant_id=merchant_id,
                    category=category,
                    transaction_type="PAYMENT",
                    old_balance_orig=float(row.get('C1', 0)) if not pd.isna(row.get('C1')) else 0.0,
                    new_balance_orig=float(row.get('C2', 0)) if not pd.isna(row.get('C2')) else 0.0,
                )
                transactions_to_insert.append((transaction, row))
                
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only print first 5 errors
                    print(f"\n⚠ Error processing transaction {row.get('TransactionID', 'unknown')}: {e}")
                continue
        
        # Insert transactions and create alerts/cases
        for transaction, row in transactions_to_insert:
            try:
                await transaction.insert()
                inserted_count += 1
                
                # Get original row data
                is_fraud = row['isFraud'] == 1
                
                # Calculate risk score using fast heuristic
                risk_score = calculate_risk_score_fast(transaction, is_fraud, row)
                
                # Create alert if risk is high or is fraud
                if risk_score >= 50 or is_fraud:
                    risk_level = "Very High" if risk_score >= 91 else "High" if risk_score >= 71 else "Medium"
                    
                    alert = Alert(
                        transaction=transaction,  # Transaction has ID now
                        risk_score=risk_score,
                        risk_level=risk_level,
                        status="Pending",
                        assigned_queue="High Profile Queue" if risk_score >= 90 else "General Queue"
                    )
                    await alert.insert()
                    alert_count += 1
                    
                    # Auto-create case for very high risk
                    if risk_score >= 85:
                        case = Case(
                            alert=alert,  # Alert has ID now
                            status="Open",
                            analyst_id=None
                        )
                        await case.insert()
                        case_count += 1
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"\n⚠ Error inserting transaction {transaction.transaction_id}: {e}")
        
        # Update progress
        if HAS_TQDM:
            pbar.update(len(batch))
        else:
            print_progress(min(idx + batch_size, len(df)), len(df), "Ingesting", start_time)
    
    if HAS_TQDM:
        pbar.close()
    else:
        print()  # New line after progress
    
    # Final summary
    elapsed_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ INGESTION COMPLETE!")
    print(f"{'='*60}")
    print(f"  📊 Transactions: {inserted_count:,}")
    print(f"  🚨 Alerts: {alert_count:,}")
    print(f"  📁 Cases: {case_count:,}")
    print(f"  ⚠️  Errors: {error_count:,}")
    print(f"  ⏱️  Time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)")
    print(f"  📈 Rate: {inserted_count/elapsed_time:.0f} records/second")
    print(f"{'='*60}")

if __name__ == "__main__":
    import asyncio
    
    # Configuration
    # Use nrows=50000 for quick testing, None for full dataset
    # Increase batch_size for faster processing (uses more memory)
    asyncio.run(ingest_data(
        nrows=50000,  # Change to None for full dataset
        batch_size=2000  # Increase for faster processing (2000-5000 recommended)
    ))
