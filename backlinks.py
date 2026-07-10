"""
Rankivo — Backlink Analysis Module
Analyzes backlink profiles using Bing Webmaster API + Common Crawl + heuristic scoring.
Provides domain authority estimation, link quality assessment, and toxic link detection.
"""
import re
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS, BING_API_KEY, _safe_print
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# Domain Authority Heuristics
# ──────────────────────────────────────────────

HIGH_AUTHORITY_DOMAINS = {
    "wikipedia.org": 95, "github.com": 90, "stackoverflow.com": 85,
    "linkedin.com": 88, "youtube.com": 92, "twitter.com": 85, "x.com": 85,
    "reddit.com": 80, "medium.com": 75, "substack.com": 70,
    "nytimes.com": 95, "bbc.com": 95, "cnn.com": 90, "forbes.com": 90,
    "techcrunch.com": 85, "mashable.com": 80, "wired.com": 88,
    "arxiv.org": 80, "pubmed.ncbi.nlm.nih.gov": 85,
    "scholar.google.com": 90, "doi.org": 85,
    "edu": 70, "gov": 80, "org": 55,
}

TOXIC_SIGNALS = {
    "patterns": [
        r"buy\s+links", r"link\s+exchange", r"reciprocal\s+links",
        r"guest\s+post\s+network", r"private\s+blog\s+network", r"pbn",
        r"spam", r"pharmaceutical", r"casino", r"payday\s+loan",
        r"adult", r"xxx", r"porn", r"gambling",
    ],
    "tlds": {"xyz", "top", "club", "site", "online", "click", "link", "gq", "ml", "cf"},
}


# ──────────────────────────────────────────────
# 1. Bing Webmaster Backlinks API
# ──────────────────────────────────────────────

