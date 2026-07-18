from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.session import engine, Base
from app.api.v1 import auth, students, predictions, chat

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

# CORS - allow Render frontend and local development
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://campusiq-frontend.onrender.com",
    "https://*.onrender.com",
]

if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to CampusIQ API",
        "version": settings.VERSION,
        "documentation": "/docs",
        "environment": "render" if settings.RENDER else "local",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
