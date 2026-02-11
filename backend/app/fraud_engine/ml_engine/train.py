import pandas as pd
import os
import joblib
from backend.app.fraud_engine.ml_engine.model import MLEngine

def train_initial_model():
    # Paths to data
    data_dir = "New folder/Data"
    
    # Load data for training
    trans_records = pd.read_csv(os.path.join(data_dir, "Transaction Data/transaction_records.csv"))
    fraud_inds = pd.read_csv(os.path.join(data_dir, "Fraudulent Patterns/fraud_indicators.csv"))
    categories = pd.read_csv(os.path.join(data_dir, "Merchant Information/transaction_category_labels.csv"))
    
    # Merge data
    df = trans_records.merge(fraud_inds, on="TransactionID")
    df = df.merge(categories, on="TransactionID")
    
    # Initialize engine and train
    engine = MLEngine()
    engine.train(df)
    print("Initial model training complete.")

if __name__ == "__main__":
    train_initial_model()
