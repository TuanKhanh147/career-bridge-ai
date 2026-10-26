import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Header
from ..models import ChatMessageRequest, ChatMessageResponse
from ..services.ai_service import generate_career_chat_response
from ..database import db_session
from ..auth import get_optional_user

router = APIRouter(prefix="/api/chatbot", tags=["AI Career Chatbot"])

STARTER_SUGGESTIONS = [
    {
        "icon": "💼",
        "title": "Gợi ý việc làm thực tập mới",
        "prompt": "Gợi ý cho tôi các việc làm thực tập và fresher đang tuyển dụng trên hệ thống"
    },
    {
        "icon": "💰",
        "title": "Tra cứu mức lương 2026",
        "prompt": "Mức lương thị trường cho vị trí Thực tập sinh và Fresher hiện nay là bao nhiêu?"
    },
    {
        "icon": "📝",
        "title": "Bí quyết viết CV chuẩn ATS",
        "prompt": "Làm thế nào để viết CV chuẩn ATS và vượt qua vòng quét hồ sơ tự động?"
    },
    {
        "icon": "🎙️",
        "title": "Mẹo phỏng vấn câu 'Điểm yếu'",
        "prompt": "Cách trả lời câu hỏi phỏng vấn: Điểm yếu lớn nhất của bạn là gì?"
    },
    {
        "icon": "🧭",
        "title": "Định hướng nghề nghiệp",
        "prompt": "Tư vấn định hướng nghề nghiệp phù hợp với sinh viên chưa rõ đam mê"
    },
    {
        "icon": "🗺️",
        "title": "Lộ trình kỹ năng AI & Data",
        "prompt": "Lộ trình tự học từ con số 0 để làm Data Analyst hoặc AI Engineer"
    }
]

@router.get("/suggestions")
def get_chat_suggestions():
    return {
        "status": "success",
        "suggestions": STARTER_SUGGESTIONS
    }

@router.post("/chat", response_model=ChatMessageResponse)
def handle_chat_message(
    body: ChatMessageRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    session_id = body.session_id or f"sess_{uuid.uuid4().hex[:12]}"
    context = body.context or {}

    user_id = None
    if current_user:
        user_id = current_user.get("id")
        context.setdefault("full_name", current_user.get("full_name"))
        context.setdefault("major", current_user.get("major"))
        context.setdefault("university", current_user.get("university"))
        
        # Load user profile skills if present
        try:
            with db_session() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT skills, dream_roles, gpa FROM student_profiles WHERE user_id = ?", (user_id,))
                p = cursor.fetchone()
                if p:
                    context.setdefault("skills", json.loads(p["skills"]) if p["skills"] else [])
                    context.setdefault("dream_roles", json.loads(p["dream_roles"]) if p["dream_roles"] else [])
                    context.setdefault("gpa", p["gpa"])
        except Exception:
            pass

    response_data = generate_career_chat_response(
        message=body.message,
        session_id=session_id,
        context=context,
        user_id=user_id
    )

    return ChatMessageResponse(**response_data)

@router.get("/history")
def get_chat_history(session_id: str):
    if not session_id:
        return {"session_id": "", "messages": []}

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, session_id, sender, message, metadata, created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))
        rows = cursor.fetchall()

        messages = []
        for r in rows:
            meta = {}
            try:
                meta = json.loads(r["metadata"]) if r["metadata"] else {}
            except Exception:
                meta = {}
            messages.append({
                "id": r["id"],
                "sender": r["sender"],
                "message": r["message"],
                "metadata": meta,
                "created_at": r["created_at"]
            })

    return {
        "session_id": session_id,
        "messages": messages
    }

@router.post("/clear")
def clear_chat_history(body: Dict[str, str]):
    session_id = body.get("session_id")
    if session_id:
        with db_session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))

    return {"status": "success", "message": "Đã xóa lịch sử cuộc trò chuyện."}
