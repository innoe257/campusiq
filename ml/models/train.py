import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import xgboost as xgb
import mlflow
import mlflow.sklearn
import pickle
import os
from datetime import datetime

# Set MLflow tracking
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("campusiq-attrition-prediction")

def load_data(data_path: str = "/app/data/synthetic_students.csv") -> pd.DataFrame:
    """Load synthetic student data."""
    if not os.path.exists(data_path):
        # Fallback to generate on the fly
        from data_pipeline.data_generator import generate_synthetic_data
        df = generate_synthetic_data(n_students=1000)
    else:
        df = pd.read_csv(data_path)
    return df

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create features for the attrition model."""
    df["credit_completion_rate"] = df["credits_earned"] / df["credits_attempted"].clip(lower=1)
    df["years_enrolled"] = datetime.now().year - df["enrollment_year"]
    df["gpa_trend"] = df["current_gpa"] - df["first_semester_gpa"]
    
    # Interaction features
    df["gpa_x_attendance"] = df["current_gpa"] * df["attendance_rate"]
    df["engagement_x_completion"] = df["engagement_score"] * df["credit_completion_rate"]
    
    return df

def prepare_data(df: pd.DataFrame):
    """Prepare features and target for modeling."""
    feature_cols = [
        "current_gpa", "credits_earned", "credits_attempted", "attendance_rate",
        "engagement_score", "financial_aid", "first_generation", "age",
        "credit_completion_rate", "years_enrolled", "gpa_trend",
        "gpa_x_attendance", "engagement_x_completion",
    ]
    
    X = df[feature_cols].fillna(0)
    y = df["dropped_out"]
    
    return X, y, feature_cols

def train_model(X_train, y_train, X_test, y_test, feature_names):
    """Train XGBoost model with MLflow tracking."""
    
    with mlflow.start_run(run_name=f"attrition_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Log parameters
        params = {
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "max_depth": 6,
            "learning_rate": 0.1,
            "n_estimators": 200,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
        }
        mlflow.log_params(params)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = xgb.XGBClassifier(**params)
        model.fit(
            X_train_scaled, y_train,
            eval_set=[(X_test_scaled, y_test)],
            early_stopping_rounds=20,
            verbose=False,
        )
        
        # Evaluate
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)
        
        auc = roc_auc_score(y_test, y_pred_proba)
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)
        
        # Log metrics
        mlflow.log_metric("auc", auc)
        mlflow.log_metric("precision", report["1"]["precision"])
        mlflow.log_metric("recall", report["1"]["recall"])
        mlflow.log_metric("f1_score", report["1"]["f1-score"])
        
        # Log feature importance
        importance = model.feature_importances_
        for name, imp in zip(feature_names, importance):
            mlflow.log_metric(f"importance_{name}", imp)
        
        # Save model artifacts
        model_dir = "/app/ml/models"
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, "attrition_model.pkl")
        scaler_path = os.path.join(model_dir, "scaler.pkl")
        
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)
        
        mlflow.sklearn.log_model(model, "model")
        mlflow.log_artifact(model_path)
        
        print(f"Model trained - AUC: {auc:.4f}")
        print(f"Confusion Matrix:\n{cm}")
        print(f"Model saved to {model_path}")
        
        return model, scaler, auc

if __name__ == "__main__":
    print("Loading data...")
    df = load_data()
    
    print("Engineering features...")
    df = engineer_features(df)
    
    print("Preparing data...")
    X, y, feature_names = prepare_data(df)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training model...")
    model, scaler, auc = train_model(X_train, y_train, X_test, y_test, feature_names)
    
    print(f"\nTraining complete! Model AUC: {auc:.4f}")
