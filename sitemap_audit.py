"""
Rankivo — Sitemap Audit Module
Analyzes XML sitemaps: validates format, counts URLs, checks lastmod,
detects sitemap indexes, validates against best practices.
"""
import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


# ──────────────────────────────────────────────
# Sitemap Discovery
# ──────────────────────────────────────────────

def discover_sitemaps(url: str) -> dict:
    """Discover sitemaps from robots.txt and common locations."""
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    base = f"{parsed.scheme}://{parsed.netloc}"

    sitemaps_found = []
    issues = []

    # 1. Check robots.txt for Sitemap directives
    robots_url = f"{base}/robots.txt"
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(robots_url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            for line in resp.text.split("\n"):
                line = line.strip()
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    if sitemap_url:
                        sitemaps_found.append({"url": sitemap_url, "source": "robots.txt"})
        else:
            issues.append({"severity": "warning", "message": "No robots.txt found"})
    except Exception as e:
        issues.append({"severity": "warning", "message": f"Could not fetch robots.txt: {e}"})

    # 2. Check common sitemap locations
    common_paths = [
        "/sitemap.xml",
        "/sitemap_index.xml",
        "/sitemap-index.xml",
        "/sitemap/",
        "/sitemaps.xml",
    ]

    for path in common_paths:
        sitemap_url = f"{base}{path}"
        already_found = any(s["url"] == sitemap_url for s in sitemaps_found)
        if already_found:
            continue
        try:
            headers = {"User-Agent": _random_ua()}
            resp = requests.head(sitemap_url, headers=headers, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                ct = resp.headers.get("content-type", "")
                if "xml" in ct or "text" in ct:
                    sitemaps_found.append({"url": sitemap_url, "source": "common-location"})
                    break  # Found one, stop checking
        except Exception:
            continue

    # 3. Check HTML for sitemap link
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(base, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        if resp.status_code == 200:
            html = resp.text.lower()
            if "sitemap" in html:
                # Try to find sitemap URL in HTML
                match = re.search(r'href=["\']([^"\']*sitemap[^"\']*\.xml)["\']', html, re.I)
                if match:
                    sm_url = match.group(1)
                    if not sm_url.startswith("http"):
                        sm_url = base + sm_url
                    already_found = any(s["url"] == sm_url for s in sitemaps_found)
                    if not already_found:
                        sitemaps_found.append({"url": sm_url, "source": "html-link"})
    except Exception:
        pass

    if not sitemaps_found:
        issues.append({"severity": "critical", "message": "No sitemaps found anywhere"})

    return {"sitemaps": sitemaps_found, "issues": issues}


# ──────────────────────────────────────────────
# Sitemap Parsing & Validation
# ──────────────────────────────────────────────

def _parse_sitemap_index(content: str) -> dict:
    """Parse a sitemap index file."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {"valid": False, "error": f"Invalid XML: {e}"}

    child_sitemaps = root.findall(".//sm:sitemap", SITEMAP_NS)
    entries = []
    for child in child_sitemaps:
        loc = child.find("sm:loc", SITEMAP_NS)
        lastmod = child.find("sm:lastmod", SITEMAP_NS)
        entries.append({
            "loc": loc.text if loc is not None else "",
            "lastmod": lastmod.text if lastmod is not None else "",
        })

    return {
        "valid": True,
        "is_index": True,
        "child_count": len(entries),
        "entries": entries,
    }


def _parse_sitemap(content: str) -> dict:
    """Parse a regular sitemap file."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {"valid": False, "error": f"Invalid XML: {e}"}

    # Check if it's actually a sitemap index
    child_sitemaps = root.findall(".//sm:sitemap", SITEMAP_NS)
    if child_sitemaps:
        return _parse_sitemap_index(content)

    url_entries = root.findall(".//sm:url", SITEMAP_NS)
    entries = []
    for entry in url_entries:
        loc = entry.find("sm:loc", SITEMAP_NS)
        lastmod = entry.find("sm:lastmod", SITEMAP_NS)
        changefreq = entry.find("sm:changefreq", SITEMAP_NS)
        priority = entry.find("sm:priority", SITEMAP_NS)

        entries.append({
            "loc": loc.text if loc is not None else "",
            "lastmod": lastmod.text if lastmod is not None else "",
            "changefreq": changefreq.text if changefreq is not None else "",
            "priority": priority.text if priority is not None else "",
        })

    return {
        "valid": True,
        "is_index": False,
        "url_count": len(entries),
        "entries": entries,
    }


def _validate_sitemap_urls(entries: list[dict], base_domain: str) -> dict:
    """Validate URLs within a sitemap."""
    issues = []
    internal = 0
    external = 0
    malformed = 0
    duplicate_locs = set()
    all_locs = []

    for entry in entries:
        loc = entry.get("loc", "")
        if not loc:
            issues.append({"severity": "warning", "message": "Entry with empty <loc> found"})
            malformed += 1
            continue

        all_locs.append(loc)

        # Check for duplicates
        if loc in duplicate_locs:
            issues.append({"severity": "warning", "message": f"Duplicate URL: {loc[:80]}"})
        duplicate_locs.add(loc)

        # Check if URL belongs to the same domain
        try:
            parsed = urlparse(loc)
            if parsed.netloc and parsed.netloc != base_domain:
                external += 1
            else:
                internal += 1
        except Exception:
            malformed += 1

        # Check for HTTP URLs (should be HTTPS)
        if loc.startswith("http://"):
            issues.append({"severity": "warning", "message": f"HTTP URL found (should be HTTPS): {loc[:80]}"})

        # Check lastmod format
        lastmod = entry.get("lastmod", "")
        if lastmod:
            # ISO 8601 check (basic)
            if not re.match(r'\d{4}-\d{2}-\d{2}', lastmod):
                issues.append({"severity": "info", "message": f"Non-standard lastmod format: {lastmod}"})

        # Check changefreq validity
        changefreq = entry.get("changefreq", "")
        if changefreq:
            valid_freqs = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
            if changefreq.lower() not in valid_freqs:
                issues.append({"severity": "info", "message": f"Invalid changefreq: {changefreq}"})

        # Check priority range
        priority = entry.get("priority", "")
        if priority:
            try:
                p = float(priority)
                if p < 0 or p > 1:
                    issues.append({"severity": "info", "message": f"Priority out of range (0-1): {priority}"})
            except ValueError:
                issues.append({"severity": "info", "message": f"Invalid priority value: {priority}"})

    return {
        "total": len(entries),
        "internal": internal,
        "external": external,
        "malformed": malformed,
        "duplicates": len(duplicate_locs) < len(all_locs),
        "issues": issues,
    }


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_sitemap(url: str) -> dict:
    """
    Full sitemap audit for a URL.
    Discovers sitemaps, parses them, validates URLs, and checks best practices.
    """
    result = {
        "url": url,
        "sitemaps_found": [],
        "sitemap_details": [],
        "total_urls": 0,
        "issues": [],
        "recommendations": [],
        "score": 100,
    }

    # Step 1: Discover sitemaps
    discovery = discover_sitemaps(url)
    result["sitemaps_found"] = discovery["sitemaps"]
    result["issues"].extend(discovery["issues"])

    if not discovery["sitemaps"]:
        result["score"] = 20
        result["recommendations"].append(
            "Create an XML sitemap and add it to robots.txt with: Sitemap: https://yoursite.com/sitemap.xml"
        )
        return result

    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    base_domain = parsed.netloc

    # Step 2: Fetch and parse each sitemap
    for sm_info in discovery["sitemaps"]:
        sm_url = sm_info["url"]
        detail = {"url": sm_url, "source": sm_info.get("source", "")}

        try:
            headers = {"User-Agent": _random_ua()}
            resp = requests.get(sm_url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            content = resp.text

            # Check if XML
            if not content.strip().startswith("<?xml") and "<urlset" not in content and "<sitemapindex" not in content:
                detail["valid"] = False
                detail["error"] = "Not a valid XML sitemap"
                result["issues"].append({"severity": "critical", "message": f"{sm_url} is not valid XML"})
                result["score"] -= 15
                result["sitemap_details"].append(detail)
                continue

            # Parse
            parsed_sm = _parse_sitemap(content)
            detail.update(parsed_sm)

            if not parsed_sm.get("valid"):
                result["issues"].append({"severity": "critical", "message": f"XML parse error in {sm_url}: {parsed_sm.get('error', '')}"})
                result["score"] -= 15
                result["sitemap_details"].append(detail)
                continue

            # If it's an index, recursively fetch children
            if parsed_sm.get("is_index"):
                detail["children_fetched"] = 0
                child_entries = parsed_sm.get("entries", [])
                all_url_entries = []

                for child in child_entries[:50]:  # Limit to 50 child sitemaps
                    child_url = child.get("loc", "")
                    if not child_url:
                        continue
                    try:
                        child_resp = requests.get(child_url, headers=headers, timeout=REQUEST_TIMEOUT)
                        child_resp.raise_for_status()
                        child_parsed = _parse_sitemap(child_resp.text)
                        if child_parsed.get("valid") and not child_parsed.get("is_index"):
                            all_url_entries.extend(child_parsed.get("entries", []))
                            detail["children_fetched"] += 1
                    except Exception:
                        continue

                # Validate all URLs from child sitemaps
                url_validation = _validate_sitemap_urls(all_url_entries, base_domain)
                detail["url_validation"] = url_validation
                result["total_urls"] += url_validation["total"]
                result["issues"].extend(url_validation["issues"])

            else:
                # Regular sitemap
                entries = parsed_sm.get("entries", [])
                url_validation = _validate_sitemap_urls(entries, base_domain)
                detail["url_validation"] = url_validation
                result["total_urls"] += url_validation["total"]
                result["issues"].extend(url_validation["issues"])

            # Check sitemap size limits
            url_count = parsed_sm.get("url_count", parsed_sm.get("child_count", 0))
            if url_count > 50000:
                result["issues"].append({
                    "severity": "warning",
                    "message": f"Sitemap has {url_count} URLs — Google recommends max 50,000 per sitemap"
                })
                result["score"] -= 10

            # Check for deprecated tags
            if "<priority>" in content:
                result["issues"].append({
                    "severity": "info",
                    "message": "Sitemap uses <priority> tag — Google ignores this tag"
                })
            if "<changefreq>" in content:
                result["issues"].append({
                    "severity": "info",
                    "message": "Sitemap uses <changefreq> tag — Google largely ignores this tag"
                })

        except requests.RequestException as e:
            detail["valid"] = False
            detail["error"] = str(e)
            result["issues"].append({"severity": "critical", "message": f"Could not fetch {sm_url}: {e}"})
            result["score"] -= 15

        result["sitemap_details"].append(detail)

    # Score adjustments
    if result["total_urls"] == 0:
        result["score"] = max(result["score"] - 20, 0)

    # Check for lastmod coverage
    has_lastmod = any(
        entry.get("lastmod")
        for detail in result["sitemap_details"]
        for entry in detail.get("entries", [])
    )
    if not has_lastmod and result["total_urls"] > 0:
        result["issues"].append({
            "severity": "info",
            "message": "No lastmod dates found — adding lastmod helps search engines prioritize fresh content"
        })

    # Recommendations
    if result["total_urls"] > 0:
        result["recommendations"].append("Submit sitemap to Google Search Console and Bing Webmaster Tools")
    if result["total_urls"] > 50000:
        result["recommendations"].append("Split large sitemaps into multiple files under 50,000 URLs each")
    if not has_lastmod:
        result["recommendations"].append("Add lastmod dates to help crawlers prioritize fresh content")

    result["score"] = max(0, min(100, result["score"]))
    return result
