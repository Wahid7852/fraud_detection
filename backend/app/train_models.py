import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import json
import os
import joblib

# Configuration
DATA_DIR = r'c:\Users\Wahid Khan\Desktop\g_project\sources'
MODEL_DIR = r'c:\Users\Wahid Khan\Desktop\g_project\backend\app\ml_models'
os.makedirs(MODEL_DIR, exist_ok=True)

def load_and_preprocess(nrows=50000):
    print("Loading data...")
    train_trans = pd.read_csv(os.path.join(DATA_DIR, 'train_transaction.csv'), nrows=nrows)
    
    # Select key features for the demo/analysis
    # In a real scenario, we'd do extensive feature engineering
    features = ['TransactionAmt', 'ProductCD', 'card1', 'card2', 'card3', 'card4', 'card5', 'card6', 'addr1', 'addr2', 'P_emaildomain', 'R_emaildomain']
    target = 'isFraud'
    
    df = train_trans[features + [target]].copy()
    
    # Handle missing values
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('unknown')
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
        else:
            df[col] = df[col].fillna(df[col].median())
            
    X = df[features]
    y = df[target]
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_decision_tree(X_train, X_test, y_train, y_test):
    print("Training Decision Tree...")
    dt = DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, random_state=42)
    dt.fit(X_train, y_train)
    score = dt.score(X_test, y_test)
    joblib.dump(dt, os.path.join(MODEL_DIR, 'decision_tree.joblib'))
    
    # Feature importance
    importance = dict(zip(X_train.columns, dt.feature_importances_))
    return {"accuracy": score, "feature_importance": importance}

def train_naive_bayes(X_train, X_test, y_train, y_test):
    print("Training Naive Bayes...")
    nb = GaussianNB()
    nb.fit(X_train, y_train)
    score = nb.score(X_test, y_test)
    joblib.dump(nb, os.path.join(MODEL_DIR, 'naive_bayes.joblib'))
    return {"accuracy": score}

def train_knn(X_train, X_test, y_train, y_test):
    print("Training KNN with PCA...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # PCA for dimensionality reduction
    pca = PCA(n_components=5)
    X_train_pca = pca.fit_transform(X_train_scaled)
    X_test_pca = pca.transform(X_test_scaled)
    
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train_pca, y_train)
    score = knn.score(X_test_pca, y_test)
    
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'knn_scaler.joblib'))
    joblib.dump(pca, os.path.join(MODEL_DIR, 'knn_pca.joblib'))
    joblib.dump(knn, os.path.join(MODEL_DIR, 'knn.joblib'))
    
    return {"accuracy": score}

def train_ann(X_train, X_test, y_train, y_test):
    print("Training ANN...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = Sequential([
        Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train_scaled, y_train, epochs=5, batch_size=32, verbose=0)
    
    _, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
    model.save(os.path.join(MODEL_DIR, 'ann_model.h5'))
    joblib.dump(scaler, os.path.join(MODEL_DIR, 'ann_scaler.joblib'))
    
    return {"accuracy": float(accuracy)}

if __name__ == "__main__":
    X_train, X_test, y_train, y_test = load_and_preprocess()
    
    results = {}
    results['decision_tree'] = train_decision_tree(X_train, X_test, y_train, y_test)
    results['naive_bayes'] = train_naive_bayes(X_train, X_test, y_train, y_test)
    results['knn'] = train_knn(X_train, X_test, y_train, y_test)
    results['ann'] = train_ann(X_train, X_test, y_train, y_test)
    
    with open(os.path.join(MODEL_DIR, 'results.json'), 'w') as f:
        json.dump(results, f, indent=4)
    
    print("All models trained and results saved.")
