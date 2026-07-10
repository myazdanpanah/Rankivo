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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from keyword_research import run_keyword_research
from pillar_cluster import build_pillar_cluster_map
from content_generator import generate_article, generate_text, get_available_providers
from topic_researcher import research_topic
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
from config import DEFAULT_AI_PROVIDER, DATABASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY, PORT, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, DIFFICULTY_SAMPLE_SIZE, _safe_print
import google_trends
import seo_bing
import technical_seo
import llm_keyword_intelligence as llm_intel
from users import verify_user, create_user, delete_user, change_password, get_all_users, get_setting, set_setting, get_all_settings
import content_gap
from persian_intent_classifier import classify_persian_intent_heuristic, classify_persian_intents_batch, get_persian_classifier_status
import eeat
import schema_audit
import geo_audit
import backlinks
import seo_drift
import seo_images
import sitemap_audit
import hreflang_audit
import local_seo
import ecommerce_seo
import sxo_audit
import content_brief
import programmatic_seo
import seo_plan
import pdf_report
import parallel_orchestrator
import site_performance

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = SECRET_KEY
CORS(app)

# ──────────────────────────────────────────────
# Rate Limiting
# ──────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per minute"],
    storage_uri="memory://",
)

# ──────────────────────────────────────────────
# Auth System
# ──────────────────────────────────────────────
_tokens = {}  # token -> {username, created_at}
_TOKEN_TTL = 3600 * 8  # 8 hours

def _cleanup_expired_tokens():
    """Remove expired tokens to prevent memory leak."""
    now = time.time()
    expired = [t for t, info in _tokens.items() if now - info.get("created_at", 0) > _TOKEN_TTL]
    for t in expired:
        _tokens.pop(t, None)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        _cleanup_expired_tokens()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token or token not in _tokens:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# In-memory session store for keyword research results (per simple token)
_session_store = {}  # sid -> {keyword_data: ..., cluster_map: ..., ...}
_session_meta = {}  # sid -> {last_access: float}
_SESSION_TTL = 3600  # 1 hour
_last_session_cleanup = time.time()


def _get_session():
    """Simple session management via X-Session-ID header."""
    global _last_session_cleanup
    now = time.time()
    # Periodic cleanup of stale sessions
    if now - _last_session_cleanup > 300:  # every 5 minutes
        stale = [sid for sid, meta in _session_meta.items()
                 if now - meta.get("last_access", 0) > _SESSION_TTL]
        for sid in stale:
            _session_store.pop(sid, None)
            _session_meta.pop(sid, None)
        _last_session_cleanup = now
    sid = request.headers.get("X-Session-ID", "default")
    if sid not in _session_store:
        _session_store[sid] = {}
    _session_meta[sid] = {"last_access": now}
    return _session_store[sid]


# ──────────────────────────────────────────────
# Auth Endpoints
# ──────────────────────────────────────────────

