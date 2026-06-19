"""
Rankivo — Flask API Backend
Serves the Web UI and exposes all SEO modules as REST endpoints.
"""
import os
import io
import csv
import json
import hashlib
import time
import traceback
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

from keyword_research import run_keyword_research
from pillar_cluster import build_pillar_cluster_map
from content_generator import generate_article, get_available_providers
from seo_audit import audit_url
from batch_audit import parse_csv_urls, batch_audit, generate_comparison_table, generate_sample_csv
from content_calendar import (
    create_events_from_content_plan, get_calendar_stats,
    export_calendar_markdown, export_calendar_json, STATUS_COLORS,
)
from database import (
    db_track_keyword, db_get_tracked_keywords, db_get_keyword_history, db_delete_keyword,
    db_save_calendar_events, db_load_calendar_events, db_update_event_status, db_delete_event,
    db_save_audit, db_get_audit_history,
)
from seo_recommendations import analyze_audit_for_recommendations, generate_quick_wins
from notifications import send_email, send_slack_message, get_upcoming_deadlines, send_deadline_email, send_deadline_slack
from config import DEFAULT_AI_PROVIDER, DATABASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = SECRET_KEY
CORS(app)

# ──────────────────────────────────────────────
# Auth System
# ──────────────────────────────────────────────
_tokens = {}  # token -> {username, created_at}

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token or token not in _tokens:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# In-memory session store for keyword research results (per simple token)
_session_store = {}


def _get_session():
    """Simple session management via X-Session-ID header."""
    sid = request.headers.get("X-Session-ID", "default")
    if sid not in _session_store:
        _session_store[sid] = {}
    return _session_store[sid]


# ──────────────────────────────────────────────
# Auth Endpoints
# ──────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if username == ADMIN_USERNAME and _hash_password(password) == _hash_password(ADMIN_PASSWORD):
        token = hashlib.sha256(f"{username}{time.time()}{SECRET_KEY}".encode()).hexdigest()
        _tokens[token] = {"username": username, "created_at": time.time()}
        return jsonify({"success": True, "token": token, "username": username})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    _tokens.pop(token, None)
    return jsonify({"success": True})


@app.route("/api/auth/check")
def api_auth_check():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token and token in _tokens:
        return jsonify({"authenticated": True, "username": _tokens[token]["username"]})
    return jsonify({"authenticated": False})


