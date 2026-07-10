"""
Rankivo — Search Experience Optimization (SXO) Audit Module
Analyzes SERP intent vs page-type alignment, user persona scoring,
and search experience quality.
"""
import re
import requests
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# Page Type Taxonomy
# ──────────────────────────────────────────────

PAGE_TYPES = {
    "article": {
        "signals": [r'\b(?:article|blog|post|guide|tutorial|how[- ]to|step[- ]by[- ]step)\b'],
        "content_signals": {"word_count_min": 800, "has_headings": True, "has_images": True},
        "label": "Article / Blog Post",
    },
    "product": {
        "signals": [r'\b(?:buy|price|cart|shop|order|add to|purchase|قیمت|خرید)\b'],
        "content_signals": {"has_price": True, "has_buy_button": True},
        "label": "Product / E-commerce",
    },
    "landing": {
        "signals": [r'\b(?:sign up|start free|get started|try|demo|request|contact us|ارائه)\b'],
        "content_signals": {"has_cta": True, "word_count_max": 1500},
        "label": "Landing Page",
    },
    "tool": {
        "signals": [r'\b(?:calculator|tool|checker|generator|optimizer|ابزار|ماشین حساب)\b'],
        "content_signals": {"has_interactive": True},
        "label": "Tool / Calculator",
    },
    "listing": {
        "signals": [r'\b(?:top \d+|best \d+|list of|directory|categories|لیست|بهترین)\b'],
        "content_signals": {"has_list": True, "word_count_min": 1000},
        "label": "Listicle / Directory",
    },
    "comparison": {
        "signals": [r'\b(?:vs\.?|versus|compare|comparison|alternative|compared to|مقایسه)\b'],
        "content_signals": {"has_table": True, "word_count_min": 1000},
        "label": "Comparison Page",
    },
    "definition": {
        "signals": [r'\b(?:what is|definition|meaning|defined as|refers to|چیست|تعریف)\b'],
        "content_signals": {"has_definition": True, "word_count_min": 500},
        "label": "Definition / Explainer",
    },
    "local": {
        "signals": [r'\b(?:near me|in \w+|location|address|directions|hours|نزدیک|آدرس)\b'],
        "content_signals": {"has_map": True, "has_address": True},
        "label": "Local Business Page",
    },
}


def _classify_page_type(soup, body_text: str, url: str) -> dict:
    """Classify the page type based on signals."""
    scores = {}
    url_lower = url.lower()
    text_lower = body_text.lower()

    for ptype, config in PAGE_TYPES.items():
        score = 0
        matched_signals = []

        # URL signals
        for pattern in config["signals"]:
            if re.search(pattern, url_lower) or re.search(pattern, text_lower[:2000]):
                score += 2
                matched_signals.append(pattern)

        # Content signals
        content = config.get("content_signals", {})
        if content.get("word_count_min"):
            wc = len(body_text.split())
            if wc >= content["word_count_min"]:
                score += 1
        if content.get("word_count_max"):
            wc = len(body_text.split())
            if wc <= content["word_count_max"]:
                score += 1
        if content.get("has_headings"):
            h2s = soup.find_all("h2")
            if len(h2s) >= 3:
                score += 1
        if content.get("has_price"):
            if re.search(r'[\$€£¥]\d+|price|قیمت', text_lower):
                score += 2
        if content.get("has_buy_button"):
            if re.search(r'(?:buy|cart|add to|order|خرید)', text_lower):
                score += 2
        if content.get("has_list"):
            lists = soup.find_all(["ol", "ul"])
            if len(lists) >= 2:
                score += 1
        if content.get("has_table"):
            tables = soup.find_all("table")
            if tables:
                score += 1
        if content.get("has_map"):
            if soup.find("iframe", src=re.compile(r"maps", re.I)):
                score += 2
        if content.get("has_definition"):
            if re.search(r'(?:is defined as|refers to|means|is a .{5,50} that)', text_lower):
                score += 2
        if content.get("has_cta"):
            if re.search(r'(?:sign up|start|try|get|learn more|contact)', text_lower):
                score += 1

        if score > 0:
            scores[ptype] = {"score": score, "signals": matched_signals}

    if not scores:
        return {"type": "generic", "label": "General Page", "confidence": 0, "scores": {}}

    best = max(scores.items(), key=lambda x: x[1]["score"])
    total_score = sum(s["score"] for s in scores.values())
    confidence = round(best[1]["score"] / max(total_score, 1) * 100)

    return {
        "type": best[0],
        "label": PAGE_TYPES[best[0]]["label"],
        "confidence": confidence,
        "all_scores": {k: v["score"] for k, v in scores.items()},
    }


