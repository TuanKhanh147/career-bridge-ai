import uuid
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from ..models import UserRegister, UserLogin, TokenResponse, UserOut
from ..auth import hash_password, verify_password, create_access_token, get_current_user
from ..database import db_session

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserRegister):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_in.email.strip().lower(),))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email này đã được đăng ký trên hệ thống. Vui lòng đăng nhập hoặc sử dụng email khác."
            )
        
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        hashed = hash_password(user_in.password)
        clean_email = user_in.email.strip().lower()
        
        cursor.execute("""
            INSERT INTO users (id, email, hashed_password, full_name, role, phone, university, major, graduation_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            clean_email,
            hashed,
            user_in.full_name.strip(),
            user_in.role,
            user_in.phone or "",
            user_in.university or "Đại học Quốc gia",
            user_in.major or "Công nghệ Thông tin",
            user_in.graduation_year or 2026,
            now
        ))
        
        # If student, create rich student_profile with their skills and goals
        if user_in.role == "student":
            init_skills = user_in.skills if user_in.skills else ["Python", "Git", "SQL"]
            init_roles = user_in.dream_roles if user_in.dream_roles else ["Lập trình viên"]
            init_gpa = user_in.gpa if user_in.gpa is not None else 3.2
            cursor.execute("""
                INSERT INTO student_profiles (user_id, gpa, skills, dream_roles, cv_text, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, init_gpa, json.dumps(init_skills), json.dumps(init_roles), user_in.cv_text or "", now))
            
        token = create_access_token({"sub": user_id, "email": clean_email, "role": user_in.role})
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = dict(cursor.fetchone())
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user_row
        }

@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (login_in.email,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác"
            )
        user = dict(row)
        if not verify_password(login_in.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác"
            )
        if not user.get("is_active"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị tạm khóa, vui lòng liên hệ Trung tâm Hướng nghiệp"
            )
            
        token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }

@router.get("/me", response_model=UserOut)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/demo-accounts")
def get_demo_accounts():
    return [
        {
            "role": "student",
            "role_title": "Sinh viên (Nguyễn Minh Quân - Khoa CNTT)",
            "email": "student@careerbridge.edu.vn",
            "password": "password123",
            "description": "Trải nghiệm AI Job Matching, Chấm điểm CV ATS, Phỏng vấn thử Mock Interview, Lộ trình kỹ năng."
        },
        {
            "role": "recruiter",
            "role_title": "Nhà tuyển dụng (FPT Software / TechCorp)",
            "email": "recruiter@careerbridge.edu.vn",
            "password": "password123",
            "description": "Đăng tin tuyển dụng JD, AI gợi ý danh sách ứng viên phù hợp nhất, Duyệt & Phê duyệt hồ sơ."
        },
        {
            "role": "admin",
            "role_title": "Trung tâm Hướng nghiệp / Quản trị viên trường",
            "email": "admin@careerbridge.edu.vn",
            "password": "password123",
            "description": "Dashboard thị trường, Thống kê tỷ lệ việc làm, Quản lý người dùng, Phân tích xu hướng tuyển dụng."
        }
    ]

@router.get("/registered-students")
def get_registered_students():
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.email, u.full_name, u.university, u.major, u.graduation_year,
                   p.gpa, p.skills, p.dream_roles
            FROM users u
            LEFT JOIN student_profiles p ON u.id = p.user_id
            WHERE u.role = 'student' AND u.is_active = 1
            ORDER BY u.created_at DESC
        """)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            result.append({
                "id": d["id"],
                "email": d["email"],
                "full_name": d["full_name"],
                "university": d["university"],
                "major": d["major"],
                "graduation_year": d["graduation_year"],
                "gpa": d["gpa"] or 3.2,
                "skills": json.loads(d["skills"] or "[]"),
                "dream_roles": json.loads(d["dream_roles"] or "[]")
            })
        return result
