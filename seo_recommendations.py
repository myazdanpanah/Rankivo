"""
SEO AI Tools - AI SEO Recommendations Module
Analyzes audit results and uses AI to generate specific, actionable SEO fixes.
"""
from content_generator import generate_text


def analyze_audit_for_recommendations(audit_data: dict, provider: str = "ollama") -> str:
    """
    Build a detailed prompt from audit data for the AI to generate recommendations.
    Returns the AI-generated recommendations as a string.
    """
    if audit_data.get("error"):
        return "⚠️ Cannot generate recommendations — audit failed. Please fix the URL and try again."

    # Build structured context from audit
    url = audit_data.get("final_url", audit_data.get("url", ""))
    score = audit_data.get("score", 0)
    title = audit_data.get("page_title", "")
    desc = audit_data.get("meta_description", "")
    canonical = audit_data.get("canonical", "")
    wc = audit_data.get("word_count", 0)
    ratio = audit_data.get("text_to_html_ratio", 0)

    h1s = audit_data.get("headings", {}).get("h1", [])
    h2s = audit_data.get("headings", {}).get("h2", [])
    h3s = audit_data.get("headings", {}).get("h3", [])

    links = audit_data.get("links", {})
    images = audit_data.get("images", {})
    ka = audit_data.get("keyword_analysis", {})

    issues = audit_data.get("issues", [])
    issues_text = "\n".join(
        f"- [{i['severity'].upper()}] [{i['category']}] {i['message']}"
        for i in issues
    )

    prompt = f"""You are an expert SEO consultant. Analyze this audit data and provide specific, actionable recommendations to improve the page's SEO.

## URL: {url}
## Current SEO Score: {score}/100

## Meta Tags
- Title: "{title}" ({len(title)} chars)
- Meta Description: "{desc}" ({len(desc)} chars)
- Canonical: {canonical or "MISSING"}

## Content
- Word Count: {wc}
- Text/HTML Ratio: {ratio}%
- H1 Tags: {h1s if h1s else "MISSING"}
- H2 Tags: {h2s[:5] if h2s else "None"}
- H3 Tags: {h3s[:5] if h3s else "None"}

## Links & Images
- Internal Links: {links.get('internal_count', 0)}
- External Links: {links.get('external_count', 0)}
- Images: {images.get('total', 0)} ({images.get('alt_coverage', 0)}% with alt text)

## Keyword Analysis
- Keyword: {ka.get('keyword', 'N/A')}
- Exact Matches: {ka.get('exact_matches', 0)} ({ka.get('exact_density_pct', 0)}%)
- First Position: {ka.get('first_position_pct', -1)}%

## Detected Issues
{issues_text if issues_text else "No issues detected."}

## Your Task
Provide specific, prioritized recommendations organized by category:

### 1. 🔴 Critical Fixes (do these first)
### 2. 🟡 Important Improvements
### 3. 🔵 Quick Wins
### 4. 📝 Content Recommendations
### 5. 🔗 Link Strategy
### 6. 📊 Long-term Strategy

For EACH recommendation, provide:
- What specifically to change
- Why it matters for SEO
- An example of the improved version where applicable (e.g., suggested title, meta description)

Be concrete and actionable — not generic advice.
"""

    system_prompt = (
        "You are a world-class SEO consultant with 15+ years of experience. "
        "You provide specific, data-driven recommendations with concrete examples. "
        "Format your response in clean Markdown."
    )

    try:
        result = generate_text(prompt, provider=provider, system_prompt=system_prompt)
        return result
    except Exception as e:
        return f"⚠️ AI recommendation generation failed: {e}\n\nHere are the detected issues you can address manually:\n\n{issues_text}"


