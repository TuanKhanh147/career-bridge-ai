import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from ..models import (
    JobPostingCreate, JobPostingOut, ApplicationCreate,
    ApplicationOut, ApplicationStatusUpdate
)
from ..auth import get_current_user, require_roles
from ..database import db_session
from ..services.matching_engine import calculate_match

router = APIRouter(prefix="/api/jobs", tags=["Job Postings & Matching"])

@router.get("", response_model=List[JobPostingOut])
def list_jobs(
    q: Optional[str] = None,
    job_type: Optional[str] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user)
):
    with db_session() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM job_postings WHERE is_active = 1"
        params = []
        
        if q:
            query += " AND (title LIKE ? OR company_name LIKE ? OR description LIKE ? OR required_skills LIKE ?)"
            wildcard = f"%{q}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])
        if job_type:
            query += " AND job_type = ?"
            params.append(job_type)
        if industry:
            query += " AND industry = ?"
            params.append(industry)
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
            
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        job_rows = cursor.fetchall()

        # If user is a student, compute AI Match scores
        student_profile = None
        if current_user and current_user.get("role") == "student":
            cursor.execute("SELECT * FROM student_profiles WHERE user_id = ?", (current_user["id"],))
            p_row = cursor.fetchone()
            if p_row:
                student_profile = dict(p_row)

        results = []
        for row in job_rows:
            job = dict(row)
            skills = json.loads(job["required_skills"] or "[]")
            
            match_score = None
            match_analysis = None
            if student_profile:
                analysis = calculate_match(student_profile, current_user, job)
                match_score = analysis["match_score"]
                match_analysis = analysis

            results.append({
                "id": job["id"],
                "recruiter_id": job["recruiter_id"],
                "title": job["title"],
                "company_name": job["company_name"],
                "company_logo": job["company_logo"],
                "location": job["location"],
                "job_type": job["job_type"],
                "salary_range": job["salary_range"],
                "description": job["description"],
                "requirements": job["requirements"],
                "responsibilities": job["responsibilities"],
                "required_skills": skills,
                "industry": job["industry"],
                "min_gpa": job["min_gpa"],
                "is_active": bool(job["is_active"]),
                "created_at": job["created_at"],
                "match_score": match_score,
                "match_analysis": match_analysis
            })

        # If student, sort by match_score descending
        if student_profile:
            results.sort(key=lambda x: (x["match_score"] or 0), reverse=True)

        return results

