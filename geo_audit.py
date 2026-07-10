"""
Rankivo — GEO / AEO Audit Module
Evaluates pages for AI search optimization (Generative Engine Optimization).
Aligned with Google's AI Optimization Guide (May 2026).
Scores passage citability, entity presence, question headings, and AI-readiness.
"""
import re
import json
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


# ──────────────────────────────────────────────
# Entity database — domains that signal entity presence
# ──────────────────────────────────────────────

ENTITY_SIGNALS = {
    "wikipedia": {"weight": 1.0, "label": "Wikipedia"},
    "wikidata": {"weight": 0.9, "label": "Wikidata"},
    "linkedin.com": {"weight": 0.7, "label": "LinkedIn"},
    "github.com": {"weight": 0.6, "label": "GitHub"},
    "youtube.com": {"weight": 0.6, "label": "YouTube"},
    "reddit.com": {"weight": 0.5, "label": "Reddit"},
    "twitter.com": {"weight": 0.5, "label": "Twitter/X"},
    "x.com": {"weight": 0.5, "label": "X (Twitter)"},
    "facebook.com": {"weight": 0.4, "label": "Facebook"},
    "crunchbase.com": {"weight": 0.7, "label": "Crunchbase"},
    "producthunt.com": {"weight": 0.5, "label": "Product Hunt"},
    "g2.com": {"weight": 0.5, "label": "G2"},
    "trustpilot.com": {"weight": 0.5, "label": "Trustpilot"},
}


# ──────────────────────────────────────────────
# Passage Citability Analysis
# ──────────────────────────────────────────────

def _analyze_passage_citability(body_text: str) -> dict:
    """
    Score how citable the content is for AI systems.
    Ideal: self-contained 134-167 word answer blocks that AI can quote.
    """
    signals = []
    score = 0
    max_score = 25

    # Split into paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body_text) if len(p.strip()) > 20]

    if not paragraphs:
        return {"score": 0, "max_score": max_score, "signals": ["No substantive paragraphs found"]}

    # Count self-contained answer blocks (134-167 words)
    answer_blocks = []
    for para in paragraphs:
        words = para.split()
        wc = len(words)
        if 100 <= wc <= 250:
            # Check if it's self-contained (has subject, explanation)
            has_definition = bool(re.search(
                r'(?:is defined as|refers to|means|involves|consists of|is a|is the|are the)',
                para, re.IGNORECASE
            ))
            has_facts = bool(re.search(r'\d', para))  # has numbers/data
            has_structure = bool(re.search(r'(?:\. ){{2,}}', para))  # multiple sentences
            if has_definition or (has_facts and has_structure):
                answer_blocks.append({"text": para[:200], "word_count": wc})

    if len(answer_blocks) >= 3:
        score += 10
        signals.append(f"{len(answer_blocks)} citable answer blocks found (ideal: 134-167 words)")
    elif len(answer_blocks) >= 1:
        score += 5
        signals.append(f"{len(answer_blocks)} potential answer block(s) found")
    else:
        signals.append("No ideal-length answer blocks — AI may struggle to quote your content")

    # Question-answer pattern density
    qa_patterns = [
        r'(?:what|how|why|when|where|who|which|is|are|can|do|does)\s+.{10,}\?',
    ]
    questions = []
    for pattern in qa_patterns:
        questions.extend(re.findall(pattern, body_text, re.IGNORECASE))

    if len(questions) >= 5:
        score += 5
        signals.append(f"{len(questions)} questions in content (good for AI Q&A extraction)")
    elif len(questions) >= 2:
        score += 2
        signals.append(f"{len(questions)} questions found")
    else:
        signals.append("Few questions in content — add Q&A sections for AI citability")

    # Definition patterns (AI loves clear definitions)
    definition_patterns = [
        r'(?:is defined as|is a .{5,50} that|refers to|means that|can be described as)',
    ]
    defs = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in definition_patterns
    )
    if defs >= 3:
        score += 5
        signals.append(f"{defs} clear definitions (excellent for AI extraction)")
    elif defs >= 1:
        score += 2
        signals.append(f"{defs} definition(s) found")
    else:
        signals.append("No clear definitions — add 'X is...' statements for AI citability")

    # Numbered lists and bullet points (AI systems prefer structured data)
    lists = len(re.findall(r'(?:^|\n)\s*(?:\d+[\.\)]\s|[-*•]\s)', body_text))
    if lists >= 5:
        score += 3
        signals.append(f"{lists} list items (structured content is AI-friendly)")
    elif lists >= 1:
        score += 1
        signals.append(f"{lists} list items found")

    # Statistics and data points
    stats = len(re.findall(r'\d+(?:\.\d+)?(?:%| percent| million| billion| thousand)', body_text, re.I))
    if stats >= 3:
        score += 2
        signals.append(f"{stats} data points / statistics (AI systems cite data-rich content)")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


