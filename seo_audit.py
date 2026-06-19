"""
SEO AI Tools - SEO Audit Module
Analyzes a URL for meta tags, headings, word count, keyword density, links, and images.
"""
import requests
import re
from urllib.parse import urlparse, urljoin
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


def audit_url(url: str, focus_keyword: str = "") -> dict:
    """
    Perform a full SEO audit on a given URL.
    Returns a dict with all audit data.
    """
    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch URL: {e}", "url": url}

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(resp.text, "lxml")
    final_url = resp.url

    result = {
        "url": url,
        "final_url": final_url,
        "status_code": resp.status_code,
        "redirected": url != final_url,
        "page_title": _get_title(soup),
        "meta_description": _get_meta_description(soup),
        "meta_keywords": _get_meta_keywords(soup),
        "canonical": _get_canonical(soup),
        "og_tags": _get_og_tags(soup),
        "headings": _get_headings(soup),
        "word_count": _get_word_count(soup),
        "text_to_html_ratio": _get_text_ratio(resp.text, soup),
        "links": _analyze_links(soup, final_url),
        "images": _analyze_images(soup, final_url),
        "keyword_analysis": {},
        "issues": [],
        "score": 0,
    }

    # Keyword analysis
    body_text = _get_body_text(soup)
    if focus_keyword.strip():
        result["keyword_analysis"] = _analyze_keyword(body_text, focus_keyword.strip())

    # Generate issues and score
    result["issues"] = _generate_issues(result)
    result["score"] = _calculate_score(result)

    return result


# ──────────────────────────────────────────────
# Meta Tag Extraction
# ──────────────────────────────────────────────


def _get_title(soup) -> str:
    tag = soup.find("title")
    return tag.get_text(strip=True) if tag else ""


def _get_meta_description(soup) -> str:
    tag = soup.find("meta", attrs={"name": "description"})
    return tag.get("content", "").strip() if tag else ""


def _get_meta_keywords(soup) -> str:
    tag = soup.find("meta", attrs={"name": "keywords"})
    return tag.get("content", "").strip() if tag else ""


def _get_canonical(soup) -> str:
    tag = soup.find("link", attrs={"rel": "canonical"})
    return tag.get("href", "") if tag else ""


def _get_og_tags(soup) -> dict:
    og = {}
    for tag in soup.find_all("meta", attrs={"property": re.compile(r"^og:")}):
        prop = tag.get("property", "")
        content = tag.get("content", "")
        if prop and content:
            og[prop] = content
    return og


# ──────────────────────────────────────────────
# Heading Hierarchy
# ──────────────────────────────────────────────


def _get_headings(soup) -> dict:
    headings = {}
    for level in range(1, 7):
        tag = f"h{level}"
        elements = soup.find_all(tag)
        headings[tag] = [el.get_text(strip=True) for el in elements]
    return headings


# ──────────────────────────────────────────────
# Content Analysis
# ──────────────────────────────────────────────


def _get_body_text(soup) -> str:
    # Remove scripts and styles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def _get_word_count(soup) -> int:
    text = _get_body_text(soup)
    words = text.split()
    return len(words)


def _get_text_ratio(html: str, soup) -> float:
    body_text = _get_body_text(soup)
    if not html:
        return 0.0
    return round(len(body_text) / len(html) * 100, 1)


# ──────────────────────────────────────────────
# Link Analysis
# ──────────────────────────────────────────────


def _analyze_links(soup, base_url: str) -> dict:
    parsed_base = urlparse(base_url)
    internal = []
    external = []
    nofollow = 0

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        is_internal = parsed.netloc == "" or parsed.netloc == parsed_base.netloc

        rel = a.get("rel", [])
        if "nofollow" in rel:
            nofollow += 1

        link_info = {
            "url": full_url,
            "text": a.get_text(strip=True)[:100],
            "nofollow": "nofollow" in rel,
        }

        if is_internal:
            internal.append(link_info)
        else:
            external.append(link_info)

    return {
        "internal_count": len(internal),
        "external_count": len(external),
        "nofollow_count": nofollow,
        "internal": internal[:20],  # limit for display
        "external": external[:20],
    }


# ──────────────────────────────────────────────
# Image Analysis
# ──────────────────────────────────────────────


def _analyze_images(soup, base_url: str) -> dict:
    images = soup.find_all("img")
    total = len(images)
    with_alt = sum(1 for img in images if img.get("alt", "").strip())
    without_alt = total - with_alt

    details = []
    for img in images[:20]:
        details.append({
            "src": urljoin(base_url, img.get("src", "")),
            "alt": img.get("alt", ""),
            "has_alt": bool(img.get("alt", "").strip()),
            "width": img.get("width", ""),
            "height": img.get("height", ""),
        })

    return {
        "total": total,
        "with_alt": with_alt,
        "without_alt": without_alt,
        "alt_coverage": round(with_alt / total * 100, 1) if total > 0 else 100.0,
        "details": details,
    }


