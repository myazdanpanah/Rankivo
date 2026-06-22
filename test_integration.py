"""
Comprehensive integration test for all Rankivo components.
Tests against https://nabzgroup.com/ with keyword "گوشی پزشکی"
"""
import json
import os
import sys
import requests
import time

# Fix Windows console encoding for Persian characters
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import io
# Also create a file-safe output
_log_file = open('test_results.txt', 'w', encoding='utf-8')

BASE = "http://localhost:5500"
SITE = "https://nabzgroup.com/"
KEYWORD = "گوشی پزشکی"

results = {}

def safe_str(val):
    """Convert any value to a safe string for Windows console."""
    try:
        s = str(val)
        return s.encode('ascii', errors='replace').decode('ascii')
    except Exception:
        return '[binary data]'

def safe_print(msg):
    """Print to console with encoding fallback."""
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            print(msg.encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            print('[encoding error - see test_results.txt]')

def log_file(msg):
    """Write to the results file."""
    try:
        _log_file.write(str(msg) + '\n')
        _log_file.flush()
    except Exception:
        pass

def log(test_name, status, data=None):
    """Log test result to both console and file."""
    icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    results[test_name] = {"status": status, "data": data}
    
    # Write full data to file (with Persian chars)
    log_file(f"\n{'='*60}")
    log_file(f"{icon} TEST: {test_name}")
    log_file(f"{'='*60}")
    if data and isinstance(data, dict):
        for k, v in data.items():
            log_file(f"  {k}: {v}")
    
    # Print safe ASCII summary to console
    safe_print(f"\n{'='*60}")
    safe_print(f"{icon} TEST: {test_name}")
    safe_print(f"{'='*60}")
    if data and isinstance(data, dict):
        for k, v in data.items():
            try:
                if isinstance(v, (list, dict)):
                    safe_print(f"  {k}: [{type(v).__name__} with {len(v)} items]")
                elif isinstance(v, bool):
                    safe_print(f"  {k}: {v}")
                elif isinstance(v, (int, float)):
                    safe_print(f"  {k}: {v}")
                else:
                    safe_print(f"  {k}: {safe_str(v)}")
            except Exception:
                safe_print(f"  {k}: [data present]")

# ============================================================
# 0. AUTH - Login and get token
# ============================================================
safe_print("\n[Auth] Logging in...")
resp = requests.post(f"{BASE}/api/auth/login", json={
    "username": "admin",
    "password": "rankivo"
})
if resp.status_code == 200:
    token = resp.json().get("token", "")
    log("Auth Login", "PASS", {"token": token[:20] + "...", "status": resp.status_code})
else:
    log("Auth Login", "FAIL", {"status": resp.status_code, "body": resp.text[:200]})
    exit(1)

HEADERS = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# ============================================================
# 1. KEYWORD RESEARCH
# ============================================================
safe_print("\n\n[1] Testing Keyword Research...")
try:
    resp = requests.post(f"{BASE}/api/keyword-research", headers=HEADERS, json={
        "seed": KEYWORD,
        "depth": 1,
        "expand_modifiers": True,
        "include_trends": True
    }, timeout=60)
    data = resp.json()
    if "error" not in data:
        kw_count = len(data.get("suggestions", []))
        log("1. Keyword Research", "PASS", {
            "status": resp.status_code,
            "suggestions": kw_count,
            "modifier_expanded": len(data.get("modifier_expanded", [])),
            "related_searches": len(data.get("related_searches", [])),
            "people_also_ask": len(data.get("people_also_ask", [])),
            "has_trends": "trends" in data,
            "first_5_suggestions": data.get("suggestions", [])[:5]
        })
    else:
        log("1. Keyword Research", "FAIL", {"error": data["error"]})
except Exception as e:
    log("1. Keyword Research", "FAIL", {"exception": str(e)})

# ============================================================
# 2. PILLAR-CLUSTER
# ============================================================
safe_print("\n\n[2] Testing Pillar-Cluster...")
try:
    resp = requests.post(f"{BASE}/api/pillar-cluster", headers=HEADERS, json={
        "threshold": 0.30
    }, timeout=60)
    data = resp.json()
    if "error" not in data:
        log("2. Pillar-Cluster", "PASS", {
            "status": resp.status_code,
            "total_clusters": data.get("stats", {}).get("total_clusters", 0),
            "total_content_pieces": data.get("stats", {}).get("total_content_pieces", 0),
            "content_plan_items": len(data.get("content_plan", [])),
        })
    else:
        log("2. Pillar-Cluster", "FAIL", {"error": data["error"]})
except Exception as e:
    log("2. Pillar-Cluster", "FAIL", {"exception": str(e)})

# ============================================================
# 3. SEO AUDIT
# ============================================================
safe_print("\n\n[3] Testing SEO Audit...")
try:
    resp = requests.post(f"{BASE}/api/audit", headers=HEADERS, json={
        "url": SITE,
        "keyword": KEYWORD,
        "page_type": "generic"
    }, timeout=60)
    data = resp.json()
    if "error" not in data:
        log("3. SEO Audit", "PASS", {
            "status": resp.status_code,
            "score": data.get("score", 0),
            "title": (data.get("page_title", "") or "MISSING")[:60],
            "word_count": data.get("word_count", 0),
            "issues_count": len(data.get("issues", [])),
            "links_internal": data.get("links", {}).get("internal_count", 0),
            "links_external": data.get("links", {}).get("external_count", 0),
            "images_total": data.get("images", {}).get("total", 0),
            "images_with_alt": data.get("images", {}).get("with_alt", 0),
        })
    else:
        log("3. SEO Audit", "FAIL", {"error": data["error"]})
except Exception as e:
    log("3. SEO Audit", "FAIL", {"exception": str(e)})

# ============================================================
# 4. CONTENT GAP ANALYSIS
# ============================================================
safe_print("\n\n[4] Testing Content Gap Analysis...")
try:
    resp = requests.post(f"{BASE}/api/content-gap/analyze", headers=HEADERS, json={
        "seed": KEYWORD,
        "num_serp_results": 3,
        "max_competitors": 3
    }, timeout=120)
    data = resp.json()
    if "error" not in data:
        summary = data.get("summary", {})
        log("4. Content Gap Analysis", "PASS", {
            "status": resp.status_code,
            "total_gaps": summary.get("total_gaps", 0),
            "competitors_found": summary.get("competitors_analyzed", 0),
            "coverage": summary.get("coverage_percentage", 0),
            "top_3_gaps": [g.get("keyword", "") for g in data.get("gap_analysis", {}).get("gap_keywords", [])[:3]],
        })
    else:
        log("4. Content Gap Analysis", "FAIL", {"error": data.get("error", "")[:200]})
except Exception as e:
    log("4. Content Gap Analysis", "FAIL", {"exception": str(e)})

# ============================================================
# 5. LLM KEYWORD INTELLIGENCE
# ============================================================
safe_print("\n\n[5] Testing LLM Keyword Intelligence...")
try:
    # Get keyword suggestions first for analysis
    kw_resp = requests.post(f"{BASE}/api/keyword-research", headers=HEADERS, json={
        "seed": KEYWORD, "depth": 1, "expand_modifiers": True, "include_trends": False
    }, timeout=60)
    kw_data = kw_resp.json()
    all_keywords = kw_data.get("suggestions", [])[:10] + kw_data.get("modifier_expanded", [])[:5]
    if not all_keywords:
        all_keywords = [KEYWORD]
    
    resp = requests.post(f"{BASE}/api/llm-intel/analyze", headers=HEADERS, json={
        "keywords": all_keywords[:10],
        "seed": KEYWORD,
        "classify_intent": True,
        "cluster": True,
        "estimate_difficulty": True,
        "difficulty_sample_size": 3
    }, timeout=120)
    data = resp.json()
    if "error" not in data:
        log("5. LLM Keyword Intelligence", "PASS", {
            "status": resp.status_code,
            "intent_classifications": len(data.get("intent_map", {})),
            "clusters": len(data.get("clusters", {}).get("clusters", [])),
            "difficulty_estimates": len(data.get("difficulty", {}).get("results", [])),
            "methods_used": data.get("methods_used", {}),
        })
    else:
        log("5. LLM Keyword Intelligence", "FAIL", {"error": data.get("error", "")[:200]})
except Exception as e:
    log("5. LLM Keyword Intelligence", "FAIL", {"exception": str(e)})

# ============================================================
# 6. TECHNICAL SEO
# ============================================================
safe_print("\n\n[6] Testing Technical SEO...")

# 6a. Robots.txt
try:
    resp = requests.post(f"{BASE}/api/technical/robots-txt", headers=HEADERS, json={
        "url": SITE
    }, timeout=30)
    data = resp.json()
    log("6a. Robots.txt", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "has_robots": data.get("has_robots", False),
        "rules_count": len(data.get("rules", [])),
        "sitemaps_found": len(data.get("sitemaps", [])),
    })
