import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .seed_data import seed_database
from .routers import auth, students, jobs, users, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed realistic sample data
    init_db()
    seed_database()
    yield

app = FastAPI(
    title="CareerBridge AI - Hệ thống Hướng nghiệp & Kết nối Tuyển dụng Sinh viên",
    description="Nền tảng AI hỗ trợ sinh viên tiếp cận cơ hội thực tập, việc làm, tối ưu CV, phỏng vấn thử và phân tích thị trường.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(jobs.router)
app.include_router(users.router)
app.include_router(analytics.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CareerBridge AI Platform",
        "version": "1.0.0",
        "deployment": "production-ready"
    }

# Serve Frontend static assets
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        # If static file requested
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Fallback to SPA index.html for client-side routing
        return FileResponse(FRONTEND_DIR / "index.html")
