"""
Component integration test for Rankivo.
Tests all components against https://nabzgroup.com/ with keyword: ghooshi pezeshki
Results saved to test_results.json (UTF-8).
"""
import json
import os
import sys
import time
import traceback

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import requests

BASE = "http://localhost:5500"
SITE = "https://nabzgroup.com/"
KEYWORD_FA = "\u06af\u0648\u0634\u06cc \u067e\u0632\u0634\u06a9\u06cc"  # ghooshi pezeshki

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
resp = requests.post(f"{BASE}/api/auth/login", json={"username": "admin", "password": "admin12345"})
token = resp.json()["token"]
H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
p("  Logged in OK")

# --- 1. Keyword Research ---
p("\n--- 1. KEYWORD RESEARCH ---")
def test_kw():
    r = requests.post(f"{BASE}/api/keyword-research", headers=H, json={
        "seed": KEYWORD_FA, "depth": 1, "expand_modifiers": True, "include_trends": True
    }, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "suggestions_count": len(d.get("suggestions", [])),
        "modifier_expanded_count": len(d.get("modifier_expanded", [])),
        "related_count": len(d.get("related_searches", [])),
        "paa_count": len(d.get("people_also_ask", [])),
        "has_trends": "trends" in d,
        "suggestions_sample": d.get("suggestions", [])[:5],
    }
run_test("Keyword Research", test_kw)

# --- 2. Pillar-Cluster ---
p("\n--- 2. PILLAR-CLUSTER ---")
def test_pc():
    r = requests.post(f"{BASE}/api/pillar-cluster", headers=H, json={"threshold": 0.30}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "total_clusters": d.get("stats", {}).get("total_clusters", 0),
        "total_content_pieces": d.get("stats", {}).get("total_content_pieces", 0),
        "content_plan_items": len(d.get("content_plan", [])),
    }
run_test("Pillar-Cluster", test_pc)

# --- 3. SEO Audit ---
p("\n--- 3. SEO AUDIT ---")
def test_audit():
    r = requests.post(f"{BASE}/api/audit", headers=H, json={
        "url": SITE, "keyword": KEYWORD_FA, "page_type": "generic"
    }, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "score": d.get("score", 0),
        "word_count": d.get("word_count", 0),
        "issues_count": len(d.get("issues", [])),
        "links_internal": d.get("links", {}).get("internal_count", 0),
        "links_external": d.get("links", {}).get("external_count", 0),
        "images_total": d.get("images", {}).get("total", 0),
        "images_with_alt": d.get("images", {}).get("with_alt", 0),
        "text_to_html_ratio": d.get("text_to_html_ratio", 0),
    }
run_test("SEO Audit", test_audit)

# --- 4. Content Gap ---
p("\n--- 4. CONTENT GAP ANALYSIS ---")
def test_gap():
    r = requests.post(f"{BASE}/api/content-gap/analyze", headers=H, json={
        "seed": KEYWORD_FA, "num_serp_results": 3, "max_competitors": 3
    }, timeout=120)
    d = r.json()
    assert "error" not in d, d.get("error")
    s = d.get("summary", {})
    return {
        "total_gaps": s.get("total_gaps", 0),
        "competitors_analyzed": s.get("competitors_analyzed", 0),
        "coverage_pct": s.get("coverage_percentage", 0),
        "top_gaps": [g.get("keyword", "") for g in d.get("gap_analysis", {}).get("gap_keywords", [])[:5]],
    }
run_test("Content Gap", test_gap)

# --- 5. LLM Keyword Intelligence ---
p("\n--- 5. LLM KEYWORD INTELLIGENCE ---")
def test_llm():
    kw_r = requests.post(f"{BASE}/api/keyword-research", headers=H, json={
        "seed": KEYWORD_FA, "depth": 1, "expand_modifiers": True, "include_trends": False
    }, timeout=60)
    kw_d = kw_r.json()
    kws = kw_d.get("suggestions", [])[:10]
    if not kws:
        kws = [KEYWORD_FA]
    r = requests.post(f"{BASE}/api/llm-intel/analyze", headers=H, json={
        "keywords": kws, "seed": KEYWORD_FA,
        "classify_intent": True, "cluster": True,
        "estimate_difficulty": True, "difficulty_sample_size": 3
    }, timeout=120)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "intent_count": len(d.get("intent_map", {})),
        "cluster_count": len(d.get("clusters", [])),
        "difficulty_count": len(d.get("difficulties", {})),
        "methods": d.get("methods_used", {}),
    }
run_test("LLM Keyword Intelligence", test_llm)

# --- 6. Technical SEO ---
p("\n--- 6. TECHNICAL SEO ---")

