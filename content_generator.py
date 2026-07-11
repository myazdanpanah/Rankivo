"""
SEO AI Tools - AI Content Generator
Pluggable backend: Ollama (local), OpenAI, Anthropic Claude, Google Gemini.
"""
import time
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
    check_ollama,
    LLM_MAX_RETRIES,
    LLM_RETRY_BASE_DELAY,
    _safe_print,
)


# ──────────────────────────────────────────────
# Retry helper
# ──────────────────────────────────────────────

def _retry_call(func, *args, max_retries=None, **kwargs):
    """Call func with exponential backoff retry."""
    retries = max_retries if max_retries is not None else LLM_MAX_RETRIES
    last_err = None
    for attempt in range(retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_err = e
            if attempt < retries:
                delay = LLM_RETRY_BASE_DELAY * (2 ** attempt)
                _safe_print(f"[content_generator] Retry {attempt+1}/{retries} after {delay:.1f}s: {e}")
                time.sleep(delay)
    raise last_err


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


def _call_ollama_stream(user_prompt: str, system_prompt: str = "", model: str = ""):
    """Stream Ollama response chunk by chunk. Yields text chunks."""
    if not model:
        model = OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": True,
    }
    resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=180, stream=True)
    resp.raise_for_status()
    for line in resp.iter_lines():
        if line:
            try:
                import json
                chunk = json.loads(line)
                if chunk.get("response"):
                    yield chunk["response"]
            except Exception:
                pass


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
    if check_ollama():
        available.append("ollama")
    if OPENAI_API_KEY:
        available.append("openai")
    if ANTHROPIC_API_KEY:
        available.append("anthropic")
    if GOOGLE_API_KEY:
        available.append("gemini")
    return available


def generate_text(user_prompt: str, provider: str = "ollama", system_prompt: str = "") -> str:
    """Call the chosen AI provider with retry logic."""
    func = PROVIDERS.get(provider)
    if not func:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")
    return _retry_call(func, user_prompt, system_prompt)


def generate_text_stream(user_prompt: str, provider: str = "ollama", system_prompt: str = "", model: str = ""):
    """Stream text from LLM. Yields chunks for Ollama, falls back to non-streaming for others."""
    if provider == "ollama":
        for chunk in _call_ollama_stream(user_prompt, system_prompt, model=model):
            yield chunk
    else:
        # Non-streaming providers: yield full response as single chunk
        func = PROVIDERS.get(provider)
        if func:
            result = _retry_call(func, user_prompt, system_prompt)
            yield result


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

        # Iran province trends (for Persian content)
        province_trends = research_data.get("province_trends", {})
        if province_trends and language == "fa":
            research_section += "\n## Iran Province Search Trends:\n"
            for kw, pdata in province_trends.items():
                if pdata.get("top_provinces"):
                    top_fa = [f"{p.get('name_fa', '')} ({p.get('score', 0)})" for p in pdata["top_provinces"][:5]]
                    research_section += f"  - {kw}: {', '.join(top_fa)}\n"
                if pdata.get("recommendation"):
                    research_section += f"  Recommendation: {pdata['recommendation']}\n"

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
            "\n"
            "CRITICAL PERSIAN RULES:\n"
            "- ALL H1, H2, H3 headings: Persian\n"
            "- Title tag / SEO Title: Persian\n"
            "- Meta description: Persian (max 160 chars in Persian)\n"
            "- URL slug: use transliterated Persian or English (URLs cannot be in Persian script)\n"
            "- FAQ questions and answers: Persian\n"
            "- Schema markup: Persian values for name, description, headline\n"
            "- Image alt text: Persian\n"
            "- Internal link suggestions: Persian anchor text\n"
            "- Table headers and content: Persian\n"
            "- Bullet points, lists, bold text: Persian\n"
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
            "\u0634\u0645\u0627 \u06cc\u06a9 \u0646\u0648\u06cc\u0633\u0646\u062f\u0647 \u0645\u062d\u062a\u0648\u0627\u06cc \u0633\u0626\u0648\u06cc \u062d\u0631\u0641\u0647\u200c\u0627\u06cc \u0647\u0633\u062a\u06cc\u062f. \u0634\u0645\u0627 \u0645\u062d\u062a\u0648\u0627\u06cc \u0633\u0627\u062e\u062a\u0627\u0631\u06cc\u0627\u0641\u062a\u0647, \u0627\u0635\u06cc\u0644 \u0648 \u0628\u0647\u06cc\u0646\u0647\u200c\u0634\u062f\u0647 \u0628\u0631\u0627\u06cc \u0645\u0648\u062a\u0648\u0631\u0647\u0627\u06cc \u062c\u0633\u062a\u062c\u0648 \u062a\u0648\u0644\u06cc\u062f \u0645\u06cc\u200c\u06a9\u0646\u06cc\u062f. "
            "\u0647\u0645\u06cc\u0634\u0647 \u0628\u0647 \u0632\u0628\u0627\u0646 \u0641\u0627\u0631\u0633\u06cc \u0648 \u062f\u0631 \u0642\u0627\u0644\u0628 \u0645\u0627\u0631\u06a9\u200c\u062f\u0627\u0646 \u0645\u06cc\u200c\u0646\u0648\u06cc\u0633\u06cc\u062f. "
            "\u062a\u0645\u0627\u0645\u06cc \u0639\u0646\u0627\u0648\u06cc\u0646 (\u0647\u0631 H1, H2, H3), \u0645\u062a\u0627 \u062a\u0648\u0636\u06cc\u062d\u0627\u062a, \u0645\u062a\u0627 \u0639\u0646\u0648\u0627\u0646, \u0628\u062e\u0634 FAQ, \u0645\u062a\u0646 \u0645\u062d\u062a\u0648\u0627, \u0645\u062a\u0646 \u062c\u0627\u06cc\u06af\u0632\u06cc\u0646 \u062a\u0635\u0627\u0648\u06cc\u0631, \u0648 schema markup \u0628\u0627\u06cc\u062f \u0628\u0647 \u0632\u0628\u0627\u0646 \u0641\u0627\u0631\u0633\u06cc \u0628\u0627\u0634\u0646\u062f. \u0641\u0642\u0637 URL slug \u0628\u0627\u06cc\u062f \u0628\u0647 \u0627\u0646\u06af\u0644\u06cc\u0633\u06cc (\u062d\u0631\u0648\u0641 \u0644\u0627\u062a\u06cc\u0646) \u0628\u0627\u0634\u062f."
        )
    else:
        system_prompt = (
            "You are a world-class SEO content writer. You produce well-structured, "
            "original, keyword-optimized content that ranks well on search engines. "
            "You always write in Markdown format."
        )

    return generate_text(prompt, provider=provider, system_prompt=system_prompt)
