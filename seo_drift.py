"""
Rankivo — SEO Drift Monitoring Module
Tracks SEO changes over time using SQLite snapshots.
Detects regressions, improvements, and anomalies between audit runs.
"""
import os
import json
import sqlite3
from datetime import datetime
from config import _safe_print

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DRIFT_DB = os.path.join(DATA_DIR, "seo_drift.db")


def _ensure_db():
    """Create drift tracking tables if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DRIFT_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drift_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            snapshot_type TEXT DEFAULT 'audit',
            score INTEGER DEFAULT 0,
            word_count INTEGER DEFAULT 0,
            issues_count INTEGER DEFAULT 0,
            h1_count INTEGER DEFAULT 0,
            h2_count INTEGER DEFAULT 0,
            internal_links INTEGER DEFAULT 0,
            external_links INTEGER DEFAULT 0,
            images_total INTEGER DEFAULT 0,
            images_with_alt INTEGER DEFAULT 0,
            has_canonical INTEGER DEFAULT 0,
            has_schema INTEGER DEFAULT 0,
            meta_desc_length INTEGER DEFAULT 0,
            title_length INTEGER DEFAULT 0,
            text_to_html_ratio REAL DEFAULT 0,
            full_data TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_drift_url ON drift_snapshots(url)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_drift_date ON drift_snapshots(created_at)
    """)

    conn.commit()
    conn.close()


def save_snapshot(url: str, audit_data: dict) -> dict:
    """
    Save an audit snapshot for drift tracking.
    Extracts key metrics for efficient comparison.
    """
    _ensure_db()

    # Extract key metrics from audit data
    headings = audit_data.get("headings", {})
    links = audit_data.get("links", {})
    images = audit_data.get("images", {})

    snapshot = {
        "url": url,
        "score": audit_data.get("score", 0),
        "word_count": audit_data.get("word_count", 0),
        "issues_count": len(audit_data.get("issues", [])),
        "h1_count": len(headings.get("h1", [])),
        "h2_count": len(headings.get("h2", [])),
        "internal_links": links.get("internal_count", 0),
        "external_links": links.get("external_count", 0),
        "images_total": images.get("total", 0),
        "images_with_alt": images.get("with_alt", 0),
        "has_canonical": 1 if audit_data.get("canonical") else 0,
        "has_schema": 1 if audit_data.get("schemas_found", 0) > 0 or any(
            "schema" in str(audit_data.get("structured_data", {}))
        ) else 0,
        "meta_desc_length": len(audit_data.get("meta_description", "") or ""),
        "title_length": len(audit_data.get("page_title", "") or ""),
        "text_to_html_ratio": audit_data.get("text_to_html_ratio", 0),
        "full_data": json.dumps(audit_data, ensure_ascii=False),
    }

    conn = sqlite3.connect(DRIFT_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO drift_snapshots (
            url, snapshot_type, score, word_count, issues_count,
            h1_count, h2_count, internal_links, external_links,
            images_total, images_with_alt, has_canonical, has_schema,
            meta_desc_length, title_length, text_to_html_ratio, full_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        snapshot["url"], "audit", snapshot["score"], snapshot["word_count"],
        snapshot["issues_count"], snapshot["h1_count"], snapshot["h2_count"],
        snapshot["internal_links"], snapshot["external_links"],
        snapshot["images_total"], snapshot["images_with_alt"],
        snapshot["has_canonical"], snapshot["has_schema"],
        snapshot["meta_desc_length"], snapshot["title_length"],
        snapshot["text_to_html_ratio"], snapshot["full_data"],
    ))
    conn.commit()
    snapshot_id = cursor.lastrowid
    conn.close()

    return {"success": True, "snapshot_id": snapshot_id, "url": url}


def get_history(url: str, limit: int = 50) -> list[dict]:
    """Get snapshot history for a URL."""
    _ensure_db()
    conn = sqlite3.connect(DRIFT_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM drift_snapshots
        WHERE url = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (url, limit))

    results = []
    for row in cursor.fetchall():
        results.append({
            "id": row["id"],
            "url": row["url"],
            "score": row["score"],
            "word_count": row["word_count"],
            "issues_count": row["issues_count"],
            "h1_count": row["h1_count"],
            "h2_count": row["h2_count"],
            "internal_links": row["internal_links"],
            "external_links": row["external_links"],
            "has_canonical": row["has_canonical"],
            "meta_desc_length": row["meta_desc_length"],
            "title_length": row["title_length"],
            "created_at": row["created_at"],
        })

    conn.close()
    return results


