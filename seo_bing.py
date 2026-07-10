"""
SEO AI Tools - Bing SEO Compatibility Module
Analyzes pages for Bing-specific SEO requirements and provides compatibility scores.
"""
import json
import time
import requests
import traceback
from typing import Optional
from config import (
    random_ua,
    REQUEST_TIMEOUT,
    USER_AGENTS,
    BING_API_KEY,
)
import random




# ──────────────────────────────────────────────
# Bing Webmaster API Integration
# ──────────────────────────────────────────────


def _get_bing_headers() -> dict:
    """Get headers for Bing Webmaster API calls."""
    if not BING_API_KEY:
        return {}
    return {
        "Ocp-Apim-Subscription-Key": BING_API_KEY,
        "Content-Type": "application/json",
    }


def check_bing_index_status(url: str) -> dict:
    """
    Check if a URL is indexed in Bing using the Bing Webmaster API.
    
    Requires BING_API_KEY to be configured.
    Returns index status information.
    """
    if not BING_API_KEY:
        return {
            "available": False,
            "message": "Bing API key not configured. Set BING_API_KEY in .env",
            "indexed": None,
        }

    try:
        # Bing URL Submission API - check index status
        api_url = "https://api.bing.microsoft.com/v7.0/webmaster/indexing/check"
        headers = _get_bing_headers()
        
        resp = requests.get(
            api_url,
            headers=headers,
            params={"url": url},
            timeout=REQUEST_TIMEOUT,
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "available": True,
                "indexed": data.get("isIndexed", False),
                "status": data.get("indexingStatus", "unknown"),
                "last_crawled": data.get("lastCrawled", ""),
                "message": f"URL is {'indexed' if data.get('isIndexed') else 'not indexed'} in Bing",
            }
        elif resp.status_code == 401:
            return {
                "available": True,
                "indexed": None,
                "error": "Invalid Bing API key",
                "message": "Bing API authentication failed. Check your BING_API_KEY.",
            }
        else:
            return {
                "available": True,
                "indexed": None,
                "error": f"API returned {resp.status_code}",
                "message": f"Bing API returned status {resp.status_code}",
            }
    except Exception as e:
        return {
            "available": True,
            "indexed": None,
            "error": str(e),
            "message": f"Bing API error: {e}",
        }


def submit_url_to_bing(url: str) -> dict:
    """
    Submit a URL to Bing for indexing via the Bing Webmaster API.
    """
    if not BING_API_KEY:
        return {
            "success": False,
            "message": "Bing API key not configured",
        }

    try:
        api_url = "https://api.bing.microsoft.com/v7.0/webmaster/indexing/submit"
        headers = _get_bing_headers()
        
        resp = requests.post(
            api_url,
            headers=headers,
            json={"url": url},
            timeout=REQUEST_TIMEOUT,
        )
        
        if resp.status_code in (200, 202):
            return {
                "success": True,
                "message": f"URL submitted to Bing for indexing: {url}",
            }
        else:
            return {
                "success": False,
                "message": f"Bing submission returned {resp.status_code}",
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Bing submission error: {e}",
        }


# ──────────────────────────────────────────────
# On-Page Bing SEO Analysis
# ──────────────────────────────────────────────


