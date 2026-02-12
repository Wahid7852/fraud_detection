"""
Train all 4 ML models with proper class imbalance handling
1. Decision Tree (Primary)
2. Naive Bayes (Baseline)
3. KNN (Distance-based with PCA)
4. ANN (Deep Learning)
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_fscore_support
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import json
import os
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = r'c:\Users\Wahid Khan\Desktop\g_project\sources'
MODEL_DIR = r'c:\Users\Wahid Khan\Desktop\g_project\backend\app\ml_models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Key features from Kaggle dataset
FEATURE_COLUMNS = [
    'TransactionAmt', 'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6',
    'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain',
    'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14',
    'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15',
    'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9'
]

def load_and_preprocess(nrows=100000, use_smote=True):
    """
    Load and preprocess Kaggle data
    nrows: Number of rows to load (None for all)
    use_smote: Whether to use SMOTE for class imbalance
    """
    print("=" * 60)
    print("Loading and Preprocessing Data")
    print("=" * 60)
    
    print(f"Loading transaction data from {DATA_DIR}/train_transaction.csv...")
    train_trans = pd.read_csv(
        os.path.join(DATA_DIR, 'train_transaction.csv'),
        nrows=nrows
    )
    print(f"Loaded {len(train_trans)} records")
    
    # Select features
    available_features = [f for f in FEATURE_COLUMNS if f in train_trans.columns]
    print(f"Using {len(available_features)} features: {available_features[:10]}...")
    
    target = 'isFraud'
    df = train_trans[available_features + [target]].copy()
    
    print(f"\nOriginal class distribution:")
    print(f"  Fraud: {df[target].sum()} ({df[target].mean()*100:.2f}%)")
    print(f"  Legitimate: {(df[target]==0).sum()} ({(1-df[target].mean())*100:.2f}%)")
    
    # Handle missing values
    print("\nHandling missing values...")
    for col in available_features:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('unknown')
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            # Save encoder for later use
            joblib.dump(le, os.path.join(MODEL_DIR, f'le_{col}.joblib'))
        else:
            df[col] = df[col].fillna(df[col].median())
    
    X = df[available_features]
    y = df[target]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set: {len(X_train)} samples ({y_train.sum()} fraud)")
    print(f"Test set: {len(X_test)} samples ({y_test.sum()} fraud)")
    
    # Apply SMOTE to training data if requested
    if use_smote:
        print("\nApplying SMOTE to balance training data...")
        smote = SMOTE(random_state=42, sampling_strategy=0.1)  # 10% fraud rate
        X_train, y_train = smote.fit_resample(X_train, y_train)
        print(f"After SMOTE - Train set: {len(X_train)} samples ({y_train.sum()} fraud, {y_train.mean()*100:.2f}%)")
    
    # Save feature columns for later use
    joblib.dump(available_features, os.path.join(MODEL_DIR, 'feature_columns.joblib'))
    
    return X_train, X_test, y_train, y_test, available_features

def train_decision_tree(X_train, X_test, y_train, y_test, feature_names):
    """Train Decision Tree with class weighting"""
    print("\n" + "=" * 60)
    print("Training Decision Tree (Primary Model)")
    print("=" * 60)
    
    # Calculate class weights
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.unique(y_train)
    class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
    class_weight_dict = dict(zip(classes, class_weights))
    
    dt = DecisionTreeClassifier(
        max_depth=15,
        min_samples_leaf=10,
        min_samples_split=20,
        class_weight=class_weight_dict,
        random_state=42
    )
    
    dt.fit(X_train, y_train)
    
    # Evaluate
    y_pred = dt.predict(X_test)
    y_pred_proba = dt.predict_proba(X_test)[:, 1]
    
    accuracy = dt.score(X_test, y_test)
    auc = roc_auc_score(y_test, y_pred_proba)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
    
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  AUC-ROC: {auc:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    # Feature importance
    importance = dict(zip(feature_names, dt.feature_importances_))
    top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nTop 10 Features:")
    for feat, imp in top_features:
        print(f"  {feat}: {imp:.4f}")
    
    # Save model
    joblib.dump(dt, os.path.join(MODEL_DIR, 'decision_tree.joblib'))
    
    return {
        "accuracy": float(accuracy),
        "auc_roc": float(auc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "feature_importance": {k: float(v) for k, v in importance.items()},
        "top_features": [{"name": k, "importance": float(v)} for k, v in top_features]
    }

def train_naive_bayes(X_train, X_test, y_train, y_test):
    """Train Naive Bayes (Baseline Statistical Model)"""
    print("\n" + "=" * 60)
    print("Training Naive Bayes (Baseline Model)")
    print("=" * 60)
    
    nb = GaussianNB()
    nb.fit(X_train, y_train)
    
    # Evaluate
    y_pred = nb.predict(X_test)
    y_pred_proba = nb.predict_proba(X_test)[:, 1]
    
    accuracy = nb.score(X_test, y_test)
    auc = roc_auc_score(y_test, y_pred_proba)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
    
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  AUC-ROC: {auc:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    # Save model
    joblib.dump(nb, os.path.join(MODEL_DIR, 'naive_bayes.joblib'))
    
    return {
        "accuracy": float(accuracy),
        "auc_roc": float(auc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1)
    }

def train_knn(X_train, X_test, y_train, y_test):
    """Train KNN with PCA and scaling"""
    print("\n" + "=" * 60)
    print("Training KNN with PCA (Distance-Based Model)")
    print("=" * 60)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # PCA for dimensionality reduction
    n_components = min(50, X_train.shape[1])  # Use 50 components or all features if less
    pca = PCA(n_components=n_components, random_state=42)
    X_train_pca = pca.fit_transform(X_train_scaled)
    X_test_pca = pca.transform(X_test_scaled)
    
    print(f"Reduced dimensions: {X_train.shape[1]} -> {n_components}")
    print(f"Explained variance: {pca.explained_variance_ratio_.sum():.4f}")
    
    # Train KNN
    knn = KNeighborsClassifier(n_neighbors=5, weights='distance')
    knn.fit(X_train_pca, y_train)
    
    # Evaluate
    y_pred = knn.predict(X_test_pca)
    y_pred_proba = knn.predict_proba(X_test_pca)[:, 1]
    
    accuracy = knn.score(X_test_pca, y_test)
    auc = roc_auc_score(y_test, y_pred_proba)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
    
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  AUC-ROC: {auc:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    # Save models and preprocessors
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'knn_scaler.joblib'))
    joblib.dump(pca, os.path.join(MODEL_DIR, 'knn_pca.joblib'))
    joblib.dump(knn, os.path.join(MODEL_DIR, 'knn.joblib'))
    
    return {
        "accuracy": float(accuracy),
        "auc_roc": float(auc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "n_components": n_components,
        "explained_variance": float(pca.explained_variance_ratio_.sum())
    }

def train_ann(X_train, X_test, y_train, y_test):
    """Train ANN (Deep Learning Model)"""
    print("\n" + "=" * 60)
    print("Training ANN (Deep Learning Model)")
    print("=" * 60)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Calculate class weights for ANN
    from sklearn.utils.class_weight import compute_class_weight
    classes = np.unique(y_train)
    class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
    class_weight_dict = dict(zip(classes, class_weights))
    
    # Build model
    model = Sequential([
        Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )
    
    print(f"Model architecture:")
    model.summary()
    
    # Train with early stopping
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=5,
        restore_best_weights=True
    )
    
    history = model.fit(
        X_train_scaled, y_train,
        validation_split=0.2,
        epochs=20,
        batch_size=256,
        class_weight=class_weight_dict,
        callbacks=[early_stopping],
        verbose=1
    )
    
    # Evaluate
    test_results = model.evaluate(X_test_scaled, y_test, verbose=0)
    y_pred_proba = model.predict(X_test_scaled, verbose=0).flatten()
    y_pred = (y_pred_proba > 0.5).astype(int)
    
    accuracy = test_results[1]
    auc = test_results[2]
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary', zero_division=0)
    
    print(f"\nResults:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  AUC-ROC: {auc:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    # Save model and scaler
    model.save(os.path.join(MODEL_DIR, 'ann_model.h5'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'ann_scaler.joblib'))
    
    return {
        "accuracy": float(accuracy),
        "auc_roc": float(auc),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "epochs_trained": len(history.history['loss'])
    }

if __name__ == "__main__":
    print("=" * 60)
    print("ML Model Training Pipeline")
    print("=" * 60)
    
    # Load and preprocess data
    X_train, X_test, y_train, y_test, feature_names = load_and_preprocess(
        nrows=100000,  # Use 100k for training (increase for better results)
        use_smote=True
    )
    
    # Train all models
    results = {}
    
    results['decision_tree'] = train_decision_tree(X_train, X_test, y_train, y_test, feature_names)
    results['naive_bayes'] = train_naive_bayes(X_train, X_test, y_train, y_test)
    results['knn'] = train_knn(X_train, X_test, y_train, y_test)
    results['ann'] = train_ann(X_train, X_test, y_train, y_test)
    
    # Determine best model
    best_model = max(results.items(), key=lambda x: x[1].get('f1_score', 0))
    results['best_model'] = best_model[0]
    results['best_f1_score'] = best_model[1].get('f1_score', 0)
    
    # Save results
    with open(os.path.join(MODEL_DIR, 'results.json'), 'w') as f:
        json.dump(results, f, indent=4)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"\nBest Model: {best_model[0]} (F1: {best_model[1].get('f1_score', 0):.4f})")
    print(f"\nAll Results:")
    for model_name, metrics in results.items():
        if model_name not in ['best_model', 'best_f1_score']:
            print(f"  {model_name}: F1={metrics.get('f1_score', 0):.4f}, AUC={metrics.get('auc_roc', 0):.4f}")
    print(f"\nResults saved to {MODEL_DIR}/results.json")
