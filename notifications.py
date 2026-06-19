"""
SEO AI Tools - Notifications Module
Sends email and Slack webhook notifications for content calendar deadlines.
"""
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional

from config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM,
    SLACK_WEBHOOK_URL,
    NOTIFICATION_DAYS_BEFORE,
)


# ──────────────────────────────────────────────
# Email Notifications
# ──────────────────────────────────────────────


def send_email(subject: str, body: str, to_email: str) -> bool:
    """Send an email notification."""
    if not SMTP_HOST or not SMTP_USER:
        print("[notifications] SMTP not configured — skipping email")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM or SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))

        import ssl
        port = int(SMTP_PORT)
        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, port, context=context) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, port) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

        print(f"[notifications] Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"[notifications] Email failed: {e}")
        return False


def send_deadline_email(events: list[dict], to_email: str) -> int:
    """Send a digest email for upcoming deadlines. Returns count of emails sent."""
    if not events:
        return 0

    rows = ""
    for event in events:
        status_icon = {
            "planned": "📋", "in_progress": "🔨", "draft": "📝",
            "review": "👁️", "published": "✅", "paused": "⏸️"
        }.get(event.get("status", ""), "📋")
        type_badge = "🏛️" if event.get("type") == "pillar" else "📄"
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #eee;">{status_icon} {type_badge}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;font-weight:bold;">{event.get('title', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;">{event.get('keyword', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;color:#e74c3c;font-weight:bold;">{event.get('date', '')}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;">{event.get('status', '')}</td>
        </tr>"""

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto;">
        <h2 style="color:#2c3e50;">📅 Content Calendar — Upcoming Deadlines</h2>
        <p style="color:#666;">You have <strong>{len(events)}</strong> content piece(s) with approaching deadlines:</p>
        <table style="width:100%;border-collapse:collapse;">
            <tr style="background:#f8f9fa;">
                <th style="padding:8px;text-align:left;">Type</th>
                <th style="padding:8px;text-align:left;">Title</th>
                <th style="padding:8px;text-align:left;">Keyword</th>
                <th style="padding:8px;text-align:left;">Date</th>
                <th style="padding:8px;text-align:left;">Status</th>
            </tr>
            {rows}
        </table>
        <p style="color:#999;font-size:12px;margin-top:20px;">— Rankivo SEO AI Tools</p>
    </body>
    </html>"""

    subject = f"📅 Rankivo: {len(events)} Upcoming Deadline{'s' if len(events) > 1 else ''}"
    return 1 if send_email(subject, html, to_email) else 0


# ──────────────────────────────────────────────
# Slack Notifications
# ──────────────────────────────────────────────


def send_slack_message(text: str, blocks: list | None = None) -> bool:
    """Send a message to Slack via webhook."""
    import requests as req

    if not SLACK_WEBHOOK_URL:
        print("[notifications] Slack webhook not configured — skipping")
        return False

    payload = {"text": text}
    if blocks:
        payload["blocks"] = blocks

    try:
        resp = req.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        print("[notifications] Slack message sent")
        return True
    except Exception as e:
        print(f"[notifications] Slack failed: {e}")
        return False


def send_deadline_slack(events: list[dict]) -> bool:
    """Send a Slack notification for upcoming deadlines."""
    if not events:
        return False

    lines = ["📅 *Content Calendar — Upcoming Deadlines*\n"]
    for event in events:
        status_icon = {
            "planned": "📋", "in_progress": "🔨", "draft": "📝",
            "review": "👁️", "published": "✅", "paused": "⏸️"
        }.get(event.get("status", ""), "📋")
        type_badge = "🏛️" if event.get("type") == "pillar" else "📄"
        lines.append(
            f"{status_icon} {type_badge} *{event.get('title', '')}* "
            f"— keyword: `{event.get('keyword', '')}` | date: *{event.get('date', '')}*"
        )

    text = "\n".join(lines)
    return send_slack_message(text)


# ──────────────────────────────────────────────
# Deadline Checker
# ──────────────────────────────────────────────


def get_upcoming_deadlines(events: list[dict], days_ahead: int | None = None) -> list[dict]:
    """
    Find events with deadlines within the specified number of days.
    """
    if days_ahead is None:
        days_ahead = NOTIFICATION_DAYS_BEFORE

    today = datetime.now().date()
    deadline = today + timedelta(days=days_ahead)

    upcoming = []
    for event in events:
        if event.get("status") in ("published", "paused"):
            continue
        try:
            event_date = datetime.fromisoformat(event["date"]).date()
            if today <= event_date <= deadline:
                upcoming.append(event)
        except (ValueError, KeyError):
            continue

    upcoming.sort(key=lambda e: e.get("date", "9999"))
    return upcoming


def check_and_notify(events: list[dict], to_email: str = "") -> dict:
    """
    Check for upcoming deadlines and send notifications.
    Returns a summary of what was sent.
    """
    upcoming = get_upcoming_deadlines(events)

    result = {
        "upcoming_count": len(upcoming),
        "email_sent": False,
        "slack_sent": False,
        "upcoming_events": upcoming,
    }

    if upcoming:
        if to_email:
            result["email_sent"] = send_deadline_email(upcoming, to_email) > 0
        result["slack_sent"] = send_deadline_slack(upcoming)

    return result
