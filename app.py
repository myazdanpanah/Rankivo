"""
Rankivo - SEO AI Tools Dashboard
Web-based SEO tool with keyword research, pillar-cluster mapping, AI article generation,
SEO audit, batch audit, keyword tracking, content calendar, AI recommendations, and notifications.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

from keyword_research import run_keyword_research
from pillar_cluster import build_pillar_cluster_map
from content_generator import generate_article, get_available_providers
from seo_audit import audit_url
from batch_audit import parse_csv_urls, batch_audit, generate_comparison_table, generate_comparison_markdown, generate_sample_csv
from keyword_tracker import track_keyword
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
from notifications import check_and_notify, get_upcoming_deadlines, send_email, send_slack_message
from config import DEFAULT_AI_PROVIDER, DATABASE_URL

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Rankivo - SEO AI Tools",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px 8px 0 0; }
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px; border-radius: 12px; color: white;
    }
    div[data-testid="stMetric"] label { color: #e0e0e0 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

with st.sidebar:
    st.title("🔍 Rankivo")
    st.caption("SEO AI Tools — All-in-One")
    if DATABASE_URL:
        st.success("🐘 PostgreSQL connected")
    else:
        st.info("📦 Using SQLite (local)")
    st.divider()

    st.subheader("🤖 AI Provider")
    @st.cache_data(ttl=60)
    def _cached_providers():
        return get_available_providers()
    available_providers = _cached_providers()
    if available_providers:
        selected_provider = st.selectbox("Choose AI backend", available_providers,
            index=available_providers.index(DEFAULT_AI_PROVIDER) if DEFAULT_AI_PROVIDER in available_providers else 0)
        st.success(f"✅ {selected_provider.upper()} ready")
    else:
        selected_provider = "ollama"
        st.warning("⚠️ No AI providers detected.")

    st.divider()
    st.subheader("📝 Article Settings")
    article_word_count = st.slider("Target word count", 500, 5000, 1500, step=100)
    article_tone = st.selectbox("Tone", ["informative, authoritative", "casual, friendly", "professional, technical", "persuasive, marketing", "educational, beginner-friendly"])
    article_style = st.selectbox("Style", ["blog post", "guide", "tutorial", "listicle", "case study"])

    st.divider()
    st.subheader("🔔 Notifications")
    notify_email = st.text_input("Email for deadline alerts", placeholder="you@example.com")
    notify_days = st.slider("Days before deadline", 1, 14, 3)
    if st.button("📤 Test Notification"):
        if notify_email:
            ok = send_email("Rankivo Test", "<h2>✅ Notifications are working!</h2><p>This is a test from Rankivo SEO Tools.</p>", notify_email)
            st.success("✅ Test email sent!") if ok else st.error("❌ Failed to send")
        else:
            st.warning("Enter an email first.")

    st.divider()
    st.caption("Built with Streamlit · PostgreSQL · Ollama/OpenAI/Claude/Gemini")

# ──────────────────────────────────────────────
# Tabs
# ──────────────────────────────────────────────

st.title("🔍 Rankivo — SEO AI Tools")
st.markdown("Research keywords → Build clusters → Generate articles → Audit → Track → Schedule")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊 Keyword Research", "🗺️ Pillar-Cluster", "✍️ Articles",
    "🔍 SEO Audit", "📋 Batch Audit", "📈 Tracking",
    "📅 Calendar", "🧠 AI Recommendations", "📜 Audit History",
])

# ══════════════════════════════════════════════
# Tab 1: Keyword Research
# ══════════════════════════════════════════════

with tab1:
    st.header("📊 Keyword Research")
    col1, col2 = st.columns([3, 1])
    with col1:
        seed_keyword = st.text_input("Enter seed keyword", placeholder="e.g. python web development", key="seed_kw")
    with col2:
        research_depth = st.slider("Depth", 1, 3, 1)
        expand_modifiers = st.checkbox("Expand modifiers", value=True)

    if st.button("🚀 Start Research", type="primary", key="btn_research"):
        if not seed_keyword.strip():
            st.error("Enter a keyword.")
        else:
            cache_key = f"{seed_keyword.strip().lower()}_{research_depth}_{expand_modifiers}"
            if cache_key in st.session_state.get("kw_cache", {}):
                st.session_state["keyword_data"] = st.session_state["kw_cache"][cache_key]
            else:
                with st.spinner("Fetching..."):
                    kw_data = run_keyword_research(seed_keyword.strip(), depth=research_depth, expand_with_modifiers=expand_modifiers)
                    st.session_state.setdefault("kw_cache", {})[cache_key] = kw_data
                    st.session_state["keyword_data"] = kw_data

    kw_data = st.session_state.get("keyword_data")
    if kw_data:
        st.divider()
        all_kw = set()
        for k in ["suggestions", "modifier_expanded", "related_searches", "people_also_ask"]:
            all_kw.update(kw_data.get(k, []))
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Keywords", len(all_kw))
        m2.metric("Autocomplete", len(kw_data.get("suggestions", [])))
        m3.metric("PAA", len(kw_data.get("people_also_ask", [])))
        m4.metric("Related", len(kw_data.get("related_searches", [])))

        if kw_data.get("intent_map"):
            intent_counts = {}
            for intent in kw_data["intent_map"].values():
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            fig = px.pie(names=list(intent_counts.keys()), values=list(intent_counts.values()), hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════
# Tab 2: Pillar-Cluster
# ══════════════════════════════════════════════

with tab2:
    st.header("🗺️ Pillar-Cluster Map")
    kw_data_c = st.session_state.get("keyword_data")
    if not kw_data_c:
        st.info("👈 Run keyword research first.")
    else:
        threshold = st.slider("Similarity threshold", 0.15, 0.60, 0.30, 0.05)
        if st.button("🗺️ Build Map", type="primary", key="btn_cluster"):
            with st.spinner("Building clusters..."):
                st.session_state["cluster_map"] = build_pillar_cluster_map(kw_data_c, threshold)

        cm = st.session_state.get("cluster_map")
        if cm:
            stats = cm["stats"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Clusters", stats["total_clusters"])
            c2.metric("Keywords", stats["total_keywords"])
            c3.metric("Content Pieces", stats["total_content_pieces"])

            if cm["pillar_clusters"]:
                sizes = [{"Cluster": f"#{pc['cluster_id']}: {pc['pillar_keyword'][:25]}", "Keywords": pc["size"]} for pc in cm["pillar_clusters"]]
                fig = px.bar(pd.DataFrame(sizes), x="Keywords", y="Cluster", orientation="h", color="Keywords", color_continuous_scale="Viridis")
                st.plotly_chart(fig, use_container_width=True)

            for pc in cm["content_plan"]:
                with st.expander(f"🏛️ {pc['pillar_title']} ({pc['total_content_pieces']} articles)"):
                    st.json(pc["articles"])

# ══════════════════════════════════════════════
# Tab 3: Articles
# ══════════════════════════════════════════════

with tab3:
    st.header("✍️ Article Generator")
    if not available_providers:
        st.warning("No AI provider detected.")
    else:
        col_topic, col_kw = st.columns([1, 1])
        with col_topic:
            article_topic = st.text_input("Topic", placeholder="How to use Python for SEO", key="article_topic")
        with col_kw:
            article_keywords = st.text_area("Keywords (one per line)", key="article_kw", height=80)

        if st.button("✍️ Generate", type="primary", key="btn_gen"):
            if article_topic.strip():
                kw_list = [k.strip() for k in article_keywords.strip().split("\n") if k.strip()] or [article_topic.strip()]
                with st.spinner(f"Generating with {selected_provider.upper()}..."):
                    try:
                        md = generate_article(topic=article_topic.strip(), target_keywords=kw_list, provider=selected_provider, word_count=article_word_count, tone=article_tone, style=article_style)
                        st.session_state["generated_article"] = md
                        st.session_state["article_topic"] = article_topic.strip()
                    except Exception as e:
                        st.error(f"Failed: {e}")
            else:
                st.error("Enter a topic.")

        article = st.session_state.get("generated_article")
        if article:
            st.divider()
            topic = st.session_state.get("article_topic", "Article")
            st.markdown(article)
            st.download_button("📥 Download MD", article, f"{topic.lower().replace(' ','_')}.md", "text/markdown")

# ══════════════════════════════════════════════
# Tab 4: SEO Audit
# ══════════════════════════════════════════════

with tab4:
    st.header("🔍 SEO Audit")
    col_url, col_kw = st.columns([3, 1])
    with col_url:
        audit_url_input = st.text_input("URL to audit", placeholder="https://example.com", key="audit_url")
    with col_kw:
        audit_keyword = st.text_input("Focus keyword", key="audit_kw")

    if st.button("🔍 Audit", type="primary", key="btn_audit"):
        if audit_url_input.strip():
            with st.spinner("Auditing..."):
                result = audit_url(audit_url_input.strip(), audit_keyword.strip())
                st.session_state["audit_result"] = result
                if not result.get("error"):
                    db_save_audit(result)
        else:
            st.error("Enter a URL.")

    audit = st.session_state.get("audit_result")
    if audit and not audit.get("error"):
        st.divider()
        score = audit["score"]
        sc = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(f"{sc} Score", f"{score}/100")
        m2.metric("Words", audit["word_count"])
        m3.metric("Internal Links", audit["links"]["internal_count"])
        m4.metric("Images", audit["images"]["total"])

        if audit["issues"]:
            st.subheader("⚠️ Issues")
            for issue in audit["issues"]:
                icon = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "warning" else "ℹ️"
                st.markdown(f"{icon} **[{issue['category'].upper()}]** {issue['message']}")

        st.subheader("🏷️ Meta")
        st.markdown(f"**Title:** `{audit['page_title'] or 'MISSING'}` ({len(audit['page_title'])} chars)")
        st.markdown(f"**Description:** `{audit['meta_description'] or 'MISSING'}` ({len(audit['meta_description'])} chars)")

# ══════════════════════════════════════════════
# Tab 5: Batch Audit
# ══════════════════════════════════════════════

with tab5:
    st.header("📋 Batch Audit")
    uploaded = st.file_uploader("Upload CSV (url, keyword)", type=["csv"], key="batch_csv")
    st.download_button("📥 Sample CSV", generate_sample_csv(), "sample.csv", "text/csv", key="dl_sample")

    if uploaded:
        entries = parse_csv_urls(uploaded.read().decode("utf-8"))
        st.info(f"{len(entries)} URLs found")
        if st.button("🚀 Run Batch", type="primary", key="btn_batch"):
            with st.spinner(f"Auditing {len(entries)} URLs..."):
                results = batch_audit(entries, max_workers=2, delay=1.5)
                st.session_state["batch_results"] = results

    batch = st.session_state.get("batch_results")
    if batch:
        valid = [r for r in batch if not r.get("error") or r.get("page_title")]
        avg = sum(r.get("score", 0) for r in valid) / len(valid) if valid else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("Audited", len(batch))
        m2.metric("Avg Score", f"{avg:.0f}/100")
        m3.metric("Errors", len(batch) - len(valid))

        comp = generate_comparison_table(batch)
        st.dataframe(pd.DataFrame(comp), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# Tab 6: Keyword Tracking
# ══════════════════════════════════════════════

with tab6:
    st.header("📈 Keyword Tracking")

    kw_track = st.session_state.get("keyword_data")
    if kw_track:
        if st.button("📌 Track This Keyword", type="primary", key="btn_track"):
            all_kw_count = len(set().union(*[kw_track.get(k, []) for k in ['suggestions', 'modifier_expanded', 'related_searches', 'people_also_ask']]))
            snapshot = {
                "total_keywords": all_kw_count,
                "suggestions_count": len(kw_track.get("suggestions", [])),
                "paa_count": len(kw_track.get("people_also_ask", [])),
                "related_count": len(kw_track.get("related_searches", [])),
            }
            db_track_keyword(kw_track.get("seed", ""), snapshot)
            st.success(f"✅ Tracked '{kw_track.get('seed', '')}'!")
            st.rerun()
    else:
        st.info("Run keyword research first.")

    st.divider()
    tracked = db_get_tracked_keywords()
    if tracked:
        for item in tracked:
            kw = item["keyword"]
            with st.expander(f"📌 **{kw}** — {item['snapshot_count']} snapshots"):
                latest = item.get("latest_snapshot", {})
                if latest:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Keywords", latest.get("total_keywords", 0))
                    c2.metric("Suggestions", latest.get("suggestions_count", 0))
                    c3.metric("PAA", latest.get("paa_count", 0))
                if st.button(f"🗑️ Delete {kw}", key=f"del_{kw}"):
                    db_delete_keyword(kw)
                    st.rerun()
    else:
        st.info("No keywords tracked yet.")

# ══════════════════════════════════════════════
# Tab 7: Content Calendar
# ══════════════════════════════════════════════

with tab7:
    st.header("📅 Content Calendar")

    cm_cal = st.session_state.get("cluster_map")
    if cm_cal:
        if st.button("📅 Generate Calendar", type="primary", key="btn_cal"):
            events = create_events_from_content_plan(cm_cal["content_plan"])
            db_save_calendar_events(events)
            st.success(f"✅ Generated {len(events)} events!")
            st.rerun()

    st.divider()
    cal_events = db_load_calendar_events()

    if cal_events:
        stats = get_calendar_stats(cal_events)
        m1, m2, m3 = st.columns(3)
        m1.metric("Events", stats["total"])
        m2.metric("Pillar", stats["by_type"].get("pillar", 0))
        m3.metric("Cluster", stats["by_type"].get("cluster", 0))

        # Deadline notifications
        upcoming = get_upcoming_deadlines(cal_events, notify_days)
        if upcoming:
            st.subheader(f"🔔 {len(upcoming)} Upcoming Deadlines")
            for ev in upcoming:
                st.markdown(f"- **{ev.get('date', '')}** — {ev.get('title', '')} ({ev.get('status', '')})")
            if notify_email:
                if st.button("📤 Send Notification", key="btn_notify"):
                    from notifications import send_deadline_email, send_deadline_slack
                    email_ok = send_deadline_email(upcoming, notify_email)
                    slack_ok = send_deadline_slack(upcoming)
                    if email_ok or slack_ok:
                        st.success(f"✅ Sent! (Email: {'✅' if email_ok else '❌'} | Slack: {'✅' if slack_ok else '❌'})")
                    else:
                        st.warning("Configure SMTP or Slack webhook in .env")
                    st.success("✅ Notifications sent!") if result.get("email_sent") else st.info("Check SMTP config")

        for event in cal_events:
            icon = {"planned": "📋", "in_progress": "🔨", "draft": "📝", "review": "👁️", "published": "✅", "paused": "⏸️"}.get(event.get("status", ""), "📋")
            with st.expander(f"{icon} **{event.get('date', '')}** — {event.get('title', '')}"):
                st.markdown(f"Keyword: `{event.get('keyword', '')}` | Status: {event.get('status', '')}")
                new_status = st.selectbox("Status", ["planned", "in_progress", "draft", "review", "published", "paused"],
                    index=["planned", "in_progress", "draft", "review", "published", "paused"].index(event.get("status", "planned")),
                    key=f"s_{event['id']}")
                if new_status != event.get("status"):
                    if st.button("💾 Save", key=f"u_{event['id']}"):
                        db_update_event_status(event["id"], new_status, STATUS_COLORS.get(new_status, "#6c757d"))
                        st.rerun()
    else:
        st.info("No calendar events. Generate from pillar-cluster map.")

# ══════════════════════════════════════════════
# Tab 8: AI Recommendations
# ══════════════════════════════════════════════

with tab8:
    st.header("🧠 AI SEO Recommendations")
    st.markdown("Get AI-powered recommendations based on your SEO audit results.")

    audit_rec = st.session_state.get("audit_result")
    if not audit_rec:
        st.info("👈 Run an SEO audit first in the Audit tab.")
    else:
        url_display = audit_rec.get("final_url", audit_rec.get("url", ""))
        score = audit_rec.get("score", 0)
        sc = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        st.info(f"Auditing: **{url_display}** — Score: **{sc} {score}/100**")

        # Quick wins (no AI needed)
        st.subheader("⚡ Quick Wins")
        quick_wins = generate_quick_wins(audit_rec)
        if quick_wins:
            for i, win in enumerate(quick_wins):
                impact_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(win["impact"], "⚪")
                with st.expander(f"{impact_color} **{win['action'][:80]}**"):
                    st.markdown(f"**Impact:** {win['impact']} | **Difficulty:** {win['difficulty']}")
                    st.markdown(f"💡 *{win['example']}*")
        else:
            st.success("No quick wins — page looks well optimized!")

        # AI-powered recommendations
        st.divider()
        st.subheader("🤖 AI-Powered Analysis")
        if st.button("🧠 Generate AI Recommendations", type="primary", key="btn_recs"):
            with st.spinner("Analyzing with AI..."):
                recs = analyze_audit_for_recommendations(audit_rec)
                st.session_state["seo_recommendations"] = recs

        recs = st.session_state.get("seo_recommendations")
        if recs:
            st.markdown(recs)
            st.download_button("📥 Download Recommendations", recs, "seo_recommendations.md", "text/markdown")

# ══════════════════════════════════════════════
# Tab 9: Audit History
# ══════════════════════════════════════════════

with tab9:
    st.header("📜 Audit History")
    st.markdown("View all past SEO audits stored in the database.")

    history = db_get_audit_history()
    if not history:
        st.info("No audit history yet. Run an audit to start tracking.")
    else:
        hist_df = pd.DataFrame(history)
        if "created_at" in hist_df.columns:
            hist_df["created_at"] = pd.to_datetime(hist_df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")

        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        if not hist_df.empty:
            fig = px.bar(hist_df, x="url", y="score", color="score", color_continuous_scale="RdYlGn", range_color=[0, 100])
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
