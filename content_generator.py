"""
SEO AI Tools - AI Content Generator
Pluggable backend: Ollama (local), OpenAI, Anthropic Claude, Google Gemini.
"""
import requests
from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    DEFAULT_ARTICLE_WORD_COUNT,
    DEFAULT_ARTICLE_TONE,
    DEFAULT_ARTICLE_STYLE,
)


# ──────────────────────────────────────────────
# Provider abstraction
# ──────────────────────────────────────────────


def _call_ollama(user_prompt: str, system_prompt: str = "") -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
    }
    resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"]


def _call_openai(user_prompt: str, system_prompt: str = "") -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    resp = client.chat.completions.create(model=OPENAI_MODEL, messages=messages, temperature=0.7)
    return resp.choices[0].message.content


def _call_claude(user_prompt: str, system_prompt: str = "") -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return resp.content[0].text


def _call_gemini(user_prompt: str, system_prompt: str = "") -> str:
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        system_instruction=system_prompt if system_prompt else None,
    )
    resp = model.generate_content(user_prompt)
    return resp.text


PROVIDERS = {
    "ollama": _call_ollama,
    "openai": _call_openai,
    "anthropic": _call_claude,
    "gemini": _call_gemini,
}


def get_available_providers() -> list[str]:
    """Return list of providers that have credentials configured."""
    available = []
    if _check_ollama():
        available.append("ollama")
    if OPENAI_API_KEY:
        available.append("openai")
    if ANTHROPIC_API_KEY:
        available.append("anthropic")
    if GOOGLE_API_KEY:
        available.append("gemini")
    return available


def _check_ollama() -> bool:
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def generate_text(user_prompt: str, provider: str = "ollama", system_prompt: str = "") -> str:
    """Call the chosen AI provider."""
    func = PROVIDERS.get(provider)
    if not func:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
    return func(user_prompt, system_prompt)


# ──────────────────────────────────────────────
# SEO Article Prompts
# ──────────────────────────────────────────────