@router.get("/{job_id}", response_model=JobPostingOut)
def get_job(job_id: str, current_user: Optional[dict] = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_postings WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy việc làm")
        
        job = dict(row)
        skills = json.loads(job["required_skills"] or "[]")
        
        match_score = None
        match_analysis = None
        if current_user and current_user.get("role") == "student":
            cursor.execute("SELECT * FROM student_profiles WHERE user_id = ?", (current_user["id"],))
            p_row = cursor.fetchone()
            if p_row:
                analysis = calculate_match(dict(p_row), current_user, job)
                match_score = analysis["match_score"]
                match_analysis = analysis

        return {
            "id": job["id"],
            "recruiter_id": job["recruiter_id"],
            "title": job["title"],
            "company_name": job["company_name"],
            "company_logo": job["company_logo"],
            "location": job["location"],
            "job_type": job["job_type"],
            "salary_range": job["salary_range"],
            "description": job["description"],
            "requirements": job["requirements"],
            "responsibilities": job["responsibilities"],
            "required_skills": skills,
            "industry": job["industry"],
            "min_gpa": job["min_gpa"],
            "is_active": bool(job["is_active"]),
            "created_at": job["created_at"],
            "match_score": match_score,
            "match_analysis": match_analysis
        }

@router.post("", response_model=JobPostingOut)
def create_job(job_in: JobPostingCreate, current_user: dict = Depends(require_roles("recruiter", "admin"))):
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_postings (
                id, recruiter_id, title, company_name, company_logo, location,
                job_type, salary_range, description, requirements, responsibilities,
                required_skills, industry, min_gpa, is_active, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """, (
            job_id,
            current_user["id"],
            job_in.title,
            job_in.company_name,
            job_in.company_logo or "",
            job_in.location,
            job_in.job_type,
            job_in.salary_range,
            job_in.description,
            job_in.requirements,
            job_in.responsibilities or "",
            json.dumps(job_in.required_skills or []),
            job_in.industry,
            job_in.min_gpa or 0.0,
            now
        ))

    return get_job(job_id, current_user)

@router.put("/{job_id}", response_model=JobPostingOut)
def update_job(job_id: str, job_in: JobPostingCreate, current_user: dict = Depends(require_roles("recruiter", "admin"))):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_postings WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy việc làm")
        
        job = dict(row)
        if current_user["role"] != "admin" and job["recruiter_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Không có quyền chỉnh sửa tin tuyển dụng này")

        cursor.execute("""
            UPDATE job_postings
            SET title = ?, company_name = ?, location = ?, job_type = ?,
                salary_range = ?, description = ?, requirements = ?, responsibilities = ?,
                required_skills = ?, industry = ?, min_gpa = ?
            WHERE id = ?
        """, (
            job_in.title, job_in.company_name, job_in.location, job_in.job_type,
            job_in.salary_range, job_in.description, job_in.requirements, job_in.responsibilities or "",
            json.dumps(job_in.required_skills or []), job_in.industry, job_in.min_gpa or 0.0,
            job_id
        ))

    return get_job(job_id, current_user)

@router.delete("/{job_id}")
def delete_job(job_id: str, current_user: dict = Depends(require_roles("recruiter", "admin"))):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_postings WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy việc làm")
        job = dict(row)
        if current_user["role"] != "admin" and job["recruiter_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Không có quyền xóa bài đăng này")
            
        cursor.execute("UPDATE job_postings SET is_active = 0 WHERE id = ?", (job_id,))
        return {"message": "Đã đóng tin tuyển dụng thành công"}

# Applications
@router.post("/{job_id}/apply", response_model=ApplicationOut)
def apply_to_job(job_id: str, app_in: ApplicationCreate, current_user: dict = Depends(require_roles("student"))):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_postings WHERE id = ? AND is_active = 1", (job_id,))
        job_row = cursor.fetchone()
        if not job_row:
            raise HTTPException(status_code=404, detail="Vị trí tuyển dụng không tồn tại hoặc đã đóng")
        job = dict(job_row)

        cursor.execute("SELECT id FROM applications WHERE job_id = ? AND student_id = ?", (job_id, current_user["id"]))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Bạn đã nộp hồ sơ ứng tuyển vị trí này rồi")

        # Get student profile and compute AI match
        cursor.execute("SELECT * FROM student_profiles WHERE user_id = ?", (current_user["id"],))
        p_row = cursor.fetchone()
        student_profile = dict(p_row) if p_row else {"skills": "[]", "gpa": 3.0}

        analysis = calculate_match(student_profile, current_user, job)
        app_id = f"app_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO applications (
                id, job_id, student_id, match_score, match_analysis, cover_note, status, applied_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'applied', ?)
        """, (
            app_id,
            job_id,
            current_user["id"],
            analysis["match_score"],
            json.dumps(analysis),
            app_in.cover_note or "",
            now
        ))

        return {
            "id": app_id,
            "job_id": job_id,
            "student_id": current_user["id"],
            "match_score": analysis["match_score"],
            "match_analysis": analysis,
            "cover_note": app_in.cover_note or "",
            "status": "applied",
            "applied_at": now
        }

@router.get("/my/applications", response_model=List[ApplicationOut])
def list_my_applications(current_user: dict = Depends(require_roles("student"))):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, j.title as job_title, j.company_name, j.location, j.job_type, j.salary_range,
                   j.description, j.requirements, j.responsibilities, j.required_skills, j.industry, j.min_gpa,
                   j.is_active as job_active, j.created_at as job_created_at
            FROM applications a
            JOIN job_postings j ON a.job_id = j.id
            WHERE a.student_id = ?
            ORDER BY a.applied_at DESC
        """, (current_user["id"],))
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            d = dict(r)
            job_obj = {
                "id": d["job_id"],
                "recruiter_id": "",
                "title": d["job_title"],
                "company_name": d["company_name"],
                "company_logo": "",
                "location": d["location"],
                "job_type": d["job_type"],
                "salary_range": d["salary_range"],
                "description": d["description"],
                "requirements": d["requirements"],
                "responsibilities": d["responsibilities"],
                "required_skills": json.loads(d["required_skills"] or "[]"),
                "industry": d["industry"],
                "min_gpa": d["min_gpa"],
                "is_active": bool(d["job_active"]),
                "created_at": d["job_created_at"]
            }
            results.append({
                "id": d["id"],
                "job_id": d["job_id"],
                "student_id": d["student_id"],
                "match_score": d["match_score"],
                "match_analysis": json.loads(d["match_analysis"] or "{}"),
                "cover_note": d["cover_note"],
                "status": d["status"],
                "applied_at": d["applied_at"],
                "job": job_obj
            })
        return results

@router.get("/{job_id}/applications", response_model=List[ApplicationOut])
def get_job_applications(job_id: str, current_user: dict = Depends(require_roles("recruiter", "admin"))):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, u.full_name, u.email, u.phone, u.university, u.major, u.graduation_year,
                   p.gpa, p.skills, p.dream_roles, p.cv_text
            FROM applications a
            JOIN users u ON a.student_id = u.id
            LEFT JOIN student_profiles p ON a.student_id = p.user_id
            WHERE a.job_id = ?
            ORDER BY a.match_score DESC
        """, (job_id,))
        rows = cursor.fetchall()

        results = []
        for r in rows:
            d = dict(r)
            student_user = {
                "id": d["student_id"],
                "email": d["email"],
                "full_name": d["full_name"],
                "role": "student",
                "phone": d["phone"],
                "university": d["university"],
                "major": d["major"],
                "graduation_year": d["graduation_year"],
                "is_active": True,
                "created_at": ""
            }
            student_profile = {
                "user_id": d["student_id"],
                "gpa": d["gpa"] or 3.0,
                "skills": json.loads(d["skills"] or "[]"),
                "dream_roles": json.loads(d["dream_roles"] or "[]"),
                "target_industries": [],
                "languages": [],
                "certifications": [],
                "experience": [],
                "education": [],
                "portfolio_links": {},
                "cv_text": d["cv_text"] or "",
                "updated_at": ""
            }
            results.append({
                "id": d["id"],
                "job_id": d["job_id"],
                "student_id": d["student_id"],
                "match_score": d["match_score"],
                "match_analysis": json.loads(d["match_analysis"] or "{}"),
                "cover_note": d["cover_note"],
                "status": d["status"],
                "applied_at": d["applied_at"],
                "student": student_user,
                "student_profile": student_profile
            })
        return results

