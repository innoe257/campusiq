from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.models import Student, Course, Prediction, StudyPlan
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

class StudentResponse(BaseModel):
    id: int
    student_id: str
    first_name: str
    last_name: str
    email: str
    program: str
    major: str
    gpa: float
    risk_score: float | None
    risk_category: str | None
    
    class Config:
        from_attributes = True

class StudentDetail(BaseModel):
    id: int
    student_id: str
    first_name: str
    last_name: str
    email: str
    enrollment_year: int
    program: str
    major: str
    gpa: float
    credits_earned: int
    credits_attempted: int
    attendance_rate: float
    engagement_score: float
    financial_aid: bool
    first_generation: bool
    risk_score: float | None
    risk_category: str | None
    top_factors: List | None
    
    class Config:
        from_attributes = True

class StudyPlanCreate(BaseModel):
    title: str
    plan_data: dict


@router.get("/", response_model=List[StudentResponse])
async def list_students(
    program: Optional[str] = None,
    risk_category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Student)
    
    if program:
        query = query.filter(Student.program == program)
    
    if risk_category:
        query = query.join(Prediction).filter(Prediction.risk_category == risk_category)
    
    students = query.offset(skip).limit(limit).all()
    
    result = []
    for student in students:
        latest_prediction = db.query(Prediction).filter(Prediction.student_id == student.id).order_by(Prediction.created_at.desc()).first()
        result.append(StudentResponse(
            id=student.id,
            student_id=student.student_id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            program=student.program,
            major=student.major,
            gpa=student.gpa,
            risk_score=latest_prediction.risk_score if latest_prediction else None,
            risk_category=latest_prediction.risk_category if latest_prediction else None,
        ))
    
    return result


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_students = db.query(Student).count()
    active_students = db.query(Student).filter(Student.is_active == True).count()
    
    risk_stats = db.query(
        Prediction.risk_category,
        func.count(Prediction.id).label("count")
    ).group_by(Prediction.risk_category).all()
    
    avg_gpa = db.query(func.avg(Student.gpa)).scalar()
    
    return {
        "total_students": total_students,
        "active_students": active_students,
        "risk_distribution": {r.risk_category: r.count for r in risk_stats},
        "average_gpa": round(avg_gpa, 2) if avg_gpa else 0,
    }


@router.get("/{student_id}", response_model=StudentDetail)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    latest_prediction = db.query(Prediction).filter(Prediction.student_id == student.id).order_by(Prediction.created_at.desc()).first()
    
    return StudentDetail(
        id=student.id,
        student_id=student.student_id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        enrollment_year=student.enrollment_year,
        program=student.program,
        major=student.major,
        gpa=student.gpa,
        credits_earned=student.credits_earned,
        credits_attempted=student.credits_attempted,
        attendance_rate=student.attendance_rate,
        engagement_score=student.engagement_score,
        financial_aid=student.financial_aid,
        first_generation=student.first_generation,
        risk_score=latest_prediction.risk_score if latest_prediction else None,
        risk_category=latest_prediction.risk_category if latest_prediction else None,
        top_factors=latest_prediction.top_factors if latest_prediction else [],
    )


@router.post("/{student_id}/study-plans")
async def create_study_plan(
    student_id: int,
    plan: StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    new_plan = StudyPlan(
        student_id=student_id,
        title=plan.title,
        plan_data=plan.plan_data,
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan
