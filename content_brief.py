"""
Rankivo — Content Brief Generator Module
Combines topic research, keyword data, competitor analysis,
and SERP signals into structured content briefs.
"""
import re
import requests
from datetime import datetime
from urllib.parse import urlparse
from config import REQUEST_TIMEOUT, USER_AGENTS, _safe_print
import random


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


# ──────────────────────────────────────────────
# Heading Outline Generator
# ──────────────────────────────────────────────

def _generate_heading_outline(
    topic: str,
    competitor_headings: list[str],
    keywords: list[str],
    intent: str = "informational",
) -> list[dict]:
    """Generate a recommended heading outline based on competitor analysis."""
    outline = []

    # H1: Primary keyword + compelling modifier
    primary_kw = keywords[0] if keywords else topic
    modifiers = {
        "informational": ["Guide", "Complete Guide", "Everything You Need to Know", "Explained"],
        "transactional": ["Buy", "Best", "Top", "Deals"],
        "commercial": ["Best", "Top", "vs", "Comparison", "Review"],
        "navigational": ["Official", "Login", "Homepage"],
    }
    modifier = random.choice(modifiers.get(intent, modifiers["informational"]))
    outline.append({"level": "H1", "text": f"{modifier}: {primary_kw}"})

    # Extract common H2 patterns from competitors
    competitor_h2s = [h for h in competitor_headings if len(h) > 5][:20]

    # Standard H2 sections based on intent
    if intent == "informational":
        standard_h2s = [
            f"What is {primary_kw}?",
            f"Why {primary_kw} Matters",
            f"How to Get Started with {primary_kw}",
            f"Best Practices for {primary_kw}",
            f"Common Mistakes to Avoid",
            f"FAQ: {primary_kw}",
        ]
    elif intent == "commercial":
        standard_h2s = [
            f"Top {primary_kw} Options in 2026",
            f"Comparison Table",
            f"Pros and Cons",
            f"Pricing Overview",
            f"Which {primary_kw} is Right for You?",
            f"FAQ",
        ]
    elif intent == "transactional":
        standard_h2s = [
            f"Why Choose {primary_kw}?",
            f"Features & Benefits",
            f"Pricing & Plans",
            f"How to Buy {primary_kw}",
            f"Customer Reviews",
            f"FAQ",
        ]
    else:
        standard_h2s = [
            f"About {primary_kw}",
            f"Key Features",
            f"How It Works",
            f"FAQ",
        ]

    # Merge competitor insights with standard outline
    used = set()
    for h2 in standard_h2s:
        if h2.lower() not in used:
            outline.append({"level": "H2", "text": h2, "source": "recommended"})
            used.add(h2.lower())

    # Add competitor-derived H2s that aren't covered
    for ch in competitor_h2s[:8]:
        ch_lower = ch.lower().strip()
        if ch_lower not in used and not any(ch_lower in u for u in used):
            outline.append({"level": "H2", "text": ch, "source": "competitor"})
            used.add(ch_lower)

    # Add H3s under key sections
    h3_suggestions = [
        f"Step 1: Research",
        f"Step 2: Plan",
        f"Step 3: Execute",
        f"Step 4: Measure",
    ]
    outline.append({"level": "H3", "text": h3_suggestions[0], "parent": "How to Get Started"})

    return outline


# ──────────────────────────────────────────────
# Internal Link Recommendations
# ──────────────────────────────────────────────

def _suggest_internal_links(topic: str, keywords: list[str]) -> list[dict]:
    """Suggest internal link topics based on the content topic."""
    suggestions = []

    # Related topics
    related = [
        {"topic": f"{topic} alternatives", "anchor": f"alternative {topic} options"},
        {"topic": f"{topic} vs competitors", "anchor": f"compare {topic}"},
        {"topic": f"how to use {topic}", "anchor": f"{topic} tutorial"},
        {"topic": f"{topic} pricing", "anchor": f"{topic} cost"},
        {"topic": f"{topic} reviews", "anchor": f"{topic} customer reviews"},
    ]

    for r in related[:5]:
        suggestions.append({
            "suggested_page": r["topic"],
            "anchor_text": r["anchor"],
            "context": f"Link naturally within a relevant section about {r['topic']}",
        })

    return suggestions