except Exception as e:
    log("6a. Robots.txt", "FAIL", {"exception": str(e)})

# 6b. Sitemap
try:
    resp = requests.post(f"{BASE}/api/technical/sitemap", headers=HEADERS, json={
        "url": SITE
    }, timeout=30)
    data = resp.json()
    log("6b. Sitemap", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "has_sitemap": data.get("has_sitemap", False),
        "urls_count": len(data.get("urls", [])),
    })
except Exception as e:
    log("6b. Sitemap", "FAIL", {"exception": str(e)})

# 6c. Structured Data
try:
    resp = requests.post(f"{BASE}/api/technical/structured-data", headers=HEADERS, json={
        "url": SITE
    }, timeout=30)
    data = resp.json()
    log("6c. Structured Data", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "schemas_found": len(data.get("schemas", [])),
        "types": [s.get("type", "") for s in data.get("schemas", [])[:5]],
    })
except Exception as e:
    log("6c. Structured Data", "FAIL", {"exception": str(e)})

# 6d. Web Vitals
try:
    resp = requests.post(f"{BASE}/api/technical/web-vitals", headers=HEADERS, json={
        "url": SITE,
        "strategy": "mobile"
    }, timeout=60)
    data = resp.json()
    log("6d. Web Vitals", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "metrics": list(data.get("metrics", {}).keys())[:5] if data.get("metrics") else [],
    })
