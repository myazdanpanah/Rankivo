"""
Unit tests for all new Rankivo modules added in the claude-seo gap closure.
Tests: seo_images, sitemap_audit, hreflang_audit, local_seo, ecommerce_seo,
       sxo_audit, content_brief, programmatic_seo, seo_plan, pdf_report,
       site_performance, parallel_orchestrator.
"""
import json
import os
import sys
import traceback

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests

BASE = "http://localhost:5500"
SITE = "https://nabzgroup.com/"

results = {}


def p(msg):
    try:
        print(msg)
    except:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def run_test(name, fn):
    try:
        data = fn()
        results[name] = {"status": "PASS", "data": data}
        p(f"  [PASS] {name}")
        return data
    except Exception as e:
        tb = traceback.format_exc()
        results[name] = {"status": "FAIL", "error": str(e), "traceback": tb}
        p(f"  [FAIL] {name}: {e}")
        return None


# --- Login ---
p("\n--- AUTH ---")
try:
    resp = requests.post(f"{BASE}/api/auth/login", json={"username": "admin", "password": "admin12345"}, timeout=10)
    token = resp.json()["token"]
    H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    p("  Logged in OK")
except Exception as e:
    p(f"  [FATAL] Cannot login: {e}")
    sys.exit(1)


# ══════════════════════════════════════════════
# 1. Image SEO Analysis
# ══════════════════════════════════════════════
p("\n--- 1. IMAGE SEO ---")
def test_images():
    r = requests.post(f"{BASE}/api/images/analyze", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "total_images": d.get("summary", {}).get("total_images", 0),
        "with_alt": d.get("summary", {}).get("images_with_alt", 0),
        "issues": len(d.get("issues", [])),
        "has_score": "score" in d,
    }
run_test("Image SEO Analysis", test_images)


# ══════════════════════════════════════════════
# 2. Sitemap Audit
# ══════════════════════════════════════════════
p("\n--- 2. SITEMAP AUDIT ---")
def test_sitemap_audit():
    r = requests.post(f"{BASE}/api/sitemap/audit", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "found": d.get("sitemap_found", False),
        "urls_count": d.get("urls_count", 0),
        "issues": len(d.get("issues", [])),
    }
run_test("Sitemap Audit", test_sitemap_audit)


# ══════════════════════════════════════════════
# 3. Hreflang / i18n Audit
# ══════════════════════════════════════════════
p("\n--- 3. HREFLANG AUDIT ---")
def test_hreflang():
    r = requests.post(f"{BASE}/api/hreflang/audit", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "has_hreflang": d.get("has_hreflang_tags", False),
        "tags_found": d.get("tags_found", 0),
        "issues": len(d.get("issues", [])),
    }
run_test("Hreflang Audit", test_hreflang)


# ══════════════════════════════════════════════
# 4. Local SEO Audit
# ══════════════════════════════════════════════
p("\n--- 4. LOCAL SEO ---")
def test_local_seo():
    r = requests.post(f"{BASE}/api/local-seo/audit", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "score": d.get("score", 0),
        "has_nap": d.get("nap", {}).get("found", False),
        "has_local_business": d.get("local_business_schema", False),
        "issues": len(d.get("issues", [])),
    }
run_test("Local SEO Audit", test_local_seo)


# ══════════════════════════════════════════════
# 5. E-commerce SEO Audit
# ══════════════════════════════════════════════
p("\n--- 5. E-COMMERCE SEO ---")
def test_ecommerce():
    r = requests.post(f"{BASE}/api/ecommerce/audit", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "score": d.get("score", 0),
        "has_product_schema": d.get("product_schema", False),
        "has_pricing": d.get("pricing_signals", False),
        "issues": len(d.get("issues", [])),
    }
run_test("E-commerce SEO Audit", test_ecommerce)


# ══════════════════════════════════════════════
# 6. SXO (Search Experience) Audit
# ══════════════════════════════════════════════
p("\n--- 6. SXO AUDIT ---")
def test_sxo():
    r = requests.post(f"{BASE}/api/sxo/audit", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "score": d.get("score", 0),
        "page_type": d.get("page_type", "unknown"),
        "intent_alignment": d.get("intent_alignment", {}).get("score", 0),
        "issues": len(d.get("issues", [])),
    }
run_test("SXO Audit", test_sxo)


# ══════════════════════════════════════════════
# 7. Content Brief Generator
# ══════════════════════════════════════════════
p("\n--- 7. CONTENT BRIEF ---")
def test_content_brief():
    r = requests.post(f"{BASE}/api/content-brief/generate", headers=H,
                      json={"topic": "SEO best practices", "keywords": ["seo tips", "seo guide"],
                            "intent": "informational", "language": "en"}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "has_outline": "outline" in d,
        "has_keywords": "primary_keywords" in d or "keywords" in d,
        "has_recommendations": "recommendations" in d or "content_recommendations" in d,
        "outline_sections": len(d.get("outline", [])),
    }
run_test("Content Brief Generator", test_content_brief)