# ──────────────────────────────────────────────
# Static Files
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return send_file("static/index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


# ──────────────────────────────────────────────
# Config & Status
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/status")
def api_status():
    providers = get_available_providers()
    return jsonify({
        "database": "PostgreSQL" if DATABASE_URL else "SQLite",
        "providers": providers,
        "default_provider": DEFAULT_AI_PROVIDER,
    })


# ──────────────────────────────────────────────
# 1. Keyword Research
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/keyword-research", methods=["POST"])
def api_keyword_research():
    try:
        data = request.json
        seed = data.get("seed", "").strip()
        depth = data.get("depth", 1)
        expand = data.get("expand_modifiers", True)

        if not seed:
            return jsonify({"error": "Seed keyword is required"}), 400

        result = run_keyword_research(seed, depth=depth, expand_with_modifiers=expand)
        session = _get_session()
        session["keyword_data"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/keyword-research", methods=["GET"])
def api_get_keyword_data():
    session = _get_session()
    kw_data = session.get("keyword_data")
    if not kw_data:
        return jsonify({"error": "No keyword data in session. Run research first."}), 404
    return jsonify(kw_data)


# ──────────────────────────────────────────────
# 2. Pillar-Cluster
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/pillar-cluster", methods=["POST"])
def api_pillar_cluster():
    try:
        session = _get_session()
        kw_data = session.get("keyword_data")
        if not kw_data:
            return jsonify({"error": "Run keyword research first"}), 400

        data = request.json or {}
        threshold = data.get("threshold", 0.30)

        result = build_pillar_cluster_map(kw_data, cluster_threshold=threshold)
        session["cluster_map"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/pillar-cluster", methods=["GET"])
def api_get_cluster_map():
    session = _get_session()
    cm = session.get("cluster_map")
    if not cm:
        return jsonify({"error": "No cluster map. Build one first."}), 404
    return jsonify(cm)


# ──────────────────────────────────────────────
# 3. Article Generation
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/article/generate", methods=["POST"])
def api_generate_article():
    try:
        data = request.json
        topic = data.get("topic", "").strip()
        keywords = data.get("keywords", [])
        provider = data.get("provider", DEFAULT_AI_PROVIDER)
        word_count = data.get("word_count", 1500)
        tone = data.get("tone", "informative, authoritative")
        style = data.get("style", "blog post")

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        if not keywords:
            keywords = [topic]

        session = _get_session()
        kw_data = session.get("keyword_data", {})

        article = generate_article(
            topic=topic,
            target_keywords=keywords,
            provider=provider,
            people_also_ask=kw_data.get("people_also_ask"),
            serp_context=kw_data.get("serp_results"),
            word_count=word_count,
            tone=tone,
            style=style,
        )

        return jsonify({"article": article, "topic": topic})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/article/providers")
def api_providers():
    return jsonify({"providers": get_available_providers(), "default": DEFAULT_AI_PROVIDER})


# ──────────────────────────────────────────────
# 4. SEO Audit
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/audit", methods=["POST"])
def api_audit():
    try:
        data = request.json
        url = data.get("url", "").strip()
        keyword = data.get("keyword", "").strip()

        if not url:
            return jsonify({"error": "URL is required"}), 400

        result = audit_url(url, keyword)

        if not result.get("error"):
            db_save_audit(result)
            session = _get_session()
            session["audit_result"] = result

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# 5. Batch Audit
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/batch-audit", methods=["POST"])
def api_batch_audit():
    try:
        data = request.json
        csv_content = data.get("csv", "")
        max_workers = data.get("max_workers", 2)
        delay = data.get("delay", 1.5)

        if not csv_content:
            return jsonify({"error": "CSV content is required"}), 400

        entries = parse_csv_urls(csv_content)
        if not entries:
            return jsonify({"error": "No valid URLs found in CSV"}), 400

        results = batch_audit(entries, max_workers=max_workers, delay=delay)
        comparison = generate_comparison_table(results)

        return jsonify({"results": results, "comparison": comparison, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/batch-audit/sample-csv")
def api_sample_csv():
    return jsonify({"csv": generate_sample_csv()})


# ──────────────────────────────────────────────
# 6. Keyword Tracking
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/tracking", methods=["GET"])
def api_get_tracked():
    return jsonify({"tracked": db_get_tracked_keywords()})


@require_auth
@app.route("/api/tracking", methods=["POST"])
def api_track_keyword():
    try:
        session = _get_session()
        kw_data = session.get("keyword_data")
        if not kw_data:
            return jsonify({"error": "Run keyword research first"}), 400

        all_kw = set()
        for k in ["suggestions", "modifier_expanded", "related_searches", "people_also_ask"]:
            all_kw.update(kw_data.get(k, []))

        snapshot = {
            "total_keywords": len(all_kw),
            "suggestions_count": len(kw_data.get("suggestions", [])),
            "paa_count": len(kw_data.get("people_also_ask", [])),
            "related_count": len(kw_data.get("related_searches", [])),
        }

        db_track_keyword(kw_data.get("seed", ""), snapshot)
        return jsonify({"success": True, "keyword": kw_data.get("seed", "")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/tracking/<keyword>", methods=["DELETE"])
def api_delete_tracked(keyword):
    db_delete_keyword(keyword)
    return jsonify({"success": True})


@require_auth
@app.route("/api/tracking/<keyword>/history")
def api_keyword_history(keyword):
    history = db_get_keyword_history(keyword)
    return jsonify({"history": history})


# ──────────────────────────────────────────────
# 7. Content Calendar
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/calendar", methods=["GET"])
def api_get_calendar():
    events = db_load_calendar_events()
    stats = get_calendar_stats(events) if events else {}
    return jsonify({"events": events, "stats": stats})


@require_auth
@app.route("/api/calendar", methods=["POST"])
def api_generate_calendar():
    try:
        session = _get_session()
        cm = session.get("cluster_map")
        if not cm:
            return jsonify({"error": "Build pillar-cluster map first"}), 400

        events = create_events_from_content_plan(cm["content_plan"])
        db_save_calendar_events(events)
        return jsonify({"events": events, "count": len(events)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/calendar/<event_id>", methods=["PATCH"])
def api_update_event(event_id):
    try:
        data = request.json
        new_status = data.get("status", "")
        color = STATUS_COLORS.get(new_status, "#6c757d")
        db_update_event_status(event_id, new_status, color)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/calendar/<event_id>", methods=["DELETE"])
def api_delete_event(event_id):
    db_delete_event(event_id)
    return jsonify({"success": True})


@require_auth
@app.route("/api/calendar/export/<fmt>")
def api_export_calendar(fmt):
    events = db_load_calendar_events()
    if fmt == "markdown":
        return jsonify({"content": export_calendar_markdown(events)})
    elif fmt == "json":
        return jsonify({"content": export_calendar_json(events)})
    return jsonify({"error": "Invalid format"}), 400


# ──────────────────────────────────────────────
# 8. AI Recommendations
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/recommendations", methods=["POST"])
def api_recommendations():
    try:
        session = _get_session()
        audit_data = session.get("audit_result")
        if not audit_data:
            return jsonify({"error": "Run an SEO audit first"}), 400

        data = request.json or {}
        provider = data.get("provider", DEFAULT_AI_PROVIDER)

        recs = analyze_audit_for_recommendations(audit_data, provider=provider)
        return jsonify({"recommendations": recs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/recommendations/quick-wins")
def api_quick_wins():
    session = _get_session()
    audit_data = session.get("audit_result")
    if not audit_data:
        return jsonify({"error": "Run an SEO audit first"}), 400

    wins = generate_quick_wins(audit_data)
    return jsonify({"quick_wins": wins})


# ──────────────────────────────────────────────
# 9. Audit History
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/audit-history")
def api_audit_history():
    limit = request.args.get("limit", 50, type=int)
    history = db_get_audit_history(limit=limit)
    return jsonify({"history": history})


# ──────────────────────────────────────────────
# 10. PDF Export (Audit Report)
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/audit/export-pdf", methods=["POST"])
def api_export_audit_pdf():
    try:
        data = request.json or {}
        audit_data = data.get("audit_result")
        if not audit_data:
            session = _get_session()
            audit_data = session.get("audit_result")
        if not audit_data:
            return jsonify({"error": "No audit data to export"}), 400

        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle('Title2', parent=styles['Title'], fontSize=20, spaceAfter=6)
        heading_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=14, spaceAfter=8, spaceBefore=16, textColor=colors.HexColor('#4f46e5'))
        body_style = ParagraphStyle('Body2', parent=styles['BodyText'], fontSize=10, leading=14)
        small_style = ParagraphStyle('Small', parent=styles['BodyText'], fontSize=9, textColor=colors.grey)

        score = audit_data.get('score', 0)
        score_color = '#10b981' if score >= 80 else '#f59e0b' if score >= 50 else '#ef4444'
        score_label = 'Excellent' if score >= 80 else 'Good' if score >= 50 else 'Needs Work'

        elements.append(Paragraph('Rankivo — SEO Audit Report', title_style))
        elements.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0')))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(f'URL: {audit_data.get("final_url", audit_data.get("url", ""))}', body_style))
        elements.append(Paragraph(f'Score: {score}/100 ({score_label})', body_style))
        elements.append(Spacer(1, 12))

        # Meta Info
        elements.append(Paragraph('Page Information', heading_style))
        meta_data = [
            ['Title', audit_data.get('page_title', 'MISSING') or 'MISSING'],
            ['Meta Description', (audit_data.get('meta_description', '') or 'MISSING')[:120]],
            ['Canonical', audit_data.get('canonical', '') or 'MISSING'],
            ['Word Count', str(audit_data.get('word_count', 0))],
            ['Text/HTML Ratio', f"{audit_data.get('text_to_html_ratio', 0)}%"],
        ]
        t = Table(meta_data, colWidths=[120, 380])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        # Links & Images
        links = audit_data.get('links', {})
        images = audit_data.get('images', {})
        elements.append(Paragraph('Links & Images', heading_style))
        li_data = [
            ['Internal Links', str(links.get('internal_count', 0))],
            ['External Links', str(links.get('external_count', 0))],
            ['Nofollow Links', str(links.get('nofollow_count', 0))],
            ['Total Images', str(images.get('total', 0))],
            ['Images with Alt', str(images.get('with_alt', 0))],
            ['Alt Coverage', f"{images.get('alt_coverage', 0)}%"],
        ]
        t2 = Table(li_data, colWidths=[140, 140])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 12))

        # Issues
        issues = audit_data.get('issues', [])
        if issues:
            elements.append(Paragraph(f'Issues ({len(issues)})', heading_style))
            for issue in issues:
                severity = issue.get('severity', 'info')
                icon = 'CRITICAL' if severity == 'critical' else 'WARNING' if severity == 'warning' else 'INFO'
                elements.append(Paragraph(
                    f"<b>[{icon}]</b> [{issue.get('category', '').upper()}] {issue.get('message', '')}",
                    body_style
                ))
                elements.append(Spacer(1, 4))

        # Headings
        headings = audit_data.get('headings', {})
        h1s = headings.get('h1', [])
        if h1s:
            elements.append(Paragraph('H1 Tags', heading_style))
            for h in h1s:
                elements.append(Paragraph(h, body_style))

        doc.build(elements)
        buf.seek(0)

        url_slug = (audit_data.get('final_url', audit_data.get('url', 'audit'))).replace('https://', '').replace('http://', '').replace('/', '_')[:50]
        return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=f'seo-audit-{url_slug}.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# 11. CSV Export (Keyword Research)
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/keyword-research/export-csv", methods=["POST"])
def api_export_keywords_csv():
    try:
        data = request.json or {}
        kw_data = data.get("keyword_data")
        if not kw_data:
            session = _get_session()
            kw_data = session.get("keyword_data")
        if not kw_data:
            return jsonify({"error": "No keyword data to export"}), 400

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(['Keyword', 'Source', 'Intent'])

        intent_map = kw_data.get('intent_map', {})
        for kw in kw_data.get('suggestions', []):
            writer.writerow([kw, 'Autocomplete', intent_map.get(kw, '')])
        for kw in kw_data.get('modifier_expanded', []):
            writer.writerow([kw, 'Modifier Expanded', intent_map.get(kw, '')])
        for kw in kw_data.get('related_searches', []):
            writer.writerow([kw, 'Related Search', intent_map.get(kw, '')])
        for kw in kw_data.get('people_also_ask', []):
            writer.writerow([kw, 'People Also Ask', intent_map.get(kw, '')])

        output = io.BytesIO()
        output.write(buf.getvalue().encode('utf-8-sig'))
        output.seek(0)

        seed = kw_data.get('seed', 'keywords').replace(' ', '_')
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f'keywords-{seed}.csv')
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# 12. Notifications
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/notifications/test-email", methods=["POST"])
def api_test_email():
    try:
        data = request.json
        email = data.get("email", "")
        if not email:
            return jsonify({"error": "Email is required"}), 400

        ok = send_email(
            "Rankivo Test",
            "<h2>✅ Notifications are working!</h2><p>This is a test from Rankivo SEO Tools.</p>",
            email,
        )
        return jsonify({"success": ok})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/notifications/deadlines", methods=["POST"])
def api_notify_deadlines():
    try:
        data = request.json or {}
        days = data.get("days", 3)
        email = data.get("email", "")

        events = db_load_calendar_events()
        upcoming = get_upcoming_deadlines(events, days)

        result = {"upcoming": upcoming, "email_sent": False, "slack_sent": False}
        if upcoming:
            if email:
                result["email_sent"] = send_deadline_email(upcoming, email) > 0
            result["slack_sent"] = send_deadline_slack(upcoming)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🚀 Rankivo Web UI starting at http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
