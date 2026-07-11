"""
SEO AI Tools - SEO Audit Module
Analyzes a URL for meta tags, headings, word count, keyword density, links, and images.
"""
import requests
import re
from urllib.parse import urlparse, urljoin
from config import REQUEST_TIMEOUT, USER_AGENTS, random_ua
import random




PAGE_TYPES = {
    "homepage": {
        "label": "Homepage / Main Page",
        "icon": "🏠",
        "description": "Brand authority, navigation, broad keyword targeting, internal linking hub",
    },
    "product": {
        "label": "Product / Service Page",
        "icon": "🛒",
        "description": "Conversion-focused, unique descriptions, structured data, transactional intent",
    },
    "blog": {
        "label": "Blog / Article Page",
        "icon": "📝",
        "description": "Engagement, E-E-A-T, search intent alignment, content depth",
    },
    "generic": {
        "label": "General Page",
        "icon": "📄",
        "description": "Standard SEO checks for any page type",
    },
}


def auto_detect_page_type(url: str) -> str:
    """
    Auto-detect page type from URL patterns.
    Returns one of 'homepage', 'product', 'blog', 'generic'.
    """
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    path = parsed.path.lower().rstrip("/")

    # Homepage: root or empty path
    if not path or path == "/":
        return "homepage"

    # Blog patterns
    blog_patterns = ["/blog", "/post", "/article", "/news", "/resource",
                     "/guide", "/tutorial", "/how-to", "/tips"]
    if any(p in path for p in blog_patterns):
        return "blog"

    # Product patterns
    product_patterns = ["/product", "/item", "/shop", "/buy", "/store",
                        "/p/", "/dp/", "/collection", "/category",
                        "/service", "/pricing", "/plan"]
    if any(p in path for p in product_patterns):
        return "product"

    # Page segments count heuristic: deep paths likely product/detail pages
    segments = [s for s in path.split("/") if s]
    if len(segments) >= 3:
        return "product"

    return "generic"


def audit_url(url: str, focus_keyword: str = "", page_type: str = "generic") -> dict:
    """
    Perform a full SEO audit on a given URL.
    Args:
        url: The URL to audit.
        focus_keyword: Optional target keyword for density analysis.
        page_type: One of 'homepage', 'product', 'blog', 'generic', or 'auto'.
    Returns a dict with all audit data.
    """
    # Auto-detect page type if requested
    detected = None
    if page_type == "auto":
        detected = auto_detect_page_type(url)
        page_type = detected

    # Ensure URL has a scheme
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        headers = {"User-Agent": random_ua()}
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
        "page_type": page_type,
        "page_type_auto_detected": detected is not None,
        "page_type_info": PAGE_TYPES.get(page_type, PAGE_TYPES["generic"]),
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
    result["issues"] = _generate_issues(result, page_type)
    result["score"] = _calculate_score(result, page_type)
    result["page_type_insights"] = _generate_page_type_insights(result, page_type)

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


def _generate_issues(data: dict, page_type: str = "generic") -> list[dict]:
    issues = []

    def _add(severity: str, category: str, message: str):
        issues.append({"severity": severity, "category": category, "message": message})

    # ── Universal checks ──
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

    # ── Page-type-specific checks ──
    if page_type == "homepage":
        _generate_homepage_issues(data, _add)
    elif page_type == "product":
        _generate_product_issues(data, _add)
    elif page_type == "blog":
        _generate_blog_issues(data, _add)

    return issues


# ──────────────────────────────────────────────
# Homepage-Specific Issues
# ──────────────────────────────────────────────

def _generate_homepage_issues(data: dict, _add) -> None:
    """Homepage: brand authority, navigation, internal linking hub."""
    wc = data["word_count"]
    links = data["links"]
    headings = data["headings"]
    title = (data["page_title"] or "").lower()

    # Internal linking is critical for homepages
    if links["internal_count"] < 5:
        _add("critical", "links", f"Homepage has only {links['internal_count']} internal links — aim for 10+ to key pages")
    elif links["internal_count"] < 10:
        _add("warning", "links", f"Homepage has {links['internal_count']} internal links — add links to key categories and pages")

    # Brand name in title
    if title and not any(w in title for w in ["|", "-", "—", ":"]):
        _add("info", "title", "Consider adding a separator and brand name to the title (e.g. 'Keyword | Brand')")

    # Heading hierarchy for navigation
    h2s = headings.get("h2", [])
    h3s = headings.get("h3", [])
    if len(h2s) < 2:
        _add("info", "headings", "Homepage should use H2s for main sections (e.g. Services, Features, About)")

    # Word count — homepages are typically lighter
    if wc > 0 and wc < 100:
        _add("warning", "content", f"Homepage has very little text ({wc} words) — add brand value proposition and key messaging")

    # OG tags for social sharing
    og = data.get("og_tags", {})
    if not og.get("og:title"):
        _add("info", "social", "Missing Open Graph tags — add og:title, og:description, og:image for social sharing")

    # Schema/structured data hint
    if links["internal_count"] == 0:
        _add("warning", "technical", "Homepage should link to main category/product pages for proper crawl hierarchy")