except Exception as e:
    log("6d. Web Vitals", "FAIL", {"exception": str(e)})

# ============================================================
# 7. BING SEO
# ============================================================
safe_print("\n\n[7] Testing Bing SEO...")
try:
    resp = requests.post(f"{BASE}/api/bing/analyze", headers=HEADERS, json={
        "url": SITE
    }, timeout=30)
    data = resp.json()
    log("7. Bing SEO Analyze", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "has_data": bool(data),
    })
except Exception as e:
    log("7. Bing SEO Analyze", "FAIL", {"exception": str(e)})

# Bing Trends
try:
    resp = requests.post(f"{BASE}/api/bing/trends", headers=HEADERS, json={
        "keywords": [KEYWORD],
        "geo": "IR"
    }, timeout=30)
    data = resp.json()
    log("7b. Bing Trends", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "source": data.get("source", ""),
        "simulated": data.get("simulated", False),
        "dates_count": len(data.get("dates", [])),
        "keywords_count": len(data.get("values", {})),
    })
except Exception as e:
    log("7b. Bing Trends", "FAIL", {"exception": str(e)})

# ============================================================
# 8. GOOGLE TRENDS
# ============================================================
safe_print("\n\n[8] Testing Google Trends...")
try:
    resp = requests.post(f"{BASE}/api/trends/interest-over-time", headers=HEADERS, json={
        "keywords": [KEYWORD],
        "timeframe": "today 12-m",
        "geo": ""
    }, timeout=30)
    data = resp.json()
    log("8a. Trends Interest Over Time", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "has_data": bool(data.get("interest_over_time")),
        "keywords_tracked": len(data.get("keywords", [])),
    })