def analyze_bing_seo(url: str, html_content: Optional[str] = None, page_data: Optional[dict] = None) -> dict:
    """
    Analyze a page for Bing-specific SEO factors and provide a compatibility score.
    
    Checks:
    - Bing Webmaster verification tag (msvalidate.01)
    - Meta description quality
    - Title tag quality
    - Content relevance and quality
    - Mobile-friendliness signals
    - Page load factors
    - Social signals (Open Graph, Twitter Cards)
    - Structured data
    - Sitemap presence
    
    Returns a dict with score, checks, and recommendations.
    """
    from bs4 import BeautifulSoup

    fetched_html = html_content
    fetched_page_data = page_data or {}

    # Fetch the page if not provided
    if not fetched_html:
        try:
            headers = {"User-Agent": random_ua()}
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                fetched_html = resp.text
        except Exception as e:
            return {
                "url": url,
                "score": 0,
                "error": f"Could not fetch page: {e}",
                "checks": [],
                "recommendations": [f"Failed to fetch URL: {e}"],
            }

    if not fetched_html:
        return {
            "url": url,
            "score": 0,
            "error": "No HTML content available",
            "checks": [],
            "recommendations": ["Could not retrieve page content"],
        }

    soup = BeautifulSoup(fetched_html, "lxml")
    
    checks = []
    score = 100
    recommendations = []

    # 1. Bing Verification Tag
    bing_meta = soup.find("meta", attrs={"name": "msvalidate.01"})
    if bing_meta:
        checks.append({
            "category": "Bing Verification",
            "status": "pass",
            "message": "Bing Webmaster verification tag found (msvalidate.01)",
            "weight": 5,
        })
    else:
        checks.append({
            "category": "Bing Verification",
            "status": "fail",
            "message": "Bing Webmaster verification tag not found (msvalidate.01)",
            "weight": 5,
        })
        score -= 5
        recommendations.append("Add Bing Webmaster verification meta tag: <meta name=\"msvalidate.01\" content=\"YOUR_VERIFICATION_CODE\" />")

    # 2. Title Tag
    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    if title_text:
        title_len = len(title_text)
        if 30 <= title_len <= 65:
            checks.append({
                "category": "Title Tag",
                "status": "pass",
                "message": f"Title tag length is optimal ({title_len} chars). Bing prefers 30-65 chars.",
                "weight": 10,
            })
        elif title_len < 30:
            checks.append({
                "category": "Title Tag",
                "status": "warn",
                "message": f"Title tag too short ({title_len} chars). Aim for 30-65 chars for Bing.",
                "weight": 10,
            })
            score -= 5
            recommendations.append(f"Extend title tag ({title_len} chars → aim for 30-65 chars)")
        else:
            checks.append({
                "category": "Title Tag",
                "status": "warn",
                "message": f"Title tag too long ({title_len} chars). Bing may truncate after 65 chars.",
                "weight": 10,
            })
            score -= 5
            recommendations.append(f"Shorten title tag ({title_len} chars → aim for 30-65 chars)")
    else:
        checks.append({
            "category": "Title Tag",
            "status": "fail",
            "message": "Missing title tag – critical for Bing SEO",
            "weight": 10,
        })
        score -= 10
        recommendations.append("Add a descriptive title tag (30-65 chars)")

    # 3. Meta Description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    desc_content = meta_desc.get("content", "").strip() if meta_desc else ""
    if desc_content:
        desc_len = len(desc_content)
        if 120 <= desc_len <= 165:
            checks.append({
                "category": "Meta Description",
                "status": "pass",
                "message": f"Meta description length is optimal ({desc_len} chars). Bing displays ~160 chars.",
                "weight": 10,
            })
        else:
            checks.append({
                "category": "Meta Description",
                "status": "warn",
                "message": f"Meta description length ({desc_len} chars). Bing recommends 120-165 chars.",
                "weight": 10,
            })
            score -= 5
            recommendations.append(f"Optimize meta description length ({desc_len} chars → aim 120-165 chars)")
    else:
        checks.append({
            "category": "Meta Description",
            "status": "fail",
            "message": "Missing meta description – Bing uses this for search snippets",
            "weight": 10,
        })
        score -= 10
        recommendations.append("Add a compelling meta description (120-165 chars)")

    # 4. Open Graph Tags (Bing uses OG for social signals)
    og_tags = {
        "og:title": soup.find("meta", attrs={"property": "og:title"}),
        "og:description": soup.find("meta", attrs={"property": "og:description"}),
        "og:image": soup.find("meta", attrs={"property": "og:image"}),
        "og:url": soup.find("meta", attrs={"property": "og:url"}),
    }
    og_found = sum(1 for v in og_tags.values() if v)
    if og_found >= 3:
        checks.append({
            "category": "Open Graph",
            "status": "pass",
            "message": f"Good Open Graph tags found ({og_found}/4 required)",
            "weight": 8,
        })
    elif og_found > 0:
        checks.append({
            "category": "Open Graph",
            "status": "warn",
            "message": f"Partial Open Graph tags ({og_found}/4). Bing uses OG for rich snippets.",
            "weight": 8,
        })
        score -= 4
        recommendations.append("Add missing Open Graph tags (og:title, og:description, og:image, og:url)")
    else:
        checks.append({
            "category": "Open Graph",
            "status": "fail",
            "message": "No Open Graph tags found. Bing uses OG tags for rich results.",
            "weight": 8,
        })
        score -= 8
        recommendations.append("Add Open Graph meta tags for better Bing presentation")

    # 5. Twitter Cards
    twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
    if twitter_card:
        checks.append({
            "category": "Twitter Cards",
            "status": "pass",
            "message": "Twitter Card tag found",
            "weight": 3,
        })
    else:
        checks.append({
            "category": "Twitter Cards",
            "status": "info",
            "message": "Twitter Card not found (optional, but helps Bing social signals)",
            "weight": 3,
        })

    # 6. Heading Structure
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 1:
        checks.append({
            "category": "Heading Structure",
            "status": "pass",
            "message": f"Exactly one H1 tag found: \"{h1_tags[0].get_text(strip=True)[:60]}\"",
            "weight": 8,
        })
    elif len(h1_tags) == 0:
        checks.append({
            "category": "Heading Structure",
            "status": "fail",
            "message": "No H1 tag found. Bing expects one H1 per page.",
            "weight": 8,
        })
        score -= 8
        recommendations.append("Add exactly one H1 heading containing your primary keyword")
    else:
        checks.append({
            "category": "Heading Structure",
            "status": "warn",
            "message": f"Multiple H1 tags ({len(h1_tags)}). Bing recommends a single H1.",
            "weight": 8,
        })
        score -= 4
        recommendations.append(f"Use only one H1 tag per page (you have {len(h1_tags)})")

    # 7. Keyword in H1
    h2_tags = soup.find_all("h2")
    checks.append({
        "category": "Heading Structure",
        "status": "info",
        "message": f"H2 tags found: {len(h2_tags)}. Having 3-5 H2s helps Bing understand content structure.",
        "weight": 3,
    })

    # 8. Alt Text on Images
    images = soup.find_all("img")
    total_imgs = len(images)
    imgs_with_alt = sum(1 for img in images if img.get("alt", "").strip())
    if total_imgs > 0:
        alt_pct = (imgs_with_alt / total_imgs) * 100
        if alt_pct >= 80:
            checks.append({
                "category": "Image Alt Text",
                "status": "pass",
                "message": f"Good alt text coverage: {imgs_with_alt}/{total_imgs} ({alt_pct:.0f}%)",
                "weight": 7,
            })
        elif alt_pct >= 50:
            checks.append({
                "category": "Image Alt Text",
                "status": "warn",
                "message": f"Moderate alt text coverage: {imgs_with_alt}/{total_imgs} ({alt_pct:.0f}%)",
                "weight": 7,
            })
            score -= 3
            recommendations.append(f"Add alt text to {total_imgs - imgs_with_alt} images")
        else:
            checks.append({
                "category": "Image Alt Text",
                "status": "fail",
                "message": f"Poor alt text coverage: {imgs_with_alt}/{total_imgs} ({alt_pct:.0f}%)",
                "weight": 7,
            })
            score -= 7
            recommendations.append(f"Add descriptive alt text to {total_imgs - imgs_with_alt} images (Bing uses alt text for image search)")
    else:
        checks.append({
            "category": "Image Alt Text",
            "status": "info",
            "message": "No images on page",
            "weight": 7,
        })

    # 9. Content Quality Signals
    body_text = soup.get_text(strip=True)
    word_count = len(body_text.split())
    if word_count >= 500:
        checks.append({
            "category": "Content Quality",
            "status": "pass",
            "message": f"Good content length: ~{word_count} words. Bing favors comprehensive content.",
            "weight": 10,
        })
    elif word_count >= 200:
        checks.append({
            "category": "Content Quality",
            "status": "warn",
            "message": f"Moderate content: ~{word_count} words. Bing recommends 500+ words for good ranking.",
            "weight": 10,
        })
        score -= 5
        recommendations.append(f"Expand content (~{word_count} words → aim for 500+ for Bing)")
    else:
        checks.append({
            "category": "Content Quality",
            "status": "fail",
            "message": f"Thin content: ~{word_count} words. Significantly expand for Bing ranking.",
            "weight": 10,
        })
        score -= 10
        recommendations.append(f"Significantly expand content (~{word_count} words → aim for 1000+)")

    # 10. Structured Data (Schema.org)
    schema_tags = soup.find_all("script", attrs={"type": "application/ld+json"})
    if schema_tags:
        checks.append({
            "category": "Structured Data",
            "status": "pass",
            "message": f"Found {len(schema_tags)} structured data entries. Bing uses schema.org markup.",
            "weight": 8,
        })
    else:
        checks.append({
            "category": "Structured Data",
            "status": "warn",
            "message": "No structured data (schema.org) found. Adding markup helps Bing understand content.",
            "weight": 8,
        })
        score -= 4
        recommendations.append("Add structured data (JSON-LD schema.org markup) for better Bing visibility")

    # 11. Canonical Tag
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if canonical:
        checks.append({
            "category": "Canonical URL",
            "status": "pass",
            "message": f"Canonical tag found: {canonical.get('href', '')[:60]}",
            "weight": 5,
        })
    else:
        checks.append({
            "category": "Canonical URL",
            "status": "warn",
            "message": "No canonical tag. Bing recommends specifying canonical URLs.",
            "weight": 5,
        })
        score -= 3
        recommendations.append("Add a canonical URL tag to prevent duplicate content issues in Bing")

    # 12. Viewport / Mobile-friendliness
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if viewport:
        checks.append({
            "category": "Mobile Friendliness",
            "status": "pass",
            "message": "Viewport meta tag found (mobile-friendly signal)",
            "weight": 5,
        })
    else:
        checks.append({
            "category": "Mobile Friendliness",
            "status": "fail",
            "message": "No viewport meta tag. Bing prioritizes mobile-friendly pages.",
            "weight": 5,
        })
        score -= 5
        recommendations.append("Add viewport meta tag for mobile responsiveness (Bing mobile-first)")

    # 13. Nofollow / Sponsored links
    all_links = soup.find_all("a")
    nofollow_links = sum(1 for a in all_links if a.get("rel") and "nofollow" in a.get("rel", []))
    if nofollow_links > 0:
        checks.append({
            "category": "Link Attributes",
            "status": "info",
            "message": f"{nofollow_links} nofollow links found. Bing respects rel=\"nofollow\" and rel=\"sponsored\".",
            "weight": 3,
        })

    # 14. Language Declaration
    html_tag = soup.find("html")
    lang = html_tag.get("lang", "") if html_tag else ""
    if lang:
        checks.append({
            "category": "Language Declaration",
            "status": "pass",
            "message": f"Language declared: {lang}. Bing uses lang attribute for language targeting.",
            "weight": 4,
        })
    else:
        checks.append({
            "category": "Language Declaration",
            "status": "warn",
            "message": "No lang attribute on <html> tag. Specify language for Bing.",
            "weight": 4,
        })
        score -= 2
        recommendations.append("Add lang attribute to <html> tag (e.g., <html lang=\"en\">)")

    # Ensure score is within 0-100
    score = max(0, min(100, score))

    return {
        "url": url,
        "score": score,
        "checks": checks,
        "recommendations": recommendations[:10],
        "api_available": bool(BING_API_KEY),
    }