# ──────────────────────────────────────────────
# Competitor Angle Analysis
# ──────────────────────────────────────────────

def _analyze_competitor_angles(competitor_data: list[dict]) -> dict:
    """Analyze what angles competitors are using."""
    angles = {
        "unique_angles": [],
        "common_themes": [],
        "content_gaps": [],
        "length_distribution": {},
    }

    if not competitor_data:
        return angles

    # Word count distribution
    word_counts = [c.get("word_count", 0) for c in competitor_data if c.get("word_count")]
    if word_counts:
        avg = sum(word_counts) // len(word_counts)
        angles["length_distribution"] = {
            "min": min(word_counts),
            "max": max(word_counts),
            "average": avg,
            "recommended": max(avg, 1500),
        }

    # Collect all H2 headings
    all_h2s = []
    for comp in competitor_data:
        h2s = comp.get("h2", [])
        all_h2s.extend(h2s)

    # Find common themes (headings that appear in 2+ competitors)
    from collections import Counter
    h2_lower = [h.lower().strip() for h in all_h2s if h]
    theme_counts = Counter(h2_lower)
    common = [(h, c) for h, c in theme_counts.most_common(10) if c >= 2]
    angles["common_themes"] = [{"theme": h, "count": c} for h, c in common]

    return angles


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def generate_content_brief(
    topic: str,
    target_keywords: list[str] = None,
    competitor_data: list[dict] = None,
    intent: str = "informational",
    language: str = "en",
) -> dict:
    """
    Generate a comprehensive content brief for a topic.
    
    Args:
        topic: Main topic/keyword
        target_keywords: List of target keywords
        competitor_data: Competitor analysis data from topic_researcher
        intent: Search intent (informational, transactional, commercial, navigational)
        language: Content language (en, fa, etc.)
    
    Returns:
        Complete content brief with outline, keywords, and recommendations
    """
    if target_keywords is None:
        target_keywords = [topic]
    if competitor_data is None:
        competitor_data = []

    # Collect competitor headings
    competitor_headings = []
    for comp in competitor_data:
        for level in ["h1", "h2", "h3"]:
            competitor_headings.extend(comp.get(level, []))

    # Generate heading outline
    outline = _generate_heading_outline(topic, competitor_headings, target_keywords, intent)

    # Analyze competitor angles
    angles = _analyze_competitor_angles(competitor_data)

    # Internal link suggestions
    internal_links = _suggest_internal_links(topic, target_keywords)

    # Word count recommendation
    wc_recommended = 1500
    if angles.get("length_distribution", {}).get("recommended"):
        wc_recommended = angles["length_distribution"]["recommended"]

    # Build the brief
    brief = {
        "topic": topic,
        "language": language,
        "intent": intent,
        "primary_keyword": target_keywords[0] if target_keywords else topic,
        "secondary_keywords": target_keywords[1:10] if len(target_keywords) > 1 else [],

        "heading_outline": outline,
        "word_count_target": wc_recommended,
        "competitor_word_count": angles.get("length_distribution", {}),

        "internal_link_suggestions": internal_links,
        "competitor_angles": angles,

        "seo_checklist": [
            f"Include primary keyword '{target_keywords[0]}' in H1, first paragraph, and 2-3 H2s",
            f"Write {wc_recommended}+ words of comprehensive content",
            "Use question-based H2s for featured snippets",
            "Add 3-5 internal links to related pages",
            "Include 2-3 external links to authoritative sources",
            "Add images with descriptive alt text",
            "Include a FAQ section with 3-5 questions",
            "Add structured data (Article schema)",
        ],

        "meta_recommendations": {
            "title_format": f"{topic} [Complete Guide {__import__('datetime').datetime.now().year}]",
            "title_length": "50-60 characters",
            "meta_description": f"Learn everything about {topic}. {', '.join(target_keywords[:3])}. Expert guide with step-by-step instructions.",
            "meta_description_length": "150-160 characters",
            "year": datetime.now().year,
        },
    }

    # Language-specific adjustments
    if language == "fa":
        brief["seo_checklist"].extend([
            "تمامی عناوین به زبان فارسی باشد",
            " slug URL به انگلیسی باشد",
            "از کلمات کلیدی فارسی به صورت طبیعی استفاده شود",
        ])

    return brief
