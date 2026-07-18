#!/bin/bash
set -e

echo "========================================="
echo "CampusIQ Backend Startup Script (Render)"
echo "========================================="

# Wait a moment for database to be ready
sleep 5

# 1. Run database migrations / create tables
echo "[1/4] Initializing database..."
python -c "
from app.db.session import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully')
"

# 2. Initialize vector store (if pgvector is available)
echo "[2/4] Attempting to initialize vector store..."
python -c "
import os
from sqlalchemy import create_engine, text
from app.core.config import get_settings

try:
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                id SERIAL PRIMARY KEY,
                document_id VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB DEFAULT '{}',
                embedding VECTOR(384),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        '''))
        conn.execute(text('''
            CREATE INDEX IF NOT EXISTS knowledge_embeddings_embedding_idx 
            ON knowledge_embeddings 
            USING ivfflat (embedding vector_cosine_ops) 
            WITH (lists = 100)
        '''))
        conn.commit()
    print('Vector store initialized successfully')
except Exception as e:
    print(f'Vector store initialization skipped (pgvector may not be available): {e}')
"

# 3. Seed sample data
echo "[3/4] Seeding sample data..."
python -c "
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.models import Student, User, Course
from app.core.security import get_password_hash

db = SessionLocal()

# Create demo user if not exists
demo_user = db.query(User).filter(User.username == 'demo').first()
if not demo_user:
    demo_user = User(
        username='demo',
        email='demo@campusiq.edu',
        hashed_password=get_password_hash('demo123'),
        full_name='Demo Faculty',
        role='faculty'
    )
    db.add(demo_user)
    print('Created demo user (demo / demo123)')

# Create sample students if none exist
student_count = db.query(Student).count()
if student_count == 0:
    sample_students = [
        Student(student_id='STU-2024-001', first_name='Sarah', last_name='Johnson', email='sarah@uni.edu',
                enrollment_year=2024, program='Computer Science', major='AI/ML',
                gpa=3.8, credits_earned=45, credits_attempted=48, attendance_rate=0.95, engagement_score=0.92,
                financial_aid=False, first_generation=False),
        Student(student_id='STU-2024-002', first_name='Michael', last_name='Chen', email='michael@uni.edu',
                enrollment_year=2024, program='Business', major='Finance',
                gpa=2.1, credits_earned=28, credits_attempted=45, attendance_rate=0.65, engagement_score=0.48,
                financial_aid=True, first_generation=True),
        Student(student_id='STU-2024-003', first_name='Emma', last_name='Wilson', email='emma@uni.edu',
                enrollment_year=2023, program='Psychology', major='Clinical',
                gpa=2.3, credits_earned=52, credits_attempted=72, attendance_rate=0.72, engagement_score=0.55,
                financial_aid=True, first_generation=False),
        Student(student_id='STU-2024-004', first_name='James', last_name='Brown', email='james@uni.edu',
                enrollment_year=2024, program='Computer Science', major='Data Science',
                gpa=3.5, credits_earned=38, credits_attempted=42, attendance_rate=0.88, engagement_score=0.85,
                financial_aid=False, first_generation=False),
        Student(student_id='STU-2024-005', first_name='Olivia', last_name='Davis', email='olivia@uni.edu',
                enrollment_year=2023, program='Engineering', major='Mechanical',
                gpa=3.2, credits_earned=58, credits_attempted=64, attendance_rate=0.82, engagement_score=0.78,
                financial_aid=False, first_generation=True),
        Student(student_id='STU-2024-006', first_name='William', last_name='Miller', email='william@uni.edu',
                enrollment_year=2024, program='Business', major='Marketing',
                gpa=1.8, credits_earned=18, credits_attempted=36, attendance_rate=0.58, engagement_score=0.35,
                financial_aid=True, first_generation=True),
        Student(student_id='STU-2024-007', first_name='Sophia', last_name='Garcia', email='sophia@uni.edu',
                enrollment_year=2023, program='Computer Science', major='Cybersecurity',
                gpa=3.9, credits_earned=62, credits_attempted=64, attendance_rate=0.97, engagement_score=0.95,
                financial_aid=False, first_generation=False),
        Student(student_id='STU-2024-008', first_name='Daniel', last_name='Martinez', email='daniel@uni.edu',
                enrollment_year=2024, program='Nursing', major='RN Program',
                gpa=2.8, credits_earned=42, credits_attempted=48, attendance_rate=0.85, engagement_score=0.72,
                financial_aid=True, first_generation=False),
    ]
    db.add_all(sample_students)
    print(f'Created {len(sample_students)} sample students')

# Create sample courses if none exist
course_count = db.query(Course).count()
if course_count == 0:
    sample_courses = [
        Course(course_code='CS101', title='Introduction to Programming', description='Python fundamentals', credits=3, program='Computer Science', semester='Fall', difficulty=2.0),
        Course(course_code='CS201', title='Data Structures', description='Arrays, trees, graphs', credits=3, program='Computer Science', prerequisites=['CS101'], semester='Spring', difficulty=4.0),
        Course(course_code='CS301', title='Machine Learning', description='ML algorithms and models', credits=3, program='Computer Science', prerequisites=['CS201', 'MATH201'], semester='Fall', difficulty=5.0),
        Course(course_code='BUS101', title='Intro to Business', description='Business fundamentals', credits=3, program='Business', semester='Fall', difficulty=2.0),
        Course(course_code='BUS201', title='Financial Accounting', description='Accounting principles', credits=3, program='Business', semester='Spring', difficulty=3.0),
        Course(course_code='PSYCH101', title='Introduction to Psychology', description='Behavior and mental processes', credits=3, program='Psychology', semester='Fall', difficulty=2.0),
        Course(course_code='ENG101', title='Engineering Fundamentals', description='Design and problem solving', credits=4, program='Engineering', semester='Fall', difficulty=3.0),
        Course(course_code='NURS101', title='Nursing Fundamentals', description='Patient care basics', credits=4, program='Nursing', semester='Fall', difficulty=3.5),
    ]
    db.add_all(sample_courses)
    print(f'Created {len(sample_courses)} sample courses')

db.commit()
db.close()
print('Database seeding complete')
"

# 4. Generate predictions for sample students
echo "[4/4] Generating risk predictions..."
python -c "
import sys
sys.path.insert(0, '.')
from app.db.session import SessionLocal
from app.models import Student, Prediction
from app.services.prediction_service import PredictionService

db = SessionLocal()
service = PredictionService()

students = db.query(Student).all()
for student in students:
    existing = db.query(Prediction).filter(Prediction.student_id == student.id).first()
    if not existing:
        service.predict(student, db)
        print(f'Predicted risk for {student.first_name} {student.last_name}')

db.close()
print('Predictions generated')
"

echo "========================================="
echo "Startup complete! Starting server..."
echo "========================================="

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
