import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from ..models import (
    StudentProfileOut, StudentProfileUpdate,
    CVReviewRequest, CVReviewOut,
    MockInterviewStartRequest, MockInterviewSubmitAnswerRequest, MockInterviewOut,
    SkillRoadmapRequest, SkillRoadmapOut
)
from ..auth import get_current_user, require_roles
from ..database import db_session
from ..services.ai_service import (
    analyze_cv_content, get_mock_questions,
    evaluate_interview_answer, generate_skill_roadmap
)

router = APIRouter(prefix="/api/students", tags=["Student Features"])

@router.get("/profile", response_model=StudentProfileOut)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_profiles WHERE user_id = ?", (current_user["id"],))
        row = cursor.fetchone()
        
        if not row:
            # Create if not exists
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO student_profiles (user_id, gpa, skills, dream_roles, updated_at)
                VALUES (?, 3.2, '["Python", "Git", "SQL"]', '["Backend Developer"]', ?)
            """, (current_user["id"], now))
            cursor.execute("SELECT * FROM student_profiles WHERE user_id = ?", (current_user["id"],))
            row = cursor.fetchone()
            
        data = dict(row)
        return {
            "user_id": data["user_id"],
            "gpa": data["gpa"],
            "skills": json.loads(data["skills"] or "[]"),
            "dream_roles": json.loads(data["dream_roles"] or "[]"),
            "target_industries": json.loads(data["target_industries"] or "[]"),
            "languages": json.loads(data["languages"] or "[]"),
            "certifications": json.loads(data["certifications"] or "[]"),
            "experience": json.loads(data["experience"] or "[]"),
            "education": json.loads(data["education"] or "[]"),
            "portfolio_links": json.loads(data["portfolio_links"] or "{}"),
            "cv_text": data["cv_text"] or "",
            "updated_at": data["updated_at"],
            "user_info": current_user
        }

@router.put("/profile", response_model=StudentProfileOut)
def update_profile(profile_in: StudentProfileUpdate, current_user: dict = Depends(get_current_user)):
    now = datetime.now().isoformat()
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE student_profiles
            SET gpa = ?, skills = ?, dream_roles = ?, target_industries = ?,
                languages = ?, certifications = ?, experience = ?, education = ?,
                portfolio_links = ?, cv_text = ?, updated_at = ?
            WHERE user_id = ?
        """, (
            profile_in.gpa,
            json.dumps(profile_in.skills or []),
            json.dumps(profile_in.dream_roles or []),
            json.dumps(profile_in.target_industries or []),
            json.dumps(profile_in.languages or []),
            json.dumps(profile_in.certifications or []),
            json.dumps(profile_in.experience or []),
            json.dumps(profile_in.education or []),
            json.dumps(profile_in.portfolio_links or {}),
            profile_in.cv_text or "",
            now,
            current_user["id"]
        ))
        
    return get_my_profile(current_user)

# CV Reviewer & ATS Optimizer
@router.post("/cv-review", response_model=CVReviewOut)
def create_cv_review(req: CVReviewRequest, current_user: dict = Depends(get_current_user)):
    analysis = analyze_cv_content(req.cv_text, req.target_role or "")
    review_id = f"cvr_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()
    
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cv_reviews (
                id, student_id, target_role, ats_score, strengths,
                weaknesses, missing_keywords, bullet_rewrites, action_recommendations, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            review_id,
            current_user["id"],
            analysis["target_role"],
            analysis["ats_score"],
            json.dumps(analysis["strengths"]),
            json.dumps(analysis["weaknesses"]),
            json.dumps(analysis["missing_keywords"]),
            json.dumps(analysis["bullet_rewrites"]),
            json.dumps(analysis["action_recommendations"]),
            now
        ))
        
        # Also update student's cv_text if empty or shorter
        cursor.execute("SELECT cv_text FROM student_profiles WHERE user_id = ?", (current_user["id"],))
        p = cursor.fetchone()
        if p and (not p["cv_text"] or len(req.cv_text) > len(p["cv_text"])):
            cursor.execute("UPDATE student_profiles SET cv_text = ? WHERE user_id = ?", (req.cv_text, current_user["id"]))

    return {
        "id": review_id,
        "ats_score": analysis["ats_score"],
        "target_role": analysis["target_role"],
        "strengths": analysis["strengths"],
        "weaknesses": analysis["weaknesses"],
        "missing_keywords": analysis["missing_keywords"],
        "bullet_rewrites": analysis["bullet_rewrites"],
        "action_recommendations": analysis["action_recommendations"],
        "created_at": now
    }

@router.get("/cv-reviews")
def get_cv_reviews(current_user: dict = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cv_reviews WHERE student_id = ? ORDER BY created_at DESC", (current_user["id"],))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            result.append({
                "id": d["id"],
                "target_role": d["target_role"],
                "ats_score": d["ats_score"],
                "strengths": json.loads(d["strengths"] or "[]"),
                "weaknesses": json.loads(d["weaknesses"] or "[]"),
                "missing_keywords": json.loads(d["missing_keywords"] or "[]"),
                "bullet_rewrites": json.loads(d["bullet_rewrites"] or "[]"),
                "action_recommendations": json.loads(d["action_recommendations"] or "[]"),
                "created_at": d["created_at"]
            })
        return result