# ──────────────────────────────────────────────
# Product Page-Specific Issues
# ──────────────────────────────────────────────

def _generate_product_issues(data: dict, _add) -> None:
    """Product page: conversion, unique descriptions, structured data, transactional."""
    wc = data["word_count"]
    links = data["links"]
    img = data["images"]
    ka = data.get("keyword_analysis", {})
    title = (data["page_title"] or "").lower()
    desc = (data["meta_description"] or "").lower()

    # Product descriptions should be substantial
    if wc < 150:
        _add("critical", "content", f"Product description too thin ({wc} words) — aim for 300-500+ words of unique copy")
    elif wc < 300:
        _add("warning", "content", f"Product description is light ({wc} words) — add benefits, use cases, and specifications")

    # Images are critical for products
    if img["total"] == 0:
        _add("critical", "images", "Product page has no images — add high-quality product photos from multiple angles")
    elif img["total"] == 1:
        _add("warning", "images", "Only 1 image on product page — add multiple angles, lifestyle shots, and detail images")
    elif img["total"] < 3:
        _add("info", "images", f"Only {img['total']} images — consider adding more product views and detail shots")

    # Alt text on product images
    if img["without_alt"] > 0:
        _add("warning", "images", f"{img['without_alt']} product images missing alt text — include product name and features")

    # Transactional signals in title/description
    transactional_words = ["buy", "price", "shop", "order", "deal", "best", "top", "review", "compare"]
    if ka and ka.get("keyword"):
        kw = ka["keyword"].lower()
        if not any(w in kw for w in transactional_words):
            _add("info", "keyword", "Consider targeting a transactional keyword (e.g. 'buy X', 'best X', 'X review')")

    # Price/buy signals in meta description
    if desc and not any(w in desc for w in ["price", "buy", "shop", "order", "free", "discount", "deal"]):
        _add("info", "meta", "Product meta description should include a CTA (buy, shop, compare) or price point")

    # Internal linking to related products
    if links["internal_count"] < 2:
        _add("info", "links", "Add links to related products, categories, or comparison pages")

    # Canonical — critical for product variants
    if not data["canonical"]:
        _add("warning", "technical", "Missing canonical tag — critical for product pages to avoid duplicate content from variants")

    # Word count upper bound — product pages shouldn't be essays
    if wc > 2000:
        _add("info", "content", f"Product page is very long ({wc} words) — consider moving detailed specs to a separate section")


# ──────────────────────────────────────────────
# Blog Page-Specific Issues
# ──────────────────────────────────────────────

def _generate_blog_issues(data: dict, _add) -> None:
    """Blog: engagement, E-E-A-T, search intent, content depth, featured snippets."""
    wc = data["word_count"]
    headings = data["headings"]
    links = data["links"]
    img = data["images"]
    ratio = data["text_to_html_ratio"]

    # Content depth — blog posts need substance
    if wc < 300:
        _add("critical", "content", f"Blog post too short ({wc} words) — aim for 1000-2000 words for comprehensive coverage")
    elif wc < 800:
        _add("warning", "content", f"Blog post could be longer ({wc} words) — aim for 1000-2000 words")
    elif wc > 5000:
        _add("info", "content", f"Very long post ({wc} words) — consider splitting into a series or adding a table of contents")

    # Heading structure — H2s/H3s for scanability and featured snippets
    h2s = headings.get("h2", [])
    h3s = headings.get("h3", [])
    if len(h2s) == 0:
        _add("critical", "headings", "No H2 subheadings — blog posts need clear section structure for readability and featured snippets")
    elif len(h2s) < 3 and wc > 500:
        _add("warning", "headings", f"Only {len(h2s)} H2 subheadings — add more sections to improve scanability")
    if wc > 1000 and len(h3s) == 0 and len(h2s) > 0:
        _add("info", "headings", "Consider adding H3 subheadings within sections for better hierarchy")

    # Internal linking — blogs should funnel to products/categories
    if links["internal_count"] == 0:
        _add("warning", "links", "Blog post has no internal links — link to related posts, product pages, or categories")
    elif links["internal_count"] < 2:
        _add("info", "links", f"Only {links['internal_count']} internal link(s) — add 3-5 links to related content and product pages")

    # Images improve engagement
    if img["total"] == 0:
        _add("warning", "images", "Blog post has no images — add relevant images, screenshots, or infographics")
    elif img["total"] == 1:
        _add("info", "images", "Only 1 image — add more visuals to break up text and improve engagement")

    # Text/HTML ratio — blogs should be content-heavy
    if ratio < 10:
        _add("warning", "content", f"Low text ratio ({ratio}%) — blog content should be substantial relative to code")

    # Question-based headings for featured snippets
    h2_texts = " ".join(h2s).lower()
    if not any(q in h2_texts for q in ["what", "how", "why", "when", "where", "which", "who", "?"]):
        _add("info", "headings", "Consider using question-based H2s (How, What, Why) to target featured snippets")

    # External links add authority
    if links["external_count"] == 0 and wc > 500:
        _add("info", "links", "No external links — citing authoritative sources improves E-E-A-T")