def _analyze_question_headings(soup) -> dict:
    """
    Check for question-based heading hierarchy (H2/H3 with ? or question words).
    AI systems prefer question-based headings for structured answers.
    """
    signals = []
    score = 0
    max_score = 15

    question_words = [
        "what", "how", "why", "when", "where", "who", "which",
        "is", "are", "can", "do", "does", "should", "will",
    ]

    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
    h3s = [h.get_text(strip=True) for h in soup.find_all("h3")]
    all_headings = h2s + h3s

    question_headings = []
    for h in all_headings:
        h_lower = h.lower().strip()
        if "?" in h_lower:
            question_headings.append(h)
        elif any(h_lower.startswith(qw + " ") for qw in question_words):
            question_headings.append(h)

    if len(question_headings) >= 5:
        score += 12
        signals.append(f"{len(question_headings)} question-based headings (excellent for AI)")
    elif len(question_headings) >= 3:
        score += 8
        signals.append(f"{len(question_headings)} question-based headings (good)")
    elif len(question_headings) >= 1:
        score += 4
        signals.append(f"{len(question_headings)} question-based heading(s)")
    else:
        signals.append("No question-based headings — add How/What/Why H2s for AI optimization")

    # Heading depth (H2 > H3 > H4 = better hierarchy)
    if len(h2s) >= 3 and len(h3s) >= 2:
        score += 3
        signals.append(f"Good heading depth: {len(h2s)} H2s, {len(h3s)} H3s")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


def _analyze_entity_presence(soup, body_text: str, url: str) -> dict:
    """
    Check entity presence across platforms and in structured data.
    AI systems cross-reference entities across Wikipedia, Reddit, LinkedIn, etc.
    """
    signals = []
    score = 0
    max_score = 20

    # Find all outbound links
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if href.startswith("http"):
            links.append(href)

    # Check for entity platform presence
    found_entities = []
    for link in links:
        for domain, info in ENTITY_SIGNALS.items():
            if domain in link:
                found_entities.append(info["label"])

    found_entities = list(set(found_entities))
    if len(found_entities) >= 4:
        score += 10
        signals.append(f"Entity presence on {len(found_entities)} platforms: {', '.join(found_entities)}")
    elif len(found_entities) >= 2:
        score += 6
        signals.append(f"Entity presence on {len(found_entities)} platforms: {', '.join(found_entities)}")
    elif len(found_entities) >= 1:
        score += 3
        signals.append(f"Entity presence on: {', '.join(found_entities)}")
    else:
        signals.append("No entity platform links found — add LinkedIn, GitHub, Wikipedia links")

    # Schema.org entity signals
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                items = data.get("@graph", [data]) if "@graph" in data else [data]
                for item in items:
                    if isinstance(item, dict):
                        if item.get("sameAs"):
                            score += 3
                            same_as = item["sameAs"]
                            if isinstance(same_as, list):
                                signals.append(f"Schema sameAs: {len(same_as)} links")
                            else:
                                signals.append(f"Schema sameAs present")
                        if item.get("@id"):
                            score += 2
                            signals.append("Schema @id present (entity identity)")
                        if item.get("knowsAbout"):
                            score += 2
                            signals.append("Schema knowsAbout present (topical authority)")
                            break
        except Exception:
            pass

    # Brand name mentions in body text (entity salience)
    brand_patterns = [
        r"(?:about us|our company|our team|our mission|our story)",
        r"(?:founded|established|since \d{4})",
    ]
    brand_count = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in brand_patterns
    )
    if brand_count >= 2:
        score += 3
        signals.append(f"Brand entity signals ({brand_count} mentions)")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


def _analyze_attribution_density(body_text: str, soup) -> dict:
    """
    Check attribution density — how well sources are cited.
    AI systems prefer content with clear attribution.
    """
    signals = []
    score = 0
    max_score = 10

    # Citation patterns
    citation_patterns = [
        r'(?:according to|source:|cited from|based on|research by|study by)',
        r'(?:\[\d+\]|\(\d{4}\))',  # academic citations
        r'(?:published in|reported by|data from)',
    ]
    citations = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in citation_patterns
    )

    if citations >= 5:
        score += 6
        signals.append(f"{citations} attribution/citation signals (excellent)")
    elif citations >= 2:
        score += 3
        signals.append(f"{citations} attribution signals found")
    elif citations >= 1:
        score += 1
        signals.append(f"{citations} attribution signal found")
    else:
        signals.append("No citations or attribution found — add source references")

    # External links with descriptive anchor text
    ext_links = 0
    cited_domains = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            parsed = urlparse(href)
            if parsed.netloc:
                ext_links += 1
                cited_domains.add(parsed.netloc)

    if ext_links >= 5:
        score += 4
        signals.append(f"{ext_links} external citations to {len(cited_domains)} domains")
    elif ext_links >= 2:
        score += 2
        signals.append(f"{ext_links} external links")

    score = min(score, max_score)
    return {"score": score, "max_score": max_score, "signals": signals}