# ──────────────────────────────────────────────
# Search Intent Analysis
# ──────────────────────────────────────────────

INTENT_SIGNALS = {
    "informational": {
        "patterns": [
            r'\b(?:how to|what is|why|guide|tutorial|learn|understand|explain|آموزش|راهنما|چیست)\b',
        ],
        "content_signals": ["long_form", "headings", "definitions", "examples"],
    },
    "transactional": {
        "patterns": [
            r'\b(?:buy|purchase|order|price|cheap|deal|discount|خرید|قیمت|تخفیف)\b',
        ],
        "content_signals": ["price", "buy_button", "cta", "urgency"],
    },
    "navigational": {
        "patterns": [
            r'\b(?:login|official|website|app|homepage|ورود|سایت رسمی)\b',
        ],
        "content_signals": ["brand_name", "single_focus"],
    },
    "commercial": {
        "patterns": [
            r'\b(?:best|top|review|vs|comparison|alternative|بهترین|مقایسه|نقد)\b',
        ],
        "content_signals": ["comparisons", "ratings", "pros_cons"],
    },
}


def _analyze_intent_alignment(page_type: str, body_text: str) -> dict:
    """Analyze if the page content aligns with search intent."""
    text_lower = body_text.lower()
    intent_scores = {}

    for intent, config in INTENT_SIGNALS.items():
        score = 0
        for pattern in config["patterns"]:
            matches = len(re.findall(pattern, text_lower))
            score += matches
        intent_scores[intent] = score

    # Determine dominant intent
    if not intent_scores or max(intent_scores.values()) == 0:
        detected_intent = "informational"
    else:
        detected_intent = max(intent_scores.items(), key=lambda x: x[1])[0]

    # Check alignment with page type
    alignment_map = {
        "article": "informational",
        "product": "transactional",
        "landing": "transactional",
        "tool": "transactional",
        "listing": "commercial",
        "comparison": "commercial",
        "definition": "informational",
        "local": "transactional",
    }

    expected_intent = alignment_map.get(page_type, "informational")
    is_aligned = detected_intent == expected_intent

    return {
        "detected_intent": detected_intent,
        "expected_intent": expected_intent,
        "is_aligned": is_aligned,
        "intent_scores": intent_scores,
        "issue": None if is_aligned else f"Page type '{page_type}' expects {expected_intent} intent but content shows {detected_intent}",
    }


# ──────────────────────────────────────────────
# User Persona Scoring
# ──────────────────────────────────────────────

PERSONAS = {
    "researcher": {
        "signals": [r'\b(?:research|study|data|analysis|findings|evidence|paper)\b'],
        "label": "Researcher / Academic",
    },
    "buyer": {
        "signals": [r'\b(?:buy|price|purchase|deal|discount|offer|free trial)\b'],
        "label": "Buyer / Decision Maker",
    },
    "expert": {
        "signals": [r'\b(?:advanced|technical|implementation|architecture|enterprise|api)\b'],
        "label": "Expert / Developer",
    },
    "casual": {
        "signals": [r'\b(?:easy|simple|beginner|quick|what is|introduction|basics)\b'],
        "label": "Casual / Beginner",
    },
}


def _score_personas(body_text: str) -> dict:
    """Score how well the page serves different user personas."""
    text_lower = body_text.lower()
    scores = {}

    for persona, config in PERSONAS.items():
        count = 0
        for pattern in config["signals"]:
            count += len(re.findall(pattern, text_lower))
        scores[persona] = {
            "score": count,
            "label": config["label"],
            "coverage": "high" if count >= 5 else "medium" if count >= 2 else "low",
        }

    # Determine primary persona
    primary = max(scores.items(), key=lambda x: x[1]["score"])[0] if scores else "casual"

    return {
        "scores": scores,
        "primary_persona": primary,
        "primary_label": scores[primary]["label"],
        "coverage": scores[primary]["coverage"],
    }


# ──────────────────────────────────────────────
# Content Quality Signals
# ──────────────────────────────────────────────

