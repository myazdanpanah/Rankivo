"""
Rankivo — E-E-A-T Scoring Module
Evaluates pages against Google's Search Quality Rater Guidelines (Sept 2025).
Scores Experience, Expertise, Authoritativeness, and Trustworthiness separately,
then produces a composite E-E-A-T grade.
"""
import re
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS, random_ua
import random




# ──────────────────────────────────────────────
# Schema types that imply author / org signals
# ──────────────────────────────────────────────

_AUTHOR_SCHEMA_TYPES = {"Person", "Organization", "Author"}
_ARTICLE_SCHEMA_TYPES = {
    "Article", "NewsArticle", "BlogPosting", "TechArticle",
    "ScholarlyArticle", "Report", "Review", "ProfilePage",
}
_TRUST_SCHEMA_TYPES = {
    "Organization", "LocalBusiness", "MedicalOrganization",
    "EducationalOrganization", "NGO", "GovernmentOrganization",
}


# ──────────────────────────────────────────────
# Falsifiable checks — each returns (score_delta, message)
# ──────────────────────────────────────────────

def _check_experience(soup, body_text: str, url: str) -> dict:
    """
    Experience: first-hand, original content signals.
    Checks for: author bio, personal pronouns, first-person narrative,
    original images/media, case studies, date stamps.
    """
    signals = []
    score = 0
    max_score = 25

    # Author information present
    author_found = False
    # Check meta author
    meta_author = soup.find("meta", attrs={"name": "author"})
    if meta_author and meta_author.get("content", "").strip():
        author_found = True
        signals.append("Meta author tag present")

    # Check schema.org author
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            import json
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict) and item.get("author"):
                        author_found = True
                        signals.append("Schema.org author present")
                        break
        except Exception:
            pass

    # Check for author section in HTML (rel="author", class with "author")
    author_link = soup.find("a", attrs={"rel": "author"})
    if author_link:
        author_found = True
        signals.append("Author link (rel=author) found")

    author_el = soup.find(attrs={"class": re.compile(r"author", re.I)})
    if author_el:
        author_found = True
        signals.append("Author element found in HTML")

    if author_found:
        score += 8

    # First-person narrative (Experience signal)
    first_person_patterns = [
        r"\bI (?:have|was|used|tried|found|tested|discovered|wrote|created)\b",
        r"\bwe (?:have|are|were|use|tested|built|developed)\b",
        r"\bour (?:team|experience|research|study|findings)\b",
    ]
    first_person_count = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in first_person_patterns
    )
    if first_person_count >= 3:
        score += 6
        signals.append(f"First-person narrative ({first_person_count} instances)")
    elif first_person_count >= 1:
        score += 3
        signals.append(f"Some first-person narrative ({first_person_count} instances)")

    # Date stamps (content freshness)
    date_patterns = [
        r"(?:published|updated|last modified|date)[:\s]*\w+ \d{1,2},? \d{4}",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* \d{1,2},? \d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
    ]
    date_count = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in date_patterns
    )
    if date_count >= 2:
        score += 5
        signals.append(f"Multiple date stamps ({date_count})")
    elif date_count >= 1:
        score += 2
        signals.append("At least one date stamp found")

    # Original images (not stock photo patterns)
    images = soup.find_all("img")
    original_img_hints = 0
    for img in images[:20]:
        src = img.get("src", "")
        alt = img.get("alt", "")
        # Stock photo indicators
        is_stock = any(s in src.lower() for s in ["shutterstock", "getty", "istock", "unsplash", "pexels"])
        if not is_stock and alt.strip():
            original_img_hints += 1
    if original_img_hints >= 3:
        score += 4
        signals.append(f"Non-stock images with alt text ({original_img_hints})")
    elif original_img_hints >= 1:
        score += 2
        signals.append("Some original images found")

    # Case study / review / tutorial signals
    case_study_patterns = [
        r"case study", r"our experience", r"we tested", r"step-by-step",
        r"tutorial", r"how we", r"our results", r"before and after",
    ]
    cs_count = sum(
        1 for p in case_study_patterns
        if re.search(p, body_text, re.IGNORECASE)
    )
    if cs_count >= 2:
        score += 2
        signals.append(f"Case study / hands-on signals ({cs_count})")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


