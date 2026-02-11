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
        self.le_category = None
        
        # Try to load the model if sklearn/joblib are available
        try:
            import joblib
            if os.path.exists(self.model_path):
                loaded_data = joblib.load(self.model_path)
                if isinstance(loaded_data, dict):
                    self.model = loaded_data.get('model')
                    self.le_category = loaded_data.get('le_category')
                else:
                    self.model = loaded_data
        except ImportError:
            # sklearn/joblib not available in production (Vercel size limit)
            self.model = None

    def train(self, data):
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import LabelEncoder
        import joblib

        self.le_category = LabelEncoder()
        
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
        # Check if we can use the ML model
        if self.model is not None:
            try:
                import numpy as np
                try:
                    cat_encoded = self.le_category.transform([category])[0]
                except:
                    cat_encoded = 0 # Default/Other
                    
                features = np.array([[amount, cat_encoded]])
                probability = self.model.predict_proba(features)[0][1]
                return float(probability)
            except Exception as e:
                print(f"ML prediction error: {e}")
                # Fallback to heuristic
        
        # Lightweight heuristic prediction (no dependencies)
        # Higher risk for high amounts and certain categories
        base_risk = 0.05
        
        # Amount heuristic
        if amount > 5000:
            base_risk += 0.4
        elif amount > 1000:
            base_risk += 0.2
            
        # Category heuristic
        high_risk_cats = ['crypto', 'electronics', 'transfer', 'gambling']
        if category.lower() in high_risk_cats:
            base_risk += 0.3
            
        return min(float(base_risk), 0.95)