def _analyze_content_quality(soup, body_text: str) -> dict:
    """Analyze content quality signals for SXO."""
    words = body_text.split()
    wc = len(words)
    h2s = soup.find_all("h2")
    h3s = soup.find_all("h3")
    images = soup.find_all("img")
    lists = soup.find_all(["ol", "ul"])
    tables = soup.find_all("table")

    # Readability (simple approximation)
    sentences = re.split(r'[.!?]+', body_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    avg_sentence_length = wc / max(len(sentences), 1)

    # Filler detection
    filler_patterns = [
        r'\b(?:in conclusion|to sum up|overall|basically|actually|really|very|just)\b',
        r'\b(?:it is important to note|it should be noted|needless to say)\b',
    ]
    filler_count = sum(
        len(re.findall(p, body_text, re.IGNORECASE))
        for p in filler_patterns
    )

    # Question density
    questions = len(re.findall(r'\?', body_text))

    return {
        "word_count": wc,
        "heading_count": len(h2s) + len(h3s),
        "h2_count": len(h2s),
        "h3_count": len(h3s),
        "image_count": len(images),
        "list_count": len(lists),
        "table_count": len(tables),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(avg_sentence_length, 1),
        "question_count": questions,
        "filler_count": filler_count,
        "readability": "good" if 15 <= avg_sentence_length <= 25 else "complex" if avg_sentence_length > 25 else "simple",
    }


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def audit_sxo(url: str) -> dict:
    """
    Full Search Experience Optimization audit for a URL.
    Classifies page type, analyzes intent alignment, and scores personas.
    """
    result = {
        "url": url,
        "page_type": {},
        "intent_alignment": {},
        "persona_scores": {},
        "content_quality": {},
        "issues": [],
        "recommendations": [],
        "score": 100,
    }

    # Fetch page
    try:
        headers = {"User-Agent": _random_ua()}
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        result["issues"].append({"severity": "critical", "message": f"Could not fetch URL: {e}"})
        result["score"] = 0
        return result

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    # Remove boilerplate
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(separator=" ", strip=True)

    # Classify page type
    result["page_type"] = _classify_page_type(soup, body_text, url)

    # Analyze intent alignment
    result["intent_alignment"] = _analyze_intent_alignment(result["page_type"]["type"], body_text)

    # Score personas
    result["persona_scores"] = _score_personas(body_text)

    # Content quality
    result["content_quality"] = _analyze_content_quality(soup, body_text)

    # Generate issues
    if result["intent_alignment"].get("issue"):
        result["issues"].append({
            "severity": "warning",
            "message": result["intent_alignment"]["issue"],
        })
        result["score"] -= 15

    if result["content_quality"]["word_count"] < 300:
        result["issues"].append({
            "severity": "warning",
            "message": f"Thin content ({result['content_quality']['word_count']} words) — aim for 800+",
        })
        result["score"] -= 10

    if result["content_quality"]["h2_count"] < 2:
        result["issues"].append({
            "severity": "info",
            "message": "Few headings — add H2/H3 structure for better scanability",
        })
        result["score"] -= 5

    if result["content_quality"]["image_count"] == 0:
        result["issues"].append({
            "severity": "info",
            "message": "No images — visual content improves engagement",
        })
        result["score"] -= 3

    if result["persona_scores"]["coverage"] == "low":
        result["issues"].append({
            "severity": "info",
            "message": f"Content primarily serves {result['persona_scores']['primary_label']} — consider broadening appeal",
        })

    # Generate recommendations
    page_type = result["page_type"]["type"]
    intent = result["intent_alignment"]["detected_intent"]

    if intent == "informational":
        result["recommendations"].append(
            "Add clear definitions, step-by-step instructions, and examples for informational queries"
        )
    elif intent == "transactional":
        result["recommendations"].append(
            "Include prominent CTAs, pricing, and urgency signals for transactional pages"
        )
    elif intent == "commercial":
        result["recommendations"].append(
            "Add comparison tables, pros/cons lists, and ratings for commercial investigation"
        )

    if result["content_quality"]["question_count"] < 3:
        result["recommendations"].append(
            "Add question-based headings (H2/H3 with ?) for featured snippet opportunities"
        )

    result["score"] = max(0, min(100, result["score"]))
    return result
