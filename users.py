"""
SEO AI Tools - User Management Module
Handles user CRUD, password management, and authentication.
"""
import hashlib
import json
import time
from typing import Optional

import bcrypt

from database import db_get_connection


def _hash_password(pw: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def _verify_password(pw: str, pw_hash: str) -> bool:
    """Verify a password against a bcrypt hash. Falls back to SHA-256 for legacy hashes."""
    try:
        if pw_hash.startswith("$2"):
            # bcrypt hash
            return bcrypt.checkpw(pw.encode(), pw_hash.encode())
        else:
            # Legacy SHA-256 hash — verify and re-hash with bcrypt on success
            if hashlib.sha256(pw.encode()).hexdigest() == pw_hash:
                return True
            return False
    except Exception:
        return False


def _is_bcrypt_hash(pw_hash: str) -> bool:
    """Check if a hash is bcrypt format."""
    return pw_hash.startswith("$2")


def init_users_table():
    """Create the users table if it doesn't exist."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                email TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT NOW(),
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                email TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
    conn.commit()

    # Check if admin user exists, create default if not
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        # Create default admin user
        from config import ADMIN_USERNAME, ADMIN_PASSWORD
        default_password = ADMIN_PASSWORD if ADMIN_PASSWORD else "rankivo"
        if db_type == "pg":
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (ADMIN_USERNAME, _hash_password(default_password), "admin"),
            )
        else:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (ADMIN_USERNAME, _hash_password(default_password), "admin"),
            )
        conn.commit()

    conn.close()


def create_user(username: str, password: str, role: str = "user", email: str = "") -> dict:
    """Create a new user."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    try:
        if db_type == "pg":
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, email) VALUES (%s, %s, %s, %s)",
                (username, _hash_password(password), role, email),
            )
        else:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)",
                (username, _hash_password(password), role, email),
            )
        conn.commit()
        return {"success": True, "message": f"User '{username}' created"}
    except Exception as e:
        error_str = str(e)
        if "UNIQUE" in error_str or "unique" in error_str or "duplicate" in error_str:
            return {"success": False, "error": f"Username '{username}' already exists"}
        return {"success": False, "error": error_str}
    finally:
        if db_type != "pg":
            conn.close()


def delete_user(username: str) -> dict:
    """Delete a user. Cannot delete the last admin."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    # Check if this is the last admin
    if db_type == "pg":
        cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
    else:
        cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return {"success": False, "error": f"User '{username}' not found"}

    if user["role"] == "admin":
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        if admin_count <= 1:
            return {"success": False, "error": "Cannot delete the last admin user"}

    if db_type == "pg":
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    else:
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()

    if db_type != "pg":
        conn.close()
    return {"success": True, "message": f"User '{username}' deleted"}


def change_password(username: str, old_password: str, new_password: str) -> dict:
    """Change a user's password."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = %s",
            (username,),
        )
    else:
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        )
    user = cursor.fetchone()
    if not user:
        return {"success": False, "error": "User not found"}

    if not _verify_password(old_password, user["password_hash"]):
        return {"success": False, "error": "Current password is incorrect"}

    if len(new_password) < 4:
        return {"success": False, "error": "New password must be at least 4 characters"}

    if db_type == "pg":
        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = %s",
            (_hash_password(new_password), username),
        )
    else:
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (_hash_password(new_password), username),
        )
    conn.commit()

    if db_type != "pg":
        conn.close()
    return {"success": True, "message": "Password changed successfully"}


def verify_user(username: str, password: str) -> Optional[dict]:
    """Verify user credentials. Returns user info dict or None."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    # Fetch user by username only (can't filter by password_hash with bcrypt)
    if db_type == "pg":
        cursor.execute(
            "SELECT username, role, email, is_active, password_hash FROM users WHERE username = %s",
            (username,),
        )
    else:
        cursor.execute(
            "SELECT username, role, email, is_active, password_hash FROM users WHERE username = ?",
            (username,),
        )
    user = cursor.fetchone()

    if not user:
        if db_type != "pg":
            conn.close()
        return None

    user_dict = dict(user)

    # Verify password using bcrypt (with SHA-256 backward compat)
    if not _verify_password(password, user_dict.get("password_hash", "")):
        if db_type != "pg":
            conn.close()
        return None

    # Check if user is active (SQLite uses 0/1, PG uses True/False)
    is_active = user_dict.get("is_active", True)
    if not bool(is_active):
        if db_type != "pg":
            conn.close()
        return None

    # If password was verified via legacy SHA-256, upgrade to bcrypt
    if not _is_bcrypt_hash(user_dict.get("password_hash", "")):
        new_hash = _hash_password(password)
        if db_type == "pg":
            cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s", (new_hash, username))
        else:
            cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hash, username))
        conn.commit()

    # Update last login
    if db_type == "pg":
        cursor.execute("UPDATE users SET last_login = NOW() WHERE username = %s", (username,))
    else:
        cursor.execute("UPDATE users SET last_login = datetime('now') WHERE username = ?", (username,))
    conn.commit()

    if db_type != "pg":
        conn.close()

    return {
        "username": user_dict.get("username", ""),
        "role": user_dict.get("role", "user"),
        "email": user_dict.get("email", ""),
    }


def get_all_users() -> list[dict]:
    """Get all users."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, email, created_at, last_login, is_active FROM users ORDER BY created_at")
    
    users = []
    for row in cursor.fetchall():
        # Convert row to dict for safe access
        row_dict = dict(row)
        users.append({
            "username": row_dict.get("username", ""),
            "role": row_dict.get("role", "user"),
            "email": row_dict.get("email", ""),
            "created_at": row_dict.get("created_at", ""),
            "last_login": row_dict.get("last_login", ""),
            "is_active": bool(row_dict.get("is_active", True)),
        })
    
    if db_type != "pg":
        conn.close()
    return users


# ──────────────────────────────────────────────
# Settings Management
# ──────────────────────────────────────────────


def init_settings_table():
    """Create the settings table if it doesn't exist."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
    conn.commit()
    conn.close()


def get_setting(key: str, default: str = "") -> str:
    """Get a setting value."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("SELECT value FROM settings WHERE key = %s", (key,))
    else:
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    
    if db_type != "pg":
        conn.close()
    
    if row:
        return row["value"]
    return default


def set_setting(key: str, value: str):
    """Set or update a setting value."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("""
            INSERT INTO settings (key, value, updated_at) VALUES (%s, %s, NOW())
            ON CONFLICT (key) DO UPDATE SET value = %s, updated_at = NOW()
        """, (key, value, value))
    else:
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, datetime('now'))
        """, (key, value))
    conn.commit()

    if db_type != "pg":
        conn.close()


def get_all_settings() -> dict:
    """Get all settings as a dict."""
    conn, db_type = db_get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    
    settings = {}
    for row in cursor.fetchall():
        settings[row["key"]] = row["value"]
    
    if db_type != "pg":
        conn.close()
    return settings


# Initialize on import
init_users_table()
init_settings_table()