def generate_quick_wins(audit_data: dict) -> list[dict]:
    """
    Generate a list of quick wins based on the audit data (no AI needed).
    Returns a list of dicts with {action, impact, difficulty}.
    """
    if audit_data.get("error"):
        return []

    wins = []

    # Title issues
    title = audit_data.get("page_title", "")
    if not title:
        wins.append({
            "action": "Add a compelling page title with your target keyword",
            "impact": "High",
            "difficulty": "Easy",
            "example": "Use format: Primary Keyword | Secondary Keyword - Brand Name",
        })
    elif len(title) < 30:
        wins.append({
            "action": f"Expand your title tag (currently {len(title)} chars, aim for 50-60)",
            "impact": "High",
            "difficulty": "Easy",
            "example": "Add your primary keyword and a compelling modifier",
        })

    # Meta description
    desc = audit_data.get("meta_description", "")
    if not desc:
        wins.append({
            "action": "Write a meta description with target keyword and a call-to-action",
            "impact": "High",
            "difficulty": "Easy",
            "example": "Include primary keyword, describe the page value, add CTA (150-160 chars)",
        })

    # H1
    h1s = audit_data.get("headings", {}).get("h1", [])
    if not h1s:
        wins.append({
            "action": "Add an H1 tag with your primary keyword",
            "impact": "High",
            "difficulty": "Easy",
            "example": "Use one H1 per page, matching user search intent",
        })
    elif len(h1s) > 1:
        wins.append({
            "action": f"Reduce to one H1 tag (currently {len(h1s)})",
            "impact": "Medium",
            "difficulty": "Easy",
            "example": "Keep one H1, convert others to H2",
        })

    # Word count
    wc = audit_data.get("word_count", 0)
    if wc < 300:
        wins.append({
            "action": f"Significantly expand content (currently {wc} words, aim for 1500+)",
            "impact": "High",
            "difficulty": "Hard",
            "example": "Add sections: introduction, detailed guides, FAQs, conclusion",
        })
    elif wc < 800:
        wins.append({
            "action": f"Expand content (currently {wc} words, aim for 1000+)",
            "impact": "Medium",
            "difficulty": "Medium",
            "example": "Add examples, case studies, or a FAQ section",
        })

    # Images
    images = audit_data.get("images", {})
    if images.get("without_alt", 0) > 0:
        wins.append({
            "action": f"Add alt text to {images['without_alt']} image(s)",
            "impact": "Medium",
            "difficulty": "Easy",
            "example": "Describe the image content with relevant keywords naturally",
        })

    # Canonical
    if not audit_data.get("canonical"):
        wins.append({
            "action": "Add a canonical tag to prevent duplicate content issues",
            "impact": "Medium",
            "difficulty": "Easy",
            "example": '<link rel="canonical" href="https://yoursite.com/page" />',
        })

    # Keyword density
    ka = audit_data.get("keyword_analysis", {})
    if ka and ka.get("keyword"):
        if ka.get("exact_density_pct", 0) == 0:
            wins.append({
                "action": f"Include target keyword '{ka['keyword']}' in the body content",
                "impact": "High",
                "difficulty": "Medium",
                "example": "Use the keyword naturally 3-5 times in headings and body text",
            })
        elif ka.get("exact_density_pct", 0) > 3:
            wins.append({
                "action": "Reduce keyword density — risk of keyword stuffing",
                "impact": "Medium",
                "difficulty": "Easy",
                "example": "Use synonyms and related terms instead of repeating the exact keyword",
            })

    # Text/HTML ratio
    ratio = audit_data.get("text_to_html_ratio", 0)
    if ratio < 10:
        wins.append({
            "action": f"Increase text content relative to code (ratio: {ratio}%, aim for 15%+)",
            "impact": "Medium",
            "difficulty": "Medium",
            "example": "Add more body content, reduce bloated JavaScript/CSS",
        })

    # Links
    links = audit_data.get("links", {})
    if links.get("internal_count", 0) == 0:
        wins.append({
            "action": "Add internal links to other pages on your site",
            "impact": "Medium",
            "difficulty": "Easy",
            "example": "Link to 3-5 related pages using descriptive anchor text",
        })

    # Sort by impact
    impact_order = {"High": 0, "Medium": 1, "Low": 2}
    wins.sort(key=lambda w: impact_order.get(w["impact"], 2))

    return wins