# ══════════════════════════════════════════════
# 8. Programmatic SEO Audit
# ══════════════════════════════════════════════
p("\n--- 8. PROGRAMMATIC SEO ---")
def test_programmatic():
    r = requests.post(f"{BASE}/api/programmatic/audit", headers=H,
                      json={"url": SITE}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "score": d.get("score", 0),
        "patterns_found": len(d.get("url_patterns", [])),
        "has_thin_content": d.get("thin_content_risk", False),
        "issues": len(d.get("issues", [])),
    }
run_test("Programmatic SEO Audit", test_programmatic)


# ══════════════════════════════════════════════
# 9. SEO Strategic Plan
# ══════════════════════════════════════════════
p("\n--- 9. SEO STRATEGIC PLAN ---")
def test_seo_plan():
    r = requests.post(f"{BASE}/api/plan/generate", headers=H,
                      json={"industry": "saas"}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "has_phases": "phases" in d or "plan" in d,
        "has_priorities": "priorities" in d or "recommendations" in d,
        "industry": d.get("industry", "unknown"),
    }
run_test("SEO Strategic Plan", test_seo_plan)


def test_seo_plan_industries():
    r = requests.get(f"{BASE}/api/plan/industries", headers=H, timeout=10)
    d = r.json()
    return {"industries_count": len(d.get("industries", []))}
run_test("SEO Plan Industries List", test_seo_plan_industries)


# ══════════════════════════════════════════════
# 10. PDF Report Generation
# ══════════════════════════════════════════════
p("\n--- 10. PDF REPORT ---")
def test_pdf_report():
    # First get an audit result to use as report data
    r = requests.post(f"{BASE}/api/audit", headers=H,
                      json={"url": SITE, "keyword": "seo"}, timeout=60)
    audit = r.json()
    # Generate report
    r2 = requests.post(f"{BASE}/api/report/generate", headers=H,
                       json={"audit_data": audit, "report_type": "full", "format": "html"}, timeout=30)
    d = r2.json()
    assert "error" not in d, d.get("error")
    return {
        "has_report": "report" in d or "content" in d or "html" in d,
        "report_length": len(d.get("html", d.get("content", d.get("report", "")))),
    }
run_test("PDF/HTML Report Generation", test_pdf_report)


# ══════════════════════════════════════════════
# 11. Site Performance Monitoring
# ══════════════════════════════════════════════
p("\n--- 11. SITE PERFORMANCE ---")
def test_perf_dashboard():
    r = requests.post(f"{BASE}/api/performance/dashboard", headers=H,
                      json={"url": SITE, "days": 30}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "has_current": bool(d.get("current")),
        "grade": d.get("grade", "N/A"),
        "cwv_status": d.get("cwv_status", "unknown"),
        "snapshots": d.get("snapshots_count", 0),
    }
run_test("Performance Dashboard", test_perf_dashboard)


def test_perf_save_snapshot():
    r = requests.post(f"{BASE}/api/performance/save-snapshot", headers=H,
                      json={"url": SITE, "audit_data": {"score": 75, "word_count": 1000, "issues": [], "headings": {"h2": ["a"]}, "links": {"internal_count": 5, "external_count": 2}, "images": {"total": 3}}}, timeout=30)
    d = r.json()
    return {"saved": d.get("saved", False), "overall_score": d.get("overall_score", 0)}
run_test("Performance Save Snapshot", test_perf_save_snapshot)


def test_perf_tracked_sites():
    r = requests.get(f"{BASE}/api/performance/tracked-sites", headers=H, timeout=10)
    d = r.json()
    return {"tracked_count": len(d.get("sites", []))}
run_test("Performance Tracked Sites", test_perf_tracked_sites)


# ══════════════════════════════════════════════
# 12. Parallel Orchestrator
# ══════════════════════════════════════════════
p("\n--- 12. PARALLEL ORCHESTRATOR ---")
def test_orchestrator_info():
    r = requests.get(f"{BASE}/api/orchestrator/info", headers=H, timeout=10)
    d = r.json()
    return {"agents": len(d.get("agents", d.get("available_agents", [])))}
run_test("Orchestrator Info", test_orchestrator_info)


def test_orchestrator_focused():
    r = requests.post(f"{BASE}/api/orchestrator/focused", headers=H,
                      json={"url": SITE, "modules": ["seo_audit", "technical_seo"]}, timeout=120)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "overall_score": d.get("overall_score", 0),
        "modules_run": d.get("modules_run", 0),
        "has_recommendations": bool(d.get("recommendations")),
    }
run_test("Orchestrator Focused Audit", test_orchestrator_focused)


# ══════════════════════════════════════════════
# Save results
# ══════════════════════════════════════════════
with open("test_new_modules_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# Summary
p("\n" + "=" * 60)
p("NEW MODULES TEST RESULTS")
p("=" * 60)
passed = sum(1 for r in results.values() if r["status"] == "PASS")
failed = sum(1 for r in results.values() if r["status"] == "FAIL")
for name, r in results.items():
    tag = "PASS" if r["status"] == "PASS" else "FAIL"
    p(f"  [{tag}] {name}")
p(f"\n  TOTAL: {len(results)} | PASSED: {passed} | FAILED: {failed}")
p("=" * 60)