except Exception as e:
    log("8a. Trends Interest Over Time", "FAIL", {"exception": str(e)})

try:
    resp = requests.post(f"{BASE}/api/trends/related-queries", headers=HEADERS, json={
        "keywords": [KEYWORD],
        "timeframe": "today 12-m",
        "geo": ""
    }, timeout=30)
    data = resp.json()
    log("8b. Trends Related Queries", "PASS" if "error" not in data else "FAIL", {
        "status": resp.status_code,
        "has_data": bool(data.get("related_queries")),
    })
except Exception as e:
    log("8b. Trends Related Queries", "FAIL", {"exception": str(e)})

# ============================================================
# 9. ARTICLE GENERATION
# ============================================================
safe_print("\n\n[9] Testing Article Generation...")
try:
    resp = requests.post(f"{BASE}/api/article/generate", headers=HEADERS, json={
        "topic": f"راهنمای جامع {KEYWORD}",
        "keywords": [KEYWORD, "خرید گوشی پزشکی", "قیمت گوشی پزشکی"],
        "provider": "ollama",
        "word_count": 500,
        "tone": "informative, authoritative",
        "language": "fa"
    }, timeout=120)
    data = resp.json()
    if "error" not in data and "article" in data:
        article = data["article"]
        log("9. Article Generation", "PASS", {
            "status": resp.status_code,
            "topic": data.get("topic", ""),
            "article_length": len(article) if isinstance(article, str) else 0,
            "preview": (article[:150] + "...") if isinstance(article, str) else str(article)[:150],
        })
    else:
        log("9. Article Generation", "FAIL", {"error": data.get("error", "Unknown")[:200]})
except Exception as e:
    log("9. Article Generation", "FAIL", {"exception": str(e)})

# ============================================================
# 10. FULL PIPELINE
# ============================================================
safe_print("\n\n[10] Testing Full Pipeline Run...")
try:
    resp = requests.post(f"{BASE}/api/pipeline/run", headers=HEADERS, json={
        "seed": KEYWORD,
        "depth": 1,
        "expand_modifiers": True,
        "provider": "ollama",
        "threshold": 0.30
    }, timeout=180)
    data = resp.json()
    if "error" not in data:
        log("10. Full Pipeline", "PASS", {
            "status": resp.status_code,
            "total_keywords": data.get("stats", {}).get("total_keywords", 0),
            "total_clusters": data.get("stats", {}).get("total_clusters", 0),
            "total_articles": data.get("stats", {}).get("total_articles", 0),
            "has_ai_analysis": bool(data.get("ai_analysis")),
            "has_gap_analysis": data.get("gap_analysis", {}).get("status") == "success",
            "content_plan_items": len(data.get("content_plan", [])),
        })
    else:
        log("10. Full Pipeline", "FAIL", {"error": data.get("error", "")[:200]})
except Exception as e:
    log("10. Full Pipeline", "FAIL", {"exception": str(e)})

# ============================================================
# SUMMARY
# ============================================================
print("\n\n" + "="*60)
print("📋 TEST SUMMARY")
print("="*60)
passed = sum(1 for r in results.values() if r["status"] == "PASS")
failed = sum(1 for r in results.values() if r["status"] == "FAIL")
total = len(results)

for name, r in results.items():
    icon = "[PASS]" if r["status"] == "PASS" else "[FAIL]"
    print(f"  {icon} {name}")

print(f"\n{'='*60}")
print(f"  TOTAL: {total} | PASSED: {passed} | FAILED: {failed}")
print(f"{'='*60}")