# ──────────────────────────────────────────────
# Keyword Density Analysis
# ──────────────────────────────────────────────


def _analyze_keyword(text: str, keyword: str) -> dict:
    text_lower = text.lower()
    kw_lower = keyword.lower()
    words = text_lower.split()
    total_words = len(words)

    # Exact match count
    exact_count = text_lower.count(kw_lower)
    exact_density = round(exact_count / total_words * 100, 2) if total_words > 0 else 0

    # Word-level density
    kw_words = kw_lower.split()
    kw_len = len(kw_words)
    if kw_len == 1:
        phrase_count = words.count(kw_lower)
    else:
        phrase_count = sum(
            1 for i in range(len(words) - kw_len + 1)
            if " ".join(words[i : i + kw_len]) == kw_lower
        )

    phrase_density = round(phrase_count / total_words * 100, 2) if total_words > 0 else 0

    # Find first occurrence position
    first_pos = text_lower.find(kw_lower)
    first_position_pct = round(first_pos / len(text_lower) * 100, 1) if first_pos >= 0 and text_lower else -1

    return {
        "keyword": keyword,
        "exact_matches": exact_count,
        "exact_density_pct": exact_density,
        "phrase_matches": phrase_count,
        "phrase_density_pct": phrase_density,
        "first_position_pct": first_position_pct,
        "in_title": False,  # filled by caller
        "in_headings": False,  # filled by caller
    }


# ──────────────────────────────────────────────
# Issue Detection & Scoring
# ──────────────────────────────────────────────


def _generate_issues(data: dict) -> list[dict]:
    issues = []

    def _add(severity: str, category: str, message: str):
        issues.append({"severity": severity, "category": category, "message": message})

    # Title
    title = data["page_title"]
    if not title:
        _add("critical", "title", "Missing page title")
    elif len(title) < 30:
        _add("warning", "title", f"Title too short ({len(title)} chars) — aim for 50-60")
    elif len(title) > 60:
        _add("warning", "title", f"Title too long ({len(title)} chars) — aim for 50-60")

    # Meta description
    desc = data["meta_description"]
    if not desc:
        _add("critical", "meta", "Missing meta description")
    elif len(desc) < 120:
        _add("warning", "meta", f"Meta description too short ({len(desc)} chars) — aim for 150-160")
    elif len(desc) > 160:
        _add("warning", "meta", f"Meta description too long ({len(desc)} chars) — aim for 150-160")

    # Headings
    h1s = data["headings"].get("h1", [])
    if len(h1s) == 0:
        _add("critical", "headings", "Missing H1 tag")
    elif len(h1s) > 1:
        _add("warning", "headings", f"Multiple H1 tags ({len(h1s)}) — use only one")

    # Word count
    wc = data["word_count"]
    if wc < 300:
        _add("warning", "content", f"Very thin content ({wc} words) — aim for 1000+")
    elif wc < 800:
        _add("info", "content", f"Content could be longer ({wc} words) — aim for 1000+")

    # Text to HTML ratio
    ratio = data["text_to_html_ratio"]
    if ratio < 10:
        _add("warning", "content", f"Low text-to-HTML ratio ({ratio}%) — page may be too code-heavy")

    # Canonical
    if not data["canonical"]:
        _add("info", "technical", "Missing canonical tag")

    # Images
    img = data["images"]
    if img["total"] == 0:
        _add("info", "content", "No images found — visual content improves engagement")
    elif img["without_alt"] > 0:
        _add("warning", "images", f"{img['without_alt']} image(s) missing alt text")

    # Links
    links = data["links"]
    if links["internal_count"] == 0 and links["external_count"] == 0:
        _add("info", "links", "No links found on page")
    elif links["nofollow_count"] > links["internal_count"]:
        _add("warning", "links", "More nofollow links than followed — check link strategy")

    # Keyword analysis
    ka = data.get("keyword_analysis", {})
    if ka and ka.get("keyword"):
        if ka["exact_density_pct"] == 0:
            _add("warning", "keyword", f"Target keyword '{ka['keyword']}' not found in body text")
        elif ka["exact_density_pct"] > 3.0:
            _add("warning", "keyword", f"Keyword density too high ({ka['exact_density_pct']}%) — risk of keyword stuffing")
        elif ka["exact_density_pct"] > 2.5:
            _add("info", "keyword", f"Keyword density is high ({ka['exact_density_pct']}%) — consider reducing")

    return issues


def _calculate_score(data: dict) -> int:
    """Calculate an SEO score from 0-100."""
    score = 100
    issues = data.get("issues", [])

    for issue in issues:
        if issue["severity"] == "critical":
            score -= 15
        elif issue["severity"] == "warning":
            score -= 7
        elif issue["severity"] == "info":
            score -= 2

    return max(0, min(100, score))
