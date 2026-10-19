import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from ..models import UserOut, UserUpdate, UserRegister
from ..auth import get_current_user, require_roles, hash_password
from ..database import db_session

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.get("", response_model=List[UserOut])
def list_users(
    role: Optional[str] = None,
    q: Optional[str] = None,
    current_user: dict = Depends(require_roles("admin"))
):
    with db_session() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if role:
            query += " AND role = ?"
            params.append(role)
        if q:
            query += " AND (full_name LIKE ? OR email LIKE ? OR university LIKE ? OR major LIKE ?)"
            wildcard = f"%{q}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])
            
        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # Students and recruiters can only view their own user details, unless admin
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền xem chi tiết người dùng này")
        
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
        return dict(row)

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, user_in: UserUpdate, current_user: dict = Depends(get_current_user)):
    # Regular users can only update their own non-privileged info
    is_admin = current_user["role"] == "admin"
    if not is_admin and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền chỉnh sửa người dùng này")

    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
        
        current = dict(row)
        new_name = user_in.full_name if user_in.full_name is not None else current["full_name"]
        new_phone = user_in.phone if user_in.phone is not None else current["phone"]
        new_avatar = user_in.avatar if user_in.avatar is not None else current["avatar"]
        new_uni = user_in.university if user_in.university is not None else current["university"]
        new_major = user_in.major if user_in.major is not None else current["major"]
        new_year = user_in.graduation_year if user_in.graduation_year is not None else current["graduation_year"]
        new_bio = user_in.bio if user_in.bio is not None else current["bio"]
        
        # Only admin can change role and is_active
        new_role = user_in.role if (is_admin and user_in.role) else current["role"]
        new_active = int(user_in.is_active) if (is_admin and user_in.is_active is not None) else current["is_active"]

        cursor.execute("""
            UPDATE users
            SET full_name = ?, phone = ?, avatar = ?, university = ?,
                major = ?, graduation_year = ?, bio = ?, role = ?, is_active = ?
            WHERE id = ?
        """, (
            new_name, new_phone, new_avatar, new_uni,
            new_major, new_year, new_bio, new_role, new_active,
            user_id
        ))

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return dict(cursor.fetchone())

@router.delete("/{user_id}")
def delete_user(user_id: str, current_user: dict = Depends(require_roles("admin"))):
    if current_user["id"] == user_id:
        raise HTTPException(status_code=400, detail="Không thể tự khóa tài khoản quản trị viên của chính bạn")
        
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
        return {"message": "Đã tạm khóa tài khoản thành công"}
