# train_model.py

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

def main():
    print("Starting ML Model Training...")
    
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'ml_data', 'blood_transfusion', 'raw', 'transfusion.csv')
    model_dir = os.path.join(base_dir, 'app', 'ml')
    model_path = os.path.join(model_dir, 'blood_model.joblib')
    
    if not os.path.exists(csv_path):
        print(f"ERROR: Dataset not found at {csv_path}")
        return
        
    # Load dataset
    print(f"Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Clean column names (strip whitespace and quotes)
    df.columns = [c.strip().strip('"') for c in df.columns]
    print(f"Dataset columns: {list(df.columns)}")
    
    # Target column is the last column
    target_col = df.columns[-1]
    feature_cols = list(df.columns[:-1])
    
    X = df[feature_cols]
    y = df[target_col]
    
    print(f"Features: {feature_cols}")
    print(f"Target: {target_col}")
    print(f"Dataset shape: {df.shape}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest Classifier
    print("Training RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)
    
    # Predict and evaluate
    y_pred = clf.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print("\nModel Evaluation Metrics:")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    # Save model
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
    print(f"\nSaving trained model to: {model_path}")
    joblib.dump(clf, model_path)
    print("ML Model training and serialization complete!")

if __name__ == '__main__':
    main()