# Mock Interview Endpoints
@router.post("/mock-interview/start")
def start_mock_interview(req: MockInterviewStartRequest, current_user: dict = Depends(get_current_user)):
    questions = get_mock_questions(req.role_title)
    interview_id = f"intv_{uuid.uuid4().hex[:12]}"
    now = datetime.now().isoformat()
    
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mock_interviews (
                id, student_id, role_title, difficulty, interview_type,
                questions_data, answers_data, overall_score, feedback, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, '[]', 0.0, '{}', ?)
        """, (
            interview_id,
            current_user["id"],
            req.role_title,
            req.difficulty,
            req.interview_type,
            json.dumps(questions),
            now
        ))

    return {
        "id": interview_id,
        "role_title": req.role_title,
        "difficulty": req.difficulty,
        "interview_type": req.interview_type,
        "questions": questions,
        "total_questions": len(questions)
    }

@router.post("/mock-interview/answer")
def submit_mock_answer(req: MockInterviewSubmitAnswerRequest, current_user: dict = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mock_interviews WHERE id = ? AND student_id = ?", (req.interview_id, current_user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiên phỏng vấn")
        
        data = dict(row)
        questions = json.loads(data["questions_data"] or "[]")
        answers = json.loads(data["answers_data"] or "[]")
        
        if req.question_index >= len(questions):
            raise HTTPException(status_code=400, detail="Chỉ mục câu hỏi không hợp lệ")
            
        question = questions[req.question_index]
        eval_result = evaluate_interview_answer(data["role_title"], question, req.user_answer)
        
        # Record answer
        answer_entry = {
            "question_index": req.question_index,
            "question": question["question"],
            "user_answer": req.user_answer,
            "evaluation": eval_result
        }
        
        # Update or append
        existing_idx = next((i for i, a in enumerate(answers) if a["question_index"] == req.question_index), None)
        if existing_idx is not None:
            answers[existing_idx] = answer_entry
        else:
            answers.append(answer_entry)
            
        # Calculate overall score
        scores = [a["evaluation"]["score"] for a in answers]
        overall_score = round(sum(scores) / len(scores), 1) if scores else 0.0
        
        cursor.execute("""
            UPDATE mock_interviews
            SET answers_data = ?, overall_score = ?
            WHERE id = ?
        """, (json.dumps(answers), overall_score, req.interview_id))
        
        return {
            "interview_id": req.interview_id,
            "question_index": req.question_index,
            "overall_score": overall_score,
            "evaluation": eval_result,
            "is_completed": len(answers) == len(questions)
        }

@router.get("/mock-interviews")
def list_mock_interviews(current_user: dict = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mock_interviews WHERE student_id = ? ORDER BY created_at DESC", (current_user["id"],))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            results.append({
                "id": d["id"],
                "role_title": d["role_title"],
                "difficulty": d["difficulty"],
                "interview_type": d["interview_type"],
                "overall_score": d["overall_score"],
                "total_questions": len(json.loads(d["questions_data"] or "[]")),
                "answered_count": len(json.loads(d["answers_data"] or "[]")),
                "answers_data": json.loads(d["answers_data"] or "[]"),
                "created_at": d["created_at"]
            })
        return results

# Skill Gap Roadmap Endpoints
@router.post("/roadmap", response_model=SkillRoadmapOut)
def create_roadmap(req: SkillRoadmapRequest, current_user: dict = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT skills FROM student_profiles WHERE user_id = ?", (current_user["id"],))
        p = cursor.fetchone()
        skills = json.loads(p["skills"] or "[]") if p else []
        
        roadmap_data = generate_skill_roadmap(req.target_role, skills)
        roadmap_id = f"rdm_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO skill_roadmaps (
                id, student_id, target_role, current_skills, missing_skills, milestones, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            roadmap_id,
            current_user["id"],
            req.target_role,
            json.dumps(roadmap_data["current_skills"]),
            json.dumps(roadmap_data["missing_skills"]),
            json.dumps(roadmap_data["milestones"]),
            now
        ))

        return {
            "id": roadmap_id,
            "target_role": req.target_role,
            "current_skills": roadmap_data["current_skills"],
            "missing_skills": roadmap_data["missing_skills"],
            "readiness_percentage": roadmap_data["readiness_percentage"],
            "milestones": roadmap_data["milestones"],
            "created_at": now
        }

@router.get("/roadmaps")
def get_roadmaps(current_user: dict = Depends(get_current_user)):
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skill_roadmaps WHERE student_id = ? ORDER BY created_at DESC", (current_user["id"],))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            current_s = json.loads(d["current_skills"] or "[]")
            missing_s = json.loads(d["missing_skills"] or "[]")
            total = len(current_s) + len(missing_s)
            readiness = int((len(current_s) / max(1, total)) * 100) if total else 65
            results.append({
                "id": d["id"],
                "target_role": d["target_role"],
                "current_skills": current_s,
                "missing_skills": missing_s,
                "readiness_percentage": readiness,
                "milestones": json.loads(d["milestones"] or "[]"),
                "created_at": d["created_at"]
            })
        return results
