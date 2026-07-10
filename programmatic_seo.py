"""
Rankivo — Programmatic SEO Analysis Module
Analyzes pages generated at scale: URL patterns, thin content detection,
template analysis, index bloat, and internal linking patterns.
"""
import re
import requests
from urllib.parse import urlparse, urljoin
from config import REQUEST_TIMEOUT, USER_AGENTS, _safe_print
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# URL Pattern Analysis
# ──────────────────────────────────────────────

def _analyze_url_patterns(urls: list[str]) -> dict:
    """Analyze URL patterns for programmatic SEO detection."""
    if not urls:
        return {"patterns": [], "is_programmatic": False}

    parsed_urls = []
    for url in urls:
        try:
            p = urlparse(url)
            segments = [s for s in p.path.split("/") if s]
            parsed_urls.append({
                "url": url,
                "path": p.path,
                "segments": segments,
                "depth": len(segments),
            })
        except Exception:
            continue

    if not parsed_urls:
        return {"patterns": [], "is_programmatic": False}

    # Find common URL structures
    segment_patterns = {}
    for pu in parsed_urls:
        if len(pu["segments"]) >= 2:
            # Use the second-to-last segment as a pattern indicator
            pattern_key = "/".join(pu["segments"][:-1])
            if pattern_key not in segment_patterns:
                segment_patterns[pattern_key] = []
            segment_patterns[pattern_key].append(pu)

    # Detect programmatic patterns (many pages under same structure)
    programmatic_patterns = []
    for pattern, pages in segment_patterns.items():
        if len(pages) >= 5:
            programmatic_patterns.append({
                "pattern": f"/{pattern}/[slug]",
                "count": len(pages),
                "examples": [p["url"][:80] for p in pages[:3]],
            })

    is_programmatic = len(programmatic_patterns) > 0

    return {
        "total_urls": len(parsed_urls),
        "avg_depth": round(sum(p["depth"] for p in parsed_urls) / max(len(parsed_urls), 1), 1),
        "patterns": programmatic_patterns,
        "is_programmatic": is_programmatic,
    }


# ──────────────────────────────────────────────
# Thin Content Detection
# ──────────────────────────────────────────────

def _check_thin_content(url: str) -> dict:
    """Check a single page for thin content."""
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")

        # Remove boilerplate
        for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            tag.decompose()

        body_text = soup.get_text(separator=" ", strip=True)
        words = body_text.split()
        wc = len(words)

        # Check for duplicate/template content indicators
        has_unique_content = wc > 300
        has_meaningful_headings = len(soup.find_all("h2")) >= 2

        return {
            "url": url[:120],
            "word_count": wc,
            "has_unique_content": has_unique_content,
            "has_meaningful_headings": has_meaningful_headings,
            "is_thin": wc < 200,
            "is_suspiciously_similar": False,  # Would need comparison
        }
    except Exception as e:
        return {
            "url": url[:120],
            "error": str(e),
            "is_thin": True,
        }


# ──────────────────────────────────────────────
# Index Bloat Detection
# ──────────────────────────────────────────────

def _check_index_bloat(soup, body_text: str) -> dict:
    """Check for index bloat signals."""
    issues = []

    # Check for noindex
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    if robots_meta:
        content = robots_meta.get("content", "").lower()
        if "noindex" in content:
            issues.append("Page has noindex tag")

    # Check for canonical
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if not canonical:
        issues.append("Missing canonical tag — potential duplicate content")

    # Check for pagination signals
    if re.search(r'(?:page|page_num|p=\d+|\?page=)', body_text[:500]):
        issues.append("Pagination detected — ensure proper canonical and rel=prev/next")

    # Check for faceted navigation indicators
    faceted_patterns = [
        r'(?:filter|sort|color|size|brand|price_range)=',
        r'\?(?:ref|src|utm)=',
    ]
    for pattern in faceted_patterns:
        if re.search(pattern, body_text[:1000]):
            issues.append("Faceted navigation signals detected — ensure proper crawl directives")
            break

    return {
        "issues": issues,
        "has_noindex": "noindex" in (robots_meta.get("content", "") if robots_meta else ""),
        "has_canonical": canonical is not None,
    }


# ──────────────────────────────────────────────
# Template Analysis
# ──────────────────────────────────────────────

def _analyze_template(url: str) -> dict:
    """Analyze page template structure."""
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")

        # Template structure
        structure = {
            "has_header": bool(soup.find("header")),
            "has_nav": bool(soup.find("nav")),
            "has_main": bool(soup.find("main")),
            "has_article": bool(soup.find("article")),
            "has_footer": bool(soup.find("footer")),
            "has_sidebar": bool(soup.find("aside") or soup.find(attrs={"class": re.compile(r"sidebar", re.I)})),
        }

        # Unique content area
        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main:
            for tag in main(["script", "style", "noscript"]):
                tag.decompose()
            main_text = main.get_text(separator=" ", strip=True)
            unique_word_count = len(main_text.split())
        else:
            unique_word_count = 0

        structure["unique_word_count"] = unique_word_count
        structure["template_score"] = sum(1 for v in structure.values() if v) / 7 * 100

        return structure
    except Exception:
        return {"error": "Could not analyze template"}


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_programmatic_seo(url: str, sample_urls: list[str] = None) -> dict:
    """
    Programmatic SEO analysis for a URL or set of URLs.
    Detects URL patterns, thin content, index bloat, and template issues.
    """
    result = {
        "url": url,
        "url_patterns": {},
        "thin_content_check": {},
        "index_bloat_check": {},
        "template_analysis": {},
        "issues": [],
        "recommendations": [],
        "score": 100,
    }

    # Analyze URL patterns if sample URLs provided
    urls_to_check = sample_urls or [url]
    result["url_patterns"] = _analyze_url_patterns(urls_to_check)

    # Check the main URL for thin content
    result["thin_content_check"] = _check_thin_content(url)

    # Analyze template
    result["template_analysis"] = _analyze_template(url)

    # Fetch page for index bloat check
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        body_text = soup.get_text(separator=" ", strip=True)

        result["index_bloat_check"] = _check_index_bloat(soup, body_text)
    except Exception:
        pass

    # Generate issues
    score = 100

    if result["thin_content_check"].get("is_thin"):
        result["issues"].append({
            "severity": "critical",
            "message": f"Thin content detected ({result['thin_content_check'].get('word_count', 0)} words) — aim for 300+ unique words",
        })
        score -= 20

    for issue in result["index_bloat_check"].get("issues", []):
        result["issues"].append({"severity": "warning", "message": issue})
        score -= 5

    if result["url_patterns"].get("is_programmatic"):
        count = len(result["url_patterns"].get("patterns", []))
        result["issues"].append({
            "severity": "info",
            "message": f"Programmatic patterns detected ({count} patterns) — ensure unique content per page",
        })
        score -= 5

    # Generate recommendations
    if result["thin_content_check"].get("is_thin"):
        result["recommendations"].append(
            "Add unique content (300+ words) to each programmatically generated page"
        )
    if not result["index_bloat_check"].get("has_canonical"):
        result["recommendations"].append(
            "Add self-referencing canonical tags to prevent duplicate content issues"
        )
    if result["url_patterns"].get("is_programmatic"):
        result["recommendations"].extend([
            "Use dynamic unique content blocks (reviews, descriptions, FAQs) per page",
            "Add noindex to low-value parameter pages (filters, sorts)",
            "Implement proper internal linking between related programmatic pages",
        ])

    result["score"] = max(0, min(100, score))
    return result