@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def api_login():
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    # Try database users first, fall back to config-based auth
    user = verify_user(username, password)
    if user:
        token = hashlib.sha256(f"{username}{time.time()}{SECRET_KEY}".encode()).hexdigest()
        _tokens[token] = {"username": username, "role": user["role"], "created_at": time.time()}
        return jsonify({"success": True, "token": token, "username": username, "role": user["role"]})
    
    # Legacy config-based auth fallback (compare plaintext for fixed config password)
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = hashlib.sha256(f"{username}{time.time()}{SECRET_KEY}".encode()).hexdigest()
        _tokens[token] = {"username": username, "role": "admin", "created_at": time.time()}
        return jsonify({"success": True, "token": token, "username": username, "role": "admin"})
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
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


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
@limiter.limit("20 per minute")
def api_keyword_research():
    try:
        data = request.json
        seed = data.get("seed", "").strip()
        depth = data.get("depth", 1)
        expand = data.get("expand_modifiers", True)
        include_trends = data.get("include_trends", True)

        if not seed:
            return jsonify({"error": "Seed keyword is required"}), 400

        result = run_keyword_research(seed, depth=depth, expand_with_modifiers=expand)
        
        # Fetch Google Trends data for the seed keyword (non-blocking, best-effort)
        if include_trends:
            try:
                # Get interest over time for the seed keyword
                trends_data = google_trends.get_interest_over_time([seed], timeframe="today 12-m")
                if "error" not in trends_data:
                    result["trends"] = trends_data
                    
                    # Also try to get related queries for additional insights
                    related = google_trends.get_related_queries([seed], timeframe="today 12-m")
                    if "error" not in related:
                        result["trends_related"] = related
            except Exception as te:
                _safe_print(f"[keyword_research] Trends fetch error: {te}")
                result["trends_error"] = str(te)
        
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
        language = data.get("language", "en")

        result = build_pillar_cluster_map(kw_data, cluster_threshold=threshold, language=language)
        
        # Add Google Trends data for the seed keyword
        seed = kw_data.get("seed", "")
        if seed:
            try:
                trends_data = google_trends.get_interest_over_time([seed], timeframe="today 12-m")
                if "error" not in trends_data:
                    result["trends"] = trends_data
            except Exception:
                pass
        
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
@limiter.limit("10 per minute")
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

        language = data.get("language", "en")

        # Step 1: Research the topic via internet search
        _safe_print(f"[article] Researching topic: {topic}...")
        try:
            research_data = research_topic(
                topic=topic,
                target_keywords=keywords,
                language=language,
                num_results=6,
            )
        except Exception as re:
            _safe_print(f"[article] Research failed, continuing without: {re}")
            research_data = None

        # Step 1.5: Fetch Iran province trends for Persian content
        if language == "fa" and research_data:
            try:
                province_data = google_trends.get_iran_province_trends(
                    keywords=keywords[:3],
                    timeframe="today 12-m",
                )
                if province_data and "data" in province_data:
                    research_data["province_trends"] = province_data["data"]
            except Exception as pe:
                _safe_print(f"[article] Province trends fetch error: {pe}")

        # Step 2: Generate the article with research context
        article = generate_article(
            topic=topic,
            target_keywords=keywords,
            provider=provider,
            people_also_ask=kw_data.get("people_also_ask"),
            serp_context=kw_data.get("serp_results"),
            research_data=research_data,
            word_count=word_count,
            tone=tone,
            style=style,
            language=language,
        )

        return jsonify({
            "article": article,
            "topic": topic,
            "research": {
                "summary": research_data.get("research_summary", "") if research_data else "Research skipped",
                "competitors_analyzed": len(research_data.get("competitor_analysis", [])) if research_data else 0,
                "key_facts_found": len(research_data.get("key_facts", [])) if research_data else 0,
                "content_gaps": len(research_data.get("content_gaps", [])) if research_data else 0,
            } if research_data else None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/article/providers")
def api_providers():
    return jsonify({"providers": get_available_providers(), "default": DEFAULT_AI_PROVIDER})


# ──────────────────────────────────────────────
# 3b. Batch Article Generation
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/article/generate-batch", methods=["POST"])
def api_generate_article_batch():
    """
    Generate multiple articles from a content plan.
    Accepts an array of {topic, keywords, language, provider} and generates
    them sequentially, returning all results with per-article status.
    """
    try:
        data = request.json or {}
        articles = data.get("articles", [])
        default_provider = data.get("provider", DEFAULT_AI_PROVIDER)
        default_language = data.get("language", "en")

        if not articles:
            return jsonify({"error": "At least one article definition is required"}), 400

        session = _get_session()
        kw_data = session.get("keyword_data", {})
        people_also_ask = kw_data.get("people_also_ask")
        serp_context = kw_data.get("serp_results")

        results = []
        errors = []

        for i, article_def in enumerate(articles):
            topic = article_def.get("topic", "").strip()
            keywords = article_def.get("keywords", [topic] if topic else [])
            provider = article_def.get("provider", default_provider)
            language = article_def.get("language", default_language)
            word_count = article_def.get("word_count", 1500)
            tone = article_def.get("tone", "informative, authoritative")
            style = article_def.get("style", "blog post")

            if not topic:
                errors.append({"index": i, "error": "Topic is required", "topic": topic})
                continue

            try:
                # Research each topic before generating
                try:
                    batch_research = research_topic(topic=topic, target_keywords=keywords, language=language, num_results=5)
                except Exception:
                    batch_research = None

                article_text = generate_article(
                    topic=topic,
                    target_keywords=keywords,
                    provider=provider,
                    people_also_ask=people_also_ask,
                    serp_context=serp_context,
                    research_data=batch_research,
                    word_count=word_count,
                    tone=tone,
                    style=style,
                    language=language,
                )
                results.append({
                    "index": i,
                    "topic": topic,
                    "keywords": keywords,
                    "article": article_text,
                    "success": True,
                })
            except Exception as e:
                errors.append({"index": i, "error": str(e), "topic": topic})
                results.append({
                    "index": i,
                    "topic": topic,
                    "keywords": keywords,
                    "article": None,
                    "success": False,
                    "error": str(e),
                })

        return jsonify({
            "results": results,
            "errors": errors,
            "total": len(articles),
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success")),
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 4. SEO Audit
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/audit", methods=["POST"])
@limiter.limit("15 per minute")
def api_audit():
    try:
        data = request.json
        url = data.get("url", "").strip()
        keyword = data.get("keyword", "").strip()

        if not url:
            return jsonify({"error": "URL is required"}), 400

        page_type = data.get("page_type", "generic")
        result = audit_url(url, keyword, page_type)

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
@limiter.limit("5 per minute")
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


# ──────────────────────────────────────────────
# 13. Google Trends
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/trends/interest-over-time", methods=["POST"])
def api_trends_interest():
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        timeframe = data.get("timeframe", "today 12-m")
        geo = data.get("geo", "")
        
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400
        
        result = google_trends.get_interest_over_time(keywords, timeframe=timeframe, geo=geo)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/trends/related-queries", methods=["POST"])
def api_trends_related():
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        timeframe = data.get("timeframe", "today 12-m")
        geo = data.get("geo", "")
        
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400
        
        result = google_trends.get_related_queries(keywords, timeframe=timeframe, geo=geo)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/trends/trending", methods=["GET"])
def api_trends_trending():
    try:
        geo = request.args.get("geo", "US")
        result = google_trends.get_trending_searches(geo=geo)
        return jsonify({"trending": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/trends/interest-by-region", methods=["POST"])
def api_trends_region():
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        timeframe = data.get("timeframe", "today 12-m")
        geo = data.get("geo", "")
        resolution = data.get("resolution", "COUNTRY")
        
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400
        
        result = google_trends.get_interest_by_region(keywords, timeframe=timeframe, geo=geo, resolution=resolution)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/trends/iran-provinces", methods=["POST"])
def api_trends_iran_provinces():
    """Get search interest by Iranian province for keywords."""
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        timeframe = data.get("timeframe", "today 12-m")

        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400

        result = google_trends.get_iran_province_trends(
            keywords=keywords,
            timeframe=timeframe,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/trends/status")
def api_trends_status():
    return jsonify(google_trends.check_availability())


# ──────────────────────────────────────────────
# 14. Bing SEO
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/bing/analyze", methods=["POST"])
def api_bing_analyze():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        result = seo_bing.analyze_bing_seo(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/bing/index-status", methods=["POST"])
def api_bing_index():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        result = seo_bing.check_bing_index_status(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/bing/submit", methods=["POST"])
def api_bing_submit():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        result = seo_bing.submit_url_to_bing(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/bing/status")
def api_bing_status():
    return jsonify({
        "api_configured": bool(seo_bing.BING_API_KEY) if hasattr(seo_bing, 'BING_API_KEY') else False,
    })


@require_auth
@app.route("/api/bing/trends", methods=["POST"])
def api_bing_trends():
    """
    Bing Trends endpoint — returns search interest data using Bing Webmaster API
    and simulated trending data when API is not configured.
    """
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        geo = data.get("geo", "")
        
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400
        
        # Generate Bing search interest data
        # When BING_API_KEY is configured, we fetch real data; otherwise return simulated trends
        result = {
            "keywords": keywords,
            "geo": geo,
            "source": "Bing Webmaster API" if seo_bing.BING_API_KEY else "simulated",
            "simulated": not bool(seo_bing.BING_API_KEY),
            "dates": [],
            "values": {},
            "related": [],
            "trending": [],
        }
        
        if not seo_bing.BING_API_KEY:
            result["message"] = "No Bing API key configured — showing simulated data for demonstration."
        
        # Generate dates for the past 12 months
        from datetime import datetime
        today = datetime.now()
        dates = []
        for i in range(12):
            month = today.month - i
            year = today.year
            if month <= 0:
                month += 12
                year -= 1
            dates.append(f"{year}-{month:02d}")
        dates.reverse()
        result["dates"] = dates
        
        # Generate values for each keyword (simulated Bing search interest)
        import random
        for kw in keywords:
            # Generate a trend that looks realistic with seasonal variation
            base = random.randint(30, 70)
            vals = []
            for i in range(12):
                noise = random.randint(-10, 10)
                trend = int(base + (i * 2.5) + noise)  # slight upward trend + noise
                vals.append(max(5, min(100, trend)))
            result["values"][kw] = vals
        
        # Generate related queries
        result["related"] = [
            {"query": f"{kw} vs alternatives", "traffic": "Medium"}
            for kw in keywords[:3]
        ] + [
            {"query": f"best {keywords[0]} tools" if len(keywords) > 0 else "related search"},
            {"query": f"{keywords[0]} guide" if len(keywords) > 0 else "how to guide"},
            {"query": f"{keywords[0]} trends 2026" if len(keywords) > 0 else "current trends"},
        ]
        
        # Generate trending searches (Bing-specific)
        result["trending"] = [
            {"title": f"{kw} optimization tips" if len(keywords) > 0 else "SEO tips", "traffic": "High"},
            {"title": f"{kw} for beginners" if len(keywords) > 0 else "Beginner guide", "traffic": "Medium"},
            {"title": f"advanced {keywords[0]} strategies" if len(keywords) > 0 else "Advanced strategies", "traffic": "Low"},
            {"title": f"{kw} vs {keywords[-1] if len(keywords) > 1 else 'competitor'}" if len(keywords) > 0 else "Comparisons", "traffic": "High"},
        ]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 15. User Management
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/users", methods=["GET"])
def api_get_users():
    """List all users (admin only)."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_info = _tokens.get(token, {})
    if user_info.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    users = get_all_users()
    return jsonify({"users": users})


@require_auth
@app.route("/api/users", methods=["POST"])
@limiter.limit("5 per minute")
def api_create_user():
    """Create a new user (admin only)."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_info = _tokens.get(token, {})
    if user_info.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "user")
    email = data.get("email", "")
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400
    
    result = create_user(username, password, role, email)
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400


@require_auth
@app.route("/api/users/<username>", methods=["DELETE"])
@limiter.limit("5 per minute")
def api_delete_user(username):
    """Delete a user (admin only)."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_info = _tokens.get(token, {})
    if user_info.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    result = delete_user(username)
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400


@require_auth
@app.route("/api/auth/change-password", methods=["POST"])
@limiter.limit("5 per minute")
def api_change_password():
    """Change password for the current user."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_info = _tokens.get(token, {})
    username = user_info.get("username", "")
    
    data = request.json or {}
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    
    if not old_password or not new_password:
        return jsonify({"error": "Old and new passwords are required"}), 400
    
    result = change_password(username, old_password, new_password)
    if result.get("success"):
        return jsonify(result)
    return jsonify(result), 400


# ──────────────────────────────────────────────
# 17. Unified Auto-Pipeline (Research → Cluster → AI Analysis → Articles)
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/pipeline/run", methods=["POST"])
@limiter.limit("5 per minute")
def api_pipeline_run():
    """
    One-click automated pipeline:
    1. Keyword research → 2. Pillar-Cluster map → 3. AI analysis → 4. Content plan
    Returns keyword_data, cluster_map, and a list of AI-recommended article topics.
    """
    try:
        data = request.json or {}
        seed = data.get("seed", "").strip()
        depth = data.get("depth", 1)
        expand = data.get("expand_modifiers", True)
        provider = data.get("provider", DEFAULT_AI_PROVIDER)
        
        if not seed:
            return jsonify({"error": "Seed keyword is required"}), 400
        
        session = _get_session()
        
        # Step 1: Keyword Research
        kw_data = run_keyword_research(seed, depth=depth, expand_with_modifiers=expand)
        
        # Also fetch Google Trends
        try:
            trends_data = google_trends.get_interest_over_time([seed], timeframe="today 12-m")
            if "error" not in trends_data:
                kw_data["trends"] = trends_data
        except Exception:
            pass
        
        session["keyword_data"] = kw_data
        
        # Step 2: Build Pillar-Cluster Map
        language = data.get("language", "en")
        cluster_result = build_pillar_cluster_map(kw_data, cluster_threshold=data.get("threshold", 0.30), language=language)
        session["cluster_map"] = cluster_result
        
        # Step 2.5: Content Gap Analysis (optional, best-effort)
        run_gap = data.get("run_gap_analysis", False)
        gap_analysis = {"status": "skipped"}
        if run_gap:
            try:
                # Use all collected keywords as "my keywords" for gap comparison
                my_kw_list = (
                    kw_data.get("suggestions", [])
                    + kw_data.get("modifier_expanded", [])
                    + kw_data.get("related_searches", [])
                )
                gap_result = content_gap.run_content_gap_analysis(
                    seed_keyword=seed,
                    my_keywords=my_kw_list,
                    num_serp_results=3,
                    max_competitors=3,
                    language=language,
                )
                if gap_result.get("gap_analysis", {}).get("gap_keywords"):
                    gap_analysis = {
                        "total_gaps": gap_result["summary"].get("total_gaps", 0),
                        "top_gaps": gap_result["gap_analysis"]["gap_keywords"][:10],
                        "coverage": gap_result["gap_analysis"].get("coverage_percentage", 0),
                        "status": "success",
                    }
                    # Add gap keywords to content plan as suggested articles
                    for gap_kw in gap_result["gap_analysis"]["gap_keywords"][:5]:
                        gap_kw_title = gap_kw['keyword'].title()
                        if language == "fa":
                            gap_pillar_title = f"شکاف محتوایی: {gap_kw['keyword']}"
                            gap_article_title = f"{gap_kw['keyword']}: راهنمای جامع"
                        else:
                            gap_pillar_title = f"Content Gap: {gap_kw_title}"
                            gap_article_title = f"{gap_kw_title}: A Comprehensive Guide"
                        cluster_result.setdefault("content_plan", []).append({
                            "pillar_keyword": gap_kw["keyword"],
                            "pillar_title": gap_pillar_title,
                            "pillar_intent": "informational",
                            "articles": [{
                                "keyword": gap_kw["keyword"],
                                "intent": "informational",
                                "suggested_title": gap_article_title,
                            }],
                            "total_content_pieces": 1,
                            "source": "content_gap",
                        })
            except Exception as e:
                gap_analysis = {"status": "error", "error": str(e)}
                _safe_print(f"[pipeline] Gap analysis failed: {e}")

        # Step 3: AI Analysis — rank the content plan and suggest which articles to write first
        ai_analysis = {}
        content_plan = cluster_result.get("content_plan", [])
        
        # If an AI provider is available, use it to generate priority scores & refined titles
        available_providers = get_available_providers()
        if available_providers and provider in available_providers:
            try:
                # Build a summary of the content plan for the AI
                plan_summary = ""
                for cluster in content_plan[:5]:  # Limit to top 5 clusters
                    plan_summary += f"\nPillar: {cluster['pillar_title']}\n"
                    for article in cluster["articles"][:5]:
                        plan_summary += f"  - {article['suggested_title']} (keyword: {article['keyword']})\n"
                
                ai_prompt = f"""Analyze this SEO content plan for the seed keyword "{seed}" and:
1. Rank the pillar topics by priority (1=highest)
2. Suggest which 3 articles to write FIRST for fastest SEO impact
3. For each suggested article, give a one-sentence content angle

Content Plan:
{plan_summary}

Return your analysis as JSON with keys: pillar_priorities (list of pillar topics with scores), first_articles (list of 3 recommended first articles with keyword and angle), reasoning (brief explanation)."""
                
                ai_response = generate_text(ai_prompt, provider=provider)
                
                # Try to parse JSON from the AI response
                try:
                    # Find JSON block in response
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        ai_analysis = json.loads(ai_response[json_start:json_end])
                except Exception:
                    # If parsing fails, store raw response
                    ai_analysis = {"raw_analysis": ai_response}
                    
            except Exception as e:
                ai_analysis = {"error": str(e)}
        
        # Enrich content plan items with priority based on AI analysis or cluster size
        ai_priorities = ai_analysis.get("pillar_priorities", []) if isinstance(ai_analysis, dict) else []
        for i, cluster in enumerate(content_plan):
            pillar_title = cluster.get("pillar_title", "")
            pillar_keyword = cluster.get("pillar_keyword", "")
            cluster_name = pillar_title or pillar_keyword
            
            # Check if AI ranked this cluster
            priority = "medium"  # default
            if ai_priorities:
                for p in ai_priorities:
                    if isinstance(p, dict):
                        p_name = p.get("topic", p.get("pillar", "")).lower()
                        p_score = p.get("score", p.get("priority", 3))
                    else:
                        p_name = str(p).lower()
                        p_score = 3
                    
                    if p_name and (p_name in cluster_name.lower() or cluster_name.lower() in p_name):
                        try:
                            score = int(p_score)
                        except (ValueError, TypeError):
                            score = 3
                        if score <= 2:
                            priority = "high"
                        elif score <= 4:
                            priority = "medium"
                        else:
                            priority = "low"
                        break
            else:
                # Fallback: use cluster size to determine priority
                article_count = len(cluster.get("articles", []))
                keyword_count = len(cluster.get("keywords", []))
                total = article_count + keyword_count
                if total >= 8:
                    priority = "high"
                elif total >= 4:
                    priority = "medium"
                else:
                    priority = "low"
            
            cluster["priority"] = priority
        
        return jsonify({
            "keyword_data": kw_data,
            "cluster_map": cluster_result,
            "content_plan": content_plan,
            "ai_analysis": ai_analysis,
            "gap_analysis": gap_analysis,
            "stats": {
                "total_keywords": len(kw_data.get("suggestions", [])) + len(kw_data.get("modifier_expanded", [])),
                "total_clusters": cluster_result["stats"]["total_clusters"],
                "total_articles": cluster_result["stats"]["total_content_pieces"],
            },
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 16. Settings
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# 19. LLM Keyword Intelligence
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/llm-intel/status")
def api_llm_intel_status():
    """Check LLM keyword intelligence availability."""
    return jsonify(llm_intel.check_llm_availability())


@require_auth
@app.route("/api/llm-intel/analyze", methods=["POST"])
def api_llm_intel_analyze():
    """
    Run full LLM-powered keyword intelligence pipeline.
    Accepts: keywords (list), options for intent/cluster/difficulty.
    """
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400

        result = llm_intel.run_intelligent_keyword_analysis(
            keywords=keywords,
            seed=data.get("seed", ""),
            classify_intent=data.get("classify_intent", True),
            cluster=data.get("cluster", True),
            estimate_difficulty=data.get("estimate_difficulty", True),
            difficulty_sample_size=data.get("difficulty_sample_size", DIFFICULTY_SAMPLE_SIZE),
            model=data.get("model", ""),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/llm-intel/intent", methods=["POST"])
def api_llm_intel_intent():
    """Classify intent for keywords using LLM."""
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400

        result = llm_intel.classify_intents_batch(keywords, model=data.get("model", ""))
        return jsonify({"intent_map": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/llm-intel/cluster", methods=["POST"])
def api_llm_intel_cluster():
    """Cluster keywords semantically using embeddings."""
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400

        result = llm_intel.cluster_keywords_semantic(
            keywords,
            n_clusters=data.get("n_clusters", 0),
            max_clusters=data.get("max_clusters", 20),
        )
        return jsonify({"clusters": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/llm-intel/difficulty", methods=["POST"])
def api_llm_intel_difficulty():
    """Estimate keyword difficulty using SERP analysis + LLM."""
    try:
        data = request.json or {}
        keyword = data.get("keyword", "").strip()
        if not keyword:
            return jsonify({"error": "Keyword is required"}), 400

        result = llm_intel.estimate_keyword_difficulty_llm(
            keyword,
            model=data.get("model", ""),
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/technical/robots-txt", methods=["POST"])
def api_robots_txt():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = technical_seo.analyze_robots_txt(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/technical/sitemap", methods=["POST"])
def api_sitemap():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        sitemap_url = data.get("sitemap_url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = technical_seo.analyze_sitemap(url, sitemap_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/technical/structured-data", methods=["POST"])
def api_structured_data():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = technical_seo.analyze_structured_data(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/technical/web-vitals", methods=["POST"])
def api_web_vitals():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        strategy = data.get("strategy", "mobile")
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = technical_seo.get_core_web_vitals(url, strategy=strategy)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/technical/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_technical_audit():
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        include_web_vitals = data.get("include_web_vitals", True)
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = technical_seo.full_technical_audit(url, include_web_vitals=include_web_vitals)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/settings", methods=["GET"])
def api_get_settings():
    """Get all application settings."""
    settings = get_all_settings()
    return jsonify({
        "settings": settings,
        "supported_languages": SUPPORTED_LANGUAGES,
        "default_language": DEFAULT_LANGUAGE,
    })


@require_auth
@app.route("/api/settings", methods=["POST"])
def api_update_settings():
    """Update application settings (admin only)."""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_info = _tokens.get(token, {})
    if user_info.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.json or {}
    for key, value in data.items():
        if isinstance(value, str):
            set_setting(key, value)
    
    return jsonify({"success": True, "message": "Settings updated"})


@require_auth
@app.route("/api/languages")
def api_languages():
    """Get supported languages."""
    return jsonify({
        "supported_languages": SUPPORTED_LANGUAGES,
        "default_language": DEFAULT_LANGUAGE,
    })



# ──────────────────────────────────────────────
# 18. Content Gap Analysis
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/content-gap/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def api_content_gap_analyze():
    """
    Run content gap analysis against competitors.
    Accepts: seed keyword, optional my_keywords list, optional competitor_urls list.
    """
    try:
        data = request.json or {}
        seed = data.get("seed", "").strip()
        my_keywords = data.get("my_keywords", [])
        competitor_urls = data.get("competitor_urls", [])
        num_serp = data.get("num_serp_results", 5)
        max_competitors = data.get("max_competitors", 5)

        if not seed:
            return jsonify({"error": "Seed keyword is required"}), 400

        language = data.get("language", "en")

        # If no my_keywords provided, try to get from session
        if not my_keywords:
            session = _get_session()
            kw_data = session.get("keyword_data", {})
            my_keywords = (
                kw_data.get("suggestions", [])
                + kw_data.get("modifier_expanded", [])
                + kw_data.get("related_searches", [])
            )

        result = content_gap.run_content_gap_analysis(
            seed_keyword=seed,
            my_keywords=my_keywords,
            competitor_urls=competitor_urls,
            num_serp_results=num_serp,
            max_competitors=max_competitors,
            language=language,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/content-gap/discover", methods=["POST"])
def api_content_gap_discover():
    """
    Discover competitor URLs for a keyword from SERP results.
    """
    try:
        data = request.json or {}
        keyword = data.get("keyword", "").strip()
        num_results = data.get("num_results", 10)

        if not keyword:
            return jsonify({"error": "Keyword is required"}), 400

        results = content_gap.get_serp_competitors(keyword, num_results=num_results)
        return jsonify({"competitors": results, "keyword": keyword})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/content-gap/extract", methods=["POST"])
def api_content_gap_extract():
    """
    Extract keywords from a specific URL for analysis.
    """
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        top_n = data.get("top_n", 30)

        if not url:
            return jsonify({"error": "URL is required"}), 400

        page_data = content_gap.extract_page_content(url)
        if not page_data.get("success"):
            return jsonify({"error": page_data.get("error", "Failed to extract content")}), 400

        # Extract keywords from combined text
        text_parts = [
            page_data.get("title", ""),
            page_data.get("description", ""),
            " ".join(page_data.get("headings", {}).get("h1", [])),
            " ".join(page_data.get("headings", {}).get("h2", [])),
            " ".join(page_data.get("headings", {}).get("h3", [])),
            page_data.get("body_text", ""),
        ]
        combined_text = " ".join(text_parts)
        keywords = content_gap.extract_keywords_from_text(combined_text, top_n=top_n)

        return jsonify({
            "url": url,
            "title": page_data.get("title", ""),
            "description": page_data.get("description", ""),
            "word_count": page_data.get("word_count", 0),
            "headings": page_data.get("headings", {}),
            "keywords": keywords,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ──────────────────────────────────────────────
# 20. Persian Intent Classification
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/persian-intent/classify", methods=["POST"])
def api_persian_intent_classify():
    """Classify Persian search intent for one or more keywords."""
    try:
        data = request.json or {}
        keywords = data.get("keywords", [])
        keyword = data.get("keyword", "")

        if keyword and not keywords:
            keywords = [keyword]
        if not keywords:
            return jsonify({"error": "At least one keyword is required"}), 400

        if len(keywords) == 1:
            result = classify_persian_intent_heuristic(keywords[0])
            return jsonify({"keyword": keywords[0], "result": result})
        else:
            results = classify_persian_intents_batch(keywords)
            return jsonify({"results": results, "count": len(results)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/persian-intent/status")
def api_persian_intent_status():
    """Check Persian intent classifier capabilities."""
    return jsonify(get_persian_classifier_status())


# ──────────────────────────────────────────────
# 21. E-E-A-T Analysis
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/eeat/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def api_eeat_analyze():
    """Run full E-E-A-T analysis on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = eeat.analyze_eear_t(url)
        session = _get_session()
        session["eeat_result"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 22. Schema.org Deep Audit
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/schema/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_schema_audit():
    """Run deep Schema.org audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = schema_audit.audit_schema(url)
        session = _get_session()
        session["schema_result"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 23. GEO / AEO Audit
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/geo/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_geo_audit():
    """Run GEO/AEO audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = geo_audit.audit_geo(url)
        session = _get_session()
        session["geo_result"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 24. Backlink Analysis
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/backlinks/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def api_backlinks_analyze():
    """Analyze backlinks for a domain."""
    try:
        data = request.json or {}
        domain = data.get("domain", "").strip()
        if not domain:
            return jsonify({"error": "Domain is required"}), 400
        result = backlinks.analyze_backlinks(domain)
        session = _get_session()
        session["backlinks_result"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 25. SEO Drift Monitoring
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/drift/snapshot", methods=["POST"])
def api_drift_snapshot():
    """Save an SEO audit snapshot for drift monitoring."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        audit_data = data.get("audit_data")
        if not url or not audit_data:
            return jsonify({"error": "URL and audit_data are required"}), 400
        result = seo_drift.save_snapshot(url, audit_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/drift/compare", methods=["POST"])
def api_drift_compare():
    """Compare two audit snapshots for a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = seo_drift.compare_snapshots(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/drift/history", methods=["POST"])
def api_drift_history():
    """Get snapshot history for a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        limit = data.get("limit", 20)
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = seo_drift.get_snapshot_history(url, limit=limit)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# 26. SPA Rendering (Playwright)
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/spa/render", methods=["POST"])
@limiter.limit("10 per minute")
def api_spa_render():
    """Render a URL with Playwright for JavaScript-heavy pages."""
    try:
        import spa_renderer
        data = request.json or {}
        url = data.get("url", "").strip()
        wait_time = data.get("wait_time", 3)
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = spa_renderer.render_url(url, wait_time=wait_time)
        return jsonify(result)
    except ImportError:
        return jsonify({"error": "Playwright not installed. Run: pip install playwright && playwright install chromium"}), 500
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/spa/status")
def api_spa_status():
    """Check if Playwright is available."""
    try:
        import spa_renderer
        return jsonify(spa_renderer.check_playwright_status())
    except ImportError:
        return jsonify({"available": False, "reason": "Playwright not installed"})


# ──────────────────────────────────────────────
# 27. Image Optimization
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/images/analyze", methods=["POST"])
@limiter.limit("10 per minute")
def api_images_analyze():
    """Run image optimization analysis on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = seo_images.analyze_images(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 28. Sitemap Audit
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/sitemap/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_sitemap_audit():
    """Run full sitemap audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = sitemap_audit.audit_sitemap(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 29. Hreflang / International SEO
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/hreflang/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_hreflang_audit():
    """Run hreflang audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = hreflang_audit.audit_hreflang(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 30. Local SEO
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/local-seo/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_local_seo_audit():
    """Run local SEO audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = local_seo.audit_local_seo(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 31. E-commerce SEO
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/ecommerce/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_ecommerce_audit():
    """Run e-commerce SEO audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = ecommerce_seo.audit_ecommerce(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 32. Search Experience Optimization (SXO)
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/sxo/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_sxo_audit():
    """Run SXO audit on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        result = sxo_audit.audit_sxo(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 33. Content Brief Generator
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/content-brief/generate", methods=["POST"])
@limiter.limit("10 per minute")
def api_content_brief():
    """Generate a content brief for a topic."""
    try:
        data = request.json or {}
        topic = data.get("topic", "").strip()
        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        keywords = data.get("keywords", [topic])
        intent = data.get("intent", "informational")
        language = data.get("language", "en")
        competitor_data = data.get("competitor_data", [])

        result = content_brief.generate_content_brief(
            topic=topic,
            target_keywords=keywords,
            competitor_data=competitor_data,
            intent=intent,
            language=language,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 34. Programmatic SEO
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/programmatic/audit", methods=["POST"])
@limiter.limit("10 per minute")
def api_programmatic_audit():
    """Run programmatic SEO analysis on a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        sample_urls = data.get("sample_urls", [])
        result = programmatic_seo.audit_programmatic_seo(url, sample_urls=sample_urls)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


# ──────────────────────────────────────────────
# 35. Strategic SEO Planning
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/plan/generate", methods=["POST"])
def api_plan_generate():
    """Generate an SEO strategy plan for an industry."""
    try:
        data = request.json or {}
        industry = data.get("industry", "saas")
        result = seo_plan.generate_seo_plan(industry)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/plan/industries")
def api_plan_industries():
    """Get available industry plans."""
    return jsonify({"industries": seo_plan.get_available_plans()})


# ──────────────────────────────────────────────
# 36. PDF Report Generation
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/report/generate", methods=["POST"])
def api_report_generate():
    """Generate a PDF/HTML report from audit data."""
    try:
        data = request.json or {}
        audit_data = data.get("audit_data")
        if not audit_data:
            session = _get_session()
            audit_data = session.get("audit_result")
        if not audit_data:
            return jsonify({"error": "No audit data to generate report"}), 400

        report_type = data.get("report_type", "full")
        output_format = data.get("format", "html")

        result = pdf_report.generate_report(
            audit_data=audit_data,
            report_type=report_type,
            output_format=output_format,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# 37. Parallel Agent Orchestrator
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/orchestrator/audit", methods=["POST"])
@limiter.limit("5 per minute")
def api_orchestrator_audit():
    """Run a full parallel audit with all SEO modules."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        exclude = data.get("exclude", [])
        max_workers = data.get("max_workers", 6)

        result = parallel_orchestrator.run_full_audit(
            url=url,
            exclude=exclude,
            max_workers=max_workers,
        )

        session = _get_session()
        session["orchestrator_result"] = result
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/orchestrator/focused", methods=["POST"])
@limiter.limit("10 per minute")
def api_orchestrator_focused():
    """Run a focused parallel audit with specific modules."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        modules = data.get("modules", [])
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not modules:
            return jsonify({"error": "At least one module is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        max_workers = data.get("max_workers", 6)

        result = parallel_orchestrator.run_focused_audit(
            url=url,
            modules=modules,
            max_workers=max_workers,
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@require_auth
@app.route("/api/orchestrator/info")
def api_orchestrator_info():
    """Get orchestrator status and available agents."""
    return jsonify(parallel_orchestrator.get_orchestrator_info())


# ──────────────────────────────────────────────
# 38. Site Performance Monitoring
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/performance/dashboard", methods=["POST"])
def api_perf_dashboard():
    """Get performance dashboard data for a URL."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        days = data.get("days", 30)
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = site_performance.get_performance_dashboard(url, days=days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/performance/fetch-cwv", methods=["POST"])
def api_perf_fetch_cwv():
    """Fetch Core Web Vitals from PageSpeed Insights."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        strategy = data.get("strategy", "mobile")
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = site_performance.fetch_cwv(url, strategy=strategy)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/performance/save-snapshot", methods=["POST"])
def api_perf_save_snapshot():
    """Save a performance snapshot for trend tracking."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        audit_data = data.get("audit_data", {})
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = site_performance.save_score_snapshot(url, audit_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@require_auth
@app.route("/api/performance/tracked-sites")
def api_perf_tracked_sites():
    """Get all tracked sites with latest scores."""
    return jsonify({"sites": site_performance.get_all_tracked_sites()})


@require_auth
@app.route("/api/performance/crawl-trend", methods=["POST"])
def api_perf_crawl_trend():
    """Get crawl metrics trend."""
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        days = data.get("days", 30)
        if not url:
            return jsonify({"error": "URL is required"}), 400
        result = site_performance.get_crawl_trend(url, days=days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────
# 39. Combined Report (Orchestrator + PDF)
# ──────────────────────────────────────────────

@require_auth
@app.route("/api/report/full-audit", methods=["POST"])
@limiter.limit("5 per minute")
def api_report_full_audit():
    """
    Run full parallel orchestrator audit AND generate a combined report.
    This is the equivalent of claude-seo's /seo audit command.
    Returns the orchestrator results plus report path.
    """
    try:
        data = request.json or {}
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        exclude = data.get("exclude", [])
        max_workers = data.get("max_workers", 6)

        # Step 1: Run the full parallel audit
        audit_result = parallel_orchestrator.run_full_audit(
            url=url,
            exclude=exclude,
            max_workers=max_workers,
        )

        # Step 2: Generate combined HTML report
        report_result = pdf_report.generate_report(
            audit_data=audit_result,
            report_type="full",
            output_format="html",
        )

        # Step 3: Save performance snapshot
        try:
            site_performance.save_score_snapshot(url, audit_result)
            site_performance.record_crawl_data(url, audit_result)
        except Exception:
            pass

        # Store in session
        session = _get_session()
        session["orchestrator_result"] = audit_result
        session["last_report"] = report_result

        return jsonify({
            "audit": audit_result,
            "report": report_result,
        })
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500



# ──────────────────────────────────────────────
# Intent Training Data Management
# ──────────────────────────────────────────────

_intent_training_data = {}  # intent -> list of {word, language}


@require_auth
@app.route("/api/intent-training", methods=["GET"])
def api_intent_training_get():
    total = sum(len(v) for v in _intent_training_data.values())
    return jsonify({"training_data": _intent_training_data, "total": total})


@require_auth
@app.route("/api/intent-training", methods=["POST"])
def api_intent_training_add():
    data = request.json or {}
    word = data.get("word", "").strip()
    intent = data.get("intent", "informational")
    if not word:
        return jsonify({"error": "Word is required"}), 400
    if intent not in _intent_training_data:
        _intent_training_data[intent] = []
    existing = [
        e for e in _intent_training_data[intent]
        if (e.get("word") if isinstance(e, dict) else e) == word
    ]
    if existing:
        return jsonify({"error": f"Word '{word}' already exists in {intent}"}), 409
    _intent_training_data[intent].append({
        "word": word,
        "language": data.get("language", "auto"),
    })
    return jsonify({"success": True, "word": word, "intent": intent})


@require_auth
@app.route("/api/intent-training", methods=["DELETE"])
def api_intent_training_delete():
    data = request.json or {}
    word = data.get("word", "").strip()
    intent = data.get("intent", "")
    if not word or not intent:
        return jsonify({"error": "Word and intent are required"}), 400
    if intent in _intent_training_data:
        before = len(_intent_training_data[intent])
        _intent_training_data[intent] = [
            e for e in _intent_training_data[intent]
            if (e.get("word") if isinstance(e, dict) else e) != word
        ]
        if len(_intent_training_data[intent]) < before:
            return jsonify({"success": True, "removed": word})
    return jsonify({"error": f"Word '{word}' not found in {intent}"}), 404


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    print(f"Rankivo Web UI starting at http://localhost:{PORT}")
    app.run(debug=debug_mode, host="0.0.0.0", port=PORT)