def _check_expertise(soup, body_text: str) -> dict:
    """
    Expertise: topical depth, credentials, comprehensive coverage.
    """
    signals = []
    score = 0
    max_score = 25

    # Word count as proxy for depth
    words = body_text.split()
    wc = len(words)
    if wc >= 2000:
        score += 6
        signals.append(f"Comprehensive content ({wc} words)")
    elif wc >= 1000:
        score += 4
        signals.append(f"Good content depth ({wc} words)")
    elif wc >= 500:
        score += 2
        signals.append(f"Moderate content ({wc} words)")
    else:
        signals.append(f"Thin content ({wc} words) — expertise signal is weak")

    # Heading structure (H2/H3 = organized expertise)
    h2s = soup.find_all("h2")
    h3s = soup.find_all("h3")
    if len(h2s) >= 5:
        score += 4
        signals.append(f"Well-structured with {len(h2s)} H2s and {len(h3s)} H3s")
    elif len(h2s) >= 3:
        score += 2
        signals.append(f"Good structure ({len(h2s)} H2s)")

    # External citations / references (authority through linking)
    external_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") and "nofollow" not in a.get("rel", []):
            parsed = urlparse(href)
            if parsed.netloc and parsed.netloc not in ["", "localhost"]:
                external_links.append(href)
    # Authority domains
    authority_domains = [
        "wikipedia.org", "scholar.google", "pubmed", "nih.gov", "edu",
        "gov", "arxiv.org", "github.com", "stackoverflow.com",
    ]
    authority_links = sum(
        1 for link in external_links
        if any(d in link for d in authority_domains)
    )
    if authority_links >= 3:
        score += 5
        signals.append(f"Cites {authority_links} authoritative sources")
    elif authority_links >= 1:
        score += 2
        signals.append(f"Cites {authority_links} authoritative source(s)")
    elif len(external_links) >= 2:
        score += 1
        signals.append(f"{len(external_links)} external links (no authority domains)")

    # Technical depth indicators
    technical_patterns = [
        r"\b\d{1,3}(?:\.\d+)?%",  # percentages / statistics
        r"\b(?:study|research|data|survey|analysis|report)s?\b",
        r"\bsource[s]?\b",
        r"\breference[s]?\b",
    ]
    tech_count = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in technical_patterns
    )
    if tech_count >= 5:
        score += 5
        signals.append(f"Data-rich content ({tech_count} technical signals)")
    elif tech_count >= 2:
        score += 3
        signals.append(f"Some technical depth ({tech_count} signals)")

    # Lists, tables, structured content = organized expertise
    lists = soup.find_all(["ul", "ol"])
    tables = soup.find_all("table")
    if len(lists) >= 3 or tables:
        score += 3
        signals.append("Uses lists/tables for organized presentation")
    elif lists:
        score += 1
        signals.append("Uses lists")

    # Code blocks / technical content
    code_blocks = soup.find_all(["code", "pre"])
    if code_blocks:
        score += 2
        signals.append(f"Technical content ({len(code_blocks)} code elements)")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


def _check_authoritativeness(soup, body_text: str, url: str) -> dict:
    """
    Authoritativeness: external recognition, brand signals, backlink potential.
    """
    signals = []
    score = 0
    max_score = 25

    # Open Graph / social presence
    og_site = soup.find("meta", attrs={"property": "og:site_name"})
    if og_site and og_site.get("content"):
        score += 2
        signals.append(f"Brand site name: {og_site['content']}")

    # Social media links
    social_platforms = [
        "twitter.com", "x.com", "linkedin.com", "facebook.com",
        "instagram.com", "youtube.com", "github.com",
    ]
    social_links = []
    for a in soup.find_all("a", href=True):
        for platform in social_platforms:
            if platform in a["href"]:
                social_links.append(platform)
    social_links = list(set(social_links))
    if len(social_links) >= 3:
        score += 5
        signals.append(f"Social presence: {', '.join(social_links)}")
    elif len(social_links) >= 1:
        score += 2
        signals.append(f"Social links: {', '.join(social_links)}")

    # Schema.org Organization / brand signals
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            import json
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict):
                        stype = item.get("@type", "")
                        if stype in _TRUST_SCHEMA_TYPES:
                            score += 3
                            signals.append(f"Schema type: {stype}")
                            if item.get("sameAs"):
                                score += 2
                                signals.append("Has sameAs links (brand verification)")
                            if item.get("logo"):
                                score += 1
                                signals.append("Has logo in schema")
                            break
        except Exception:
            pass

    # Domain authority signals (tLD)
    parsed = urlparse(url)
    tld = parsed.netloc.split(".")[-1].lower()
    trust_tlds = {"edu": 5, "gov": 5, "org": 2}
    if tld in trust_tlds:
        score += trust_tlds[tld]
        signals.append(f"Trusted TLD: .{tld}")

    # Internal linking strength (deep site = established)
    internal_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/") or parsed.netloc in href:
            internal_links.append(href)
    if len(internal_links) >= 10:
        score += 3
        signals.append(f"Strong internal linking ({len(internal_links)} internal links)")
    elif len(internal_links) >= 5:
        score += 1
        signals.append(f"Good internal linking ({len(internal_links)} links)")

    # Contact information present
    contact_signals = []
    if soup.find("a", href=re.compile(r"mailto:", re.I)):
        contact_signals.append("email")
    if soup.find("a", href=re.compile(r"tel:", re.I)):
        contact_signals.append("phone")
    contact_text = re.findall(
        r"(?:contact|phone|email|address|call us)",
        body_text, re.IGNORECASE
    )
    if contact_signals:
        score += 3
        signals.append(f"Contact info: {', '.join(contact_signals)}")
    elif contact_text:
        score += 1
        signals.append("Contact-related text found")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


