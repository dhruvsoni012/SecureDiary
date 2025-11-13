# database.py
import os
import sqlite3
from cryptography.fernet import Fernet
from auth import get_kek
from datetime import datetime

DB_PATH = "diary_data/diary.db"
DIARY_KEY_FILE = "diary_data/diary.key"


def init_db():
    if not os.path.exists("diary_data"):
        os.makedirs("diary_data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content BLOB NOT NULL,
            mood TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def load_or_create_diary_key(master_password: str) -> bytes:
    """
    Return the decrypted Fernet key used for the diary.
    🔒 CRITICAL SECURITY: If diary.key is deleted, ALL entries become undecryptable!
    """
    if not os.path.exists(DIARY_KEY_FILE):
        # create a random diary key and encrypt it with KEK
        raw_diary_key = Fernet.generate_key()
        kek = get_kek(master_password)
        f = Fernet(kek)
        enc_diary_key = f.encrypt(raw_diary_key)
        with open(DIARY_KEY_FILE, "wb") as f_out:
            f_out.write(enc_diary_key)
        return raw_diary_key
    else:
        # decrypt existing diary key
        with open(DIARY_KEY_FILE, "rb") as f_in:
            enc_diary_key = f_in.read()
        kek = get_kek(master_password)
        f = Fernet(kek)
        try:
            return f.decrypt(enc_diary_key)
        except Exception:
            raise ValueError("Wrong master password: unable to decrypt diary key.")


def encrypt_content(content: str, key: bytes) -> bytes:
    return Fernet(key).encrypt(content.encode())


def decrypt_content(enc_content: bytes, key: bytes) -> str:
    """
    🔒 CRITICAL: This will fail if diary.key was deleted/corrupted
    """
    return Fernet(key).decrypt(enc_content).decode()


def add_entry(title, content, key, mood=None, tags=None):
    """Add new diary entry"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    enc_content = encrypt_content(content, key)
    cur.execute("""
        INSERT INTO entries (title, content, mood, tags, created_at, updated_at, is_favorite)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (title, enc_content, mood, tags, datetime.now(), datetime.now()))
    conn.commit()
    conn.close()


def update_entry(entry_id, title, content, key, mood=None, tags=None):
    """Update existing diary entry"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    enc_content = encrypt_content(content, key)
    cur.execute("""
        UPDATE entries 
        SET title=?, content=?, mood=?, tags=?, updated_at=?
        WHERE id=?
    """, (title, enc_content, mood, tags, datetime.now(), entry_id))
    conn.commit()
    conn.close()


def delete_entry(entry_id):
    """Delete diary entry"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()


def toggle_favorite(entry_id):
    """Toggle favorite status"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT is_favorite FROM entries WHERE id=?", (entry_id,))
    current = cur.fetchone()[0]
    cur.execute("UPDATE entries SET is_favorite=? WHERE id=?", (1 if current == 0 else 0, entry_id))
    conn.commit()
    conn.close()


def fetch_entries(key, search_query=None, filter_mood=None, filter_favorite=False):
    """
    Fetch all diary entries with optional filters.
    🔒 Returns 'Undecryptable' if diary.key is missing/corrupted
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    query = "SELECT id, title, content, mood, tags, created_at, updated_at, is_favorite FROM entries WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND title LIKE ?"
        params.append(f'%{search_query}%')
    
    if filter_mood:
        query += " AND mood=?"
        params.append(filter_mood)
    
    if filter_favorite:
        query += " AND is_favorite=1"
    
    query += " ORDER BY created_at DESC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        try:
            # 🔒 CRITICAL: This will fail if diary.key was deleted
            content = decrypt_content(r[2], key)
            decryptable = True
        except Exception:
            content = "🔒 Undecryptable - Diary key missing or corrupted"
            decryptable = False
        
        result.append({
            "id": r[0],
            "title": r[1],
            "content": content,
            "mood": r[3],
            "tags": r[4],
            "created_at": r[5],
            "updated_at": r[6],
            "is_favorite": r[7] == 1,
            "decryptable": decryptable
        })
    
    return result


def get_entry_by_id(entry_id, key):
    """Get single entry by ID"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, mood, tags, created_at, updated_at, is_favorite FROM entries WHERE id=?", (entry_id,))
    r = cur.fetchone()
    conn.close()
    
    if not r:
        return None
    
    try:
        content = decrypt_content(r[2], key)
        decryptable = True
    except Exception:
        content = "🔒 Undecryptable"
        decryptable = False
    
    return {
        "id": r[0],
        "title": r[1],
        "content": content,
        "mood": r[3],
        "tags": r[4],
        "created_at": r[5],
        "updated_at": r[6],
        "is_favorite": r[7] == 1,
        "decryptable": decryptable
    }


def get_stats():
    """Get diary statistics"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM entries")
    total = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM entries WHERE is_favorite=1")
    favorites = cur.fetchone()[0]
    
    cur.execute("SELECT mood, COUNT(*) FROM entries WHERE mood IS NOT NULL GROUP BY mood")
    moods = dict(cur.fetchall())
    
    conn.close()
    
    return {
        "total_entries": total,
        "favorites": favorites,
        "moods": moods,
        "diary_encrypted": os.path.exists(DIARY_KEY_FILE)
    }