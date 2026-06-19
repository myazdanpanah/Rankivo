"""
SEO AI Tools - Keyword Tracker Module
Saves keyword research snapshots over time and provides trend analysis.
"""
import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRACKER_FILE = os.path.join(DATA_DIR, "keyword_history.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_history() -> dict:
    _ensure_data_dir()
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tracked_keywords": {}}


def _save_history(data: dict):
    _ensure_data_dir()
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def track_keyword(keyword: str, research_data: dict) -> dict:
    """
    Save a keyword research snapshot with a timestamp.
    Returns the updated tracking entry.
    """
    history = _load_history()

    if keyword not in history["tracked_keywords"]:
        history["tracked_keywords"][keyword] = {
            "keyword": keyword,
            "snapshots": [],
            "first_tracked": datetime.now().isoformat(),
        }

    # Count keywords for volume estimate
    all_kw = set()
    for key in ["suggestions", "modifier_expanded", "related_searches", "people_also_ask"]:
        all_kw.update(research_data.get(key, []))

    # Intent distribution
    intent_map = research_data.get("intent_map", {})
    intent_dist = {}
    for intent in intent_map.values():
        intent_dist[intent] = intent_dist.get(intent, 0) + 1

    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "total_keywords": len(all_kw),
        "suggestions_count": len(research_data.get("suggestions", [])),
        "paa_count": len(research_data.get("people_also_ask", [])),
        "related_count": len(research_data.get("related_searches", [])),
        "serp_count": len(research_data.get("serp_results", [])),
        "intent_distribution": intent_dist,
        "top_suggestions": research_data.get("suggestions", [])[:10],
        "top_paa": research_data.get("people_also_ask", [])[:5],
    }

    history["tracked_keywords"][keyword]["snapshots"].append(snapshot)
    _save_history(history)

    return history["tracked_keywords"][keyword]


def get_tracked_keywords() -> list[dict]:
    """Return all tracked keywords with their latest snapshot."""
    history = _load_history()
    tracked = []
    for kw, data in history.get("tracked_keywords", {}).items():
        snapshots = data.get("snapshots", [])
        latest = snapshots[-1] if snapshots else None
        tracked.append({
            "keyword": kw,
            "first_tracked": data.get("first_tracked", ""),
            "snapshot_count": len(snapshots),
            "latest_snapshot": latest,
        })
    tracked.sort(key=lambda x: x.get("snapshot_count", 0), reverse=True)
    return tracked


def get_keyword_history(keyword: str) -> dict | None:
    """Return full history for a specific keyword."""
    history = _load_history()
    return history.get("tracked_keywords", {}).get(keyword)


def delete_keyword(keyword: str) -> bool:
    """Remove a keyword from tracking."""
    history = _load_history()
    if keyword in history.get("tracked_keywords", {}):
        del history["tracked_keywords"][keyword]
        _save_history(history)
        return True
    return False


def get_trend_data(keyword: str) -> list[dict]:
    """
    Get trend data for a keyword: timestamps vs total_keywords over time.
    Suitable for plotting with Plotly.
    """
    kw_history = get_keyword_history(keyword)
    if not kw_history:
        return []

    trend = []
    for snap in kw_history.get("snapshots", []):
        trend.append({
            "date": snap["timestamp"][:10],
            "total_keywords": snap["total_keywords"],
            "suggestions": snap["suggestions_count"],
            "paa_questions": snap["paa_count"],
            "related": snap["related_count"],
        })
    return trend


def export_all_tracking() -> str:
    """Export all tracking data as JSON string."""
    history = _load_history()
    return json.dumps(history, indent=2, ensure_ascii=False)


def import_tracking(json_str: str) -> bool:
    """Import tracking data from JSON string."""
    try:
        data = json.loads(json_str)
        if "tracked_keywords" in data:
            _save_history(data)
            return True
    except (json.JSONDecodeError, KeyError):
        pass
    return False
