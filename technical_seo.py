"""
SEO AI Tools - Technical SEO Module
Analyzes robots.txt, sitemaps, structured data (JSON-LD), and Core Web Vitals.
"""
import json
import requests
import traceback
from urllib.parse import urlparse, urljoin
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# 1. robots.txt Analysis
# ──────────────────────────────────────────────


def analyze_robots_txt(url: str) -> dict:
    """
    Fetch and analyze a site's robots.txt file.
    Returns directives, issues, and recommendations.
    """
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    base = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base}/robots.txt"

    result = {
        "url": robots_url,
        "found": False,
        "directives": {},
        "sitemaps_found": [],
        "user_agents": [],
        "issues": [],
        "score": 100,
    }

    try:
        resp = requests.get(robots_url, headers={"User-Agent": _random_ua()}, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            result["issues"].append({
                "severity": "critical",
                "message": "No robots.txt file found — search engines have no crawl directives",
            })
            result["score"] = 50
            return result
        resp.raise_for_status()
        result["found"] = True
    except requests.RequestException as e:
        result["issues"].append({
            "severity": "warning",
            "message": f"Could not fetch robots.txt: {e}",
        })
        return result

    content = resp.text
    lines = content.strip().split("\n")

    current_agent = "*"
    directives = {}
    sitemaps = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "user-agent":
            current_agent = value
            if current_agent not in directives:
                directives[current_agent] = {"allow": [], "disallow": [], "crawl_delay": None}
        elif key == "disallow" and value:
            if current_agent in directives:
                directives[current_agent]["disallow"].append(value)
        elif key == "allow" and value:
            if current_agent in directives:
                directives[current_agent]["allow"].append(value)
        elif key == "crawl-delay":
            if current_agent in directives:
                directives[current_agent]["crawl_delay"] = value
        elif key == "sitemap":
            sitemaps.append(value)

    result["directives"] = directives
    result["sitemaps_found"] = sitemaps
    result["user_agents"] = list(directives.keys())

    # Issues
    if not sitemaps:
        result["issues"].append({
            "severity": "warning",
            "message": "No Sitemap directive found in robots.txt — add Sitemap: <url> to help discovery",
        })
        result["score"] -= 10

    wildcard = directives.get("*", {})
    if not wildcard.get("disallow") and not wildcard.get("allow"):
        result["issues"].append({
            "severity": "info",
            "message": "No explicit rules for User-agent: * — all paths are allowed by default",
        })

    # Check for overly broad disallow
    for agent, rules in directives.items():
        if "/" in rules.get("disallow", []):
            result["issues"].append({
                "severity": "critical",
                "message": f"User-agent: {agent} is fully blocked (Disallow: /) — search engines cannot crawl the site",
            })
            result["score"] -= 40

    result["score"] = max(0, result["score"])
    return result


# ──────────────────────────────────────────────
# 2. Sitemap Analysis
# ──────────────────────────────────────────────


def analyze_sitemap(url: str, sitemap_url: str = "") -> dict:
    """
    Fetch and analyze a sitemap.xml file.
    If no sitemap_url provided, tries /sitemap.xml.
    Returns URL counts, types, issues, and recommendations.
    """
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    base = f"{parsed.scheme}://{parsed.netloc}"

    if not sitemap_url:
        sitemap_url = f"{base}/sitemap.xml"

    result = {
        "url": sitemap_url,
        "found": False,
        "is_index": False,
        "total_urls": 0,
        "child_sitemaps": [],
        "url_entries": [],
        "issues": [],
        "score": 100,
    }

    try:
        resp = requests.get(sitemap_url, headers={"User-Agent": _random_ua()}, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            result["issues"].append({
                "severity": "critical",
                "message": "No sitemap.xml found — search engines rely on crawling to discover pages",
            })
            result["score"] = 40
            return result
        resp.raise_for_status()
        result["found"] = True
    except requests.RequestException as e:
        result["issues"].append({
            "severity": "warning",
            "message": f"Could not fetch sitemap: {e}",
        })
        return result

    content = resp.text
    is_xml = content.strip().startswith("<?xml") or "<urlset" in content or "<sitemapindex" in content

    if not is_xml:
        result["issues"].append({
            "severity": "warning",
            "message": "Sitemap does not appear to be valid XML",
        })
        result["score"] -= 10

    # Parse with built-in XML if available, else regex fallback
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
    except Exception:
        # Regex fallback
        import re
        urls = re.findall(r"<loc>(.*?)</loc>", content)
        result["total_urls"] = len(urls)
        result["url_entries"] = [{"loc": u} for u in urls[:50]]
        if not urls:
            result["issues"].append({
                "severity": "critical",
                "message": "Sitemap contains no URLs",
            })
            result["score"] -= 30
        return result

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    # Check if it's a sitemap index
    child_sitemaps = root.findall(".//sm:sitemap", ns)
    if child_sitemaps:
        result["is_index"] = True
        for child in child_sitemaps:
            loc = child.find("sm:loc", ns)
            if loc is not None and loc.text:
                result["child_sitemaps"].append(loc.text)
        result["total_urls"] = len(result["child_sitemaps"])
        if not result["child_sitemaps"]:
            result["issues"].append({
                "severity": "critical",
                "message": "Sitemap index contains no child sitemaps",
            })
            result["score"] -= 30
    else:
        # Regular sitemap
        url_entries = root.findall(".//sm:url", ns)
        result["total_urls"] = len(url_entries)

        for entry in url_entries[:50]:
            loc = entry.find("sm:loc", ns)
            lastmod = entry.find("sm:lastmod", ns)
            changefreq = entry.find("sm:changefreq", ns)
            priority = entry.find("sm:priority", ns)
            result["url_entries"].append({
                "loc": loc.text if loc is not None else "",
                "lastmod": lastmod.text if lastmod is not None else "",
                "changefreq": changefreq.text if changefreq is not None else "",
                "priority": priority.text if priority is not None else "",
            })

        if not url_entries:
            result["issues"].append({
                "severity": "critical",
                "message": "Sitemap contains no URLs",
            })
            result["score"] -= 30

        # Check for lastmod
        has_lastmod = any(e.get("lastmod") for e in result["url_entries"])
        if not has_lastmod:
            result["issues"].append({
                "severity": "info",
                "message": "No lastmod dates found — adding lastmod helps search engines prioritize fresh content",
            })
            result["score"] -= 5

    return result


# ──────────────────────────────────────────────
# 3. Structured Data (JSON-LD) Validation
# ──────────────────────────────────────────────


def analyze_structured_data(url: str) -> dict:
    """
    Fetch a page and validate all JSON-LD structured data blocks.
    Checks for required fields per schema type and common issues.
    """
    result = {
        "url": url,
        "schemas_found": 0,
        "schemas": [],
        "issues": [],
        "score": 100,
    }

    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["issues"].append({
            "severity": "critical",
            "message": f"Could not fetch page: {e}",
        })
        result["score"] = 0
        return result

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    # Find all JSON-LD script blocks
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    result["schemas_found"] = len(scripts)

    if not scripts:
        result["issues"].append({
            "severity": "warning",
            "message": "No structured data (JSON-LD) found on page — add schema.org markup for rich results",
        })
        result["score"] = 40
        return result

    for i, script in enumerate(scripts):
        raw = script.string or ""
        raw = raw.strip()
        if not raw:
            continue

        schema_info = {
            "index": i,
            "type": "unknown",
            "valid": True,
            "issues": [],
            "fields_present": [],
            "fields_missing": [],
        }

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            schema_info["valid"] = False
            schema_info["issues"].append(f"Invalid JSON: {e}")
            result["issues"].append({
                "severity": "critical",
                "message": f"Schema #{i + 1}: Invalid JSON — {e}",
            })
            result["score"] -= 15
            result["schemas"].append(schema_info)
            continue

        # Handle @graph wrapper
        items = [data]
        if isinstance(data, dict) and "@graph" in data:
            items = data["@graph"]
        elif isinstance(data, list):
            items = data

        for item in items:
            if not isinstance(item, dict):
                continue

            schema_type = item.get("@type", "unknown")
            schema_info["type"] = schema_type

            # Check @context
            if "@context" not in item:
                schema_info["issues"].append("Missing @context")
                schema_info["valid"] = False
                result["issues"].append({
                    "severity": "warning",
                    "message": f"Schema '{schema_type}': Missing @context property",
                })
                result["score"] -= 5

            # Check required fields per type
            required_fields = _get_required_fields(schema_type)
            optional_fields = _get_common_fields(schema_type)
            all_fields = required_fields + optional_fields

            for field in required_fields:
                if field in item and item[field]:
                    schema_info["fields_present"].append(field)
                else:
                    schema_info["fields_missing"].append(field)
                    schema_info["issues"].append(f"Missing required field: {field}")
                    result["issues"].append({
                        "severity": "warning",
                        "message": f"Schema '{schema_type}': Missing required field '{field}'",
                    })
                    result["score"] -= 5

            for field in optional_fields:
                if field in item and item[field]:
                    schema_info["fields_present"].append(field)

        result["schemas"].append(schema_info)

    result["score"] = max(0, result["score"])
    return result


def _get_required_fields(schema_type: str) -> list[str]:
    """Return required fields for common schema types."""
    requirements = {
        "Article": ["headline", "author"],
        "NewsArticle": ["headline", "author"],
        "BlogPosting": ["headline", "author"],
        "WebPage": ["name"],
        "WebSite": ["name"],
        "Organization": ["name"],
        "LocalBusiness": ["name", "address"],
        "Product": ["name"],
        "FAQPage": [],
        "HowTo": ["name"],
        "BreadcrumbList": ["itemListElement"],
    }
    return requirements.get(schema_type, [])


def _get_common_fields(schema_type: str) -> list[str]:
    """Return common recommended fields for schema types."""
    common = {
        "Article": ["datePublished", "dateModified", "image", "description", "publisher"],
        "NewsArticle": ["datePublished", "image", "description"],
        "BlogPosting": ["datePublished", "dateModified", "image"],
        "WebPage": ["description", "url", "image"],
        "WebSite": ["url", "potentialAction"],
        "Organization": ["url", "logo", "description"],
        "LocalBusiness": ["telephone", "openingHours", "geo"],
        "Product": ["description", "image", "offers", "brand"],
        "HowTo": ["step", "totalTime"],
        "BreadcrumbList": [],
    }
    return common.get(schema_type, [])


# ──────────────────────────────────────────────
# 4. Core Web Vitals (PageSpeed Insights)
# ──────────────────────────────────────────────


def get_core_web_vitals(url: str, strategy: str = "mobile") -> dict:
    """
    Fetch Core Web Vitals and performance metrics from Google PageSpeed Insights API.
    
    Args:
        url: The URL to analyze
        strategy: "mobile" or "desktop"
    
    Returns:
        dict with performance score, metrics (LCP, FID, CLS, FCP, TTFB, TBT, Speed Index),
        opportunities, and diagnostics.
    """
    from config import PAGESPEED_API_KEY

    result = {
        "url": url,
        "strategy": strategy,
        "performance_score": None,
        "metrics": {},
        "opportunities": [],
        "diagnostics": [],
        "issues": [],
        "score": 0,
    }

    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
    }
    if PAGESPEED_API_KEY:
        params["key"] = PAGESPEED_API_KEY

    try:
        resp = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params=params,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        result["issues"].append({
            "severity": "warning",
            "message": f"PageSpeed Insights API error: {e}",
        })
        result["score"] = 0
        return result
    except Exception as e:
        result["issues"].append({
            "severity": "warning",
            "message": f"Failed to parse PageSpeed response: {e}",
        })
        return result

    # Performance score
    lhr = data.get("lighthouseResult", {})
    categories = lhr.get("categories", {})
    perf = categories.get("performance", {})
    score = perf.get("score")
    if score is not None:
        result["performance_score"] = round(score * 100)
        result["score"] = round(score * 100)

    # Extract key metrics
    audits = lhr.get("audits", {})
    metric_keys = {
        "largest-contentful-paint": "lcp",
        "first-contentful-paint": "fcp",
        "cumulative-layout-shift": "cls",
        "total-blocking-time": "tbt",
        "speed-index": "speed_index",
        "interactive": "tti",
        "server-response-time": "ttfb",
        "max-potential-fid": "fid",
    }

    for audit_key, short_name in metric_keys.items():
        audit = audits.get(audit_key, {})
        if audit:
            result["metrics"][short_name] = {
                "value": audit.get("displayValue", ""),
                "numeric_value": audit.get("numericValue", 0),
                "score": audit.get("score", 0),
                "title": audit.get("title", ""),
            }

    # Opportunities (actionable improvements)
    for key, audit in audits.items():
        if audit.get("details", {}).get("type") == "opportunity" and audit.get("score") is not None and audit["score"] < 1:
            savings = audit.get("details", {}).get("overallSavingsMs", 0)
            result["opportunities"].append({
                "title": audit.get("title", ""),
                "description": audit.get("description", "")[:200],
                "savings_ms": round(savings),
                "score": audit.get("score", 0),
            })

    # Sort opportunities by savings
    result["opportunities"].sort(key=lambda x: x.get("savings_ms", 0), reverse=True)
    result["opportunities"] = result["opportunities"][:10]

    # Diagnostics (non-critical improvements)
    for key, audit in audits.items():
        if audit.get("details", {}).get("type") == "table" and audit.get("score") is not None and audit["score"] < 1:
            if key not in metric_keys:
                result["diagnostics"].append({
                    "title": audit.get("title", ""),
                    "description": audit.get("description", "")[:150],
                    "score": audit.get("score", 0),
                })

    result["diagnostics"] = result["diagnostics"][:10]

    # Generate issues from metrics
    lcp = result["metrics"].get("lcp", {})
    if lcp.get("numeric_value", 0) > 4000:
        result["issues"].append({
            "severity": "critical",
            "message": f"LCP is {lcp.get('value', '')} — aim for under 2.5 seconds",
        })
    elif lcp.get("numeric_value", 0) > 2500:
        result["issues"].append({
            "severity": "warning",
            "message": f"LCP is {lcp.get('value', '')} — aim for under 2.5 seconds",
        })

    cls = result["metrics"].get("cls", {})
    if cls.get("numeric_value", 0) > 0.25:
        result["issues"].append({
            "severity": "critical",
            "message": f"CLS is {cls.get('value', '')} — aim for under 0.1",
        })
    elif cls.get("numeric_value", 0) > 0.1:
        result["issues"].append({
            "severity": "warning",
            "message": f"CLS is {cls.get('value', '')} — aim for under 0.1",
        })

    tbt = result["metrics"].get("tbt", {})
    if tbt.get("numeric_value", 0) > 600:
        result["issues"].append({
            "severity": "critical",
            "message": f"Total Blocking Time is {tbt.get('value', '')} — aim for under 200ms",
        })
    elif tbt.get("numeric_value", 0) > 200:
        result["issues"].append({
            "severity": "warning",
            "message": f"Total Blocking Time is {tbt.get('value', '')} — aim for under 200ms",
        })

    return result


# ──────────────────────────────────────────────
# 5. Full Technical SEO Audit
# ──────────────────────────────────────────────


def full_technical_audit(url: str, include_web_vitals: bool = True) -> dict:
    """
    Run a complete technical SEO audit combining all checks:
    - robots.txt analysis
    - sitemap.xml analysis
    - Structured data validation
    - Core Web Vitals (optional)
    """
    result = {
        "url": url,
        "robots_txt": {},
        "sitemap": {},
        "structured_data": {},
        "core_web_vitals": {},
        "overall_score": 0,
        "total_issues": 0,
    }

    # Run all checks
    result["robots_txt"] = analyze_robots_txt(url)
    result["sitemap"] = analyze_sitemap(url)
    result["structured_data"] = analyze_structured_data(url)

    if include_web_vitals:
        result["core_web_vitals"] = get_core_web_vitals(url)

    # Calculate overall score (weighted average)
    scores = []
    weights = {
        "robots_txt": 0.15,
        "sitemap": 0.20,
        "structured_data": 0.25,
        "core_web_vitals": 0.40,
    }

    for key, weight in weights.items():
        section = result.get(key, {})
        if section:
            s = section.get("score", 0)
            if key == "core_web_vitals" and not include_web_vitals:
                continue
            scores.append((s, weight))

    if scores:
        total_weight = sum(w for _, w in scores)
        result["overall_score"] = round(sum(s * w for s, w in scores) / total_weight) if total_weight > 0 else 0

    # Count total issues
    for section_key in ["robots_txt", "sitemap", "structured_data", "core_web_vitals"]:
        section = result.get(section_key, {})
        result["total_issues"] += len(section.get("issues", []))

    return result