def test_robots():
    r = requests.post(f"{BASE}/api/technical/robots-txt", headers=H, json={"url": SITE}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {"has_robots": d.get("has_robots", False), "rules": len(d.get("rules", []))}
run_test("Technical: robots.txt", test_robots)

def test_sitemap():
    r = requests.post(f"{BASE}/api/technical/sitemap", headers=H, json={"url": SITE}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {"has_sitemap": d.get("has_sitemap", False), "urls": len(d.get("urls", []))}
run_test("Technical: sitemap", test_sitemap)

def test_struct():
    r = requests.post(f"{BASE}/api/technical/structured-data", headers=H, json={"url": SITE}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {"schemas": len(d.get("schemas", []))}
run_test("Technical: structured data", test_struct)

def test_vitals():
    r = requests.post(f"{BASE}/api/technical/web-vitals", headers=H, json={"url": SITE, "strategy": "mobile"}, timeout=60)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {"metrics": list(d.get("metrics", {}).keys()) if d.get("metrics") else []}
run_test("Technical: web vitals", test_vitals)

# --- 7. Bing SEO ---
p("\n--- 7. BING SEO ---")
def test_bing():
    r = requests.post(f"{BASE}/api/bing/analyze", headers=H, json={"url": SITE}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {"has_data": bool(d)}
run_test("Bing SEO Analyze", test_bing)

def test_bing_trends():
    r = requests.post(f"{BASE}/api/bing/trends", headers=H, json={"keywords": [KEYWORD_FA], "geo": "IR"}, timeout=30)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {"source": d.get("source", ""), "simulated": d.get("simulated", False), "dates": len(d.get("dates", []))}
run_test("Bing Trends", test_bing_trends)

# --- 8. Google Trends ---
p("\n--- 8. GOOGLE TRENDS ---")
def test_trends_iot():
    r = requests.post(f"{BASE}/api/trends/interest-over-time", headers=H, json={
        "keywords": [KEYWORD_FA], "timeframe": "today 12-m", "geo": ""
    }, timeout=30)
    d = r.json()
    has = bool(d.get("interest_over_time"))
    return {"has_data": has, "keywords": len(d.get("keywords", []))}
run_test("Trends: interest over time", test_trends_iot)

def test_trends_rated():
    r = requests.post(f"{BASE}/api/trends/related-queries", headers=H, json={
        "keywords": [KEYWORD_FA], "timeframe": "today 12-m", "geo": ""
    }, timeout=30)
    d = r.json()
    return {"has_data": bool(d.get("related_queries"))}
run_test("Trends: related queries", test_trends_rated)

# --- 9. Article Generation ---
p("\n--- 9. ARTICLE GENERATION ---")
def test_article():
    r = requests.post(f"{BASE}/api/article/generate", headers=H, json={
        "topic": f"Guide to {KEYWORD_FA}",
        "keywords": [KEYWORD_FA],
        "provider": "ollama",
        "word_count": 500,
        "tone": "informative",
        "language": "fa"
    }, timeout=120)
    d = r.json()
    assert "error" not in d, d.get("error")
    art = d.get("article", "")
    return {"length": len(art) if isinstance(art, str) else 0, "has_content": len(art) > 50 if isinstance(art, str) else False}
run_test("Article Generation", test_article)

# --- 10. Full Pipeline ---
p("\n--- 10. FULL PIPELINE ---")
def test_pipeline():
    r = requests.post(f"{BASE}/api/pipeline/run", headers=H, json={
        "seed": KEYWORD_FA, "depth": 1, "expand_modifiers": True,
        "provider": "ollama", "threshold": 0.30
    }, timeout=180)
    d = r.json()
    assert "error" not in d, d.get("error")
    return {
        "total_keywords": d.get("stats", {}).get("total_keywords", 0),
        "total_clusters": d.get("stats", {}).get("total_clusters", 0),
        "total_articles": d.get("stats", {}).get("total_articles", 0),
        "has_ai_analysis": bool(d.get("ai_analysis")),
        "content_plan_items": len(d.get("content_plan", [])),
    }
run_test("Full Pipeline", test_pipeline)

# --- Save results ---
with open("test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# --- Summary ---
p("\n" + "=" * 60)
p("RESULTS SUMMARY")
p("=" * 60)
passed = sum(1 for r in results.values() if r["status"] == "PASS")
failed = sum(1 for r in results.values() if r["status"] == "FAIL")
for name, r in results.items():
    tag = "PASS" if r["status"] == "PASS" else "FAIL"
    p(f"  [{tag}] {name}")
p(f"\n  TOTAL: {len(results)} | PASSED: {passed} | FAILED: {failed}")
p("=" * 60)
p("Full results saved to test_results.json")
