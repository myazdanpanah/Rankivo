"""
Rankivo — PDF Report Generation Module
Generates professional SEO audit reports as PDF using matplotlib charts.
Falls back to HTML report if PDF libraries are not installed.
"""
import os
from html import escape as html_escape
from datetime import datetime
from config import _safe_print


def _check_dependencies() -> dict:
    """Check which report generation libraries are available."""
    deps = {"matplotlib": False, "reportlab": False, "weasyprint": False}
    try:
        import matplotlib
        deps["matplotlib"] = True
    except ImportError:
        pass
    try:
        import reportlab
        deps["reportlab"] = True
    except ImportError:
        pass
    try:
        import weasyprint
        deps["weasyprint"] = True
    except ImportError:
        pass
    return deps


# ──────────────────────────────────────────────
# HTML Report Generator (always available)
# ──────────────────────────────────────────────

def _generate_html_report(audit_data: dict, report_type: str = "full") -> str:
    """Generate a comprehensive HTML report."""
    url = html_escape(str(audit_data.get("url", "Unknown")))
    score = audit_data.get("score", audit_data.get("composite_score", 0))
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Score color
    if score >= 80:
        score_color = "#10b981"
        score_label = "Excellent"
    elif score >= 60:
        score_color = "#f59e0b"
        score_label = "Good"
    elif score >= 40:
        score_color = "#f97316"
        score_label = "Needs Work"
    else:
        score_color = "#ef4444"
        score_label = "Poor"

    # Collect all issues
    issues = audit_data.get("issues", [])
    critical = [i for i in issues if i.get("severity") == "critical"]
    warnings = [i for i in issues if i.get("severity") == "warning"]
    infos = [i for i in issues if i.get("severity") == "info"]

    # Collect recommendations
    recommendations = audit_data.get("recommendations", [])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SEO Audit Report - {url}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #1a1a2e; background: #f8fafc; line-height: 1.6; }}
  .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
  .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 16px; margin-bottom: 30px; }}
  .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
  .header .url {{ font-size: 14px; opacity: 0.9; word-break: break-all; }}
  .header .date {{ font-size: 13px; opacity: 0.7; margin-top: 8px; }}
  .score-card {{ display: flex; align-items: center; justify-content: center; gap: 20px; background: white; border-radius: 16px; padding: 30px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  .score-circle {{ width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px; font-weight: 800; color: white; background: {score_color}; }}
  .score-info h2 {{ font-size: 24px; color: {score_color}; }}
  .score-info p {{ color: #64748b; font-size: 14px; }}
  .section {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
  .section h3 {{ font-size: 18px; margin-bottom: 16px; color: #1a1a2e; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
  .issue {{ padding: 10px 14px; margin-bottom: 8px; border-radius: 8px; font-size: 14px; }}
  .issue.critical {{ background: #fef2f2; border-left: 4px solid #ef4444; color: #991b1b; }}
  .issue.warning {{ background: #fffbeb; border-left: 4px solid #f59e0b; color: #92400e; }}
  .issue.info {{ background: #eff6ff; border-left: 4px solid #3b82f6; color: #1e40af; }}
  .rec {{ padding: 10px 14px; margin-bottom: 8px; border-radius: 8px; background: #f0fdf4; border-left: 4px solid #22c55e; font-size: 14px; color: #166534; }}
  .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }}
  .metric {{ background: #f8fafc; border-radius: 8px; padding: 16px; text-align: center; }}
  .metric .value {{ font-size: 24px; font-weight: 700; color: #667eea; }}
  .metric .label {{ font-size: 12px; color: #64748b; margin-top: 4px; }}
  .footer {{ text-align: center; padding: 30px; color: #94a3b8; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🔍 SEO Audit Report</h1>
    <div class="url">{url}</div>
    <div class="date">Generated: {now} | Powered by Rankivo</div>
  </div>

  <div class="score-card">
    <div class="score-circle">{score}</div>
    <div class="score-info">
      <h2>{score_label}</h2>
      <p>Overall SEO Health Score</p>
      <p>{len(critical)} critical issues · {len(warnings)} warnings · {len(infos)} notices</p>
    </div>
  </div>
"""

    # Add metric cards if available
    metrics_to_show = []
    if "word_count" in audit_data:
        metrics_to_show.append(("Word Count", str(audit_data["word_count"])))
    if "links" in audit_data:
        links = audit_data["links"]
        metrics_to_show.append(("Internal Links", str(links.get("internal_count", 0))))
        metrics_to_show.append(("External Links", str(links.get("external_count", 0))))
    if "images" in audit_data:
        imgs = audit_data["images"]
        metrics_to_show.append(("Images", str(imgs.get("total", 0))))
        metrics_to_show.append(("Alt Coverage", f"{imgs.get('alt_coverage', 0)}%"))
    if "composite_score" in audit_data and "factors" in audit_data:
        for factor_name, factor_data in audit_data["factors"].items():
            if isinstance(factor_data, dict) and "score" in factor_data:
                metrics_to_show.append(
                    (factor_name.replace("_", " ").title(), f"{factor_data['score']}/{factor_data.get('max_score', 25)}")
                )

    if metrics_to_show:
        html += '  <div class="section"><h3>📊 Key Metrics</h3><div class="metric-grid">'
        for label, value in metrics_to_show[:8]:
            html += f'<div class="metric"><div class="value">{value}</div><div class="label">{label}</div></div>'
        html += '</div></div>\n'

    # Critical issues
    if critical:
        html += '  <div class="section"><h3>🔴 Critical Issues</h3>'
        for issue in critical[:15]:
            msg = html_escape(str(issue.get("message", str(issue))))
            html += f'<div class="issue critical">⚠️ {msg}</div>'
        html += '</div>\n'

    # Warnings
    if warnings:
        html += '  <div class="section"><h3>🟡 Warnings</h3>'
        for issue in warnings[:15]:
            msg = html_escape(str(issue.get("message", str(issue))))
            html += f'<div class="issue warning">⚡ {msg}</div>'
        html += '</div>\n'

    # Info
    if infos:
        html += '  <div class="section"><h3>🔵 Notices</h3>'
        for issue in infos[:10]:
            msg = html_escape(str(issue.get("message", str(issue))))
            html += f'<div class="issue info">ℹ️ {msg}</div>'
        html += '</div>\n'

    # Recommendations
    if recommendations:
        html += '  <div class="section"><h3>✅ Recommendations</h3>'
        for rec in recommendations[:15]:
            if isinstance(rec, dict):
                msg = rec.get("action", rec.get("message", str(rec)))
            else:
                msg = str(rec)
            html += f'<div class="rec">💡 {msg}</div>'
        html += '</div>\n'

    html += f"""
  <div class="footer">
    Report generated by <strong>Rankivo</strong> — Free AI-Powered SEO Tool<br>
    {now}
  </div>
</div>
</body>
</html>"""

    return html


# ──────────────────────────────────────────────
# Chart Generation (matplotlib)
# ──────────────────────────────────────────────

def _generate_charts(audit_data: dict, output_dir: str) -> list[str]:
    """Generate matplotlib charts for the report. Returns list of image paths."""
    chart_paths = []
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        os.makedirs(output_dir, exist_ok=True)

        # 1. Score breakdown chart (for E-E-A-T, GEO, etc.)
        factors = audit_data.get("factors", {})
        if factors and any(isinstance(v, dict) and "score" in v for v in factors.values()):
            fig, ax = plt.subplots(figsize=(8, 4))
            factor_names = []
            factor_scores = []
            factor_maxes = []
            for name, data in factors.items():
                if isinstance(data, dict) and "score" in data:
                    factor_names.append(name.replace("_", " ").title())
                    factor_scores.append(data["score"])
                    factor_maxes.append(data.get("max_score", 25))

            if factor_names:
                x = range(len(factor_names))
                bars = ax.bar(x, factor_scores, color="#667eea", label="Score", zorder=3)
                ax.bar(x, factor_maxes, color="#e2e8f0", label="Max", zorder=2)
                ax.set_xticks(x)
                ax.set_xticklabels(factor_names, rotation=30, ha="right", fontsize=10)
                ax.set_ylabel("Score")
                ax.set_title("Factor Breakdown")
                ax.legend()
                plt.tight_layout()
                path = os.path.join(output_dir, "chart_factors.png")
                plt.savefig(path, dpi=150, bbox_inches="tight")
                plt.close()
                chart_paths.append(path)

        # 2. Issues by severity pie chart
        issues = audit_data.get("issues", [])
        if issues:
            severity_counts = {}
            for issue in issues:
                sev = issue.get("severity", "info")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            if severity_counts:
                fig, ax = plt.subplots(figsize=(5, 5))
                colors = {"critical": "#ef4444", "warning": "#f59e0b", "info": "#3b82f6"}
                labels = list(severity_counts.keys())
                sizes = list(severity_counts.values())
                chart_colors = [colors.get(l, "#94a3b8") for l in labels]
                ax.pie(sizes, labels=[l.title() for l in labels], colors=chart_colors, autopct="%1.0f%%", startangle=90)
                ax.set_title("Issues by Severity")
                plt.tight_layout()
                path = os.path.join(output_dir, "chart_issues.png")
                plt.savefig(path, dpi=150, bbox_inches="tight")
                plt.close()
                chart_paths.append(path)

        # 3. Link distribution (if available)
        links = audit_data.get("links", {})
        if links.get("internal_count", 0) + links.get("external_count", 0) > 0:
            fig, ax = plt.subplots(figsize=(5, 5))
            labels = ["Internal", "External", "Nofollow"]
            sizes = [links.get("internal_count", 0), links.get("external_count", 0), links.get("nofollow_count", 0)]
            colors = ["#10b981", "#667eea", "#f59e0b"]
            ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
            ax.set_title("Link Distribution")
            plt.tight_layout()
            path = os.path.join(output_dir, "chart_links.png")
            plt.savefig(path, dpi=150, bbox_inches="tight")
            plt.close()
            chart_paths.append(path)

    except ImportError:
        _safe_print("[pdf_report] matplotlib not available — skipping charts")
    except Exception as e:
        _safe_print(f"[pdf_report] Chart generation error: {e}")

    return chart_paths


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def generate_report(
    audit_data: dict,
    report_type: str = "full",
    output_format: str = "html",
    output_dir: str = None,
) -> dict:
    """
    Generate an SEO audit report.
    
    Args:
        audit_data: Audit results from any module
        report_type: Type of report ('full', 'eeat', 'geo', 'technical', etc.)
        output_format: 'html' or 'pdf'
        output_dir: Directory to save the report
    
    Returns:
        dict with report_path, format, and html_content
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(output_dir, exist_ok=True)

    # Generate HTML report
    html_content = _generate_html_report(audit_data, report_type)

    # Generate charts
    charts = _generate_charts(audit_data, output_dir)

    # Save HTML
    url_slug = (audit_data.get("url", "report")
                .replace("https://", "").replace("http://", "")
                .replace("/", "_")[:50])
    filename = f"seo_report_{url_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    result = {
        "report_path": filepath,
        "filename": filename,
        "format": "html",
        "charts": charts,
        "html_content": html_content[:500] + "...",
    }

    # Try PDF if requested and weasyprint available
    if output_format == "pdf":
        deps = _check_dependencies()
        if deps.get("weasyprint"):
            try:
                import weasyprint
                pdf_filename = filename.replace(".html", ".pdf")
                pdf_path = os.path.join(output_dir, pdf_filename)
                weasyprint.HTML(string=html_content).write_pdf(pdf_path)
                result["pdf_path"] = pdf_path
                result["pdf_filename"] = pdf_filename
                result["format"] = "pdf"
            except Exception as e:
                _safe_print(f"[pdf_report] PDF generation failed: {e}")
                result["pdf_error"] = str(e)

    return result
