from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UserRegister(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = Field("student", pattern="^(student|recruiter|admin)$")
    phone: Optional[str] = ""
    university: Optional[str] = ""
    major: Optional[str] = ""
    graduation_year: Optional[int] = 2026
    gpa: Optional[float] = 3.2
    skills: Optional[List[str]] = []
    dream_roles: Optional[List[str]] = []
    cv_text: Optional[str] = ""

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = ""
    avatar: Optional[str] = ""
    university: Optional[str] = ""
    major: Optional[str] = ""
    graduation_year: Optional[int] = 2026
    bio: Optional[str] = ""
    is_active: bool = True
    created_at: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# Student Profile Models
class StudentProfileUpdate(BaseModel):
    gpa: Optional[float] = 3.0
    skills: Optional[List[str]] = []
    dream_roles: Optional[List[str]] = []
    target_industries: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    experience: Optional[List[Dict[str, Any]]] = []
    education: Optional[List[Dict[str, Any]]] = []
    portfolio_links: Optional[Dict[str, str]] = {}
    cv_text: Optional[str] = ""

class StudentProfileOut(BaseModel):
    user_id: str
    gpa: float
    skills: List[str]
    dream_roles: List[str]
    target_industries: List[str]
    languages: List[str]
    certifications: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    portfolio_links: Dict[str, str]
    cv_text: str
    updated_at: str
    user_info: Optional[UserOut] = None

# Job Posting Models
class JobPostingCreate(BaseModel):
    title: str
    company_name: str
    company_logo: Optional[str] = ""
    location: str
    job_type: str
    salary_range: str
    description: str
    requirements: str
    responsibilities: Optional[str] = ""
    required_skills: List[str]
    industry: str
    min_gpa: Optional[float] = 0.0

class JobPostingOut(BaseModel):
    id: str
    recruiter_id: str
    title: str
    company_name: str
    company_logo: str
    location: str
    job_type: str
    salary_range: str
    description: str
    requirements: str
    responsibilities: str
    required_skills: List[str]
    industry: str
    min_gpa: float
    is_active: bool
    created_at: str
    match_score: Optional[float] = None
    match_analysis: Optional[Dict[str, Any]] = None

# Application Models
class ApplicationCreate(BaseModel):
    job_id: str
    cover_note: Optional[str] = ""

class ApplicationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(applied|reviewing|interview_scheduled|accepted|rejected)$")

class ApplicationOut(BaseModel):
    id: str
    job_id: str
    student_id: str
    match_score: float
    match_analysis: Dict[str, Any]
    cover_note: str
    status: str
    applied_at: str
    job: Optional[JobPostingOut] = None
    student: Optional[UserOut] = None
    student_profile: Optional[StudentProfileOut] = None

# CV Review Models
class CVReviewRequest(BaseModel):
    cv_text: str
    target_role: Optional[str] = ""

class CVReviewOut(BaseModel):
    id: str
    ats_score: int
    target_role: str
    strengths: List[str]
    weaknesses: List[str]
    missing_keywords: List[str]
    bullet_rewrites: List[Dict[str, str]]
    action_recommendations: List[str]
    created_at: str

# Mock Interview Models
class MockInterviewStartRequest(BaseModel):
    role_title: str
    difficulty: str = "Fresher / Thực tập sinh"
    interview_type: str = "Tổng hợp (Kỹ thuật + Tình huống + Behavioral)"

class MockInterviewSubmitAnswerRequest(BaseModel):
    interview_id: str
    question_index: int
    user_answer: str

class MockInterviewOut(BaseModel):
    id: str
    role_title: str
    difficulty: str
    interview_type: str
    questions_data: List[Dict[str, Any]]
    answers_data: List[Dict[str, Any]]
    overall_score: float
    feedback: Dict[str, Any]
    created_at: str

# Skill Gap Roadmap Models
class SkillRoadmapRequest(BaseModel):
    target_role: str

class SkillRoadmapOut(BaseModel):
    id: str
    target_role: str
    current_skills: List[str]
    missing_skills: List[str]
    readiness_percentage: int
    milestones: List[Dict[str, Any]]
    created_at: str
