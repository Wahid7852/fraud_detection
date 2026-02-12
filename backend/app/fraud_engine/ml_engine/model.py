"""
ML Engine for fraud detection using trained models
Supports: Decision Tree, Naive Bayes, KNN, ANN
"""
import os
import numpy as np
from typing import Dict, Any, Optional

class MLEngine:
    def __init__(self, model_type: str = "decision_tree"):
        """
        Initialize ML Engine
        model_type: 'decision_tree', 'naive_bayes', 'knn', 'ann', or 'ensemble'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self.pca = None
        self.label_encoders = {}
        self.feature_columns = None
        
        # Get model directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = os.path.join(current_dir, "..", "..", "ml_models")
        
        # Load models if available
        self._load_models()
    
    def _load_models(self):
        """Load trained models and preprocessors"""
        try:
            import joblib
            import tensorflow as tf
            
            # Load feature columns
            feature_path = os.path.join(self.model_dir, 'feature_columns.joblib')
            if os.path.exists(feature_path):
                self.feature_columns = joblib.load(feature_path)
            
            # Load label encoders for categorical features
            if self.feature_columns:
                for col in self.feature_columns:
                    le_path = os.path.join(self.model_dir, f'le_{col}.joblib')
                    if os.path.exists(le_path):
                        self.label_encoders[col] = joblib.load(le_path)
            
            # Load model based on type
            if self.model_type == "decision_tree":
                model_path = os.path.join(self.model_dir, 'decision_tree.joblib')
                if os.path.exists(model_path):
                    self.model = joblib.load(model_path)
            
            elif self.model_type == "naive_bayes":
                model_path = os.path.join(self.model_dir, 'naive_bayes.joblib')
                if os.path.exists(model_path):
                    self.model = joblib.load(model_path)
            
            elif self.model_type == "knn":
                scaler_path = os.path.join(self.model_dir, 'knn_scaler.joblib')
                pca_path = os.path.join(self.model_dir, 'knn_pca.joblib')
                model_path = os.path.join(self.model_dir, 'knn.joblib')
                
                if all(os.path.exists(p) for p in [scaler_path, pca_path, model_path]):
                    self.scaler = joblib.load(scaler_path)
                    self.pca = joblib.load(pca_path)
                    self.model = joblib.load(model_path)
            
            elif self.model_type == "ann":
                scaler_path = os.path.join(self.model_dir, 'ann_scaler.joblib')
                model_path = os.path.join(self.model_dir, 'ann_model.h5')
                
                if all(os.path.exists(p) for p in [scaler_path, model_path]):
                    self.scaler = joblib.load(scaler_path)
                    self.model = tf.keras.models.load_model(model_path)
            
            elif self.model_type == "ensemble":
                # Load all models for ensemble
                self.models = {}
                for mt in ["decision_tree", "naive_bayes", "knn", "ann"]:
                    engine = MLEngine(model_type=mt)
                    if engine.model is not None:
                        self.models[mt] = engine
            
        except ImportError:
            # Dependencies not available
            self.model = None
        except Exception as e:
            print(f"Error loading ML models: {e}")
            self.model = None
    
    def _extract_features_from_transaction(self, transaction) -> np.ndarray:
        """
        Extract features from Transaction model
        Maps transaction fields to model features
        """
        if not self.feature_columns:
            return None
        
        features = {}
        
        # Map transaction fields to feature columns
        feature_mapping = {
            'TransactionAmt': transaction.amount,
            'ProductCD': self._map_category_to_product_cd(transaction.category),
            'card1': transaction.merchant_id,
            'card2': transaction.customer_id % 1000,
            'card3': int(transaction.amount) % 1000,
            'card4': 'unknown',  # Default
            'card5': transaction.customer_id % 100,
            'card6': 'credit',  # Default
            'addr1': transaction.merchant_id,
            'addr2': transaction.customer_id % 100,
            'P_emaildomain': 'unknown',
            'R_emaildomain': 'unknown',
        }
        
        # Fill in C features (balance-related)
        for i in range(1, 15):
            c_val = getattr(transaction, f'old_balance_orig', 0) if i == 1 else \
                   getattr(transaction, f'new_balance_orig', 0) if i == 2 else 0
            features[f'C{i}'] = float(c_val) if c_val else 0.0
        
        # Fill in D features (time-related, use defaults)
        for i in range(1, 16):
            features[f'D{i}'] = 0.0
        
        # Fill in M features (merchant-related, use defaults)
        for i in range(1, 10):
            features[f'M{i}'] = 'T' if i % 2 == 0 else 'F'
        
        # Build feature vector
        feature_vector = []
        for col in self.feature_columns:
            if col in feature_mapping:
                val = feature_mapping[col]
            elif col in features:
                val = features[col]
            else:
                val = 0.0  # Default
            
            # Encode categorical features
            if col in self.label_encoders:
                try:
                    val = self.label_encoders[col].transform([str(val)])[0]
                except:
                    val = 0
            elif isinstance(val, str):
                val = hash(val) % 1000  # Simple hash encoding
            
            feature_vector.append(float(val))
        
        return np.array([feature_vector])
    
    def _map_category_to_product_cd(self, category: str) -> str:
        """Map category to ProductCD"""
        mapping = {
            'Web': 'W',
            'Credit': 'C',
            'Retail': 'R',
            'Service': 'S',
            'Home': 'H'
        }
        return mapping.get(category, 'W')
    
    def predict(self, transaction) -> float:
        """
        Predict fraud probability for a transaction
        Returns: probability between 0 and 1
        """
        if self.model is None:
            return self._heuristic_prediction(transaction)
        
        try:
            # Extract features
            features = self._extract_features_from_transaction(transaction)
            if features is None:
                return self._heuristic_prediction(transaction)
            
            # Preprocess based on model type
            if self.model_type == "knn":
                if self.scaler and self.pca:
                    features = self.scaler.transform(features)
                    features = self.pca.transform(features)
            
            elif self.model_type == "ann":
                if self.scaler:
                    features = self.scaler.transform(features)
            
            # Predict
            if self.model_type == "ann":
                probability = float(self.model.predict(features, verbose=0)[0][0])
            elif self.model_type == "ensemble":
                # Average predictions from all models
                probabilities = []
                for mt, engine in self.models.items():
                    prob = engine.predict(transaction)
                    probabilities.append(prob)
                probability = float(np.mean(probabilities))
            else:
                probability = float(self.model.predict_proba(features)[0][1])
            
            return min(max(probability, 0.0), 1.0)
        
        except Exception as e:
            print(f"ML prediction error: {e}")
            return self._heuristic_prediction(transaction)
    
    def _heuristic_prediction(self, transaction) -> float:
        """
        Fallback heuristic prediction when ML models are not available
        """
        base_risk = 0.05
        
        # Amount-based risk
        if transaction.amount > 5000:
            base_risk += 0.4
        elif transaction.amount > 1000:
            base_risk += 0.2
        elif transaction.amount > 500:
            base_risk += 0.1
        
        # Category-based risk
        high_risk_cats = ['crypto', 'electronics', 'transfer', 'gambling', 'gaming']
        if transaction.category.lower() in high_risk_cats:
            base_risk += 0.3
        
        # Balance change risk
        if transaction.old_balance_orig and transaction.new_balance_orig:
            balance_change = abs(transaction.old_balance_orig - transaction.new_balance_orig)
            if balance_change > transaction.amount * 1.5:  # Suspicious balance change
                base_risk += 0.2
        
        return min(float(base_risk), 0.95)
