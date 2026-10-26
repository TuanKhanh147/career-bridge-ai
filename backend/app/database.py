import sqlite3
import json
from contextlib import contextmanager
from .config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db_session():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db_session() as conn:
        cursor = conn.cursor()
        
        # 1. Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'recruiter', 'admin')),
            phone TEXT DEFAULT '',
            avatar TEXT DEFAULT '',
            university TEXT DEFAULT '',
            major TEXT DEFAULT '',
            graduation_year INTEGER DEFAULT 2026,
            bio TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """)
        
        # 2. Student Profiles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            user_id TEXT PRIMARY KEY,
            gpa REAL DEFAULT 3.0,
            skills TEXT DEFAULT '[]',
            dream_roles TEXT DEFAULT '[]',
            target_industries TEXT DEFAULT '[]',
            languages TEXT DEFAULT '[]',
            certifications TEXT DEFAULT '[]',
            experience TEXT DEFAULT '[]',
            education TEXT DEFAULT '[]',
            portfolio_links TEXT DEFAULT '{}',
            cv_text TEXT DEFAULT '',
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 3. Job Postings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id TEXT PRIMARY KEY,
            recruiter_id TEXT NOT NULL,
            title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            company_logo TEXT DEFAULT '',
            location TEXT NOT NULL,
            job_type TEXT NOT NULL,
            salary_range TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT NOT NULL,
            responsibilities TEXT DEFAULT '',
            required_skills TEXT DEFAULT '[]',
            industry TEXT NOT NULL,
            min_gpa REAL DEFAULT 0.0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 4. Job Applications table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            match_score REAL DEFAULT 0.0,
            match_analysis TEXT DEFAULT '{}',
            cover_note TEXT DEFAULT '',
            status TEXT DEFAULT 'applied' CHECK(status IN ('applied', 'reviewing', 'interview_scheduled', 'accepted', 'rejected')),
            applied_at TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 5. CV Reviews table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cv_reviews (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            cv_filename TEXT DEFAULT '',
            target_role TEXT DEFAULT '',
            ats_score INTEGER DEFAULT 0,
            strengths TEXT DEFAULT '[]',
            weaknesses TEXT DEFAULT '[]',
            missing_keywords TEXT DEFAULT '[]',
            bullet_rewrites TEXT DEFAULT '[]',
            action_recommendations TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 6. Mock Interviews table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS mock_interviews (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            interview_type TEXT NOT NULL,
            questions_data TEXT DEFAULT '[]',
            answers_data TEXT DEFAULT '[]',
            overall_score REAL DEFAULT 0.0,
            feedback TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # 7. Skill Roadmaps table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_roadmaps (
            id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            target_role TEXT NOT NULL,
            current_skills TEXT DEFAULT '[]',
            missing_skills TEXT DEFAULT '[]',
            milestones TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # 8. User Activity Logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
        """)

        # 9. AI Chatbot Messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            user_id TEXT,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_messages(session_id)")
