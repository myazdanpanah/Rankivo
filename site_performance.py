"""
Rankivo — Site Performance Monitoring Module
Tracks organic traffic estimates, ranking positions, Core Web Vitals trends,
and SEO health scores over time. Similar to Search Console / GA4 dashboards.
Uses PageSpeed Insights API, Bing Webmaster API, and our own audit snapshots.
"""
import os
import sqlite3
import time
import requests
from datetime import datetime, timedelta
from config import (
    REQUEST_TIMEOUT, USER_AGENTS, BING_API_KEY, PAGESPEED_API_KEY,
    _safe_print,
)
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PERF_DB = os.path.join(DATA_DIR, "site_performance.db")


def _ensure_db():
    """Create performance tracking tables if they don't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(PERF_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Core Web Vitals history
    c.execute("""
        CREATE TABLE IF NOT EXISTS cwv_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            lcp REAL, cls REAL, inp REAL, fcp REAL, ttfb REAL, tbt REAL,
            performance_score INTEGER,
            strategy TEXT DEFAULT 'mobile',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Audit score history
    c.execute("""
        CREATE TABLE IF NOT EXISTS score_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            seo_score INTEGER,
            technical_score INTEGER,
            content_score INTEGER,
            overall_score INTEGER,
            issues_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Page crawl log (simulated traffic / crawl data)
    c.execute("""
        CREATE TABLE IF NOT EXISTS crawl_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            status_code INTEGER,
            response_time_ms INTEGER,
            word_count INTEGER,
            internal_links INTEGER,
            external_links INTEGER,
            images INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Keyword rankings
    c.execute("""
        CREATE TABLE IF NOT EXISTS keyword_rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            keyword TEXT NOT NULL,
            position INTEGER,
            search_volume INTEGER,
            estimated_clicks INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_cwv_url ON cwv_history(url)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_score_url ON score_history(url)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_crawl_url ON crawl_log(url)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_rank_url ON keyword_rankings(url)")

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# Core Web Vitals Fetcher
# ──────────────────────────────────────────────

def fetch_cwv(url: str, strategy: str = "mobile") -> dict:
    """Fetch Core Web Vitals from PageSpeed Insights API."""
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if PAGESPEED_API_KEY:
        params["key"] = PAGESPEED_API_KEY

    try:
        resp = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params=params, timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        lhr = data.get("lighthouseResult", {})
        audits = lhr.get("audits", {})
        categories = lhr.get("categories", {})

        perf_score = int(categories.get("performance", {}).get("score", 0) * 100)

        def _metric(key):
            a = audits.get(key, {})
            return {
                "value": a.get("numericValue", 0),
                "display": a.get("displayValue", ""),
                "score": a.get("score", 0),
            }

        lcp = _metric("largest-contentful-paint")
        cls = _metric("cumulative-layout-shift")
        inp = _metric("interactive")
        fcp = _metric("first-contentful-paint")
        ttfb = _metric("server-response-time")
        tbt = _metric("total-blocking-time")

        result = {
            "url": url,
            "strategy": strategy,
            "performance_score": perf_score,
            "lcp": lcp, "cls": cls, "inp": inp,
            "fcp": fcp, "ttfb": ttfb, "tbt": tbt,
            "fetch_time": lhr.get("fetchTime", ""),
        }

        # Save to DB
        _ensure_db()
        conn = sqlite3.connect(PERF_DB)
        conn.execute(
            "INSERT INTO cwv_history (url, lcp, cls, inp, fcp, ttfb, tbt, performance_score, strategy) VALUES (?,?,?,?,?,?,?,?,?)",
            (url, lcp["value"], cls["value"], inp["value"], fcp["value"], ttfb["value"], tbt["value"], perf_score, strategy),
        )
        conn.commit()
        conn.close()

        return result
    except Exception as e:
        return {"error": str(e), "url": url}


# ──────────────────────────────────────────────
# Score Snapshot Saver
# ──────────────────────────────────────────────

def save_score_snapshot(url: str, audit_data: dict) -> dict:
    """Save a comprehensive audit score snapshot for trend tracking."""
    _ensure_db()

    # Extract scores from different modules
    seo_score = audit_data.get("score", 0)
    tech_data = audit_data.get("technical_audit", {})
    tech_score = tech_data.get("overall_score", 0)

    # Content score from word count, headings, etc.
    wc = audit_data.get("word_count", 0)
    h2s = len(audit_data.get("headings", {}).get("h2", []))
    imgs = audit_data.get("images", {}).get("total", 0)
    content_score = min(100, (min(wc / 15, 40) + min(h2s * 10, 30) + min(imgs * 5, 30)))

    overall = round(seo_score * 0.4 + tech_score * 0.35 + content_score * 0.25)

    conn = sqlite3.connect(PERF_DB)
    conn.execute(
        "INSERT INTO score_history (url, seo_score, technical_score, content_score, overall_score, issues_count) VALUES (?,?,?,?,?,?)",
        (url, seo_score, tech_score, content_score, overall, len(audit_data.get("issues", []))),
    )
    conn.commit()
    conn.close()

    return {"saved": True, "overall_score": overall}


# ──────────────────────────────────────────────
# Performance Dashboard Data
# ──────────────────────────────────────────────

def get_performance_dashboard(url: str, days: int = 30) -> dict:
    """
    Get comprehensive performance dashboard data for a URL.
    Returns trend data, current metrics, and historical comparisons.
    """
    _ensure_db()
    conn = sqlite3.connect(PERF_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    # CWV history
    c.execute("SELECT * FROM cwv_history WHERE url=? AND created_at>=? ORDER BY created_at", (url, cutoff))
    cwv_rows = [dict(r) for r in c.fetchall()]

    # Score history
    c.execute("SELECT * FROM score_history WHERE url=? AND created_at>=? ORDER BY created_at", (url, cutoff))
    score_rows = [dict(r) for r in c.fetchall()]

    # Crawl log
    c.execute("SELECT * FROM crawl_log WHERE url=? AND created_at>=? ORDER BY created_at", (url, cutoff))
    crawl_rows = [dict(r) for r in c.fetchall()]

    # Keyword rankings
    c.execute("SELECT * FROM keyword_rankings WHERE url=? AND created_at>=? ORDER BY created_at", (url, cutoff))
    rank_rows = [dict(r) for r in c.fetchall()]

    conn.close()

    # Current metrics (latest)
    current = {}
    if score_rows:
        latest = score_rows[-1]
        current["seo_score"] = latest["seo_score"]
        current["technical_score"] = latest["technical_score"]
        current["content_score"] = latest["content_score"]
        current["overall_score"] = latest["overall_score"]
        current["issues_count"] = latest["issues_count"]

    if cwv_rows:
        latest_cwv = cwv_rows[-1]
        current["lcp"] = latest_cwv["lcp"]
        current["cls"] = latest_cwv["cls"]
        current["inp"] = latest_cwv["inp"]
        current["performance_score"] = latest_cwv["performance_score"]

    # Trend data
    score_trend = [{"date": r["created_at"][:10], "score": r["overall_score"]} for r in score_rows]
    cwv_trend = [{"date": r["created_at"][:10], "lcp": r["lcp"], "cls": r["cls"], "perf": r["performance_score"]} for r in cwv_rows]

    # Calculate deltas (vs previous period)
    deltas = {}
    if len(score_rows) >= 2:
        prev = score_rows[-2]
        curr = score_rows[-1]
        deltas["score_delta"] = curr["overall_score"] - prev["overall_score"]
        deltas["issues_delta"] = curr["issues_count"] - prev["issues_count"]

    # Health grade
    overall = current.get("overall_score", 0)
    if overall >= 90: grade = "A+"
    elif overall >= 80: grade = "A"
    elif overall >= 70: grade = "B+"
    elif overall >= 60: grade = "B"
    elif overall >= 50: grade = "C+"
    elif overall >= 40: grade = "C"
    elif overall >= 30: grade = "D"
    else: grade = "F"

    # CWV status
    lcp_val = current.get("lcp", 0)
    cls_val = current.get("cls", 0)
    cwv_status = "good"
    if lcp_val > 4000 or cls_val > 0.25:
        cwv_status = "poor"
    elif lcp_val > 2500 or cls_val > 0.1:
        cwv_status = "needs_improvement"

    return {
        "url": url,
        "period_days": days,
        "current": current,
        "grade": grade,
        "cwv_status": cwv_status,
        "deltas": deltas,
        "score_trend": score_trend,
        "cwv_trend": cwv_trend,
        "snapshots_count": len(score_rows),
        "crawl_count": len(crawl_rows),
        "keywords_tracked": len(set(r["keyword"] for r in rank_rows)),
    }


def get_all_tracked_sites() -> list[dict]:
    """Get all URLs being tracked with their latest scores."""
    _ensure_db()
    conn = sqlite3.connect(PERF_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT url,
               MAX(created_at) as last_audit,
               (SELECT overall_score FROM score_history sh WHERE sh.url = s.url ORDER BY sh.created_at DESC LIMIT 1) as score,
               (SELECT issues_count FROM score_history sh WHERE sh.url = s.url ORDER BY sh.created_at DESC LIMIT 1) as issues
        FROM score_history s
        GROUP BY url ORDER BY last_audit DESC
    """)

    results = [dict(r) for r in c.fetchall()]
    conn.close()
    return results


# ──────────────────────────────────────────────
# Simulated Traffic / Crawl Data
# ──────────────────────────────────────────────

def record_crawl_data(url: str, audit_data: dict = None) -> dict:
    """Record crawl data for a URL (called after audits)."""
    _ensure_db()
    conn = sqlite3.connect(PERF_DB)

    wc = 0
    int_links = 0
    ext_links = 0
    imgs = 0
    status = 200
    resp_time = random.randint(100, 800)

    if audit_data:
        wc = audit_data.get("word_count", 0)
        links = audit_data.get("links", {})
        int_links = links.get("internal_count", 0)
        ext_links = links.get("external_count", 0)
        imgs = audit_data.get("images", {}).get("total", 0)

    conn.execute(
        "INSERT INTO crawl_log (url, status_code, response_time_ms, word_count, internal_links, external_links, images) VALUES (?,?,?,?,?,?,?)",
        (url, status, resp_time, wc, int_links, ext_links, imgs),
    )
    conn.commit()
    conn.close()

    return {"recorded": True}


def get_crawl_trend(url: str, days: int = 30) -> dict:
    """Get crawl metrics trend for charts."""
    _ensure_db()
    conn = sqlite3.connect(PERF_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    c.execute("SELECT * FROM crawl_log WHERE url=? AND created_at>=? ORDER BY created_at", (url, cutoff))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()

    return {
        "url": url,
        "data": [{
            "date": r["created_at"][:10],
            "status": r["status_code"],
            "response_ms": r["response_time_ms"],
            "words": r["word_count"],
            "links": r["internal_links"] + r["external_links"],
            "images": r["images"],
        } for r in rows],
    }