# ──────────────────────────────────────────────
# Page-Type Insights
# ──────────────────────────────────────────────

def _generate_page_type_insights(data: dict, page_type: str) -> dict:
    """Generate actionable insights specific to the page type."""
    info = PAGE_TYPES.get(page_type, PAGE_TYPES["generic"])
    insights = {
        "page_type": page_type,
        "label": info["label"],
        "focus_areas": [],
        "recommendations": [],
    }

    if page_type == "homepage":
        insights["focus_areas"] = [
            "Brand authority & messaging",
            "Internal linking to key pages",
            "Clear navigation structure",
            "Social proof & trust signals",
        ]
        links = data["links"]
        if links["internal_count"] < 10:
            insights["recommendations"].append(
                f"Add internal links to your top {10 - links['internal_count']} most important pages (categories, products, contact)"
            )
        if not data.get("og_tags", {}).get("og:title"):
            insights["recommendations"].append("Add Open Graph tags for better social media sharing")
        if data["word_count"] < 200:
            insights["recommendations"].append("Add a clear value proposition and brand messaging above the fold")

    elif page_type == "product":
        insights["focus_areas"] = [
            "Unique product descriptions",
            "High-quality product images",
            "Transactional keyword targeting",
            "Structured data (Product schema)",
            "Clear CTAs and conversion paths",
        ]
        if data["word_count"] < 300:
            insights["recommendations"].append("Write unique product descriptions (300+ words) covering benefits, use cases, and specs")
        if data["images"]["total"] < 3:
            insights["recommendations"].append("Add multiple product images: main shot, angles, lifestyle, and detail views")
        if not data["canonical"]:
            insights["recommendations"].append("Add canonical tags to prevent duplicate content from product variants")
        ka = data.get("keyword_analysis", {})
        if ka and ka.get("exact_density_pct", 0) == 0:
            insights["recommendations"].append("Include target product keyword in the body text naturally")

    elif page_type == "blog":
        insights["focus_areas"] = [
            "Content depth & comprehensiveness",
            "Search intent alignment",
            "E-E-A-T signals (author, sources)",
            "Heading structure for featured snippets",
            "Internal links to product/category pages",
        ]
        if data["word_count"] < 1000:
            insights["recommendations"].append("Expand content to 1000-2000 words for comprehensive coverage")
        h2s = data["headings"].get("h2", [])
        if len(h2s) < 3:
            insights["recommendations"].append("Add more H2 subheadings to improve structure and featured snippet chances")
        if data["links"]["internal_count"] < 2:
            insights["recommendations"].append("Add 3-5 internal links to related posts, products, or category pages")
        if data["images"]["total"] == 0:
            insights["recommendations"].append("Add relevant images, screenshots, or infographics to improve engagement")

    else:  # generic
        insights["focus_areas"] = [
            "Meta tags optimization",
            "Content quality & depth",
            "Link strategy",
            "Image optimization",
        ]

    return insights


def _calculate_score(data: dict, page_type: str = "generic") -> int:
    """
    Calculate an SEO score from 0-100 with page-type-specific weighting.
    
    Homepage: links & navigation weighted higher.
    Product: content uniqueness & images weighted higher.
    Blog: content depth & heading structure weighted higher.
    """
    score = 100
    issues = data.get("issues", [])

    # Page-type-specific severity multipliers
    type_multipliers = {
        "homepage": {
            "links": 1.5,       # Internal linking is critical
            "content": 0.8,     # Less text-heavy is OK
            "images": 0.8,      # Less critical
            "headings": 1.0,
        },
        "product": {
            "content": 1.4,     # Unique descriptions critical
            "images": 1.5,      # Product images essential
            "keyword": 1.3,     # Transactional keywords important
            "technical": 1.2,   # Canonical is critical for variants
            "links": 0.9,
        },
        "blog": {
            "content": 1.3,     # Content depth matters
            "headings": 1.4,    # Structure for snippets
            "links": 1.2,       # Internal + external links
            "images": 1.0,
        },
        "generic": {},
    }

    multipliers = type_multipliers.get(page_type, {})

    for issue in issues:
        category = issue.get("category", "")
        multiplier = multipliers.get(category, 1.0)

        if issue["severity"] == "critical":
            score -= int(15 * multiplier)
        elif issue["severity"] == "warning":
            score -= int(7 * multiplier)
        elif issue["severity"] == "info":
            score -= int(2 * multiplier)

    return max(0, min(100, score))
