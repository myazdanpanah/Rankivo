"""
SEO AI Tools - Database Module
PostgreSQL (primary) with SQLite fallback for persistent storage.
Stores keyword tracking snapshots, calendar events, and audit history.
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import Optional

from config import DATABASE_URL

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SQLITE_PATH = os.path.join(DATA_DIR, "rankivo.db")

_pg_pool = None


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ──────────────────────────────────────────────
# Connection Helpers
# ──────────────────────────────────────────────


def _get_pg_connection():
    """Get a PostgreSQL connection using psycopg2."""
    global _pg_pool
    try:
        import psycopg2
        # Check if existing connection is still alive
        if _pg_pool is not None:
            try:
                with _pg_pool.cursor() as cur:
                    cur.execute("SELECT 1")
                return _pg_pool
            except Exception:
                # Connection is dead, reconnect
                try:
                    _pg_pool.close()
                except Exception:
                    pass
                _pg_pool = None
        if _pg_pool is None:
            _pg_pool = psycopg2.connect(DATABASE_URL)
            _pg_pool.autocommit = True
        return _pg_pool
    except Exception as e:
        print(f"[database] PostgreSQL connection failed: {e}")
        return None


def _get_sqlite_connection():
    """Get a SQLite connection."""
    _ensure_data_dir()
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _get_connection():
    """Return PostgreSQL if available, else SQLite."""
    if DATABASE_URL:
        conn = _get_pg_connection()
        if conn:
            return conn, "pg"
    return _get_sqlite_connection(), "sqlite"


def db_get_connection():
    """Public wrapper to get database connection."""
    return _get_connection()


def init_db():
    """Create tables if they don't exist."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyword_snapshots (
                id SERIAL PRIMARY KEY,
                keyword TEXT NOT NULL,
                snapshot JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                type TEXT DEFAULT 'cluster',
                keyword TEXT DEFAULT '',
                intent TEXT DEFAULT '',
                date DATE NOT NULL,
                cluster_id INTEGER DEFAULT 0,
                status TEXT DEFAULT 'planned',
                color TEXT DEFAULT '#6c757d',
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS audit_history (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                word_count INTEGER DEFAULT 0,
                issues_count INTEGER DEFAULT 0,
                full_result JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyword_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                snapshot TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                type TEXT DEFAULT 'cluster',
                keyword TEXT DEFAULT '',
                intent TEXT DEFAULT '',
                date TEXT NOT NULL,
                cluster_id INTEGER DEFAULT 0,
                status TEXT DEFAULT 'planned',
                color TEXT DEFAULT '#6c757d',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                score INTEGER DEFAULT 0,
                word_count INTEGER DEFAULT 0,
                issues_count INTEGER DEFAULT 0,
                full_result TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
    conn.commit()
    conn.close()

    # ── Migration: add page_type column if missing ──
    _migrate_audit_history()


def _migrate_audit_history():
    """Add page_type column to audit_history if it doesn't exist."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    try:
        if db_type == "pg":
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='audit_history' AND column_name='page_type'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE audit_history ADD COLUMN page_type TEXT DEFAULT 'generic'")
        else:
            cursor.execute("PRAGMA table_info(audit_history)")
            columns = [row[1] for row in cursor.fetchall()]
            if "page_type" not in columns:
                cursor.execute("ALTER TABLE audit_history ADD COLUMN page_type TEXT DEFAULT 'generic'")
        conn.commit()
    except Exception:
        pass  # Column already exists or migration not needed
    finally:
        conn.close()


# ──────────────────────────────────────────────
# Keyword Tracking (DB-backed)
# ──────────────────────────────────────────────


def db_track_keyword(keyword: str, snapshot: dict):
    """Insert a keyword snapshot into the database."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    snapshot_json = json.dumps(snapshot, ensure_ascii=False)

    if db_type == "pg":
        cursor.execute(
            "INSERT INTO keyword_snapshots (keyword, snapshot) VALUES (%s, %s)",
            (keyword, snapshot_json),
        )
    else:
        cursor.execute(
            "INSERT INTO keyword_snapshots (keyword, snapshot) VALUES (?, ?)",
            (keyword, snapshot_json),
        )
    conn.commit()
    if db_type != "pg":
        conn.close()


def db_get_tracked_keywords() -> list[dict]:
    """Get all tracked keywords with snapshot counts and latest snapshot."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("""
            SELECT keyword,
                   COUNT(*) as snapshot_count,
                   MAX(created_at) as last_tracked,
                   (SELECT snapshot FROM keyword_snapshots ks2
                    WHERE ks2.keyword = ks1.keyword ORDER BY ks2.created_at DESC LIMIT 1) as latest
            FROM keyword_snapshots ks1
            GROUP BY keyword
            ORDER BY snapshot_count DESC
        """)
    else:
        cursor.execute("""
            SELECT keyword,
                   COUNT(*) as snapshot_count,
                   MAX(created_at) as last_tracked,
                   (SELECT snapshot FROM keyword_snapshots ks2
                    WHERE ks2.keyword = ks1.keyword ORDER BY ks2.created_at DESC LIMIT 1) as latest
            FROM keyword_snapshots ks1
            GROUP BY keyword
            ORDER BY snapshot_count DESC
        """)

    results = []
    for row in cursor.fetchall():
        latest = json.loads(row["latest"]) if row["latest"] else None
        results.append({
            "keyword": row["keyword"],
            "snapshot_count": row["snapshot_count"],
            "last_tracked": row["last_tracked"],
            "latest_snapshot": latest,
        })
    if db_type != "pg":
        conn.close()
    return results


def db_get_keyword_history(keyword: str) -> list[dict]:
    """Get all snapshots for a keyword."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute(
            "SELECT snapshot, created_at FROM keyword_snapshots WHERE keyword = %s ORDER BY created_at",
            (keyword,),
        )
    else:
        cursor.execute(
            "SELECT snapshot, created_at FROM keyword_snapshots WHERE keyword = ? ORDER BY created_at",
            (keyword,),
        )

    results = []
    for row in cursor.fetchall():
        snap = json.loads(row["snapshot"])
        snap["date"] = row["created_at"][:10] if row["created_at"] else ""
        results.append(snap)
    if db_type != "pg":
        conn.close()
    return results


