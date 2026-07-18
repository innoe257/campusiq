from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.models import Student, Prediction
from app.core.security import get_current_user
from app.models.user import User
from app.services.prediction_service import PredictionService

router = APIRouter()
prediction_service = PredictionService()

class PredictionResponse(BaseModel):
    id: int
    student_id: int
    risk_score: float
    risk_category: str
    top_factors: List
    model_version: str
    created_at: str
    
    class Config:
        from_attributes = True

class BatchPredictionRequest(BaseModel):
    student_ids: List[int]


@router.post("/predict/{student_id}", response_model=PredictionResponse)
async def predict_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    prediction = prediction_service.predict(student, db)
    return prediction


@router.post("/predict-batch")
async def predict_batch(
    request: BatchPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = []
    for student_id in request.student_ids:
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            prediction = prediction_service.predict(student, db)
            results.append(prediction)
    
    return {"predictions": results, "total": len(results)}


@router.get("/student/{student_id}", response_model=List[PredictionResponse])
async def get_student_predictions(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = db.query(Prediction).filter(Prediction.student_id == student_id).order_by(Prediction.created_at.desc()).all()
    return predictions


@router.get("/history")
async def get_prediction_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()
    return predictions
