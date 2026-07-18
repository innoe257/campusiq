import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models import Student

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "CampusIQ"


def test_register_user(db):
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "student"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_login_user():
    # First register
    client.post("/api/v1/auth/register", json={
        "username": "logintest",
        "email": "login@test.com",
        "password": "testpassword123",
        "full_name": "Login Test"
    })
    
    # Then login
    response = client.post("/api/v1/auth/login", data={
        "username": "logintest",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user():
    # Register and login
    client.post("/api/v1/auth/register", json={
        "username": "currenttest",
        "email": "current@test.com",
        "password": "testpassword123"
    })
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "currenttest",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currenttest"


def test_dashboard_stats():
    # Register and login
    client.post("/api/v1/auth/register", json={
        "username": "statstest",
        "email": "stats@test.com",
        "password": "testpassword123"
    })
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "statstest",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    response = client.get("/api/v1/students/dashboard/stats", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "total_students" in data


def test_chat_endpoint():
    # Register and login
    client.post("/api/v1/auth/register", json={
        "username": "chattest",
        "email": "chat@test.com",
        "password": "testpassword123"
    })
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "chattest",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    response = client.post("/api/v1/chat/message", headers={
        "Authorization": f"Bearer {token}"
    }, json={
        "message": "What are the prerequisites for CS201?",
        "session_id": "test-session-123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data


def test_prediction_endpoint():
    # Register and login
    client.post("/api/v1/auth/register", json={
        "username": "predtest",
        "email": "pred@test.com",
        "password": "testpassword123"
    })
    
    login_response = client.post("/api/v1/auth/login", data={
        "username": "predtest",
        "password": "testpassword123"
    })
    token = login_response.json()["access_token"]
    
    # Create a student first
    db = TestingSessionLocal()
    student = Student(
        student_id="STU-TEST-001",
        first_name="Test",
        last_name="Student",
        email="test.student@uni.edu",
        gpa=2.5,
        credits_earned=45,
        credits_attempted=60,
        attendance_rate=0.8,
        engagement_score=0.6,
        program="Computer Science",
        major="Software Engineering"
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    student_id = student.id
    db.close()
    
    response = client.post(f"/api/v1/predictions/predict/{student_id}", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_category" in data
    assert 0 <= data["risk_score"] <= 1
