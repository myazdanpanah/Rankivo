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
    word_count: int = DEFAULT_ARTICLE_WORD_COUNT,
    tone: str = DEFAULT_ARTICLE_TONE,
    style: str = DEFAULT_ARTICLE_STYLE,
    language: str = "en",
) -> str:
    """Build a detailed prompt for SEO article generation."""

    kw_list = ", ".join(f'"{k}"' for k in target_keywords[:20])
    paa_section = ""
    if people_also_ask:
        questions = "\n".join(f"  - {q}" for q in people_also_ask[:10])
        paa_section = f"""
## People Also Ask (address these in your article):
{questions}
"""

    serp_section = ""
    if serp_context:
        snippets = "\n".join(
            f"  - {r.get('title', '')}: {r.get('snippet', '')[:200]}"
            for r in serp_context[:5]
        )
        serp_section = f"""
## Top-ranking competitor content to surpass (do NOT copy):
{snippets}
"""

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

    return f"""You are an expert SEO content writer. Write a comprehensive, engaging {style} on the topic: "{topic}".

## Requirements:
1. **Word count**: Aim for approximately {word_count} words.
2. **Tone**: {tone}.
3. **Primary keyword**: "{target_keywords[0] if target_keywords else topic}"
4. **Secondary keywords** (use naturally throughout): {kw_list}
5. **SEO structure**:
   - Compelling H1 title (include primary keyword)
   - Meta description (150-160 chars, include primary keyword)
   - Introduction hook in the first paragraph
   - Clear H2/H3 subheadings
   - Use bullet points and numbered lists where appropriate
   - Conclusion with a call to action
6. **Internal linking suggestions**: Mark spots with [INTERNAL LINK: topic] where internal links should go.
7. **Write in Markdown format.**
8. **Language**: {lang_instruction}
{paa_section}{serp_section}

Write the complete article now. Start with the H1 title on the first line.
"""


def generate_article(
    topic: str,
    target_keywords: list[str],
    provider: str = "ollama",
    people_also_ask: list[str] | None = None,
    serp_context: list[dict] | None = None,
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
