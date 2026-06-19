"""
SEO AI Tools - Content Calendar Module
Generates an editorial calendar from pillar-cluster content plans.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CALENDAR_FILE = os.path.join(DATA_DIR, "content_calendar.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_calendar() -> dict:
    _ensure_data_dir()
    if os.path.exists(CALENDAR_FILE):
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"events": []}


def _save_calendar(data: dict):
    _ensure_data_dir()
    with open(CALENDAR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# Status colors for display
STATUS_COLORS = {
    "planned": "#6c757d",
    "in_progress": "#ffc107",
    "draft": "#17a2b8",
    "review": "#fd7e14",
    "published": "#28a745",
    "paused": "#dc3545",
}


def create_events_from_content_plan(
    content_plan: list[dict],
    start_date: str | None = None,
    pillar_interval_days: int = 7,
    cluster_interval_days: int = 3,
    status: str = "planned",
) -> list[dict]:
    """
    Generate calendar events from a pillar-cluster content plan.
    Each pillar page gets a date, and its cluster articles are spaced after it.
    """
    if start_date:
        current_date = datetime.fromisoformat(start_date)
    else:
        current_date = datetime.now()

    events = []

    for plan in content_plan:
        # Pillar page event
        pillar_event = {
            "id": f"pillar_{plan['cluster_id']}",
            "title": plan["pillar_title"],
            "type": "pillar",
            "keyword": plan["pillar_keyword"],
            "intent": plan["pillar_intent"],
            "date": current_date.isoformat()[:10],
            "cluster_id": plan["cluster_id"],
            "status": status,
            "color": "#6f42c1" if status == "planned" else STATUS_COLORS.get(status, "#6c757d"),
        }
        events.append(pillar_event)

        # Cluster article events
        cluster_date = current_date + timedelta(days=pillar_interval_days)
        for i, article in enumerate(plan.get("articles", [])):
            cluster_event = {
                "id": f"cluster_{plan['cluster_id']}_{i}",
                "title": article["suggested_title"],
                "type": "cluster",
                "keyword": article["keyword"],
                "intent": article["intent"],
                "date": cluster_date.isoformat()[:10],
                "cluster_id": plan["cluster_id"],
                "status": status,
                "color": "#17a2b8" if status == "planned" else STATUS_COLORS.get(status, "#6c757d"),
            }
            events.append(cluster_event)
            cluster_date += timedelta(days=cluster_interval_days)

        # Move to next pillar after all its clusters
        current_date = cluster_date + timedelta(days=2)

    return events


def save_calendar_events(events: list[dict]):
    """Save calendar events to disk."""
    data = _load_calendar()
    data["events"] = events
    _save_calendar(data)


def load_calendar_events() -> list[dict]:
    """Load calendar events from disk."""
    data = _load_calendar()
    return data.get("events", [])


def update_event_status(event_id: str, new_status: str) -> bool:
    """Update the status of a specific event."""
    data = _load_calendar()
    for event in data.get("events", []):
        if event["id"] == event_id:
            event["status"] = new_status
            event["color"] = STATUS_COLORS.get(new_status, "#6c757d")
            _save_calendar(data)
            return True
    return False


def delete_event(event_id: str) -> bool:
    """Remove an event from the calendar."""
    data = _load_calendar()
    original_len = len(data.get("events", []))
    data["events"] = [e for e in data.get("events", []) if e["id"] != event_id]
    if len(data["events"]) < original_len:
        _save_calendar(data)
        return True
    return False


def get_calendar_stats(events: list[dict]) -> dict:
    """Compute summary statistics for the calendar."""
    if not events:
        return {"total": 0, "by_status": {}, "by_type": {}, "date_range": ""}

    by_status = {}
    by_type = {}
    dates = []
    for e in events:
        status = e.get("status", "planned")
        by_status[status] = by_status.get(status, 0) + 1

        etype = e.get("type", "cluster")
        by_type[etype] = by_type.get(etype, 0) + 1

        if e.get("date"):
            dates.append(e["date"])

    date_range = ""
    if dates:
        dates.sort()
        date_range = f"{dates[0]} → {dates[-1]}"

    return {
        "total": len(events),
        "by_status": by_status,
        "by_type": by_type,
        "date_range": date_range,
    }


def export_calendar_markdown(events: list[dict]) -> str:
    """Export calendar as a Markdown document."""
    lines = ["# Content Calendar\n"]
    lines.append(f"**Total Content Pieces:** {len(events)}\n")

    # Group by month
    events_sorted = sorted(events, key=lambda e: e.get("date", "9999"))
    current_month = ""
    for event in events_sorted:
        month = event.get("date", "")[:7]
        if month != current_month:
            current_month = month
            lines.append(f"\n## {month}\n")

        status_icon = {
            "planned": "📋", "in_progress": "🔨", "draft": "📝",
            "review": "👁️", "published": "✅", "paused": "⏸️"
        }.get(event.get("status", ""), "📋")

        type_badge = "🏛️" if event.get("type") == "pillar" else "📄"
        lines.append(
            f"- {status_icon} {type_badge} **{event.get('date', '')}** — "
            f"{event.get('title', 'Untitled')} "
            f"*(keyword: {event.get('keyword', 'N/A')}, status: {event.get('status', 'planned')})*"
        )

    return "\n".join(lines)


def export_calendar_json(events: list[dict]) -> str:
    """Export calendar as JSON."""
    return json.dumps(events, indent=2, ensure_ascii=False)