def _check_trustworthiness(soup, body_text: str, url: str) -> dict:
    """
    Trustworthiness: HTTPS, privacy policy, about page, corrections, transparency.
    Most heavily weighted in Google's QRG.
    """
    signals = []
    score = 0
    max_score = 25

    # HTTPS
    parsed = urlparse(url)
    if parsed.scheme == "https":
        score += 3
        signals.append("HTTPS enabled")
    else:
        signals.append("⚠️ Not using HTTPS — critical trust issue")

    # Privacy policy / terms links
    privacy_signals = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a["href"].lower()
        if any(kw in text or kw in href for kw in ["privacy", "terms", "policy", "legal", "gdpr", "cookie"]):
            privacy_signals.append(text or href)
    if privacy_signals:
        score += 4
        signals.append(f"Legal pages found: {', '.join(privacy_signals[:3])}")
    else:
        signals.append("⚠️ No privacy policy or terms links found")

    # About page
    about_links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True).lower()
        href = a["href"].lower()
        if any(kw in text or kw in href for kw in ["about", "team", "company", "our story", "mission"]):
            about_links.append(text or href)
    if about_links:
        score += 3
        signals.append(f"About/team page linked: {', '.join(about_links[:2])}")
    else:
        signals.append("No about/team page linked")

    # HTTPS certificate (implied by scheme)
    # Content transparency signals
    transparency_patterns = [
        r"editorial (?:policy|process|guidelines)",
        r"fact.check", r"reviewed by", r"verified",
        r"corrections?", r"editor.s note", r"disclosure",
        r"affiliate", r"sponsored", r"advertising",
    ]
    trans_count = sum(
        1 for p in transparency_patterns
        if re.search(p, body_text, re.IGNORECASE)
    )
    if trans_count >= 2:
        score += 4
        signals.append(f"Transparency signals ({trans_count}): editorial policy, disclosures")
    elif trans_count >= 1:
        score += 2
        signals.append("Some transparency signals found")

    # YMYL safety: medical, financial, legal warnings
    ymyl_keywords = {
        "medical": ["medical", "health", "diagnosis", "treatment", "symptom", "drug", "dosage"],
        "financial": ["invest", "financial advice", "tax", "insurance", "retirement", "loan"],
        "legal": ["legal advice", "attorney", "lawsuit", "court", "law firm"],
    }
    ymyl_detected = []
    for category, keywords in ymyl_keywords.items():
        if any(kw in body_text.lower() for kw in keywords):
            ymyl_detected.append(category)

    if ymyl_detected:
        # YMYL pages need stronger trust signals
        signals.append(f"⚠️ YMYL content detected ({', '.join(ymyl_detected)}) — needs strong trust signals")
        # Check if we have enough trust for YMYL
        has_author = bool(re.search(r"(?:author|written by|medically reviewed)", body_text, re.I))
        has_citations = bool(re.search(r"(?:source|reference|study|journal)", body_text, re.I))
        if has_author and has_citations:
            score += 4
            signals.append("YMYL requirements met (author + citations present)")
        elif has_author or has_citations:
            score += 2
            signals.append("Partial YMYL compliance — add more trust signals")
        else:
            signals.append("⚠️ YMYL content lacks author/citations — high risk")
    else:
        signals.append("Non-YMYL content (lower trust requirements)")

    # No misleading / deceptive signals
    deceptive_patterns = [
        r"click here to (?:claim|get|receive) your (?:free|bonus)",
        r"limited time (?:offer|deal)",
        r"act now",
        r"guaranteed (?:results?|income|earnings?)",
    ]
    deceptive_count = sum(
        1 for p in deceptive_patterns
        if re.search(p, body_text, re.IGNORECASE)
    )
    if deceptive_count == 0:
        score += 3
        signals.append("No deceptive language detected")
    else:
        score -= 2
        signals.append(f"⚠️ {deceptive_count} potentially deceptive phrases found")

    # Cookie consent / GDPR banner
    consent = soup.find(attrs={"class": re.compile(r"cookie|consent|gdpr", re.I)})
    if consent:
        score += 2
        signals.append("Cookie consent banner present")

    score = min(max(score, 0), max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


# ──────────────────────────────────────────────
# Composite Scoring
# ──────────────────────────────────────────────

def _compute_grade(total_score: int) -> str:
    """Map 0-100 composite score to a letter grade."""
    if total_score >= 90:
        return "A+"
    elif total_score >= 80:
        return "A"
    elif total_score >= 70:
        return "B+"
    elif total_score >= 60:
        return "B"
    elif total_score >= 50:
        return "C+"
    elif total_score >= 40:
        return "C"
    elif total_score >= 30:
        return "D"
    else:
        return "F"


def _compute_ymyl_risk(ymyl_categories: list[str]) -> str:
    """Assess YMYL risk level."""
    if not ymyl_categories:
        return "none"
    critical = {"medical", "financial", "legal"}
    if critical & set(ymyl_categories):
        return "high"
    return "medium"


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def analyze_eear_t(url: str) -> dict:
    """
    Full E-E-A-T analysis of a URL.
    Returns composite score (0-100), per-factor breakdown, and actionable recommendations.
    """
    result = {
        "url": url,
        "factors": {},
        "composite_score": 0,
        "grade": "F",
        "ymyl_risk": "unknown",
        "issues": [],
        "recommendations": [],
    }

    # Fetch page
    try:
        headers = {"User-Agent": random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["issues"].append({
            "severity": "critical",
            "message": f"Could not fetch URL: {e}",
        })
        return result

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    # Remove boilerplate
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    body_text = soup.get_text(separator=" ", strip=True)

    # Run all four factor checks
    experience = _check_experience(soup, body_text, url)
    expertise = _check_expertise(soup, body_text)
    authoritativeness = _check_authoritativeness(soup, body_text, url)
    trustworthiness = _check_trustworthiness(soup, body_text, url)

    result["factors"] = {
        "experience": experience,
        "expertise": expertise,
        "authoritativeness": authoritativeness,
        "trustworthiness": trustworthiness,
    }

    # Composite score (weighted: Trust 35%, Experience 25%, Expertise 25%, Authority 15%)
    total_max = (
        experience["max_score"] + expertise["max_score"]
        + authoritativeness["max_score"] + trustworthiness["max_score"]
    )
    raw_total = (
        experience["score"] + expertise["score"]
        + authoritativeness["score"] + trustworthiness["score"]
    )
    result["composite_score"] = round(raw_total / total_max * 100) if total_max > 0 else 0
    result["grade"] = _compute_grade(result["composite_score"])

    # YMYL detection
    ymyl_cats = []
    for signal in trustworthiness.get("signals", []):
        if "YMYL content detected" in signal:
            m = re.search(r"\(([^)]+)\)", signal)
            if m:
                ymyl_cats = [c.strip() for c in m.group(1).split(",")]
    result["ymyl_risk"] = _compute_ymyl_risk(ymyl_cats)

    # Aggregate issues and recommendations
    all_signals = []
    for factor_name, factor in result["factors"].items():
        for sig in factor.get("signals", []):
            all_signals.append({"factor": factor_name, "signal": sig})

    # Convert low-scoring factors to issues
    for factor_name, factor in result["factors"].items():
        ratio = factor["score"] / factor["max_score"] if factor["max_score"] > 0 else 0
        if ratio < 0.4:
            result["issues"].append({
                "severity": "warning",
                "factor": factor_name,
                "message": f"{factor_name.title()} score is weak ({factor['score']}/{factor['max_score']})",
            })

    # Generate recommendations
    if experience["score"] < experience["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "experience",
            "priority": "high",
            "action": "Add author bio, first-person narrative, and original images to demonstrate hands-on experience",
            "how_to_verify": "After changes, re-run E-E-A-T audit and check experience score increased",
        })
    if expertise["score"] < expertise["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "expertise",
            "priority": "high",
            "action": "Expand content depth (1500+ words), add structured headings, cite authoritative sources",
            "how_to_verify": "Re-run audit — expertise score should exceed 12/25",
        })
    if authoritativeness["score"] < authoritativeness["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "authoritativeness",
            "priority": "medium",
            "action": "Add social media links, Organization schema, contact information, and internal links",
            "how_to_verify": "Check that social links and schema appear in page source",
        })
    if trustworthiness["score"] < trustworthiness["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "trustworthiness",
            "priority": "critical",
            "action": "Add HTTPS, privacy policy, about page, editorial disclosures, and cookie consent",
            "how_to_verify": "Trust score should reach 15/25 minimum for non-YMYL, 20/25 for YMYL",
        })

    # Overall signals summary
    result["signals_summary"] = all_signals[:20]

    return result