def compare_snapshots(url: str) -> dict:
    """
    Compare the two most recent snapshots for a URL.
    Detect regressions, improvements, and anomalies.
    """
    _ensure_db()
    history = get_history(url, limit=2)

    if len(history) < 2:
        return {
            "url": url,
            "has_comparison": False,
            "message": "Need at least 2 snapshots to compare. Run audit again later.",
            "snapshot_count": len(history),
        }

    current = history[0]  # most recent
    previous = history[1]  # second most recent

    # Calculate deltas
    changes = []
    regressions = []
    improvements = []

    metrics = {
        "score": {"label": "SEO Score", "unit": "pts"},
        "word_count": {"label": "Word Count", "unit": "words"},
        "issues_count": {"label": "Issues", "unit": "issues"},
        "h2_count": {"label": "H2 Headings", "unit": ""},
        "internal_links": {"label": "Internal Links", "unit": ""},
        "external_links": {"label": "External Links", "unit": ""},
        "meta_desc_length": {"label": "Meta Description", "unit": "chars"},
    }

    for key, info in metrics.items():
        old_val = previous.get(key, 0)
        new_val = current.get(key, 0)
        delta = new_val - old_val

        if delta != 0:
            change = {
                "metric": info["label"],
                "old_value": old_val,
                "new_value": new_val,
                "delta": delta,
                "direction": "up" if delta > 0 else "down",
            }

            # Determine if it's a regression or improvement
            if key == "issues_count":
                if delta > 0:
                    change["severity"] = "regression"
                    regressions.append(change)
                else:
                    change["severity"] = "improvement"
                    improvements.append(change)
            elif key == "score":
                if delta < 0:
                    change["severity"] = "regression"
                    regressions.append(change)
                else:
                    change["severity"] = "improvement"
                    improvements.append(change)
            elif key in ("word_count", "h2_count", "internal_links", "external_links", "meta_desc_length"):
                if delta < 0:
                    change["severity"] = "regression"
                    regressions.append(change)
                else:
                    change["severity"] = "improvement"
                    improvements.append(change)

            changes.append(change)

    # Anomaly detection (unusual changes)
    anomalies = []
    if abs(current.get("score", 0) - previous.get("score", 0)) > 20:
        anomalies.append({
            "type": "score_spike",
            "message": f"Large score change: {previous.get('score', 0)} → {current.get('score', 0)}",
            "severity": "high" if current.get("score", 0) < previous.get("score", 0) else "medium",
        })

    if current.get("word_count", 0) < 100 and previous.get("word_count", 0) > 500:
        anomalies.append({
            "type": "content_loss",
            "message": f"Significant content loss: {previous.get('word_count', 0)} → {current.get('word_count', 0)} words",
            "severity": "critical",
        })

    if previous.get("has_canonical", 0) == 1 and current.get("has_canonical", 0) == 0:
        anomalies.append({
            "type": "canonical_lost",
            "message": "Canonical tag was removed",
            "severity": "high",
        })

    # Overall drift assessment
    if regressions and not improvements:
        drift_status = "regressing"
    elif improvements and not regressions:
        drift_status = "improving"
    elif regressions and improvements:
        drift_status = "mixed"
    else:
        drift_status = "stable"

    return {
        "url": url,
        "has_comparison": True,
        "drift_status": drift_status,
        "current_snapshot": current,
        "previous_snapshot": previous,
        "changes": changes,
        "regressions": regressions,
        "improvements": improvements,
        "anomalies": anomalies,
        "days_between": _days_between(current.get("created_at", ""), previous.get("created_at", "")),
    }


def get_all_tracked_urls() -> list[dict]:
    """Get all URLs being tracked with their latest snapshot."""
    _ensure_db()
    conn = sqlite3.connect(DRIFT_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT url,
               COUNT(*) as snapshot_count,
               MAX(created_at) as last_audit,
               (SELECT score FROM drift_snapshots ds2
                WHERE ds2.url = ds1.url ORDER BY ds2.created_at DESC LIMIT 1) as latest_score
        FROM drift_snapshots ds1
        GROUP BY url
        ORDER BY last_audit DESC
    """)

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def delete_url_history(url: str) -> bool:
    """Delete all snapshots for a URL."""
    _ensure_db()
    conn = sqlite3.connect(DRIFT_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM drift_snapshots WHERE url = ?", (url,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def _days_between(date_str1: str, date_str2: str) -> int:
    """Calculate days between two date strings."""
    try:
        fmt = "%Y-%m-%d %H:%M:%S"
        d1 = datetime.strptime(date_str1[:19], fmt)
        d2 = datetime.strptime(date_str2[:19], fmt)
        return abs((d1 - d2).days)
    except Exception:
        return 0