def build_article_prompt(
    topic: str,
    target_keywords: list[str],
    people_also_ask: list[str] | None = None,
    serp_context: list[dict] | None = None,
    research_data: dict | None = None,
    word_count: int = DEFAULT_ARTICLE_WORD_COUNT,
    tone: str = DEFAULT_ARTICLE_TONE,
    style: str = DEFAULT_ARTICLE_STYLE,
    language: str = "en",
) -> str:
    """Build a detailed prompt for SEO article generation."""

    primary_kw = target_keywords[0] if target_keywords else topic
    kw_list = ", ".join(f'"{k}"' for k in target_keywords[:20])

    # ── Research context (from internet research) ──
    research_section = ""
    if research_data:
        # Key facts extracted from top content
        facts = research_data.get("key_facts", [])
        if facts:
            facts_text = "\n".join(f"  - {f}" for f in facts[:15])
            research_section += f"\n## Key Facts & Statistics (verified from top sources):\n{facts_text}\n"

        # Content gaps to exploit
        gaps = research_data.get("content_gaps", [])
        if gaps:
            gaps_text = "\n".join(f"  - {g}" for g in gaps[:8])
            research_section += f"\n## Content Gaps to Exploit (competitors miss these):\n{gaps_text}\n"

        # Recommended structure from competitor analysis
        rec = research_data.get("recommended_structure", {})
        if rec:
            suggested_wc = rec.get("suggested_word_count", word_count)
            common_h2s = rec.get("common_h2_patterns", [])[:5]
            research_section += f"\n## Competitor Analysis:\n"
            research_section += f"- Competitor average word count: {rec.get('competitor_avg_word_count', 'N/A')}\n"
            research_section += f"- Recommended word count: {suggested_wc}\n"
            if common_h2s:
                research_section += f"- Common H2 patterns in top results: {', '.join(common_h2s[:5])}\n"
            if rec.get("has_lists_in_competitors"):
                research_section += "- Top competitors use lists/bullet points\n"
            if rec.get("has_tables_in_competitors"):
                research_section += "- Top competitors use tables/comparisons\n"

        # Competitor headings for structure inspiration
        top_headings = research_data.get("top_headings", [])
        if top_headings:
            h2s = [h for h in top_headings if h and len(h) > 5][:15]
            if h2s:
                research_section += f"\n## Competitor Heading Structure (DO NOT copy, use for inspiration):\n"
                for h in h2s:
                    research_section += f"  - {h}\n"

    # ── People Also Ask ──
    paa_section = ""
    all_paa = list(people_also_ask or [])
    # Also use PAA from research data
    if research_data:
        # PAA might be in search results snippets
        pass
    if all_paa:
        questions = "\n".join(f"  - {q}" for q in all_paa[:12])
        paa_section = f"\n## People Also Ask (answer ALL of these in your article):\n{questions}\n"

    # ── SERP Context (competitor snippets) ──
    serp_section = ""
    serp_data = list(serp_context or [])
    if research_data:
        for comp in research_data.get("competitor_analysis", [])[:5]:
            serp_data.append({
                "title": comp.get("title", ""),
                "snippet": comp.get("description", ""),
            })
    if serp_data:
        snippets = "\n".join(
            f"  - {r.get('title', '')}: {r.get('snippet', '')[:200]}"
            for r in serp_data[:5]
        )
        serp_section = f"\n## Top-ranking competitor content to surpass (do NOT copy):\n{snippets}\n"

    # Language-specific instructions
    if language == "fa":
        lang_instruction = (
            "YOU MUST WRITE THE ENTIRE ARTICLE IN PERSIAN (FARSI) LANGUAGE.\n"
            "Use Persian (RTL) text throughout. All headings, body text, and metadata must be in Persian.\n"
            "Use proper Persian SEO conventions and naturally incorporate Persian keywords.\n"
            "Write in a style appropriate for Persian-speaking audiences.\n"
        )
    else:
        lang_instruction = f"Write in {language} language."

    return f"""You are an expert SEO content writer. Write a comprehensive, fully SEO-optimized {style} on the topic: "{topic}".

## PRIMARY GOAL:
Create the BEST possible article on this topic that would rank #1 on Google. It must be more comprehensive, better structured, and more valuable than anything currently ranking.

## Requirements:
1. **Word count**: Aim for approximately {word_count} words.
2. **Tone**: {tone}.
3. **Primary keyword**: "{primary_kw}"
4. **Secondary keywords** (use naturally throughout, not stuffed): {kw_list}
5. **SEO-Optimized Structure:**
   - H1 title: Compelling, includes primary keyword, under 60 chars if possible
   - Meta description: 150-160 chars, includes primary keyword and a CTA
   - URL slug suggestion on the line after meta description
   - Hook the reader in the first 2 sentences of the introduction
   - Clear H2 and H3 subheadings (include secondary keywords naturally)
   - Use bullet points, numbered lists, and tables where appropriate
   - Bold key terms and takeaways
   - Internal linking suggestions: Mark spots with [INTERNAL LINK: topic/keyword]
   - Image suggestions: Mark spots with [IMAGE: description of image to include]
   - FAQ section at the end (3-5 questions from People Also Ask)
   - Strong conclusion with call to action
6. **Write in Markdown format.**
7. **Language**: {lang_instruction}
{research_section}{paa_section}{serp_section}

## OUTPUT FORMAT:
Start with these SEO metadata lines, then the article:

**SEO Metadata:**
- Title: [your H1 title]
- Meta Description: [150-160 char description]
- URL Slug: [suggested slug]
- Focus Keyword: {primary_kw}
- Secondary Keywords: {kw_list}

**Article Body:**
[Write the full article in Markdown]

**FAQ Section:**
[Write 3-5 FAQ items with questions and answers]

**Schema Markup (JSON-LD):**
[Provide the Article and FAQPage JSON-LD schema]

Write the complete article now.
"""


def generate_article(
    topic: str,
    target_keywords: list[str],
    provider: str = "ollama",
    people_also_ask: list[str] | None = None,
    serp_context: list[dict] | None = None,
    research_data: dict | None = None,
    word_count: int = DEFAULT_ARTICLE_WORD_COUNT,
    tone: str = DEFAULT_ARTICLE_TONE,
    style: str = DEFAULT_ARTICLE_STYLE,
    language: str = "en",
) -> str:
    """Generate a full SEO article using the chosen AI provider."""
    prompt = build_article_prompt(
        topic=topic,
        target_keywords=target_keywords,
        people_also_ask=people_also_ask,
        serp_context=serp_context,
        research_data=research_data,
        word_count=word_count,
        tone=tone,
        style=style,
        language=language,
    )

    if language == "fa":
        system_prompt = (
            "شما یک نویسنده محتوای سئوی حرفه‌ای هستید. شما محتوای ساختاریافته، "
            "اصیل و بهینه‌شده برای موتورهای جستجو تولید می‌کنید. "
            "همیشه به زبان فارسی و در قالب مارک‌داون می‌نویسید."
        )
    else:
        system_prompt = (
            "You are a world-class SEO content writer. You produce well-structured, "
            "original, keyword-optimized content that ranks well on search engines. "
            "You always write in Markdown format."
        )

    return generate_text(prompt, provider=provider, system_prompt=system_prompt)