# ──────────────────────────────────────────────
# Composite GEO Score
# ──────────────────────────────────────────────

def _compute_geo_grade(total_score: int) -> str:
    if total_score >= 85:
        return "A+"
    elif total_score >= 75:
        return "A"
    elif total_score >= 65:
        return "B+"
    elif total_score >= 55:
        return "B"
    elif total_score >= 45:
        return "C+"
    elif total_score >= 35:
        return "C"
    elif total_score >= 25:
        return "D"
    else:
        return "F"


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_geo(url: str) -> dict:
    """
    Full GEO/AEO audit for a URL.
    Evaluates AI search readiness: passage citability, question headings,
    entity presence, attribution density.
    """
    result = {
        "url": url,
        "factors": {},
        "composite_score": 0,
        "grade": "F",
        "ai_readiness": "low",
        "issues": [],
        "recommendations": [],
    }

    # Fetch page
    try:
        headers = {"User-Agent": _random_ua()}
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

    # Get body text
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(separator=" ", strip=True)

    # Run all GEO factor checks
    passage_citability = _analyze_passage_citability(body_text)
    question_headings = _analyze_question_headings(soup)
    entity_presence = _analyze_entity_presence(soup, body_text, url)
    attribution_density = _analyze_attribution_density(body_text, soup)

    result["factors"] = {
        "passage_citability": passage_citability,
        "question_headings": question_headings,
        "entity_presence": entity_presence,
        "attribution_density": attribution_density,
    }

    # Composite score
    total_max = (
        passage_citability["max_score"] + question_headings["max_score"]
        + entity_presence["max_score"] + attribution_density["max_score"]
    )
    raw_total = (
        passage_citability["score"] + question_headings["score"]
        + entity_presence["score"] + attribution_density["score"]
    )
    result["composite_score"] = round(raw_total / total_max * 100) if total_max > 0 else 0
    result["grade"] = _compute_geo_grade(result["composite_score"])

    # AI readiness level
    if result["composite_score"] >= 75:
        result["ai_readiness"] = "high"
    elif result["composite_score"] >= 55:
        result["ai_readiness"] = "medium"
    elif result["composite_score"] >= 35:
        result["ai_readiness"] = "low"
    else:
        result["ai_readiness"] = "very_low"

    # Generate recommendations
    if passage_citability["score"] < passage_citability["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "passage_citability",
            "priority": "high",
            "action": "Create self-contained 134-167 word answer blocks. Start paragraphs with clear definitions ('X is...'). Add numbered lists and statistics.",
            "how_to_verify": "Re-run GEO audit — passage citability should exceed 12/25",
        })
    if question_headings["score"] < question_headings["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "question_headings",
            "priority": "high",
            "action": "Convert H2s to question format: 'What is X?', 'How to do Y?', 'Why does Z matter?'",
            "how_to_verify": "Re-run audit — should detect 3+ question-based headings",
        })
    if entity_presence["score"] < entity_presence["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "entity_presence",
            "priority": "medium",
            "action": "Add sameAs links to social profiles (LinkedIn, GitHub, YouTube). Add Organization schema with @id and knowsAbout.",
            "how_to_verify": "Check schema has sameAs array pointing to 3+ platforms",
        })
    if attribution_density["score"] < attribution_density["max_score"] * 0.5:
        result["recommendations"].append({
            "factor": "attribution_density",
            "priority": "medium",
            "action": "Cite sources: 'According to [source]...', add external links to authoritative references, include data with attribution.",
            "how_to_verify": "Re-run audit — should detect 3+ attribution signals",
        })

    # Meta description analysis (AI systems use this for snippet selection)
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"]
        if "?" in desc:
            result["factors"]["meta_question"] = True
        if len(desc) > 120:
            result["factors"]["meta_descriptive"] = True
    else:
        result["issues"].append({
            "severity": "warning",
            "message": "Missing meta description — AI systems use this for snippet selection",
        })

    return result