def _get_bing_backlinks(url: str) -> dict:
    """
    Fetch backlink data from Bing Webmaster API.
    Returns referring domains, pages, and anchor text.
    """
    if not BING_API_KEY:
        return {"available": False, "message": "Bing API key not configured"}

    parsed = urlparse(url)
    domain = parsed.netloc

    try:
        headers = {
            "Ocp-Apim-Subscription-Key": BING_API_KEY,
            "Content-Type": "application/json",
        }
        # Get backlinks for the domain
        api_url = "https://api.bing.microsoft.com/v7.0/webmaster/backlinks"
        resp = requests.get(
            api_url, headers=headers,
            params={"siteUrl": domain, "offset": 0, "count": 50},
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code == 200:
            data = resp.json()
            value = data.get("d", {}).get("BacklinkEntries", [])
            referring_domains = set()
            backlinks = []
            for entry in value:
                from_url = entry.get("FromUrl", "")
                if from_url:
                    from_parsed = urlparse(from_url)
                    referring_domains.add(from_parsed.netloc)
                    backlinks.append({
                        "url": from_url,
                        "domain": from_parsed.netloc,
                        "anchor_text": entry.get("AnchorText", ""),
                        "page_title": entry.get("Title", ""),
                    })
            return {
                "available": True,
                "source": "Bing Webmaster API",
                "total_backlinks": len(backlinks),
                "referring_domains": len(referring_domains),
                "backlinks": backlinks[:50],
            }
        elif resp.status_code == 401:
            return {"available": True, "error": "Invalid Bing API key", "message": "Authentication failed"}
        else:
            return {"available": True, "error": f"API returned {resp.status_code}"}
    except Exception as e:
        return {"available": True, "error": str(e)}


# ──────────────────────────────────────────────
# 2. Common Crawl Backlink Discovery
# ──────────────────────────────────────────────

def _get_common_crawl_backlinks(url: str) -> dict:
    """
    Discover backlinks via Common Crawl index.
    Searches for pages linking to the target URL.
    """
    parsed = urlparse(url)
    domain = parsed.netloc

    try:
        # Use Common Crawl index API
        index_url = f"https://index.commoncrawl.org/CC-MAIN-2024-51-index?url={domain}&output=json&limit=20"
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(index_url, headers=headers, timeout=30)

        if resp.status_code == 200:
            lines = resp.text.strip().split("\n")
            referring_domains = set()
            backlinks = []
            for line in lines[:20]:
                try:
                    import json
                    entry = json.loads(line)
                    url_found = entry.get("url", "")
                    if url_found:
                        from_parsed = urlparse(url_found)
                        if from_parsed.netloc != domain:
                            referring_domains.add(from_parsed.netloc)
                            backlinks.append({
                                "url": url_found,
                                "domain": from_parsed.netloc,
                                "crawl_date": entry.get("timestamp", ""),
                            })
                except Exception:
                    continue
            return {
                "available": True,
                "source": "Common Crawl",
                "total_backlinks": len(backlinks),
                "referring_domains": len(referring_domains),
                "backlinks": backlinks,
            }
        return {"available": True, "source": "Common Crawl", "total_backlinks": 0, "message": "No results found"}
    except Exception as e:
        return {"available": True, "source": "Common Crawl", "error": str(e)}


# ──────────────────────────────────────────────
# 3. Domain Authority Scoring
# ──────────────────────────────────────────────

def _estimate_domain_authority(domain: str) -> int:
    """
    Heuristic domain authority score (0-100).
    Based on known high-authority domains and TLD signals.
    """
    domain_lower = domain.lower()

    # Check known high-authority domains
    for known_domain, score in HIGH_AUTHORITY_DOMAINS.items():
        if domain_lower == known_domain or domain_lower.endswith("." + known_domain):
            return score

    # TLD-based scoring
    tld = domain_lower.split(".")[-1] if "." in domain_lower else ""
    tld_scores = {
        "edu": 75, "gov": 80, "org": 55, "com": 50, "net": 45,
        "io": 50, "co": 48, "ai": 55, "dev": 50,
    }
    base_score = tld_scores.get(tld, 35)

    # Subdomain penalty (less authoritative)
    parts = domain_lower.split(".")
    if len(parts) > 2:
        base_score = max(base_score - 10, 10)

    return min(base_score, 100)


def _assess_link_quality(backlink: dict) -> dict:
    """
    Assess the quality of a single backlink.
    Returns quality score, risk level, and reasons.
    """
    score = 50  # neutral starting point
    risks = []
    positives = []

    domain = backlink.get("domain", "")
    url = backlink.get("url", "")
    anchor = backlink.get("anchor_text", "")

    # Domain authority boost
    da = _estimate_domain_authority(domain)
    score = da

    # Toxic signal detection
    combined_text = f"{url} {anchor}".lower()
    for pattern in TOXIC_SIGNALS["patterns"]:
        if re.search(pattern, combined_text):
            score = max(score - 30, 0)
            risks.append(f"Toxic pattern detected: {pattern}")

    # Suspicious TLD
    tld = domain.split(".")[-1] if "." in domain else ""
    if tld in TOXIC_SIGNALS["tlds"]:
        score = max(score - 15, 0)
        risks.append(f"Suspicious TLD: .{tld}")

    # Anchor text quality
    if anchor:
        if len(anchor) > 50:
            risks.append("Over-optimized anchor text (too long)")
            score = max(score - 10, 0)
        elif any(kw in anchor.lower() for kw in ["buy", "cheap", "free", "casino"]):
            risks.append("Commercial/spammy anchor text")
            score = max(score - 15, 0)
        else:
            positives.append("Natural anchor text")
    else:
        risks.append("No anchor text (may indicate image-only link)")

    # URL path signals
    if "/blog/" in url or "/post/" in url or "/article/" in url:
        positives.append("Editorial link (blog/article)")
        score = min(score + 5, 100)
    if "/comment/" in url or "/forum/" in url:
        risks.append("Forum/comment link (lower quality)")
        score = max(score - 5, 0)

    # Risk level
    if score >= 70:
        risk_level = "low"
    elif score >= 40:
        risk_level = "medium"
    else:
        risk_level = "high"

    return {
        "score": min(max(score, 0), 100),
        "risk_level": risk_level,
        "positives": positives,
        "risks": risks,
    }


# ──────────────────────────────────────────────
# 4. Backlink Profile Summary
# ──────────────────────────────────────────────

def _analyze_anchor_text_distribution(backlinks: list[dict]) -> dict:
    """Analyze anchor text distribution for over-optimization."""
    anchors = [b.get("anchor_text", "").lower().strip() for b in backlinks if b.get("anchor_text")]
    if not anchors:
        return {"total_anchors": 0, "distribution": {}, "over_optimized": False}

    # Categorize anchors
    branded = 0
    exact_match = 0
    partial_match = 0
    generic = 0
    url_anchors = 0

    generic_phrases = {"click here", "read more", "learn more", "here", "this", "website", "link"}

    for anchor in anchors:
        if anchor.startswith("http") or anchor.startswith("www"):
            url_anchors += 1
        elif anchor in generic_phrases:
            generic += 1
        elif len(anchor.split()) == 1 and len(anchor) > 20:
            exact_match += 1
        elif len(anchor.split()) >= 2:
            partial_match += 1
        else:
            branded += 1

    total = len(anchors)
    exact_pct = (exact_match / total * 100) if total > 0 else 0
    over_optimized = exact_pct > 30

    return {
        "total_anchors": total,
        "distribution": {
            "branded": branded,
            "exact_match": exact_match,
            "partial_match": partial_match,
            "generic": generic,
            "url": url_anchors,
        },
        "percentages": {
            "branded": round(branded / total * 100, 1) if total else 0,
            "exact_match": round(exact_match / total * 100, 1) if total else 0,
            "partial_match": round(partial_match / total * 100, 1) if total else 0,
            "generic": round(generic / total * 100, 1) if total else 0,
            "url": round(url_anchors / total * 100, 1) if total else 0,
        },
        "over_optimized": over_optimized,
        "recommendation": "Anchor text is over-optimized (>30% exact match). Diversify with branded and generic anchors." if over_optimized else "Anchor text distribution looks natural.",
    }


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def analyze_backlinks(url: str) -> dict:
    """
    Full backlink analysis for a URL.
    Combines Bing Webmaster API, Common Crawl, and heuristic scoring.
    """
    result = {
        "url": url,
        "total_backlinks": 0,
        "referring_domains": 0,
        "backlinks": [],
        "quality_summary": {},
        "anchor_analysis": {},
        "toxic_links": [],
        "top_referring_domains": [],
        "score": 0,
        "issues": [],
        "recommendations": [],
    }

    # Fetch backlinks from multiple sources
    bing_data = _get_bing_backlinks(url)
    cc_data = _get_common_crawl_backlinks(url)

    # Merge backlinks from all sources
    all_backlinks = []
    sources_used = []

    if bing_data.get("backlinks"):
        all_backlinks.extend(bing_data["backlinks"])
        sources_used.append("Bing Webmaster API")

    if cc_data.get("backlinks"):
        # Deduplicate by URL
        existing_urls = {b["url"] for b in all_backlinks}
        for b in cc_data["backlinks"]:
            if b["url"] not in existing_urls:
                all_backlinks.append(b)
                existing_urls.add(b["url"])
        sources_used.append("Common Crawl")

    result["backlinks"] = all_backlinks[:100]  # limit for display
    result["total_backlinks"] = len(all_backlinks)
    result["sources"] = sources_used

    # Count unique referring domains
    domains = set()
    for b in all_backlinks:
        d = b.get("domain", "")
        if d:
            domains.add(d)
    result["referring_domains"] = len(domains)

    # Assess quality of each backlink
    quality_scores = []
    toxic = []
    domain_scores = {}

    for b in all_backlinks:
        quality = _assess_link_quality(b)
        b["quality"] = quality
        quality_scores.append(quality["score"])

        if quality["risk_level"] == "high":
            toxic.append(b)

        domain = b.get("domain", "")
        if domain and domain not in domain_scores:
            domain_scores[domain] = _estimate_domain_authority(domain)

    result["toxic_links"] = toxic[:20]

    # Anchor text analysis
    result["anchor_analysis"] = _analyze_anchor_text_distribution(all_backlinks)

    # Top referring domains by authority
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    result["top_referring_domains"] = [
        {"domain": d, "authority": score} for d, score in sorted_domains[:15]
    ]

    # Overall score
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        da_bonus = sum(domain_scores.values()) / max(len(domain_scores), 1) * 0.3
        result["score"] = min(round(avg_quality * 0.7 + da_bonus), 100)
    else:
        result["score"] = 0

    # Quality summary
    result["quality_summary"] = {
        "average_quality": round(sum(quality_scores) / max(len(quality_scores), 1), 1),
        "high_quality": sum(1 for s in quality_scores if s >= 70),
        "medium_quality": sum(1 for s in quality_scores if 40 <= s < 70),
        "low_quality": sum(1 for s in quality_scores if s < 40),
        "toxic_count": len(toxic),
    }

    # Generate recommendations
    if result["total_backlinks"] == 0:
        result["issues"].append({"severity": "critical", "message": "No backlinks found"})
        result["recommendations"].append("Build backlinks through guest posting, content marketing, and PR")
    elif result["total_backlinks"] < 10:
        result["issues"].append({"severity": "warning", "message": f"Only {result['total_backlinks']} backlinks found"})
        result["recommendations"].append("Increase backlink acquisition through link-worthy content")

    if result["anchor_analysis"].get("over_optimized"):
        result["issues"].append({"severity": "warning", "message": "Anchor text is over-optimized"})
        result["recommendations"].append(result["anchor_analysis"]["recommendation"])

    if toxic:
        result["issues"].append({"severity": "warning", "message": f"{len(toxic)} potentially toxic backlinks detected"})
        result["recommendations"].append("Consider disavowing toxic backlinks via Google Search Console")

    if not bing_data.get("available") and not cc_data.get("backlinks"):
        result["issues"].append({"severity": "info", "message": "Limited data — configure BING_API_KEY for richer backlink data"})

    return result
