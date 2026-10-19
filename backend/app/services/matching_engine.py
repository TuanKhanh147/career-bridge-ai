import json
import re
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return ' '.join(text.split())

def calculate_match(student_profile: Dict[str, Any], student_user: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hybrid Matching Algorithm:
    1. Skill overlap (40% weight)
    2. Semantic TF-IDF cosine similarity between CV/profile text & Job description/requirements (35% weight)
    3. Target role & industry alignment (15% weight)
    4. Academic/GPA criteria check (10% weight)
    """
    student_skills_raw = student_profile.get("skills", [])
    if isinstance(student_skills_raw, str):
        try:
            student_skills = json.loads(student_skills_raw)
        except Exception:
            student_skills = [s.strip() for s in student_skills_raw.split(',') if s.strip()]
    else:
        student_skills = student_skills_raw or []
        
    job_skills_raw = job.get("required_skills", [])
    if isinstance(job_skills_raw, str):
        try:
            job_skills = json.loads(job_skills_raw)
        except Exception:
            job_skills = [s.strip() for s in job_skills_raw.split(',') if s.strip()]
    else:
        job_skills = job_skills_raw or []

    student_skills_norm = {s.lower().strip() for s in student_skills}
    job_skills_norm = {s.lower().strip() for s in job_skills}

    # 1. Skill Overlap Calculation
    matched_skills = []
    missing_skills = []
    for js in job_skills:
        js_lower = js.lower().strip()
        found = False
        for ss in student_skills:
            ss_lower = ss.lower().strip()
            if js_lower == ss_lower or js_lower in ss_lower or ss_lower in js_lower:
                matched_skills.append(js)
                found = True
                break
        if not found:
            missing_skills.append(js)

    skill_score = 0.0
    if job_skills_norm:
        skill_score = (len(matched_skills) / len(job_skills)) * 100.0
    else:
        skill_score = 80.0

    # 2. Semantic TF-IDF Cosine Similarity
    student_doc = f"{student_user.get('major', '')} {student_user.get('bio', '')} {student_profile.get('cv_text', '')} {' '.join(student_skills)}"
    job_doc = f"{job.get('title', '')} {job.get('industry', '')} {job.get('description', '')} {job.get('requirements', '')} {job.get('responsibilities', '')} {' '.join(job_skills)}"

    student_clean = clean_text(student_doc)
    job_clean = clean_text(job_doc)

    semantic_score = 50.0
    try:
        if student_clean and job_clean:
            vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
            tfidf_matrix = vectorizer.fit_transform([student_clean, job_clean])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Normalize to percentage with reasonable scale
            semantic_score = min(100.0, max(20.0, float(sim * 130.0)))
    except Exception:
        semantic_score = 60.0

    # 3. Dream Role & Industry Alignment
    dream_roles_raw = student_profile.get("dream_roles", [])
    if isinstance(dream_roles_raw, str):
        try:
            dream_roles = json.loads(dream_roles_raw)
        except Exception:
            dream_roles = [r.strip() for r in dream_roles_raw.split(',') if r.strip()]
    else:
        dream_roles = dream_roles_raw or []

    job_title_lower = job.get("title", "").lower()
    role_matched = any(dr.lower() in job_title_lower or job_title_lower in dr.lower() for dr in dream_roles)
    industry_matched = job.get("industry", "").lower() in [i.lower() for i in student_profile.get("target_industries", []) if isinstance(i, str)]
    
    role_score = 50.0
    if role_matched and industry_matched:
        role_score = 100.0
    elif role_matched or industry_matched:
        role_score = 85.0
    elif not dream_roles:
        role_score = 70.0

    # 4. GPA & Academic Criteria Check
    student_gpa = float(student_profile.get("gpa") or 3.0)
    min_gpa = float(job.get("min_gpa") or 0.0)
    gpa_score = 100.0 if student_gpa >= min_gpa else max(40.0, 100.0 - (min_gpa - student_gpa) * 30.0)

    # Final Weighted Score
    final_score = (skill_score * 0.40) + (semantic_score * 0.30) + (role_score * 0.20) + (gpa_score * 0.10)
    final_score = round(min(99.0, max(30.0, final_score)), 1)

    # Determine Fit Level
    if final_score >= 88.0:
        fit_level = "Rất phù hợp (Top Match)"
        badge_color = "emerald"
    elif final_score >= 75.0:
        fit_level = "Phù hợp cao (High Match)"
        badge_color = "blue"
    elif final_score >= 60.0:
        fit_level = "Tiềm năng (Good Match)"
        badge_color = "amber"
    else:
        fit_level = "Cần bổ sung kỹ năng (Low Match)"
        badge_color = "gray"

    # Generate Strengths
    strengths = []
    if matched_skills:
        strengths.append(f"Đáp ứng {len(matched_skills)}/{len(job_skills)} kỹ năng chính: {', '.join(matched_skills[:4])}")
    if role_matched:
        strengths.append(f"Vị trí '{job.get('title')}' trùng khớp với nguyện vọng nghề nghiệp")
    if student_gpa >= (min_gpa or 3.0):
        strengths.append(f"Điểm học tập (GPA {student_gpa}/4.0) đạt yêu cầu tuyển dụng")
    if semantic_score >= 65:
        strengths.append("Hồ sơ năng lực có tính tương đồng cao với mô tả công việc (JD)")

    # Generate Gaps
    gaps = []
    if missing_skills:
        gaps.append(f"Cần bổ sung hoặc làm rõ kỹ năng: {', '.join(missing_skills[:3])}")
    if student_gpa < min_gpa:
        gaps.append(f"GPA hiện tại ({student_gpa}) thấp hơn yêu cầu tối thiểu của công ty ({min_gpa})")
    if not role_matched and dream_roles:
        gaps.append(f"Khác định hướng chính: bạn đang ưu tiên '{', '.join(dream_roles[:2])}'")

    # Generate Action Recommendations
    recommendations = []
    if missing_skills:
        recommendations.append(f"Tham gia khóa học hoặc tự làm mini-project với {missing_skills[0]} để bổ sung vào CV.")
    recommendations.append(f"Tùy biến mục kinh nghiệm trong CV để làm nổi bật các từ khóa: {', '.join((matched_skills or job_skills)[:3])}.")
    recommendations.append("Thực hành phỏng vấn thử (AI Mock Interview) với câu hỏi tình huống cho vị trí này.")

    return {
        "match_score": final_score,
        "fit_level": fit_level,
        "badge_color": badge_color,
        "skill_match_percentage": round(skill_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "strengths": strengths,
        "gaps": gaps,
        "recommendations": recommendations
    }