@router.put("/applications/{app_id}/status")
def update_application_status(
    app_id: str,
    status_in: ApplicationStatusUpdate,
    current_user: dict = Depends(require_roles("recruiter", "admin"))
):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn ứng tuyển")
        
        cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (status_in.status, app_id))
        return {"message": "Cập nhật trạng thái ứng tuyển thành công", "status": status_in.status}

# AI Proactive Search: Match All Students to a Job
@router.get("/{job_id}/ai-matched-candidates")
def find_matched_candidates(job_id: str, current_user: dict = Depends(require_roles("recruiter", "admin"))):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_postings WHERE id = ?", (job_id,))
        job_row = cursor.fetchone()
        if not job_row:
            raise HTTPException(status_code=404, detail="Không tìm thấy công việc")
        job = dict(job_row)

        cursor.execute("""
            SELECT u.*, p.gpa, p.skills, p.dream_roles, p.cv_text
            FROM users u
            JOIN student_profiles p ON u.id = p.user_id
            WHERE u.role = 'student' AND u.is_active = 1
        """)
        students = cursor.fetchall()

        matched_list = []
        for s in students:
            s_dict = dict(s)
            p_dict = {
                "skills": s_dict["skills"],
                "gpa": s_dict["gpa"],
                "dream_roles": s_dict["dream_roles"],
                "cv_text": s_dict["cv_text"]
            }
            analysis = calculate_match(p_dict, s_dict, job)
            
            matched_list.append({
                "student": {
                    "id": s_dict["id"],
                    "full_name": s_dict["full_name"],
                    "email": s_dict["email"],
                    "phone": s_dict["phone"],
                    "university": s_dict["university"],
                    "major": s_dict["major"],
                    "graduation_year": s_dict["graduation_year"],
                    "gpa": s_dict["gpa"],
                    "skills": json.loads(s_dict["skills"] or "[]"),
                    "dream_roles": json.loads(s_dict["dream_roles"] or "[]")
                },
                "match_score": analysis["match_score"],
                "fit_level": analysis["fit_level"],
                "strengths": analysis["strengths"],
                "gaps": analysis["gaps"]
            })

        matched_list.sort(key=lambda x: x["match_score"], reverse=True)
        return matched_list