def db_delete_keyword(keyword: str) -> bool:
    """Delete all snapshots for a keyword."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    if db_type == "pg":
        cursor.execute("DELETE FROM keyword_snapshots WHERE keyword = %s", (keyword,))
    else:
        cursor.execute("DELETE FROM keyword_snapshots WHERE keyword = ?", (keyword,))
    deleted = cursor.rowcount > 0
    conn.commit()
    if db_type != "pg":
        conn.close()
    return deleted


# ──────────────────────────────────────────────
# Calendar Events (DB-backed)
# ──────────────────────────────────────────────


def db_save_calendar_events(events: list[dict]):
    """Replace all calendar events."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()

    if db_type == "pg":
        cursor.execute("DELETE FROM calendar_events")
        for e in events:
            cursor.execute(
                """INSERT INTO calendar_events (id, title, type, keyword, intent, date, cluster_id, status, color)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (e["id"], e.get("title", ""), e.get("type", "cluster"), e.get("keyword", ""),
                 e.get("intent", ""), e.get("date", ""), e.get("cluster_id", 0),
                 e.get("status", "planned"), e.get("color", "#6c757d")),
            )
    else:
        cursor.execute("DELETE FROM calendar_events")
        for e in events:
            cursor.execute(
                """INSERT INTO calendar_events (id, title, type, keyword, intent, date, cluster_id, status, color)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (e["id"], e.get("title", ""), e.get("type", "cluster"), e.get("keyword", ""),
                 e.get("intent", ""), e.get("date", ""), e.get("cluster_id", 0),
                 e.get("status", "planned"), e.get("color", "#6c757d")),
            )
    conn.commit()
    if db_type != "pg":
        conn.close()


def db_load_calendar_events() -> list[dict]:
    """Load all calendar events."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calendar_events ORDER BY date")
    events = []
    for row in cursor.fetchall():
        events.append({
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "keyword": row["keyword"],
            "intent": row["intent"],
            "date": row["date"],
            "cluster_id": row["cluster_id"],
            "status": row["status"],
            "color": row["color"],
        })
    if db_type != "pg":
        conn.close()
    return events


def db_update_event_status(event_id: str, new_status: str, color: str = "") -> bool:
    """Update an event's status."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    if db_type == "pg":
        cursor.execute("UPDATE calendar_events SET status = %s, color = %s WHERE id = %s",
                       (new_status, color, event_id))
    else:
        cursor.execute("UPDATE calendar_events SET status = ?, color = ? WHERE id = ?",
                       (new_status, color, event_id))
    updated = cursor.rowcount > 0
    conn.commit()
    if db_type != "pg":
        conn.close()
    return updated


def db_delete_event(event_id: str) -> bool:
    """Delete a calendar event."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    if db_type == "pg":
        cursor.execute("DELETE FROM calendar_events WHERE id = %s", (event_id,))
    else:
        cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    if db_type != "pg":
        conn.close()
    return deleted


# ──────────────────────────────────────────────
# Audit History (DB-backed)
# ──────────────────────────────────────────────


def db_save_audit(audit_result: dict):
    """Save an audit result to history."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    url = audit_result.get("final_url", audit_result.get("url", ""))
    score = audit_result.get("score", 0)
    wc = audit_result.get("word_count", 0)
    issues_count = len(audit_result.get("issues", []))
    page_type = audit_result.get("page_type", "generic")
    full_json = json.dumps(audit_result, ensure_ascii=False)

    if db_type == "pg":
        cursor.execute(
            "INSERT INTO audit_history (url, score, word_count, issues_count, page_type, full_result) VALUES (%s, %s, %s, %s, %s, %s)",
            (url, score, wc, issues_count, page_type, full_json),
        )
    else:
        cursor.execute(
            "INSERT INTO audit_history (url, score, word_count, issues_count, page_type, full_result) VALUES (?, ?, ?, ?, ?, ?)",
            (url, score, wc, issues_count, page_type, full_json),
        )
    conn.commit()
    if db_type != "pg":
        conn.close()


def db_get_audit_history(limit: int = 50) -> list[dict]:
    """Get recent audit history."""
    conn, db_type = _get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT url, score, word_count, issues_count, page_type, created_at FROM audit_history ORDER BY created_at DESC LIMIT ?"
        if db_type == "sqlite"
        else f"SELECT url, score, word_count, issues_count, page_type, created_at FROM audit_history ORDER BY created_at DESC LIMIT {limit}",
        () if db_type == "pg" else (limit,),
    )
    results = [dict(row) for row in cursor.fetchall()]
    if db_type != "pg":
        conn.close()
    return results


# Initialize DB on import
init_db()
