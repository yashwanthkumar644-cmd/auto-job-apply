import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

def init_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Applied / Processed Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            platform TEXT NOT NULL,
            job_url TEXT UNIQUE NOT NULL,
            match_score REAL,
            tailored_keywords TEXT,
            cover_letter TEXT,
            status TEXT NOT NULL,  -- 'APPLIED', 'QUEUED', 'SKIPPED', 'INTERVIEW'
            applied_at DATETIME,
            notes TEXT
        )
    ''')
    
    # Candidate Profile & Preferences store
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidate_profile (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME
        )
    ''')
    
    conn.commit()
    conn.close()

def is_job_applied_or_skipped(job_url, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM job_applications WHERE job_url = ?", (job_url,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def record_job_application(job_id, title, company, location, platform, job_url, match_score, keywords, cover_letter, status, notes="", db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    keywords_str = json.dumps(keywords) if isinstance(keywords, list) else str(keywords)
    
    cursor.execute('''
        INSERT OR REPLACE INTO job_applications 
        (id, job_title, company, location, platform, job_url, match_score, tailored_keywords, cover_letter, status, applied_at, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (job_id, title, company, location, platform, job_url, match_score, keywords_str, cover_letter, status, now, notes))
    
    conn.commit()
    conn.close()

def get_application_stats(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM job_applications GROUP BY status")
    rows = cursor.fetchall()
    
    cursor.execute("SELECT AVG(match_score) FROM job_applications WHERE status = 'APPLIED'")
    avg_score = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT id, job_title, company, platform, match_score, status, applied_at FROM job_applications ORDER BY applied_at DESC LIMIT 20")
    recent = cursor.fetchall()
    
    conn.close()
    stats = {status: count for status, count in rows}
    stats["avg_match_score"] = round(avg_score, 1)
    stats["recent"] = recent
    return stats

def save_profile_key(key, data, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    value_str = json.dumps(data) if not isinstance(data, str) else data
    cursor.execute("INSERT OR REPLACE INTO candidate_profile (key, value, updated_at) VALUES (?, ?, ?)", (key, value_str, now))
    conn.commit()
    conn.close()

def get_profile_key(key, default=None, db_path=DB_PATH):
    if not os.path.exists(db_path):
        return default
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM candidate_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return default
    try:
        return json.loads(row[0])
    except Exception:
        return row[0]
