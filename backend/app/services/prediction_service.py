import json
import pickle
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from app.models import Student, Prediction
from app.core.config import get_settings
import numpy as np

settings = get_settings()

class PredictionService:
    def __init__(self):
        self.model_path = "/app/ml/models/attrition_model.pkl"
        self.model_version = "1.0.0"
        self._load_model()
    
    def _load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None
    
    def _extract_features(self, student: Student) -> np.ndarray:
        features = [
            student.gpa or 0.0,
            student.credits_earned or 0,
            student.credits_attempted or 1,
            student.attendance_rate or 0.0,
            student.engagement_score or 0.0,
            1 if student.financial_aid else 0,
            1 if student.first_generation else 0,
            (student.credits_earned or 0) / (student.credits_attempted or 1),
            datetime.now().year - (student.enrollment_year or datetime.now().year),
        ]
        return np.array(features).reshape(1, -1)
    
    def _get_feature_names(self) -> list:
        return [
            "gpa", "credits_earned", "credits_attempted", "attendance_rate",
            "engagement_score", "financial_aid", "first_generation",
            "credit_completion_rate", "years_enrolled"
        ]
    
    def _categorize_risk(self, score: float) -> str:
        if score >= 0.7:
            return "critical"
        elif score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def predict(self, student: Student, db: Session) -> Prediction:
        features = self._extract_features(student)
        
        if self.model:
            risk_score = float(self.model.predict_proba(features)[0][1])
        else:
            # Fallback rule-based model if ML model not trained
            risk_score = self._rule_based_score(student)
        
        risk_category = self._categorize_risk(risk_score)
        
        # Determine top factors
        top_factors = self._analyze_factors(student)
        
        prediction = Prediction(
            student_id=student.id,
            risk_score=risk_score,
            risk_category=risk_category,
            top_factors=top_factors,
            model_version=self.model_version,
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        return prediction
    
    def _rule_based_score(self, student: Student) -> float:
        score = 0.0
        if student.gpa and student.gpa < 2.0:
            score += 0.3
        if student.attendance_rate and student.attendance_rate < 0.7:
            score += 0.25
        if student.engagement_score and student.engagement_score < 0.4:
            score += 0.2
        if student.financial_aid:
            score += 0.1
        if student.first_generation:
            score += 0.05
        completion_rate = (student.credits_earned or 0) / (student.credits_attempted or 1)
        if completion_rate < 0.5:
            score += 0.2
        return min(score, 0.95)
    
    def _analyze_factors(self, student: Student) -> list:
        factors = []
        if student.gpa and student.gpa < 2.5:
            factors.append({"factor": "Low GPA", "impact": "high", "value": student.gpa})
        if student.attendance_rate and student.attendance_rate < 0.75:
            factors.append({"factor": "Low Attendance", "impact": "high", "value": student.attendance_rate})
        if student.engagement_score and student.engagement_score < 0.5:
            factors.append({"factor": "Low Engagement", "impact": "medium", "value": student.engagement_score})
        completion_rate = (student.credits_earned or 0) / (student.credits_attempted or 1)
        if completion_rate < 0.6:
            factors.append({"factor": "Low Credit Completion", "impact": "high", "value": round(completion_rate, 2)})
        return factors
