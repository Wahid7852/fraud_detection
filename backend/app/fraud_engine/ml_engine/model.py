import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class MLEngine:
    def __init__(self, model_path="backend/app/fraud_engine/ml_engine/fraud_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.le_category = LabelEncoder()
        
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)

    def train(self, data: pd.DataFrame):
        # Prepare features
        # Assuming data has: Amount, Category, FraudIndicator
        X = data[['Amount', 'Category']].copy()
        y = data['FraudIndicator']
        
        X['Category'] = self.le_category.fit_transform(X['Category'])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Save model
        joblib.dump(self.model, self.model_path)
        print(f"Model trained and saved to {self.model_path}")

    def predict(self, amount: float, category: str) -> float:
        if self.model is None:
            # Fallback if no model trained
            return 0.1 # Low probability
            
        try:
            cat_encoded = self.le_category.transform([category])[0]
        except:
            cat_encoded = 0 # Default/Other
            
        features = np.array([[amount, cat_encoded]])
        probability = self.model.predict_proba(features)[0][1]
        return float(probability)
