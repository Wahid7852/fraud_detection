import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class MLEngine:
    def __init__(self, model_path=None):
        if model_path is None:
            # Get the path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(current_dir, "fraud_model.joblib")
        else:
            self.model_path = model_path
            
        self.model = None
        self.le_category = LabelEncoder()
        
        if os.path.exists(self.model_path):
            loaded_data = joblib.load(self.model_path)
            if isinstance(loaded_data, dict):
                self.model = loaded_data.get('model')
                self.le_category = loaded_data.get('le_category')
            else:
                self.model = loaded_data
                # le_category remains a new instance

    def train(self, data: pd.DataFrame):
        # Prepare features
        # Assuming data has: Amount, Category, FraudIndicator
        X = data[['Amount', 'Category']].copy()
        y = data['FraudIndicator']
        
        X['Category'] = self.le_category.fit_transform(X['Category'])
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Save model and encoder
        joblib.dump({
            'model': self.model,
            'le_category': self.le_category
        }, self.model_path)
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
